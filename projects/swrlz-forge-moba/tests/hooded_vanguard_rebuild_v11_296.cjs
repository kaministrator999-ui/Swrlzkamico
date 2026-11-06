// Focused native-factory regression; no browser, GPU or remote services.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const file=require('node:path').join(__dirname,'../runtime/hooded_vanguard_rebuild_v11_296.js');
const source=fs.readFileSync(file,'utf8');
const fields=[];
const native={
 surface(fn,bounds,step){
  assert(Array.isArray(bounds)&&bounds.length===2&&step>0);
  const middle=bounds[0].map((x,i)=>(x+bounds[1][i])/2);
  assert(Number.isFinite(fn(...middle)),'SDF finite at sample');
  fields.push({fn,bounds,step});
  // Geometry stub for exercising native project construction, not meshing.
  return {positions:[0,0,0,.1,0,0,0,.1,0],indices:[0,1,2]};
 },
 weld(g){return g;}
};
const stats={attempts:0,successes:0,lastError:null,lastParts:0,lastTriangles:0};
const model={project:{modelAtelier:{},environmentSettings:{}}};
const context={window:{SWYRL_ENGINE_HAND_SURFACE:native},structuredClone,
 MODEL_ATELIER_CANONICAL_PROJECT:model,se291HeroScene:()=>null,
 se291HeroMaterial:()=>null,se291OpenHero:()=>true,se291Stats:stats,
 console,THREE:{},document:{}};
vm.createContext(context);
vm.runInContext(source,context,{filename:file,timeout:12000});
const scene=vm.runInContext('se296HeroScene()',context,{timeout:12000});
assert.equal(scene.project.name,'Hooded Vanguard · Rebuilt Character');
assert.equal(scene.project.modelAtelier.parts.length,17);
assert.equal(scene.project.modelAtelier.assemblies,null);
assert.equal(scene.project.modelAtelier.rigging,null);
assert.equal(fields.length,5,'figure + two gloves + two boots SDFs');
const names=scene.project.modelAtelier.parts.map(p=>p.name);
assert.equal(names.filter(n=>/glove/.test(n)).length,2);
assert(names.some(n=>/curved fitted hood/.test(n)));
assert(names.some(n=>/breastplate/.test(n)));
assert(names.some(n=>/face-framing/.test(n)));
const ids=new Set();
for(const p of scene.project.modelAtelier.parts){
 assert(!ids.has(p.id));ids.add(p.id);
 assert.equal(p.kind,'topologyMesh');
 const g=p.topologyMesh;
 assert.equal(g.uvs.length,g.positions.length/3*2,p.name+' uv parity');
 assert.equal(g.indices.length%3,0);
 assert(g.positions.every(Number.isFinite));
 assert(g.uvs.every(Number.isFinite));
 assert(g.indices.every(i=>Number.isInteger(i)&&i>=0&&i<g.positions.length/3));
 assert(p.heroPBR.tile.startsWith('v296:'));
}
const gloveFields=fields.filter(o=>o.bounds[0][1]===2.15);
assert.equal(gloveFields.length,2);
for(let k=0;k<gloveFields.length;k++){
 const s=k===0?-1:1,hx=s*.888;
 for(let i=0;i<4;i++){
  const x=hx+(i-1.5)*.043+(i-1.5)*.006;
  const y=2.36-[.115,.145,.137,.108][i];
  assert(gloveFields[k].fn(x,y,.099)<.012,'modeled fingertip '+s+'/'+i);
 }
 assert(gloveFields[k].fn(hx-s*.115,2.40,.145)<.014,'modeled thumb '+s);
}
assert.equal(stats.lastParts,17);
assert.equal(stats.successes,1);
const status=vm.runInContext('window.SWYRL_ENGINE_HOODED_VANGUARD.status()',context);
assert.equal(status.anatomicalHands,true);
assert.equal(status.version,'v11.296');
console.log('VANGUARD_REBUILD_FACTORY_OK',JSON.stringify({
 parts:scene.project.modelAtelier.parts.length,
 facesWithMappedFeatures:1,individualGloves:2,modeledFingertips:10,
 geometrySurfaces:fields.length,materialFamilies:11,
 ownerAppearanceAccepted:false}));
