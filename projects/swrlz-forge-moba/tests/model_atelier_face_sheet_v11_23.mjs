import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const s=fs.readFileSync(new URL('../runtime/model_atelier_face_sheet_v11_23.js',import.meta.url),'utf8');
const c=vm.createContext({THREE,MODEL_ATELIER_KINDS:['sphere'],console});
vm.runInContext(s,c);
const data={
 id:'face-test',kind:'faceSheet',faceSheet:{refId:'ref-1',shape:'oval',
   gridU:48,gridV:16,crop:[.1,.1,.8,.7]}
};
assert(c.atelierFaceSheetValid(data));
assert(!c.atelierFaceSheetValid({...data,faceSheet:{...data.faceSheet,gridU:500}}));
assert(!c.atelierFaceSheetValid({...data,faceSheet:{...data.faceSheet,crop:[.5,.5,.8,.8]}}));
assert(!c.atelierFaceSheetValid({...data,faceSheet:{...data.faceSheet,shape:'prism'}}));
let g=c.atelierFaceSheetGeometry(data);
const triangles=g.index.count/3,uv=g.attributes.uv;
assert(triangles>1000,'Oval face sheet should be a real triangulated surface');
assert.equal(g.attributes.position.count,1+data.faceSheet.gridU*data.faceSheet.gridV);
for(let i=0;i<uv.count;i++){
 assert(uv.getX(i)>=.0999&&uv.getX(i)<=.9001,'Cropped horizontal UV must remain inside image');
 assert(uv.getY(i)>=.0999&&uv.getY(i)<=.8001,'Cropped vertical UV must remain inside image');
}
const original=Array.from(uv.array);
const positions=g.attributes.position;
for(let i=0;i<positions.count;i++){
 const x=positions.getX(i),y=positions.getY(i);
 positions.setZ(i,.1*Math.exp(-(x*x+y*y)*24));
}
assert.deepEqual(Array.from(uv.array),original,'Sculpting facial relief must not disturb UV registration');
g=c.atelierFaceSheetGeometry({...data,faceSheet:{...data.faceSheet,shape:'rectangle',gridU:32,gridV:24}});
assert.equal(g.index.count/3,32*24*2);
assert.equal(g.attributes.uv.count,33*25);
console.log('V1123_UV_FACE_SHEET_TRIANGULATION_CROP_SCULPT_REGISTRATION_PASS',triangles);
