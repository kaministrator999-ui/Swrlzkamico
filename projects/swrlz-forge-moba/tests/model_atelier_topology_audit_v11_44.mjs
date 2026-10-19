import assert from 'node:assert/strict';import * as THREE from 'three';
import fs from 'node:fs';import vm from 'node:vm';
const read=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,MODEL_ATELIER_KINDS:['sphere'],console});
vm.runInContext([
 'model_atelier_topology_lod_v11_38.js',
 'model_atelier_runtime_lod_v11_43.js',
 'model_atelier_topology_audit_v11_44.js'
].map(read).join('\n'),c);
const square={positions:[0,0,0,1,0,0,1,1,0,0,1,0],
 uvs:[0,0,1,0,1,1,0,1],indices:[0,1,2,0,3,2]}; // second face clockwise shared same directed edge 2 -> 0
const p={kind:'topologyMesh',topologyMesh:square};
assert(c.atelierTopologyValid(p));
const a=c.atelierTopologyAudit(square);
assert.equal(a.faces,2);
assert.equal(a.boundaryEdges,4);
assert.equal(a.nonManifoldEdges,0);
assert.equal(a.zeroAreaFaces,0);
assert.equal(a.oppositeWindingErrors,1);
const candidate=c.atelierTopologyReorientCandidate(p);
assert(candidate.ok,candidate.reason);
assert.equal(candidate.flips,1);
assert.equal(candidate.after.oppositeWindingErrors,0);
assert.equal(candidate.after.boundaryEdges,4);
assert.deepEqual(JSON.parse(JSON.stringify(candidate.data.positions)),square.positions);
assert.deepEqual(JSON.parse(JSON.stringify(candidate.data.uvs)),square.uvs);
assert.equal(JSON.stringify(p.topologyMesh),JSON.stringify(square));
assert(!c.atelierTopologyReorientCandidate({kind:'topologyMesh',topologyMesh:candidate.data}).ok);
const nonManifold={...square,indices:[0,1,2,0,3,2,0,2,1]};
const broken=c.atelierTopologyAudit(nonManifold);
assert.equal(broken.nonManifoldEdges,1);
assert(!c.atelierTopologyReorientCandidate({kind:'topologyMesh',topologyMesh:nonManifold}).ok);
const degenerate={...square,positions:[0,0,0,1,0,0,2,0,0,0,1,0]};
assert(c.atelierTopologyAudit(degenerate).zeroAreaFaces>0);
assert(!c.atelierTopologyReorientCandidate({kind:'topologyMesh',topologyMesh:degenerate}).ok);
const reloaded=JSON.parse(JSON.stringify({...p,topologyMesh:candidate.data}));
assert(c.atelierTopologyValid(reloaded));
assert.equal(c.atelierTopologyAudit(reloaded.topologyMesh).oppositeWindingErrors,0);
console.log('V1144_MESH_BOUNDARY_NONMANIFOLD_DEGENERATE_AND_SAFE_WINDING_UNDO_CANDIDATE_PASS');
