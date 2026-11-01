// §E v11.203 — Quest forward sheep building and low-lag wrist menu.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
class Vec3{
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z})}
 clone(){return new Vec3(this.x,this.y,this.z)}
 addScaledVector(v,t){this.x+=v.x*t;this.y+=v.y*t;this.z+=v.z*t;return this}
 dot(v){return this.x*v.x+this.y*v.y+this.z*v.z}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this}
 length(){return Math.hypot(this.x,this.y,this.z)}
 normalize(){const d=this.length()||1;this.x/=d;this.y/=d;this.z/=d;return this}
 copy(v){Object.assign(this,{x:v.x,y:v.y,z:v.z});return this}
}
class CylinderGeometry{
 constructor(){this.disposed=false}
 dispose(){this.disposed=true}
}
class BasicMaterial{
 constructor(opts){Object.assign(this,opts);this.color={setHex:v=>{this.colorHex=v}};this.disposed=false}
 dispose(){this.disposed=true}
}
class BuildMesh{
 constructor(geometry,material){this.geometry=geometry;this.material=material;
  this.position=new Vec3();this.quaternion={setFromUnitVectors(){return this}};
  this.scale={y:1};this.userData={};this.visible=false}
}
class MeshTree{
 constructor(name){this.name=name;this.children=[{
  geometry:{disposed:false,dispose(){this.disposed=true;}},
  material:{disposed:false,dispose(){this.disposed=true;}}
 }];this.position=new Vec3();this.quaternion={clone:()=>({}),copy(){return this}};this.visible=false;this.disposed=false;}
 traverse(fn){fn(this);for(const o of this.children)fn(o)}
}
const rightRecord={cast:{origin:new Vec3(0,8.7,-31.9),
 direction:new Vec3(0,0,1)},se192:{
 beam:{visible:true},
 dot:{position:new Vec3(),quaternion:{setFromUnitVectors(){return this}},
 visible:false}}};
let originalRayRenders=0;
const scene={children:[],add(o){this.children.push(o)},remove(o){this.children=this.children.filter(v=>v!==o)}};
const ctx={
 console,Math,scene,performance:{now:()=>now},
 THREE:{Vector3:Vec3,CylinderGeometry,MeshBasicMaterial:BasicMaterial,Mesh:BuildMesh,MathUtils:{clamp:(n,a,b)=>Math.max(a,Math.min(b,n))},
  CanvasTexture:class{constructor(c){this.canvas=c;this.disposed=false}dispose(){this.disposed=true;}},
  SRGBColorSpace:'srgb'},
 window:{},
 stSession:{controlledId:'u1',units:[{id:'u1',pos:new Vec3(0,0,0)}]},
 stUi:{build:'st-farm'},
 se193:{angle:0,zoom:1.4},
 se200:{horizontal:21,vertical:26},
 se202:{vertical:26,rearBias:2.5},
 se200Active:()=>true,
 se195:{visible:false,photo:false,mode:'game',page:'main',radial:null,buttons:[],
  textures:[],hover:null,fps:70},
 se181XR:{controllers:[]},
 terrainHeight:(x,z)=>.01*x,
 se191XRHeadPose:()=>({eye:new Vec3(0,9.1,-31.9)}),
 se192Ray:record=>record?.cast,
 se192InputRecord:hand=>hand==='right'?rightRecord:null,
 se192RenderRay:()=>{originalRayRenders++},
 se203Dummy:0,
 se193XRGameGround:()=>{physicalCalls++;return new Vec3(99,0,99)},
 se195Text:()=>{throw Error('should replace old textures')},
 se195MakeRadial:null,se195SetVisible:null,se195PositionRadial:()=>{positioned++},
 se195UpdateHand:()=>{handUpdates++},
 se195AcquireHand:()=>{handAcquisitions++},
 se193XRCleanup:null,
 document:{createElement(kind){
  assert.equal(kind,'canvas');canvases++;
  return {width:0,height:0,getContext:()=>({
   scale(x,y){scales.push([x,y])},clearRect(){},
   createLinearGradient:()=>({addColorStop(){}}),
   beginPath(){},roundRect(){},fill(){},stroke(){},fillText(){}
  })};
 }}
};
let now=1200,physicalCalls=0,canvases=0,scales=[],positioned=0;
let oldMenuBuilds=0,oldMenuDisposals=0,handUpdates=0,handAcquisitions=0;
ctx.se195MakeRadial=function(){
 const root=new MeshTree(ctx.se195.mode+'|'+ctx.se195.page);
 ctx.se195.radial=root;ctx.se195.buttons=[{name:'a'}];
 ctx.se195Text(ctx.se195.page.toUpperCase(),true);
 ctx.se195Text('CAPTURE',false);
 root.visible=ctx.se195.visible;scene.add(root);oldMenuBuilds++;
};
ctx.se195SetVisible=function(value){
 ctx.se195.visible=!!value;
 if(ctx.se195.radial)ctx.se195.radial.visible=ctx.se195.visible;
};
ctx.se193XRCleanup=function(){
 if(ctx.se195.radial){
  const root=ctx.se195.radial;scene.remove(root);
  root.traverse(o=>{o.geometry?.dispose?.();o.material?.dispose?.()});
  ctx.se195.radial=null;oldMenuDisposals++;
 }
};
vm.createContext(ctx);
const source=fs.readFileSync(path.join(__dirname,'..','runtime',
 'engine_xr_wrist_forward_placement_v11_203.js'),'utf8');
