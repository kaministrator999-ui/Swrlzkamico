import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';
const src=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const vmc=vm.createContext({THREE,console});
vm.runInContext(['model_atelier_surface_targeting_v11_22.js',
 'model_atelier_sculpt_brush_v11_21.js',
 'model_atelier_surface_lasso_v11_22.js',
 'model_atelier_local_refinement_v11_23.js'].map(src).join('\n'),vmc);
const pin=(x,y)=>({point:[x,y,0],tri:0,bary:[1,0,0]});
const base={id:'corners',name:'Corner contour',axis:[0,0,1],
 pins:[pin(-.3,-.3),pin(.3,-.3),pin(.3,.3),pin(-.3,.3)],
 feather:0,morph:.08,enabled:true,resolution:[0,0]};
const raw=JSON.stringify(base),smooth={...base,boundaryCurve:1};
assert(vmc.atelierLassoValid({sculptLassos:[base]}));
assert(vmc.atelierLassoValid({sculptLassos:[smooth]}));
for(const curve of [-1,1.01,Infinity,'round',NaN])
 assert(!vmc.atelierLassoValid({sculptLassos:[{...base,boundaryCurve:curve}]}));
assert(vmc.atelierLassoPolygonValid(smooth));
const straight=vmc.atelierLassoProjection(base).poly;
const curve=vmc.atelierLassoProjection(smooth).poly;
assert.equal(straight.length,4);
assert.equal(curve.length,16,'Two rounds of bounded curve interpolation sample 4× control edges');
assert.equal(vmc.atelierLassoCurvePoints(straight,0),straight,
 'Disabled curve must return source polygon without allocating altered contour');
const srcCount=32,poly=Array.from({length:srcCount},(_,i)=>
 [Math.cos(i*Math.PI*2/srcCount),Math.sin(i*Math.PI*2/srcCount)]);
assert.equal(vmc.atelierLassoCurvePoints(poly,1).length,128,
 'Max 32 pins must cap interpolated contour to 128 evaluated coordinates');
assert.equal(vmc.atelierLassoInside([.58,.58],straight),true);
assert.equal(vmc.atelierLassoInside([.58,.58],curve),false,
 'Rounded boundaries must trim the actual polygon corner region');
assert.equal(vmc.atelierLassoInside([.3,.3],curve),true);
assert.equal(JSON.stringify(base),raw,'Sampling curve cannot rewrite pinned region');
const geometry=new THREE.PlaneGeometry(1,1,40,40);
const original=Float32Array.from(geometry.attributes.position.array);
const morph=r=>vmc.atelierLassoApply(geometry.clone(),{sculptLassos:[r]});
const straightMesh=morph(base),curvedMesh=morph(smooth);
const pos=geometry.attributes.position;
let corner=-1,center=-1;
for(let i=0;i<pos.count;i++){
 if(Math.hypot(pos.getX(i)-.275,pos.getY(i)-.275)<1e-5)corner=i;
 if(Math.hypot(pos.getX(i),pos.getY(i))<1e-5)center=i;
}
assert(corner>=0&&center>=0);
assert(straightMesh.attributes.position.getZ(corner)>.05);
assert(Math.abs(curvedMesh.attributes.position.getZ(corner))<1e-6,
 'Curve strength must change actual morph footprint, not just a line drawing');
assert(curvedMesh.attributes.position.getZ(center)>.05,
 'Smoothed contour must preserve center morph influence');
const layer={id:'round-detail',regionId:base.id,level:1,enabled:true};
const run=r=>{
 const part={sculptLassos:[r],refinementLayers:[layer]};
 const next=vmc.atelierRefineApply(geometry.clone(),part);
 const preview=vmc.atelierRefineCandidate({geometry},r,1,part);
 assert(preview.ok);assert.equal(preview.after,vmc.atelierRefineCount(next));
 return preview.after;
};
const a=run(base),b=run(smooth);
assert(b<a,'Smoothing must refine fewer real boundary-corner triangles');
assert.deepEqual(Array.from(geometry.attributes.position.array),Array.from(original));
const roundtrip=JSON.parse(JSON.stringify({sculptLassos:[smooth]}));
assert(vmc.atelierLassoValid(roundtrip));
assert.deepEqual(Array.from(morph(roundtrip.sculptLassos[0]).attributes.position.array),
 Array.from(curvedMesh.attributes.position.array));
console.log('V1135_CORNER_CURVE_SAVED_PIN_COUNT_UNCHANGED_MORPH_AND_TRIANGLE_MASK_PASS',
 a,b);
