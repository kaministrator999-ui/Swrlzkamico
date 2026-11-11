// §E v11.392 — reduce the frequency of Sheep Tag FOLLOW reference-space writes.
// Quest owner A/B: FREE removes world repaint/geometry distortion; remaining
// frame-freezes need independent XR callback investigation.
const se392Follow={minIntervalMs:140,minDistance:.12,maxStep:.62,metersPerSecond:4.8,
  lastWriteAt:0,writes:0,skippedCadence:0,skippedSmall:0,lastStep:0,
  largestStep:0,resets:0};
function se392FollowPlan(distance,at){
  if(!Number.isFinite(distance)||distance<se392Follow.minDistance){
    se392Follow.skippedSmall++;return 0;
  }
  const elapsed=se392Follow.lastWriteAt?
    at-se392Follow.lastWriteAt:se392Follow.minIntervalMs;
  if(!Number.isFinite(elapsed)||elapsed<se392Follow.minIntervalMs){
    se392Follow.skippedCadence++;return 0;
  }
  const seconds=Math.min(.22,Math.max(.14,elapsed/1000));
  return Math.min(distance*.82,se392Follow.maxStep,
    se392Follow.metersPerSecond*seconds);
}
function se392FollowCommit(at,step=0){
  se392Follow.lastWriteAt=at;se392Follow.writes++;
  se392Follow.lastStep=step;
  se392Follow.largestStep=Math.max(se392Follow.largestStep,step);
}
function se392FollowReset(){
  se392Follow.lastWriteAt=0;se392Follow.writes=0;
  se392Follow.skippedCadence=se392Follow.skippedSmall=0;
  se392Follow.lastStep=se392Follow.largestStep=0;
  se392Follow.resets++;
}
const se392PriorStart=se193XRStart;
se193XRStart=function(...args){
  se392FollowReset();
  return se392PriorStart(...args);
};
window.SWYRL_ENGINE_SHEEP_STABLE_FOLLOW_392=Object.freeze({
  diagnose:()=>({
    xr:!!se181XR.session&&renderer.xr.isPresenting,
    gameplay:se193XRGameActive(),follow:!!se193.follow,
    intervalMs:se392Follow.minIntervalMs,
    movementThresholdMeters:se392Follow.minDistance,
    stepCapMeters:se392Follow.maxStep,
    referenceWrites:se392Follow.writes,
    skippedCadence:se392Follow.skippedCadence,
    skippedSmallMovements:se392Follow.skippedSmall,
    lastStepMeters:se392Follow.lastStep,
    largestStepMeters:se392Follow.largestStep,
    freeCameraUntouched:true,
    ownerHeadsetAcceptancePending:true
  })
});
