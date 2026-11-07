// §E v11.321 — building-occluded enemy sight and busy Quest head-turn metrics.
// SE321_LOS_CORE_START
const se321Sight={
  session:null,cache:new WeakMap(),tested:0,blocked:0,reused:0,
  lastReason:'Distance/stealth vision still authoritative'
};
function se321HouseBetween(a,b,house){
  const halfX=house.localHalfX??house.halfX,halfZ=house.localHalfZ??house.halfZ;
  if(!(halfX>0&&halfZ>0))return false;
  // Cheap broad phase before the rotated footprint's segment/slab test.
  const rx=house.halfX??Math.hypot(halfX,halfZ),
    rz=house.halfZ??Math.hypot(halfX,halfZ);
  if(Math.max(a.x,b.x)<house.pos.x-rx||Math.min(a.x,b.x)>house.pos.x+rx||
     Math.max(a.z,b.z)<house.pos.z-rz||Math.min(a.z,b.z)>house.pos.z+rz)return false;
  const c=Math.cos(house.rotation||0),sn=Math.sin(house.rotation||0);
  const ax=a.x-house.pos.x,az=a.z-house.pos.z,bx=b.x-house.pos.x,bz=b.z-house.pos.z;
  const x0=ax*c-az*sn,z0=ax*sn+az*c,x1=bx*c-bz*sn,z1=bx*sn+bz*c;
  let lo=0,hi=1;
  for(const [p,d,h] of [[x0,x1-x0,halfX],[z0,z1-z0,halfZ]]){
    if(Math.abs(d)<1e-9){if(p< -h||p>h)return false;continue;}
    let near=(-h-p)/d,far=(h-p)/d;
    if(near>far){const swap=near;near=far;far=swap;}
    lo=Math.max(lo,near);hi=Math.min(hi,far);
    if(hi<=lo)return false;
  }
  return lo<.995&&hi>.005;
}
const se321PriorPerceivesDirect=stPerceivesDirect;
stPerceivesDirect=function(observer,target){
  const visible=se321PriorPerceivesDirect(observer,target);
  if(!visible||!stSession||stSession.rules.fogMode==='off'||!observer||!target||
     !((observer.kind==='wolf'&&target.kind==='sheep')||
       (observer.kind==='sheep'&&target.kind==='wolf'))||
     observer.archiveOnUpper||target.archiveOnUpper)return visible;
  const s=stSession;
  if(se321Sight.session!==s){
    se321Sight.session=s;se321Sight.cache=new WeakMap();
    se321Sight.tested=0;se321Sight.blocked=0;se321Sight.reused=0;
  }
  let targets=se321Sight.cache.get(observer);
  if(!targets){targets=new WeakMap();se321Sight.cache.set(observer,targets);}
  const prior=targets.get(target);
  if(prior&&prior.at===s.elapsed&&prior.nav===s.navVersion&&
    prior.ax===observer.pos.x&&prior.az===observer.pos.z&&
    prior.bx===target.pos.x&&prior.bz===target.pos.z){
    se321Sight.reused++;return prior.visible;
  }
  let blocked=false;
  for(const house of s.buildings){
    if(house.hp<=0||house.progress<.5)continue;
    if(se321HouseBetween(observer.pos,target.pos,house)){blocked=true;break;}
  }
  se321Sight.tested++;if(blocked)se321Sight.blocked++;
  targets.set(target,{at:s.elapsed,nav:s.navVersion,
    ax:observer.pos.x,az:observer.pos.z,bx:target.pos.x,bz:target.pos.z,
    visible:!blocked});
  return !blocked;
};
// SE321_LOS_CORE_END
const se321Busy={session:null,active:false,sheep:0,wolves:0,houses:0,budget:2,
  moving:{frames:0,gapSum:0,late35:0,draws:0,maxGap:0},
  still:{frames:0,gapSum:0,late35:0,draws:0,maxGap:0}};
