// Frostveil v11.2 opt-in flight controls. v11.1 walk-v1 imports remain untouched.
const MAUL_FLIGHT_PROFILE='hover-v1';
MAUL_BATCH_CANONICAL_PROJECT.project.maulBuilderFlight=MAUL_FLIGHT_PROFILE;
// The launchable Projects tile loads the independently saved v11.2 starter scene.
// The earlier grouped scene stays available for historical imports/replays.
const maulFlightPriorStarter=maulLoadStarter;
maulLoadStarter=function(){
  if(!MAUL_FLIGHT_CANONICAL_PROJECT?.scene?.actors?.length)return maulFlightPriorStarter();
  loadProject(structuredClone(MAUL_FLIGHT_CANONICAL_PROJECT),{workspaceLocal:true});
  maulFrameMap();initializeHistory('Opened Frostveil Maul · flying builders');
  markSaved();toast('Frostveil Maul · flying builders and glacial map');return true;
};
const maulFlightEnabled=()=>maulWalkBuildEnabled()&&currentProject?.maulBuilderFlight===MAUL_FLIGHT_PROFILE;
let maulFlightSuppressGroundMove=false;
const maulFlightNativePosition=maulSetActorWorldPosition;
maulSetActorWorldPosition=function(actor,position){
  if(maulFlightSuppressGroundMove&&maulFlightEnabled()&&actor?.userData?.actorType==='maul-builder')return;
  return maulFlightNativePosition(actor,position);
};
const maulFlightNativePlan=maulPlanWalkBuild;
maulPlanWalkBuild=function(kind,cx,cz){
  if(!maulFlightEnabled())return maulFlightNativePlan(kind,cx,cz);
  if(!maulSession||paused||['won','lost'].includes(maulSession.phase))return {ok:false,reason:'Resume an active match to build.'};
  if(kind==='maze-wall')return {ok:false,reason:'Use towers to shape the maze, not standalone walls.'};
  const fit=MAUL_CORE.canBuild(maulSession,kind,cx,cz);
  if(!fit.ok)return fit;
  const sector=maulSession.selectedSector;
  const builder=actors.find(a=>a.userData.actorType==='maul-builder'&&a.userData.maul?.sector===sector);
  if(!builder)return {ok:false,reason:'No builder is assigned to this sector.'};
  const site={x:cx,z:cz},start=maulActorCell(maulSession.map,builder);
  const plan=MAUL_FLIGHT_CORE.plan(maulSession.map,start,site,sector);
  if(!plan.ok)return plan;
  if([...maulPendingBuilds.values()].some(p=>p.cx===cx&&p.cz===cz&&p.builderId!==builder.userData.id))
    return {ok:false,reason:'Another builder already has this site.'};
  return {ok:true,fit,builder,plan,sector};
};
const maulFlightNativeOrder=maulOrder;
maulOrder=function(command){
  if(!maulFlightEnabled()||command?.type!=='move-builder')return maulFlightNativeOrder(command);
  if(!maulSession||paused||['won','lost'].includes(maulSession.phase))
    return {ok:false,reason:'Resume Play to move your builder.'};
  const world=maulScreenWorld(command.clientX,command.clientY);
  const sector=maulSession.selectedSector;
  const builder=actors.find(a=>a.userData.actorType==='maul-builder'&&a.userData.maul?.sector===sector);
  const cell=world&&MAUL_CORE.worldToCell(maulSession.map,world.x,world.z);
  if(!builder||!MAUL_FLIGHT_CORE.allowed(maulSession.map,cell,sector)){
    const result={ok:false,reason:'Fly to a position inside your own defense sector.'};
    maulUIFeedback(result.reason,true);maulRefreshHUD(true);return result;
  }
  maulSession.builderOrders??={};
  maulSession.builderOrders[builder.userData.id]={path:[cell],index:0,flight:true};
  if(maulPendingBuilds.delete(builder.userData.id))
    stRunGuard(()=>stRunNote('maul-build-cancelled',builder.userData.id,{reason:'Builder received a flying move order'}));
  stRunGuard(()=>stRunNote('maul-flight-move',builder.userData.id,{cx:cell.x,cz:cell.z,sector}));
  maulUIFeedback('Builder flying above the battlefield.');maulRefreshHUD(true);
  return {ok:true,code:'flying',destination:cell};
};
const maulFlightNativeUpdate=maulUpdate;
maulUpdate=function(dt){
  if(!maulFlightEnabled()||!maulSession||paused||['won','lost'].includes(maulSession.phase))
    return maulFlightNativeUpdate(dt);
  const s=maulSession,elapsed=s.elapsed;
  const seconds=Math.max(0,Math.min(Number(dt)||0,.1))*Math.max(1,Math.min(4,s.speed||1));
  for(const actor of actors.filter(a=>a.userData.actorType==='maul-builder')){
    const id=actor.userData.id,order=s.builderOrders?.[id],cell=order?.path?.at(-1);
    const current=actor.getWorldPosition(new THREE.Vector3());
    let position={x:current.x,z:current.z,arrived:true};
    if(cell&&MAUL_FLIGHT_CORE.allowed(s.map,cell,actor.userData.maul?.sector)){
      position=MAUL_FLIGHT_CORE.travel(current,MAUL_CORE.cellToWorld(s.map,cell),seconds);
      if(position.arrived&&!maulPendingBuilds.has(id))delete s.builderOrders[id];
    }else if(cell&&!maulPendingBuilds.has(id))delete s.builderOrders[id];
    if(Math.hypot(position.x-current.x,position.z-current.z)>.001)
      actor.rotation.y=Math.atan2(position.x-current.x,position.z-current.z);
    const height=MAUL_FLIGHT_CORE.HEIGHT+Math.sin((elapsed+seconds)*3+actor.userData.maul.sector)*.12;
    maulFlightNativePosition(actor,new THREE.Vector3(position.x,height,position.z));
    for(const side of [-1,1]){
      const wing=actor.getObjectByName('MaulBuilderWing'+side);
      if(wing)wing.rotation.z=side*(.18+Math.sin((elapsed+seconds)*12+side)*.18);
    }
  }
  maulFlightSuppressGroundMove=true;
  try{return maulFlightNativeUpdate(dt);}
  finally{maulFlightSuppressGroundMove=false;}
};
const maulFlightNativeStart=maulStartSession;
maulStartSession=function(simulate=false){
  const started=maulFlightNativeStart(simulate);
  if(started&&maulFlightEnabled())for(const actor of actors.filter(a=>a.userData.actorType==='maul-builder')){
    const p=actor.getWorldPosition(new THREE.Vector3());maulFlightNativePosition(actor,new THREE.Vector3(p.x,MAUL_FLIGHT_CORE.HEIGHT,p.z));
  }
  return started;
};
const maulFlightNativeInstall=maulInstallUI;
maulInstallUI=function(...args){
  const value=maulFlightNativeInstall(...args);
  if(maulFlightEnabled()){
    const help=$('maulHelpPanel');
    if(help)for(const p of help.querySelectorAll('p'))
      p.textContent=p.textContent.replace('send your builder to construct it','send your flying builder directly above that cell to construct it');
  }
  return value;
};
window.SWYRL_ENGINE_MAUL.flightStatus=()=>({enabled:!!maulFlightEnabled(),speed:MAUL_FLIGHT_CORE.SPEED,height:MAUL_FLIGHT_CORE.HEIGHT,constructionAt:'builder-hover-cell',sectorBound:true,builders:actors.filter(a=>a.userData.actorType==='maul-builder').map(a=>({sector:a.userData.maul?.sector,id:a.userData.id,position:a.getWorldPosition(new THREE.Vector3()).toArray()}))});
