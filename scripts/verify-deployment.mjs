import {readFile,readdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('../',import.meta.url)), build=path.join(root,'build');
const read=f=>readFile(path.join(build,f),'utf8');
const manifest=JSON.parse(await read('manifest.webmanifest'));
assert.equal(manifest.name,'CivicEye AI'); assert.equal(manifest.start_url,'/');
assert.equal(manifest.display,'standalone'); assert.equal(manifest.orientation,'portrait-primary');
assert.equal(manifest.prefer_related_applications,false);
for (const icon of manifest.icons) {
  const png=await readFile(path.join(build,icon.src));
  assert.equal(png.subarray(1,4).toString(),'PNG');
  assert.equal(png.readUInt32BE(16),Number(icon.sizes.split('x')[0]));
  assert.equal(png.readUInt32BE(20),Number(icon.sizes.split('x')[1]));
}
for (const file of await readdir(build)) if (/\.(js|html|css)$/.test(file)) {
  assert(!/127\.0\.0\.1|http:\/\/localhost/.test(await read(file)),`Production localhost leaked: ${file}`);
}
assert((await read('index.html')).includes('rel="manifest"'));
assert((await read('_redirects')).includes('/*    /index.html    200'));
// Exercise service worker routing, including forbidden API caching.
const handlers={}, network=[], writes=[];
const cache={addAll:async files=>writes.push(...files),match:async p=>({cached:p})};
const context={URL,Set,Promise,self:{location:{origin:'https://civic.example'},addEventListener:(n,f)=>handlers[n]=f,clients:{claim:async()=>{}}},
  caches:{open:async()=>cache,keys:async()=>[],delete:async()=>true}, fetch:async request=>{network.push(request);return {network:true};}};
vm.runInNewContext(await read('sw.js'),context);
let pending; handlers.install({waitUntil:p=>pending=p}); await pending;
assert(!writes.some(p=>/detect|health|api\//.test(p)));
function route(url,method='GET',mode='cors') {let response; handlers.fetch({request:{url,method,mode},respondWith:p=>response=p}); return response;}
assert.equal(route('https://api.example/detect','POST'),undefined);
assert.equal(route('https://civic.example/detect'),undefined);
assert.equal(route('https://civic.example/health'),undefined);
assert.equal(route('https://civic.example/api/records'),undefined);
assert.equal(route('https://civic.example/private-photo.jpg'),undefined);
assert((await route('https://civic.example/app.js')).cached);
context.fetch=async()=>{throw Error('offline');};
assert.equal((await route('https://civic.example/live-scan','GET','navigate')).cached,'/index.html');
// Verify registration and native-event-only install behavior without fabricating a browser install.
const events={}, button={hidden:true,addEventListener:(name,handler)=>button[name]=handler};
const media={matches:false,addEventListener:()=>{}}; let registered=false, prompted=0;
const pwa={window:{matchMedia:()=>media,isSecureContext:true,addEventListener:(n,f)=>events[n]=f},
 document:{getElementById:()=>button},navigator:{serviceWorker:{register:async(u,o)=>{assert.equal(u,'/sw.js');assert.equal(o.scope,'/');registered=true;}}},console};
vm.runInNewContext(await read('pwa.js'),pwa);
assert.equal(button.hidden,true); events.load(); await Promise.resolve(); assert(registered);
events.beforeinstallprompt({preventDefault(){},prompt:async()=>{prompted++;},userChoice:Promise.resolve({outcome:'accepted'})});
assert.equal(button.hidden,false); await button.click(); assert.equal(prompted,1); assert.equal(button.hidden,true);
events.appinstalled(); assert.equal(button.hidden,true);
const healthContext={URL,Math,Number,AbortController,setTimeout,clearTimeout,
  window:{CIVICEYE_VISION_ENV:{visionApiUrl:'https://api.example',production:true}},
  scan:{mode:'live',paused:false,camera:false,feed:[],detections:[]},
  updateScanUi:()=>{},scheduleScan:()=>{},
  fetch:async()=>({ok:true,json:async()=>({status:'online',model_loaded:true,ready:true,pothole_detector:false})})};
const adapter=await read('vision-backend.js');
vm.runInNewContext(adapter.slice(0,adapter.indexOf('\ndetectFrame=')),healthContext);
assert.equal(vm.runInNewContext('visionUrls().detect',healthContext),'https://api.example/detect');
await healthContext.checkVisionHealth();
assert(healthContext.scan.status.includes('POTHOLE UNAVAILABLE'));
console.log('PASS: manifest/icons, production HTTPS configuration, SPA rules, shell-only offline caching, API bypass, registration and native install-event handling.');
