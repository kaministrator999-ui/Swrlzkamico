import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const root=new URL('../',import.meta.url);
const read=p=>fs.readFileSync(new URL(p,root),'utf8');
const c=vm.createContext({THREE,console});
vm.runInContext([
 'runtime/model_atelier_occluded_brush_v11_51.js',
 'runtime/model_atelier_surface_targeting_v11_22.js',
 'runtime/model_atelier_sculpt_brush_v11_21.js',
 'runtime/model_atelier_brush_ops_v11_27.js',
 'runtime/model_atelier_surface_lasso_v11_22.js',
 'runtime/model_atelier_local_refinement_v11_23.js'
].map(read).join('\n'),c);
const stroke=(extra={})=>({
 center:[0,0,.07],axis:[0,0,1],cameraLocal:[0,0,2],
 radius:.44,selectionRadius:.44,strength:.12,operation:'push',
 surfaceMode:'visible-geodesic',falloff:'smooth',half:false,level:false,
 snap:0,plateau:.2,taper:.5,yaw:0,pitch:0,offsetU:0,offsetV:0,...extra
});
const plane=(x,z)=>{const g=new THREE.PlaneGeometry(.18,.18,4,4);g.translate(x,0,z);return g;};
function layers(){
 const patches=[plane(0,.07),plane(0,0),plane(.25,.07)];
 const count=patches[0].attributes.position.count;
 const coords=new Float32Array(count*patches.length*3);
 const normals=new Float32Array(coords.length),indices=[];
 patches.forEach((patch,j)=>{
  coords.set(patch.attributes.position.array,j*count*3);
  normals.set(patch.attributes.normal.array,j*count*3);
  indices.push(...Array.from(patch.index.array,i=>i+j*count));
 });
 const g=new THREE.BufferGeometry();
 g.setAttribute('position',new THREE.BufferAttribute(coords,3));
 g.setAttribute('normal',new THREE.BufferAttribute(normals,3));
 g.setIndex(indices);
 return {g,front:12,rear:count+12,adjacent:count*2+12};
}
const {g,front,rear,adjacent}=layers();
const original=g.attributes.position;
assert(c.atelierSculptValid({sculptBrushes:[stroke()]}));
for(const bad of [{cameraLocal:[NaN,0,1]},{cameraLocal:[0,2]},{cameraLocal:undefined},
 {cameraLocal:[601,0,0]},{surfaceMode:'imaginary'}]){
 assert(!c.atelierSculptValid({sculptBrushes:[stroke(bad)]}),'reject untrusted native stroke');
}
const combined=c.atelierSculptApply(g.clone(),{sculptBrushes:[stroke()]});
const visible=c.atelierSculptApply(g.clone(),{sculptBrushes:[stroke({surfaceMode:'occluded'})]});
const oldConnected=c.atelierSculptApply(g.clone(),{sculptBrushes:[
 stroke({surfaceMode:'connected',cameraLocal:undefined})]});
assert(combined.attributes.position.getZ(front)>original.getZ(front)+.04,
 'new mode must sculpt the actual front connected surface');
assert(Math.abs(combined.attributes.position.getZ(rear)-original.getZ(rear))<1e-7,
 'hidden back sheet must never move, even though normals are identical');
assert(Math.abs(combined.attributes.position.getZ(adjacent)-original.getZ(adjacent))<1e-7,
 'disconnected but visible adjacent island must not move');
assert(visible.attributes.position.getZ(adjacent)>original.getZ(adjacent)+.01,
 'camera-only mode intentionally allows disconnected visible island');
assert(Math.abs(oldConnected.attributes.position.getZ(adjacent)-original.getZ(adjacent))<1e-7,
 'legacy geodesic mode must still preserve distinct topology');
const distances=c.atelierSurfaceWeights(g,stroke());
assert(Number.isFinite(distances.dist[front])&&distances.dist[front]<.01);
assert(!Number.isFinite(distances.dist[rear]));
assert(!Number.isFinite(distances.dist[adjacent]));
assert.equal(distances.valid[rear],0);
assert.equal(distances.valid[adjacent],1,'adjacent camera-visible island is eligible, but unreachable');
const inflated=c.atelierSculptApply(g.clone(),{sculptBrushes:[stroke({operation:'inflate'})]});
assert(inflated.attributes.position.getZ(front)>original.getZ(front)+.04);
assert(Math.abs(inflated.attributes.position.getZ(rear)-original.getZ(rear))<1e-7);
assert(Math.abs(inflated.attributes.position.getZ(adjacent)-original.getZ(adjacent))<1e-7);
const through=c.atelierSculptApply(g.clone(),{sculptBrushes:[
 stroke({surfaceMode:'through',cameraLocal:undefined})]});
assert(through.attributes.position.getZ(rear)>original.getZ(rear)+.01,
 'legacy through-volume selection still moves rear layer');
// Verified fail-closed eye/budget and preservation of old saved JSON schema.
const excessive=new THREE.PlaneGeometry(1,1,400,400);
const tooBig=c.atelierSurfaceWeights(excessive,stroke());
assert(tooBig.error&&tooBig.valid.every(v=>v===0));
const saved=JSON.parse(JSON.stringify(stroke()));
assert(c.atelierSculptValid({sculptBrushes:[saved]}));
assert.deepEqual(saved.cameraLocal,[0,0,2]);
console.log('V1159_VISIBLE_GEODESIC_CAMERA_RAY_OCCLUSION_CONNECTED_SHELL_OPERATOR_BUDGET_PASS');
