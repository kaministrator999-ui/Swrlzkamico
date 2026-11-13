/* SE436_VR_CUBE_EXTRUDE_START */
// Draw-outline Extrude historically ignored a normal cube. Route only a
// selected plain cube or topology body to the existing native face workshop.
const se436PreviousModelXRAction=se340ModelXRAction;
se340ModelXRAction=function(action,record=null){
 const s=se340XR;
 if(action!=='extrude'||s.se430Manual||!s.session||!s.scene||!se340VisibleSession())
  return se436PreviousModelXRAction(action,record);
 const api=ModelAtelier?.workshop,selection=api?.inspect()?.selection;
 const part=currentProject?.modelAtelier?.parts?.find(p=>p.id===selection?.partId);
 // Keep the authored outline-extrusion flow for non-cube geometry.
 if(!part||!['box','topologyMesh'].includes(part.kind))return se436PreviousModelXRAction(action,record);
 if(!se436PreviousModelXRAction('manual-mesh',record))return false;
 if(part.kind==='box'){
  const converted=api.convert();
  if(!converted?.ok){
   se340Notice(converted?.reason||'This cube cannot be converted safely. No edit was applied.',true);
   se340SyncUI();se340Publish();return true;
  }
  se350Invalidate();
 }
 se436PreviousModelXRAction('manual-extrude',record);
 se340Notice('Cube face Extrude ready · Trigger to select a face, then Preview and Apply. For a hollow pouch, Inset the top first; use In/out for negative depth.');
 se340SyncUI();se340Publish();return true;
};
window.SWYRL_ENGINE_MODEL_VR_CUBE_EXTRUDE_436=Object.freeze({inspect:()=>({
 version:'v11.436',mode:se340XR.mode,manual:!!se340XR.se430Manual,
 operation:se340XR.se430Operation,selected:ModelAtelier?.workshop?.inspect()?.selection?.partId||null
})});
/* SE436_VR_CUBE_EXTRUDE_END */
