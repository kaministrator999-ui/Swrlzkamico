// §E v11.214 — Quest Sheep Tag PLAY modal quick-wheel comfort and pointer ownership.
// Fix three real-device symptoms: a world-space wheel left behind as the sheep
// camera tracks, unwanted camera chasing/tilting during selection, and a second
// neon building guide or controller aura behind a thumbstick-only radial.
// HMD native tracking (including safety-critical head roll) is never modified.
const se214={
 lastYaw:new THREE.Vector3(0,0,-1),up:new THREE.Vector3(0,1,0),
 eyeLevel:new THREE.Vector3(),matrix:new THREE.Matrix4(),
 entered:0,exited:0,positionFrames:0,headingFallbacks:0,
 cameraBlocks:0,movementBlocks:0,stoppedOrders:0,groundBlocks:0,
 beamsHidden:0,extraEffectsMuted:0,rayRestores:0,
 menuRayHits:0,menuRayMisses:0,menuRaySelections:0,
 lastMode:'',lastError:''
};
function se214WheelOpen(){
 return !!se204?.wheel?.root?.visible&&se204Gameplay()&&
  !!se181XR?.session&&renderer.xr.isPresenting&&
  !(typeof se205OverlayActive==='function'&&se205OverlayActive())&&
  !(typeof se211Paused==='function'&&se211Paused());
}
function se214PositionWheel(){
 if(!se214WheelOpen())return false;
 const root=se204.wheel.root,pose=se191XRHeadPose();
 if(!pose?.eye||!pose?.forward)return false;
 // A native XR camera must follow real headset orientation. Only the game
 // radial is yaw-upright: never inherit HMD pitch or roll from lookAt(eye).
 const horizontal=se214.eyeLevel.copy(pose.forward).setY(0);
 if(horizontal.lengthSq()>.015){
  horizontal.normalize();se214.lastYaw.copy(horizontal);
 }else{
  horizontal.copy(se214.lastYaw);
  se214.headingFallbacks++;
 }
 root.position.copy(pose.eye).addScaledVector(horizontal,1.08);
 root.position.y=pose.eye.y-.075;
 se214.eyeLevel.copy(pose.eye);
 se214.eyeLevel.y=root.position.y;
 se214.matrix.lookAt(se214.eyeLevel,root.position,se214.up);
 root.quaternion.setFromRotationMatrix(se214.matrix);
 root.updateMatrixWorld(true);
 se214.positionFrames++;
 return true;
}
function se214HideExtraRays(){
 if(!se193XRGameActive())return;
 // se203 can reconstruct the physical-to-virtual-ground link EVERY frame
 // while stUi.build remains equipped. Keep the placement guide hidden while
 // a modal A/X wheel owns the rays; do not hide the menu targeting beams.
 if(typeof se203GroundGuideHide==='function')se203GroundGuideHide();
 for(const record of se181XR.controllers||[]){
  if(record.ray)record.ray.visible=false;
  const visual=record.se195;
  if(visual?.halo?.visible){visual.halo.visible=false;se214.extraEffectsMuted++;}
  if(visual?.points?.visible){visual.points.visible=false;se214.extraEffectsMuted++;}
  if(se214WheelOpen()&&record.se192){
   // A/X modal: retain controller beams for visual ray-based selection.
   record.se192.beam.visible=true;
  }
 }
}
function se214RestoreGamePointer(){
 for(const record of se181XR.controllers||[]){
  if(record.ray)record.ray.visible=false; // legacy XR Line already superseded
  if(record.se192){
   record.se192.beam.visible=true; // the following normal frame decides
   record.se192.dot.visible=false; // contact marker re-evaluates on ray hit
  }
 }
 se214.rayRestores++;
}
function se214StopStickOrder(){
 const s=stSession,u=s?.units?.find?.(x=>x.id===s.controlledId);
 if(u?.order?.vrStick){
  stSetOrder(u,null);
  se214.stoppedOrders++;
 }
 // No camera or UI update should reinterpret a held left stick as "pan".
 if(se200?.stickHeld)se200.stickHeld=false;
}
const se214PriorPosition=se204WheelPosition;
se204WheelPosition=function(){
 if(se214WheelOpen())return se214PositionWheel();
 return se214PriorPosition();
};
const se214PriorShow=se204WheelShow;
se204WheelShow=function(type){
 const before=se214WheelOpen(),result=se214PriorShow(type);
 if(se214WheelOpen()){
  if(!before){se214.entered++;se214StopStickOrder();}
  se214PositionWheel();
  se214HideExtraRays();
  se214.lastMode=type;
 }
 return result;
};
const se214PriorHide=se204WheelHide;
se204WheelHide=function(){
 const active=!!se204.wheel;
 const out=se214PriorHide();
 if(active){
  se214.exited++;se214RestoreGamePointer();
  se214.lastMode='';
 }
 return out;
};
// Freeze Sheep Tag joystick locomotion only during A/X modal selection.
// Its host/server simulation, enemies, fog visibility, and native timers
// continue normally. No editor or non-VR joystick controls are touched.
const se214PriorStickIntent=se199StickIntent;
se199StickIntent=function(){
 if(se214WheelOpen()){
  se214.movementBlocks++;
  return {strength:0,x:0,z:0};
 }
 return se214PriorStickIntent();
};
// The world camera is already following the sheep. Do not chase the player
// with reference-space translations while the modal is placed from the HMD;
// allow natural HMD tracking and resume the current follow on close.
const se214PriorFollow=se195FollowCamera;
se195FollowCamera=function(dt){
 if(se214WheelOpen()){
  se214.cameraBlocks++;
  return;
 }
 return se214PriorFollow(dt);
};
// Prevent the v11.203 forward-building guide from reconstructing while an
// A/X wheel is showing. This also prevents ghost ray and building placement
// behind a modal wheel.
const se214PriorForwardGround=se203GroundFromForwardRay;
se203GroundFromForwardRay=function(record){
 if(se214WheelOpen()){
  se214.groundBlocks++;
  return null;
 }
 return se214PriorForwardGround(record);
};
// The original controller marker appends a SECOND glow cylinder around the
// native tapered §E beam. Keep only one visible ray for the modal wheel,
// with an endpoint on the actual hit option (not on the game terrain).
// Editor/modeler controller effects retain their own ownership.
const se214PriorHand=se195UpdateHand;
se195UpdateHand=function(record,t,dist){
 if(se193XRGameActive())return;
 return se214PriorHand(record,t,dist);
};
const se214PriorRenderRay=se192RenderRay;
se192RenderRay=function(record,hit){
 const out=se214PriorRenderRay(record,hit);
 if(se193XRGameActive()){
  const hand=record?.se195;
  if(hand?.halo)hand.halo.visible=false;
  if(hand?.points)hand.points.visible=false;
  if(se214WheelOpen()){
   if(typeof se203GroundGuideHide==='function')se203GroundGuideHide();
   const menuHit=se204WheelRayHit(record);
   if(record?.se192){
    const cast=se192Ray(record),{beam,dot}=record.se192;
    beam.visible=true;
    beam.scale.z=THREE.MathUtils.clamp(menuHit?.distance||1.08,.12,2.5);
    if(menuHit?.point&&cast){
     dot.position.copy(menuHit.point);
     dot.lookAt(cast.origin);
     dot.scale.setScalar(.7);dot.visible=true;
     se214.menuRayHits++;
     if(Number.isInteger(menuHit.wheelIndex)){
      if(se204WheelHover(record,menuHit))se214.menuRaySelections++;
      beam.material.color.setHex(0x9affdf);
     }else beam.material.color.setHex(0xffd180);
    }else{
     dot.visible=false;beam.material.color.setHex(0xffd180);
     se214.menuRayMisses++;
    }
   }
   if(record?.ray)record.ray.visible=false;
  }
 }
 return out;
};
function se214Frame(){
 if(se214WheelOpen()){
  se214PositionWheel();
  se214HideExtraRays();
 }
}
const se214PriorFrame=se193XRFrame;
se193XRFrame=function(){
 const out=se214PriorFrame();
 se214Frame();
 return out;
};
const se214PriorCleanup=se193XRCleanup;
se193XRCleanup=function(){
 se214.lastMode='';se214.lastYaw.set(0,0,-1);
 return se214PriorCleanup();
};
window.SWYRL_ENGINE_SHEEP_WHEEL_COMFORT_214=Object.freeze({
 diagnose:()=>({
  wheelOpen:se214WheelOpen(),menuType:se214.lastMode,
  yawOnlyMenu:true,headsetTrackingUnchanged:true,
  enteringModal:se214.entered,leavingModal:se214.exited,
  uprightWheelFrames:se214.positionFrames,
  verticalHeadGazeFallbacks:se214.headingFallbacks,
  cameraFollowFramesSuppressed:se214.cameraBlocks,
  joystickFramesSuppressed:se214.movementBlocks,
  previousJoystickOrdersStopped:se214.stoppedOrders,
  underlyingBuildGuideSuppressed:se214.groundBlocks,
  extraRayHides:se214.beamsHidden,
  duplicateControllerAuraSuppressed:se214.extraEffectsMuted,
  menuRayHits:se214.menuRayHits,menuRayMisses:se214.menuRayMisses,
  rayHoverChanges:se214.menuRaySelections,
  pointerRestores:se214.rayRestores,lastError:se214.lastError
 })
});
