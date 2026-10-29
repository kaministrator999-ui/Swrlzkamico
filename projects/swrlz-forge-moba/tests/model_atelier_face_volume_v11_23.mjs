import assert from 'node:assert/strict';
import vm from 'node:vm';import fs from 'node:fs';import * as THREE from 'three';
const root=new URL('../runtime/',import.meta.url);
const read=n=>fs.readFileSync(new URL(n,root),'utf8');
const ctx=vm.createContext({THREE,console,MODEL_ATELIER_KINDS:['sphere','box']});
vm.runInContext(read('model_atelier_face_sheet_v11_23.js')+'\n'+read('model_atelier_face_volume_v11_23.js'),ctx);
const part=(headDepth,shape='oval')=>({
 kind:'faceSheet',faceSheet:{refId:'r1',shape,gridU:20,gridV:8,crop:[.1,.15,.8,.7],headDepth}
});
const flat=ctx.atelierFaceSheetGeometry(part(0));
assert(!flat.userData.faceVolume);
const closed=ctx.atelierFaceSheetGeometry(part(.65));
assert(closed.userData.faceVolume);
assert(closed.index.count>flat.index.count,'Closing oval must create actual rear triangles');
const positions=closed.attributes.position,uv=closed.attributes.uv;
assert(positions.count>flat.attributes.position.count);
let rear=0;
for(let i=0;i<positions.count;i++){
 const z=positions.getZ(i);if(z<-.0001)rear++;
 assert(Number.isFinite(z));
 assert(uv.getX(i)>=.1-1e-5&&uv.getX(i)<=.9+1e-5);
 assert(uv.getY(i)>=.15-1e-5&&uv.getY(i)<=.85+1e-5);
}
assert(rear>=60,'Manual closure adds three 20-point rear rings plus a pole');

closed.computeBoundingBox();assert(Math.abs(closed.boundingBox.min.z+.65)<1e-5);
const edgeCounts=new Map(),indices=closed.index.array;
for(let t=0;t<indices.length;t+=3)for(const [a,b]of[
 [indices[t],indices[t+1]],[indices[t+1],indices[t+2]],[indices[t+2],indices[t]]]){
 const key=Math.min(a,b)+','+Math.max(a,b);edgeCounts.set(key,(edgeCounts.get(key)||0)+1);
}
assert([...edgeCounts.values()].every(x=>x===2),'Closed face/head must be a watertight 2-manifold without T junctions');
const shape=part(.65);
let stat=ctx.atelierFaceVolumeStats(closed,shape);
assert(stat.count>0&&stat.maximum<1e-4,'Unedited front image must retain original UV registration');
const center=0;
positions.setZ(center,.2);positions.needsUpdate=true;
stat=ctx.atelierFaceVolumeStats(closed,shape);
assert(stat.maximum>.04,'Depth deformation should produce measurable UV surface stretch');
assert(!ctx.atelierFaceSheetValid({...shape,faceSheet:{...shape.faceSheet,headDepth:3}}));
assert(!ctx.atelierFaceSheetValid({...shape,faceSheet:{...shape.faceSheet,shape:'rectangle',headDepth:.5}}));
const open=ctx.atelierFaceSheetGeometry(part(0,'rectangle'));
assert.equal(open.index.count,20*8*6);
console.log('V1123_FACE_VOLUME_MANIFOLD_FRONT_UV_NORMALS_STRETCH_PASS',indices.length/3,edgeCounts.size);
