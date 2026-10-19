import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const read=p=>fs.readFileSync(new URL('../runtime/'+p,import.meta.url),'utf8');
const vmc=vm.createContext({THREE,console});
vm.runInContext([
 read('model_atelier_surface_targeting_v11_22.js'),
 read('model_atelier_sculpt_brush_v11_21.js'),
 read('model_atelier_surface_lasso_v11_22.js'),
 read('model_atelier_local_refinement_v11_23.js')
].join('\n'),vmc);
const pin=(x,y,z=0)=>({point:[x,y,z],tri:0,bary:[1,0,0]});
const region={id:'nose-area',name:'Nose region',pins:[pin(-.14,-.14),pin(.14,-.14),pin(.14,.14),pin(-.14,.14)],
 axis:[0,0,1],feather:.02,morph:0,enabled:true,resolution:[0,0]};
const layer={id:'detail-layer',regionId:region.id,level:1,enabled:true};
const part={sculptLassos:[region],refinementLayers:[layer]};
assert(vmc.atelierRefineValid(part));
assert(!vmc.atelierRefineValid({...part,refinementLayers:[{...layer,regionId:'absent'}]}));
assert(!vmc.atelierRefineValid({...part,refinementLayers:[{...layer,level:6}]}));
assert(!vmc.atelierRefineValid({...part,refinementLayers:[{...layer,level:NaN}]}));
const plane=new THREE.PlaneGeometry(1,1,12,12);
plane.setAttribute('color',new THREE.Float32BufferAttribute(
 Array.from({length:plane.attributes.position.count},(_,i)=>
 [i/plane.attributes.position.count,.5,1]).flat(),3));
const preview=vmc.atelierRefineCandidate({geometry:plane},region,1);
assert(preview.ok&&preview.after>preview.before&&preview.delta>0);
assert.equal(preview.before,vmc.atelierRefineCount(plane));
assert.equal(vmc.atelierRefineCount(plane),288,'Preview must not alter the original plane');
assert.equal(vmc.atelierRefineCandidate({geometry:plane},region,7).ok,false);
const result=vmc.atelierRefineApply(plane.clone(),part);
const before=vmc.atelierRefineCount(plane),after=vmc.atelierRefineCount(result);
assert(after>before&&after<before*4,'Only the local region should densify, not the whole mesh');
assert.equal(preview.after,after,'Preview must exactly match actual local refinement');
assert.equal(preview.vertices,result.attributes.position.count);
assert(result.attributes.uv&&result.attributes.color,'UV mapping and vertex dye must survive');
for(const q of result.attributes.uv.array)assert(q>=-.00001&&q<=1.00001);
for(const q of result.attributes.position.array)assert(Number.isFinite(q));
assert.equal(vmc.atelierRefineCount(vmc.atelierRefineApply(plane.clone(),{
 ...part,refinementLayers:[{...layer,enabled:false}]
})),before,'Disabling layer restores base topology');
const edges=new Map(),a=result.attributes.position,idx=result.index;
const key=p=>p.map(n=>Math.round(n*1e5)).join(',');
for(let t=0;t<after;t++){
 const pts=Array.from({length:3},(_,i)=>{
   const v=idx?idx.getX(t*3+i):t*3+i;
   return [a.getX(v),a.getY(v),a.getZ(v)];
 });
 for(let i=0;i<3;i++){
   const k=[key(pts[i]),key(pts[(i+1)%3])].sort().join('|');
   edges.set(k,(edges.get(k)||0)+1);
 }
}
let boundary=0,internal=0;
for(const [k,n]of edges){
 assert(n<=2,'Conforming mesh should have no duplicated overlaid triangles');
 if(n===2){internal++;continue;}
 boundary++;
 const endpoints=k.split('|').map(t=>t.split(',').map(x=>Number(x)/1e5));
 const onOutside=endpoints.every(p=>Math.abs(Math.abs(p[0])-.5)<.00003)
    ||endpoints.every(p=>Math.abs(Math.abs(p[1])-.5)<.00003);
 assert(onOutside,'Interior open edge detected (crack/T-junction): '+k);
}
assert(internal>0&&boundary>0);
const twice=vmc.atelierRefineApply(plane.clone(),{...part,refinementLayers:[{...layer,level:2}]});
assert(vmc.atelierRefineCount(twice)>after);
const serialized=JSON.parse(JSON.stringify(part));
const replay=vmc.atelierRefineApply(plane.clone(),serialized);
assert.equal(vmc.atelierRefineCount(replay),after);
assert.deepEqual(Array.from(replay.attributes.position.array),Array.from(result.attributes.position.array));
console.log('V1123_LOCAL_REFINEMENT_CONFORMING_EDGES_UV_COLORS_LAYER_JSON_PASS',
 before,after,'boundary',boundary,'interior',internal);
