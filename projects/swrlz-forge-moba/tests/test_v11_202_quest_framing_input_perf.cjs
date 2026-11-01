// §E v11.202 source-truth mock: Quest camera, input, resources and fog scope.
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const assert=require('node:assert/strict');
class V{
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z})}
 clone(){return new V(this.x,this.y,this.z)}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
 addScaledVector(v,n){this.x+=v.x*n;this.y+=v.y*n;this.z+=v.z*n;return this}
}
let xr=true,now=1000,originalObstacleCalls=0,hudSnapshots=0;
let foundationCalls=0,oldFrames=0,startCalls=0,cleanupCalls=0,seenCalls=0;
const farm=(id,x,kind='st-farm',visible=true,progress=1)=>({
 id,kind,hp:20,progress,pos:new V(x,0,0),halfX:1.2,halfZ:1.2,
 localHalfX:1.2,localHalfZ:1.2,rotation:0,mesh:{visible},
});
const scene={children:[],add(o){this.children.push(o)},remove(o){this.children=this.children.filter(v=>v!==o)}};
class RingGeometry{
 constructor(innerRadius,outerRadius,segments){this.parameters={innerRadius,outerRadius,segments};this.disposed=false}
 dispose(){this.disposed=true}
}
class Material{
 constructor(options){Object.assign(this,options);this.disposed=false}
 dispose(){this.disposed=true}
}
class Mesh{
 constructor(geometry,material){this.geometry=geometry;this.material=material;this.position=new V();this.rotation={x:0};this.userData={}}
}
class Box3{
 setFromObject(){this.min={x:-.42,z:-.65};this.max={x:.42,z:.70};return this}
}
const actor={getWorldPosition:()=>new V()};
const s={
 navVersion:5,controlledId:'mine',selectedId:'mine',role:'sheep',
 resources:{mine:40},units:[{id:'mine',kind:'sheep',captured:false,isIllusion:false,actor,pos:new V(0,0,-2)}],
 buildings:[
  farm('a',2),farm('hidden',6,'st-income',false),
  farm('raised',8,'st-wall',true,.5)
 ],rules:{},simulate:false
};
const ctx={
 console,Math,
 THREE:{Vector3:V,Mesh,RingGeometry,MeshBasicMaterial:Material,DoubleSide:2,Box3},
 scene,terrainHeight:()=>0,stUnitRadius:()=>.27,
 se193XRGameActive:()=>xr,
 performance:{now:()=>now},
 se200:{horizontal:14,vertical:26,defaultZoom:1.4},
 se193:{angle:Math.PI,zoom:1.5},
 se200CameraAnchor:()=>new V(0,26*ctx.se193.zoom,21*ctx.se193.zoom),
 se200Active:()=>xr,
 stSession:s,
 stUi:{shown:true,build:'st-farm',rotation:0,focus:{x:0,z:0},preview:{}},
 stObstacles:()=>{originalObstacleCalls++;return ['native-obstacles',originalObstacleCalls]},
 stUiView:()=>{hudSnapshots++;return {controlledId:'mine',buildings:[]}},
 stSeenByRole:b=>{seenCalls++;return b.id!=='hidden'},
 stClarityUpdateOverlay:state=>{foundationCalls++;ctx.recentFoundation=state},
 se193XRFrame:()=>{oldFrames++},
 se193XRStart:()=>{startCalls++},
 se193XRCleanup:()=>{cleanupCalls++},
 window:{}
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime',
 'engine_xr_sheep_framing_input_v11_202.js'),'utf8'),ctx);
const diag=()=>ctx.window.SWYRL_ENGINE_SHEEP_VR_FOLLOW_INPUT_202.diagnose();
assert.equal(ctx.se200.horizontal,21);
assert.equal(ctx.se200.vertical,26);
assert.equal(ctx.se200.defaultZoom,1.4);
ctx.se193.zoom=1.4;
let anchor=ctx.se200CameraAnchor();
assert.ok(Math.abs(anchor.x)<.000001,'no added sideways offset');
assert.ok(Math.abs(anchor.z-(21*1.4+2.5))<.000001,'pullback and rearward bias');
assert.equal(anchor.y,36.4,'camera height must stay exactly as v11.200');
assert.equal(ctx.se193.angle,Math.PI,'never pitch or rotate physical headset');
assert.equal(diag().eyePitchIndependent,true);
assert.equal(diag().joystickOnlyVR,true);
// Dense house movement: native collision snapshot reused per step.
const one=ctx.se202ObstacleSnapshot(),two=ctx.se202ObstacleSnapshot();
assert.strictEqual(one,two,'same obstacle snapshot reused between steps');
assert.equal(originalObstacleCalls,1);
s.navVersion++;
assert.notStrictEqual(ctx.se202ObstacleSnapshot(),one,'new house/remove navVersion invalidates');
assert.equal(originalObstacleCalls,2);
s.buildings[2].progress=1;
ctx.se202ObstacleSnapshot();
assert.equal(originalObstacleCalls,3,'new fully-built raised wall invalidates obstacle snapshot');
ctx.se202ObstacleSnapshot();
assert.equal(originalObstacleCalls,3);
assert.equal(diag().obstacleReuse,2);
// Quest preview: full view status never needed for owner or nearby buildings.
assert.equal(ctx.se202PreviewOwner(),'mine');
const available=ctx.se202VisibleBuildings();
assert.deepEqual(Array.from(available,b=>b.id),['a','raised'],
 'hidden house must never appear in preview (fog-of-war)');
