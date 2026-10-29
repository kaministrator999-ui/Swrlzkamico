import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';
const source=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,console,MODEL_ATELIER_KINDS:['sphere']});
vm.runInContext(['model_atelier_face_volume_v11_23.js',
 'model_atelier_face_sheet_v11_23.js',
 'model_atelier_face_profile_v11_47.js'].map(source).join('\n'),c);
const sheet={refId:'front-1',shape:'oval',gridU:48,gridV:20,
 crop:[0,0,1,1],headDepth:.6};
const front={kind:'faceSheet',faceSheet:sheet};
assert(c.atelierFaceSheetValid(front));
const guide={refId:'right-2',originU:.50,unitsPerU:1,direction:1};
assert(Math.abs(c.atelierFaceProfileDepth(guide,.65)-.15)<1e-8);
const nose={name:'noseTip',uv:[.5,.5],radius:.15,depth:.15,profileU:.65};
const eye={name:'eyeLeft',uv:[.31,.68],radius:.1,depth:-.07,profileU:.43};
const p={kind:'faceSheet',faceSheet:{...sheet,profileGuide:guide,
 landmarks:[nose,eye]}};
assert(c.atelierFaceSheetValid(p),'Calibrated front+side must match native landmark schema');
const g=c.atelierFaceSheetGeometry(p);
const old=c.atelierFaceSheetGeometry(front);
assert.equal(g.attributes.position.count,old.attributes.position.count);
assert.deepEqual(Array.from(g.attributes.uv.array),Array.from(old.attributes.uv.array));
assert(Math.abs(g.attributes.position.getZ(0)-.15)<1e-5,'Nose tip must actually protrude');
let min=Infinity;const a=g.attributes.uv,b=g.attributes.position;
for(let i=0;i<a.count;i++){
 const d=Math.hypot(a.getX(i)-.31,a.getY(i)-.68);
 if(d<.05)min=Math.min(min,b.getZ(i));
}
assert(min<-.03,'Side guide can recess eye socket as real vertices');
const restored=JSON.parse(JSON.stringify(p));assert(c.atelierFaceSheetValid(restored));
assert.deepEqual(Array.from(c.atelierFaceSheetGeometry(restored).attributes.position.array),
 Array.from(g.attributes.position.array));
for(const bad of [
 {refId:'right-2',originU:1.2,unitsPerU:1,direction:1},
 {refId:'right-2',originU:.5,unitsPerU:2.5,direction:1},
 {refId:'right-2',originU:.5,unitsPerU:1,direction:0},
 {refId:'',originU:.5,unitsPerU:1,direction:1},
 {refId:'right-2',originU:.5,unitsPerU:1,direction:1,extra:5}
])assert(!c.atelierFaceSheetValid({kind:'faceSheet',faceSheet:{...sheet,profileGuide:bad}}));
assert(!c.atelierFaceSheetValid({kind:'faceSheet',faceSheet:{...sheet,landmarks:[nose]}}),
 'Linked profile point with no calibration must reject');
assert(!c.atelierFaceSheetValid({kind:'faceSheet',
 faceSheet:{...p.faceSheet,landmarks:[{...nose,depth:.1}]}}),
 'Saved image position and depth must agree');
const left={...guide,direction:-1};
assert(Math.abs(c.atelierFaceProfileDepth(left,.65)+.15)<1e-8);
assert(c.atelierFaceSheetValid({kind:'faceSheet',faceSheet:{...sheet,
 profileGuide:left,landmarks:[{...nose,depth:-.15}]}}));
console.log('V1147_MANUAL_TWO_IMAGE_CALIBRATED_PROFILE_NOSE_EYE_DEPTH_UV_NATIVE_PASS',
 g.attributes.position.count);
