/* SE439_SHEEP_CAPTURE_PURSUIT_START */
// Quest SOLO pursuit: avoid nine synchronous A* approach probes per moving
// sheep, keep native swept collision, and count capture work separately.
const se439Telemetry={session:null,approachChecks:0,directApproaches:0,blockedApproaches:0,
  approachCpuMs:0,maxApproachMs:0,botPlans:0,deferredWolfPlans:0,
  directRoutes:0,contactSweeps:0,sweptTags:0,eligibleChecks:0,
  inRangeChecks:0,actualCaptures:0,duplicateAttempts:0,captureCpuMs:0,
  maxCaptureCpuMs:0,maxCaptureFrameMs:0,postCaptureMaxFrameMs:0,
  lastCaptureFrameMs:0,lastCaptureCpuMs:0,navChangeCaptures:0};
let se439PlanningAt=-1,se439PlanningSession=null,se439PlansUsed=0;
let se439UpdatingWolf=null,se439CaptureSequence=0,se439AfterTicks=0;
const se439Recent=[];
function se439SoloXR(s){
 return !!s&&!s.simulate&&!s.winner&&renderer.xr?.isPresenting&&
  typeof se437Solo==='function'&&se437Solo(s);
}
function se439Reset(s){
 if(se439Telemetry.session===s)return;
 se439Telemetry.session=s;se439PlanningSession=s;se439PlanningAt=-1;se439PlansUsed=0;
 se439AfterTicks=0;se439Recent.length=0;
 for(const key of Object.keys(se439Telemetry))if(key!=='session')se439Telemetry[key]=0;
}
const se439NativeApproach=stLanesSheepApproach;
stLanesSheepApproach=function(wolf,sheep){
 const s=stSession;
 if(!se439SoloXR(s))return se439NativeApproach(wolf,sheep);
 se439Reset(s);
 const began=performance.now();se439Telemetry.approachChecks++;
 try{
  if(Math.abs(wolf.pos.y-sheep.pos.y)>=1.2)return null;
  // If the static lane is clear, the sheep's *current* position is a valid
  // pursuit aim. Native movement still performs body/collision checks.
  const context={rules:s.rules,obstacles:stObstacles()},r=stUnitRadius(wolf);
  if(stSegmentClear(context,wolf.pos,sheep.pos,r)){
   se439Telemetry.directApproaches++;return sheep.pos.clone();
  }
  // A crowded/blocked lane remains for the existing wolf/building planner.
  // Do not evaluate up to 9 synchronous A* paths on every moving target.
  se439Telemetry.blockedApproaches++;return null;
 }finally{
  const ms=performance.now()-began;se439Telemetry.approachCpuMs+=ms;
  se439Telemetry.maxApproachMs=Math.max(ms,se439Telemetry.maxApproachMs);
 }
};
function se439DirectChase(unit,aim,context){
 const s=stSession;
 if(!se439SoloXR(s)||unit.kind!=='wolf'||unit.order?.action!=='attack')return false;
 const sheep=s.units.find(u=>u.id===unit.order.id&&u.kind==='sheep'&&!u.captured);
 if(!sheep||Math.abs(unit.pos.y-sheep.pos.y)>=1.2||aim.distanceToSquared(sheep.pos)>.16)return false;
 if(unit.pos.distanceToSquared(sheep.pos)>36)return false;
 if(!stSegmentClear(context,unit.pos,aim,stUnitRadius(unit)))return false;
 se439Telemetry.directRoutes++;return true;
}
// One full wolf AI decision per SOLO XR simulation tick. This does not
// throttle unit movement, contact checks or non-XR / LAN gameplay.
const se439PriorBotWolf=stBotWolf;
stBotWolf=function(unit){
 const s=stSession;
 if(!se439SoloXR(s)||s.elapsed<s.rules.headstart||s.elapsed<unit.botAt||
    unit.archiveRoute)return se439PriorBotWolf.apply(this,arguments);
 se439Reset(s);
 if(se439PlanningSession!==s||se439PlanningAt!==s.elapsed){
  se439PlanningSession=s;se439PlanningAt=s.elapsed;se439PlansUsed=0;
 }
 if(se439PlansUsed>=1){
  se439Telemetry.deferredWolfPlans++;return;
 }
 se439PlansUsed++;se439Telemetry.botPlans++;
 return se439PriorBotWolf.apply(this,arguments);
};
// Native body collision can reject the entire 0.09-unit movement step as it
// enters a sheep's radius. Capture is legal as soon as the swept step reaches
// the EXISTING 1.05-unit tag radius, even if that physical step is blocked.
const se439PriorOccupant=stLanesSegmentOccupant;
stLanesSegmentOccupant=function(unit,a,b){
 const blocker=se439PriorOccupant.apply(this,arguments);
 const s=stSession;
 if(se439UpdatingWolf!==unit||!se439SoloXR(s)||unit.kind!=='wolf'||
    blocker?.kind!=='sheep'||blocker.captured||
    s.elapsed<blocker.invulnerableUntil||Math.abs(unit.pos.y-blocker.pos.y)>=1.2)return blocker;
 se439Telemetry.contactSweeps++;
 const dx=b.x-a.x,dz=b.z-a.z,den=dx*dx+dz*dz;
 const t=den?Math.min(1,Math.max(0,((blocker.pos.x-a.x)*dx+(blocker.pos.z-a.z)*dz)/den)):0;
 const x=a.x+dx*t,z=a.z+dz*t;
 if((x-blocker.pos.x)**2+(z-blocker.pos.z)**2<1.05**2)
  unit.se439SweptContact={sheep:blocker,session:s,at:s.elapsed};
 return blocker;
};
const se439PriorWolfUpdate=stUpdateWolf;
stUpdateWolf=function(wolf,dt){
 const s=stSession;
 if(!se439SoloXR(s))return se439PriorWolfUpdate.apply(this,arguments);
 se439Reset(s);
 // Observe candidate counts without replacing or duplicating the native
 // capture scan. The native movement and capture decision remain unchanged.
 for(const target of s.units){
  if(target.kind!=='sheep'||target.captured||s.elapsed<target.invulnerableUntil)continue;
  se439Telemetry.eligibleChecks++;
  const dx=wolf.pos.x-target.pos.x,dz=wolf.pos.z-target.pos.z;
  if(dx*dx+dz*dz<1.05**2)se439Telemetry.inRangeChecks++;
 }
 wolf.se439SweptContact=null;se439UpdatingWolf=wolf;
 let result;
 try{result=se439PriorWolfUpdate.apply(this,arguments);}
 finally{se439UpdatingWolf=null;}
 const touch=wolf.se439SweptContact;wolf.se439SweptContact=null;
 if(touch?.session===s&&touch.at===s.elapsed&&!touch.sheep.captured&&
    s.elapsed>=touch.sheep.invulnerableUntil){
  se439Telemetry.sweptTags++;stCapture(touch.sheep,wolf);
 }
 return result;
};
const se439PriorCapture=stCapture;
stCapture=function(unit,wolf){
 const s=stSession;if(s&&se439SoloXR(s))se439Reset(s);
 if(unit?.captured){
  if(s&&se439SoloXR(s))se439Telemetry.duplicateAttempts++;
  return se439PriorCapture.apply(this,arguments);
 }
 if(!s||!se439SoloXR(s))return se439PriorCapture.apply(this,arguments);
 const began=performance.now(),nav=s.navVersion;
 const result=se439PriorCapture.apply(this,arguments);
 if(unit.captured){
  const ms=performance.now()-began;
  se439Telemetry.actualCaptures++;se439Telemetry.captureCpuMs+=ms;
  se439Telemetry.lastCaptureCpuMs=+ms.toFixed(2);
  se439Telemetry.maxCaptureCpuMs=Math.max(ms,se439Telemetry.maxCaptureCpuMs);
  se439Telemetry.navChangeCaptures+=Number(s.navVersion!==nav);
  se439CaptureSequence++;se439AfterTicks=3;
  se439Recent.push({time:+s.elapsed.toFixed(2),sheep:String(unit.id),
    wolf:String(wolf?.id||''),captureCpuMs:+ms.toFixed(2),navChanged:s.navVersion!==nav});
  if(se439Recent.length>8)se439Recent.shift();
 }
 return result;
};
const se439PriorUpdate=stUpdate;
stUpdate=function(...args){
 const s=stSession,serial=se439CaptureSequence,start=performance.now();
 let result;
 try{result=se439PriorUpdate.apply(this,args);}
 finally{
  if(s&&se439SoloXR(s)){
   const ms=performance.now()-start;
   if(serial!==se439CaptureSequence){
    se439Telemetry.lastCaptureFrameMs=+ms.toFixed(2);
    se439Telemetry.maxCaptureFrameMs=Math.max(ms,se439Telemetry.maxCaptureFrameMs);
   }else if(se439AfterTicks>0){
    se439Telemetry.postCaptureMaxFrameMs=Math.max(ms,se439Telemetry.postCaptureMaxFrameMs);
    se439AfterTicks--;
   }
  }
 }
 return result;
};
window.SWYRL_ENGINE_SHEEP_CAPTURE_PURSUIT_439=Object.freeze({
 diagnose:()=>({...Object.fromEntries(Object.entries(se439Telemetry).filter(([k])=>k!=='session')),
  active:!!stSession,soloXR:se439SoloXR(stSession),recentCaptures:se439Recent.slice(),
  capturesAreOneShot:true,tagRadius:1.05,workerAndLanAuthorityUnchanged:true,
  cpuTimingExcludesGPUCompositor:true})
});
/* SE439_SHEEP_CAPTURE_PURSUIT_END */
