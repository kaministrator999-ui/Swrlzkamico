/* §E v11.497: one-mesh sculpted Sorting Hat geometry regression.
   node tests/sorting_hat_sculpted_v11_497.cjs */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'runtime/sorting_hat_sculpted_v11_497.js'),'utf8');
const cut=source.indexOf('async function se497OpenSculptedHat(');
assert(cut>0);
const sandbox={};
vm.runInNewContext(source.slice(0,cut)+';globalThis.fn=se497DeformHat',sandbox);
const scene=JSON.parse(fs.readFileSync(path.join(root,'scenes/model-atelier-sorting-hat.swyrl.json'),'utf8'));
const untouched=structuredClone(scene);
const part=scene.project.modelAtelier.parts[0],geo=part.topologyMesh;
const before=geo.positions.slice(),indices=geo.indices.slice(),uvs=geo.uvs.slice(),paint=part.uvPaintPNG;
sandbox.fn(scene);
assert.equal(untouched.project.canonicalId,'sorting-hat');
assert.equal(scene.project.canonicalId,'sorting-hat-sculpted');
assert.equal(scene.project.template,'sorting-hat-sculpted');
assert.equal(scene.project.modelAtelier.parts.length,1);
assert.equal(part.kind,'topologyMesh');
assert.deepEqual(geo.indices,indices,'Must preserve connected watertight index topology');
assert.deepEqual(geo.uvs,uvs,'Must preserve entire native UV atlas');
assert.equal(part.uvPaintPNG,paint,'Must preserve painted UV texture');
assert.equal(geo.positions.length,7859*3);
assert(geo.positions.every(n=>Number.isFinite(n)&&Math.abs(n)<20));
let changed=0,brimChanged=0,crownChanged=0;
for(let vertex=0;vertex<7859;vertex++){
 const i=vertex*3;
 if(before[i]!==geo.positions[i]||before[i+1]!==geo.positions[i+1]||before[i+2]!==geo.positions[i+2]){
  changed++;
  if(vertex<60*97)crownChanged++;else if(vertex<73*97)brimChanged++;
 }
}
assert(changed>3000&&crownChanged>4000&&brimChanged>500,{changed,crownChanged,brimChanged});
assert(geo.positions[0]-before[0]>.5,'Apex must lean sideways in the alternate sculpture');
assert(geo.positions[1]<before[1]-.19,'Apex bend compresses cloth vertically');
const dirs=new Map(),edges=new Map(),I=indices;
for(let k=0;k<I.length;k+=3){
 for(const [a,b] of [[I[k],I[k+1]],[I[k+1],I[k+2]],[I[k+2],I[k]]]){
  const key=Math.min(a,b)+':'+Math.max(a,b),dr=a+':'+b;
  edges.set(key,(edges.get(key)||0)+1);dirs.set(dr,(dirs.get(dr)||0)+1);
 }
}
assert([...edges.values()].every(n=>n===2),'Cloth must remain a closed manifold');
assert([...dirs.values()].every(n=>n===1),'Triangle winding must remain unique');
console.log('SE497_SORTING_HAT_SCULPTED_PASS',JSON.stringify({parts:1,vertices:7859,triangles:I.length/3,changed,crownChanged,brimChanged}));
