// §E v11.234 candidate — budget Sheep Tag's own reference-space writes.
// Head tracking is XR compositor-owned. Never use changing HMD position as a
// gameplay follow error; only world-space sheep/orbit/zoom changes may move the rig.
// This late adapter preserves v11.200/202/205/211/214/216 camera/input ownership.
const se234Camera={
  minTranslation:0.055, minIntervalMs:28, urgentTranslation:0.30,
  lastWriteAt:0, lastApplied:null, worldWriteAttempts:0,
  worldWrites:0, skippedTiny:0, skippedDense:0, noGameFrames:0
};
const se234OldAnchor=se200CameraAnchor;
se200CameraAnchor=function(){
  const desired=se234OldAnchor();
  if(!se200Active()||!se200.anchorReady||!se195.rigReady||
     !se200.applied){se234Camera.noGameFrames++;return desired;}
  // Source follows sheep/world coordinates only; no live headset pose here.
  const current=se200.applied, now=performance.now();
  const remaining=desired.distanceTo(current);
  if(remaining<se234Camera.minTranslation){
    se234Camera.skippedTiny++;
    return current.clone(); // Native follow sees no movement to apply.
  }
  if(now-se234Camera.lastWriteAt<se234Camera.minIntervalMs&&
     remaining<se234Camera.urgentTranslation){
    se234Camera.skippedDense++;
    return current.clone(); // Keep the unapplied world delta for a later frame.
  }
  return desired;
};
const se234OldMoveRig=se195MoveRig;
se195MoveRig=function(dx,dy,dz){
  const game=se200Active()&&se200.anchorReady;
  if(game)se234Camera.worldWriteAttempts++;
  const ok=se234OldMoveRig(dx,dy,dz); // Keep v11.211 focus/held-input guards.
  if(ok&&game){
    se234Camera.lastWriteAt=performance.now();
    se234Camera.worldWrites++;
    se234Camera.lastApplied={dx,dy,dz};
  }
  return ok;
};
const se234PreviousStart=se193XRStart;
se193XRStart=function(){
  se234Camera.lastWriteAt=0;se234Camera.lastApplied=null;
  return se234PreviousStart();
};
const se234PreviousCleanup=se193XRCleanup;
se193XRCleanup=function(){
  se234Camera.lastWriteAt=0;
  return se234PreviousCleanup();
};
window.SWYRL_ENGINE_QUEST_FRAME_BUDGET_234=Object.freeze({
  diagnose:()=>({
    active:se200Active(),nativeHeadTrackingUnchanged:true,
    referenceWrites:se234Camera.worldWrites,
    referenceAttempts:se234Camera.worldWriteAttempts,
    tinyWorldDeltasSuppressed:se234Camera.skippedTiny,
    excessiveWriteRateSuppressed:se234Camera.skippedDense,
    lastWorldTranslation:se234Camera.lastApplied,
    minTranslation:se234Camera.minTranslation,
    minIntervalMs:se234Camera.minIntervalMs,
    source:'world-anchor only',
    existingWorldFollowWrites:se200.referenceWrites,
    focusGuard:window.SWYRL_ENGINE_QUEST_OS_STABILITY_211?.diagnose?.()||null
  })
});
