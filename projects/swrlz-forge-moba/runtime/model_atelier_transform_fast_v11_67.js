// §E v11.67: reuse existing native meshes for transform-only commits.
function atelierMeshRestoreLiveTransforms(records){
 if(!modelRoot||!Array.isArray(records))return;
 const map=new Map(records.map(r=>[r.id,r]));
 for(const mesh of modelRoot.children){
  if(!mesh.isMesh)continue;
  const value=map.get(mesh.userData.atelierId);
  if(!value)continue;
  mesh.position.set(...value.position);
  mesh.rotation.set(...value.rotation);
  mesh.scale.set(...value.scale);
  mesh.updateMatrixWorld(true);
 }
 for(const helper of modelRoot.children)
  if(helper instanceof THREE.BoxHelper)helper.update();
}
function atelierMeshTransformOnlyCommit(records){
 if(!model()||!modelRoot)return;
 atelierMeshRestoreLiveTransforms(records);
 model().editedAt='local';
 if(typeof markDirty==='function')markDirty();
 refreshInspector();
 const back=$m('Undo'),forward=$m('Redo');
 if(back)back.disabled=!undo.length;
 if(forward)forward.disabled=!redo.length;
 if(typeof atelierSculptVertexMode!=='undefined'&&atelierSculptVertexMode)
  atelierSculptOverlayRefresh();
 if(typeof atelierLassoOverlay!=='undefined'&&atelierLassoOverlay)
  atelierLassoOverlayRefresh();
 atelierMeshToolbarRefresh();
}
