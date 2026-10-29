import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const root=new URL('../',import.meta.url);
const read=p=>fs.readFileSync(new URL(p,root),'utf8');
const context=vm.createContext({THREE,console});
vm.runInContext([
 'runtime/model_atelier_occluded_brush_v11_51.js',
 'runtime/model_atelier_surface_targeting_v11_22.js',
 'runtime/model_atelier_sculpt_brush_v11_21.js',
 'runtime/model_atelier_surface_lasso_v11_22.js',
 'runtime/model_atelier_local_refinement_v11_23.js'
].map(read).join('\n'),context);
const s=(extra={})=>({
 center:[0,0,.05],axis:[0,0,1],cameraLocal:[0,0,2],
 radius:.28,selectionRadius:.28,strength:.1,surfaceMode:'occluded',
 operation:'push',falloff:'smooth',half:false,level:false,
 snap:0,plateau:.2,taper:.5,yaw:0,pitch:0,offsetU:0,offsetV:0,...extra
});
const face=z=>{const g=new THREE.PlaneGeometry(.3,.3,4,4);g.translate(0,0,z);return g};
function doubled(){
 const low=face(0),hi=face(.05),n=low.attributes.position.count,m=hi.attributes.position.count;
 const pos=new Float32Array((n+m)*3),nor=new Float32Array((n+m)*3);
 for(const [part,start] of [[low,0],[hi,n]]){
  pos.set(part.attributes.position.array,start*3);
  nor.set(part.attributes.normal.array,start*3);
 }
 const g=new THREE.BufferGeometry();
 g.setAttribute('position',new THREE.BufferAttribute(pos,3));
 g.setAttribute('normal',new THREE.BufferAttribute(nor,3));
 g.setIndex([...low.index.array,...Array.from(hi.index.array,x=>x+n)]);
 return {g,n,front:n+12,back:12};
}
const {g,front,back}=doubled();
const before=g.attributes.position;
assert(Math.abs(before.getZ(front)-.05)<1e-6, 'outer sheet is in front');
assert(context.atelierSculptValid({sculptBrushes:[s()]}));
for(const wrong of [{cameraLocal:[NaN,0,1]},{cameraLocal:[0,0]},{cameraLocal:undefined},{cameraLocal:[601,0,0]}]){
 assert(!context.atelierSculptValid({sculptBrushes:[s(wrong)]}),'reject invalid stored eye');
}
const occluded=context.atelierSculptApply(g.clone(),{sculptBrushes:[s()]});
const through=context.atelierSculptApply(g.clone(),{sculptBrushes:[s({surfaceMode:'through',cameraLocal:undefined})]});
assert(Math.abs(occluded.attributes.position.getZ(back)-before.getZ(back))<1e-6,
 'rear triangle sheet must be unchanged even when normals point the same way');
assert(occluded.attributes.position.getZ(front)>before.getZ(front)+.06,
 'outer visible sheet must still deform');
assert(through.attributes.position.getZ(back)>before.getZ(back)+.03,
 'legacy through mode must continue to select rear vertices');
const mask=context.atelierBrushOcclusionMask(g,[0,0,2],new Uint8Array(before.count).fill(1),.3);
assert.equal(mask[front],1);assert.equal(mask[back],0);
const nonindexed=g.toNonIndexed();
const all=context.atelierBrushOcclusionMask(nonindexed,[0,0,2],
 new Uint8Array(nonindexed.attributes.position.count).fill(1),.3);
assert(all.some(v=>v===0)&&all.some(v=>v===1),'nonindexed triangles must be ray-tested');
assert.equal(context.atelierBrushOcclusionMask(g,[Infinity,0,0],new Uint8Array(before.count),.3),null);
const many=new THREE.PlaneGeometry(1,1,400,400);
assert.equal(context.atelierBrushOcclusionMask(many,[0,0,2],new Uint8Array(many.attributes.position.count),.3),null,'mobile budget fails closed');
// Legacy surface-mode behavior is covered by v11.22's independent test.
console.log('V1151_BVH_CAMERA_OCCLUSION_SHELL_NONINDEXED_SCHEMA_BUDGET_PASS');
