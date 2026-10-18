import assert from 'node:assert/strict';import * as THREE from 'three';
import fs from 'node:fs';import vm from 'node:vm';
const src=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,MODEL_ATELIER_KINDS:['sphere'],console});
vm.runInContext(src('model_atelier_face_volume_v11_23.js')+'\n'+
 src('model_atelier_face_sheet_v11_23.js'),c);
const base={refId:'front',shape:'oval',gridU:48,gridV:20,crop:[0,0,1,1],headDepth:0};
const part=v=>({kind:'faceSheet',faceSheet:v});
const original=c.atelierFaceSheetGeometry(part(base));
const contour=[.55,.75,.98,1,1,.9,.75,.9,1,1,.98,.75];
const shaped={...base,contour};assert(c.atelierFaceSheetValid(part(shaped)));
const g=c.atelierFaceSheetGeometry(part(shaped));
assert.equal(g.attributes.position.count,original.attributes.position.count);
assert.equal(g.index.count,original.index.count);
const rim=1+(base.gridV-1)*base.gridU;
const oldY=original.attributes.position.getY(rim),newY=g.attributes.position.getY(rim);
assert(Math.abs(oldY-.5)<1e-7);
assert(Math.abs(newY-.275)<1e-6);
assert(Math.abs(g.attributes.uv.getY(rim)-(.5+newY))<1e-6,
 'Source photograph UV stays registered with actual trimmed contour');
assert(Math.abs(g.attributes.uv.getX(0)-original.attributes.uv.getX(0))<1e-7);
const closed=c.atelierFaceSheetGeometry(part({...shaped,headDepth:.6}));
assert(closed.attributes.position.count>g.attributes.position.count);
assert.equal(JSON.stringify(shaped),JSON.stringify(JSON.parse(JSON.stringify(shaped))));
for(const bad of [[.8],Array(12).fill(1.1),Array(12).fill(0),
 [...Array(11).fill(1),NaN],Array(12).fill('1')])
 assert(!c.atelierFaceSheetValid(part({...base,contour:bad})));
assert(!c.atelierFaceSheetValid(part({...base,shape:'rectangle',contour})));
const landmarks=[{name:'noseTip',uv:[.5,.5],radius:.13,depth:.18}];
const withNose=c.atelierFaceSheetGeometry(part({...shaped,landmarks}));
assert(withNose.attributes.position.getZ(0)>.17);
assert.deepEqual(Array.from(withNose.attributes.uv.array),Array.from(g.attributes.uv.array));
assert.deepEqual(Array.from(c.atelierFaceSheetGeometry(part({...base})).attributes.position.array),
 Array.from(original.attributes.position.array),'Legacy round oval remains identical');
console.log('V1141_REAL_12_POINT_FACE_SILHOUETTE_UV_CLOSED_HEAD_LANDMARK_COMPAT_PASS',rim,newY);
