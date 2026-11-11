// §E v11.393 — time-slice NPC sheep base/build planning in SOLO Quest XR.
// Prevent a single headset frame from examining 12 building sites and 24
// route searches per AI sheep; human motion/physics still run on every tick.
const se393Plan={session:null,frame:-1,used:0,perFrame:1,
  baseStarted:0,baseFinished:0,buildStarted:0,buildFinished:0,
  buildExhausted:0,checks:0,waits:0,visibilityReuse:0,visibilityTests:0};
let se393SightCache=new WeakMap();
function se393Active(){
  return !!stSession&&!stSession.simulate&&!!renderer?.xr?.isPresenting&&
    se193XRGameActive()&&
    !(typeof se150Match!=='undefined'&&se150Match.active);
}
function se393ResetSession(s){
  if(se393Plan.session===s)return;
  se393Plan.session=s;se393Plan.frame=-1;se393Plan.used=0;
  for(const key of ['baseStarted','baseFinished','buildStarted',
      'buildFinished','buildExhausted','checks','waits','visibilityReuse',
      'visibilityTests'])se393Plan[key]=0;
  se393SightCache=new WeakMap();
}
function se393TakeSlot(){
  const s=stSession;
  se393ResetSession(s);
  if(se393Plan.frame!==s.elapsed){
    se393Plan.frame=s.elapsed;se393Plan.used=0;
  }
  if(se393Plan.used>=se393Plan.perFrame){se393Plan.waits++;return false;}
  se393Plan.used++;se393Plan.checks++;
  return true;
}
function se393CancelSheepPlan(unit){
  if(unit){unit.se393Base=null;unit.se393Build=null;}
}
function se393ChooseSheepBase(unit){
  if(unit.base){unit.se393Base=null;return true;}
  const s=stSession;
  let scan=unit.se393Base;
  if(!scan){
    const known=stBotKnownEnemies(unit);
    const candidates=[unit.home.clone(),
      ...s.buildings.filter(b=>b.hp>0&&s.units.some(u=>
        u.id===b.owner&&u.kind==='sheep')).slice(0,12)
        .map(b=>b.pos.clone().add(new THREE.Vector3(4.5,0,4.5)))];
    scan=unit.se393Base={known,candidates,index:0,
      best:unit.home.clone(),score:-Infinity};
    se393Plan.baseStarted++;
  }
  if(!se393TakeSlot())return false;
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
  unit.base=scan.best;unit.se393Base=null;se393Plan.baseFinished++;
  return true;
}
function se393PlanSheepBuild(unit){
  const s=stSession;
  let scan=unit.se393Build;
  if(!scan){
    if(s.elapsed<unit.nextBuildAt)return false;
    unit.nextBuildAt=s.elapsed+5+unit.phase*.25;
    const owned=s.buildings.filter(b=>b.owner===unit.id&&b.hp>0);
    if(owned.length>=Math.min(12,s.rules.houseLimit??28))return false;
    const kind=!owned.some(b=>b.kind==='st-income')&&
      (s.resources[unit.id]||0)>=60?'st-income':
      (s.resources[unit.id]||0)>150&&owned.length%4===3?'st-fort':'st-farm';
    scan=unit.se393Build={index:0,kind,baseX:unit.base.x,baseZ:unit.base.z,
      offsets:[[-3,-3],[0,-3],[3,-3],[-3,0],[3,0],[-3,3],
               [0,3],[3,3],[-3,6],[3,6],[0,9],[-6,0]]};
    se393Plan.buildStarted++;
  }
  if(!se393TakeSlot())return true;
  const j=scan.index++,offset=scan.offsets[(j+unit.botIndex)%scan.offsets.length];
  const x=scan.baseX+offset[0],z=scan.baseZ+offset[1],
    result=stCanBuild(scan.kind,x,z,unit.id);
  if(result.ok){
    const proposed={rules:s.rules,obstacles:[...stObstacles(),
      stFootprint(result.x,result.z,1.2,1.2)]};
    const nav=stBuildNavigation(proposed,stUnitRadius(unit));
    const exits=[new THREE.Vector3(unit.base.x,0,unit.base.z+7.5),
      new THREE.Vector3(unit.base.x+7.5,0,unit.base.z)];
    if(exits.some(p=>stFindPath(nav,unit.pos,p))&&
       stIssueBuild(unit,scan.kind,x,z).ok){
      unit.aiIntent='build a compact maze with a viable sheep exit';
      unit.se393Build=null;se393Plan.buildFinished++;return true;
    }
  }
  if(scan.index<scan.offsets.length)return true;
  unit.se393Build=null;se393Plan.buildExhausted++;
  return false;
}
const se393PriorSeenByRole=stSeenByRole;
stSeenByRole=function(entity,role=stSession?.role){
  const s=stSession;
  if(!se393Active()||!entity||!s)
    return se393PriorSeenByRole(entity,role);
  se393ResetSession(s);
  const p=entity.spirit?.position||entity.pos;
  const x=p?.x,z=p?.z,captured=!!entity.captured;
  const previous=se393SightCache.get(entity);
  if(previous&&previous.elapsed===s.elapsed&&previous.nav===s.navVersion&&
     previous.role===role&&previous.x===x&&previous.z===z&&
     previous.captured===captured){
    se393Plan.visibilityReuse++;
    return previous.value;
  }
  const value=se393PriorSeenByRole(entity,role);
  se393Plan.visibilityTests++;
  se393SightCache.set(entity,{elapsed:s.elapsed,nav:s.navVersion,
    role,x,z,captured,value});
  return value;
};
window.SWYRL_ENGINE_SHEEP_AI_FRAME_BUDGET_393=Object.freeze({
  diagnose:()=>({
    active:se393Active(),soloXrOnly:true,aiCandidatesPerGameTick:se393Plan.perFrame,
    basePlansStarted:se393Plan.baseStarted,basePlansCompleted:se393Plan.baseFinished,
    buildingPlansStarted:se393Plan.buildStarted,
    buildingPlansCompleted:se393Plan.buildFinished,
    buildingPlansExhausted:se393Plan.buildExhausted,
    planningCandidatesEvaluated:se393Plan.checks,
    deferredBotPlanning:se393Plan.waits,
    visibilityQueries:se393Plan.visibilityTests,
    duplicateSameTickVisibilityAvoided:se393Plan.visibilityReuse,
    pendingBase:stSession?.units?.filter(u=>!!u.se393Base).length||0,
    pendingBuilding:stSession?.units?.filter(u=>!!u.se393Build).length||0,
    controlledSheepMotionEveryFrame:true,
    collisionAndGameplayRulesUnchanged:true,
    cameraAndWebXRPoseUnchanged:true
  })
});
