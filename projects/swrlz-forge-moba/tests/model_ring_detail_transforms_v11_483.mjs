import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../runtime/model_ring_detail_kernel_v11_483.js',import.meta.url),'utf8');
const studio=fs.readFileSync(new URL('../runtime/model_ring_detail_studio_v11_483.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../runtime/model_ring_detail_studio_v11_483.css',import.meta.url),'utf8');
const patch=fs.readFileSync(new URL('../patches/v11_483_ring_detail_transforms.py',import.meta.url),'utf8');
new vm.Script(source);new vm.Script(studio);

function audit(d){
 const pos=d?.positions,uv=d?.uvs,idx=d?.indices,edges=new Map(),sets=new Set();
 if(!Array.isArray(pos)||!Array.isArray(uv)||!Array.isArray(idx)||pos.length%3||
  pos.length/3>9000||uv.length!==pos.length/3*2||idx.length%3||idx.length/3>16000)
  return {ok:false,reason:'bad dimensions'};
 if(!pos.every(Number.isFinite)||!uv.every(Number.isFinite))return {ok:false,reason:'nonfinite'};
 const p=i=>pos.slice(i*3,i*3+3);
 for(let i=0;i<idx.length;i+=3){
  const tri=idx.slice(i,i+3);
  if(tri.some(v=>!Number.isInteger(v)||v<0||v>=pos.length/3)||
     new Set(tri).size!==3)return {ok:false,reason:'invalid triangle'};
  const sig=[...tri].sort((a,b)=>a-b).join(':');
  if(sets.has(sig))return {ok:false,reason:'duplicate face'};
  sets.add(sig);
  const [a,b,c]=tri.map(p),u=b.map((v,k)=>v-a[k]),v=c.map((w,k)=>w-a[k]);
  const cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
  if(Math.hypot(...cross)<1e-9)return {ok:false,reason:'zero triangle'};
  for(let k=0;k<3;k++){
   const from=tri[k],to=tri[(k+1)%3],edge=[from,to].sort((x,y)=>x-y).join(':');
   if(!edges.has(edge))edges.set(edge,[]);
   edges.get(edge).push([from,to]);
  }
 }
 if([...edges.values()].some(v=>v.length>2||v.length===2&&v[0][0]===v[1][0]))
  return {ok:false,reason:'nonmanifold/winding'};
 return {ok:true,vertices:pos.length/3,faces:idx.length/3,edges};
}
const ctx=vm.createContext({Math,Array,Object,Map,Set,Number,console,
 se430MeshOps:{audit,limits:{vertices:9000,faces:16000}}});
vm.runInContext(source+'\nthis.kernel=se483RingDetailKernel;',ctx);
const api=ctx.kernel;
const same=x=>JSON.parse(JSON.stringify(x));
const disc=(n=12)=>{
 const d={positions:[0,0,0],uvs:[.5,.5],indices:[]};
 for(let i=0;i<n;i++){
  const a=2*Math.PI*i/n,x=Math.cos(a),z=Math.sin(a);
  d.positions.push(x,0,z);d.uvs.push(.5+x*.5,.5+z*.5);
 }
 for(let i=0;i<n;i++)d.indices.push(0,1+i,1+(i+1)%n);
 return d;
};
const circle=disc(12);
assert(audit(circle).ok);
const exact=JSON.stringify(circle);
const internal=api.detail(circle,Array.from({length:13},(_,i)=>i),{
 action:'internal',center:[0,0,0],plane:'xz',radius:1,innerRings:2,spacing:'even'
});
console.log('SE483_INTERNAL',JSON.stringify({
 ok:internal.ok,reason:internal.reason,stats:internal.stats,
 radii:internal.ringRadii,members:internal.ringMembers?.map(x=>x.length)
}));
assert(internal.ok,internal.reason);
assert.equal(internal.ringRadii.length,2);
assert(internal.ringMembers.every(m=>m.length>=12),
 'Each internal band must create real connected radial vertices');
const mesh=internal.data;
assert(audit(mesh).ok);
assert(mesh.indices.length>circle.indices.length&&
 mesh.positions.length>circle.positions.length,'Subdivision creates actual indexed faces');
