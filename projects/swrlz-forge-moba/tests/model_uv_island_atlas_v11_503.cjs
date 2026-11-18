#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
const ROOT=path.join(__dirname,'..');
const context={};
vm.runInNewContext(fs.readFileSync(path.join(ROOT,'runtime/model_uv_island_math_v11_503.js'),'utf8')+
 ';globalThis.__uv=se503AtlasMath;',context,{filename:'atlas-math.js'});
const uv=context.__uv;
const hat=JSON.parse(fs.readFileSync(path.join(ROOT,'scenes/model-atelier-sorting-hat.swyrl.json'),'utf8'))
 .project.modelAtelier.parts[0];
const src=hat.topologyMesh;
assert.equal(hat.kind,'topologyMesh');
assert.equal(src.positions.length/3,7859);
assert.equal(src.indices.length/3,15714);
function test(preset){
 const result=uv.unwrap(src,{preset});
 assert.equal(result.triangles,15714);
 assert.ok(result.vertices<=9000,'native vertex limit');
 assert.ok(result.duplicatedVertices>0,'true seam vertex duplication');
 assert.equal(result.data.uvs.length,2*result.vertices);
 assert.equal(result.data.indices.length,src.indices.length);
 assert.equal(result.data.positions.length,3*result.vertices);
 assert.ok(result.data.uvs.every(v=>Number.isFinite(v)&&v>=0&&v<=1));
 assert.equal(result.faces.length,src.indices.length/3);
 for(let i=0;i<src.indices.length;i+=3){
  const original=src.indices.slice(i,i+3),newIds=result.data.indices.slice(i,i+3);
  original.forEach((id,k)=>{
   const a=src.positions.slice(3*id,3*id+3),b=result.data.positions.slice(3*newIds[k],3*newIds[k]+3);
   assert.deepEqual(a,b,'mesh-space vertex and triangle winding preserved');
  });
 }
 for(const face of result.faces){
  const rect=result.stats.find(s=>s.id===face.group).rect;
  for(const [u,v] of face.uv){
   assert.ok(u>rect[0]&&u<rect[2]&&v>rect[1]&&v<rect[3],
    'UV island remains inside own padded region');
  }
 }
 // A true paint guide must use exactly the same UVs as the saved candidate.
 for(const f of result.faces){
  for(let k=0;k<3;k++){
   const id=f.ids[k];
   assert.ok(Math.abs(f.uv[k][0]-result.data.uvs[id*2])<1e-9);
   assert.ok(Math.abs(f.uv[k][1]-result.data.uvs[id*2+1])<1e-9);
  }
 }
 return {preset,vertices:result.vertices,dup:result.duplicatedVertices,
  collapsed:result.collapsed,groups:result.stats.map(x=>[x.name,x.triangles])};
}
const quad=test('panels-rim'),two=test('panels');
assert.equal(quad.groups.length,4);
assert.equal(two.groups.length,2);
const adjusted=uv.unwrap(src,{preset:'panels-rim',transforms:{0:{scale:.92,angle:6,shiftU:.01,shiftV:-.01}}});
assert.equal(adjusted.vertices,quad.vertices);
assert.ok(adjusted.data.uvs.some((v,i)=>Math.abs(v-uv.unwrap(src,{preset:'panels-rim'}).data.uvs[i])>1e-6));
assert.throws(()=>uv.unwrap(src,{transforms:{0:{scale:2}}}),/supported limits/);
assert.throws(()=>uv.unwrap(src,{transforms:{0:{shiftU:.10,scale:1.3}}}),/padded atlas/);
const first=quad.groups.find(g=>g[0]==='Front');
assert.ok(first);
const sourceFace=uv.unwrap(src).faces.find(x=>x.group===0);
const oldPoint=sourceFace.sourceIds.reduce((acc,i)=>{
 acc[0]+=src.uvs[i*2]/3;acc[1]+=src.uvs[i*2+1]/3;return acc;
},[0,0]);
const anchor=uv.remapCenter(src,uv.unwrap(src),...oldPoint);
assert.ok(anchor&&anchor.every(x=>x>=0&&x<=1),'UV anchor remapped');
console.log('SE503_UV_ATLAS_MATH_PASS',JSON.stringify({quad,two,anchor}));