assert.equal(hudSnapshots,0,'avoid serializing full fog on XR');
assert.ok(seenCalls>=2);
let point={x:4,z:5};
assert.equal(ctx.se202ShouldRefreshPreview(point),true);
assert.equal(ctx.se202ShouldRefreshPreview({x:4.02,z:5.02}),false,
 'skip unchanged aim and snapped position');
assert.equal(diag().previewSkipped,1);
assert.equal(ctx.se202ShouldRefreshPreview({x:4.09,z:5}),true,'move 9 cm');
now+=600;
assert.equal(ctx.se202ShouldRefreshPreview({x:4.09,z:5}),true,'mobile unit expiry');
s.resources.mine=32;
assert.equal(ctx.se202ShouldRefreshPreview({x:4.09,z:5}),true,'new gold/funding state');
s.navVersion++;
assert.equal(ctx.se202ShouldRefreshPreview({x:4.09,z:5}),true,'new building state');
// VR foundation: low cadence, only when navigation/meaningful move changes.
ctx.se193XRFrame();
assert.equal(oldFrames,1,'original XR frame still runs');
assert.equal(foundationCalls,1,'first world overlay refresh');
const collisionRing=scene.children.find(o=>o.name==='Sheep actual navigation collision radius');
const visualHalo=scene.children.find(o=>o.name==='Sheep model-size cosmetic selector (not collision)');
assert.ok(collisionRing&&visualHalo,'two cheap selector rings rendered in Quest');
assert.equal(collisionRing.geometry.parameters.outerRadius,.27,'precise sheep collider radius');
assert.ok(visualHalo.geometry.parameters.outerRadius>.7,'cosmetic ring fits model silhouette');
assert.ok(visualHalo.material.opacity<collisionRing.material.opacity,
 'collision circle remains visually dominant');
assert.equal(collisionRing.position.x,0);
assert.equal(collisionRing.position.z,-2);
const oldRingCreations=diag().ringCreations;
assert.deepEqual(Array.from(ctx.recentFoundation.buildings,b=>b.id),['a','raised']);
assert.equal(hudSnapshots,0);
ctx.se193XRFrame();
assert.equal(foundationCalls,1,'no second overlay at same frame');
assert.equal(diag().ringCreations,oldRingCreations,'no new ring meshes while stationary');
now+=700;ctx.se193XRFrame();
assert.equal(foundationCalls,1,'stationary scene no rebuild');
s.units[0].pos.x+=2.1;now+=700;ctx.se193XRFrame();
assert.equal(foundationCalls,2,'moving sheep updates nearby lane visibility');
assert.equal(collisionRing.position.x,2.1,'ground selector tracks controlled sheep');
s.navVersion++;now+=700;ctx.se193XRFrame();
assert.equal(foundationCalls,3,'construction forces refresh');
ctx.se193XRStart();
assert.equal(startCalls,1);
assert.equal(scene.children.length,0,'XR reentry cleans selector meshes');
assert.ok(collisionRing.geometry.disposed&&visualHalo.material.disposed,'old GPU buffers freed');
assert.equal(ctx.se202ObstacleSnapshot().length,2,'initial snapshot after reset');
assert.equal(originalObstacleCalls,4);
ctx.se193XRCleanup();
assert.equal(cleanupCalls,1);
xr=false;
assert.equal(ctx.se202PreviewOwner(),'mine');
ctx.se202VisibleBuildings();
assert.equal(hudSnapshots,2,'non-XR still uses native status view');
assert.equal(ctx.se202ShouldRefreshPreview({x:4,z:5}),true);
const before=originalObstacleCalls;
ctx.se202ObstacleSnapshot();
assert.equal(originalObstacleCalls,before+1,'non-XR collision uses native function');
console.log(JSON.stringify({pass:true,checks:39,obstacleCalls:originalObstacleCalls,
 xrStatusBypasses:diag().statusBypasses,skippedPreviews:diag().previewSkipped,
 selectorRadius:.27,haloRadius:diag().visualHaloRadius,
 foundationRefreshes:foundationCalls}));
