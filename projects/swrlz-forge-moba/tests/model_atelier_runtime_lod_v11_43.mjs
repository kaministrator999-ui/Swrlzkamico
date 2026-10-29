import assert from 'node:assert/strict';
import vm from 'node:vm';import fs from 'node:fs';import * as THREE from 'three';
const source=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,MODEL_ATELIER_KINDS:['sphere'],console});
vm.runInContext(source('model_atelier_topology_lod_v11_38.js')+'\n'+
 source('model_atelier_runtime_lod_v11_43.js'),c);
const raw=new THREE.SphereGeometry(1,48,32);
const data=c.atelierLODPlan(raw,.7);
assert(data.ok&&data.canBake,data.reason);
const low=c.atelierLODPlan(c.atelierTopologyGeometry({kind:'topologyMesh',topologyMesh:data.data}),.3);
assert(low.ok&&low.canBake,low.reason);
const p={kind:'topologyMesh',topologyMesh:data.data,runtimeLOD:{
 enabled:true,switchDistance:6,low:low.data}};
assert(c.atelierTopologyValid(p),'Save both real meshes in one native part');
assert(low.after<data.after&&low.after>0);
assert.equal(c.atelierRuntimeLODChoose(p,3,false),'high');
assert.equal(c.atelierRuntimeLODChoose(p,10,false),'low');
assert.equal(c.atelierRuntimeLODChoose(p,10,true),'high','Editing forces source-high topology');
assert.equal(c.atelierRuntimeLODChoose(p,5.6,false,'low'),'low','Hysteresis avoids flicker');
assert.equal(c.atelierRuntimeLODChoose(p,5,false,'low'),'high');
assert.equal(c.atelierRuntimeLODChoose({...p,runtimeLOD:{...p.runtimeLOD,enabled:false}},10,false),'high');
assert.equal(c.atelierRuntimeLODChoose(p,Number.NaN,false),'high');
assert.equal(c.atelierTopologyValid({...p,runtimeLOD:{...p.runtimeLOD,switchDistance:121}}),false);
assert.equal(c.atelierTopologyValid({...p,runtimeLOD:{...p.runtimeLOD,enabled:1}}),false);
assert.equal(c.atelierTopologyValid({...p,runtimeLOD:{...p.runtimeLOD,low:p.topologyMesh}}),false);
assert.equal(c.atelierTopologyValid({kind:'sphere',runtimeLOD:p.runtimeLOD}),false);
const saved=JSON.parse(JSON.stringify(p));
assert(c.atelierTopologyValid(saved));
assert.equal(saved.topologyMesh.indices.length/3,data.after);
assert.equal(saved.runtimeLOD.low.indices.length/3,low.after);
const high=c.atelierTopologyGeometry(saved),lo=c.atelierTopologyGeometry({
 kind:'topologyMesh',topologyMesh:saved.runtimeLOD.low});
assert.equal(high.index.count/3,data.after);
assert.equal(lo.index.count/3,low.after);
assert.equal(lo.attributes.uv.count,lo.attributes.position.count);
console.log('V1143_NATIVE_GAME_LOD_TWO_ACTUAL_MESHES_DISTANCE_HYSTERESIS_EDIT_SAFETY_PASS',data.after,low.after);
