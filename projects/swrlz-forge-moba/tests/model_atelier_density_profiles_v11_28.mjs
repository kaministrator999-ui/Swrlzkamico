import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';
const code=fs.readFileSync(new URL('../runtime/model_atelier_density_profiles_v11_28.js',import.meta.url),'utf8');
const c=vm.createContext({THREE,console,
 geometry:p=>new THREE.SphereGeometry(1,p.meshDensity.u,p.meshDensity.v),
 checkPart:p=>!!p&&['sphere','loft'].includes(p.kind)&&p.meshDensity.u<=256,
 atelierSculptResolution:p=>[p.meshDensity.u,p.meshDensity.v],
 selection:null,partById:()=>null,$m:()=>null});
vm.runInContext(code,c);
assert.equal(vm.runInContext('typeof atelierSculptDensityRefresh',c),'function');
assert.doesNotMatch(code,/function\s+atelierDensityRefresh\s*\(/);
assert.equal(vm.runInContext('typeof atelierSculptDensityInstall',c),'function');
assert.doesNotMatch(code,/function\s+atelierDensityInstall\s*\(/);
const source={kind:'sphere',meshDensity:{u:64,v:48},
 sculptVertexEdits:[{indices:[1],delta:[.1,0,0],resolution:[64,48]}],
 sculptBrushes:[{strength:.1}]};
const before=JSON.stringify(source);
const r=c.atelierDensityPlan(source,32,24);
assert(r.ok);assert.equal(r.u,32);assert.equal(r.v,24);
assert(r.after.vertices<r.before.vertices);
assert(r.after.triangles<r.before.triangles);
assert.equal(r.after.vertices,(32+1)*(24+1));
assert.equal(r.after.triangles,2*32*(24-1));
assert.equal(r.clearsIndexedEdits,true);
assert.equal(r.preservesBrushes,true);
assert.equal(JSON.stringify(source),before,'Preview must not mutate the real native part');
for(const [u,v]of[[10,24],[260,24],[32,193],[256,192],[Infinity,24],[32,NaN],[32,0]]){
 const bad=c.atelierDensityPlan(source,u,v);
 assert(!bad.ok,'Invalid density must be rejected '+u+','+v);
}
assert.equal(c.atelierDensityPlan({...source,kind:'box'},32,24).ok,false);
console.log('V1128_PARAMETRIC_DENSITY_PRESETS_GENERATOR_EXACT_COUNTS_NONMUTATING_PASS');
