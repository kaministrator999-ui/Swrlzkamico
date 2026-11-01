// §E v11.196 — headset report hotfix: non-mirrored stationary radial,
// non-flying cinematic camera and non-VR fog/terrain depth separation.
// Additive to v11.195, no new WebGL renderer, simulation loop or saved-scene edits.
const se196={
 lastMode:'',menuAnchored:false,menuFocus:new THREE.Vector3(),
 menuHeading:new THREE.Vector3(),menuSnaps:0,gameSnaps:0,radialAnchors:0,
 fogSessions:0,fogPaints:0,fogCoalesced:0,activeFog:null,
 lastError:'',groundLayers:0
};
function se196FogRepair(s){
 const fog=s?.fog;
 if(!fog?.mesh)return false;
 if(fog.se196DepthFixed)return true;
 const plane=fog.mesh,mat=plane.material;
 // The old y=.055 fog intersects the meadow at y=.04, and shallow
 // decorative geometry. This is visible even in a floating 2D browser,
 // not only WebXR. Keep the fog one uninterrupted world-space layer.
 plane.position.y=Math.max(.23,plane.position.y);
 plane.renderOrder=Math.max(3,plane.renderOrder||0);
 mat.transparent=true;
 mat.depthTest=true;
 mat.depthWrite=false;
 mat.polygonOffset=true;
 mat.polygonOffsetFactor=-3;
 mat.polygonOffsetUnits=-6;
 mat.needsUpdate=true;
 fog.se196DepthFixed=true;
 fog.se196LastPaint=0;
 fog.se196PaintCount=0;
 se196.fogSessions++;
 se196.activeFog=fog;
 return true;
}
const se196CreateFogOriginal=stCreateFog;
stCreateFog=function(s){
 const result=se196CreateFogOriginal(s);
 se196FogRepair(s);
 return result;
};
// Keep exploration and vision updates authoritative. Only the canvas
// texture repaint/upload is coalesced, in 2D as well as immersive VR.
const se196PaintOriginal=stSoftFogPaint;
stSoftFogPaint=function(s){
 const fog=s?.fog;
 if(!fog)return se196PaintOriginal(s);
 if(!fog.se196DepthFixed)se196FogRepair(s);
 const now=performance.now();
 const minDelay=se195Gameplay()?290:210;
 if(fog.se196LastPaint>0&&now-fog.se196LastPaint<minDelay){
  se196.fogCoalesced++;
  return;
 }
 const painted=se196PaintOriginal(s);
 fog.se196LastPaint=now;
 fog.se196PaintCount++;
 se196.fogPaints++;
 return painted;
};
function se196KnownFog(){
 if(stSession?.fog)se196FogRepair(stSession);
}
const se196XRStartPrevious=se193XRStart;
se193XRStart=function(){
 se196XRStartPrevious();
 se196.lastMode='';se196.menuAnchored=false;se196.gameSnaps=0;
 se196KnownFog();
 // Do not make the player's viewpoint orbit automatically on entering
 // immersive VR. The authored sheep/house cinematic still animates.
 se195.menuOrbit=false;
};
const se196CleanupPrevious=se193XRCleanup;
se193XRCleanup=function(){
 se196.menuAnchored=false;se196.lastMode='';
 se196CleanupPrevious();
};
// Fix THREE.Matrix4.lookAt(plane, eye) (backward facing +Z). A world
// PlaneGeometry's positive Z is its FRONT; Object3D.lookAt(eye)
// produces that orientation, never the mirrored back face.
se195PositionRadial=function(force=false){
 if(!se195.radial||!se195Active()||!force)return;
 const pose=se191XRHeadPose();
 if(!pose)return;
 const aim=pose.forward.clone().normalize();
 const right=new THREE.Vector3().crossVectors(aim,new THREE.Vector3(0,1,0));
 if(right.lengthSq()<.001)right.set(1,0,0);
 right.normalize();
 // Prefer a location within reach of the right-hand ray on OPEN.
 // Clamp extreme hand positions to the headset-visible foreground.
 const visible=pose.eye.clone().addScaledVector(aim,1.05)
  .addScaledVector(right,.20).add(new THREE.Vector3(0,-.12,0));
 let wanted=visible.clone();
 const controller=se192InputRecord('right')?.controller;
 if(controller){
  controller.updateMatrixWorld(true);
  const origin=controller.getWorldPosition(new THREE.Vector3());
  const vector=new THREE.Vector3(0,0,-1)
   .transformDirection(controller.matrixWorld).normalize();
  const hand=origin.addScaledVector(vector,.82)
   .addScaledVector(right,.11);
  if(hand.distanceTo(visible)<.52)wanted.lerp(hand,.35);
 }
 se195.radial.position.copy(wanted);
 se195.radial.lookAt(pose.eye);
 se195.radial.updateMatrixWorld(true);
 se196.radialAnchors++;
};
// Menu actors already run their cinematic independently. Replace the old
// CINEMA camera-drift toggle with an explicit comfort-safe REFOCUS command.
const se196OptionsPrevious=se195Options;
se195Options=function(mode=se195.mode,page=se195.page){
 if(mode==='menu'&&page==='main')return [
  ['start','PLAY'],['recenter','REFOCUS'],['capturePage','CAPTURE'],
  ['help','CONTROLS'],['editor','EDIT']
 ];
 return se196OptionsPrevious(mode,page);
};
const se196ActionPrevious=se195HandleAction;
se195HandleAction=function(action,record){
 if(action==='recenter'&&se195Menu()){
  se196.menuAnchored=false;
  se195MenuCamera(0);
  se195.lastAction='VR sheep menu recentered';
  return true;
 }
 return se196ActionPrevious(action,record);
};
// The existing frame calls se195PositionRadial(false) continuously;
// the above intentionally makes that a no-op. The dial reanchors only
// when summoned or when changing its menu page, not when aiming at it.
const se196EditorMove=se192MoveFrame;
se192MoveFrame=function(dt){
 // The level selector's cinematic is not marked 'playing', so the old
 // editor locomotion ran *alongside* the VR cinematic camera movement.
 if(se195Active()&&(se193XRMenuActive()||se193XRGameActive()))return;
 return se196EditorMove(dt);
};
const se196Grab=se192GrabFrame;
se192GrabFrame=function(record){
 if(se195Active()&&(se193XRMenuActive()||se193XRGameActive()))return;
 return se196Grab(record);
};
// Freeze the menu camera's world anchor while authored sheep dance
// around it. Camera translation on initial VR entry is a single rebase,
// not dozens of large 'fly toward the sheep' steps.
se195MenuCamera=function(dt){
 if(!se195Menu())return;
 if(se196.menuAnchored)return;
 const pose=se191XRHeadPose();
 if(!pose)return;
 const sheep=se195FocusSheep();
 const front=pose.forward.clone().setY(0);
 if(front.lengthSq()<.001)front.set(0,0,-1);
 front.normalize();
 se196.menuFocus.copy(sheep);
 se196.menuHeading.copy(front);
 const wanted=sheep.clone().addScaledVector(front,-12.4);
 wanted.y=sheep.y+6.8;
 const delta=wanted.sub(pose.eye);
 if(delta.lengthSq()>.0025){
  if(!se195MoveRig(delta.x,delta.y,delta.z))return;
 }
 se196.menuAnchored=true;
 se196.menuSnaps++;
};
const se196GameCamera=se195FollowCamera;
se195FollowCamera=function(dt){
 // v11.195 gradually flew 25m into position after start, causing severe
 // discomfort and a sideways impression. Snap ONCE into the strategic
 // follow view; the regular smoothly-tracking camera owns later frames.
 if(!se195Gameplay())return;
 if(!se195.rigReady){
  const s=stSession,unit=s?.units?.find(u=>u.id===s.controlledId);
  const pose=se191XRHeadPose();
  if(!unit?.pos||!pose)return;
  const f=pose.forward.clone().setY(0);
  if(f.lengthSq()<.001)f.set(0,0,-1);
  f.normalize();
  se193.angle=Math.atan2(f.x,f.z);
  se193.focus.set(unit.pos.x,0,unit.pos.z);
  se193.follow=true;
  se195.rigReady=true;
  se195.rigAt=0; // avoid temporary high-speed initial catch-up
  const wanted=se193.focus.clone().addScaledVector(f,-25*se193.zoom);
  wanted.y=17*se193.zoom;
  const delta=wanted.sub(pose.eye);
  if(delta.lengthSq()>.0025&&!se195MoveRig(delta.x,delta.y,delta.z)){
   se195.rigReady=false;return;
  }
  se196.gameSnaps++;
  return;
 }
 return se196GameCamera(Math.min(.032,Math.max(0,dt)));
};
const se196XrFrameOriginal=se193XRFrame;
se193XRFrame=function(){
 if(se195Active()){
  const kind=se195Mode();
  if(kind!==se196.lastMode){
   se196.lastMode=kind;
   se196.menuAnchored=false;
   if(kind!=='game')se195.rigReady=false;
   // Rebase the stable reference for the new session mode.
   se195.referenceBase=null;se195.referenceOffset.set(0,0,0);
  }
  se196KnownFog();
 }
 return se196XrFrameOriginal();
};
window.SWYRL_ENGINE_SHEEP_VR_FIX196=Object.freeze({
 diagnose:()=>({
  xr:se195Active(),version:'v11.196',
  cameraMode:se196.lastMode,menuAnchorLocked:se196.menuAnchored,
  menuSnaps:se196.menuSnaps,gameSnaps:se196.gameSnaps,
  radialAnchors:se196.radialAnchors,
  fogDepth:stSession?.fog?.mesh?.position.y??null,
  fogPaints:se196.fogPaints,coalescedFogPaints:se196.fogCoalesced,
  paused:!!paused,lastError:se196.lastError
 })
});