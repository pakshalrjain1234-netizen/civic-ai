import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const file=await readFile(new URL('../dist/local-workflow.js',import.meta.url),'utf8');
const c={state:{live:false,page:'report',report:{}},visionService:{potholeLoaded:false,ready:true},
 reportPage:()=>'<button id="analyze">Analyze image</button><div id="analysis-result">result</div>',
 analysisCard:r=>`<div class="eyebrow">${r.analysis.demo===false?'Visual analysis':'Simulated finding'}</div><h3>${r.analysis.issue_type}</h3>`,
 now:()=>new Date().toISOString(),esc:String,visionReady:()=>true,checkVisionHealth:async()=>{},
 displayType:cls=>cls[0].toUpperCase()+cls.slice(1),priority:()=>({level:'MEDIUM',reasons:[]}),
 departments:{Pothole:'Road Maintenance'},badge:()=>'',icon:()=>'',setTimeout,clearTimeout,AbortController};
vm.createContext(c);
vm.runInContext(file.slice(file.indexOf('analyze=async function('),file.indexOf('const originalAssistedIncidentDetail=')),c);
// Use saved genuine production responses, not fabricated model predictions.
const endpoint=JSON.parse(await readFile(new URL('../reports/moving-scan/endpoint-checks.json',import.meta.url),'utf8'));
const actual=endpoint.production.capture_comparison.flatMap(g=>g.samples);
for(const name of ['garbage','waterlogging']){
 const sample=actual.find(s=>s.response.detections.some(d=>d.class===name));assert(sample,`Missing real ${name} fixture`);
 let uploaded;c.detectFrame=async image=>{uploaded=image;return sample.response};
 const result=await c.analyze('specific-photo-'+name,'Pothole','HIGH');
 assert.equal(uploaded,'specific-photo-'+name);assert.equal(result.demo,false);assert.equal(result.source,'onnx-api');
 assert.equal(result.issue_type,c.displayType(sample.response.detections.sort((a,b)=>b.confidence-a.confidence)[0].class));
 c.state.report={image:'specific-photo-'+name,analysis:result};
 const html=c.reportPage();assert(!html.includes('assisted-pothole'),'Real class result must not show pothole controls');
 assert(c.analysisCard(c.state.report).includes('REAL AI DETECTION'));
}
const negative=actual.find(s=>s.response.detections.length===0);assert(negative,'Missing genuine negative response');
c.detectFrame=async()=>negative.response;const none=await c.analyze('clean-road-photo','Waterlogging','HIGH');
assert.equal(none.issue_type,'None');assert.equal(none.demo,false);assert.equal(none.source,'onnx-api');
c.state.report={image:'photo'};assert(c.reportPage().includes('assisted-pothole-open'));assert(!c.reportPage().includes('assisted-severity'));
c.state.report.assisted_requested=true;assert(c.reportPage().includes('assisted-severity'));
c.state.report.analysis={issue_type:'Waterlogging',demo:true};assert(c.analysisCard(c.state.report).includes('DEMO — NO AI ANALYSIS'));
c.visionReady=()=>false;await assert.rejects(c.analyze('photo','Waterlogging','HIGH'),/AI service unavailable/);
// Run the actual photo request handler with a delayed response and a replacement photo.
let resolve;const button={disabled:false};c.$=()=>button;c.rememberReport=()=>c.state.report;
c.render=()=>{};c.analyze=async()=>new Promise(r=>resolve=r);
vm.runInContext(file.slice(file.indexOf('let reportPhotoRequest='),file.indexOf('render=function(){')),c);
c.state.report={image:'old-photo'};const request=c.analyzeReportPhoto();await Promise.resolve();
c.state.report.image='replacement-photo';resolve({issue_type:'Waterlogging',demo:false});await request;
assert.equal(c.state.report.analysis,null,'Late old-photo result cannot overwrite replacement');
const features=await readFile(new URL('../dist/features.js',import.meta.url),'utf8');
assert(features.includes('delete r.scan_context;delete r.location_confirmed;delete r.assisted_requested;'));
console.log('PASS: actual /detect class/confidence provenance, no demo substitution, class-specific controls, explicit pothole fallback, stale-photo response rejection.');
