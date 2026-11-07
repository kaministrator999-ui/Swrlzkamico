/* SE304_MODELER_DOCUMENT_VIEW_SYNC_START */
// A native document can be replaced while Model Atelier is already visible.
// Its open() fast path intentionally keeps the current renderer. Track what
// that renderer actually projects instead of mistaking visible UI for a sync.
let se304RenderedModel=null,se304RenderedParts=null,se304RenderedRoot=null;
const se304RenderPartsBase=renderParts;
renderParts=function(...args){
  const result=se304RenderPartsBase(...args);
  const active=model();
  if(modelRoot&&active){
    se304RenderedModel=active;se304RenderedParts=active.parts;se304RenderedRoot=modelRoot;
  }
  return result;
};
function se304ClearDocumentViewTargets(){
  // These are derived editor targets, never document/history fields. Do not
  // call drag-cancel/Undo handlers: they can restore an old document's values.
  selection=null;pressed=null;
  atelierMeshIds=[];atelierMeshAdding=false;atelierGroupCurrent=null;
  atelierMeshDrag=null;atelierMeshPivot=null;atelierMeshDensityShownPart=null;
  atelierComponentIds=[];atelierComponentPartId=null;
  atelierComponentGesture=null;atelierComponentDrag=null;atelierComponentPivot=null;
  atelierSculptVertexIDs=[];atelierSculptLastVertexPart=null;atelierSculptDrag=null;
  atelierSculptHit=null;atelierLassoArm=null;atelierLassoPending=[];
  atelierLassoActive=null;atelierLassoDrag=null;atelierLassoTempPin=null;
  atelierLassoSelectedPin=0;atelierLassoFreehand=null;
  atelierViewportGizmoDrag=null;atelierDesktopDrag=null;atelierPaintDrag=null;
  atelierPrecisionGizmoDrag=null;atelierPrecisionGuardTap=null;
  atelierCameraTouches.clear();atelierCameraConsumedTouches.clear();
  atelierCameraGesture=null;atelierCameraMousePan=null;
  atelierCameraInterior=false;atelierInteriorPartId=null;
  atelierInteriorPreviousMode=null;atelierInteriorPreviousCamera=null;
  atelierDetailTarget=null;atelierCameraPan.set(0,0,0);
  atelierViewOverrides.clear();atelierViewMaterialOverrides.clear();
  atelierComponentOverlayClear();atelierSculptOverlayClear();
  atelierLassoOverlayClear();atelierMeshGizmoClear();
}
const se304SyncProjectBase=syncProject;
syncProject=function(...args){
  const result=se304SyncProjectBase(...args);
  const active=model();
  if(!panel||panel.hidden||!renderer||!modelRoot||!active){
    se304RenderedModel=null;se304RenderedParts=null;se304RenderedRoot=null;
    return result;
  }
  if(!Array.isArray(active.parts))return result;
  if(active===se304RenderedModel&&active.parts===se304RenderedParts&&modelRoot===se304RenderedRoot)return result;
  se304ClearDocumentViewTargets();
  renderParts();refreshList();refreshInspector();cameraUpdate();
  if(world&&camera)renderer.render(world,camera);
  return result;
};
/* SE304_MODELER_DOCUMENT_VIEW_SYNC_END */
