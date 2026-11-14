/* SE448_INSET_ACTION_ROUTING_START */
// The Shape/Face quick buttons choose a real native operation AND preview it
// when a face was already selected. They never commit geometry themselves.
// A primitive's existing per-vertex edits can be explicitly baked (with Undo)
// into welded topology; painted/rigged/otherwise authored assets stay blocked.
function se448ShapeQuickActivate(faceQuick,operation){
 const hint=faceQuick?.querySelector('.se445-shape-hint');
 const say=value=>se430BeginnerWrite(hint,value);
 const api=se430BeginnerAPI(),first=api?.inspect();
 if(!first){say('Open a Model Studio project first.');return {ok:false,reason:'No project'};}
 if(first.preview.active){say('Apply or Cancel the current preview first.');return {ok:false,reason:'Preview active'};}
 if(first.selection.objectCount>1){say('Choose one mesh to edit its faces.');return {ok:false,reason:'Multiple objects'};}
 if(!first.selection.partId){say('Select a mesh, then tap a square face before choosing '+operation+'.');return {ok:false,reason:'No mesh'};}
 const partId=first.selection.partId;
 const seed=first.selection.mode==='face'&&Number.isInteger(first.selection.ids[0])?first.selection.ids[0]:null;
 // Use the native operation chooser even if we cannot yet run a preview.
 se430BeginnerNavigate(operation);
 if(first.selection.mode!=='face'){
  api.setComponentMode('face');
  say('Face mode selected. Tap a face on the mesh, then choose '+operation+' again to preview.');
  se430BeginnerQueue();
  return {ok:false,reason:'Choose face'};
 }
 if(seed===null){
  say('Tap a square face first, then choose '+operation+' again to preview.');
  se430BeginnerQueue();
  return {ok:false,reason:'Choose face'};
 }
 let state=api.inspect();
 if(state.convert?.available){
  const baking=/bake.*vertex edit/i.test(state.convert.reason||'');
  if(baking){
   const accepted=typeof window.confirm==='function'&&window.confirm(
    'This mesh has saved vertex edits. Convert will preserve the visible shape by baking them into editable topology, regenerate plain UVs, and store one Undo step. Continue?'
   );
   if(!accepted){say('Conversion canceled. Your original vertex edits are unchanged.');return {ok:false,reason:'Conversion canceled'};}
  }
  const converted=api.convert();
  if(!converted?.ok){
   say(converted?.reason||'Could not make this mesh editable.');
   return converted||{ok:false,reason:'Convert failed'};
  }
  const selected=api.selectRegion(seed,partId);
  if(!selected?.ok){
   say((selected?.reason||'Could not recover the selected face.')+' Your original mesh is available with Undo.');
   return selected||{ok:false,reason:'Face selection unavailable'};
  }
  state=api.inspect();
 }
 const available=state.operations?.[operation];
 if(!available?.available){
  const reason=available?.reason||'Tap a flat face on editable geometry first.';
  say(reason);
  se430BeginnerQueue();
  return {ok:false,reason};
 }
 const control=document.getElementById('modelAtelierWorkshopAmount');
 const value=Number(control?.value),params=Number.isFinite(value)?{amount:value}:{};
 const preview=api.preview(operation,params);
 if(preview?.ok)say(operation.charAt(0).toUpperCase()+operation.slice(1)+' preview ready. Inspect the result, adjust the amount or tap Apply geometry. Undo restores applied edits.');
 else say(preview?.reason||'The geometry preview could not be built.');
 se430BeginnerQueue();
 return preview||{ok:false,reason:'Preview unavailable'};
}
window.SWYRL_ENGINE_SHAPE_QUICK_448=Object.freeze({version:'v11.448',mode:'preview only',conversion:'explicit bake, Undo safe'});
/* SE448_INSET_ACTION_ROUTING_END */
