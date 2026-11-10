/* SE374_MODEL_VR_OWNER_FEEDBACK_START */
// Quest 2 field feedback: ray-driven menu windows, grouped selection bounds,
// visible gizmo ray contact, and first-level project saving navigation.
// Uses the existing XR scene/input frame. No native project/mesh mutations.
function se374GizmoContact(record,cast=null){
 const s=se340XR,g=s.se372Gizmo;
 if(!g?.root?.visible||!['move','rotate','scale'].includes(s.mode))return null;
 if(!cast)cast=se340Cast(record);
 if(!cast)return null;
 // Only visible handles in the active transform mode are pickable.
 let nearest=null;
 for(const hit of cast.intersectObjects(g.handles,false)){
  if(!hit.object.visible||!hit.object.userData?.se372Axis)continue;
  const axis=hit.object.userData.se372Axis;
  if(axis==='uniform'&&s.mode!=='scale')continue;
  nearest={gizmo:true,axis,point:hit.point.clone(),distance:hit.distance,object:hit.object};
  break;
 }
 return nearest;
}
function se374GroupBoundary(s,ids){
 if(!s.scene)return;
 if(!s.se374MultiOutline){
  const line=new THREE.Box3Helper(new THREE.Box3(),0xffd28a);
  line.name='Model VR · combined selection bounds';
  line.frustumCulled=false;line.renderOrder=9400;
  line.material.depthTest=false;line.material.depthWrite=false;
  line.material.transparent=true;line.material.opacity=1;
  line.userData.editorOnly=true;
  s.scene.add(line);s.se374MultiOutline=line;
 }
 const multi=ids.size>1,box=s.se374MultiOutline;
 box.visible=multi&&!s.selectedOutline.box.isEmpty();
 // Single selection keeps the original lighter helper; every additional
 // selected part enlarges the one shared group boundary.
 s.selectedOutline.visible=ids.size===1;
 if(!box.visible)return;
 const bounds=s.selectedOutline.box.clone(),length=bounds.getSize(new THREE.Vector3()).length();
 bounds.expandByScalar(Math.max(.008,Math.min(.035,length*.014)));
 box.box.copy(bounds);
 box.updateMatrixWorld(true);
}
function se374Dispose(){
 const line=se340XR.se374MultiOutline;
 if(line){line.removeFromParent();line.geometry?.dispose?.();line.material?.dispose?.();se340XR.se374MultiOutline=null;}
}
function se374MenuRayGripStart(g,hit){
 if(!hit?.point||!Number.isFinite(hit.distance))return;
 g.se374RayDistance=THREE.MathUtils.clamp(hit.distance,.20,3.5);
 g.se374PointOffset=g.start.clone().sub(hit.point);
}
function se374MenuRayGripUpdate(g){
 const ray=se340Cast(g.record);
 if(!ray||!Number.isFinite(g.se374RayDistance)||!g.se374PointOffset)return false;
 const next=ray.ray.at(g.se374RayDistance,new THREE.Vector3()).add(g.se374PointOffset);
 // Follow the controller pointer in space rather than the tiny 1:1 change
 // in grip position. The menu remains fully independent of the user's head
 // and loaded model once Grip is released.
 se340XR.ui.root.position.copy(next);
 se340XR.ui.root.updateWorldMatrix(true,true);
 return true;
}
/* SE374_MODEL_VR_OWNER_FEEDBACK_END */
