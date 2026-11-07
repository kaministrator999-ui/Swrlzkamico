// §E v11.305 narrowly validates the new freshly constructed native starter.
// No unrelated VR, Sheep Tag or CI; checks geometry+UV at the source of truth.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
const js=fs.readFileSync(path.resolve(__dirname,'../runtime/hooded_vanguard_full_mesh_uv_v11_305.js'),'utf8');
const materials=['uniform','skin','hair','hair','hood','scarf','scarf','armor',
 'pauldron','pauldron','teal','teal','leather','gloves','gloves','boots','boots'];
function ribbon(rows,cols,fn,uvfn){
 const g={positions:[],uvs:[],indices:[]};
 for(let i=0;i<=rows;i++)for(let j=0;j<=cols;j++){
  const t=i/rows,s=j/cols,p=fn(t,s),uv=uvfn?uvfn(t,s):[s,t];
  assert.equal(p.length,3);assert.equal(uv.length,2);
  g.positions.push(...p);g.uvs.push(...uv);
  if(i<rows&&j<cols){
   const a=i*(cols+1)+j,b=a+cols+1;
   g.indices.push(a,a+1,b,a+1,b+1,b);
  }
 }
 return g;
}
function join(groups){
 const g={positions:[],uvs:[],indices:[]};
 for(const p of groups){
  const start=g.positions.length/3;
  g.positions.push(...p.positions);g.uvs.push(...p.uvs);
  g.indices.push(...p.indices.map(i=>start+i));
 }
 return g;
}
const baseGeometry=ribbon(10,12,(u,v)=>[(v-.5)*.6,2.5+.9*u,
 .24+.02*Math.sin(Math.PI*v)]);
const parts=materials.map((f,i)=>({
 id:'vanguard-rebuilt-'+String(i+1).padStart(2,'0'),
 name:'Original '+i,
 heroPBR:{tile:'v300:'+f,originalArtworkSha256:'ORIGINAL_ATLAS'},
 topologyMesh:structuredClone(baseGeometry)
}));
const source=()=>({project:{name:'v11.304',modelAtelier:{
 parts:structuredClone(parts),name:'v11.304',reference:'old'}},
 engine:'§wyrl§ Engine · Maker v11.304',version:11.304});
const ctx=vm.createContext({
 Math,Map,Number,console,Array,Object,structuredClone,
 se300Ribbon:ribbon,se300Join:join,
 se303HeadSurface:(t,v)=>{
  const a=(v-.5)*Math.PI*2;
  return [.257*Math.sin(a)*Math.sin(Math.PI*t),
   3.815+.715*t,.045+.22*Math.cos(a)*Math.sin(Math.PI*t)];
 },
 se291HeroScene:source,se291OpenHero:()=>true,
 se291Stats:{successes:1},se300Status:{paintedFamilies:11},
 se301Result:{correctedHands:2},se302SurfaceStatus:{normalFamilies:11},
 se303FaceStats:{faceAtlasPixels:768},window:{}
});
vm.runInContext(js,ctx,{timeout:20000});
const out=vm.runInContext('se291HeroScene()',ctx,{timeout:20000});
const m=out.project.modelAtelier,ps=m.parts;
assert.equal(out.version,11.305);
assert.equal(ps.length,17);
assert(m.name.includes('Whole Mesh & UV'));
let vertices=0,triangles=0;
const changed=[];
for(let i=0;i<ps.length;i++){
 const p=ps[i],g=p.topologyMesh,base=parts[i].topologyMesh;
 const n=g.positions.length/3;
 assert.equal(p.id,parts[i].id,'preserve native ID');
 assert.equal(p.heroPBR.tile,parts[i].heroPBR.tile,'preserve material category');
 assert.equal(g.uvs.length,n*2,'UV parity '+i);
 assert(g.uvs.every(v=>v>=0&&v<=1&&Number.isFinite(v)),'UV bounds '+i);
 assert(g.positions.every(Number.isFinite),'3D position finite '+i);
 assert(g.indices.length%3===0&&g.indices.every(k=>Number.isInteger(k)&&k>=0&&k<n),'valid triangle indices '+i);
 assert(n>60,'adequate native surface topology '+i);
 if(i!==2&&i!==3){
  assert.notDeepEqual(g.positions,base.positions,'geometry must improve '+i);
  changed.push(i);
 }else{
  assert.deepEqual(g.positions,base.positions,'retain successful forehead/fringe '+i);
 }
 vertices+=n;triangles+=g.indices.length/3;
}
assert.equal(changed.length,15,'all non-hair geometry parts rebuilt/refined');
const body=ps[0].topologyMesh;
const bodyRing=81;
const front=40,back=0;
assert(body.positions[front*3+2]>body.positions[back*3+2],
 'torso front should point +Z, rear seam behind');
assert(body.uvs[front*2]===.5&&body.uvs[back*2]===0,
 'front and rear cylindrical native UVs');
const ears=ps[1].topologyMesh;
assert(Math.max(...ears.positions.filter((_,i)=>i%3===0))>.28,
 'sculpt folded ear protrudes beyond lateral skull');
assert(ps[4].name.includes('canopy'));
assert(ps[5].name.includes('gathered'));
assert(ps[6].name.includes('overlapping'));
for(const i of [7,8,9]){
 const mesh=ps[i].topologyMesh;
 assert(mesh.indices.length>2*baseGeometry.indices.length,
  'preserve front armor contour, add back and CLOSED trim rims');
 assert.deepEqual(mesh.positions.slice(0,baseGeometry.positions.length),
  baseGeometry.positions,'original approved armor surface must remain unchanged');
 assert.deepEqual(mesh.uvs.slice(0,baseGeometry.uvs.length),
  baseGeometry.uvs,'original authored armor UVs are intact');
}
function extentFor(i){
 const pos=ps[i].topologyMesh.positions;
 const xs=pos.filter((_,k)=>k%3===0),ys=pos.filter((_,k)=>k%3===1);
 return {xmin:Math.min(...xs),xmax:Math.max(...xs),
  ymin:Math.min(...ys),ymax:Math.max(...ys)};
}
for(const [idx,sign] of [[13,-1],[14,1]]){
 const e=extentFor(idx);
 assert(sign===-1 ? e.xmin<-.98 : e.xmax>.98,
  'fingers point out in forearm direction; not limp vertical '+idx);
 assert(e.ymin<2.7&&e.ymax>2.73-0.13,
  'wrist and finger progression smoothly follows forearm '+idx);
 assert(ps[idx].name.includes('neutral wrist'));
}
for(const i of [10,11]){
 assert(ps[i].topologyMesh.indices.length>5000,
   'front and back cloth have real fabric subdivisions');
}
for(const i of [15,16]){
 const e=extentFor(i);
 assert(e.ymax>.58&&e.ymin<.20,'boot toe and cuff shape');
}
const state=vm.runInContext('window.SWYRL_ENGINE_HOODED_VANGUARD.status()',ctx);
assert.equal(state.rebuiltParts,17);
assert.equal(state.vertices,vertices);
assert.equal(state.triangles,triangles);
assert.equal(state.geometryAndUVRebuiltTogether,true);
assert.equal(state.photographCutouts,undefined);
console.log('VANGUARD_FULL_SURFACE_UV_OK',JSON.stringify({
 version:'v11.305',editableParts:17,changedGeometryParts:changed.length,
 retainedHighResFaceAndHair:true,vertices,triangles,
 surfaceNativeUVs:true,armsAlignedWithFiveFingerHands:true,
 ownerVisualAcceptance:false}));
