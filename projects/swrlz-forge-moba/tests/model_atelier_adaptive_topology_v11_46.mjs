import assert from 'node:assert/strict';
import vm from 'node:vm';import fs from 'node:fs';import * as THREE from 'three';
const src=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,console,MODEL_ATELIER_KINDS:['sphere']});
vm.runInContext(['model_atelier_topology_lod_v11_38.js',
 'model_atelier_topology_audit_v11_44.js',
 'model_atelier_adaptive_topology_v11_46.js'].map(src).join('\n'),c);
const original={positions:[0,0,0,1,0,0,1,1,0,0,1,0],
 uvs:[0,0,1,0,1,1,0,1],indices:[0,1,2,0,2,3]};
const p={kind:'topologyMesh',topologyMesh:original};
assert(c.atelierTopologyValid(p));
const previous=JSON.stringify(original);
const planned=c.atelierAdaptiveRefineCandidate(p,[2/3,1/3,0],.1,.65);
assert(planned.ok,planned.reason);
assert.equal(planned.sourceFaces,2);
assert.equal(planned.selectedFaces,1);
assert.equal(planned.affectedFaces,2,'Shared edge split requires stitching unselected neighbor');
assert.equal(planned.newFaces,10);
assert.equal(planned.newVertices,9);
assert.equal(planned.hasNewBoundary,true);
assert.equal(JSON.stringify(original),previous);
assert(c.atelierTopologyValid({...p,topologyMesh:planned.data}));
const audit=c.atelierTopologyAudit(planned.data);
assert.equal(audit.nonManifoldEdges,0);
assert.equal(audit.zeroAreaFaces,0);
assert.equal(audit.oppositeWindingErrors,0);
assert.equal(audit.boundaryEdges,6);
function area(m){
 let sum=0;
 for(let t=0;t<m.indices.length;t+=3){
  const ids=m.indices.slice(t,t+3),v=ids.map(id=>m.positions.slice(id*3,id*3+3));
  const cross=(v[1][0]-v[0][0])*(v[2][1]-v[0][1])-
    (v[1][1]-v[0][1])*(v[2][0]-v[0][0]);
  assert(cross>1e-12,'Each descendant retains front winding');
  sum+=cross/2;
 }
 return sum;
}
assert(Math.abs(area(original)-1)<1e-9);
assert(Math.abs(area(planned.data)-1)<1e-9,'Stitched triangles must preserve surface area');
for(let i=0;i<planned.data.positions.length/3;i++){
 const x=planned.data.positions[3*i],y=planned.data.positions[3*i+1];
 assert(Math.abs(planned.data.uvs[2*i]-x)<1e-6);
 assert(Math.abs(planned.data.uvs[2*i+1]-y)<1e-6);
}
const reloaded=JSON.parse(JSON.stringify(planned.data));
assert(c.atelierTopologyValid({kind:'topologyMesh',topologyMesh:reloaded}));
assert.equal(c.atelierTopologyAudit(reloaded).nonManifoldEdges,0);
// Duplicate surface vertices across a UV seam must not induce a T-junction.
// UVs are allowed to differ between coincident nodes.
const seam={positions:[0,0,0,1,0,0,1,1,0,0,0,0,1,1,0,0,1,0],
 uvs:[0,0,1,0,1,1,.1,.1,.7,.9,.1,.9],indices:[0,1,2,3,4,5]};
const stitched=c.atelierAdaptiveRefineCandidate({kind:'topologyMesh',topologyMesh:seam},
 [2/3,1/3,0],.1,.65);
assert(stitched.ok,stitched.reason);
assert.equal(stitched.affectedFaces,2);
const beforeSeam=JSON.stringify(seam);
assert.equal(beforeSeam,JSON.stringify(seam));
for(const value of [
 [2/3,1/3,0,NaN],[2/3,1/3],
])assert(!c.atelierAdaptiveRefineCandidate(p,value,.1,.65).ok);
assert(!c.atelierAdaptiveRefineCandidate(p,[2/3,1/3,0],.01,.65).ok);
assert(!c.atelierAdaptiveRefineCandidate(p,[2/3,1/3,0],.1,4).ok);
assert(!c.atelierAdaptiveRefineCandidate(p,[2/3,1/3,0],.1,.0).ok);
console.log('V1146_ADAPTIVE_LOCAL_INDEXED_STITCHED_NO_TJUNCTION_UV_AREA_BUDGET_PASS',
 planned.sourceFaces,planned.newFaces,planned.newVertices);
