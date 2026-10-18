import assert from 'node:assert/strict';import * as THREE from 'three';
import fs from 'node:fs';import vm from 'node:vm';
const load=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,MODEL_ATELIER_KINDS:['sphere'],console});
vm.runInContext(load('model_atelier_face_volume_v11_23.js')+'\n'+
 load('model_atelier_face_sheet_v11_23.js'),c);
const sheet={refId:'manual-front',shape:'oval',gridU:48,gridV:24,
 crop:[0,0,1,1],headDepth:0};
const face=p=>({kind:'faceSheet',faceSheet:p});
assert(c.atelierFaceSheetValid(face(sheet)));
const baseline=c.atelierFaceSheetGeometry(face(sheet));
assert(Math.abs(baseline.attributes.position.getZ(0))<1e-8);
const landmarks=[
 {name:'noseTip',uv:[.5,.5],radius:.15,depth:.2},
 {name:'eyeLeft',uv:[.32,.67],radius:.10,depth:-.12}
];
const sculpted={...sheet,landmarks};
assert(c.atelierFaceSheetValid(face(sculpted)));
const mesh=c.atelierFaceSheetGeometry(face(sculpted));
assert.equal(mesh.attributes.position.count,baseline.attributes.position.count);
assert.deepEqual(Array.from(mesh.attributes.uv.array),Array.from(baseline.attributes.uv.array));
assert(Math.abs(mesh.attributes.position.getZ(0)-.2)<1e-5,
 'Front center nose tip must move real vertices while UVs remain fixed');
const uv=mesh.attributes.uv,position=mesh.attributes.position;
let eye=-1,d=Infinity;
for(let i=0;i<uv.count;i++){
 const dist=Math.hypot(uv.getX(i)-.32,uv.getY(i)-.67);
 if(dist<d){d=dist;eye=i;}
}
assert(position.getZ(eye)<-.04,'Eye socket must recess separate real vertices');
const back={...sculpted,headDepth:.8};
assert(c.atelierFaceSheetValid(face(back)));
const closed=c.atelierFaceSheetGeometry(face(back));
assert(closed.attributes.position.count>mesh.attributes.position.count);
assert(Math.min(...closed.attributes.position.array.filter((_,i)=>i%3===2))<-.6);
const serialized=JSON.parse(JSON.stringify(sculpted));
assert(c.atelierFaceSheetValid(face(serialized)));
assert.deepEqual(Array.from(c.atelierFaceSheetGeometry(face(serialized)).attributes.position.array),
 Array.from(mesh.attributes.position.array));
for(const bad of [
 [{...landmarks[0],name:'notAFeature'}],
 [{...landmarks[0],depth:.5}],
 [{...landmarks[0],radius:.01}],
 [{...landmarks[0],uv:[1.2,.3]}],
 [landmarks[0],landmarks[0]],
 [{...landmarks[0],depth:NaN}]
]){
 assert(!c.atelierFaceSheetValid(face({...sheet,landmarks:bad})));
}
assert(c.atelierFaceSheetValid(face({...sheet,landmarks:[]})));
console.log('V1139_MANUAL_LANDMARK_REAL_NOSE_EYE_DEPTH_UV_NATIVE_ROUNDTRIP_VALIDATION_PASS',
 mesh.attributes.position.count,closed.attributes.position.count);
