import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';
const read=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,console,MODEL_ATELIER_KINDS:['sphere']});
vm.runInContext(['model_atelier_topology_lod_v11_38.js',
 'model_atelier_topology_audit_v11_44.js',
 'model_atelier_boundary_cap_v11_48.js'].map(read).join('\n'),c);
const base={
 positions:[0,0,0,1,0,0,1,1,0,0,1,0,.5,.5,1],
 uvs:[0,0,1,0,1,1,0,1,.5,.5],
 indices:[0,1,4,1,2,4,2,3,4,3,0,4]
};
const part={kind:'topologyMesh',topologyMesh:base};
assert(c.atelierTopologyValid(part));
assert.equal(c.atelierTopologyAudit(base).boundaryEdges,4);
const before=JSON.stringify(part);
const x=c.atelierBoundaryCapCandidate(part,0);
assert(x.ok,x.reason);assert.equal(x.boundaryVertices,4);
assert.equal(x.addedTriangles,2);
assert.equal(x.before.boundaryEdges,4);
assert.equal(x.after.boundaryEdges,0);
assert.equal(x.after.nonManifoldEdges,0);
assert.equal(x.after.oppositeWindingErrors,0);
assert.equal(x.after.zeroAreaFaces,0);
assert.equal(x.data.positions.length,base.positions.length);
assert.equal(x.data.uvs.length,base.uvs.length);
assert.equal(JSON.stringify(x.data.indices.slice(0,base.indices.length)),JSON.stringify(base.indices));
assert.equal(x.data.indices.length/3,6);
assert.equal(JSON.stringify(part),before,'preview must not mutate source mesh');
assert(c.atelierTopologyValid({...part,topologyMesh:x.data}));
const roundtrip=JSON.parse(JSON.stringify(x.data));
assert.equal(c.atelierTopologyAudit(roundtrip).boundaryEdges,0);
assert.equal(c.atelierTopologyAudit(roundtrip).zeroAreaFaces,0);
assert(!c.atelierBoundaryCapCandidate(part,4).ok,'interior apex cannot be capped');
assert(!c.atelierBoundaryCapCandidate(part,-1).ok);
assert(!c.atelierBoundaryCapCandidate(part,9).ok);
assert(!c.atelierBoundaryCapCandidate(part,0.5).ok);
const warped=structuredClone(base);warped.positions[2]=.2;
const y=c.atelierBoundaryCapCandidate({kind:'topologyMesh',topologyMesh:warped},0);
assert(!y.ok,/nonplanar/.test(y.reason),y.reason);
const degenerate={positions:[0,0,0,1,0,0,0,1,0],
 uvs:[0,0,1,0,0,1],indices:[0,1,2]};
const z=c.atelierBoundaryCapCandidate({kind:'topologyMesh',topologyMesh:degenerate},0);
assert(!z.ok,/zero volume/.test(z.reason),z.reason);
// A concave 5-gon cavity must generate 3 properly wound triangles, not a
// naive crossing or out-of-bounds triangle fan.
const concave={positions:[0,0,0,2,0,0,2,2,0,1,1,0,0,2,0,1,1,1],
 uvs:[0,0,1,0,1,1,.5,.5,0,1,.5,.5],
 indices:[0,1,5,1,2,5,2,3,5,3,4,5,4,0,5]};
assert.equal(c.atelierTopologyAudit(concave).boundaryEdges,5);
const h=c.atelierBoundaryCapCandidate({kind:'topologyMesh',topologyMesh:concave},2);
assert(h.ok,h.reason);assert.equal(h.addedTriangles,3);
assert.equal(h.after.boundaryEdges,0);
assert.equal(h.after.oppositeWindingErrors,0);
assert.equal(h.after.nonManifoldEdges,0);
assert.equal(h.after.zeroAreaFaces,0);
console.log('V1148_EXPLICIT_PLANAR_CONCAVE_HOLE_FILL_INDEXED_MANIFOLD_NO_MUTATION_NATIVE_PASS',
 x.before.boundaryEdges,x.after.boundaryEdges,h.addedTriangles);
