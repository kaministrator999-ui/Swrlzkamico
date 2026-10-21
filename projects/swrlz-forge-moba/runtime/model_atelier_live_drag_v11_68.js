// §E v11.68 — visible native mesh/gizmo drag feedback, no full rebuild.
function atelierMeshLiveDragPreview(records){
 if(!modelRoot||!atelierMeshDrag)return;
 // Update the SAME scene meshes used by WebGLRenderer. Force world matrices
 // and the original native selection outline to follow on every pointer move.
 atelierMeshRestoreLiveTransforms(records);
 // Handle translation/group transforms without destroying gizmo handle objects
 // during a captured drag. Rotation/scale around pivot keeps the same center.
 if(atelierMeshGizmo){
  const center=atelierMeshCenter(atelierMeshSelectedMeshes());
  if(center){
   atelierMeshGizmo.position.copy(center);
   atelierMeshGizmo.updateMatrixWorld(true);
   if(atelierMeshPivot)atelierMeshPivot.copy(center);
  }
 }
}
