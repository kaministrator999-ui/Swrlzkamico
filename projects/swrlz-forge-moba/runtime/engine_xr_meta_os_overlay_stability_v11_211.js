// §E v11.211 · Meta Quest native Camera/menu focus-loss stabilization.
// This file cannot control the OS compositor or HMD pose. It only suspends
// app-owned XR input/camera/menu cosmetics while WebXR loses primary focus,
// and gates resume after throttled/missing XR frames. The game/host/network
// simulation and the browser's real native XR rendering are never paused.
const se211={
 session:null,listener:null,lastFrame:0,lastVisible:'none',returnUntil:0,
 cosmeticUntil:0,suspendStart:0,blurEvents:0,hiddenEvents:0,resumes:0,
 gapEvents:0,maxGapMs:0,overlayMs:0,skippedXRUpdates:0,
 skippedControllerFrames:0,blockedRigWrites:0,blockedHandInputs:0,
 renderSuspensions:0,renderRestores:0,resetDt:0,lastInterruption:'',
 savedVisible:new Map(),lastError:''
};
function se211Visibility(){
 const session=se181XR?.session;
 if(!session||!renderer.xr.isPresenting)return 'none';
 const state=session.visibilityState;
 return state==='hidden'||state==='visible-blurred'?state:'visible';
}
function se211NeutralizeHeldInputs(){
 // A/X (and alternate stick-click profiles) must require a new press after
 // OS camera closes. Do not fabricate a placement or cancel a native skill.
 for(const record of se181XR.controllers||[]){
  if(record?.se192)record.se192.actionHeld=
   !!se192Pressed(record,4);
  if(se193?.held&&record?.index!=null)
   se193.held.set(record.index,!!se192Pressed(record,5));
 }
 if(se204?.wheel)se204WheelHide();
 for(const state of Object.values(se204?.buttons||{})){
  state.held=false;state.opened=false;state.at=0;
 }
 if(se207?.grabbing)se207EndGrab(false);
 if(se210UI?.grabbing)se210PanelRelease(false);
 if(se210UI)se210UI.held=!!se192Pressed(se192InputRecord('right'),1);
}
function se211Cosmetics(active){
 if(active){
  if(se211.savedVisible.size)return;
  const add=(obj)=>{
   if(!obj||typeof obj.visible!=='boolean'||se211.savedVisible.has(obj))return;
   se211.savedVisible.set(obj,obj.visible);
   obj.visible=false;
  };
  // Cosmetic-only extras, not fog, authoritative actors or the landscape
  // collision roots. Modal game panels are restored to exactly their old
  // open/closed visibility when Quest returns.
  for(const mesh of se208?.props||[])add(mesh);
  for(const mesh of se210World?.meshes||[])add(mesh);
  add(se206?.mesh);add(se195?.radial);add(se204?.wheel?.root);
  for(const panel of se210UI?.panels?.values?.()||[])add(panel.root);
  se211.renderSuspensions++;
 }else if(se211.savedVisible.size){
  for(const [mesh,visible] of se211.savedVisible)
   if(mesh)mesh.visible=visible;
  se211.savedVisible.clear();
  // Respect the user's existing performance/auto quality state.
  if(typeof se210WorldRefreshVisibility==='function')
   se210WorldRefreshVisibility();
  se211.renderRestores++;
 }
}
function se211SetState(next,now){
 const old=se211.lastVisible;
 if(old===next)return;
 if((old==='visible-blurred'||old==='hidden')&&next==='visible'){
  if(se211.suspendStart)se211.overlayMs+=Math.max(0,now-se211.suspendStart);
  se211.suspendStart=0;se211.resumes++;
  se211.returnUntil=Math.max(se211.returnUntil,now+360);
  se211.cosmeticUntil=Math.max(se211.cosmeticUntil,now+1100);
  se211.lastInterruption='Quest OS menu returned';
  se211NeutralizeHeldInputs();
  // Reset only frame delta baselines. Do not reset the rig's tracked-space
  // referenceBase, accumulated offsets, camera yaw, zoom or scene focus.
  if(se193)se193.lastFrame=now;
  if(se195)se195.lastFrame=now;
  if(se192)se192.lastFrame=now;
  if(se210World)se210World.lastReportAt=now;
  if(se210UI)se210UI.lastAt=now;
  if(se207)se207.lastAt=now;
  se211.resetDt++;
 }
 if(next==='visible-blurred'||next==='hidden'){
  if(old!=='visible-blurred'&&old!=='hidden'){
   se211.suspendStart=now;
   se211NeutralizeHeldInputs();
  }
  if(next==='hidden')se211.hiddenEvents++;
  else se211.blurEvents++;
  se211.lastInterruption=next;
  se211Cosmetics(true);
 }
 if(next==='none'){
  se211.suspendStart=0;se211.returnUntil=0;
  se211.cosmeticUntil=0;se211Cosmetics(false);
 }
 se211.lastVisible=next;
}
function se211BindSession(){
 const current=se181XR?.session||null;
 if(current===se211.session)return;
 if(se211.session&&se211.listener)
  se211.session.removeEventListener?.('visibilitychange',se211.listener);
 se211.session=current;se211.lastFrame=0;se211.lastVisible='none';
 if(current){
  const listener=()=>se211SetState(se211Visibility(),performance.now());
  se211.listener=listener;
  current.addEventListener?.('visibilitychange',listener);
  se211SetState(se211Visibility(),performance.now());
 }else se211.listener=null;
}
function se211Sync(){
 se211BindSession();
 se211SetState(se211Visibility(),performance.now());
}
function se211Paused(){
 const now=performance.now();
 return se211Visibility()!=='visible'||now<se211.returnUntil;
}
function se211CameraSoftReturn(){
 return performance.now()<se211.returnUntil+850;
}
function se211OnFrame(){
 se211Sync();
 const now=performance.now(),state=se211Visibility();
 if(state==='visible'&&se211.lastFrame){
  const gap=now-se211.lastFrame;
  // Meta can throttle WebXR callbacks while system-owned UI has focus,
  // even when browser frame visibility transitions aren't reported.
  if(gap>170&&gap<30000){
   se211.gapEvents++;se211.maxGapMs=Math.max(se211.maxGapMs,gap);
   se211.returnUntil=Math.max(se211.returnUntil,now+300);
   se211.cosmeticUntil=Math.max(se211.cosmeticUntil,now+950);
   se211.lastInterruption='XR callback gap '+Math.round(gap)+'ms';
   se211NeutralizeHeldInputs();
   if(se193)se193.lastFrame=now;
   if(se195)se195.lastFrame=now;
   if(se192)se192.lastFrame=now;
   if(se210World)se210World.lastReportAt=now;
   se211.resetDt++;
  }
 }
 se211.lastFrame=now;
 const blocked=state!=='visible'||now<se211.returnUntil;
 se211Cosmetics(blocked||now<se211.cosmeticUntil);
 return blocked;
}
// The late wrapper is intentional: before it, twenty years of editor/game
// XR layers call one another per frame. While the Quest OS owns the user's
// attention, don't run the app's heavy radial, ray, metrics and fog adapters.
// Do NOT skip the outer game-loop simulation or the Three.js XR renderer.
const se211OldXRFrame=se193XRFrame;
se193XRFrame=function(){
 if(se211OnFrame()){se211.skippedXRUpdates++;return;}
 return se211OldXRFrame();
};
// The native controller ray renderer is a distinct frame path in §E.
// A Quest overlay may throttle it even when the full radial is hidden.
const se211OldControllerFrame=se192VRFrame;
se192VRFrame=function(){
 se211Sync();
 if(se211Paused()){
  se211.skippedControllerFrames++;
  for(const record of se181XR.controllers||[])
   if(record?.se192)record.se192.actionHeld=!!se192Pressed(record,4);
  return;
 }
 return se211OldControllerFrame();
};
// Extra safety against the earlier tracking-space reference translation
// while XR frames are blurred. No camera rotation/quaternion modification.
const se211OldMoveRig=se195MoveRig;
se195MoveRig=function(dx,dy,dz){
 se211Sync();
 if(se211Paused()){se211.blockedRigWrites++;return false;}
 return se211OldMoveRig(dx,dy,dz);
};
const se211OldStart=se193XRStart;
se193XRStart=function(){
 se211Cosmetics(false);
 se211.returnUntil=0;se211.cosmeticUntil=0;se211.lastFrame=0;
 se211BindSession();
 return se211OldStart();
};
const se211OldCleanup=se193XRCleanup;
se193XRCleanup=function(){
 se211Cosmetics(false);
 if(se211.session&&se211.listener)
  se211.session.removeEventListener?.('visibilitychange',se211.listener);
 se211.session=null;se211.listener=null;se211.lastVisible='none';
 se211.lastFrame=0;se211.returnUntil=0;se211.cosmeticUntil=0;
 return se211OldCleanup();
};
window.SWYRL_ENGINE_QUEST_OS_STABILITY_211=Object.freeze({
 diagnose:()=>({
  sessionState:se211Visibility(),paused:se211Paused(),
  overlayBlurEvents:se211.blurEvents,overlayHiddenEvents:se211.hiddenEvents,
  overlayReturns:se211.resumes,overlayTimeMs:Math.round(se211.overlayMs),
  callbackGaps:se211.gapEvents,largestGapMs:Math.round(se211.maxGapMs),
  skippedGameXRFrames:se211.skippedXRUpdates,
  skippedControllerXRFrames:se211.skippedControllerFrames,
  blockedCameraReferenceWrites:se211.blockedRigWrites,
  cosmeticsHidden:se211.savedVisible.size,
  cosmeticSuspends:se211.renderSuspensions,
  cosmeticRestores:se211.renderRestores,
  recoveryDtResets:se211.resetDt,lastCause:se211.lastInterruption,
  nativeQuestCompositorControlled:false,lastError:se211.lastError
 })
});
