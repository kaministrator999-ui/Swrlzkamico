// §E v11.286 — measure head movement versus idle during live Sheep Tag WebXR.
// Observational counters only: no XR reference-space mutation, new timer,
// renderer, scene objects, physics changes or additional head-pose reads.
const se286Motion={
  active:false,lastAt:0,poseVersion:0,poseReads:0,
  previous:null,latest:{x:0,y:0,z:0,fx:0,fy:0,fz:-1},
  lastDegrees:0,lastCm:0,unclassified:0,panels:0,rigWrites:0,
  moving:null,still:null,thresholdDeg:.18,thresholdCm:.8,
  before:null
};
function se286EmptyBucket(){
  return {frames:0,callbackTotal:0,maxGap:0,over20:0,over35:0,over70:0,
    reads:0,rig:0,rays:0,panels:0,paint:0,fog:0,draws:0,triangles:0};
}
function se286Reset(){
  se286Motion.moving=se286EmptyBucket();
  se286Motion.still=se286EmptyBucket();
  se286Motion.lastAt=0;se286Motion.previous=null;se286Motion.unclassified=0;
  se286Motion.lastDegrees=0;se286Motion.lastCm=0;
  se286Motion.before=null;
}
se286Reset();
function se286Active(){
  return !!se181XR.session&&renderer.xr.isPresenting&&se193XRGameActive();
}
// Count EXISTING pose queries. Do not request an additional HMD transform.
const se286PriorPose=se191XRHeadPose;
se191XRHeadPose=function(...args){
  const pose=se286PriorPose(...args);
  if(se286Active()&&pose?.eye&&pose?.forward){
    se286Motion.poseReads++;se286Motion.poseVersion++;
    const p=se286Motion.latest,e=pose.eye,f=pose.forward;
    // Exclude the game's accumulated camera-rig translation so sheep
    // following is not mistaken for physical headset movement.
    const rig=se195.referenceOffset;
    p.x=e.x-(rig?.x||0);p.y=e.y-(rig?.y||0);p.z=e.z-(rig?.z||0);
    p.fx=f.x;p.fy=f.y;p.fz=f.z;
  }
  return pose;
};
const se286PriorMoveRig=se195MoveRig;
se195MoveRig=function(...args){
  const done=se286PriorMoveRig(...args);
  if(done&&se286Active())se286Motion.rigWrites++;
  return done;
};
const se286PriorPlacePanel=se210Place;
se210Place=function(...args){
  if(se286Active())se286Motion.panels++;
  return se286PriorPlacePanel(...args);
};
function se286Before(){
  return {
    reads:se286Motion.poseReads,rig:se286Motion.rigWrites,
    rays:se239XR.gameplayRaySamples,panels:se286Motion.panels,
    paint:se210UI.panelPaints,fog:se195.fogPaints
  };
}
function se286Sample(start,at,version,prior){
  // A frame with no valid existing HMD read must not be called stationary.
  if(version===se286Motion.poseVersion){se286Motion.unclassified++;return;}
  const p=se286Motion.latest;
  if(![p.x,p.y,p.z,p.fx,p.fy,p.fz].every(Number.isFinite)){
    se286Motion.unclassified++;return;
  }
  const previous=se286Motion.previous;
  const fresh={x:p.x,y:p.y,z:p.z,fx:p.fx,fy:p.fy,fz:p.fz};
  se286Motion.previous=fresh;
  if(!previous){se286Motion.lastAt=at;return;}
  const dot=THREE.MathUtils.clamp(
    previous.fx*p.fx+previous.fy*p.fy+previous.fz*p.fz,-1,1);
  const angle=Math.acos(dot)*180/Math.PI;
  const cm=Math.hypot(previous.x-p.x,previous.y-p.y,previous.z-p.z)*100;
  se286Motion.lastDegrees=angle;se286Motion.lastCm=cm;
  const moving=angle>=se286Motion.thresholdDeg||cm>=se286Motion.thresholdCm;
  const bucket=moving?se286Motion.moving:se286Motion.still;
  bucket.frames++;
  const gap=se286Motion.lastAt?start-se286Motion.lastAt:0;
  se286Motion.lastAt=start;
  if(gap>0&&gap<500){
    bucket.callbackTotal+=gap;
    bucket.maxGap=Math.max(bucket.maxGap,gap);
    if(gap>20)bucket.over20++;
    if(gap>35)bucket.over35++;
    if(gap>70)bucket.over70++;
  }
  const after=se286Before();
  for(const k of ['reads','rig','rays','panels','paint','fog'])
    bucket[k]+=Math.max(0,after[k]-prior[k]);
  // THREE renderer.info reports the last completed render, not GPU time.
  bucket.draws+=renderer.info?.render?.calls||0;
  bucket.triangles+=renderer.info?.render?.triangles||0;
}
const se286PriorFrame=se193XRFrame;
se193XRFrame=function(...args){
  if(!se286Active()){
    if(se286Motion.active){se286Motion.active=false;se286Reset();}
    return se286PriorFrame(...args);
  }
  if(!se286Motion.active){se286Reset();se286Motion.active=true;}
  const start=performance.now(),version=se286Motion.poseVersion;
  const prior=se286Before();
  // Collect the game callbacks first; instrument only their existing work.
  const result=se286PriorFrame(...args);
  if(se286Active())se286Sample(start,performance.now(),version,prior);
  return result;
};
function se286Average(total,bucket){
  return bucket.frames?(total/bucket.frames).toFixed(1):'--';
}
function se286GapAverage(bucket){
  return bucket.frames?(bucket.callbackTotal/bucket.frames).toFixed(1):'--';
}
function se286Lines(page){
  const m=se286Motion.moving,s=se286Motion.still;
  if(page===4)return [
    'HEAD TURN '+se286Motion.lastDegrees.toFixed(2)+' deg / MOVE '+se286Motion.lastCm.toFixed(1)+' cm',
    'FRAMES: MOVING '+m.frames+' / STILL '+s.frames,
    'XR GAP AVG ms M '+se286GapAverage(m)+' / S '+se286GapAverage(s),
    'GAPS >35ms M '+m.over35+' / S '+s.over35,
    'DRAWS/frame M '+se286Average(m.draws,m)+' / S '+se286Average(s.draws,s),
    'PAGE 5/6 · MOTION vs STILL'
  ];
  return [
    'POSE READS/frame M '+se286Average(m.reads,m)+' / S '+se286Average(s.reads,s),
    'XR RIG WRITES M '+m.rig+' / S '+s.rig,
    'GAME RAYS/frame M '+se286Average(m.rays,m)+' / S '+se286Average(s.rays,s),
    'PANEL PLACES M '+m.panels+' / S '+s.panels,
    'HUD PAINTS M '+m.paint+' / S '+s.paint,
    'PAGE 6/6 · COUNTS DURING GAME'
  ];
}
const se286PriorLines=se265Lines;
se265Lines=function(snapshot,page){
  if(page===4||page===5)return se286Lines(page);
  return se286PriorLines(snapshot,page).map(x=>x.replace(/PAGE ([1-4])\/4/g,'PAGE $1/6'));
};
const se286PriorCleanup=se193XRCleanup;
se193XRCleanup=function(...args){
  se286Motion.active=false;se286Reset();
  return se286PriorCleanup(...args);
};
window.SWYRL_ENGINE_QUEST_HEAD_MOTION_286=Object.freeze({
  diagnose:()=>({
    active:se286Motion.active,
    movementThresholdDegreesPerFrame:se286Motion.thresholdDeg,
    translationThresholdCmPerFrame:se286Motion.thresholdCm,
    latestAngularDeltaDegrees:se286Motion.lastDegrees,
    latestTranslationDeltaCm:se286Motion.lastCm,
    moving:{...se286Motion.moving},still:{...se286Motion.still},
    headPoseUnavailableFrames:se286Motion.unclassified,
    callbackTimingNotGpuTime:true,
    drawCountsFromPreviousCompletedRender:true,
    sampleScope:'Sheep Tag immersive gameplay only',
    noAdditionalPoseReads:true
  })
});