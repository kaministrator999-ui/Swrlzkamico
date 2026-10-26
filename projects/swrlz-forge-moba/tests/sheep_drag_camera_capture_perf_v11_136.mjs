import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const source=fs.readFileSync(root+'runtime/sheep_capture_drag_performance_v11_136.js','utf8');
class Vector3 {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
}
let cameraShift=0,navClears=0,draws=0,updateCalls=0,stops=0;
const disposed=[],detached=[],sheep={pos:new Vector3(11,0,15)};
const buildings=Array.from({length:6},(_,i)=>({
 id:'b'+i,owner:i<4?'sheep':'other',hp:100,
 mesh:{id:'mesh'+i,removeFromParent(){detached.push(this.id);}}
}));
const session={controlledId:'sheep',navVersion:1,
 rules:{buildSnap:.15},buildings};
const ctx={console,THREE:{Vector3},Number,Infinity,Math,stSession:session,
 stUi:{build:'st-farm',rotation:0,placement:{x:2.1,z:4.2,rotation:0,ok:true,corners:[[1,3],[2,3],[2,4],[1,4]]}},
 stPlacementGridState:{guide:{root:{visible:true}}},
 terrainHeight(){return 0;},
 st135SheepPosition(){return sheep.pos;},
 stTouchPlacementOriginalGround(x,y){return new Vector3((x+cameraShift)/10,0,(y+cameraShift)/10);},
 stInvalidateNavigation(){navClears++;session.navVersion++;},
 stRemoveBuilding(b){b.hp=0;ctx.st136RetireBuildingVisual(b.mesh);ctx.stInvalidateNavigation();},
 stDisposeVisual(mesh){disposed.push(mesh.id);},
 stUpdate(){updateCalls++;},
 stStop(){stops++;},
 stPlacementGridUpdate(){draws++;ctx.stPlacementGridState.guide.root.visible=true;},
 stUiStatus(){return {active:true};}
};
vm.createContext(ctx);
vm.runInContext(source,ctx,{filename:'v11.136-runtime'});
const v=(expression)=>vm.runInContext(expression,ctx);
const a={x:140,y:220};
const first=ctx.st136StableAimTarget(a,160,250);
assert.ok(Math.abs(first.x-13)<1e-8);
assert.ok(Math.abs(first.z-18)<1e-8);
cameraShift=1000;
const second=ctx.st136StableAimTarget(a,160,250);
assert.ok(Math.abs(second.x-13)<1e-8,'follow-camera movement must not shift a held preview');
assert.ok(Math.abs(second.z-18)<1e-8);
sheep.pos.x=14;
assert.ok(Math.abs(ctx.st136StableAimTarget(a,160,250).x-16)<1e-8,'drag offset stays relative to moving sheep');
assert.equal(ctx.st136StableAimTarget(a,160,250).y,0);
ctx.st136RemoveCapturedBuildings(session,'sheep');
assert.equal(buildings.filter(b=>b.owner==='sheep'&&b.hp>0).length,0,'captured sheep structures are dead synchronously');
assert.equal(navClears,1,'capture destroys all buildings with only one nav invalidation');
assert.equal(detached.length,4,'each owned building disappears immediately');
assert.equal(disposed.length,0,'GPU disposal is deferred');
assert.equal(v('st136RetiredVisuals.length'),4);
ctx.stUpdate(.016,0);
assert.equal(disposed.length,2,'only two GPU visual disposals per update');
ctx.stUpdate(.016,0);
assert.equal(disposed.length,4);
assert.equal(v('st136RetiredVisuals.length'),0);
ctx.st136RemoveCapturedBuildings(session,'other');
assert.equal(navClears,2,'another capture invalidates navigation once');
assert.equal(detached.length,6);
ctx.stStop();
assert.equal(disposed.length,6,'stop always flushes pending GPU cleanup');
assert.equal(stops,1);
ctx.stPlacementGridUpdate();
assert.equal(draws,1);
ctx.stPlacementGridUpdate();
assert.equal(draws,1,'same snapped footprint reuses WebGL geometry');
session.navVersion++;
ctx.stPlacementGridUpdate();
assert.equal(draws,2,'navigation/collision update redraws geometry');
ctx.stUi.placement={...ctx.stUi.placement,x:2.25};
ctx.stPlacementGridUpdate();
assert.equal(draws,3,'new snapped site redraws geometry');
ctx.stUi.placement={...ctx.stUi.placement,ok:false};
ctx.stPlacementGridUpdate();
assert.equal(draws,4,'invalid fit redraws geometry');
const metrics=ctx.stUiStatus().sheepPerf;
assert.equal(metrics.captureBatches,2);
assert.equal(metrics.removals,6);
assert.ok(metrics.navCoalesced>=6);
assert.equal(metrics.visualDisposalPending,0);
assert.ok(metrics.gridSkips>=1);
if(process.env.SE_ASSEMBLED_HTML){
 const html=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 for(const token of [
 'V11_136_SHEEP_DRAG_CAMERA_CAPTURE_CLEANUP',
 'st136StableAimTarget(anchor,x,y)',
 'st136RemoveCapturedBuildings(s,unit.id)',
 'st136RetireBuildingVisual(building.mesh)',
 'st136GridNative=stPlacementGridUpdate'
 ])assert.ok(html.includes(token),'assembled integration missing '+token);
}
console.log('SE136_SAME_CAMERA_DRAG_BATCHED_CAPTURE_GPU_DISPOSAL_GRID_REUSE_PASS');
