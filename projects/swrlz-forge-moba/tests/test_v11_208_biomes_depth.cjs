// §E v11.208: full-region Quest Play art atlas, instance batching, fog depth and cleanup.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
let paint=0,strokes=0,labels=[],gradients=0,textureUploads=0;
let createGeom=0,createMat=0,disposeGeom=0,disposeMat=0,createdInstances=0;
class V{
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z})}
 set(x,y,z){Object.assign(this,{x,y,z});return this}
 clone(){return new V(this.x,this.y,this.z)}
}
class Q{setFromAxisAngle(axis,a){this.a=a;return this}}
class M4{copy(m){this.state=m;return this}}
class Obj{
 constructor(){this.position=new V();this.quaternion=new Q();this.scale=new V(1,1,1);this.matrix={};}
 updateMatrix(){this.matrix={pos:this.position.clone(),scale:this.scale.clone()}}
}
class Color{set(hex){this.value=hex;return this}}
class G{constructor(){this.disposed=false;createGeom++}
 dispose(){assert.equal(this.disposed,false);this.disposed=true;disposeGeom++}}
class Mat{constructor(props){Object.assign(this,props);this.disposed=false;createMat++}
 dispose(){assert.equal(this.disposed,false);this.disposed=true;disposeMat++}}
class IM{
 constructor(g,m,n){this.geometry=g;this.material=m;this.count=n;
  this.matrixCalls=[];this.colorCalls=[];this.userData={};this.instanceMatrix={needsUpdate:false};
  this.instanceColor={needsUpdate:false};createdInstances++}
 setMatrixAt(i,m){this.matrixCalls.push(i)}
 setColorAt(i,c){this.colorCalls.push(i)}
 computeBoundingSphere(){this.boundsComputed=true}
}
const painting={
 fillStyle:'',strokeStyle:'',lineWidth:1,
 createRadialGradient(){gradients++;return {addColorStop(){}}},
 save(){},restore(){},beginPath(){},moveTo(){},lineTo(){},
 arc(){},ellipse(){},stroke(){strokes++},fill(){paint++},
 fillRect(){paint++},setLineDash(){},
 fillText(value){labels.push(value)},
};
const s={rules:{bounds:40},simulate:false,role:'sheep',navVersion:77,
 units:[{id:'u',kind:'sheep'}],buildings:[{id:'farm'}],
 fog:{mesh:{position:{y:.175},renderOrder:3},
  material:{depthTest:true,depthWrite:false,polygonOffset:true,
   polygonOffsetFactor:-1,polygonOffsetUnits:-2},
  visible:new Uint8Array([1,0,1,1]),explored:new Uint8Array([1,1,1,0]),
  texture:{minFilter:'linear'}}};
const fogMask=s.fog.visible,explored=s.fog.explored;
const actors=[
 ...[[-20,-20],[-24,-15],[19,-19],[25,-21],[-20,22],[-14,25],[23,21],[16,20],
      [-32,-27],[32,-25],[20,32],[-30,28]].map(([x,z])=>({
       userData:{actorType:'st-tree'},updateWorldMatrix(){},
       getWorldPosition:()=>new V(x,0,z)})),
 ...[[-27,-23],[28,-22],[-24,23],[27,22]].map(([x,z])=>({
       userData:{actorType:'st-rock'},updateWorldMatrix(){},getWorldPosition:()=>new V(x,0,z)})),
 ...[[-14,-29],[19,29]].map(([x,z])=>({
       userData:{actorType:'st-pond'},updateWorldMatrix(){},getWorldPosition:()=>new V(x,0,z)})),
 {userData:{actorType:'st-meadow'}}
];
const scene={children:[],add(m){this.children.push(m)},remove(m){this.children=this.children.filter(x=>x!==m)}};
let previousInit=0,previousSlice=0,previousFinish=0,previousFog=0,previousStop=0;
const se206={canvas:null,ctx:null,stage:0,mesh:null,session:null};
const space={
 console,Math,THREE:{
  Vector3:V,Quaternion:Q,Object3D:Obj,Matrix4:M4,Color,
  InstancedMesh:IM,IcosahedronGeometry:G,DodecahedronGeometry:G,
  ConeGeometry:G,MeshBasicMaterial:Mat,DoubleSide:2
 },window:{},scene,actors,stSession:s,se206,
 renderer:{info:{render:{calls:42}}},
 terrainHeight:()=>0,
 se193XRGameActive:()=>true,
 se206RoadClear:(x,z,b)=>Math.hypot(x,z)>=10.5&&Math.abs(x)>=2.5&&
  Math.abs(z)>=2.5&&Math.abs(x-z)>=2.4&&Math.abs(x+z)>=2.4,
 se206InitDecor:()=>{
  previousInit++;se206.session=s;se206.canvas={width:768,height:768};
  se206.ctx=painting;se206.stage=1;
 },
 se206PaintSlice:()=>{previousSlice++;se206.stage++},
 se206FinishDecor:()=>{previousFinish++;se206.stage=14;se206.mesh={ready:true};
  se206.ctx=null;textureUploads++},
 se206AdjustFog:()=>{previousFog++},
 se206DecorStop:()=>{previousStop++;se206.session=null;se206.mesh=null;se206.ctx=null},
 se193XRFrame:()=>{space.frames++;return 'frame'},frames:0
};
vm.createContext(space);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime',
 'sheep_quest_biome_landmarks_fog_depth_v11_208.js'),'utf8'),space);
