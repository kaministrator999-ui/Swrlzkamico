/* SE478_RING_HEIGHT_SLIDER_START */
// Floating vertex-height controller shared by Extrude and Inset's ring / filled
// ring selection shapes. Never edits the source until native Apply succeeds.
(function se478RingHeightSlider(){
 'use strict';
 let ui=null,range=null,readout=null,applyButton=null,cancelButton=null,description=null;
 let owned=false,desired=0,queued=false,selectionKey='';
 const workshop=()=>window.SWYRL_ENGINE_MODEL_WORKSHOP;
 const modes=()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.();
 function current(){
  const state=modes(),part=partById(selection);
  if(!state?.operation||!['Extrude','Inset'].includes(state.tool)||
     state.selectionType!=='vertex'||!['ring','fill'].includes(state.shape)||
     atelierComponentMode!=='vertex'||!atelierComponentSupported()||
     part?.kind!=='topologyMesh'||!atelierComponentIds.length)return null;
  return {operation:state.tool,shape:state.shape,partId:part.id,
   ids:[...new Set(atelierComponentIds)]};
 }
 function mounted(){
  if(ui?.isConnected)return true;
  const body=panel?.querySelector('.atelier-body');
  if(!body)return false;
  ui=document.createElement('section');ui.id='se478RingHeightSlider';
  ui.className='se478-ring-height';ui.hidden=true;
  ui.setAttribute('aria-label','Selected ring height');
  const head=document.createElement('div');head.className='se478-height-header';
  const title=document.createElement('strong');title.textContent='Ring height';
  description=document.createElement('output');description.className='se478-height-count';
  head.append(title,description);
  const row=document.createElement('div');row.className='se478-height-row';
  const label=document.createElement('label');label.htmlFor='se478HeightRange';label.textContent='Raise / lower';
  range=document.createElement('input');range.id='se478HeightRange';range.type='range';
  range.min='-10';range.max='10';range.step='0.01';range.value='0';
  range.setAttribute('aria-label','Raise or lower every selected vertex along local Y');
  readout=document.createElement('output');readout.id='se478HeightValue';
  readout.htmlFor='se478HeightRange';readout.textContent='+0.00';
  row.append(label,range,readout);
  const actions=document.createElement('div');actions.className='se478-height-actions';
  applyButton=document.createElement('button');applyButton.type='button';
  applyButton.textContent='Apply height';applyButton.disabled=true;
  cancelButton=document.createElement('button');cancelButton.type='button';
  cancelButton.textContent='Cancel';cancelButton.disabled=true;
  const note=document.createElement('small');
  note.textContent='Live vertex-height preview · local Y · one Undo step';
  actions.append(applyButton,cancelButton,note);
  // Portal to the modeler panel, not the isolated grid: phone inspector
  // must never intercept input for the active height slider.
  ui.append(head,row,actions);panel.append(ui);
  // UI interactions must never select objects behind the floating control.
  for(const type of ['pointerdown','pointerup','click']){
   ui.addEventListener(type,event=>event.stopPropagation());
  }
  range.addEventListener('input',()=>{
   desired=Number(range.value);
   readout.textContent=(desired>=0?'+':'')+desired.toFixed(2);
   if(!queued){queued=true;requestAnimationFrame(flush);}
  });
  applyButton.addEventListener('click',()=>{
   if(!owned)return;
   const result=workshop()?.apply?.();
   if(result?.ok){owned=false;reset();sync();}
   else if(result)status(result.reason||result.error||'Could not apply selected height.',true);
  });
  cancelButton.addEventListener('click',()=>{
   if(owned){workshop()?.cancel?.();owned=false;}
   reset();sync();
  });
  return true;
 }
 function reset(){
  desired=0;
  if(range)range.value='0';
  if(readout)readout.textContent='+0.00';
  if(applyButton)applyButton.disabled=true;
  if(cancelButton)cancelButton.disabled=true;
 }
 function sync(){
  if(!mounted())return;
  const choice=current(),preview=workshop()?.inspect?.()?.preview;
  if(owned&&(!preview?.active||preview.operation!=='ringTransform')){owned=false;reset();}
  // Do not offer to hijack an unrelated face/inset/extrude preview.
  const conflict=preview?.active&&!owned;
  ui.hidden=!choice||conflict;
  if(ui.hidden){selectionKey='';return;}
  const key=[choice.partId,choice.operation,choice.shape,choice.ids.join(',')].join('|');
  if(key!==selectionKey&&!owned)reset();
  selectionKey=key;
  description.textContent=(choice.shape==='fill'?'Filled circle · ':'Ring · ')+
   choice.ids.length+' vertices · '+choice.operation;
  applyButton.disabled=!owned;
  cancelButton.disabled=!owned;
 }
 function flush(){
  queued=false;
  const choice=current();
  if(!choice){sync();return;}
  const native=workshop(),preview=native?.inspect?.()?.preview;
  if(preview?.active&&!owned){sync();return;}
  if(Math.abs(desired)<0.000001){
   if(owned){native.cancel();owned=false;}
   sync();return;
  }
  // RingTransform changes positions of exactly the selected topology vertices,
  // without incorrectly adding faces for an interior (filled) selection.
  const result=native?.preview?.('ringTransform',{
   offset:[0,desired,0],scale:1,leftScale:1,rightScale:1,
   tilt:[0,0,0],falloff:0
  });
  if(result?.ok)owned=true;
  else{status(result?.reason||result?.error||'Height preview unavailable.',true);}
  sync();
 }
 window.addEventListener('swrlz:model-workshop-change',sync);
 window.addEventListener('resize',sync);
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',sync,{once:true});
 else sync();
 window.SWYRL_ENGINE_RING_HEIGHT_478=Object.freeze({
  inspect:()=>({visible:!!ui&&!ui.hidden,operation:current()?.operation||null,
   shape:current()?.shape||null,selectedCount:current()?.ids.length||0,
   offset:desired,previewOwned:owned}),
  previewHeight:value=>{
   if(!mounted()||!current()||!Number.isFinite(value)||value< -10||value>10)
    return {ok:false,reason:'Select an editable ring or filled ring first.'};
   desired=value;range.value=String(value);
   readout.textContent=(desired>=0?'+':'')+desired.toFixed(2);
   flush();return {ok:owned||desired===0};
  },
  sync
 });
})();
/* SE478_RING_HEIGHT_SLIDER_END */
