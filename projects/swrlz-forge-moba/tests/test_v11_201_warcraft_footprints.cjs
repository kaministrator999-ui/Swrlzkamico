// §E v11.201 headless renderer/test: native collision stays authoritative.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
class Vec3{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}
 clone(){return new Vec3(this.x,this.y,this.z)}
}
class Attribute{
 constructor(a,n){this.array=new Float32Array(a);this.count=a.length/n;this.needsUpdate=false}
}
class Geometry{
 constructor(){this.attribs={};this.disposed=false}
 setAttribute(k,a){this.attribs[k]=a;return this}
 getAttribute(k){return this.attribs[k]}
 computeBoundingSphere(){this.bounded=true}
 setFromPoints(points){return this.setAttribute('position',new Attribute(
  points.flatMap(p=>[p.x,p.y,p.z]),3))}
 dispose(){this.disposed=true;ctx.gpuDisposed++}
}
class Material{
 constructor(opts){Object.assign(this,opts);this.disposed=false}
 dispose(){this.disposed=true;ctx.materialDisposed++}
}
class Group{
 constructor(){this.children=[];this.userData={};this.parent=null}
 add(o){o.parent=this;this.children.push(o)}
 traverse(fn){fn(this);for(const c of this.children)c.traverse(fn)}
}
class Mesh extends Group{
 constructor(geometry,material){super();this.geometry=geometry;this.material=material;this.type='Mesh'}
}
class LineLoop extends Mesh{constructor(g,m){super(g,m);this.type='LineLoop'}}
const scene={children:[],add(o){o.parent=this;this.children.push(o)},
 remove(o){this.children=this.children.filter(v=>v!==o);o.parent=null;}};
const houses=[
 {id:'a',kind:'st-farm',pos:[0,0,0],halfX:1.2,halfZ:1.2,localHalfX:1.2,localHalfZ:1.2,rotation:0,hp:100},
 {id:'b',kind:'st-farm',pos:[3.6,0,0],halfX:1.2,halfZ:1.2,localHalfX:1.2,localHalfZ:1.2,rotation:0,hp:100},
 {id:'c',kind:'st-income',pos:[8.5,0,0],halfX:1.2,halfZ:1.2,localHalfX:1.2,localHalfZ:1.2,rotation:0,hp:100},
 {id:'d',kind:'st-fort',pos:[11.8,0,0],halfX:1.2,halfZ:1.2,localHalfX:1.2,localHalfZ:1.2,rotation:0,hp:100},
 {id:'e',kind:'st-farm',pos:[18,0,0],halfX:1.2,halfZ:1.2,localHalfX:1.2,localHalfZ:1.2,rotation:0,hp:100}
];
const state={role:'sheep',selectedId:'sheep',buildings:houses,units:[{id:'sheep',controlled:true,pos:[0,0,0]}]};
const doc=new Map();
const document={createElement:t=>({nodeName:t,style:{},textContent:'',
  append(v){this.children??=[];this.children.push(v);if(v.id)doc.set(v.id,v)},
  remove(){doc.delete(this.id)}}),
 getElementById:id=>doc.get(id)||null,
 body:{append(n){doc.set(n.id,n)}}};
const stSession={rules:{bounds:40},navVersion:1,pen:{x:0,z:0},buildings:houses};
const stUi={shown:true,build:null,preview:null,placement:null,focus:{x:0,z:0}};
let priorPreview=0,priorClear=0,priorClarityDispose=0;
const ctx={console,Math,document,window:{innerWidth:800,innerHeight:600},
 gpuDisposed:0,materialDisposed:0,
 THREE:{Group,Mesh,LineLoop,BufferGeometry:Geometry,Float32BufferAttribute:Attribute,
  MeshBasicMaterial:Material,LineBasicMaterial:Material,DoubleSide:2,Vector3:Vec3},
 scene,stSession,stUi,stPlacementGridState:{guide:{
  grid:{material:{opacity:.55}},ticks:{material:{opacity:.82}},
  fill:{material:{opacity:.2}},boundary:{material:{opacity:.98}},snap:.15
 }},
 ST_LANE_HOUSES:new Set(['st-farm','st-income','st-fort']),
 stSafeLaneWidth:()=>1.2,stUnitRadius:()=>.27,stSanctuaryRadius:()=>7,
 stHuntReleased:()=>true,terrainHeight:(x,z)=>.03*Math.sin(x*.2)+.02*Math.cos(z*.2),
 stUiView:()=>state,stClarityOverlay:null,stClarityOverlayKey:'',
 stClarityPositionLabel:()=>{},stClarityPositionLegend:()=>{},
 stClarityDisposeOverlay:()=>{
  priorClarityDispose++;
  if(ctx.stClarityOverlay){
   const o=ctx.stClarityOverlay;
   o.traverse(n=>{n.geometry?.dispose();n.material?.dispose()});
   scene.remove(o);
  }
  ctx.stClarityOverlay=null;
  document.getElementById('stClearanceLegend')?.remove();
 },
 stBuildingObstacle:b=>({...b,x:b.pos.x,z:b.pos.z,
  localHalfX:b.localHalfX??b.halfX,localHalfZ:b.localHalfZ??b.halfZ}),
 stClarityGap:(a,b)=>{
  if(!ctx.ST_LANE_HOUSES.has(a.kind)||!ctx.ST_LANE_HOUSES.has(b.kind))return null;
  const gx=Math.abs(a.pos.x-b.pos.x)-a.halfX-b.halfX;
  const gz=Math.abs(a.pos.z-b.pos.z)-a.halfZ-b.halfZ;
  const axis=gx>0&&gz<-.1?'x':gz>0&&gx<-.1?'z':null;
  if(!axis)return null;
  const width=axis==='x'?gx:gz;
  if(width>3.6)return null;
  const x=axis==='x'?(a.pos.x+b.pos.x)/2:(a.pos.x+b.pos.x)/2;
  const z=axis==='z'?(a.pos.z+b.pos.z)/2:(a.pos.z+b.pos.z)/2;
  const sheep=width>=1.2;
  return {x,z,axis,width,length:2.4,sheep,wolf:width>=1.8,
   label:sheep?'SHEEP CLEAR':'BLOCKED'};
 },
 stUiPlacePreview:point=>{priorPreview++;if(!point)return;
  const x=point.x,z=point.z;
  stUi.placement={kind:'st-farm',x,z,rotation:0,halfX:1.2,halfZ:1.2,
   localHalfX:1.2,localHalfZ:1.2,
   corners:[[x-1.2,z-1.2],[x+1.2,z-1.2],[x+1.2,z+1.2],[x-1.2,z+1.2]],
   ok:true};
 },
 stUiClearPreview:()=>{priorClear++;stUi.preview=null;stUi.build=null;},
 };
