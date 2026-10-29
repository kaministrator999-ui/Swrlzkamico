import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const src=fs.readFileSync('projects/swrlz-forge-moba/runtime/sheep_build_passable_grid_v11_124.js','utf8');
const building=(x,z)=>({kind:'st-farm',hp:100,pos:{x,z},halfX:1.2,halfZ:1.2,rotation:0});
const state={rules:{sheepRadius:.27},buildings:[building(0,0)]};
const ctx={
 stSession:state,ST_GRID:.3,ST_LANE_HOUSES:new Set(['st-farm','st-income','st-fort','st-totem']),
 stLanesSnapHouse:(kind,x,z)=>({x,z}),
 stCanBuild:(kind,x,z)=>{
  const p=ctx.stLanesSnapHouse(kind,x,z);
  return {kind,x:p.x,z:p.z,halfX:1.2,halfZ:1.2,rotation:0,ok:true};
 },
 stResult:(ok,reason,fit)=>({...fit,ok,reason}),
 stClarityGap:()=>({width:.9,sheep:true,wolf:false,label:'SHEEP ONLY',color:0x48e6ed}),
 stUnitRadius:()=>state.rules.sheepRadius,
 stObstacles:()=>[
  ...state.buildings.map(b=>({kind:b.kind,x:b.pos.x,z:b.pos.z,
   halfX:b.halfX,halfZ:b.halfZ,rotation:0})),
  ...(state.extraObstacles||[])
 ],
 stSegmentClear:(context,a,b,radius)=>{
  const n=Math.max(1,Math.ceil(Math.hypot(b.x-a.x,b.z-a.z)/.015));
  for(let i=0;i<=n;i++){
   const t=i/n,x=a.x+(b.x-a.x)*t,z=a.z+(b.z-a.z)*t;
   for(const o of context.obstacles){
    const xx=Math.max(0,Math.abs(x-o.x)-(o.halfX||0));
    const zz=Math.max(0,Math.abs(z-o.z)-(o.halfZ||0));
    const d=o.radius!==undefined?
      Math.hypot(x-o.x,z-o.z)-o.radius:Math.hypot(xx,zz);
    if(d<radius-.00001)return false;
   }
  }
  return true;
 }
};
vm.createContext(ctx);vm.runInContext(src,ctx);
const close=(a,b,t=.0003)=>assert.ok(Math.abs(a-b)<t,String(a)+' vs '+String(b));
assert.equal(ctx.stSafeLaneWidth(),1.2,'one more nav-cell gap must be 1.2m');
close(ctx.stLanesSnapHouse('st-farm',3.25,0).x,3.6);
close(ctx.stLanesSnapHouse('st-farm',2.42,0).x,2.402);
close(ctx.stLanesSnapHouse('st-farm',9.11,0).x,9.0);
let fit=ctx.stCanBuild('st-farm',3.25,0);
assert.equal(fit.ok,true,fit.reason);
close(fit.x,3.6);
fit=ctx.stCanBuild('st-farm',2.42,0);
assert.equal(fit.ok,true,'true flush contact should be legal');
const originalSnap=ctx.stLanesSnapHouse;
ctx.stLanesSnapHouse=(kind,x,z)=>({x,z});
assert.equal(ctx.stCanBuild('st-farm',3.3,0).ok,false,'raw 0.9m slit accepted');
assert.equal(ctx.stCanBuild('st-farm',3.45,0).ok,false,'raw 1.05m slit accepted');
assert.equal(ctx.stCanBuild('st-farm',3.6,0).ok,true,'real 1.2m lane denied');
assert.equal(ctx.stCanBuild('st-farm',2.402,0).ok,true,'flush epsilon denied');
state.extraObstacles=[{kind:'rock',x:1.8,z:1.55,radius:.35}];
fit=ctx.stCanBuild('st-farm',3.6,0);
assert.equal(fit.ok,false,'blocked passage entrance was accepted');
assert.ok(/block/.test(fit.reason));
state.extraObstacles=[];
ctx.stLanesSnapHouse=originalSnap;
state.buildings=[building(0,0)];
close(ctx.stLanesSnapHouse('st-farm',0,3.26).z,3.6);
state.buildings=[building(0,0),building(6.3,0)];
fit=ctx.stCanBuild('st-farm',3.15,0);
assert.equal(fit.ok,false,'two-neighbor intermediate gap should fail');
assert.equal(ctx.stClarityGap().label,'BLOCKED','0.9m old houses must not be falsely labeled passable');
assert.equal(ctx.stClarityGap().sheep,false);
state.rules.sheepRadius=.55;
assert.equal(ctx.stSafeLaneWidth(),1.8,'bigger sheep must require bigger gap');
state.rules.sheepRadius=.27;
for(const s of ['stSegmentClear(context,p,q,radius)','gap.sheep=false','Math.hypot(a,b)<lane-.015'])
 assert.ok(src.includes(s),'real placement behavior missing '+s);
if(process.env.SE_ASSEMBLED_HTML){
 const html=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 for(const s of ['V11_124_FLUSH_OR_PASSABLE_SHEEP_BUILD_PLACEMENT',
 'Safe snapped sheep lanes', 'stBuildGridPreviousCanBuild',
 'stBuildGridPreviousClarityGap'])
  assert.ok(html.includes(s),'missing release source '+s);
}
console.log('SE_V11124_FLUSH_OR_PASSABLE_HOUSE_GRID_AND_TRUTHFUL_SHEEP_LABEL_PASS');
