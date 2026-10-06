// Local prototype workflow. Shared production accounts continue to use Supabase.
function confidenceText(d){return Number.isFinite(d.confidence)?Math.round(d.confidence*100)+'%':d.confidence_label||'Needs review'}
const originalDemoNote=demoNote;
demoNote=function(){return !state.live&&visionReady()?'<div class="notice">Local prototype. Connected AI analyzes real images. Roles are demonstration accounts; records and evidence are saved on this browser. Repair completion requires authority review.</div>':originalDemoNote()};
const localRecordsKey='civiceye-local-incidents-v1';
try{const saved=JSON.parse(localStorage.getItem(localRecordsKey)||'null');if(Array.isArray(saved)&&saved.every(i=>typeof i.id==='string'&&Array.isArray(i.history)))incidents=saved}catch{}
function persistLocalRecords(){if(state.live)return;try{localStorage.setItem(localRecordsKey,JSON.stringify(incidents))}catch{toast('Browser storage is full. Export or clear older evidence before leaving this page.')}}
const originalLocalSubmit=submitReport;
submitReport=async function(...args){
 const r=rememberReport();
 if(r.analysis?.user_assisted){
  if(state.live)throw Error('User-assisted reports are available in the local prototype workspace. Shared storage needs a trusted reporting bridge.');
  if(!r.image)throw Error('A pothole photo is required.');
  if(!r.location_confirmed&&!$('#assisted-location-confirm')?.checked)throw Error('Confirm the report location before submitting.');
  r.location_confirmed=true;
 }
 const result=await originalLocalSubmit(...args);persistLocalRecords();return result
};
const originalLocalAction=action;
action=async function(...args){const result=await originalLocalAction(...args);persistLocalRecords();return result};
const originalLocalRender=render;
let reportPhotoRequest=null;
async function analyzeReportPhoto(){
 const r=rememberReport(),image=r.image;
 if(!image)throw Error('Capture or upload an image first.');
 reportPhotoRequest?.controller.abort();
 const request={report:r,image,controller:new AbortController()};reportPhotoRequest=request;
 const timeout=setTimeout(()=>request.controller.abort(),15000);
 r.analysis=null;render();
 const button=$('#analyze');if(button){button.disabled=true;button.textContent='Analyzing this photo…'}
 try{
  const result=await analyze(image,undefined,undefined,undefined,undefined,request.controller.signal);
  if(reportPhotoRequest!==request||state.report!==r||r.image!==image||state.page!=='report')return;
  r.analysis=result;r.assisted_requested=false;render();
 }catch(error){
  if(request.controller.signal.aborted&&(state.report!==r||r.image!==image||state.page!=='report'))return;
  throw error.name==='AbortError'?Error('Image analysis timed out. Please retry.'):error;
 }finally{
  clearTimeout(timeout);
  if(reportPhotoRequest===request){reportPhotoRequest=null;if($('#analyze')){$('#analyze').disabled=false;$('#analyze').innerHTML=icon('spark')+'Analyze image';}}
 }
}
render=function(){persistLocalRecords();originalLocalRender();
  if(reportPhotoRequest&&(state.page!=='report'||reportPhotoRequest.report!==state.report||reportPhotoRequest.image!==state.report?.image)){
   reportPhotoRequest.controller.abort();reportPhotoRequest=null;
  }
 if(state.page==='report'){
  for(const id of ['demo-type','demo-severity']){const control=$('#'+id);if(control)control.closest('label')?.remove()}
  if($('#analyze'))$('#analyze').onclick=()=>safe(analyzeReportPhoto);
  if($('#assisted-pothole-open'))$('#assisted-pothole-open').onclick=()=>{rememberReport().assisted_requested=true;render()};
  const manual=$('#assisted-pothole');
  if(manual)manual.onclick=()=>safe(async()=>{
   const r=rememberReport();if(!r.image)throw Error('Capture or upload a pothole photo first.');
   const severity=$('#assisted-severity')?.value||'MEDIUM';
   if(!['LOW','MEDIUM','HIGH'].includes(severity))throw Error('Choose a valid severity.');
   r.analysis={issue_type:'Pothole',severity,confidence:null,confidence_label:'User-reported · unverified',
    demo:false,user_assisted:true,requires_review:true,verified:false,
    explanation:'The citizen identified this photo as a pothole. Automatic pothole detection is unavailable. Authority must review the photo and location.'};
   render();
  });
  const confirmation=$('#assisted-location-confirm');
  if(confirmation)confirmation.onchange=()=>{rememberReport().location_confirmed=confirmation.checked};
  for(const id of ['lat','lng']){const control=$('#'+id);if(control)control.addEventListener('change',()=>{
   if(state.report?.analysis?.user_assisted){state.report.location_confirmed=false;if(confirmation)confirmation.checked=false}
  })}
}};
analyze=async function(image,simType,simSeverity,before,incidentId,signal){
  if(before&&state.selected?.user_assisted)return {issue_type:'None',confidence:null,
    confidence_label:'Human review required',severity:'LOW',verified:false,demo:false,
    requires_review:true,user_assisted:true,
    explanation:'Automatic pothole verification is unavailable. Authority must compare these before/after photos and confirm the location and repair.'};
  if(!visionReady())await checkVisionHealth();
  if(!visionReady()){
    if(before&&state.selected?.demo===false)throw Error('Real evidence review requires the connected AI service.');
    throw Error('AI service unavailable. Connect the backend before analyzing this photo.');
  }
  const response=await detectFrame(image,signal),detections=response.detections;
  if(before){
    // Absence of a detection cannot establish repair or matching location.
    const remaining=detections.some(d=>displayType(d.class)===state.selected?.issue_type);
    return {issue_type:remaining?state.selected.issue_type:'None',confidence:null,confidence_label:'Needs review',
      severity:'LOW',verified:false,demo:false,requires_review:true,
      explanation:remaining?'The original issue is still detected. Authority review is required.':
        'The original issue was not detected in this image. This does not prove repair or matching location. Authority must compare the before/after evidence.'};
  }
  // A single-photo report requires the citizen to review the selected finding.
  const d=detections.slice().sort((a,b)=>(b.confidence||0)-(a.confidence||0))[0];
  if(!d)return {issue_type:'None',confidence:null,confidence_label:'Needs review',severity:'LOW',demo:false,source:'onnx-api',
    explanation:visionService.potholeLoaded!==true?'No garbage or waterlogging detected. Automatic pothole detection is unavailable; use manual pothole reporting if appropriate.':'No civic issue detected; visual models can miss hazards.'};
  return {issue_type:displayType(d.class),confidence:d.confidence,confidence_label:d.confidence_label,
    requires_review:d.requires_review||d.confidence===null,severity:d.severity==='CRITICAL'?'HIGH':d.severity,
    explanation:d.explanation,demo:false,source:'onnx-api',bbox:d.bbox,
    detector:d.detector||'civiceye-v2',processing_time_ms:response.processingTimeMs,analyzed_at:now()};
};
const originalAssistedReportPage=reportPage;
reportPage=function(){
 const r=state.report||{},html=originalAssistedReportPage();
 if(state.live||visionService.potholeLoaded===true)return html;
 // Unavailable potholes must not look like the outcome of a water/garbage analysis.
 if(r.analysis&&r.analysis.issue_type!=='None'&&!r.analysis.user_assisted)return html;
 if(!r.assisted_requested&&!r.analysis?.user_assisted){
  const option=`<button class="button-link" id="assisted-pothole-open" style="margin-top:16px" ${r.image?'':'disabled'}>Report a pothole manually</button>`;
  return html.replace('<div id="analysis-result"',option+'<div id="analysis-result"');
 }
 const manual=`<div class="notice" style="margin-top:16px"><b>Automatic pothole detection unavailable</b><p>You can report a pothole photo yourself. An authority will review it.</p></div><label class="field">Your pothole severity estimate<select id="assisted-severity">${['LOW','MEDIUM','HIGH'].map(s=>`<option ${s===(r.analysis?.user_assisted?r.analysis.severity:'MEDIUM')?'selected':''}>${s}</option>`).join('')}</select></label><button class="btn full" id="assisted-pothole" ${r.image?'':'disabled'}>Report this photo as a pothole</button>`;
 return html.replace('<div id="analysis-result"',manual+'<div id="analysis-result"');
};
const originalAssistedAnalysisCard=analysisCard;
analysisCard=function(r){
 const a=r.analysis;if(!a?.user_assisted){
  const html=originalAssistedAnalysisCard(r);
  if(a?.demo===true)return html.replace('<div class="eyebrow">Simulated finding</div>',
    '<div class="eyebrow">DEMO — NO AI ANALYSIS</div>').replace('<div class="eyebrow">Visual analysis</div>',
    '<div class="eyebrow">DEMO — NO AI ANALYSIS</div>');
  if(a?.demo===false&&a.issue_type!=='None')return html.replace('<div class="eyebrow">Visual analysis</div>',
    '<div class="eyebrow">REAL AI DETECTION</div>')+
    `<p class="subtext">Source: CivicEye ONNX detector${Number.isFinite(a.processing_time_ms)?' · Backend processing: '+Math.round(a.processing_time_ms)+' ms':''}. Severity and priority are estimates; review before submitting.</p>`;
  return html;
 }
 const p=priority({...r,...a,reports:1,created_at:now()});
 return `<div class="result"><div class="eyebrow">USER-ASSISTED REPORT</div><h3>Pothole reported by you</h3><p>${esc(a.explanation)}</p><div class="details-list"><div><label>Assessment</label><b>User-reported · unverified</b></div><div><label>Your severity estimate</label><b>${esc(a.severity)}</b></div><div><label>Suggested department</label><b>${esc(departments.Pothole)} Department</b></div><div><label>Possible priority</label>${badge(p.level)}</div></div></div><div class="priority-explanation"><b>Why this priority?</b><ul>${p.reasons.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div><div class="notice" style="margin-top:15px">This is your report, not an AI detection. Authority review is required.</div><label class="field" style="margin-top:15px"><span><input type="checkbox" id="assisted-location-confirm" ${r.location_confirmed?'checked':''}> I have confirmed the report location and coordinates</span></label><button class="btn primary full" id="submit-incident" style="margin-top:15px">${icon('check')}Submit incident</button>`;
};
const originalAssistedIncidentDetail=incidentDetail;
incidentDetail=function(){
 const html=originalAssistedIncidentDetail();if(!state.selected?.user_assisted)return html;
 return html.replace('AI finding ','Citizen report ').replace('Model assessment','Report assessment')
  .replace('<label>Severity</label>','<label>Citizen severity estimate</label>')
  .replace('Reject detection','Reject report')
  .replace('<div class="details-list">','<div class="notice" style="margin-bottom:16px">User-assisted pothole report. Automatic pothole detection is unavailable. Review the citizen photo and location.</div><div class="details-list">');
};
const originalAssistedCompletion=completion;
completion=function(){originalAssistedCompletion();if(state.selected?.user_assisted&&$('#verify'))$('#verify').textContent='Prepare for authority review'};
render();
checkVisionHealth();