vm.createContext(ctx);
const filename=path.join(__dirname,'..','runtime','sheep_warcraft_foundation_passages_v11_201.js');
vm.runInContext(fs.readFileSync(filename,'utf8'),ctx);
let stats=()=>ctx.window.SWYRL_ENGINE_SHEEP_WARCRAFT_FOOTPRINTS_201.diagnose();
ctx.stClarityUpdateOverlay(state);
assert.equal(stats().active,true,'permanent ground guide created');
assert.equal(stats().shownPermanentGaps,3,'only adjacent short wall gaps rendered');
assert.equal(scene.children.length,1,'one batched foundation group');
const permanent=scene.children[0];
const meshes=permanent.userData.meshes;
assert.ok(meshes.edge.geometry.getAttribute('position').count>300,'solid boundary strips');
assert.ok(meshes.buffer.geometry.getAttribute('position').count>300,'sheep stopping zone');
assert.ok(meshes.foundation.geometry.getAttribute('position').count>60,'soft foundations');
assert.ok(meshes.tight.visible,'just-safe sheep lane marked amber');
assert.ok(meshes.clear.visible,'wide sheep lane marked teal');
assert.ok(meshes.blocked.visible,'unsafe sheep lane marked red');
assert.ok(document.getElementById('stClearanceLegend').textContent.includes('Sheep stopping distance'));
const buildsBefore=stats().permanentRebuilds;
ctx.stClarityUpdateOverlay(state);ctx.stClarityUpdateOverlay(state);
assert.equal(stats().permanentRebuilds,buildsBefore,'no rebuild on steady frames');
assert.equal(permanent.parent,scene,'same resource reused in steady state');
stSession.navVersion++;
ctx.stClarityUpdateOverlay(state);
assert.equal(stats().permanentRebuilds,buildsBefore+1,'navigation change rebuilds base');
assert.equal(permanent.parent,null,'old guide detached and freed');
assert.ok(ctx.gpuDisposed>0&&ctx.materialDisposed>0,'GPU resources disposed');
stUi.build='st-farm';stUi.preview={};stUi.placement={};
ctx.stUiPlacePreview({x:3.6,z:3.6});
assert.equal(priorPreview,1);
assert.ok(stats().previewActive);
assert.ok(stats().previewGaps.length>=1,'nearby lane shown in preview');
const preview=scene.children.at(-1),previewBuilds=stats().previewRebuilds;
const disposedBefore=stats().disposed;
for(let i=0;i<40;i++)ctx.stUiPlacePreview({x:3.6,z:3.6});
assert.equal(stats().previewRebuilds,previewBuilds,'same snapped preview cached');
ctx.stUiPlacePreview({x:3.75,z:3.6});
assert.equal(stats().previewRebuilds,previewBuilds+1,'new preview site recalculated');
assert.equal(scene.children.at(-1),preview,'GPU objects reused across ghost motion');
assert.equal(stats().disposed,disposedBefore,'no geometry root churn during drag');
assert.equal(ctx.stPlacementGridState.guide.grid.material.opacity,.16,'fine grid muted');
assert.equal(ctx.stPlacementGridState.guide.boundary.material.opacity,.88,'exact boundary retained');
ctx.stUiClearPreview();
assert.equal(priorClear,1,'native cleanup still invoked');
assert.equal(stats().previewActive,false,'preview disposed on cancel');
assert.equal(preview.parent,null,'preview detached');
ctx.stClarityDisposeOverlay();
assert.equal(scene.children.length,0,'no orphan scene guides after leaving play');
assert.equal(document.getElementById('stClearanceLegend'),null,'legend cleaned up');
assert.ok(priorClarityDispose>=2);
console.log(JSON.stringify({pass:true,checks:24,baseRebuilds:stats().permanentRebuilds,
 previewRebuilds:stats().previewRebuilds,gpuDisposals:ctx.gpuDisposed,
 materialDisposals:ctx.materialDisposed,priorPreview}));
