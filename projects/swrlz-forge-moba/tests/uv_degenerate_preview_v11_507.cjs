#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(process.argv[2]||path.join(ROOT,'../../dist/index.html'),'utf8');
assert.ok(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_507_UV_DEGENERATE_PREVIEW'));
function section(start,end){
 const a=html.indexOf(start),b=html.indexOf(end,a+start.length);
 assert.ok(a>=0&&b>a,'missing compiled section '+start);
 return html.slice(a,b);
}
const math=Function(section('/* SE503_UV_ISLAND_MATH_START','// SE503_UV_ISLAND_MATH_END')+
 ';return se503AtlasMath;')();
const source=JSON.parse(fs.readFileSync(path.join(ROOT,'scenes/model-atelier-sorting-hat.swyrl.json'),'utf8'));
const orig=source.project.modelAtelier.parts[0].topologyMesh;
const smoothCode=fs.readFileSync(path.join(ROOT,'runtime/smooth_witch_hat_v11_504.js'),'utf8');
const smooth=Function("const se504Template='smooth-witch-hat';"+
 smoothCode.slice(smoothCode.indexOf('function se504SmoothHat('),
                      smoothCode.indexOf('async function se504OpenSmoothWitchHat'))+
 'return se504SmoothHat;')(structuredClone(source));
const mesh=smooth.project.modelAtelier.parts[0].topologyMesh;
assert.equal(mesh.positions.length/3,7859);
assert.equal(mesh.indices.length/3,15714);
function zeroAreas(t){
 let count=0;
 for(let i=0;i<t.indices.length;i+=3){
  const p=t.indices.slice(i,i+3).map(id=>t.positions.slice(3*id,3*id+3));
  const a=p[1].map((x,k)=>x-p[0][k]),b=p[2].map((x,k)=>x-p[0][k]);
  const normal=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
  if(Math.hypot(...normal)<1e-13)count++;
 }
 return count;
}
assert.equal(zeroAreas(mesh),162,'actual smooth starter has 162 degenerate 3D triangles');
assert.equal(zeroAreas(orig),0,'Sorting Hat source is non-degenerate');
const originalPositions=mesh.positions.slice(),originalUvs=mesh.uvs.slice(),
 originalIndices=mesh.indices.slice();
for(const [title,part,expect] of [
 ['Smooth Witch Hat',mesh,162],['Original Sorting Hat',orig,0]
]){
 for(const preset of ['panels','panels-rim']){
  const result=math.unwrap(part,{preset});
  assert.equal(result.degenerate3D,expect,title+' '+preset+' source face warning');
  assert.equal(result.valid3D,result.triangles-expect);
  assert.ok(result.vertices<=9000&&result.vertices>=part.positions.length/3);
  assert.equal(result.triangles,15714);
  assert.equal(result.data.indices.length,part.indices.length);
  assert.equal(result.data.uvs.length,result.data.positions.length/3*2);
  assert.ok(result.data.uvs.every(v=>Number.isFinite(v)&&v>=0&&v<=1));
  assert.equal(result.stats.length,preset==='panels'?2:4);
  for(let f=0;f<result.faces.length;f++){
   const face=result.faces[f];
   for(let k=0;k<3;k++){
    const originalId=part.indices[f*3+k],newId=face.ids[k];
    assert.deepEqual(result.data.positions.slice(newId*3,newId*3+3),
                     part.positions.slice(originalId*3,originalId*3+3),
                     '3D position unchanged including seam vertices');
   }
  }
  if(expect)assert.ok(result.collapsed>=162,'collapsed UV faces visible as warnings');
  console.log('SE507_ATLAS_MODEL_PASS',JSON.stringify({
   title,preset,degenerate3D:result.degenerate3D,collapsedUV:result.collapsed,
   vertices:result.vertices,triangles:result.triangles
  }));
 }
}
assert.deepEqual(mesh.positions,originalPositions,'generator mesh untouched by preview');
assert.deepEqual(mesh.indices,originalIndices,'indices untouched by preview');
assert.deepEqual(mesh.uvs,originalUvs,'painted UVs untouched by preview');
assert.throws(()=>math.unwrap({
 positions:[0,0,0,0,1,0,0,2,0],
 uvs:[0,0,0.5,0.5,1,1],indices:[0,1,2]
}),/Every source triangle has zero area/);
const ui=section('function se503Prepare(){','function se503Apply(){');
assert.ok(ui.includes('scrollIntoView'),'initial mobile preview scroll');
assert.ok(ui.includes("canvas.hidden=true"),'failed previews hide stale canvas');
assert.ok(html.includes('zero-area source triangles preserved'),'warning must identify degenerate source geometry');
console.log('SE507_SMOOTH_WITCH_HAT_PREVIEW_PASS');
