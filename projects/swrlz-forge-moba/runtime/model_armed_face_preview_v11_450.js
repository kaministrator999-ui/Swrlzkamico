/* SE450_ARMED_FACE_PREVIEW_START */
// Inset/Extrude are tools, not dead-end menu selections. Choose a tool,
// then tap a region to get the native geometry preview (still requires Apply).
let se450ArmedFaceOperation=null,se450ArmedFacePart=null;
function se450ArmFacePreview(operation,partId){
 se450ArmedFaceOperation=operation;se450ArmedFacePart=partId;
}
function se450RunArmedFacePreview(){
 const operation=se450ArmedFaceOperation,part=se450ArmedFacePart;
 if(!operation||!part)return;
 const api=se430BeginnerAPI(),state=api?.inspect?.();
 if(!state||state.selection.partId!==part||state.preview.active){
  se450ArmedFaceOperation=null;se450ArmedFacePart=null;return;
 }
 if(state.selection.mode!=='face'||!state.selection.faceIds?.length)return;
 const availability=state.operations?.[operation];
 if(!availability?.available){
  status(availability?.reason||'Select a flat face region for '+operation+'.',true);
  return;
 }
 const input=document.getElementById('modelAtelierWorkshopAmount');
 const n=Number(input?.value);
 const options=Number.isFinite(n)?{amount:n}:{};
 se450ArmedFaceOperation=null;se450ArmedFacePart=null;
 const result=api.preview(operation,options);
 if(result?.ok){
  status(operation.charAt(0).toUpperCase()+operation.slice(1)+' preview visible. Use Apply geometry to commit or Cancel preview to discard.');
 }else status(result?.reason||'Unable to preview '+operation+'.',true);
 se430BeginnerQueue();
}
function se450AfterPlanarFaceTap(result,hitId,partId){
 if(!se450ArmedFaceOperation||se450ArmedFacePart!==partId)return result;
 let selected=result;
 if(!selected?.ok){
  const api=se430BeginnerAPI(),state=api?.inspect?.();
  if(state?.convert?.available){
   const edited=/bake.*vertex edit/i.test(state.convert.reason||'');
   if(edited&&(!window.confirm||!window.confirm('This mesh has vertex edits. Bake the visible shape into editable topology with an Undo checkpoint before previewing the selected face?')))
    return {ok:false,reason:'Conversion canceled; original vertex edits preserved.'};
   const conversion=api.convert();
   if(!conversion?.ok)return conversion;
   selected=api.selectRegion(hitId,partId);
  }
 }
 if(selected?.ok)queueMicrotask(se450RunArmedFacePreview);
 return selected;
}
/* SE450_ARMED_FACE_PREVIEW_END */
