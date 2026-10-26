import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const base='projects/swrlz-forge-moba/';
const v124=fs.readFileSync(base+'runtime/sheep_build_passable_grid_v11_124.js','utf8');
const v139=fs.readFileSync(base+'runtime/sheep_rapid_corner_snap_v11_139.js','utf8');
const building=(x,z)=>({kind:'st-farm',hp:100,pos:{x,z},halfX:1.2,halfZ:1.2,rotation:0});
const s={rules:{sheepRadius:.27},buildings:[building(0,0)]};
let calls=0,rapid=false;
const c={console,Math,Number,ST_GRID:.3,
 stSession:s,st132Rapid:false,
 ST_LANE_HOUSES:new Set(['st-farm','st-income','st-fort','st-totem']),
 stLanesSnapHouse:(kind,x,z)=>({x,z}),
 stCanBuild:(kind,x,z,owner,rotation=0)=>{
  calls++;
  const p=c.stLanesSnapHouse(kind,x,z);
  if(s.buildings.some(b=>b.hp>0&&Math.abs(p.x-b.pos.x)<2.4-1e-7&&Math.abs(p.z-b.pos.z)<2.4-1e-7))
   return {kind,x:p.x,z:p.z,ok:false,reason:'A structure already occupies that space.',halfX:1.2,halfZ:1.2,rotation};
  return {kind,x:p.x,z:p.z,ok:true,halfX:1.2,halfZ:1.2,rotation};
 },
 stResult:(ok,reason,fit)=>({...fit,ok,reason}),
 stUnitRadius:()=>s.rules.sheepRadius,
 stClarityGap:()=>null,
 stObstacles:()=>[],stSegmentClear:()=>true
};
vm.createContext(c);vm.runInContext(v124,c);vm.runInContext(v139,c);
const close=(actual,expected,msg)=>assert.ok(Math.abs(actual-expected)<.02,msg+' '+actual+' vs '+expected);
let fit=c.stCanBuild('st-farm',3,3,'owner');
assert.equal(fit.ok,false,'ordinary/rapid-off diagonal crack must remain blocked');
assert.match(fit.reason,/diagonal crack/);
c.st132Rapid=true;calls=0;
fit=c.stCanBuild('st-farm',3,3,'owner');
assert.equal(fit.ok,true,'near-corner Rapid build should snap to a legal flush corner');
assert.equal(fit.st139CornerSnap,true);
close(fit.x,2.4,'x near legal corner');
close(fit.z,2.4,'z near legal corner');
assert.ok(calls>=2&&calls<=4,'native validator must independently approve safe candidate');
const again=c.stCanBuild('st-farm',fit.x,fit.z,'owner');
assert.equal(again.ok,true,'final order should approve same site');
assert.equal(again.x,fit.x);
assert.equal(again.z,fit.z);
// A blocker covering the snapped corner cannot be bypassed.
s.buildings.push(building(2.4,2.4));
fit=c.stCanBuild('st-farm',3,3,'owner');
assert.equal(fit.ok,false,'occupied target must remain invalid');
assert.ok(!fit.st139CornerSnap);
s.buildings=[building(0,0)];
// Tiny slit with a far-away corner shouldn't cause the auto-magnet to teleport.
fit=c.stCanBuild('st-farm',2.65,3.55,'owner');
assert.equal(fit.ok,false);
assert.match(fit.reason,/diagonal crack/);
assert.ok(!fit.st139CornerSnap);
// Valid existing wide diagonal routes are not altered.
fit=c.stCanBuild('st-farm',3.9,3.9,'owner');
assert.equal(fit.ok,true);assert.ok(!fit.st139CornerSnap);
// Other buildings types, especially elevated walls, retain their behavior.
fit=c.stCanBuild('st-wall',3,3,'owner');
assert.equal(fit.ok,true);assert.ok(!fit.st139CornerSnap);
c.st132Rapid=false;
fit=c.stCanBuild('st-farm',3,3,'owner');
assert.equal(fit.ok,false,'Rapid off never changes sheep placement rules');
// Existing units, cost, reachability, wolf collision, and nav still belong to
// the pre-existing native validator and were never bypassed by the wrapper.
assert.ok(v139.includes('st139NativeCanBuild(kind,targetX,targetZ,ownerId,rotation)'));
assert.ok(v139.includes('if(!next?.ok'));
const assembled=process.env.SE_ASSEMBLED_HTML;
if(assembled){
 const html=fs.readFileSync(assembled,'utf8');
 for(const term of ['SWYRL_ENGINE_DEPLOY_MARKER: V11_139_SAFE_RAPID_CORNER_SNAP',
  'function st139RapidCornerProposal(', 'st139NativeCanBuild=stCanBuild',
  'return st139RapidCornerProposal(fit,kind,x,z,ownerId,rotation)'])
  assert.ok(html.includes(term),'integrated release missing '+term);
}
console.log('SE139_SAFE_RAPID_CORNER_MAGNET_NATIVE_CLEARANCE_AND_NO_BYPASS_PASS');
