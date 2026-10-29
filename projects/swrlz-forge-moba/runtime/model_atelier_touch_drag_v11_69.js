// §E v11.69 — event-driven transform preview: keep the rendered scene and
// native selection outline in sync with the captured axis handle on EVERY
// pointermove. Avoid bounding-box recomputation on every drag event.
let atelierLiveDragPointerUpdates=0,atelierLiveDragRenderUpdates=0;
function atelierMeshLiveDragPreview(records){
 const drag=atelierMeshDrag;
 if(!drag||!modelRoot)return;
 const byId=new Map(records.map(value=>[value.id,value]));
 for(const mesh of modelRoot.children){
  if(!mesh.isMesh)continue;
  const values=byId.get(mesh.userData.atelierId);
  if(!values)continue;
  mesh.position.fromArray(values.position);
  mesh.rotation.set(...values.rotation);
  mesh.scale.fromArray(values.scale);
  mesh.updateMatrixWorld(true);
 }
 const target=drag.pivot.clone();
 if(drag.mode==='move'&&atelierMeshAxes[drag.axis]){
  const axis=atelierMeshAxes[drag.axis];
  target.x+=axis[0]*drag.amount;
  target.y+=axis[1]*drag.amount;
  target.z+=axis[2]*drag.amount;
 }
 if(atelierMeshPivot)atelierMeshPivot.copy(target);
 if(atelierMeshGizmo){
  atelierMeshGizmo.position.copy(target);
  atelierMeshGizmo.updateMatrixWorld(true);
 }
 // The source model owns one native selection helper; only adjust it here.
 for(const helper of modelRoot.children)
  if(helper instanceof THREE.BoxHelper)helper.update();
 atelierLiveDragPointerUpdates++;
 // Explicitly paint the lightweight transform on pointermove. Android's
 // embedded browser can defer an ordinary animation-frame paint until
 // after a touch interaction; this does NOT rebuild the model or materials.
 if(renderer&&world&&camera&&(!panel||!panel.hidden)){
  renderer.render(world,camera);
  atelierLiveDragRenderUpdates++;
 }
}
window.SWYRL_ENGINE_MESH_DRAG_DIAGNOSTICS=Object.freeze({
 status:()=>({pointerUpdates:atelierLiveDragPointerUpdates,
  drawnFrames:atelierLiveDragRenderUpdates,
  dragging:!!atelierMeshDrag})
});