vm.runInContext(source,ctx);
const internal=vm.runInContext('se203',ctx);
const state=()=>ctx.window.SWYRL_ENGINE_QUEST_SHEEP_AIM_203.diagnose();
assert.equal(ctx.se200.vertical,6.5,'lower the game camera, do not lift it');
assert.equal(ctx.se202.vertical,6.5,'consistent diagnostic camera-height configuration');
assert.equal(state().cameraAbove,9.1);
assert.equal(state().cameraBehind,31.9);
assert.equal(state().neutralDownAngleDeg,16,'near-neutral gaze rather than 49 degrees');
// Neutral controller aims near the sheep, even though physical ray is
// horizontal and cannot intersect the world-space ground y=0.
const ahead=ctx.se193XRGameGround({cast:{
 origin:new Vec3(0,8.7,-31.9),direction:new Vec3(0,0,1)
}});
assert.ok(ahead&&ahead.z>2&&ahead.z<6,'forward ray maps near sheep');
assert.equal(physicalCalls,0,'avoid relying on downward physical ground hit');
const left=ctx.se193XRGameGround({cast:{
 origin:new Vec3(0,8.7,-31.9),direction:new Vec3(-.15,0,.988)
}});
const right=ctx.se193XRGameGround({cast:{
 origin:new Vec3(0,8.7,-31.9),direction:new Vec3(.15,0,.988)
}});
assert.ok(left.x<-.5&&right.x>.5,'aiming sideways places houses on both sides');
const high=ctx.se193XRGameGround({cast:{
 origin:new Vec3(0,8.7,-31.9),direction:new Vec3(0,.1,.995)
}});
const low=ctx.se193XRGameGround({cast:{
 origin:new Vec3(0,8.7,-31.9),direction:new Vec3(0,-.1,.995)
}});
assert.ok(high.z>ahead.z&&low.z<ahead.z,'aim up farther, down nearer');
const steep=ctx.se193XRGameGround({cast:{
 origin:new Vec3(0,8.7,-31.9),direction:new Vec3(0,-.83,.55)
}});
assert.equal(steep.x,99,'steep down pointing retains physical ground targeting');
assert.equal(physicalCalls,1);
ctx.stUi.build=null;
assert.equal(ctx.se193XRGameGround({cast:null}).x,99,'normal selection rays unchanged');
ctx.stUi.build='st-farm';
ctx.se195.visible=true;
assert.equal(ctx.se193XRGameGround({cast:null}).x,99,'wrist menu never hijacks controller aiming');
ctx.se195.visible=false;
assert.equal(state().forwardAimSamples,5);
assert.equal(state().physicalAimSamples,1);
// Forward-target visual MUST end at the mapped real build ground point.
ctx.se192RenderRay(rightRecord,{});
const guide=scene.children.find(o=>o.name==='Quest Sheep Tag controller to virtual building target');
assert.ok(guide?.visible,'reusable link between hand and mapped site');
assert.equal(rightRecord.se192.beam.visible,false,'original forward beam hidden while building');
const chosen=ctx.se203GroundFromForwardRay(rightRecord);
assert.equal(rightRecord.se192.dot.position.x,chosen.x);
assert.equal(rightRecord.se192.dot.position.z,chosen.z,
 'reticle agrees with building placement rather than floating in the air');
