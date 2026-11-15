/* SE454_INSET_TOP_STEPS_START */
// One compact two-stage overlay: select face -> rim -> inward depth.
// Delegates to the existing native mesh preview and Apply/Cancel/Undo owner.
// "Set rim" is one explicit native checkpoint; "Set depth" is another.
(function(){
 'use strict';
 let panel=null,bar=null,step='idle',partId=null,lastGood=.2,depthMax=1;
 let busy=false,pendingValue=null,queued=false,feedback='';
 const api=()=>se430BeginnerAPI();
 const opInput=()=>panel?.querySelector('#modelAtelierWorkshopOperation');
 const nativeAmount=()=>panel?.querySelector('#modelAtelierWorkshopAmount');
 const state=()=>{try{return api()?.inspect?.()||null;}catch{return null;}};
 const number=n=>Number(n.toFixed(3)).toString();
 const expected=()=>step==='rim'?'inset':'extrude';
 const absDepth=n=>Math.max(.005,Math.abs(Number(n)||.15));
 const numericValue=()=>step==='rim'?lastGood:absDepth(lastGood);
 function validPreview(s){return !!s?.preview?.active&&s.preview.operation===expected();}
 function message(text){feedback=text||'';if(bar){const note=bar.querySelector('#se454Hint');if(note)note.textContent=feedback;}}
 function maxDepth(){
  // A useful slider interval for a selected rim, not a topology limit.
  // Native collision checking remains authoritative on every preview.
  try{
   const s=state(),p=s?.selection?.partId&&partById(s.selection.partId),d=p?.topologyMesh;
   if(!d||!s?.selection?.faceIds?.length)return 1;
   const r=se430MeshOps.region(d,s.selection.faceIds);
   if(!r?.ok)return 1;
   const values=d.positions,normal=r.normal,origin=r.origin;
   let extent=0;
   for(let i=0;i<values.length;i+=3){
    const t=(origin[0]-values[i])*normal[0]+(origin[1]-values[i+1])*normal[1]+(origin[2]-values[i+2])*normal[2];
    if(Number.isFinite(t))extent=Math.max(extent,t);
   }
   return Math.max(.08,Math.min(4,extent*.92||1));
  }catch{return 1;}
 }
 function draw(){
  if(!bar||!panel)return;
  const active=step!=='idle';
  panel.dataset.se454InsetStage=step;
  bar.hidden=!active;
  if(!active)return;
  const s=state(),isDepth=step==='depth',value=numericValue();
  const title=bar.querySelector('#se454Title'),range=bar.querySelector('#se454Range');
  const exact=bar.querySelector('#se454Exact'),set=bar.querySelector('#se454Set');
  title.textContent=isDepth?'2/2 · Depth inward':'1/2 · Rim width';
  range.min=isDepth?'.005':'.03';
  range.max=isDepth?String(depthMax):'.8';
  range.step=isDepth?'.005':'.005';
  if(document.activeElement!==range)range.value=number(value);
  if(document.activeElement!==exact)exact.value=number(value);
  exact.min=range.min;exact.max=range.max;exact.step=range.step;
  exact.setAttribute('aria-label',isDepth?'Inward depth in local units':'Inset fraction of selected face');
  range.setAttribute('aria-label',isDepth?'Preview inward cavity depth':'Preview inset rim width');
  set.disabled=busy||!validPreview(s);
  set.textContent=isDepth?'Set depth':'Set rim';
  if(!feedback){
   const hint=isDepth?'Drag for cavity depth; Set commits.':'Drag for rim thickness; Set continues to depth.';
   bar.querySelector('#se454Hint').textContent=!s?.selection?.partId?
    'Select a mesh, then tap one face.':!validPreview(s)?
    'Tap the face to start a preview. '+hint:hint;
  }
 }
 function syncValue(raw){
  if(busy||step==='idle'||raw===''||!Number.isFinite(Number(raw)))return;
  const depth=step==='depth';
  const min=depth?.005:.03,max=depth?depthMax:.8;
  const value=Math.round(Math.max(min,Math.min(max,Number(raw)))*1000)/1000;
  const s=state(),op=expected();
  // Refuse to replace a preview owned by a different tool.
  if(s?.preview?.active&&s.preview.operation!==op){
   message('Apply or Cancel the other preview first.');draw();return;
  }
  if(!s?.operations?.[op]?.available){
   message(s?.operations?.[op]?.reason||'Tap the connected face first.');draw();return;
  }
  const result=api()?.preview(op,{amount:depth?-value:value});
  if(result?.ok){
   lastGood=depth?-value:value;feedback='';
   const native=nativeAmount();if(native)native.value=number(lastGood);
  }else{
   message(result?.reason||'That value cannot be previewed; the previous valid shape is preserved.');
  }
  se430BeginnerResult(result);draw();
 }
 function schedule(raw){
  pendingValue=raw;
  if(queued)return;
  queued=true;
  requestAnimationFrame(()=>{
   queued=false;const value=pendingValue;pendingValue=null;
   if(value!==null&&value!==undefined)syncValue(value);
  });
 }
 function firstPreview(){
  const s=state();
  if(!s?.selection?.partId||!s.selection.faceIds?.length){
   message('Select the cube, then tap the face you want to inset.');draw();return false;
  }
  if(s.preview.active&&s.preview.operation==='inset'){feedback='';draw();return true;}
  if(s.preview.active)return false;
  const r=api()?.preview('inset',{amount:lastGood});
  if(!r?.ok){message(r?.reason||'Inset preview unavailable.');draw();return false;}
  se430BeginnerResult(r);feedback='';draw();return true;
 }
 function begin(){
  if(!panel||!bar)return false;
  const s=state();if(s?.preview?.active&&s.preview.operation!=='inset')return false;
  step='rim';partId=s?.selection?.partId||null;
  lastGood=s?.preview?.operation==='inset'&&Number.isFinite(s.preview.stats?.fraction)?s.preview.stats.fraction:
   Math.max(.03,Math.min(.8,Number(nativeAmount()?.value)||.2));
  feedback='';
  firstPreview();
  draw();return true;
 }
 function goDepth(){
  // Apply already completed the Inset and retained only the inner cap.
  // Never reselect the connected coplanar rim, which would include the lip.
  const s=state();
  if(!partId||s?.selection?.partId!==partId||!s.selection?.faceIds?.length){
   message('Rim applied. Reselect its inner face before adjusting depth.');
   step='depth';lastGood=-.15;depthMax=1;draw();return;
  }
  step='depth';depthMax=maxDepth();
  lastGood=-Math.min(.15,Math.max(.005,depthMax*.3));
  feedback='';
  se430BeginnerSetOperation('extrude',lastGood);
  const after=state();
  if(after?.operations?.extrude?.available){
   // Retry bounded shallower choices for small objects; all are previews.
   const candidates=[absDepth(lastGood),Math.min(depthMax,.075),Math.min(depthMax,.025)].filter(n=>n>=.005);
   let result=null;
   for(const candidate of [...new Set(candidates)]){
    result=api()?.preview('extrude',{amount:-candidate});
    if(result?.ok){lastGood=-candidate;break;}
   }
   if(result?.ok){
    if(nativeAmount())nativeAmount().value=number(lastGood);
    se430BeginnerResult(result);
   }else message(result?.reason||'Choose a shallower cavity depth.');
  }else message(after?.operations?.extrude?.reason||'Select the inner face to begin depth.');
  draw();
 }
 function setStage(){
  if(step==='idle'||busy)return false;
  const s=state();
  if(!validPreview(s)){message('Make a valid preview before pressing Set.');draw();return false;}
  busy=true;
  const completed=step,expectedPart=partId;
  const r=api()?.apply();
  busy=false;
  if(!r?.ok){message(r?.reason||'Could not apply the geometry.');draw();return false;}
  se430BeginnerResult(r);
  if(completed==='rim'){
   partId=expectedPart||r.id;
   goDepth();
  }else{
   const done='Rim and depth applied. Each Set has its own Undo step.';
   close(false);
   if(typeof status==='function')status(done);
  }
  return true;
 }
 function close(cancelPreview=true){
  if(step==='idle')return;
  if(cancelPreview){
   const s=state();if(s?.preview?.active&&s.preview.operation===expected())se430BeginnerResult(api()?.cancel());
  }
  const wasDepth=step==='depth';
  step='idle';partId=null;feedback='';
  draw();
  window.SWYRL_ENGINE_FACE_FLYOUTS_452?.close?.();
  if(cancelPreview&&typeof status==='function'){
   status(wasDepth?'Depth canceled; applied rim remains. Undo once to remove it.':'Inset preview canceled; geometry unchanged.');
  }
 }
 function refresh(){
  if(step==='idle')return;
  const s=state();
  if(partId&&s?.selection?.partId!==partId){
   // Guard against another project or a different selection.
   close(false);return;
  }
  if(!partId&&s?.selection?.partId)partId=s.selection.partId;
  if(step==='rim'&&!s?.preview?.active&&s?.operations?.inset?.available&&!busy){
   // A face tap can arm/produce the preview in a microtask; don't steal it.
   queueMicrotask(()=>{if(step==='rim'&&!state()?.preview?.active)firstPreview();});
  }
  if(validPreview(s)&&s.preview.stats){
   const value=step==='rim'?s.preview.stats.fraction:s.preview.stats.depth;
   if(Number.isFinite(value)){
    lastGood=value;feedback='';
   }
  }
  draw();
 }
 function mount(p){
  if(!p||p.dataset.se454TopSteps==='1')return;
  const scene=p.querySelector('.atelier-scene'),quick=p.querySelector('#se445ShapeQuick');
  if(!scene||!quick)return;
  panel=p;panel.dataset.se454TopSteps='1';
  const overlay=document.createElement('section');
  overlay.id='se454InsetTopBar';overlay.hidden=true;
  overlay.setAttribute('role','group');overlay.setAttribute('aria-label','Inset rim and depth');
  overlay.innerHTML='<div class="se454-top-row"><strong id="se454Title">1/2 · Rim width</strong>'+
   '<button type="button" id="se454Cancel" aria-label="Cancel this Inset stage" title="Cancel">×</button></div>'+
   '<div class="se454-slider-row"><input id="se454Range" type="range" min=".03" max=".8" step=".005" value=".2">'+
   '<input id="se454Exact" type="number" inputmode="decimal" min=".03" max=".8" step=".005" value=".2">'+
   '<button type="button" id="se454Set" disabled>Set rim</button></div>'+
   '<p id="se454Hint" role="status" aria-live="polite">Select a face to preview its rim.</p>';
  scene.append(overlay);bar=overlay;
  quick.addEventListener('click',e=>{
   const target=e.target.closest('[data-se445-op]');
   if(target?.dataset.se445Op==='inset'){
    // Let the original native action and v452 Face-flyout callbacks execute.
    queueMicrotask(begin);
   }else if(target&&step!=='idle'&&target.dataset.se445Op!=='inset'){
    close();
   }
  });
  overlay.querySelector('#se454Range').addEventListener('input',e=>schedule(e.target.value));
  overlay.querySelector('#se454Exact').addEventListener('change',e=>syncValue(e.target.value));
  overlay.querySelector('#se454Set').addEventListener('click',setStage);
  overlay.querySelector('#se454Cancel').addEventListener('click',()=>close());
  window.addEventListener('swrlz:model-workshop-change',refresh);
  window.addEventListener('keydown',e=>{
   if(e.key==='Escape'&&step!=='idle'&&document.activeElement&&overlay.contains(document.activeElement)){
    e.preventDefault();close();
   }
  });
  draw();
 }
 const previousInstall=se430BeginnerInstall;
 se430BeginnerInstall=function(p){const r=previousInstall(p);mount(p);return r;};
 window.SWYRL_ENGINE_INSET_TOP_STEPS_454=Object.freeze({
  version:'v11.454',begin,set:setStage,cancel:()=>close(),refresh,
  inspect:()=>({step,active:step!=='idle',partId,lastGood,depthMax})
 });
})();
/* SE454_INSET_TOP_STEPS_END */