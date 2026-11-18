/* §E v11.504: smooth textured witch hat starter regression. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const runtime=fs.readFileSync(path.join(root,'runtime/smooth_witch_hat_v11_504.js'),'utf8');
new vm.Script(runtime);
const cut=runtime.indexOf('async function se504OpenSmoothWitchHat');
assert(cut>0,'expected native async loader');
const sandbox={};
vm.runInNewContext(runtime.slice(0,cut)+';globalThis.smooth=se504SmoothHat;',sandbox);
const raw=fs.readFileSync(path.join(root,'scenes/model-atelier-sorting-hat.swyrl.json'),'utf8');
const original=JSON.parse(raw),scene=JSON.parse(raw);
const old=original.project.modelAtelier.parts[0],part=scene.project.modelAtelier.parts[0];
sandbox.smooth(scene);
assert.equal(original.project.canonicalId,'sorting-hat');
assert.equal(scene.project.canonicalId,'smooth-witch-hat');
assert.equal(scene.project.template,'smooth-witch-hat');
assert.equal(scene.project.name,'Smooth Witch Hat');
assert.equal(scene.project.modelAtelier.parts.length,1);
assert.equal(part.kind,'topologyMesh');
assert.equal(part.uvPaintPNG,old.uvPaintPNG,'keep original full UV painting');
assert.deepEqual(part.topologyMesh.uvs,old.topologyMesh.uvs,'keep UV topology');
assert.deepEqual(part.topologyMesh.indices,old.topologyMesh.indices,'keep closed indexed topology');
const pos=part.topologyMesh.positions,I=part.topologyMesh.indices;
assert.equal(pos.length,7859*3);
assert.equal(I.length,15714*3);
assert(pos.every(n=>Number.isFinite(n)));
for(const row of [1,8,16,24,32,40,48,55,59]){
 const radii=[],heights=[];
 for(let i=0;i<96;i++){
   const k=(row*97+i)*3;
   radii.push(Math.hypot(pos[k],pos[k+2]/.9));
   heights.push(pos[k+1]);
 }
 assert(Math.max(...radii)-Math.min(...radii)<.00003,'no painted facial relief in ring '+row);
 assert(Math.max(...heights)-Math.min(...heights)<.00003,'smooth crown ring '+row);
}
function radial(row){const k=(row*97)*3;return Math.hypot(pos[k],pos[k+2]/.9);}
assert(radial(65)>1.6,'wide witch brim');
assert(radial(59)>.87&&radial(59)<.92,'full-width cone base');
assert(radial(8)<radial(40),'cone grows toward brim');
assert(Math.hypot(pos[7857*3],pos[7857*3+2])<1e-7,'apex centered');
const edges=new Map(),directions=new Map();
for(let k=0;k<I.length;k+=3)for(const [a,b] of [[I[k],I[k+1]],[I[k+1],I[k+2]],[I[k+2],I[k]]]){
 const key=Math.min(a,b)+':'+Math.max(a,b),direct=a+':'+b;
 edges.set(key,(edges.get(key)||0)+1);
 directions.set(direct,(directions.get(direct)||0)+1);
}
assert([...edges.values()].every(n=>n===2),'sealed watertight topology');
assert([...directions.values()].every(n=>n===1),'no winding corruption');
console.log('SE504_SMOOTH_WITCH_HAT_PASS',JSON.stringify({project:scene.project.canonicalId,parts:1,vertices:pos.length/3,triangles:I.length/3,textureBytes:part.uvPaintPNG.length,watertight:true}));
