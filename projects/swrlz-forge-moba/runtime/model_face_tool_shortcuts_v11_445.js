/* SE445_SCULPT_FACE_SHORTCUTS_START */
// VR three-stage operation entries enter the existing native face workshop.
// This is navigation only: no geometry is changed by picking a tool.
(function(){
 'use strict';
 const previousAction=se340ModelXRAction;
 const faceOperations=new Set(['manual-inset','manual-extrude','manual-solidify','manual-subdivide','manual-deleteFaces','manual-repairNormals','manual-convert','manual-pick','manual-learn']);
 se340ModelXRAction=function(action,record=null){
  if(faceOperations.has(action)&&!se340XR.se430Manual){
   if(!previousAction('manual-mesh',record))return false;
   const api=se430VRWorkshop(),state=api?.inspect?.();
   if(state?.selection?.partId&&state.selection.mode!=='face'&&state.selection.objectCount<=1){
    const switched=api.setComponentMode('face');
    if(switched?.ok===false){se340Notice(switched.reason||'Choose Face mode.',true);return false;}
   }
  }
  return previousAction(action,record);
 };
 window.SWYRL_ENGINE_FACE_TOOLS_445=Object.freeze({
  version:'v11.445',
  sculptShortcuts:['manual-inset','manual-extrude','manual-solidify','manual-subdivide'],
  operationFlow:'native face select > preview > apply/cancel > undo',
  modelEditsOnShortcut:false
 });
})();
/* SE445_SCULPT_FACE_SHORTCUTS_END */
