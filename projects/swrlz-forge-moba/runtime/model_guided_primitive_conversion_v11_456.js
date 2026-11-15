/* SE456_GUIDED_PRIMITIVE_CONVERSION_START */
// Make the existing native primitive conversion accessible BEFORE face selection.
// One operation owner: se430BeginnerAPI().convert(). No second geometry editor.
(function(){
 'use strict';
 let panel=null, button=null, detail=null, refreshing=false, readyPartId=null;
 const api=()=>se430BeginnerAPI();
 const stage=()=>window.SWYRL_ENGINE_INSET_TOP_STEPS_454?.inspect?.()?.step||'idle';
 const state=()=>{try{return api()?.inspect?.()||null;}catch{return null;}};
 function refresh(){
  if(!panel||!button||refreshing)return;
  refreshing=true;
  try{
   const s=state(),selection=s?.selection||{},isRim=stage()==='rim';
   const active=!!s?.preview?.active,canConvert=!!s?.convert?.available;
   const single=!!selection.partId&&(selection.objectCount??1)===1;
   const visible=isRim&&single&&!active&&canConvert;
   if(!isRim||!single||selection.partId!==readyPartId)readyPartId=null;
   const awaitingFace=isRim&&single&&selection.partId===readyPartId&&
    !selection.faceIds?.length&&!active;
   button.hidden=!visible;
   button.disabled=!visible;
   const baking=/bake.*vertex edit/i.test(s?.convert?.reason||'');
   button.textContent=baking?'Bake Edits & Continue':'Make Editable & Continue';
   button.title=s?.convert?.reason||'Convert this plain primitive into editable topology.';
   if(detail){
    // A selected protected mesh can explain why no conversion is offered.
    const protectedSource=isRim&&single&&!canConvert&&!active&&
      /authored|rig|skin|animated|invalid|independent|finish the current/i.test(s?.convert?.reason||'');
    detail.hidden=!(visible||protectedSource||awaitingFace);
    if(visible)detail.textContent=baking?
     'Your vertex edits will be baked with confirmation. Undo restores the original. No face selection is needed.':
     'Convert the selected primitive first, then tap any square face to preview the rim. Undo restores the original.';
    else if(protectedSource)detail.textContent=s.convert.reason;
    else if(awaitingFace)detail.textContent='Editable cube ready. Tap its square face to preview a rim. No other conversion is needed.';
   }
  }finally{refreshing=false;}
 }
 function convertAndContinue(){
  const s=state(),single=!!s?.selection?.partId&&(s.selection.objectCount??1)===1;
  if(stage()!=='rim'||!single||s?.preview?.active||!s?.convert?.available){
   const msg=s?.convert?.reason||'Select one plain cube and choose Inset first.';
   if(detail){detail.hidden=false;detail.textContent=msg;}
   return {ok:false,reason:msg};
  }
  // The native bridge remains the only source of truth for editable topology,
  // validation, history, and selected document/part identity.
  const hasEdits=/bake.*vertex edit/i.test(s.convert.reason||'');
  if(hasEdits){
   const accepted=typeof window.confirm==='function'&&window.confirm(
    'Bake saved vertex edits into an editable mesh? Plain UV coordinates will be regenerated. One Undo step restores the original edits.'
   );
   if(!accepted){
    if(detail){detail.hidden=false;detail.textContent='Conversion canceled. Original cube and edits unchanged.';}
    return {ok:false,reason:'Conversion canceled'};
   }
  }
  const before=s.selection.partId;
  const converted=api()?.convert();
  se430BeginnerResult(converted);
  const after=state();
  if(!converted?.ok||after?.selection?.partId!==before){
   if(detail){detail.hidden=false;detail.textContent=converted?.reason||'Conversion could not complete safely.';}
   refresh();return converted||{ok:false,reason:'Conversion failed'};
  }
  readyPartId=before;
  if(after.selection.mode!=='face'){
   // Native convert normally enters Face mode. Do not bypass its result.
   const selected=api()?.setComponentMode('face');
   if(!selected?.ok){se430BeginnerResult(selected);refresh();return selected;}
  }
  if(detail){detail.hidden=false;detail.textContent='Editable cube ready. Tap the square face you want to inset. Rim and depth stay in the same top controls.';}
  const hint=panel?.querySelector('#se454Hint');
  if(hint)hint.textContent='Editable cube ready. Tap a square face to preview its rim.';
  refresh();return converted;
 }
 function mount(p){
  if(!p||p.dataset.se456GuidedConversion==='1')return;
  const top=p.querySelector('#se454InsetTopBar');
  if(!top)return;
  panel=p;p.dataset.se456GuidedConversion='1';
  button=document.createElement('button');
  button.type='button';button.id='se456MakeEditable';
  button.hidden=true;button.disabled=true;
  button.textContent='Make Editable & Continue';
  button.setAttribute('aria-label','Convert selected cube into editable mesh and continue Inset');
  detail=document.createElement('p');detail.id='se456ConversionGuidance';
  detail.setAttribute('role','status');detail.setAttribute('aria-live','polite');
  detail.hidden=true;
  const slider=top.querySelector('.se454-slider-row');
  if(!slider)return;
  slider.before(button,detail);
  button.addEventListener('pointerdown',event=>event.stopPropagation());
  button.addEventListener('click',event=>{event.stopPropagation();convertAndContinue();});
  const quick=p.querySelector('#se445ShapeQuick');
  quick?.addEventListener('click',()=>queueMicrotask(refresh));
  window.addEventListener('swrlz:model-workshop-change',refresh);
  refresh();
 }
 const originalInstall=se430BeginnerInstall;
 se430BeginnerInstall=function(p){const result=originalInstall(p);mount(p);return result;};
 const originalRefresh=se430BeginnerRefresh;
 se430BeginnerRefresh=function(...args){
  const result=originalRefresh.apply(this,args);refresh();return result;
 };
 window.SWYRL_ENGINE_GUIDED_CONVERSION_456=Object.freeze({
  version:'v11.456',refresh,convert:convertAndContinue,
  inspect:()=>({installed:!!button,visible:!!button&&!button.hidden,
    stage:stage(),nativeGeometryOwner:'se430',conversionBeforeFace:true})
 });
})();
/* SE456_GUIDED_PRIMITIVE_CONVERSION_END */
