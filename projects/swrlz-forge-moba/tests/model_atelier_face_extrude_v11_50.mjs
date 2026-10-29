import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import * as THREE from 'three';
const read=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,console,MODEL_ATELIER_KINDS:['sphere']});
vm.runInContext(['model_atelier_topology_lod_v11_38.js',
 'model_atelier_topology_audit_v11_44.js',
 'model_atelier_face_extrude_v11_50.js'].map(read).join('\n'),c);
const tetra={positions:[0,0,0,1,0,0,0,1,0,0,0,1],
 uvs:[0,0,1,0,0,1,.5,.5],indices:[
  0,2,1,0,1,3,1,2,3,2,0,3]};
const part={kind:'topologyMesh',topologyMesh:tetra};
assert(c.atelierTopologyValid(part));
const originalAudit=c.atelierTopologyAudit(tetra);
assert.equal(originalAudit.boundaryEdges,0);
assert.equal(originalAudit.nonManifoldEdges,0);
assert.equal(originalAudit.oppositeWindingErrors,0);
const before=JSON.stringify(tetra);
const r=c.atelierFaceExtrudeCandidate(part,0,.05);
assert(r.ok,r.reason);assert.equal(r.facesBefore,4);
assert.equal(r.facesAfter,10);assert.equal(r.verticesBefore,4);
assert.equal(r.verticesAfter,7);assert.equal(r.after.boundaryEdges,0);
assert.equal(r.after.nonManifoldEdges,0);
assert.equal(r.after.oppositeWindingErrors,0);
assert.equal(r.after.zeroAreaFaces,0);
assert.equal(r.data.positions[14],-.05);
assert.equal(r.data.uvs.length,tetra.uvs.length+6);
assert.equal(JSON.stringify(tetra),before,'Preview may not alter source');
assert(c.atelierTopologyValid({kind:'topologyMesh',topologyMesh:r.data}));
const restored=JSON.parse(JSON.stringify(r.data));
assert.equal(c.atelierTopologyAudit(restored).boundaryEdges,0);
assert.equal(c.atelierTopologyAudit(restored).zeroAreaFaces,0);
const inward=c.atelierFaceExtrudeCandidate(part,0,-.05);
assert(inward.ok,inward.reason);assert(inward.data.positions[14]>.049999);
assert(!c.atelierFaceExtrudeCandidate(part,0,.8).ok);
assert(!c.atelierFaceExtrudeCandidate(part,0,0).ok);
assert(!c.atelierFaceExtrudeCandidate(part,0,NaN).ok);
assert(!c.atelierFaceExtrudeCandidate(part,66,.1).ok);
const open={...tetra,indices:tetra.indices.slice(3)};
const rejected=c.atelierFaceExtrudeCandidate({kind:'topologyMesh',topologyMesh:open},0,.05);
assert(!rejected.ok,/boundary/.test(rejected.reason),rejected.reason);
const invalidUV={...tetra,uvs:tetra.uvs.map(()=>0)};
assert(!c.atelierFaceExtrudeCandidate({kind:'topologyMesh',topologyMesh:invalidUV},0,.05).ok);
console.log('V1150_INDEXED_FACE_OUT_IN_TRUE_WATERTIGHT_SIDEWALL_UV_BOUNDED_NATIVE_PASS',
 r.facesBefore,r.facesAfter,r.after.boundaryEdges);
