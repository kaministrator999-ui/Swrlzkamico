// §E v11.213 — Quest Sheep Tag PLAY modal quick-wheel comfort and pointer ownership.
// Fix three real-device symptoms: a world-space wheel left behind as the sheep
// camera tracks, unwanted camera chasing/tilting during selection, and a second
// neon building guide or controller aura behind a thumbstick-only radial.
// HMD native tracking (including safety-critical head roll) is never modified.
const se213={
 lastYaw:new THREE.Vector3(0,0,-1),up:new THREE.Vector3(0,1,0),
 eyeLevel:new THREE.Vector3(),matrix:new THREE.Matrix4(),
 entered:0,exited:0,positionFrames:0,headingFallbacks:0,
 cameraBlocks:0,movementBlocks:0,stoppedOrders:0,groundBlocks:0,
 beamsHidden:0,extraEffectsMuted:0,rayRestores:0,
 lastMode:'',lastError:''
};
function se213WheelOpen(){
 return !!se204?.wheel?.root?.visible&&se204Gameplay()&&
  !!se181XR?.session&&renderer.xr.isPresenting&&
  !(typeof se205OverlayActive==='function'&&se205OverlayActive())&&
  !(typeof se211Paused==='function'&&se211Paused());
}
function se213PositionWheel(){
 if(!se213WheelOpen())return false;
 const root=se204.wheel.root,pose=se191XRHeadPose();
 if(!pose?.eye||!pose?.forward)return false;
 // A native XR camera must follow real headset orientation. Only the game
 // radial is yaw-upright: never inherit HMD pitch or roll from lookAt(eye).
 const horizontal=se213.eyeLevel.copy(pose.forward).setY(0);
 if(horizontal.lengthSq()>.015){
  horizontal.normalize();se213.lastYaw.copy(horizontal);
 }else{
  horizontal.copy(se213.lastYaw);
  se213.headingFallbacks++;
 }
 root.position.copy(pose.eye).addScaledVector(horizontal,1.08);
 root.position.y=pose.eye.y-.075;
 se213.eyeLevel.copy(pose.eye);
 se213.eyeLevel.y=root.position.y;
 se213.matrix.lookAt(se213.eyeLevel,root.position,se213.up);
 root.quaternion.setFromRotationMatrix(se213.matrix);
 root.updateMatrixWorld(true);
 se213.positionFrames++;
 return true;
}
function se213HideExtraRays(){
 if(!se193XRGameActive())return;
 // se203 can reconstruct the physical-to-virtual-ground link EVERY frame
 // while stUi.build remains equipped. A modal A/X wheel is NOT a ground
 // placement action: it uses right thumbstick for the sector selector.
 if(typeof se203GroundGuideHide==='function')se203GroundGuideHide();
 for(const record of se181XR.controllers||[]){
  if(record.ray)record.ray.visible=false;
  const visual=record.se195;
  if(visual?.halo?.visible){visual.halo.visible=false;se213.extraEffectsMuted++;}
  if(visual?.points?.visible){visual.points.visible=false;se213.extraEffectsMuted++;}
  if(se213WheelOpen()&&record.se192){
   if(record.se192.beam.visible)se213.beamsHidden++;
   record.se192.beam.visible=false;
   record.se192.dot.visible=false;
  }
 }
}
function se213RestoreGamePointer(){
 for(const record of se181XR.controllers||[]){
  if(record.ray)record.ray.visible=false; // legacy XR Line already superseded
  if(record.se192){
   record.se192.beam.visible=true; // the following normal frame decides
   record.se192.dot.visible=false; // contact marker re-evaluates on ray hit
  }
 }
 se213.rayRestores++;
}
function se213StopStickOrder(){
 const s=stSession,u=s?.units?.find?.(x=>x.id===s.controlledId);
 if(u?.order?.vrStick){
  stSetOrder(u,null);
  se213.stoppedOrders++;
 }
 // No camera or UI update should reinterpret a held left stick as "pan".
 if(se200?.stickHeld)se200.stickHeld=false;
}
const se213PriorPosition=se204WheelPosition;
se204WheelPosition=function(){
 if(se213WheelOpen())return se213PositionWheel();
 return se213PriorPosition();
};
const se213PriorShow=se204WheelShow;
se204WheelShow=function(type){
 const before=se213WheelOpen(),result=se213PriorShow(type);
 if(se213WheelOpen()){
  if(!before){se213.entered++;se213StopStickOrder();}
  se213PositionWheel();
  se213HideExtraRays();
  se213.lastMode=type;
 }
 return result;
};
const se213PriorHide=se204WheelHide;
se204WheelHide=function(){
 const active=!!se204.wheel;
 const out=se213PriorHide();
 if(active){
  se213.exited++;se213RestoreGamePointer();
  se213.lastMode='';
 }
 return out;
};
// Freeze Sheep Tag joystick locomotion only during A/X modal selection.
// Its host/server simulation, enemies, fog visibility, and native timers
// continue normally. No editor or non-VR joystick controls are touched.
const se213PriorStickIntent=se199StickIntent;
se199StickIntent=function(){
 if(se213WheelOpen()){
  se213.movementBlocks++;
  return {strength:0,x:0,z:0};
 }
 return se213PriorStickIntent();
};
// The world camera is already following the sheep. Do not chase the player
// with reference-space translations while the modal is placed from the HMD;
// allow natural HMD tracking and resume the current follow on close.
const se213PriorFollow=se195FollowCamera;
se195FollowCamera=function(dt){
 if(se213WheelOpen()){
  se213.cameraBlocks++;
  return;
 }
 return se213PriorFollow(dt);
};
// Prevent the v11.203 forward-building guide from reconstructing while an
// A/X wheel is showing. This also prevents ghost ray and building placement
// behind a modal wheel.
const se213PriorForwardGround=se203GroundFromForwardRay;
se203GroundFromForwardRay=function(record){
 if(se213WheelOpen()){
  se213.groundBlocks++;
  return null;
 }
 return se213PriorForwardGround(record);
};
// The original controller marker appends a SECOND glow cylinder around the
// native tapered §E beam. In Sheep Tag Play it's visually redundant.
// Keep one beam when placing; no beam while choosing via the thumbstick.
// Editor/modeler controller effects retain their own ownership.
const se213PriorHand=se195UpdateHand;
se195UpdateHand=function(record,t,dist){
 if(se193XRGameActive())return;
 return se213PriorHand(record,t,dist);
};
const se213PriorRenderRay=se192RenderRay;
se192RenderRay=function(record,hit){
 const out=se213PriorRenderRay(record,hit);
 if(se193XRGameActive()){
  const hand=record?.se195;
  if(hand?.halo)hand.halo.visible=false;
  if(hand?.points)hand.points.visible=false;
  if(se213WheelOpen()){
   if(typeof se203GroundGuideHide==='function')se203GroundGuideHide();
   if(record?.se192){
    record.se192.beam.visible=false;
    record.se192.dot.visible=false;
   }
   if(record?.ray)record.ray.visible=false;
  }
 }
 return out;
};
function se213Frame(){
 if(se213WheelOpen()){
  se213PositionWheel();
  se213HideExtraRays();
 }
}
const se213PriorFrame=se193XRFrame;
se193XRFrame=function(){
 const out=se213PriorFrame();
 se213Frame();
 return out;
};
const se213PriorCleanup=se193XRCleanup;
se193XRCleanup=function(){
 se213.lastMode='';se213.lastYaw.set(0,0,-1);
 return se213PriorCleanup();
};
window.SWYRL_ENGINE_SHEEP_WHEEL_COMFORT_213=Object.freeze({
 diagnose:()=>({
  wheelOpen:se213WheelOpen(),menuType:se213.lastMode,
  yawOnlyMenu:true,headsetTrackingUnchanged:true,
  enteringModal:se213.entered,leavingModal:se213.exited,
  uprightWheelFrames:se213.positionFrames,
  verticalHeadGazeFallbacks:se213.headingFallbacks,
  cameraFollowFramesSuppressed:se213.cameraBlocks,
  joystickFramesSuppressed:se213.movementBlocks,
  previousJoystickOrdersStopped:se213.stoppedOrders,
  underlyingBuildGuideSuppressed:se213.groundBlocks,
  extraRayHides:se213.beamsHidden,
  duplicateControllerAuraSuppressed:se213.extraEffectsMuted,
  pointerRestores:se213.rayRestores,lastError:se213.lastError
 })
});
