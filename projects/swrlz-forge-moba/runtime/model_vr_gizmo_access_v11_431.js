/* SE431_MODEL_VR_GIZMO_ACCESS_START */
// Comfortable controller targets use the same native axis/grip transaction.
// Pick shells never render or enter model geometry, history or serialization.
const se431VRGizmoWhite=new THREE.Color(0xffffff);
function se431VRGizmoVisible(object){
 for(let node=object;node;node=node.parent)if(node.visible===false)return false;
 return true;
}
se372MakeGizmo=function(){
 const s=se340XR,root=new THREE.Group();root.name='Model VR · accessible transform handles';
 root.userData.editorOnly=true;root.renderOrder=9100;s.scene.add(root);
 const handles=[],owned=[],picks=[];
 const colors={x:0xf26e73,y:0x7ce8ad,z:0x71abfa,uniform:0xffdeb1};
 const pickMaterial=new THREE.MeshBasicMaterial({side:THREE.DoubleSide});
 // Material invisibility suppresses drawing without changing ray geometry.
 pickMaterial.visible=false;owned.push(pickMaterial);
 function add(geometry,axis,role,position,quaternion,pickGeometry=null){
  const material=new THREE.MeshBasicMaterial({color:colors[axis],side:THREE.DoubleSide,
   transparent:true,opacity:.94,depthTest:false,depthWrite:false});
  const handle=new THREE.Mesh(geometry,material);handle.renderOrder=9100;
  handle.userData={editorOnly:true,se372Axis:axis,se431Role:role,se431Color:colors[axis]};
  if(position)handle.position.copy(position);if(quaternion)handle.quaternion.copy(quaternion);
  root.add(handle);handles.push(handle);owned.push(geometry,material);
  if(pickGeometry){
   const pick=new THREE.Mesh(pickGeometry,pickMaterial);pick.position.copy(handle.position);pick.quaternion.copy(handle.quaternion);
   pick.userData={editorOnly:true,se431Pick:true,se372Axis:axis,se431Source:handle};
   root.add(pick);picks.push(pick);owned.push(pickGeometry);
  }
  return handle;
 }
 for(const axis of ['x','y','z']){
  const direction=new THREE.Vector3(axis==='x'?1:0,axis==='y'?1:0,axis==='z'?1:0);
  const q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0),direction);
  const ringQ=new THREE.Quaternion();
  if(axis==='x')ringQ.setFromAxisAngle(new THREE.Vector3(0,1,0),Math.PI/2);
  if(axis==='y')ringQ.setFromAxisAngle(new THREE.Vector3(1,0,0),Math.PI/2);
  add(new THREE.TorusGeometry(.15,.009,8,64),axis,'rotate',null,ringQ,new THREE.TorusGeometry(.15,.023,8,64));
  // Leave the center clear: padded stems start away from the shared origin.
  add(new THREE.CylinderGeometry(.007,.007,.13,9),axis,'move',direction.clone().multiplyScalar(.10),q,
   new THREE.CylinderGeometry(.020,.020,.13,9));
  add(new THREE.ConeGeometry(.021,.042,12),axis,'move',direction.clone().multiplyScalar(.185),q,
   new THREE.SphereGeometry(.035,12,10));
 }
 add(new THREE.BoxGeometry(.052,.052,.052),'uniform','scale',null,null,new THREE.BoxGeometry(.082,.082,.082));
 root.visible=false;s.se372Gizmo={root,handles,owned,se431Picks:picks,se431Accessible:true};
};
const se431VRPreviousGizmoFrame=se372GizmoFrame;
se372GizmoFrame=function(s){
 se431VRPreviousGizmoFrame(s);
 const g=s.se372Gizmo;if(!g?.se431Accessible)return;
 const viewer=s.lastViewer?.position||s.anchor?.position;
 if(viewer?.isVector3){
  // Keep a useful angular size when the workbench moves, with bounded reach.
  const distance=viewer.distanceTo(g.root.position);
  g.root.scale.setScalar(THREE.MathUtils.clamp(distance*.95,.75,2.2));
 }
 const active=s.gesture?.kind==='group'?s.gesture.axis:null;
 const hovered=new Set((s.controllers||[]).filter(r=>r.targetTracked&&r.hit?.gizmo&&!r.hit?.ui).map(r=>r.hit.axis));
 for(const handle of g.handles){
  const axis=handle.userData.se372Axis,selected=active?axis===active:hovered.has(axis);
  handle.visible=g.root.visible&&handle.userData.se431Role===s.mode;
  handle.material.color.setHex(handle.userData.se431Color);
  if(selected)handle.material.color.lerp(se431VRGizmoWhite,.52);
  handle.material.opacity=active?(selected?1:.42):(selected?1:.94);
 }
 for(const pick of g.se431Picks)pick.visible=pick.userData.se431Source.visible;
 g.root.updateWorldMatrix(true,true);
};
se374GizmoContact=function(record,cast=null){
 const s=se340XR,g=s.se372Gizmo;
 if(!record?.targetTracked||!g?.root||!se431VRGizmoVisible(g.root)||!['move','rotate','scale'].includes(s.mode))return null;
 cast=cast||se340Cast(record);if(!cast)return null;
 // Both hover and the immediate grip query respect spatial menu ownership.
 const ui=s.ui;
 if(ui?.root&&se431VRGizmoVisible(ui.root)){
  const menu=ui.hitTest?ui.hitTest(cast):cast.intersectObjects(ui.targets||[],false);
  if(Array.isArray(menu)?menu.length:menu)return null;
 }
 // The independently movable Satchel Academy window has the same native
 // ownership as the main console (including its folded buttons).
 const quest=s.se413Quest;
 if(quest?.root?.parent&&se431VRGizmoVisible(quest.root)){
  quest.root.updateWorldMatrix(true,true);
  const surfaces=(quest.folded?quest.buttons:[...(quest.buttons||[]),quest.panel])
   .filter(item=>item&&item.parent===quest.root&&se431VRGizmoVisible(item));
  if(cast.intersectObjects(surfaces,false).length)return null;
 }
 const valid=hit=>{
  const source=hit.object.userData.se431Source||hit.object,axis=source.userData.se372Axis;
  return Number.isFinite(hit.distance)&&hit.distance>=Math.max(.01,cast.near||0)&&hit.distance<=Math.min(5,cast.far??5)&&
   se431VRGizmoVisible(source)&&source.userData.se431Role===s.mode&&
   (axis!=='uniform'||s.mode==='scale');
 };
 // An actual visible surface wins before expanded tolerance, avoiding a
 // neighboring padded ring/axis stealing an accurately aimed handle.
 const exact=cast.intersectObjects(g.handles,false).find(valid);
 const hit=exact||cast.intersectObjects(g.se431Picks||[],false).find(valid);
 if(!hit)return null;
 const object=hit.object.userData.se431Source||hit.object;
 return {gizmo:true,axis:object.userData.se372Axis,point:hit.point.clone(),distance:hit.distance,object,padded:!exact};
};
// The existing grip dispatcher and reticle consult precisely the same picker.
se372GizmoHit=function(record){return se374GizmoContact(record)?.axis||null;};
const se431VRPreviousPoll=se340Poll;
se340Poll=function(record,frame,dt){
 const result=se431VRPreviousPoll(record,frame,dt),hit=record.hit;
 const axis=record.targetTracked&&hit?.gizmo&&!hit?.ui?hit.axis:null;
 if(axis&&axis!==record.se431GizmoHover&&!se340XR.gesture)se340Pulse(record,.11,14);
 record.se431GizmoHover=axis;
 return result;
};
window.SWYRL_ENGINE_MODEL_VR_GIZMO_ACCESS=Object.freeze({inspect:()=>{
 const s=se340XR,g=s.se372Gizmo;
 g?.root?.updateWorldMatrix(true,true);
 return {version:'v11.431',mode:s.mode,visible:!!g?.root&&se431VRGizmoVisible(g.root),
  rootMatrixWorld:g?.root?.matrixWorld.toArray()||null,
  handles:(g?.handles||[]).map(h=>({axis:h.userData.se372Axis,role:h.userData.se431Role,
   visible:se431VRGizmoVisible(h),type:h.geometry.type,parameters:{...h.geometry.parameters},
   matrixWorld:h.matrixWorld.toArray(),center:h.getWorldPosition(new THREE.Vector3()).toArray()})),
  controllers:(s.controllers||[]).map(r=>({hand:r.input?.handedness||null,tracked:!!r.targetTracked,
   axis:r.hit?.gizmo&&!r.hit?.ui?r.hit.axis:null,padded:!!r.hit?.gizmo&&!!r.hit?.padded})),
  gesture:s.gesture?{kind:s.gesture.kind,mode:s.gesture.mode,axis:s.gesture.axis||null}:null};
}});
/* SE431_MODEL_VR_GIZMO_ACCESS_END */
