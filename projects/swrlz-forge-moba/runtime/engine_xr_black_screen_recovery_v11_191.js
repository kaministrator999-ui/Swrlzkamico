// §E v11.191 — Quest VR black-view recovery.
// Spawn in the project's authored arrival zone using XR reference-space translation,
// not an ordinary editor camera transform. Keep a head-visible unlit rescue panel.
// No duplicate render loop, no modeler changes, no saved-scene mutation.
const se191XR={
 landing:null,referenceSpaceOffset:false,lastFrameAt:0,entryAt:0,frames:0,
 beacon:null,beaconGeometry:null,beaconMaterial:null,beaconTexture:null,
 watchdog:null,rayHits:new Map(),lastError:'',reason:'',framebufferScale:.8
};
function se191XRZone(){
 const zones=Array.isArray(currentProject?.teleportZones)?currentProject.teleportZones:[];
 const saved=zones.find(z=>z?.id==='arrival'&&Array.isArray(z.position)&&z.position.length===3);
 if(saved&&saved.position.every(v=>Number.isFinite(v)&&Math.abs(v)<1000))
   return {position:saved.position.slice(),source:'project arrival zone'};
 // A custom project without an arrival point is never teleported into
 // the canonical Dragon Den, or silently modified.
 if(currentProject?.environment==='dragon-den')
   return {position:[0,.02,14.1],source:'Dragon Den arrival fallback'};
 return {position:[0,0,0],source:'local-floor origin (no authored arrival)'};
}
function se191XRInstallLanding(){
 const target=se191XRZone();
 se191XR.landing=target;
 const space=renderer.xr.getReferenceSpace?.();
 if(!space?.getOffsetReferenceSpace||typeof XRRigidTransform!=='function'){
  se191XR.reason='XR reference offset not supported; showing rescue panel at tracked eye';
  se181XRNote(se191XR.reason,true);
  return false;
 }
 try{
  const [x,y,z]=target.position;
  // The new reference-space origin moves in the OPPOSITE direction of the
  // desired world-space player location: inverse(-x,-y,-z).
  const offset=space.getOffsetReferenceSpace(new XRRigidTransform({x:-x,y:-y,z:-z}));
  renderer.xr.setReferenceSpace(offset);
  se191XR.referenceSpaceOffset=true;
  se191XR.reason='VR arrival: '+target.source;
  se181XRNote('Entering Dragon Den · '+target.source);
  return true;
 }catch(e){
  se191XR.lastError=String(e?.message||e).slice(0,160);
  se191XR.reason='XR landing offset unavailable';
  se181XRNote(se191XR.reason+': '+se191XR.lastError,true);
  return false;
 }
}
function se191XRMakeBeacon(){
 if(se191XR.beacon)return;
 const canvas=document.createElement('canvas');canvas.width=768;canvas.height=320;
 const ctx=canvas.getContext('2d');
 if(!ctx)return;
 ctx.clearRect(0,0,768,320);
 ctx.fillStyle='rgba(7,27,43,0.94)';ctx.fillRect(8,8,752,304);
 ctx.strokeStyle='#6af2dc';ctx.lineWidth=12;ctx.strokeRect(10,10,748,300);
 ctx.fillStyle='#e7fffa';ctx.textAlign='center';
 ctx.font='bold 65px sans-serif';ctx.fillText('§E  ·  DRAGON DEN',384,116);
 ctx.font='35px sans-serif';ctx.fillText('VR arrival · look around',384,188);
 ctx.fillStyle='#d0a8ff';ctx.font='27px sans-serif';
 ctx.fillText('EXIT VR: Quest system menu or side sign',384,251);
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
 const geometry=new THREE.PlaneGeometry(1.2,.5);
 const material=new THREE.MeshBasicMaterial({
  map:texture,transparent:true,depthTest:false,depthWrite:false,
  side:THREE.DoubleSide,toneMapped:false
 });
 const beacon=new THREE.Mesh(geometry,material);
 beacon.name='§E VR arrival diagnostic';beacon.renderOrder=10005;
 beacon.frustumCulled=false;
 scene.add(beacon);
 se191XR.beacon=beacon;se191XR.beaconGeometry=geometry;
 se191XR.beaconMaterial=material;se191XR.beaconTexture=texture;
}
function se191XRHeadPose(){
 const head=renderer.xr.getCamera(perspectiveCamera);
 head.updateMatrixWorld(true);
 const eye=head.getWorldPosition(new THREE.Vector3());
 const forward=head.getWorldDirection(new THREE.Vector3());
 if(![eye.x,eye.y,eye.z,forward.x,forward.y,forward.z].every(Number.isFinite)||
    forward.lengthSq()<.01)return null;
 forward.normalize();
 return {eye,forward};
}
function se191XRRenderFrame(){
 if(!se181XR.session||!renderer.xr.isPresenting)return;
 se191XR.frames++;se191XR.lastFrameAt=performance.now();
 const pose=se191XRHeadPose();
 if(!pose)return;
 if(se191XR.beacon){
  // Always visible during first 9s, even inside dark or opaque geometry.
  // After arrival, remove this HUD to preserve immersion.
  const showing=performance.now()-se191XR.entryAt<9000;
  se191XR.beacon.visible=showing;
  if(showing){
   se191XR.beacon.position.copy(pose.eye).addScaledVector(pose.forward,1.3);
   se191XR.beacon.lookAt(pose.eye);
  }
 }
 // Keep a user-accessible illuminated EXIT sign in front of the headset
 // even if the room has no lighting. It is deliberately world-anchored.
 if(se181XR.exitPanel&&!se181XR.exitPanel.visible){
  const dir=pose.forward.clone();dir.y=0;if(dir.lengthSq()<.01)dir.set(0,0,-1);
  dir.normalize();
  const right=new THREE.Vector3().crossVectors(dir,new THREE.Vector3(0,1,0)).normalize();
  se181XR.exitPanel.position.copy(pose.eye).addScaledVector(dir,1.45)
   .addScaledVector(right,-.67).add(new THREE.Vector3(0,.24,0));
  se181XR.exitPanel.lookAt(pose.eye);
  se181XR.exitPanel.visible=true;
  se181XR.viewerAnchored=true;
 }
}
function se191XRRayHit(record){
 const now=performance.now(),cached=se191XR.rayHits.get(record.index);
 if(cached&&now-cached.time<95)return cached.hit;
 let hit=null;
 try{hit=se181XRRaycast(record);}catch(e){se191XR.lastError='XR ray: '+String(e?.message||e).slice(0,120);}
 se191XR.rayHits.set(record.index,{time:now,hit});
 return hit;
}
function se191XRStartWatchdog(session){
 se191XR.entryAt=performance.now();se191XR.frames=0;
 se191XR.lastFrameAt=0;se191XR.rayHits.clear();
 if(se191XR.watchdog)clearTimeout(se191XR.watchdog);
 se191XR.watchdog=setTimeout(()=>{
  se191XR.watchdog=null;
  if(se181XR.session!==session||!renderer.xr.isPresenting)return;
  if(se191XR.frames===0){
   se191XR.lastError='Headset provided no XR render frames after 9 seconds';
   se181XRNote(se191XR.lastError+' · returning to the browser',true);
   void se181XRExit();
  }
 },9000);
}
function se191XRCleanup(){
 if(se191XR.watchdog){clearTimeout(se191XR.watchdog);se191XR.watchdog=null;}
 if(se191XR.beacon){scene.remove(se191XR.beacon);}
 se191XR.beaconGeometry?.dispose();se191XR.beaconMaterial?.dispose();
 se191XR.beaconTexture?.dispose();
 se191XR.beacon=se191XR.beaconGeometry=se191XR.beaconMaterial=se191XR.beaconTexture=null;
 se191XR.rayHits.clear();se191XR.referenceSpaceOffset=false;
}
function se191XRPrepareFramebuffer(){
 try{
  if(typeof renderer.xr.setFramebufferScaleFactor==='function')
   renderer.xr.setFramebufferScaleFactor(se191XR.framebufferScale);
 }catch(e){se191XR.lastError='XR framebuffer preference: '+String(e?.message||e).slice(0,90);}
}
function se191XRDiagnostics(){
 return {immersive:!!se181XR.session&&renderer.xr.isPresenting,
  startedAt:se191XR.entryAt,frames:se191XR.frames,
  lastFrameAt:se191XR.lastFrameAt,
  selectedArrival:se191XR.landing,referenceSpaceOffset:se191XR.referenceSpaceOffset,
  beaconVisible:!!se191XR.beacon?.visible,
  exitVisible:!!se181XR.exitPanel?.visible,
  controllerRays:se181XR.controllers.length,
  message:se191XR.reason,lastError:se191XR.lastError,
  nextStep:'If the VR diagnostic panel is visible but the world is black, report that distinction; if nothing renders, use Quest menu to exit.'
 };
}
window.SWYRL_ENGINE_XR_RECOVERY=Object.freeze({diagnose:se191XRDiagnostics});
