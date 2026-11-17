/* SE480_EDITABLE_ENTRY_START */
// Native source-of-truth conversion entry for the progressive Model Studio.
// The old Inset-only conversion CTA is not reachable from Vertex Ring tools.
// This adds a contextual entry, NOT a second conversion implementation.
(function se480EditableEntry(){
 'use strict';
 const workshop=()=>window.SWYRL_ENGINE_MODEL_WORKSHOP;
 const progressive=()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.();
 let panel=null,scene=null,card=null,button=null,reason=null,heading=null,queued=false;
 let watchedPanel=null,listening=false;
 let lastStatus='';
 const write=(node,value)=>{
  if(node&&node.textContent!==value)node.textContent=value;
 };
 function place(){
  if(!card||card.hidden||!scene?.isConnected)return;
  const sr=scene.getBoundingClientRect(),shape=panel?.querySelector('#se477SelectionShapes');
  const topbar=panel?.querySelector('#se474SpecificModes');
  const lower=[shape,topbar].filter(el=>el&&!el.hidden)
    .map(el=>el.getBoundingClientRect().bottom);
  // The persistent camera bar and selection bars use independent layout
  // owners; never cover them or anchor against the full browser viewport.
  const bottom=Math.max(sr.top, ...lower);
  const offset=Math.max(7,Math.min(sr.height-68,bottom-sr.top+7));
  card.style.setProperty('--se480-y',Math.round(offset)+'px');
 }
 function refresh(){
  if(!panel?.isConnected||!card?.isConnected)return;
  const state=progressive(),api=workshop(),native=api?.inspect?.();
  const active=!!state?.operation&&
   ['Extrude','Inset'].includes(state.tool)&&
   ['vertex','face','edge'].includes(state.selectionType);
  const selected=native?.selection,part=selected?.partId?partById(selected.partId):null;
  const already=part?.kind==='topologyMesh';
  card.hidden=!active||already;
  if(card.hidden){lastStatus='';return;}
  const converting=!!native?.convert?.available&&!native?.preview?.active;
  const preview=!!native?.preview?.active;
  const named=selected?.name||part?.name||'selected mesh';
  let message;
  if(!part)message='Select one mesh in the viewport or Meshes list first.';
  else if(preview)message='Apply or Cancel the active preview before converting another mesh.';
  else if(converting)message=
   /bake.*vertex edit/i.test(native.convert.reason||'')?
    'This mesh has saved vertex edits. Conversion can bake them into editable topology with confirmation and an Undo checkpoint.':
    'Convert '+named+' into indexed editable topology. Conversion regenerates plain UVs; Undo restores the original primitive.';
  else message=native?.convert?.reason||
    'The selected model cannot be converted by the current native topology tool.';
  heading.textContent=converting?'Make mesh editable':'Editable mesh needed';
  button.disabled=!converting;
  write(button,/bake.*vertex edit/i.test(native?.convert?.reason||'')?'Bake edits & make editable':'Make mesh editable');
  write(reason,message);
  button.title=message;
  card.dataset.se480Ready=converting?'true':'false';
  card.dataset.se480Blocked=part&&!converting?'true':'false';
  lastStatus=message;
  place();
 }
 function convert(){
  const api=workshop(),s=api?.inspect?.();
  if(!s?.convert?.available||s?.preview?.active){
   refresh();return {ok:false,reason:s?.convert?.reason||'This mesh cannot be converted safely.'};
  }
  const prompt=/bake.*vertex edit/i.test(s.convert.reason||'')?
   'Bake the saved vertex edits into editable topology? Plain UV coordinates will be regenerated. Undo restores the original edits.':
   'Convert this mesh to editable topology? Plain UV coordinates will be regenerated. Undo restores the original primitive.';
  if(typeof window.confirm!=='function'||!window.confirm(prompt))
   return {ok:false,cancelled:true,reason:'Conversion cancelled; original mesh unchanged.'};
  const before=s.selection?.partId;
  // Only the original native guarded conversion writes geometry/UVs/history.
  const result=api.convert();
  if(!result?.ok){
   write(reason,result?.reason||result?.error||'Native conversion unavailable.');
   refresh();return result||{ok:false,reason:'Native conversion unavailable.'};
  }
  // Native conversion intentionally enters Face mode. Restore the active
  // progressive Vertex tool so the next rim tap can select REAL topology.
  const mode=progressive()?.selectionType||'vertex';
  if(['vertex','edge','face'].includes(mode)&&api.inspect()?.selection?.mode!==mode)
   api.setComponentMode(mode);
  if(mode==='vertex')window.SWYRL_ENGINE_VERTEX_ENTRY_477?.activate?.();
  card.hidden=true;
  window.SWYRL_ENGINE_RING_HEIGHT_478?.sync?.();
  refresh();
  if(typeof status==='function')status(
   'Editable mesh ready. Tap a vertex on its rim or choose a face for Extrude. Undo restores the original primitive.'
  );
  return {ok:true,converted:true,partId:before};
 }
 function mount(){
  const p=document.getElementById('modelAtelierPanel');
  const target=p?.querySelector('.atelier-scene');
  if(!p||!target)return false;
  if(panel===p&&scene===target&&card?.isConnected)return true;
  panel=p;scene=target;
  card=document.createElement('section');card.id='se480EditableEntry';
  card.setAttribute('role','group');card.setAttribute('aria-label','Mesh conversion for active modeling tool');
  card.hidden=true;
  heading=document.createElement('strong');heading.id='se480EditableHeading';
  button=document.createElement('button');button.type='button';button.id='se480MakeEditable';
  reason=document.createElement('p');reason.id='se480EditableReason';
  reason.setAttribute('role','status');reason.setAttribute('aria-live','polite');
  card.append(heading,button,reason);scene.append(card);
  for(const event of ['pointerdown','pointerup','click','touchstart']){
   card.addEventListener(event,e=>e.stopPropagation());
  }
  button.addEventListener('click',convert);
  refresh();
  return true;
 }
 function schedule(){
  if(queued)return;queued=true;
  queueMicrotask(()=>{queued=false;if(mount()){watch();refresh();}});
 }
 function watch(){
  const p=document.getElementById('modelAtelierPanel');
  if(!p||watchedPanel===p)return;
  watchedPanel=p;
  new MutationObserver(records=>{
   if(records.some(x=>[
    'data-se477-selection-type','data-se477-selection-shape','data-se477-operation',
    'data-se474-settings-open','data-se251-layout'].includes(x.attributeName)))schedule();
  }).observe(p,{attributes:true});
  if(!listening){
   listening=true;
   window.addEventListener('swrlz:model-workshop-change',schedule);
   window.addEventListener('resize',schedule,{passive:true});
   window.addEventListener('orientationchange',schedule,{passive:true});
  }
 }
 // The modeler panel is mounted asynchronously after the account/startup gate.
 // DOMContentLoaded alone is too early. Reuse the native modeler install hook
 // and a bounded observer that stops scheduling once our card is connected.
 const previousInstall=se430BeginnerInstall;
 se430BeginnerInstall=function(p){
  const result=previousInstall.apply(this,arguments);
  schedule();
  return result;
 };
 function watchRoot(){
  const host=document.body;
  if(!host)return;
  new MutationObserver(records=>{
   if(card?.isConnected)return;
   if(records.some(record=>record.addedNodes.length))schedule();
  }).observe(host,{childList:true,subtree:true});
 }
 if(document.readyState==='loading')
  document.addEventListener('DOMContentLoaded',()=>{schedule();watchRoot();},{once:true});
 else{schedule();watchRoot();}
 window.SWYRL_ENGINE_EDITABLE_ENTRY_480=Object.freeze({
  inspect:()=>({visible:!!card&&!card.hidden,enabled:!!button&&!button.disabled,
   message:lastStatus,partId:workshop()?.inspect?.()?.selection?.partId||null,
   conversionAvailable:workshop()?.inspect?.()?.convert?.available===true}),
  convert,refresh:schedule
 });
})();
/* SE480_EDITABLE_ENTRY_END */
