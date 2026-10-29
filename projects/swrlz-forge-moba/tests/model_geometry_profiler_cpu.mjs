import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const script=readFileSync(new URL('../runtime/model_atelier_metrics_v11_10.js',import.meta.url),'utf8');
const parts={A:{group:'Character'},B:{group:'Coral flare'}};
const attr=(count,bytes)=>({count,array:{byteLength:bytes}});
const meshes=[
  {isMesh:true,userData:{atelierId:'A'},geometry:{attributes:{position:attr(6,72),normal:attr(6,72)},getAttribute(k){return this.attributes[k]},getIndex(){return null}}},
  {isMesh:true,userData:{atelierId:'B'},geometry:{attributes:{position:attr(4,48)},getAttribute(k){return this.attributes[k]},getIndex(){return {count:6,array:{byteLength:12}}}}},
  {isMesh:true,userData:{atelierHelper:true},geometry:{attributes:{position:attr(999,999)}}},
  {isMesh:false,userData:{atelierId:'A'}}
];
const sandbox={modelRoot:{children:meshes},partById:id=>parts[id]||null};
const result=vm.runInNewContext(script+'\natelierGeometryStats()',sandbox);
assert.equal(result.meshObjects,2);
assert.equal(result.triangles,4);
assert.equal(result.vertices,10);
assert.equal(result.estimatedMeshDraws,2);
assert.equal(result.geometryBytes,204);
assert.equal(result.groups.Character.triangles,2);
assert.equal(result.groups['Coral flare'].triangles,2);
assert.equal(result.basis.includes('CPU buffers only'),true);
console.log('MODEL_GEOMETRY_PROFILER_CPU_PASS');
