// §E v11.198 — native Quest spatial editor: smooth free-flight,
// controller-grip 6DoF moving, ray-selectable XYZ handles, in-headset legend.
// Runs inside the existing renderer/scene/session. Nothing writes projects
// outside native beginTransaction/commitTransaction on actual movement.
const se198={
  speed:3.2,speeds:[1.5,3.2,6.4,12.8],turnDegrees:20,boostMultiplier:2.6,
  velocity:new THREE.Vector3(),lastFrame:0,moves:0,boosts:0,
  directGrabs:0,axisDrags:0,drag:null,grab:null,
  axisGroup:null,axisMeshes:[],legend:null,legendTexture:null,legendParent:null,
  lastSelection:null,hiddenHelpers:[],helpersScanned:false,
  inputHooks:new Map(),lastError:'',lastAction:''
};
function se198Editor(){
 return !!se181XR.session&&renderer.xr.isPresenting &&
  !playing&&!simulating && !se193XRGameActive()&&!se193XRMenuActive()&&
  !se193.editorCaptureOpen&&!se195.photo;
}
function se198Clamp(n,a,b){return Math.min(b,Math.max(a,n));}
function se198RestoreSettings(){
 try{
  const d=JSON.parse(localStorage.getItem('swyrl.xr.editor.fly.v2')||'null');
  if(d&&se198.speeds.includes(d.speed))se198.speed=d.speed;
  if(d&&[15,20,30,45].includes(d.turnDegrees))se198.turnDegrees=d.turnDegrees;
 }catch(_){}
}
function se198SaveSettings(){
 try{localStorage.setItem('swyrl.xr.editor.fly.v2',JSON.stringify({
  speed:se198.speed,turnDegrees:se198.turnDegrees}));}catch(_){}
}
se198RestoreSettings();
function se198IsValidActor(o){
 return !!o?.isObject3D&&o.visible!==false&&
  o.userData?.actorType!=='ground'&&o.userData?.type!=='ground'&&
  Array.isArray(actors)&&actors.includes(o);
}
function se198Selected(){return se198IsValidActor(selected)?selected:null;}
function se198GripPose(record){
 const ctl=record?.controller;
 if(!ctl)return null;
 ctl.updateMatrixWorld(true);
 return ctl.getWorldPosition(new THREE.Vector3());
}
function se198FinishGrab(commit=true){
 const state=se198.grab;
 if(!state)return;
 se198.grab=null;
 try{
  if(commit&&state.started&&state.moved){
   const parent=state.actor.parent;
   const end=state.target||state.actor.getWorldPosition(new THREE.Vector3());
   state.actor.position.copy(parent?parent.worldToLocal(end.clone()):end);
   state.actor.userData.spawnPos=state.actor.position.toArray();
   commitTransaction('VR free move '+state.actor.name);
   rebuildHierarchy();syncInspector();refreshDebug();
   se198.lastAction='Placed '+state.actor.name;
  }
 }catch(e){se198.lastError='VR grab commit: '+String(e?.message||e).slice(0,120);}
}
function se198GrabFrame(record){
 // No selection, grab or transform while a UI is open, in VR Play,
 // or when editing is disabled. Keep the old scene unchanged.
 if(!record||record.input?.handedness!=='right')return;
 if(!se198Editor()||se195.visible||se198.drag){
  se198FinishGrab(true);return;
 }
 const holding=se192Pressed(record,1);
 if(!holding){se198FinishGrab(true);return;}
 const hand=se198GripPose(record);
 if(!hand)return;
 let g=se198.grab;
 if(!g){
  const hit=se192Raycast(record);
  if(hit?.ui||hit?.exit||hit?.gizmoAxis)return;
  const actor=se198IsValidActor(hit?.object)?hit.object:se198Selected();
  if(!actor)return;
  g={actor,handStart:hand.clone(),
   worldStart:actor.getWorldPosition(new THREE.Vector3()),
   moved:false,started:false,target:null};
  se198.grab=g;
  selectActor(actor);se198.directGrabs++;
 }
 if(g.actor.parent===null||!se198IsValidActor(g.actor)){
  se198FinishGrab(false);return;
 }
 const target=g.worldStart.clone().add(hand.sub(g.handStart));
 if(![target.x,target.y,target.z].every(Number.isFinite)||target.length()>1000)return;
 if(target.distanceTo(g.worldStart)<.002)return;
 if(!g.started){
  try{beginTransaction('VR free move '+g.actor.name);g.started=true;}
  catch(e){se198.lastError='VR grab begin: '+String(e?.message||e);se198.grab=null;return;}
 }
 // 6DoF: delta of the real controller position, NOT a fixed distance
 // projected down the pointer ray. Pulling the controller toward the
 // headset therefore brings the object closer along world Z as expected.
 const parent=g.actor.parent;
 const worldNow=g.actor.getWorldPosition(new THREE.Vector3());
 const smooth=worldNow.lerp(target,.62);
 g.actor.position.copy(parent?parent.worldToLocal(smooth.clone()):smooth);
 g.actor.updateMatrixWorld(true);g.moved=true;g.target=target;
}
function se198MakeGizmo(){
 if(se198.axisGroup)return;
 const group=new THREE.Group();group.name='§E XR editable XYZ handles';
 const worldAxis={x:new THREE.Vector3(1,0,0),
  y:new THREE.Vector3(0,1,0),z:new THREE.Vector3(0,0,1)};
 const colors={x:0xff7177,y:0x75eeb2,z:0x72b9ff};
 for(const axis of ['x','y','z']){
  const direction=worldAxis[axis];
  const mat=new THREE.MeshBasicMaterial({color:colors[axis],depthTest:false,
   depthWrite:false,toneMapped:false});
  const stem=new THREE.Mesh(new THREE.CylinderGeometry(.012,.012,.54,8),mat);
  stem.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),direction);
  stem.position.copy(direction.clone().multiplyScalar(.30));
  stem.renderOrder=10007;group.add(stem);
  const head=new THREE.Mesh(new THREE.ConeGeometry(.075,.16,12),mat);
  head.quaternion.copy(stem.quaternion);
  head.position.copy(direction.clone().multiplyScalar(.65));
  head.userData.se198Axis=axis;head.renderOrder=10008;
  group.add(head);
  const hit=new THREE.Mesh(new THREE.SphereGeometry(.14,12,8),
   new THREE.MeshBasicMaterial({color:colors[axis],transparent:true,
    opacity:.14,depthTest:false,depthWrite:false,toneMapped:false}));
  hit.name='VR precision '+axis.toUpperCase();
  hit.position.copy(direction.clone().multiplyScalar(.68));
  hit.userData.se198Axis=axis;hit.renderOrder=10009;
  group.add(hit);se198.axisMeshes.push(hit,head);
 }
 group.visible=false;scene.add(group);se198.axisGroup=group;
}
function se198HideLegacyGizmos(){
 if(se198.helpersScanned)return;
 se198.helpersScanned=true;
 // The original 2D transform axes remain in the Three scene during VR.
 // Suppress only standalone helper roots, never authored actor geometry,
 // then restore exactly their previous visibility on XR exit.
 scene.traverse(o=>{
  if(o===se198.axisGroup||o.parent===se198.axisGroup)return;
  if(actors.includes(o))return;
  const label=String(o.name||'');
  if(o.type==='TransformControls'||/^TransformGizmo$/i.test(label)||
   /^(?:editor |selection )?(?:translate|transform) gizmo$/i.test(label)){
   se198.hiddenHelpers.push({object:o,visible:o.visible});
   o.visible=false;
  }
 });
}
function se198UpdateGizmo(){
 se198MakeGizmo();se198HideLegacyGizmos();
 const actor=se198Selected();
 const show=se198Editor()&&!se195.visible&&!!actor&&!se198.grab;
 se198.axisGroup.visible=show;
 if(!show)return;
 actor.updateWorldMatrix(true,false);
 const p=actor.getWorldPosition(new THREE.Vector3());
 se198.axisGroup.position.copy(p);
 const eye=se191XRHeadPose()?.eye;
 const radius=eye?se198Clamp(eye.distanceTo(p)*.12,.55,1.7):1;
 se198.axisGroup.scale.setScalar(radius);
 se198.axisGroup.updateMatrixWorld(true);
 se198.lastSelection=actor;
}
function se198GizmoRayHit(record,cast=se192Ray(record)){
 if(!se198Editor()||se195.visible||!se198.axisGroup?.visible||!cast)return null;
 const hits=cast.ray.intersectObjects(se198.axisMeshes,false);
 const first=hits[0];
 if(!first)return null;
 return {gizmoAxis:first.object.userData.se198Axis,
  distance:first.distance,point:first.point};
}
function se198AxisParam(cast,origin,axis){
 const d=cast.direction,w=cast.origin.clone().sub(origin);
 const b=d.dot(axis),e=axis.dot(w),f=d.dot(w);
 const denom=1-b*b;
 if(denom<.018)return null; // near-parallel rays are ill-conditioned
 return (e-b*f)/denom;
}
function se198BeginAxis(record,hit){
 const actor=se198Selected();
 if(!actor||!hit?.gizmoAxis)return false;
 const cast=se192Ray(record);
 if(!cast)return false;
 const dir={x:new THREE.Vector3(1,0,0),y:new THREE.Vector3(0,1,0),
  z:new THREE.Vector3(0,0,1)}[hit.gizmoAxis];
 const worldStart=actor.getWorldPosition(new THREE.Vector3());
 const value=se198AxisParam(cast,worldStart,dir);
 if(value===null)return false;
 se198FinishGrab(true);
 se198.drag={record,actor,axis:hit.gizmoAxis,dir,
  worldStart,initialParam:value,target:worldStart.clone(),moved:false,started:false};
 se198.axisDrags++;se198.lastAction='Drag '+hit.gizmoAxis.toUpperCase()+' via trigger';
 return true;
}
function se198AxisFrame(){
 const d=se198.drag;
 if(!d)return;
 if(!se198Editor()||se195.visible||!se198IsValidActor(d.actor)){
  se198EndAxis(true);return;
 }
 const cast=se192Ray(d.record);
 if(!cast)return;
 const value=se198AxisParam(cast,d.worldStart,d.dir);
 if(value===null)return;
 const motion=se198Clamp(value-d.initialParam,-30,30);
 if(Math.abs(motion)<.002)return;
 if(!d.started){
  try{beginTransaction('VR '+d.axis.toUpperCase()+' move '+d.actor.name);d.started=true;}
  catch(e){se198.lastError='XR gizmo begin: '+String(e?.message||e);se198.drag=null;return;}
 }
 const target=d.worldStart.clone().addScaledVector(d.dir,motion);
 const worldNow=d.actor.getWorldPosition(new THREE.Vector3());
 const smooth=worldNow.lerp(target,.7);
 d.actor.position.copy(d.actor.parent?d.actor.parent.worldToLocal(smooth.clone()):smooth);
 d.actor.updateMatrixWorld(true);
 d.moved=true;d.target=target;
}
function se198EndAxis(commit=true){
 const d=se198.drag;if(!d)return;
 se198.drag=null;
 try{
  if(commit&&d.started&&d.moved){
   d.actor.position.copy(d.actor.parent?d.actor.parent.worldToLocal(d.target.clone()):d.target);
   d.actor.userData.spawnPos=d.actor.position.toArray();
   commitTransaction('VR '+d.axis.toUpperCase()+' move '+d.actor.name);
   rebuildHierarchy();syncInspector();refreshDebug();
   se198.lastAction='Moved '+d.actor.name+' on '+d.axis.toUpperCase();
  }
 }catch(e){se198.lastError='XR gizmo commit: '+String(e?.message||e).slice(0,120);}
}
function se198FlyFrame(dt){
 if(!se198Editor()||se195.visible){
  se198.velocity.set(0,0,0);return;
 }
 const left=se192InputRecord('left'),right=se192InputRecord('right'),
  ls=se192Stick(left),rs=se192Stick(right),pose=se191XRHeadPose();
 if(!pose)return;
 const forward=pose.forward.clone().setY(0);
 if(forward.lengthSq()<.005)forward.set(0,0,-1);
 forward.normalize();
 const rightVec=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
 const direction=forward.multiplyScalar(-ls.y).addScaledVector(rightVec,ls.x);
 // Hold the LEFT grip and use right-stick up/down to ascend/descend,
 // leaving the whole left stick available for horizontal movement.
 if(se192Pressed(left,1))direction.y=-rs.y;
 if(direction.lengthSq()>1)direction.normalize();
 const fast=se192Pressed(left,3);if(fast)se198.boosts++;
 const speed=se198.speed*(fast?se198.boostMultiplier:1);
 const desired=direction.multiplyScalar(speed);
 const blend=1-Math.exp(-dt*(desired.lengthSq()>.001?16:21));
 se198.velocity.lerp(desired,blend);
 if(se198.velocity.lengthSq()>.000025){
  const motion=se198.velocity.clone().multiplyScalar(dt);
  // Reuse the stable XR reference base already corrected for Sheep
  // instead of nesting a new reference-space transform every frame.
  se195MoveRig(motion.x,motion.y,motion.z);se198.moves++;
 }
 if(Math.abs(rs.x)<.42)se192.turnLatched=false;
 else if(!se192.turnLatched&&performance.now()-se192.lastTurn>320){
  se192.turnLatched=true;se192.lastTurn=performance.now();
  if(se192SnapTurn((rs.x>0?-1:1)*THREE.MathUtils.degToRad(se198.turnDegrees))){
   se195.referenceBase=null;se195.referenceOffset.set(0,0,0);
  }
 }
 se192.inputSamples++;
}
function se198LegendCanvas(){
 const c=document.createElement('canvas');c.width=1100;c.height=900;
 const x=c.getContext('2d');
 x.fillStyle='rgba(9,21,35,.96)';x.fillRect(0,0,1100,900);
 x.strokeStyle='#75ded8';x.lineWidth=15;x.strokeRect(9,9,1082,882);
 x.fillStyle='#a1eff3';x.font='bold 66px sans-serif';
 x.fillText('§E · QUEST EDITOR CONTROLS',48,110);
 const rows=[
  ['LEFT STICK','Move forward, backward, and sideways'],
  ['LEFT GRIP + RIGHT STICK ↑↓','Ascend / descend freely'],
  ['LEFT STICK CLICK (HOLD)','Speed boost ×2.6'],
  ['RIGHT STICK ←→','Comfort snap-turn'],
  ['X (LEFT CONTROLLER)','Open or close tools radial'],
  ['RIGHT TRIGGER','Select object / drag colored gizmo'],
  ['RIGHT GRIP (HOLD)','Grab object in true 3D; pull toward you'],
  ['RED · GREEN · BLUE','Move on X · Y · Z axis'],
  ['GIZMO / FREE GRAB','Choose precise or unrestricted movement'],
  ['META SYSTEM MENU','Exit immersive VR']
 ];
 rows.forEach(([key,value],i)=>{
  const y=195+i*68;
  x.fillStyle='#f0cf89';x.font='bold 29px sans-serif';x.fillText(key,43,y);
  x.fillStyle='#e7f6f8';x.font='30px sans-serif';x.fillText(value,43,y+35);
 });
 x.fillStyle='#a7c9d7';x.font='26px sans-serif';
 x.fillText('Map editing only · Sheep Tag Play uses different controls.',43,869);
 const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;
 return tex;
}
function se198SyncLegend(){
 const parent=se195.radial;
 const visible=!!parent&&se195.visible&&se195.mode==='editor'&&se195.page==='help';
 if(!visible){if(se198.legend)se198.legend.visible=false;return;}
 if(parent!==se198.legendParent){
  if(se198.legend){
   se198.legend.removeFromParent();se198.legend.geometry.dispose();
   se198.legend.material.dispose();se198.legendTexture?.dispose();
  }
  const texture=se198LegendCanvas();
  const plane=new THREE.Mesh(new THREE.PlaneGeometry(.87,.71),
   new THREE.MeshBasicMaterial({map:texture,transparent:true,depthTest:false,
    depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
  plane.name='§E Quest readable button legend';
  plane.position.set(0,.79,.016);plane.renderOrder=10112;
  parent.add(plane);se198.legend=plane;se198.legendTexture=texture;
  se198.legendParent=parent;
 }
 se198.legend.visible=true;
}
const se198OldOptions=se195Options;
se195Options=function(mode=se195.mode,page=se195.page){
 if(mode!=='editor')return se198OldOptions(mode,page);
 if(page==='main')return [
  ['select','SELECT'],['gizmos','GIZMOS'],['flight','FLIGHT'],
  ['place','PREFABS'],['help','LEGEND']
 ];
 if(page==='flight')return [
  ['slower','SLOWER'],['faster','FASTER'],
  ['turnAngle','TURN '+se198.turnDegrees],
  ['help','LEGEND'],['back','BACK']
 ];
 if(page==='gizmos')return [
  ['select','SELECT'],['move','FREE GRAB'],['help','LEGEND'],
  ['capturePage','CAPTURE'],['back','BACK']
 ];
 if(page==='help')return [
  ['flight','FLIGHT'],['gizmos','GIZMOS'],
  ['capturePage','CAPTURE'],['back','BACK']
 ];
 return se198OldOptions(mode,page);
};
const se198OldAction=se195HandleAction;
se195HandleAction=function(action,record){
 if(se195.mode==='editor'){
  if(action==='flight'){se195Page('flight');return true;}
  if(action==='gizmos'){se195Page('gizmos');return true;}
  if(action==='help'){se195Page('help');return true;}
  if(action==='slower'||action==='faster'){
   const i=se198.speeds.indexOf(se198.speed);
   se198.speed=se198.speeds[se198Clamp(i+(action==='faster'?1:-1),0,se198.speeds.length-1)];
   se198SaveSettings();se195Page('flight');
   se198.lastAction='VR flight '+se198.speed+' m/s';return true;
  }
  if(action==='turnAngle'){
   se198.turnDegrees=({15:20,20:30,30:45,45:15})[se198.turnDegrees];
   se198SaveSettings();se195Page('flight');return true;
  }
  if(action==='select'||action==='move'){
   se192.mode=action==='select'?'edit':'move';
   se195SetVisible(false);return true;
  }
 }
 return se198OldAction(action,record);
};
const se198PreviousRaycast=se192Raycast;
se192Raycast=function(record){
 const base=se198PreviousRaycast(record);
 if(!se198Editor()||se195.visible)return base;
 const axis=se198GizmoRayHit(record);
 if(axis&&(!base||base.empty||base.ground||axis.distance<=base.distance+.09))
  return axis;
 return base;
};
const se198PreviousSelect=se192Select;
se192Select=function(record){
 if(se198Editor()&&!se195.visible){
  const hit=se192Raycast(record);
  if(hit?.gizmoAxis){
   se198BeginAxis(record,hit);
   return;
  }
 }
 return se198PreviousSelect(record);
};
se192GrabFrame=se198GrabFrame;
se192MoveFrame=se198FlyFrame;
const se198PreviousVRFrame=se192VRFrame;
se192VRFrame=function(){
 se198PreviousVRFrame();
 if(!se181XR.session||!renderer.xr.isPresenting)return;
 // Install one release listener per controller. The old editor only
 // subscribed to selectstart and couldn't end an axis drag transaction.
 for(const record of se181XR.controllers){
  if(!record.controller||se198.inputHooks.has(record.index))continue;
  const release=()=>{if(se198.drag?.record===record)se198EndAxis(true);};
  record.controller.addEventListener('selectend',release);
  se198.inputHooks.set(record.index,{record,release});
 }
 se198UpdateGizmo();se198AxisFrame();se198SyncLegend();
 for(const record of se181XR.controllers){
  const h=record.se195;
  if(h){
   h.body.scale.setScalar(.55); // screenshot: stock grip model was oversized
   h.halo.material.opacity=.11;h.points.material.opacity=.44;
   h.points.material.size=.008;
  }
 }
};
const se198PreviousCleanup=se192VRCleanup;
se192VRCleanup=function(){
 se198FinishGrab(true);se198EndAxis(true);
 for(const {record,release} of se198.inputHooks.values())
  record.controller.removeEventListener('selectend',release);
 se198.inputHooks.clear();
 if(se198.axisGroup){
  scene.remove(se198.axisGroup);
  se198.axisGroup.traverse(o=>{
   o.geometry?.dispose?.();
   if(o.material){
    const all=Array.isArray(o.material)?o.material:[o.material];
    all.forEach(m=>m.dispose?.());
   }
  });
 }
 se198.axisGroup=null;se198.axisMeshes.length=0;
 if(se198.legend){
  se198.legend.removeFromParent();se198.legend.geometry?.dispose();
  se198.legend.material?.dispose();se198.legendTexture?.dispose();
 }
 se198.legend=se198.legendTexture=se198.legendParent=null;
 for(const h of se198.hiddenHelpers)h.object.visible=h.visible;
 se198.hiddenHelpers.length=0;se198.helpersScanned=false;
 se198.velocity.set(0,0,0);se198.lastFrame=0;
 return se198PreviousCleanup();
};
const se198OldCapture=se193XRCapture;
se193XRCapture=function(mode='clean'){
 const oldGizmo=se198.axisGroup?.visible,oldLegend=se198.legend?.visible;
 if(se198.axisGroup)se198.axisGroup.visible=false;
 if(se198.legend)se198.legend.visible=false;
 try{return se198OldCapture(mode);}
 finally{
  if(se198.axisGroup)se198.axisGroup.visible=!!oldGizmo;
  if(se198.legend)se198.legend.visible=!!oldLegend;
 }
};
const se198PreviousVRStart=se192VRStart;
se192VRStart=function(){
 se198.velocity.set(0,0,0);se198.moves=0;se198.grab=null;se198.drag=null;
 se198.helpersScanned=false;se198.lastFrame=performance.now();
 se198PreviousVRStart();
};
window.SWYRL_ENGINE_XR_EDITOR_198=Object.freeze({
 diagnose:()=>({
  editor:se198Editor(),mode:se195Mode(),flySpeed:se198.speed,
  speedBoost:se198.boostMultiplier,turnDegrees:se198.turnDegrees,
  moving:se198.moves,directGrabs:se198.directGrabs,axisDrags:se198.axisDrags,
  gripDragging:!!se198.grab,axisDragging:!!se198.drag,
  gizmoVisible:!!se198.axisGroup?.visible,legendVisible:!!se198.legend?.visible,
  legacyHelpersHidden:se198.hiddenHelpers.length,
  lastAction:se198.lastAction,lastError:se198.lastError
 }),
 showLegend:()=>{
  if(!se198Editor())return false;
  se195.mode='editor';se195Page('help');return true;
 }
});