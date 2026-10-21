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

function atelierMeshSelectFast(){
 if(!modelRoot)return;
 const chosen=modelRoot.children.find(m=>m.isMesh&&m.userData.atelierId===selection);
 const old=modelRoot.children.filter(m=>m instanceof THREE.BoxHelper);
 let outline=old.shift()||null;
 for(const extra of old){
  modelRoot.remove(extra);
  extra.geometry?.dispose();extra.material?.dispose();
 }
 if(!chosen){
  if(outline){modelRoot.remove(outline);outline.geometry?.dispose();outline.material?.dispose();}
  return;
 }
 if(!outline){
  outline=new THREE.BoxHelper(chosen,0xe8f56f);
  outline.userData.atelierHelper=true;
  modelRoot.add(outline);
 }else{
  outline.setFromObject(chosen);
 }
 outline.update();
}