const state=()=>space.window.SWYRL_ENGINE_SHEEP_BIOMES_208.diagnose();
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-6,String(a)+' != '+b);
assert.equal(state().active,false);
assert.equal(state().fogPainter,'original native solo/team unchanged');
assert.equal(state().sourceActorsUnchanged,true);
assert.equal(scene.children.length,0);
space.se206InitDecor(s);
assert.equal(previousInit,1);
assert.equal(gradients,4,'one quadrant wash per region');
assert.equal(state().roadHighlights,6,'native 80m meadow crosses and diagonal edges reinforced');
assert.equal(se206.canvas.width,768,'reuse v11.206 768px texture');
const beforePaint=paint;
for(let i=0;i<12;i++)space.se206PaintSlice(s);
assert.equal(previousSlice,12);
assert.equal(state().paintedGroundDetails>400,true,
 'region-different grass/lichen brush strokes drawn in existing staged painter');
assert.ok(paint>beforePaint,'paint passes are real');
assert.equal(state().regionLandmarks,0);
space.se206FinishDecor(s);
assert.equal(previousFinish,1);
assert.equal(textureUploads,1,'only v11.206 uploads completed atlas');
assert.equal(state().regionLandmarks,4);
for(const label of ['PINEWATCH','MOONFLOWER','AMBERGLADE','WILLOWMERE'])
 assert.ok(labels.includes(label),'regional landmark '+label+' drawn');
assert.equal(se206.ctx,null);
// Instance groups are constructed only when decoration is available in Quest.
space.se193XRFrame();
assert.equal(state().active,true);
assert.equal(state().sourceAuthoredProps,18);
assert.equal(s.navVersion,77);
assert.strictEqual(s.fog.visible,fogMask);
assert.strictEqual(s.fog.explored,explored);
assert.equal(s.units.length,1);assert.equal(s.buildings.length,1);
assert.equal(actors.length,19);
assert.ok(scene.children.length>=2&&scene.children.length<=3,
 'two or three reusable instanced world meshes, not many actors');
assert.ok(scene.children.every(g=>g.userData.se208VisualOnly===true));
assert.ok(scene.children.every(g=>g.userData.sheepTagPreview));
assert.ok(scene.children.every(g=>g.frustumCulled&&g.boundsComputed));
assert.ok(scene.children.every(g=>g.instanceMatrix.needsUpdate));
assert.ok(scene.children.every(g=>g.matrixCalls.length===g.count&&
 g.colorCalls.length===g.count));
assert.ok(scene.children.every(g=>g.raycast()===undefined),'world pointer cannot hit decoration');
assert.ok(state().instances>30,'visible natural accents cluster at authored woods');
assert.ok(state().instancedDrawCalls<=3);
assert.equal(state().instanceBuffersUploaded,1);
const old=scene.children.slice();
for(let k=0;k<150;k++)space.se193XRFrame();
assert.equal(space.frames,151);
assert.equal(state().instanceBuffersUploaded,1,'no per-frame mesh or buffer updates');
assert.equal(createdInstances,old.length);
assert.equal(state().sceneDrawCalls,42,'passive GPU draw call sample');
space.se206AdjustFog(s);
assert.equal(previousFog,1);
assert.equal(state().fogDepthGuards,1);
near(s.fog.mesh.position.y,.24);
assert.equal(s.fog.mesh.renderOrder,14);
near(s.fog.material.polygonOffsetFactor,-2.5);
assert.equal(s.fog.material.polygonOffsetUnits,-3);
assert.strictEqual(s.fog.visible,fogMask);
assert.strictEqual(s.fog.explored,explored);
const top=state().fogDepthGuards;
space.se206AdjustFog(s);
assert.equal(state().fogDepthGuards,top,'fog visual setup occurs once per session');
space.se206DecorStop();
assert.equal(previousStop,1);
assert.equal(scene.children.length,0);
assert.equal(disposeGeom,old.length,'all instanced geometries cleaned');
assert.equal(disposeMat,old.length,'all instanced materials cleaned');
assert.equal(state().active,false);
assert.equal(state().decorationsDisposed,old.length);
// Older 128m Wildwood retains original JPG roads (no false painted cross).
const wild={...s,rules:{bounds:64}};
space.se206InitDecor(wild);
assert.equal(state().roadHighlights,6,'never paint 80m roads on custom Wildwood JPG');
assert.equal(gradients,8);
assert.equal(state().sourceActorsUnchanged,true);
const docs=fs.readFileSync(path.join(__dirname,'..','patches',
 'v11_208_quest_biomes_fog_depth.py'),'utf8');
assert.ok(docs.includes('V11_208_QUEST_BIOMES_FOG_DEPTH'));
assert.ok(docs.includes('sheep_quest_biome_landmarks_fog_depth_v11_208.js'));
console.log(JSON.stringify({pass:true,checks:54,drawCalls:state().instancedDrawCalls,
 instances:state().instances,landmarks:state().regionLandmarks,
 atlasUploads:textureUploads,disposedInstances:disposeGeom,
 fogDepthGuards:state().fogDepthGuards}));
