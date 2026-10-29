import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const src=fs.readFileSync(new URL('../runtime/model_atelier_topology_lod_v11_38.js',import.meta.url),'utf8');
const c=vm.createContext({THREE,MODEL_ATELIER_KINDS:['sphere']});
vm.runInContext(src,c);
// Same physical triangle with two entirely different atlas islands; a 3D
// spatial cluster must not average 0.2 and 0.7 UV values into one false chart.
const g=new THREE.BufferGeometry();
g.setAttribute('position',new THREE.Float32BufferAttribute([
 0,0,0,1,0,0,0,1,0,
 0,0,0,1,0,0,0,1,0
],3));
g.setAttribute('uv',new THREE.Float32BufferAttribute([
 .2,.2,.3,.2,.2,.3,
 .7,.7,.8,.7,.7,.8
],2));
const legacy=c.atelierLODOne(g,8),strict=c.atelierLODOne(g,8,true);
assert.equal(legacy.indices.length/3,1,'legacy voxel cluster merged different UV islands');
assert.equal(strict.indices.length/3,2,'strict guard must retain distinct image chart triangles');
assert.equal(strict.positions.length/3,6);
const distinct=(a,v)=>a.some(n=>Math.abs(n-v)<.00001);
assert(distinct(strict.uvs,.2)&&distinct(strict.uvs,.8));
assert(!distinct(legacy.uvs,.2)&&!distinct(legacy.uvs,.8),
 'legacy UV chart averaging proves the original risk');
const source=new THREE.SphereGeometry(1,64,48);
const before=Array.from(source.attributes.position.array);
const p=c.atelierLODPlan(source,.35,true);
assert(p.ok,p.reason);
assert.equal(p.strictUV,true);
assert(p.after<source.index.count/3&&p.after>30);
assert.equal(p.data.uvs.length,2*p.vertices);
assert(c.atelierTopologyValid({kind:'topologyMesh',topologyMesh:p.data}));
assert.deepEqual(Array.from(source.attributes.position.array),before);
assert(!c.atelierLODPlan(source,.4,'true').ok);
const old=c.atelierLODPlan(source,.35);
assert(old.ok&&!old.strictUV,'previous source defaults remain unchanged');
console.log('V1158_UV_ISLAND_CLUSTER_GUARD_SOURCE_PRESERVE_NATIVE_SCHEMA_PASS',p.after,old.after);
