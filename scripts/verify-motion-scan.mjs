import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const context={};vm.runInNewContext(await readFile(new URL('../dist/motion-scan.js',import.meta.url),'utf8'),context);
const {sharpness,Stabilizer,nextDelay}=context.CivicMotion;
const pixels=(pattern)=>{const a=new Uint8ClampedArray(32*24*4);for(let y=0;y<24;y++)for(let x=0;x<32;x++){
 const i=(y*32+x)*4,v=pattern(x,y);a[i]=a[i+1]=a[i+2]=v;a[i+3]=255;
}return a;};
assert.equal(sharpness(pixels(()=>80),32,24),0);
assert(sharpness(pixels((x,y)=>(x+y)%2?255:0),32,24)>sharpness(pixels(x=>x*7),32,24));
const box={x:.2,y:.3,width:.4,height:.3};const garbage={class:'garbage',confidence:.38,bbox:box};
const temporal=new Stabilizer();
assert.equal(temporal.update([garbage],0).display.length,0,'Weak new detection needs confirmation');
assert.equal(temporal.update([{...garbage,confidence:.55}],300).fresh.length,1);
assert.equal(temporal.update([],600).display[0].stale,true);
assert.equal(temporal.expire(1200).length,0);
temporal.update([{...garbage,confidence:.9}],1500);temporal.reset();assert.equal(temporal.visible.length,0);
assert.equal(temporal.update([{...garbage,confidence:.9}],1600).fresh.length,1);
assert.equal(temporal.update([{...garbage,class:'waterlogging'}],1700).display.length,0,'Changed class clears stale overlay');
assert.equal(nextDelay(100),200);assert.equal(nextDelay(700),80);assert.equal(nextDelay(100,true),1000);
// Exercise the real scan engine with delayed requests, stop, pause and stale callbacks.
const source=await readFile(new URL('../dist/live-scan.js',import.meta.url),'utf8');
const ticks=source.slice(source.indexOf('async function scanTick()'),source.indexOf('function saveFinding('));
let release,calls=0,scheduled=[],saved=0,timer;
const scan={active:true,paused:false,busy:false,mode:'live',generation:1,timeout:15000,detections:[]};
const fake={scan,CivicMotion:context.CivicMotion,scanStabilizer:new Stabilizer(),performance:{now:()=>0},
 navigator:{onLine:true},AbortController,clearTimeout:()=>{},setTimeout:fn=>{timer=fn;return 1},
 sharpestFrame:async()=> 'test-only-frame',detectFrame:async()=>{calls++;return new Promise(resolve=>release=resolve)},
 saveFinding:()=>saved++,updateScanUi:()=>{},clearScanHistory:()=>{fake.scanStabilizer.reset();scan.detections=[]},
 scheduleScan:delay=>scheduled.push(delay),persistenceTimer:null};
vm.runInNewContext(ticks,fake);
const first=fake.scanTick();await Promise.resolve();await Promise.resolve();await fake.scanTick();assert.equal(calls,1,'No overlapping inference requests');
scan.paused=true;release({detections:[{...garbage,confidence:.9}]});await first;assert.equal(saved,0,'Paused response cannot create a finding');
scan.paused=false;scan.busy=false;const second=fake.scanTick();await Promise.resolve();await Promise.resolve();
scan.generation++;scan.active=false;release({detections:[{...garbage,confidence:.9}]});await second;
assert.equal(saved,0,'Stopped generation cannot apply detections');
assert(source.includes(".toBlob(resolve,'image/jpeg',.8)"));assert(source.includes('maxFrameDimension:640'));
// Run the actual three-frame capture selector against controlled frame textures.
let frame=0,chosen=0;
const video={videoWidth:1280,videoHeight:720};
const canvases=[];
const doc={createElement:()=>{
 const index=canvases.length,c={width:0,height:0,marker:0};
 c.getContext=()=>({drawImage:image=>{if(index===0)c.marker=++frame;else c.marker=image.marker;},
   getImageData:()=>({data:pixels(c.marker===2?(x,y)=>(x+y)%2?255:0:()=>80)})});
 c.toBlob=fn=>{chosen=c.marker;fn({size:100,marker:c.marker})};canvases.push(c);return c;
}};
const captureContext={document:doc,CivicMotion:context.CivicMotion,scan:{active:true,paused:false,mode:'live',generation:1,maxFrameDimension:640},
 $:()=>video,DOMException,FileReader:class{readAsDataURL(blob){this.result='test-only-frame-'+blob.marker;this.onload();}},
 setTimeout:fn=>setTimeout(fn,0),clearTimeout};
// Thumbnails in this unit fixture are 32x24; override sharpness dimensions for their controlled buffers.
captureContext.CivicMotion={...context.CivicMotion,sharpness:data=>sharpness(data,32,24)};
vm.runInNewContext(source.slice(source.indexOf('const frameCanvas='),source.indexOf('function scheduleScan(')),captureContext);
assert.equal(await captureContext.sharpestFrame(new AbortController().signal,1),'test-only-frame-2');
assert.equal(frame,3);assert.equal(chosen,2);assert.equal(canvases[0].width,640);assert.equal(canvases[0].height,360);
const cancelled=new AbortController();cancelled.abort();await assert.rejects(captureContext.sharpestFrame(cancelled.signal,1),{name:'AbortError'});
console.log('PASS: sharpness, temporal matching/expiry, adaptive backoff, single-flight, late pause/stop rejection, 640 px capture.');
const scheduler=new context.CivicMotion.PotholeSchedule(2000);
assert.equal(scheduler.due(0,1,true),true);
assert.equal(scheduler.due(300,1,true),false);
assert.equal(scheduler.due(1999,1,true),false);
assert.equal(scheduler.due(2000,1,true),true);
assert.equal(scheduler.due(2100,2,true),true);
assert.equal(scheduler.due(5000,2,false),false);
const sampledTemporal=new context.CivicMotion.Stabilizer();
const sampledRoad={...garbage,class:'pothole',confidence:.5};
assert.equal(sampledTemporal.update([sampledRoad],0).fresh.length,0);
sampledTemporal.update([],400,['garbage','waterlogging']);
assert.equal(sampledTemporal.update([sampledRoad],2200).fresh.length,1);
assert.equal(sampledTemporal.expire(3200).length,0);
console.log('PASS: pothole scheduling, reset, sampled confirmation and stale expiry.');
