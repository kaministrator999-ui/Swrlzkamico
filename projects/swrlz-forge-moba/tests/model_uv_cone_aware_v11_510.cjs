#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(process.argv[2]||path.join(root,'../../dist/index.html'),'utf8');
function section(start,end){
 const i=html.indexOf(start),j=html.indexOf(end,i+start.length);
 assert.ok(i>=0&&j>i,'Missing assembled source section '+start);
 return html.slice(i,j);
}
const code=section('/* SE510_CONE_AWARE_UV_START','/* SE503_UV_ISLAND_MATH_START')+
 section('/* SE503_UV_ISLAND_MATH_START','// SE503_UV_ISLAND_MATH_END')+
 ';return {math:se503AtlasMath,cone:se510ConeUV};';
const {math,cone}=Function(code)();
const sorting=JSON.parse(fs.readFileSync(path.join(root,'scenes/model-atelier-sorting-hat.swyrl.json'),'utf8'));
const source=fs.readFileSync(path.join(root,'runtime/smooth_witch_hat_v11_504.js'),'utf8');
const smooth=Function("const se504Template='smooth-witch-hat';"+
 source.slice(source.indexOf('function se504SmoothHat('),
              source.indexOf('async function se504OpenSmoothWitchHat'))+
 'return se504SmoothHat;')()(structuredClone(sorting));
function valid(t,r){
 assert.ok(r.data.uvs.every(v=>Number.isFinite(v)&&v>=0&&v<=1));
 assert.equal(r.triangles,t.indices.length/3);
 assert.ok(r.vertices<=9000);
 assert.equal(r.data.indices.length,t.indices.length);
 assert.equal(r.data.positions.length,r.vertices*3);
 assert.equal(r.faces.length,r.triangles);
 for(let i=0;i<r.triangles;i++){
  const f=r.faces[i];
  for(let k=0;k<3;k++){
   const before=t.indices[i*3+k],after=f.ids[k];
   assert.deepEqual(t.positions.slice(before*3,before*3+3),
    r.data.positions.slice(after*3,after*3+3),'3D triangle positions remain unchanged');
  }
 }
 assert.ok(r.distortion.measuredFaces>5000);
}
for(const [name,asset,degenerate,limit] of [
 ['Smooth Witch Hat',smooth,162,1.28],
 ['Original Sorting Hat',sorting,0,1.55]
]){
 const t=asset.project.modelAtelier.parts[0].topologyMesh;
 const p=t.positions.slice(),u=t.uvs.slice(),i=t.indices.slice();
 const auto=math.unwrap(t,{preset:'auto-rim'}),
       tapered=math.unwrap(t,{preset:'cone-rim'}),
       original=math.unwrap(t,{preset:'panels-rim'}),
       two=math.unwrap(t,{preset:'panels'});
 for(const candidate of [auto,tapered,original,two])valid(t,candidate);
 assert.equal(auto.projectionMode,'cone-surface');
 assert.equal(tapered.projectionMode,'cone-surface');
 assert.equal(original.projectionMode,'flat-panels');
 assert.equal(two.projectionMode,'flat-panels');
 assert.equal(auto.stats.length,4);
 assert.equal(two.stats.length,2);
 assert.equal(auto.degenerate3D,degenerate);
 assert.equal(auto.distortion.method,'cone-surface');
 assert.ok(auto.distortion.current<limit,name+' cone distortion upper bound');
 assert.ok(auto.distortion.current<auto.distortion.projected*.84,
  name+' must be substantially better than flat panels');
 assert.equal(auto.vertices,original.vertices,'cone profile does not introduce extra seams');
 assert.equal(auto.duplicatedVertices,original.duplicatedVertices);
 assert.deepEqual(t.positions,p,'source positions unchanged');
 assert.deepEqual(t.indices,i,'source indices unchanged');
 assert.deepEqual(t.uvs,u,'source UVs unchanged');
 console.log('SE510_CONE_METRICS_PASS',JSON.stringify({name,sourceFaces:i.length/3,
  degenerates:degenerate,coneStretch:auto.distortion.current,
  legacyStretch:auto.distortion.projected,vertices:auto.vertices,mode:auto.projectionMode}));
}
const cube={
 positions:[-1,0,-1,1,0,-1,1,1,-1,-1,1,-1,-1,0,1,1,0,1,1,1,1,-1,1,1],
 uvs:Array.from({length:16},()=>.5),
 indices:[0,1,2,0,2,3,4,6,5,4,7,6,0,4,5,0,5,1,1,5,6,1,6,2,2,6,7,2,7,3,3,7,4,3,4,0]
};
const prof=cone.profile(cube,.2,1);
assert.equal(prof.tapered,false,'non-tapered mesh not misclassified as a cone');
const flat=math.unwrap(cube,{preset:'auto-rim'});
assert.equal(flat.projectionMode,'flat-panels');
assert.throws(()=>math.unwrap(cube,{preset:'cone-rim'}),/upright tapered crown/);
assert.match(html,/Color UV distortion/);
assert.match(html,/existing painted texture cannot follow the new unwrap/);
assert.match(html,/se510ConeUV\.stretch/);
console.log('SE510_CONE_UV_CONTRACT_PASS');
