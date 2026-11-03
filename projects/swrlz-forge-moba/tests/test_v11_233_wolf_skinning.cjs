// Focused authored Astra skinning contract against exact assembled source.
// Confirms all four coat/paw islands bind to their own limbs, not to spine.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const text=fs.readFileSync(process.argv[2],'utf8');
const a=text.indexOf('const SE224_WOLF_MOTIONS='),b=text.indexOf('function se224WolfVertexWeights(',a);
assert(a>=0&&b>a);
const end=text.indexOf('\n}\n',b)+2;
assert(end>b);
const ctx={};vm.createContext(ctx);
vm.runInContext(text.slice(a,end),ctx,{timeout:1500});
const rig=ctx.se224WolfRigSpec();
assert(ctx.se224WolfRigValid(rig));
const by=Object.fromEntries(rig.bones.map((x,i)=>[x.id,i]));
for(const [name,expected] of [
 ['wolf_head',[0,2.43,.43]],
 ['wolf_fore_l_knee',[-.33,1.13,.4]],
 ['wolf_fore_r_knee',[.33,1.13,.4]],
 ['wolf_hind_l_knee',[-.48,.75,-.43]],
 ['wolf_hind_r_knee',[.48,.75,-.43]]
]){
 const actual=rig.bones.find(b=>b.id===name)?.rest;
 assert.equal(JSON.stringify(actual),JSON.stringify(expected),name+' anatomically misaligned');
}
function weightAt(pt,id){
 const got=ctx.se224WolfVertexWeights(pt,rig,{id});
 assert.equal(got.indexes.length,4);
 assert.equal(got.weights.length,4);
 assert(got.weights.every(n=>Number.isFinite(n)&&n>=0));
 assert(Math.abs(got.weights.reduce((a,b)=>a+b,0)-1)<.00001);
 return Object.fromEntries(got.indexes.map((k,i)=>[rig.bones[k].id,(got.weights[i]||0)]));
}
for(const side of [-1,1])for(const kind of ['fore','hind']){
 const id='astra-living-'+kind+'-'+side,lower=kind==='fore'?[side*.36,.16,.63]:[side*.41,.16,-.62];
 for(const label of [id,'astra-fur-'+id,id+'-claw--1.5']){
  const w=weightAt(lower,label);
  const joint='wolf_'+kind+'_'+(side<0?'l':'r')+'_knee';
  assert((w[joint]||0)>.93,label+' paw not attached to its lower leg');
  assert((w.wolf_spine||0)<.02,label+' paw stretched by torso motion');
 }
 const knee=kind==='fore'?[side*.33,1.13,.4]:[side*.48,.75,-.43];
 const w=weightAt(knee,id);
 assert(Object.values(w).every(Number.isFinite));
 const upper='wolf_'+kind+'_'+(side<0?'l':'r');
 assert((w[upper]||0)>.25&&(w[upper]||0)<.80,id+' knee lacks smooth hinge blending');
}
const face=ctx.se224WolfVertexWeights([0,2.61,.5],rig,{id:'astra-head',organicSurface:{region:'face'}});
assert.equal(rig.bones[face.indexes[0]].id,'wolf_head');
const clips=ctx.se224WolfClips();
assert.equal(clips.clips.length,10);
assert(ctx.se224WolfClipsValid(clips));
for(const clip of clips.clips)for(const key of clip.keys)for(const angles of Object.values(key.rotations))
 assert(angles.every(n=>Number.isFinite(n)&&Math.abs(n)<=Math.PI));
console.log('SE233_WOLF_RIG_ANATOMY_PASS: 4 limbs, 4 fur islands, claws, face, 10 valid clips');
