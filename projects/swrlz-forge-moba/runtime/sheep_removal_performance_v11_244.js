// §E v11.244 — smooth Sheep Tag capture/destruction spikes.
// All game rules, scene-save semantics, and LAN authority are unchanged.
const se244DeferredVisuals=[];
let se244DisposalScheduled=false, se244BatchNavigation=0, se244NavigationPending=false;
const se244ImmediateDispose=stDisposeVisual;
let se244Hidden=0,se244Disposed=0,se244Captured=0,se244NavBatches=0;
function se244DrainOne(){
  const mesh=se244DeferredVisuals.shift();
  if(mesh){
    se244ImmediateDispose(mesh);
    se244Disposed++;
  }
  if(se244DeferredVisuals.length)se244ScheduleDisposal();
}
function se244ScheduleDisposal(){
  if(se244DisposalScheduled||!se244DeferredVisuals.length)return;
  se244DisposalScheduled=true;
  const work=()=>{se244DisposalScheduled=false;se244DrainOne();};
  if(typeof requestIdleCallback==='function')requestIdleCallback(work,{timeout:220});
  else setTimeout(work,34);
}
const se244PriorRemoveBuilding=stRemoveBuilding;
stRemoveBuilding=function(building){
  if(!building||building.hp<=0)return;
  // Author-edited buildings survive Stop; only session-owned meshes are
  // eligible for deferred disposal.
  if(building.authored||!building.mesh)return se244PriorRemoveBuilding(building);
  const removed=building.mesh,previous=stDisposeVisual;
  stDisposeVisual=function(object){
    if(object!==removed)return previous(object);
    object.visible=false;
    object.removeFromParent();
    se244DeferredVisuals.push(object);
    se244Hidden++;
    se244ScheduleDisposal();
  };
  try{return se244PriorRemoveBuilding(building);}
  finally{stDisposeVisual=previous;}
};
const se244PriorNavInvalidation=stInvalidateNavigation;
function se244DoNavInvalidation(){
  se244PriorNavInvalidation();
  const s=stSession;
  if(!s)return;
  // Spread existing bot path recomputes across a few updates, while the
  // controlled sheep responds immediately and old paths still use collision.
  for(const u of s.units){
    if(u.id===s.controlledId||!u.path?.length)continue;
    const stagger=((u.botIndex||0)%6)*.065+.045;
    u.repathAt=Math.max(u.repathAt,s.elapsed+stagger);
  }
}
stInvalidateNavigation=function(){
  if(se244BatchNavigation){se244NavigationPending=true;return;}
  se244DoNavInvalidation();
};
const se244PriorCapture=stCapture;
stCapture=function(...args){
  se244BatchNavigation++;
  try{return se244PriorCapture(...args);}
  finally{
    se244BatchNavigation--;
    if(!se244BatchNavigation&&se244NavigationPending){
      se244NavigationPending=false;
      se244DoNavInvalidation();
      se244NavBatches++;
    }
    se244Captured++;
  }
};
// The movement implementation has several historical overlays. Keep its
// authoritative pathing code unchanged; defer only a dirty bot route that
// already has a safe route and has not reached its short stagger deadline.
const se244PriorMoveUnit=stMoveUnit;
stMoveUnit=function(unit,target,dt){
  const s=stSession;
  const deferred=!!s&&!!target&&unit.id!==s.controlledId&&
    unit.pathVersion!==s.navVersion&&unit.path?.length>0&&
    !!unit.pathTarget&&unit.pathTarget.distanceToSquared(target)<=1&&
    s.elapsed<unit.repathAt;
  if(!deferred)return se244PriorMoveUnit(unit,target,dt);
  const oldVersion=unit.pathVersion;
  unit.pathVersion=s.navVersion;
  try{return se244PriorMoveUnit(unit,target,dt);}
  finally{
    if(unit.pathVersion===s.navVersion)unit.pathVersion=oldVersion;
  }
};
window.SWYRL_ENGINE_SHEEP_REMOVAL_PERFORMANCE_244=Object.freeze({
  status:()=>({hidden:se244Hidden,disposed:se244Disposed,
    queued:se244DeferredVisuals.length,captureCalls:se244Captured,
    navigationBatches:se244NavBatches})
});