// Scoped Frostveil construction update. Old saved Maul variants continue to replay
// under their original rules; the current Frostveil starter enables walk-v1.
const MAUL_WALK_BUILD_PROFILE='walk-v1';
MAUL_BATCH_CANONICAL_PROJECT.project.maulConstruction=MAUL_WALK_BUILD_PROFILE;
MAUL_BATCH_CANONICAL_PROJECT.project.maulSpawnProtection='full-pad-v1';
const maulWalkBuildEnabled=()=>currentProject?.kind==='maul'&&currentProject.maulConstruction===MAUL_WALK_BUILD_PROFILE;
const maulPendingBuilds=new Map();
let maulSpawnOverlay=null;
function maulPlanWalkBuild(kind,cx,cz){
  if(!maulSession||paused||['won','lost'].includes(maulSession.phase))return {ok:false,reason:'Resume an active match to build.'};
  if(kind==='maze-wall')return {ok:false,reason:'Build a maze using towers; standalone walls are unavailable.'};
  const fit=MAUL_CORE.canBuild(maulSession,kind,cx,cz);
  if(!fit.ok)return fit;
  const sector=maulSession.selectedSector;
  const builder=actors.find(a=>a.userData.actorType==='maul-builder'&&a.userData.maul?.sector===sector);
  if(!builder)return {ok:false,reason:'No builder is assigned to this defense sector.'};
  const start=maulActorCell(maulSession.map,builder);
  const plan=MAUL_BUILDER_CORE.plan(maulSession.map,maulSession.towers,start,{x:cx,z:cz},sector);
  if(!plan.ok)return plan;
  if([...maulPendingBuilds.values()].some(p=>p.cx===cx&&p.cz===cz&&p.builderId!==builder.userData.id))
    return {ok:false,reason:'Another builder is already assigned to this construction site.'};
  return {ok:true,fit,builder,plan,sector};
}
const maulWalkNativeBuild=maulBuildAt;
maulBuildAt=function(kind,cx,cz){
  if(!maulWalkBuildEnabled())return maulWalkNativeBuild(kind,cx,cz);
  const requested=maulPlanWalkBuild(kind,cx,cz);
  if(!requested.ok){maulUIFeedback(requested.reason,true);stRunGuard(()=>stRunNote('maul-build-rejected',null,{kind,cx,cz,reason:requested.reason}));maulClearPreview();maulRefreshHUD(true);return requested;}
  const {builder,plan,sector}=requested,id=builder.userData.id,site={cx,cz,kind,sector,builderId:id,destination:plan.destination};
  const previous=maulPendingBuilds.get(id);
  maulPendingBuilds.set(id,site);
  maulSession.builderOrders??={};
  maulSession.builderOrders[id]={path:plan.path.slice(1),index:0};
  stRunGuard(()=>stRunNote('maul-build-queued',id,{kind,cx,cz,sector,travelCells:plan.path.length-1,replaced:!!previous}));
  maulUIFeedback('Builder travelling to construct '+MAUL_CORE.definitions[kind].name+'.');
  maulClearPreview();maulRefreshHUD(true);
  // Gold changes only at completion; route and gold are checked again on arrival.
  return {ok:true,code:'queued',reason:'Builder walking to the construction site.',builderId:id,site:{cx,cz},pending:true};
};
const maulWalkNativeUpdate=maulUpdate;
maulUpdate=function(dt){
  maulWalkNativeUpdate(dt);
  if(!maulWalkBuildEnabled()||!maulSession||paused||!maulPendingBuilds.size)return;
  for(const [id,pending]of maulPendingBuilds){
    const builder=actors.find(a=>a.userData.id===id);
    if(!builder||['won','lost'].includes(maulSession.phase)){
      maulPendingBuilds.delete(id);delete maulSession.builderOrders?.[id];continue;
    }
    const p=MAUL_CORE.cellToWorld(maulSession.map,pending.destination),at=builder.getWorldPosition(new THREE.Vector3());
    if(Math.hypot(at.x-p.x,at.z-p.z)>.16){
      if(!maulSession.builderOrders?.[id]){
        maulPendingBuilds.delete(id);stRunGuard(()=>stRunNote('maul-build-cancelled',id,{reason:'Builder route interrupted',...pending}));}
      continue;
    }
    delete maulSession.builderOrders?.[id];maulPendingBuilds.delete(id);
    const baseFit=MAUL_CORE.canBuild(maulSession,pending.kind,pending.cx,pending.cz);
    const still=!baseFit.ok?baseFit:MAUL_BUILDER_CORE.protectedSpawn(maulSession.map,{x:pending.cx,z:pending.cz})?{ok:false,reason:'Enemy entrance pads are no-build zones.'}:{ok:true};
    if(!still.ok){
      maulUIFeedback('Build cancelled: '+still.reason,true);
      stRunGuard(()=>stRunNote('maul-build-cancelled',id,{reason:still.reason,...pending}));
      continue;
    }
    const result=MAUL_CORE.build(maulSession,pending.kind,pending.cx,pending.cz);
    if(result.ok){
      stRunGuard(()=>stRunNote('maul-build-completed',id,{kind:pending.kind,cx:pending.cx,cz:pending.cz,towerId:result.tower.id}));
      maulUIFeedback(MAUL_CORE.definitions[pending.kind].name+' completed.');
    }else{maulUIFeedback('Build cancelled: '+result.reason,true);stRunGuard(()=>stRunNote('maul-build-cancelled',id,{reason:result.reason,...pending}));}
    maulSyncVisuals();maulFlushEvents();maulRefreshHUD(true);
  }
};
const maulWalkNativePreview=maulPreviewAt;
maulPreviewAt=function(x,y,touch=false){
  const result=maulWalkNativePreview(x,y,touch);
  if(!result||!maulWalkBuildEnabled()||!maulUI.buildKind)return result;
  const check=maulPlanWalkBuild(maulUI.buildKind,result.cx,result.cz);
  if(!check.ok){
    maulUI.preview={...maulUI.preview,valid:false,reason:check.reason};
    const ghost=maulObjects.get('preview');
    ghost?.traverse(node=>{if(node.material){
      for(const material of Array.isArray(node.material)?node.material:[node.material])material.color?.set('#fb5c70');
    }});
    const label=typeof maulBatchPlacementLabel==='undefined'?null:maulBatchPlacementLabel;
    if(label&&!label.hidden){label.dataset.valid='false';label.textContent='✕ '+check.reason;}
    maulUIFeedback(check.reason,true);
    return {...maulUI.preview};
  }
  return result;
};
const maulWalkNativeStart=maulStartSession;
maulStartSession=function(simulate=false){
  maulPendingBuilds.clear();
  const started=maulWalkNativeStart(simulate);
  if(started&&maulWalkBuildEnabled()&&maulSession){
    // A single perimeter per spawn region is cheaper than 225 individual overlays.
    const group=new THREE.Group();group.name='Enemy arrival regions — building forbidden';
    for(const area of maulSession.map.spawnAreas||[]){
      if(!area.cells?.length)continue;
      const xs=area.cells.map(c=>c.x),zs=area.cells.map(c=>c.z);
      const lo=MAUL_CORE.cellToWorld(maulSession.map,Math.min(...xs),Math.min(...zs));
      const hi=MAUL_CORE.cellToWorld(maulSession.map,Math.max(...xs),Math.max(...zs));
      const cx=(lo.x+hi.x)/2,cz=(lo.z+hi.z)/2,w=hi.x-lo.x+1.95,h=hi.z-lo.z+1.95;
      const border=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(w,.04,h)),new THREE.LineBasicMaterial({color:'#f08a88',transparent:true,opacity:.9,depthWrite:false}));
      border.position.set(cx,.065,cz);group.add(border);
    }
    maulSpawnOverlay=group;maulRuntime.add(group);
  }
  return started;
};
const maulWalkNativeOrder=maulOrder;
maulOrder=function(command){const result=maulWalkNativeOrder(command);if(maulWalkBuildEnabled()&&result.ok&&command.type==='move-builder'){
  const builder=actors.find(a=>a.userData.actorType==='maul-builder'&&a.userData.maul?.sector===maulSession.selectedSector);
  if(builder&&maulPendingBuilds.delete(builder.userData.id))stRunGuard(()=>stRunNote('maul-build-cancelled',builder.userData.id,{reason:'Builder received a move order'}));
}return result;};
const maulWalkNativeStop=stopSession;
stopSession=function(...args){maulPendingBuilds.clear();if(maulSpawnOverlay){maulSpawnOverlay.removeFromParent();maulSpawnOverlay.traverse(n=>{n.geometry?.dispose?.();n.material?.dispose?.();});maulSpawnOverlay=null;}return maulWalkNativeStop(...args);};
const maulWalkNativeHUD=maulRefreshHUD;
maulRefreshHUD=function(...args){if($('maulBuildWall'))$('maulBuildWall').hidden=maulWalkBuildEnabled();return maulWalkNativeHUD(...args);};
const maulWalkNativeInstall=maulInstallUI;
maulInstallUI=function(...args){
  const result=maulWalkNativeInstall(...args);
  if($('maulBuildWall'))$('maulBuildWall').hidden=maulWalkBuildEnabled();
  const help=$('maulHelpPanel');
  if(help)for(const p of help.querySelectorAll('p')){
    p.textContent=p.textContent.replace('Cheap walls extend the maze. ','Towers themselves shape the maze. ').replace('maze walls','tower-built mazes').replace('tap the ground to move your builder','tap the ground to move your builder, or place a tower to send your builder to construct it');
  }
  return result;
};
window.SWYRL_ENGINE_MAUL.walkBuildStatus=()=>({enabled:maulWalkBuildEnabled(),pending:[...maulPendingBuilds.values()].map(p=>({...p}))});
