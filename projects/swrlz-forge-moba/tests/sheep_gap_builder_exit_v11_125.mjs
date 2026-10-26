import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const code=fs.readFileSync(root+'runtime/sheep_gap_builder_exit_v11_125.js','utf8');
const building=(x,z)=>({kind:'st-farm',hp:100,pos:{x,z},halfX:1.2,halfZ:1.2,rotation:0});
const a=building(0,0),b=building(3.6,0),session={rules:{sheepRadius:.27,wolfRadius:.48},buildings:[a,b],obstacles:[]};
const c={
 stSession:session,stSafeLaneWidth:()=>1.2,stUnitRadius:kind=>session.rules[kind+'Radius'],
 stBuildingObstacle:b=>({kind:b.kind,x:b.pos.x,z:b.pos.z,halfX:b.halfX,halfZ:b.halfZ}),
 stClarityGap:(a,b)=>{
  const width=Math.abs(a.pos.x-b.pos.x)-a.halfX-b.halfX;
  return {axis:'x',width,sheep:false,wolf:false,label:'BLOCKED',color:0xf17d74};
 },
 stSegmentClear:(context,p,q,r)=>{
  const n=120;
  for(let i=0;i<=n;i++){
   const t=i/n,x=p.x+(q.x-p.x)*t,z=p.z+(q.z-p.z)*t;
   for(const o of context.obstacles){
    const dx=Math.max(0,Math.abs(x-o.x)-(o.halfX||0));
    const dz=Math.max(0,Math.abs(z-o.z)-(o.halfZ||0));
    if(Math.hypot(dx,dz)<r-.00001)return false;
   }
  }
  return true;
 }
};
vm.createContext(c);vm.runInContext(code,c);
let gap=c.stClarityGap(a,b,[a,b],session.rules);
assert.equal(gap.label,'BOTH CLEAR','1.20m actually clear for these sizes');
assert.equal(gap.localClearance,true);
session.rules.wolfRadius=.65;
gap=c.stClarityGap(a,b,[a,b],session.rules);
assert.equal(gap.label,'SHEEP CLEAR','wolf diameter must be respected');
const narrow=building(3.3,0);
assert.equal(c.stClarityGap(a,narrow,[a,narrow],session.rules).label,'BLOCKED','old unsafe gap remains blocked');
// An obstacle ON the lane keeps the strip blocked rather than being painted clear.
session.obstacles=[{kind:'rock',x:1.8,z:0,halfX:.54,halfZ:1.2}];
assert.equal(c.stClarityGap(a,b,[a,b],session.rules).label,'BLOCKED');
session.obstacles=[{kind:'rock',x:1.8,z:2.5,halfX:.54,halfZ:.35}];
assert.equal(c.stClarityGap(a,b,[a,b],session.rules).sheep,true,
 'an unrelated obstacle beyond measured facing walls should not make the local gap red');
// Verify the native closest-safe-outside-side calculation instead of replacing it.
const lanes=fs.readFileSync(root+'runtime/sheep_lanes.js','utf8');
const body=lanes.slice(lanes.indexOf('function stLanesEjection('),lanes.indexOf('const stLanesCanBuildBase'));
class Vec {
 constructor(x,y,z){this.x=x;this.y=y;this.z=z;}
 distanceToSquared(v){return (this.x-v.x)**2+(this.y-v.y)**2+(this.z-v.z)**2;}
 toArray(){return [this.x,this.y,this.z];}
}
const fp={x:0,z:0,halfX:1.2,halfZ:1.2,localHalfX:1.2,localHalfZ:1.2,rotation:0};
const unit={kind:'sheep',pos:new Vec(0,0,0)};
const e={
 THREE:{Vector3:Vec,MathUtils:{clamp:(n,a,b)=>Math.max(a,Math.min(b,n))}},
 stSession:{rules:{},units:[unit]},
 stUnitRadius:()=>.27,stLocalPoint:(x,z,fp)=>[x-fp.x,z-fp.z],
 stObstacles:()=>[],stBlocked:()=>false,stLanesOccupant:()=>null,
 stLanesSegmentOccupant:()=>null,stSegmentClear:()=>true,
 stIntersectsObstacle:(x,z,r,fp)=>Math.hypot(
  Math.max(0,Math.abs(x-fp.x)-fp.halfX),
  Math.max(0,Math.abs(z-fp.z)-fp.halfZ))<r
};
vm.createContext(e);vm.runInContext(body,e);
let exit=e.stLanesEjection(unit,fp);
assert.ok(exit,'safe closest-side ejection exists');
assert.ok(Math.abs(Math.hypot(exit.x,exit.z)-1.495)<.0001,'exit must clear footprint plus sheep radius');
e.stBlocked=()=>true;
assert.equal(e.stLanesEjection(unit,fp),null,'never teleport into an obstructed site');
if(process.env.SE_ASSEMBLED_HTML){
 const html=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 for(const t of [
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_125_CLEAR_GAPS_AND_SAFE_BUILDER_EXIT',
  'u.id!==owner.id&&!u.captured','stHonestGapLocalClear','SHEEP CLEAR',
  '/* §E v11.125: allow existing validated closest-side stLanesEjection. */'
 ]) assert.ok(html.includes(t),'missing integrated behavior '+t);
 assert.ok(!html.includes('stLanesEjection=()=>null;'),'retired ejection disabling remains');
}
console.log('SE_V11125_LOCAL_GAP_AND_SAFE_BUILDER_EXIT_PASS');
