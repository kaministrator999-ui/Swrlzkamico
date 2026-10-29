import assert from 'node:assert/strict';
import * as THREE from 'three';import vm from 'node:vm';import fs from 'node:fs';
const s=fs.readFileSync(new URL('../runtime/model_atelier_topology_lod_v11_38.js',import.meta.url),'utf8');
const c=vm.createContext({THREE,MODEL_ATELIER_KINDS:['sphere']});vm.runInContext(s,c);
assert.match(s,/delete candidate\.runtimeLOD/,'High-mesh preview must drop stale low LOD');
assert.match(s,/delete part\.runtimeLOD/,'Committed topology edit must invalidate stale low LOD');
const g=new THREE.PlaneGeometry(1,1,1,1);
const p={kind:'topologyMesh',topologyMesh:{positions:Array.from(g.attributes.position.array),
 uvs:Array.from(g.attributes.uv.array),indices:Array.from(g.index.array)}};
assert(c.atelierTopologyValid(p));
const before=JSON.stringify(p);
const ids=p.topologyMesh.indices;
const one=ids.slice(0,3),two=ids.slice(3,6);
let chosen=-1;
for(let e=0;e<3;e++){
 const a=one[e],b=one[(e+1)%3];
 if(two.includes(a)&&two.includes(b)){chosen=e;break;}
}
assert(chosen>=0,'Shared interior edge required');
const result=c.atelierTopologyEditCandidate(p,'split-edge',0,chosen,0,[0,0,0]);
assert(result.ok,result.reason);
assert.equal(result.beforeFaces,2);assert.equal(result.afterFaces,4);
assert.equal(result.afterVertices,5); // four original plane vertices plus one
assert.equal(result.data.uvs.length,10);
assert.equal(JSON.stringify(p),before,'Source topology must remain unchanged');
const editable={...p,topologyMesh:result.data};
const moved=c.atelierTopologyEditCandidate(editable,'move-vertex',0,0,0,[0,0,.12]);
assert(moved.ok,moved.reason);
assert.equal(moved.afterFaces,4);assert.equal(moved.afterVertices,5);
assert.equal(moved.data.positions[2],.12);
assert.equal(JSON.stringify(moved.data.uvs),JSON.stringify(result.data.uvs));
const removed=c.atelierTopologyEditCandidate({...p,topologyMesh:moved.data},
 'remove-face',0,0,0,[0,0,0]);
assert(removed.ok,removed.reason);
assert.equal(removed.afterFaces,3);
assert(removed.afterVertices<=5);
assert(c.atelierTopologyValid({kind:'topologyMesh',topologyMesh:removed.data}));
assert(!c.atelierTopologyEditCandidate(p,'split-edge',20,0).ok);
assert(!c.atelierTopologyEditCandidate(p,'split-edge',0,4).ok);
assert(!c.atelierTopologyEditCandidate(p,'move-vertex',0,0,20,[0,0,.1]).ok);
assert(!c.atelierTopologyEditCandidate(p,'move-vertex',0,0,0,[0,0,.8]).ok);
assert(!c.atelierTopologyEditCandidate(p,'remove-face',10).ok);
// Removing a face must not reject a legal high mesh because an old low LOD
// now has the same triangle count. The prior low mesh will be discarded.
const low={positions:p.topologyMesh.positions.slice(),uvs:p.topologyMesh.uvs.slice(),indices:ids.slice(0,3)};
const withLOD={...p,runtimeLOD:{enabled:true,switchDistance:4,low}};
assert(c.atelierTopologyValid(withLOD));
const lodRemove=c.atelierTopologyEditCandidate(withLOD,'remove-face',0);
assert(lodRemove.ok,lodRemove.reason);
const rt=JSON.parse(JSON.stringify(removed.data));
assert(c.atelierTopologyValid({kind:'topologyMesh',topologyMesh:rt}));
assert.equal(JSON.stringify(rt),JSON.stringify(removed.data));
console.log('V1140_ACTUAL_SHARED_EDGE_SPLIT_VERTEX_MOVE_FACE_REMOVE_NATIVE_UNDO_CANDIDATE_PASS',
 result.afterFaces,moved.afterFaces,removed.afterFaces);