assert(JSON.stringify(circle)===exact,'Original topology unchanged by candidate');
for(let i=0;i<mesh.positions.length/3;i++){
 const x=mesh.positions[i*3],z=mesh.positions[i*3+2];
 assert(Math.abs(mesh.uvs[i*2]-(x*.5+.5))<1e-6,'Preserve atlas U interpolation');
 assert(Math.abs(mesh.uvs[i*2+1]-(z*.5+.5))<1e-6,'Preserve atlas V interpolation');
}
const radialEdges=()=>{
 const ids=new Set(internal.ringMembers[0]);
 const edges=new Set();
 for(let i=0;i<mesh.indices.length;i+=3){
  const [a,b,c]=mesh.indices.slice(i,i+3);
  for(const [u,v]of [[a,b],[b,c],[c,a]])if(ids.has(u)&&ids.has(v))
   edges.add([u,v].sort((x,y)=>x-y).join(':'));
 }
 return edges.size;
};
assert(radialEdges()>=12,'New radial band must contain connected edges, not just markers');
const altered=api.transform(mesh,internal.ringMembers[0],{
 offset:[0,.15,0],tilt:[0,7,0],scale:1.02,falloff:0,
 pivot:[0,0,0],plane:'xz',twist:0
});
console.log('SE483_TRANSFORM',JSON.stringify({
 ok:altered.ok,reason:altered.reason,selected:altered.stats?.selectedVertices
}));
assert(altered.ok,altered.reason);assert(audit(altered.data).ok);
assert.deepEqual(same(altered.data.uvs),same(mesh.uvs),'Never change UV coords for transform');
assert.deepEqual(same(altered.data.indices),same(mesh.indices),'Transforms do not add faces');
for(const id of internal.ringMembers[0]){
 const before=mesh.positions[id*3+1],after=altered.data.positions[id*3+1];
 assert(Math.abs(after-before-.15)<1e-8,'Exact ring Y movement');
}
const cylinder=(n=8)=>{
 const d={positions:[],uvs:[],indices:[]};
 const push=(x,y,z)=>{const id=d.positions.length/3;d.positions.push(x,y,z);d.uvs.push(.5+x*.5,.5+z*.5);return id;};
 const top=push(0,.5,0),bottom=push(0,-.5,0),t=[],b=[];
 for(let i=0;i<n;i++){const a=2*Math.PI*i/n;t.push(push(Math.cos(a),.5,Math.sin(a)));b.push(push(Math.cos(a),-.5,Math.sin(a)));}
 for(let i=0;i<n;i++){
  const j=(i+1)%n;
  d.indices.push(top,t[j],t[i], bottom,b[i],b[j],
   t[i],t[j],b[i], t[j],b[j],b[i]);
 }
 return {d,t};
};
const {d:closed,t:topRing}=cylinder();
assert(audit(closed).ok,'Closed cylinder fixture must have correct manifold winding');
const increased=api.detail(closed,topRing,{
 action:'density',center:[0,.5,0],plane:'xz',target:12
});
console.log('SE483_DENSITY_INCREASE',JSON.stringify({
 ok:increased.ok,reason:increased.reason,stats:increased.stats
}));
assert(increased.ok,increased.reason);
assert(increased.stats.addedPositions>=4);
assert(audit(increased.data).ok);
assert.deepEqual(same(closed),same(cylinder().d),'Density candidate must not touch source');
const reduced=api.detail(increased.data,increased.selectedVertices,{
 action:'density',center:[0,.5,0],plane:'xz',target:8
});
console.log('SE483_DENSITY_REDUCE',JSON.stringify({
 ok:reduced.ok,reason:reduced.reason,stats:reduced.stats
}));
assert(reduced.ok,reduced.reason);
assert(reduced.stats.reducedVertices>0&&audit(reduced.data).ok);
assert.equal(api.detail(closed,topRing,{action:'density',plane:'xz',center:[0,.5,0],target:999}).ok,false);
assert.equal(api.detail(circle,[0,1,2],{action:'internal',plane:'xz',center:[0,0,0],innerRings:20}).ok,false);
for(const tag of [
 'const se483RingDetailKernel=',
 'function radialCuts','function splitEdges','function reduceSafeMidpoints',
 'ringMembers','ringRadii','outerRadius',
 'function density','function transform',
])assert(source.includes(tag),'Missing kernel '+tag);
for(const tag of [
 'Make textured editable copy','ringDetail','window.SWYRL_ENGINE_RING_DETAIL_483',
 'Preview density','Preview new internal rings','Progressive twist',
 'Custom pivot','return fail','native()?.apply?.()','native()?.cancel?.()'
])if(tag!=='Make textured editable copy')assert(studio.includes(tag),'Missing ring detail UI '+tag);
assert(css.includes('SE483_RING_DETAIL_STUDIO_STYLES_END'));
for(const tag of [
 "ringDetailKernel.detail","ringDetailKernel.transform","se483Rings",
 "record.ringMetadata","V11_483_RING_DETAIL_AND_TRANSFORMS"
])assert(patch.includes(tag)||patch.includes(tag.replace("ringDetailKernel","RingDetailKernel")),
 'Missing assembly '+tag);
console.log('SE483_RING_DETAIL_STATIC_PASS: UV-safe internal loops, ring density up/down, subring transform, source immutability and native wiring');