const guideCreated=guide;
ctx.se192RenderRay(rightRecord,{});
assert.equal(scene.children.find(o=>o.name==='Quest Sheep Tag controller to virtual building target'),
 guideCreated,'single GPU guide reused every frame');
ctx.se195.visible=true;
ctx.se192RenderRay(rightRecord,{});
assert.equal(guide.visible,false,'menu blocks build guide');
assert.equal(rightRecord.se192.beam.visible,true,'native beam restored for menu selection');
ctx.se195.visible=false;
ctx.se192RenderRay(rightRecord,{});
assert.equal(guide.visible,true,'build guide restored after closing menu');
// Page geometry and small canvas textures must be cached/reused.
ctx.se195MakeRadial(true);
const rootMain=ctx.se195.radial;
assert.equal(oldMenuBuilds,1);assert.equal(canvases,2);
assert.equal(ctx.se195.menuTextures?.length||0,0,'no per-page texture disposal list');
assert.deepEqual(scales.map(x=>x.join('/')),['0.5/0.5','0.5/0.5']);
assert.equal(rootMain.visible,false);
ctx.se195.page='capture';ctx.se195MakeRadial(false);
const rootCapture=ctx.se195.radial;
assert.notEqual(rootMain,rootCapture);assert.equal(oldMenuBuilds,2);
assert.equal(canvases,3,'only new CAPTURE header texture created');
ctx.se195.page='main';ctx.se195MakeRadial(false);
assert.strictEqual(ctx.se195.radial,rootMain,'back to cached main mesh without rebuilding');
assert.equal(oldMenuBuilds,2,'menu reused');
assert.equal(canvases,3);
ctx.se195.page='capture';ctx.se195MakeRadial(false);
assert.strictEqual(ctx.se195.radial,rootCapture,'camera page cached too');
assert.equal(oldMenuBuilds,2);
// No animated hand sparks behind the menu: selection beam still exists.
const hand={halo:{visible:true},points:{visible:true}};
ctx.se181XR.controllers=[{se195:hand}];
ctx.se195SetVisible(true);
assert.equal(hand.halo.visible,false);
assert.equal(hand.points.visible,false);
ctx.se195UpdateHand();
assert.equal(handUpdates,0);
ctx.se195SetVisible(false);
assert.equal(hand.halo.visible,true);
assert.equal(hand.points.visible,true);
ctx.se195UpdateHand();
assert.equal(handUpdates,1);
const cachedTextures=[...internal.menuTextures.values()];
assert.equal(cachedTextures.length,3);
ctx.se193XRCleanup();
assert.equal(scene.children.length,0,'both detached and active menu roots and guide released');
assert.ok(guide.geometry.disposed,'long beam GPU geometry freed on exit');
assert.ok(rootMain.children[0].geometry.disposed);
assert.ok(rootCapture.children[0].material.disposed);
assert.ok(cachedTextures.every(t=>t.disposed),'all cached textures disposed once on XR exit');
assert.equal(internal.menuPages.size,0);
assert.equal(internal.menuTextures.size,0);
assert.equal(oldMenuDisposals,1,'original active menu lifecycle still owns current page');
assert.ok(state().menuPageReuses>=2);
assert.ok(state().handSparksSkipped>=1);
const original=fs.readFileSync(path.join(__dirname,'..','patches',
 'v11_203_quest_wrist_forward_aim.py'),'utf8');
assert.ok(original.includes('if(stUi.build&&!se195.visible&&!se195.photo&&now-se193.previewAt>100)'),
 'modal menu suppresses heavy house preview validation');
assert.ok(original.includes('se195.visible||se195.photo'),
 'modal menu also suspends cosmetic foundation rebuilding');
console.log(JSON.stringify({pass:true,checks:43,forwardSamples:state().forwardAimSamples,
 cameraAbove:state().cameraAbove,menuBuilds:oldMenuBuilds,
 menuReuses:state().menuPageReuses,canvasTextures:canvases,
 resourcesDisposed:state().menuResourcesDisposed}));
