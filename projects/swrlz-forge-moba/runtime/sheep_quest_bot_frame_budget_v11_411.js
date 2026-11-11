// §E v11.411 — time-slice NPC sheep base/build planning in SOLO Quest XR.
// Prevent a single headset frame from examining 12 building sites and 24
// route searches per AI sheep; human motion/physics still run on every tick.
const se411Plan={session:null,frame:-1,used:0,perFrame:1,
  baseStarted:0,baseFinished:0,buildStarted:0,buildFinished:0,
  buildExhausted:0,checks:0,waits:0,visibilityReuse:0,visibilityTests:0};
let se411SightCache=new WeakMap();
function se411Active(){
  return !!stSession&&!stSession.simulate&&!!renderer?.xr?.isPresenting&&
    se193XRGameActive()&&
    !(typeof se150Match!=='undefined'&&se150Match.active);
}
function se411ResetSession(s){
  if(se411Plan.session===s)return;
  se411Plan.session=s;se411Plan.frame=-1;se411Plan.used=0;
  for(const key of ['baseStarted','baseFinished','buildStarted',
      'buildFinished','buildExhausted','checks','waits','visibilityReuse',
      'visibilityTests'])se411Plan[key]=0;
  se411SightCache=new WeakMap();
}
function se411TakeSlot(){
  const s=stSession;
  se411ResetSession(s);
  if(se411Plan.frame!==s.elapsed){
    se411Plan.frame=s.elapsed;se411Plan.used=0;
  }
  if(se411Plan.used>=se411Plan.perFrame){se411Plan.waits++;return false;}
  se411Plan.used++;se411Plan.checks++;
  return true;
}
function se411CancelSheepPlan(unit){
  if(unit){unit.se411Base=null;unit.se411Build=null;}
}
function se411ChooseSheepBase(unit){
  if(unit.base){unit.se411Base=null;return true;}
  const s=stSession;
  let scan=unit.se411Base;
  if(!scan){
    const known=stBotKnownEnemies(unit);
    const candidates=[unit.home.clone(),
      ...s.buildings.filter(b=>b.hp>0&&s.units.some(u=>
        u.id===b.owner&&u.kind==='sheep')).slice(0,12)
        .map(b=>b.pos.clone().add(new THREE.Vector3(4.5,0,4.5)))];
    scan=unit.se411Base={known,candidates,index:0,
      best:unit.home.clone(),score:-Infinity};
    se411Plan.baseStarted++;
  }
  if(!se411TakeSlot())return false;
  const p=scan.candidates[scan.index++];
  p.x=Math.round(p.x/.15)*.15;p.z=Math.round(p.z/.15)*.15;
  const bounds=s.rules.bounds,r=stUnitRadius(unit);
  const permitted=Math.abs(p.x)<=bounds-8&&Math.abs(p.z)<=bounds-8&&
    !(Math.abs(p.x-s.pen.x)<s.pen.reserveX+8&&
      Math.abs(p.z-s.pen.z)<s.pen.reserveZ+8);
  if(permitted&&!stBlocked(p.x,p.z,r)){
    const safety=scan.known.length?
      Math.min(...scan.known.map(e=>p.distanceToSquared(e.pos))):200;
    const value=safety-unit.pos.distanceToSquared(p)*.3;
    if(value>scan.score&&stPath(unit.pos,p,r)){
      scan.score=value;scan.best=p;
    }
  }
  if(scan.index<scan.candidates.length)return false;
  unit.base=scan.best;unit.se411Base=null;se411Plan.baseFinished++;
  return true;
}
function se411PlanSheepBuild(unit){
  const s=stSession;
  let scan=unit.se411Build;
  if(!scan){
    if(s.elapsed<unit.nextBuildAt)return false;
    unit.nextBuildAt=s.elapsed+5+unit.phase*.25;
    const owned=s.buildings.filter(b=>b.owner===unit.id&&b.hp>0);
    if(owned.length>=Math.min(12,s.rules.houseLimit??28))return false;
    const kind=!owned.some(b=>b.kind==='st-income')&&
      (s.resources[unit.id]||0)>=60?'st-income':
      (s.resources[unit.id]||0)>150&&owned.length%4===3?'st-fort':'st-farm';
    scan=unit.se411Build={index:0,kind,baseX:unit.base.x,baseZ:unit.base.z,
      offsets:[[-3,-3],[0,-3],[3,-3],[-3,0],[3,0],[-3,3],
               [0,3],[3,3],[-3,6],[3,6],[0,9],[-6,0]]};
    se411Plan.buildStarted++;
  }
  if(!se411TakeSlot())return true;
  const j=scan.index++,offset=scan.offsets[(j+unit.botIndex)%scan.offsets.length];
  const x=scan.baseX+offset[0],z=scan.baseZ+offset[1],
    result=stCanBuild(scan.kind,x,z,unit.id);
  if(result.ok){
    const proposed={rules:s.rules,obstacles:[...stObstacles(),
      stFootprint(result.x,result.z,1.2,1.2)]};
    const nav=s.rules.bounds>80?null:stBuildNavigation(proposed,stUnitRadius(unit));
    const exits=[new THREE.Vector3(unit.base.x,0,unit.base.z+7.5),
      new THREE.Vector3(unit.base.x+7.5,0,unit.base.z)];
    if(exits.some(p=>nav?stFindPath(nav,unit.pos,p):stVastFindPath(proposed,unit.pos,p,stUnitRadius(unit)))&&
       stIssueBuild(unit,scan.kind,x,z).ok){
      unit.aiIntent='build a compact maze with a viable sheep exit';
      unit.se411Build=null;se411Plan.buildFinished++;return true;
    }
  }
  if(scan.index<scan.offsets.length)return true;
  unit.se411Build=null;se411Plan.buildExhausted++;
  return false;
}
const se411PriorSeenByRole=stSeenByRole;
stSeenByRole=function(entity,role=stSession?.role){
  const s=stSession;
  if(!se411Active()||!entity||!s)
    return se411PriorSeenByRole(entity,role);
  se411ResetSession(s);
  const p=entity.spirit?.position||entity.pos;
  const x=p?.x,z=p?.z,captured=!!entity.captured;
  const previous=se411SightCache.get(entity);
  if(previous&&previous.elapsed===s.elapsed&&previous.nav===s.navVersion&&
     previous.role===role&&previous.x===x&&previous.z===z&&
     previous.captured===captured){
    se411Plan.visibilityReuse++;
    return previous.value;
  }
  const value=se411PriorSeenByRole(entity,role);
  se411Plan.visibilityTests++;
  se411SightCache.set(entity,{elapsed:s.elapsed,nav:s.navVersion,
    role,x,z,captured,value});
  return value;
};
window.SWYRL_ENGINE_SHEEP_AI_FRAME_BUDGET_411=Object.freeze({
  diagnose:()=>({
    active:se411Active(),soloXrOnly:true,aiCandidatesPerGameTick:se411Plan.perFrame,
    basePlansStarted:se411Plan.baseStarted,basePlansCompleted:se411Plan.baseFinished,
    buildingPlansStarted:se411Plan.buildStarted,
    buildingPlansCompleted:se411Plan.buildFinished,
    buildingPlansExhausted:se411Plan.buildExhausted,
    planningCandidatesEvaluated:se411Plan.checks,
    deferredBotPlanning:se411Plan.waits,
    visibilityQueries:se411Plan.visibilityTests,
    duplicateSameTickVisibilityAvoided:se411Plan.visibilityReuse,
    pendingBase:stSession?.units?.filter(u=>!!u.se411Base).length||0,
    pendingBuilding:stSession?.units?.filter(u=>!!u.se411Build).length||0,
    controlledSheepMotionEveryFrame:true,
    collisionAndGameplayRulesUnchanged:true,
    cameraAndWebXRPoseUnchanged:true
  })
});