function se321BusyReset(session){
  se321Busy.session=session;
  for(const key of ['moving','still'])
    se321Busy[key]={frames:0,gapSum:0,late35:0,draws:0,maxGap:0};
}
function se321BudgetFor(xr,sheep,houses){
  return xr&&sheep>1&&houses>=8?1:2;
}
const se321PriorUpdate=stUpdate;
stUpdate=function(...args){
  const s=stSession;
  if(s!==se321Busy.session)se321BusyReset(s);
  if(s&&!s.simulate){
    let sheep=0,wolves=0,houses=0;
    for(const u of s.units)if(!u.captured&&!u.isIllusion){
      if(u.kind==='sheep')sheep++;else if(u.kind==='wolf')wolves++;
    }
    for(const b of s.buildings)if(b.hp>0)houses++;
    se321Busy.sheep=sheep;se321Busy.wolves=wolves;se321Busy.houses=houses;
    se321Busy.budget=se321BudgetFor(!!renderer?.xr?.isPresenting,
      sheep,houses);
    se321Busy.active=se321Busy.budget===1;
    // Keep all escape choices and scores; distribute A* evaluations across
    // more updates only in crowded, house-heavy immersive matches.
    se256AIBudget.perFrame=se321Busy.budget;
  }else{
    se321Busy.active=false;se321Busy.budget=2;
    se256AIBudget.perFrame=2;
  }
  return se321PriorUpdate(...args);
};
// Reuse the pre-existing head-pose classification: never request a new pose.
const se321PreviousSample=se286Sample;
se286Sample=function(start,at,version,prior){
  const priorMoving=se286Motion.moving.frames,
    priorStill=se286Motion.still.frames,last=se286Motion.lastAt;
  const result=se321PreviousSample(start,at,version,prior);
  if(!se321Busy.active)return result;
  const kind=se286Motion.moving.frames>priorMoving?'moving':
    se286Motion.still.frames>priorStill?'still':null;
  if(!kind)return result;
  const bucket=se321Busy[kind];
  const gap=last?start-last:0;
  if(gap>0&&gap<500){
    bucket.gapSum+=gap;bucket.maxGap=Math.max(bucket.maxGap,gap);
    if(gap>35)bucket.late35++;
  }
  bucket.frames++;
  // Previous completed render's draw count; no GPU duration available.
  bucket.draws+=renderer.info?.render?.calls||0;
  return result;
};
function se321StatsLines(page){
  const b=se321Busy,fmt=x=>Number(x||0).toFixed(1),m=b.moving,s=b.still;
  if(page===8)return [
    'CROWDED XR: '+b.sheep+' SHEEP / '+b.wolves+' WOLVES / '+b.houses+' HOUSES',
    'HEAD MOVING '+m.frames+' / STILL '+s.frames+' FRAMES',
    'AVG GAP M '+(m.frames?fmt(m.gapSum/m.frames):'--')+
      'ms / S '+(s.frames?fmt(s.gapSum/s.frames):'--')+'ms',
    'GAPS >35ms MOVING '+m.late35+' / STILL '+s.late35,
    'DRAWS/frame M '+(m.frames?fmt(m.draws/m.frames):'--')+
      ' / S '+(s.frames?fmt(s.draws/s.frames):'--'),
    'PAGE 9/10 · BUSY HEAD TURN vs STILL'
  ];
  return [
    'WOLF/SHEEP VISION: '+b.sheep+' SHEEP / '+b.wolves+' WOLVES',
    'SIGHT TESTS '+se321Sight.tested+
      ' · BLOCKED BY HOUSES '+se321Sight.blocked,
    'SAME-UPDATE SIGHT REUSE '+se321Sight.reused,
    'AI ESCAPE CANDIDATES/UPDATE '+b.budget,
    'HIDDEN ENEMIES: WOLVES SEARCH LAST SEEN POS',
    'PAGE 10/10 · VISION & AI BUDGET'
  ];
}
const se321PriorLines=se265Lines;
se265Lines=function(snapshot,page){
  if(page===8||page===9)return se321StatsLines(page);
  return se321PriorLines(snapshot,page).map(line=>
    line.replace(/PAGE ([1-8])\/8/g,'PAGE $1/10'));
};
window.SWYRL_ENGINE_SHEEP_VISION_XR_321=Object.freeze({
  diagnose:()=>({
    active:!!stSession&&!paused,
    fogMode:stSession?.rules?.fogMode||'off',
    sight:{tested:se321Sight.tested,occluded:se321Sight.blocked,
      reused:se321Sight.reused},
    busy:{active:se321Busy.active,sheep:se321Busy.sheep,
      wolves:se321Busy.wolves,houses:se321Busy.houses,
      aiCandidateBudgetPerUpdate:se321Busy.budget,
      moving:{...se321Busy.moving},still:{...se321Busy.still}},
    previousFrameDrawCountNotGPUTime:true,
    headPoseAdditionalReads:0
  })
});
