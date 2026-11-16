import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const math=fs.readFileSync(new URL('../runtime/uv_latitude_math_v11_471.js',import.meta.url),'utf8');
const fine=fs.readFileSync(new URL('../runtime/uv_fine_fit_v11_471.js',import.meta.url),'utf8');
new vm.Script(math);new vm.Script(fine);
const api=vm.runInNewContext(math+'\nse471Latitude;');
const sphere=api.lookup([1,1,1]);
const flat=api.lookup([1,.2,1]);
for(const [curve,name] of [[sphere,'sphere'],[flat,'flat']]){
 assert.equal(curve[0],0,name);
 assert.ok(Math.abs(curve[256]-1)<1e-12,name);
 let prev=1;
 for(let i=0;i<=100;i++){
  const v=1-i/100,w=api.remap(v,curve,1);
  assert.ok(w<=prev+1e-7&&w>=0&&w<=1,name);
  assert.ok(Math.abs(api.remap(v,curve,0)-v)<1e-10,name);
  prev=w;
 }
 assert.ok(Math.abs(api.remap(.5,curve)-.5)<1e-9);
}
assert.ok(Math.abs(api.remap(.25,flat)-.25)>.02,'Flattened sphere should produce meaningful local correction');
assert.ok(Math.abs(api.remap(.25,sphere)-.25)<.00002,'Uniform sphere must remain visually unchanged');
assert.ok(Math.abs(api.remap(.25,flat,.5)-(.25+api.remap(.25,flat))*.5)<.00001);
assert.equal(api.remap(-.1,flat),-.1);
assert.throws(()=>api.lookup([0,0,1]),/Invalid spherical scale/);
for(const term of [
 'const se471GeometryBase=geometry','geo.userData.se471LatitudeOriginalUV',
 'const se471OriginalUVInstall=se469InstallUI',
 "section.id='se471UVFineTune'",
 'checkpoint();','part.uvSphereWarp=nextWarp;','part.uvPaintRepeat=[nextU,nextV]',
 'se356UVPreviewSchedule();','se471WarpGeometry(mesh.geometry,state.item.part,warp)',
 "if(!checkPart(part))",'signalEdited();select(part.id);'
])assert(fine.includes(term),term);
console.log('SE471_LATITUDE_UV_PASS: hemisphere arc correction, monotonic seams, original preserved, Undo-friendly controls');
