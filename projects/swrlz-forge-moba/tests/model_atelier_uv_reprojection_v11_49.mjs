import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';
const read=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,console,MODEL_ATELIER_KINDS:['sphere']});
vm.runInContext(['model_atelier_topology_lod_v11_38.js',
 'model_atelier_uv_reprojection_v11_49.js'].map(read).join('\n'),c);
const bad={positions:[0,0,0,2,0,0,2,1,0,0,1,0],
 uvs:[0,0,0,0,0,0,0,0],indices:[0,1,2,0,2,3]};
const p={kind:'topologyMesh',topologyMesh:bad};
assert(c.atelierTopologyValid(p));
const before=JSON.stringify(bad);
const inspect=c.atelierUVInspect(p);
assert(inspect.ok);assert.equal(inspect.collapsedUVFaces,2);
const candidate=c.atelierUVReprojectCandidate(p,'XY');
assert(candidate.ok,candidate.reason);
assert.equal(candidate.before.collapsedUVFaces,2);
assert.equal(candidate.after.collapsedUVFaces,0);
assert.equal(candidate.after.oppositeUVFaces,0);
assert.equal(candidate.after.triangles,2);
assert.equal(candidate.after.maxLocalScaleVariation,1);
assert.equal(JSON.stringify(bad),before,'diagnose and preview cannot touch source UV');
assert.deepEqual(JSON.parse(JSON.stringify(candidate.data.uvs)),[0,0,1,0,1,1,0,1]);
assert.deepEqual(JSON.parse(JSON.stringify(candidate.data.positions)),bad.positions);
assert.deepEqual(JSON.parse(JSON.stringify(candidate.data.indices)),bad.indices);
assert(c.atelierTopologyValid({...p,topologyMesh:candidate.data}));
const restored=JSON.parse(JSON.stringify(candidate.data));
assert.equal(c.atelierUVInspect({kind:'topologyMesh',topologyMesh:restored}).collapsedUVFaces,0);
assert(!c.atelierUVReprojectCandidate(p,'XZ').ok,'Planar XY mesh collapses in XZ');
assert(!c.atelierUVReprojectCandidate(p,'xyz').ok,'No unknown plane axes');
assert(!c.atelierUVReprojectCandidate(p,'XY','true').ok);
const flipped=c.atelierUVReprojectCandidate(p,'XY',true);
assert(flipped.ok);assert.equal(flipped.data.uvs[0],1);
assert.equal(flipped.after.oppositeUVFaces,0);
const skew={...bad,positions:bad.positions.slice()};
skew.positions[8]=.3; // diagonal 3D fold: cannot project a whole curved atlas exactly.
const rejection=c.atelierUVReprojectCandidate({kind:'topologyMesh',topologyMesh:skew},'XY');
assert(rejection.ok,'XY projection of mildly skewed face without collapsed projected area can be intentional');
const edgeOn={positions:[0,0,0,1,0,0,1,0,1,0,1,0],
 uvs:[0,0,1,0,1,1,0,1],indices:[0,1,2,0,2,3]};
assert(!c.atelierUVReprojectCandidate({kind:'topologyMesh',topologyMesh:edgeOn},'XY').ok,
 'Face projecting edge-on must refuse UV repair');
console.log('V1149_NATIVE_INDEXED_UV_AREA_DIAGNOSTICS_BOUNDED_PLANAR_REPAIR_NO_SOURCE_MUTATION_PASS');
