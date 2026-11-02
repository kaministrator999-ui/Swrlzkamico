// §E v11.210 — real Quest telemetry and visual-only instanced world additions.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
class Vec{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}
 clone(){return new Vec(this.x,this.y,this.z)}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
}
class Q{setFromAxisAngle(){return this}}
class Obj{
 constructor(){this.position=new Vec();this.quaternion=new Q();this.scale=new Vec(1,1,1);this.matrix={}}
 updateMatrix(){this.matrix={x:this.position.x,z:this.position.z}}
}
let disposedG=0,disposedM=0,created=0;
class Geo{dispose(){disposedG++}}
class Mat{constructor(opts){Object.assign(this,opts)}dispose(){disposedM++}}
class IM{
 constructor(geometry,material,n){created++;this.geometry=geometry;this.material=material;
  this.count=n;this.instanceMatrix={needsUpdate:false};this.userData={};this.visible=true;
  this.positions=[]}
 setMatrixAt(index,m){this.positions.push(index)}
 computeBoundingSphere(){this.sphereMade=true}
}
let now=1000,active=true,blur=false,prevXR=0,oldSolo=0,oldTeam=0,oldStop=0,oldCleanup=0;
const session={rules:{bounds:40},simulate:false,navVersion:33,role:'sheep',units:[],
 buildings:[],fog:{texture:{version:1},visible:new Uint8Array([0,1,0]),
 explored:new Uint8Array([0,1,1])}};
const actors=[{visible:true},{visible:false},{visible:true}];
const scene={children:[],add(o){this.children.push(o)},remove(o){this.children=this.children.filter(x=>x!==o)}};
const xr={
 console,Math,performance:{now:()=>now},
 THREE:{InstancedMesh:IM,CylinderGeometry:Geo,OctahedronGeometry:Geo,
  MeshBasicMaterial:Mat,DoubleSide:2,Object3D:Obj,Vector3:Vec},
 stSession:session,actors,scene,
 renderer:{info:{render:{calls:41,triangles:3800},memory:{textures:11,geometries:49}}},
 se208:{props:[{visible:true},{visible:true}]},se209:{icons:new Map()},
 se206:{mesh:{ready:true}},se193XRGameActive:()=>active,
 se205OverlayActive:()=>blur,se206RoadClear:(x,z,b)=>Math.abs(x)>2.5&&Math.abs(z)>2.5,
 terrainHeight:()=>0,
 se193XRFrame:()=>{prevXR++;return 'frame'},
 stSoftFogPaint:()=>{oldSolo++},
 se156PaintTeamFog:s=>{oldTeam++;s.fog.texture.version++},
 stStop:()=>{oldStop++;xr.stSession=null;return 'stopped'},
 se193XRCleanup:()=>{oldCleanup++;return 'xr clean'},
 window:{}
};
vm.createContext(xr);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime',
 'sheep_xr_world_quality_metrics_v11_210.js'),'utf8'),xr);
const internal=vm.runInContext('se210World',xr);
const widget=xr.window.SWYRL_ENGINE_QUEST_PERFORMANCE_210;
const state=()=>widget.diagnose();
assert.equal(state().xr,true);
assert.equal(state().worldLandmarks3d,0);
assert.equal(scene.children.length,0);
now+=16.7;assert.equal(xr.se193XRFrame(),'frame');
assert.equal(state().worldLandmarks3d>0,true);
assert.equal(scene.children.length,2,'two instanced low-polygon landmark groups');
assert.equal(state().extraDrawCalls,2);
assert.equal(created,2);
assert.ok(scene.children.every(x=>x.userData.se210Cosmetic===true));
assert.ok(scene.children.every(x=>x.userData.sheepTagPreview===true));
assert.ok(scene.children.every(x=>x.instanceMatrix.needsUpdate));
assert.ok(scene.children.every(x=>x.positions.length===x.count));
assert.ok(scene.children.every(x=>x.raycast()===undefined),'never a raycast hit');
assert.equal(session.navVersion,33,'unchanged collision/navigation version');
assert.equal(actors.length,3,'never adds editor actors');
assert.deepEqual(Array.from(session.fog.visible),[0,1,0]);
for(let i=0;i<121;i++){now+=16.67;xr.se193XRFrame();}
assert.equal(state().rendererDrawCalls,41);
assert.equal(state().triangles,3800);
assert.equal(state().gpuTextureCount,11);
assert.equal(state().gpuGeometryCount,49);
assert.equal(state().authoredActorsVisible,2);
assert.ok(state().fps>=58&&state().fps<=61);
assert.ok(state().avgFrameMs>16&&state().avgFrameMs<17);
const init=scene.children.slice();
assert.equal(created,2,'mesh instances not created every XR frame');
assert.equal(widget.setQuality('performance'),true);
assert.ok(init.every(m=>m.visible===false));
assert.ok(xr.se208.props.every(m=>m.visible===false),
 'performance profile changes only cosmetic instances');
