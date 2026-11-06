// Narrow regression using the production v11.217 anatomy and v11.290 SDF.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
const root=path.join(__dirname,'../runtime');
const sample={window:{},console,THREE:{}};
vm.createContext(sample);
vm.runInContext(fs.readFileSync(path.join(root,'model_atelier_hand_proportions_v11_217.js'),'utf8'),sample);
vm.runInContext(fs.readFileSync(path.join(root,'cliff_gauntlet_surface_material_v11_290.js'),'utf8'),sample);
const original=vm.runInContext('se217OrganicHandSkin(se217FingerSpec,se290Math())',sample);
const combined=vm.runInContext('se290GauntletField()',sample);
// Root cause reproduction: the real 217 anatomy does NOT reach the previous
// .57 bound assumption. Its lower connected hand closes near y=.85.
assert(original(0,.58,0)>0,'original hand is absent at old hardcoded .57');
assert(original(0,.90,0)<0,'original hand is present around y=.90');
assert(combined(0,.12,0)>0,'gauntlet must close below the lower rim');
for(const y of [.24,.36,.55,.72,.90,1.05,1.22]){
 assert(combined(0,y,0)<0,'continuous stone forearm+hand at y='+y);
}
assert(combined(.54,.35,0)>0,'gauntlet is not an oversized tube');
assert(combined(0,3.5,0)>0,'no cap beyond fingertips');
const rect=[...Array(100)].flatMap((_,i)=>{
 const y=.2+i*(3.08/99);
 return [.15*Math.cos(i),y,.11*Math.sin(i)];
});
const proxy={topologyMesh:{positions:rect,indices:[0,1,2,3,4,5],uvs:[]}};
sample.window.SWYRL_ENGINE_HAND_SURFACE={
 surface:(field,bounds,step)=>{
  assert.equal(field,combined,'actual continuous field is passed to mesher');
  assert.equal(step,.047);
  assert.equal(bounds[0][1],.12);
  return {positions:rect.slice(),indices:Array.from({length:303},(_,i)=>i%100),uvs:[]};
 },
 weld:mesh=>mesh
};
const actualFieldRef=sample.window.SWYRL_ENGINE_CLIFF_GAUNTLET_290;
// Test helper call directly; fake surface verifies mesh-API contract, while
// real active SDF geometry was checked against all wrist and finger samples.
const originalBuilder=vm.runInContext('se290GauntletField',sample);
const built=actualFieldRef.build(proxy);
assert.equal(built.meshes,1);
assert.equal(built.vertices,100);
assert.equal(built.minY,.2);
assert(built.maxY>3.1);
const count=actualFieldRef.remapUV(proxy);
assert.equal(count,100);
assert.equal(proxy.topologyMesh.uvs.length,200);
assert(proxy.topologyMesh.uvs.every(n=>Number.isFinite(n)&&n>=0&&n<=1));
sample.THREE.Vector2=class Vector2{constructor(x,y){this.x=x;this.y=y}};
sample.THREE.MeshStandardMaterial=class Material{constructor(values){Object.assign(this,values)}};
sample.THREE.DoubleSide=2;
sample.THREE.TangentSpaceNormalMap=0;
vm.runInContext('function se288AtlasTile(n,color){return {tile:n,color:!!color}}',sample);
const mat=vm.runInContext('se290CliffMaterial({color:"#ffffff"})',sample);
assert(mat.normalScale.x>1&&mat.aoMapIntensity>1);
assert.equal(mat.metalness,0);
assert.equal(mat.map.tile,0);
assert.equal(mat.normalMap.tile,1);
assert.equal(mat.roughnessMap.tile,2);
assert.equal(mat.aoMap.tile,3);
assert.equal(actualFieldRef.status().renderedRockObjects,0);
assert.equal(actualFieldRef.status().renderedCrackObjects,0);
console.log('SE290_GAUNTLET_SDF_AND_PBR_OK',JSON.stringify({
 originalHandAbsentBelow:.58,continuousSamples:7,meshCount:1,
 atlasTiles:[mat.map.tile,mat.normalMap.tile,mat.roughnessMap.tile,mat.aoMap.tile],
 source:'v11.217 original hand + v11.290 genuine connected forearm'
}));
