// Focused CPU-side Quest NPC scheduler test; does not require WebXR hardware.
const assert=require('node:assert/strict'),fs=require('node:fs');
const vm=require('node:vm'),path=require('node:path');
const script=fs.readFileSync(path.join(__dirname,
  '../runtime/sheep_quest_bot_frame_budget_v11_393.js'),'utf8');
class V3{
  constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
  clone(){return new V3(this.x,this.y,this.z);}
  add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this;}
  distanceToSquared(v){return (this.x-v.x)**2+(this.y-v.y)**2+(this.z-v.z)**2;}
}
let xr=true,seen=0,pathCalls=0,checks=0,issued=0,vastPaths=0,gridBuilds=0;
const sheep=n=>({id:'sheep-'+n,kind:'sheep',pos:new V3(n*10,0,0),
  home:new V3(n*10,0,0),botIndex:n,nextBuildAt:0,phase:n,base:null});
const one=sheep(0),two=sheep(1),third=sheep(2);
const state={simulate:false,elapsed:1,navVersion:0,
  units:[one,two,third],buildings:[],resources:{[one.id]:100,[two.id]:100,
    [third.id]:100},rules:{bounds:90,houseLimit:28},
  pen:{x:0,z:0,reserveX:2,reserveZ:2},role:'sheep'};
const ctx={window:{},THREE:{Vector3:V3},stSession:state,
  renderer:{xr:{isPresenting:true}},se193XRGameActive:()=>xr,
  stBotKnownEnemies:()=>[],stUnitRadius:()=>.27,stBlocked:()=>false,
  stPath:(_start,target)=>{pathCalls++;return [target];},
  stCanBuild:(_kind,x,z)=>{checks++;return {ok:checks>=3,x,z};},
  stObstacles:()=>[],stFootprint:(x,z)=>({x,z,halfX:1.2,halfZ:1.2}),
  stBuildNavigation:()=>{gridBuilds++;return {};},stFindPath:()=>[new V3(1,0,1)],
  stVastFindPath:()=>{vastPaths++;return [new V3(1,0,1)];},
  stIssueBuild:()=>{issued++;return {ok:true};},
  stSeenByRole:entity=>{seen++;return !entity.captured;}
};
vm.createContext(ctx);vm.runInContext(script,ctx);
const step=()=>{state.elapsed+=.016;};
assert.equal(ctx.se393Active(),true);
assert.equal(ctx.se393ChooseSheepBase(one),true);
assert.equal(ctx.se393ChooseSheepBase(two),false,'second bot must defer');
let d=ctx.window.SWYRL_ENGINE_SHEEP_AI_FRAME_BUDGET_393.diagnose();
assert.equal(d.planningCandidatesEvaluated,1);
step();
assert.equal(ctx.se393ChooseSheepBase(two),true);
assert.equal(ctx.se393ChooseSheepBase(third),false);
step();
assert.equal(ctx.se393ChooseSheepBase(third),true);
assert.equal(pathCalls,2,'one candidate is correctly rejected inside the central pen');
step();
assert.equal(ctx.se393PlanSheepBuild(one),true,'first site rejected');
assert.equal(issued,0);
assert.equal(ctx.se393PlanSheepBuild(two),true,'same-frame second bot waits');
assert.equal(checks,1);
step();
assert.equal(ctx.se393PlanSheepBuild(one),true,'second site rejected');
assert.equal(checks,2);
step();
assert.equal(ctx.se393PlanSheepBuild(one),true,'third site accepted');
assert.equal(checks,3);assert.equal(issued,1);
assert.equal(gridBuilds,0,'vast-map bot validation must not allocate huge nav grids');
assert.equal(vastPaths,1,'original vast-map reachability route stays active');
assert.equal(one.se393Build,null);
assert.equal(one.aiIntent,'build a compact maze with a viable sheep exit');
d=ctx.window.SWYRL_ENGINE_SHEEP_AI_FRAME_BUDGET_393.diagnose();
assert.equal(d.buildingPlansCompleted,1);
assert.equal(d.aiCandidatesPerGameTick,1);
assert.ok(d.deferredBotPlanning>0);
const ent={kind:'sheep',pos:new V3(5,0,5),captured:false};
assert.equal(ctx.stSeenByRole(ent,'sheep'),true);
assert.equal(ctx.stSeenByRole(ent,'sheep'),true);
assert.equal(seen,1,'same-tick identical visibility should reuse value');
ent.pos.x++;
ctx.stSeenByRole(ent,'sheep');
assert.equal(seen,2,'position changes invalidate cache');
state.navVersion++;
ctx.stSeenByRole(ent,'sheep');
assert.equal(seen,3,'navigation invalidates cache');
step();ctx.stSeenByRole(ent,'sheep');assert.equal(seen,4,'simulation time invalidates cache');
ent.captured=true;
assert.equal(ctx.stSeenByRole(ent,'sheep'),false);
assert.equal(seen,5,'capture status invalidates cache');
xr=false;ctx.stSeenByRole(ent,'sheep');ctx.stSeenByRole(ent,'sheep');
assert.equal(seen,7,'non-VR source logic remains unsuppressed');
ctx.se393CancelSheepPlan(two);
assert.equal(two.se393Build,null);
assert.equal(two.se393Base,null);
console.log('v11.393: one NPC path candidate per frame across flock, deferred build decisions, unchanged 2D, exact-tick visibility cache and invalidation passed');