assert.equal(widget.setQuality('quality'),true);
assert.ok(init.every(m=>m.visible===true));
assert.equal(widget.setQuality('bogus'),false);
assert.equal(state().cosmeticQuality,'quality');
blur=true;
now+=16.7;xr.se193XRFrame();
assert.equal(state().systemOverlayFrames,1);
assert.equal(scene.children[0].visible,false);
blur=false;now+=16.7;xr.se193XRFrame();
assert.equal(state().systemOverlayFrames,1);
xr.stSoftFogPaint(session);
xr.se156PaintTeamFog(session);
assert.equal(oldSolo,1);assert.equal(oldTeam,1);
assert.equal(state().fogSampleCalls,2);
assert.equal(state().fogTextureUploads,1);
assert.deepEqual(Array.from(session.fog.visible),[0,1,0]);
widget.setQuality('auto');
for(let i=0;i<330;i++){now+=28;xr.se193XRFrame();}
assert.equal(state().cosmeticQuality,'auto');
assert.equal(state().autoReduced,true,'sustained low FPS hides only decor');
assert.ok(init.every(m=>m.visible===false));
assert.deepEqual(Array.from(session.fog.explored),[0,1,1]);
// Let the 90-frame moving average fully flush the prior low-FPS
// samples before counting 9.5 seconds of sustained recovery.
for(let i=0;i<1010;i++){now+=13.8;xr.se193XRFrame();}
assert.equal(state().autoReduced,false,'recover quality after sustained stable FPS');
assert.ok(init.every(m=>m.visible===true));
active=false;now+=17;xr.se193XRFrame();
assert.equal(scene.children.length,0);
assert.equal(disposedG,2);
assert.equal(disposedM,2);
assert.equal(state().noPhysicsOrVisibilityChanges,true);
assert.equal(xr.se193XRCleanup(),'xr clean');
assert.equal(oldCleanup,1);
active=true;now+=17;xr.se193XRFrame();
assert.equal(scene.children.length,2,'new XR session can add optional art');
assert.equal(xr.stStop(),'stopped');
assert.equal(oldStop,1);
assert.equal(scene.children.length,0,'game stop disposes world art');
assert.equal(disposedG,4);assert.equal(disposedM,4);
const patch=fs.readFileSync(path.join(__dirname,'..','patches',
 'v11_210_quest_comprehensive_polish.py'),'utf8');
assert.ok(patch.includes("V11_210_QUEST_COMPREHENSIVE_POLISH"));
assert.ok(patch.includes("se210PanelHit(se192InputRecord('right'))"),
 'world ghost must stop while controller aims at §E independent panel');
assert.ok(patch.includes('const pressed=se210Held(record,side)'),
 'only Sheep Tag quick-wheel source inputs get profile remapping');
console.log(JSON.stringify({pass:true,checks:46,created,disposedG,
 avgFrameMs:state().avgFrameMs,quality:state().cosmeticQuality,
 observedDraws:state().rendererDrawCalls,instances:state().worldLandmarks3d}));
