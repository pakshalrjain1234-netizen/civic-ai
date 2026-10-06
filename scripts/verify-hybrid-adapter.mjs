import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const base=new URL('../',import.meta.url);
const report=JSON.parse(await readFile(new URL('reports/harisanth-integration/report.json',base),'utf8'));
const responses=JSON.parse(await readFile(new URL('reports/harisanth-integration/responses.json',base),'utf8'));
const actual=Object.values(responses).find(r=>r.detections.some(d=>d.class==='pothole'));
const live=await readFile(new URL('dist/live-scan.js',base),'utf8');
const adapter=await readFile(new URL('dist/vision-backend.js',base),'utf8');
let time=0;const payloads=[];
const c={URL,AbortController,setTimeout,clearTimeout,performance:{now:()=>time},now:()=>new Date().toISOString(),
 window:{CIVICEYE_VISION_ENV:{visionApiUrl:'http://127.0.0.1:8011',production:false}},
 scan:{mode:'live',paused:false,camera:false,busy:false,detections:[],timer:null},updateScanUi:()=>{},scheduleScan:()=>{},
 waterSeverity:()=> 'MEDIUM',fetch:async(url,options)=>{if(options?.method==='POST')payloads.push(JSON.parse(options.body));return {ok:true,json:async()=>options?.method==='POST'?actual:report.health}}};
vm.createContext(c);vm.runInContext(await readFile(new URL('dist/motion-scan.js',base),'utf8'),c);
vm.runInContext(live.slice(live.indexOf('function validateDetectionResponse'),live.indexOf('async function detectFrame')),c);
vm.runInContext(adapter.slice(0,adapter.indexOf('function boxOverlap')),c);
await c.checkVisionHealth();assert.equal(c.scan.status,'MODEL LOADED / LIVE AI READY');
const result=await c.detectFrame('actual-image',undefined,{live:true,generation:1});
assert(result.detections.some(d=>d.class==='pothole'&&d.detector==='pothole-specialist'));
assert.equal(payloads.at(-1).include_pothole,true);
time=400;await c.detectFrame('next-frame',undefined,{live:true,generation:1});assert.equal(payloads.at(-1).include_pothole,false);
await c.detectFrame('photo');assert.equal(payloads.at(-1).include_pothole,true);
time=2000;await c.detectFrame('scheduled-frame',undefined,{live:true,generation:1});assert.equal(payloads.at(-1).include_pothole,true);
assert.deepEqual(result.evaluatedClasses,actual.evaluated_classes);
console.log('PASS: real integrated responses, specialist provenance, ready UI status, scheduled live vs full photo requests.');
