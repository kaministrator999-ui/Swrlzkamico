import assert from 'node:assert/strict';
import {validateMesh,unwrapMesh,assertSameTriangles,distortionStats} from '../runtime/uv_atlas_core_v11_555.mjs';
const source={
 positions:[0,0,0, 1,0,0, 1,1,0, 0,1,0],
 indices:[0,1,2, 0,2,3],
 uvs:[0,0,1,0,1,1,0,1]
};
const factory=async()=>({
 AddMeshError:{Success:0},
 createAtlas(){
  let input;
  return {
   addMesh(d){input=d;return 0;},
   generate(chart,pack){
    assert.ok(chart.maxCost>=5);assert.ok(pack.padding>=4);
    assert.ok(input.indices instanceof Uint32Array);
    assert.ok(input.positions instanceof Float32Array);
   },
   get atlasCount(){return 1;},
   get width(){return 1024;},get height(){return 1024;},
   getMesh(){
    const pos=input.positions,indices=input.indices;
    const uv=Array.from({length:pos.length/3},(_,i)=>[pos[i*3]*1024,pos[i*3+1]*1024]);
    return {indexCount:indices.length,vertexCount:uv.length,chartCount:1,
      vertices:uv.map((pair,i)=>({xref:i,uv:pair})),
      indices};
   },
   destroy(){this.destroyed=true;}
  };
 }
});
const stats=validateMesh(source.positions,source.indices);
assert.equal(stats.triangles,2);
const result=await unwrapMesh(factory,source,{resolution:1024,maxVertices:100,maxCharts:10});
assert.deepEqual(result.indices,source.indices);
assert.deepEqual(result.positions,source.positions);
assert.equal(result.charts,1);
assert.equal(result.distortion.trianglesChecked,2);
assert.equal(result.distortion.p95P05,1);
assertSameTriangles(source,result);
const duplicated={positions:[...source.positions,0,0,0],indices:source.indices};
const welded=await unwrapMesh(factory,duplicated,{weldSeams:true,maxVertices:100});
assert.equal(welded.weldedInputVertices,1);
assert.throws(()=>validateMesh(source.positions,[0,1,50]),/Invalid triangle index/);
assert.throws(()=>distortionStats(source.positions,[0,0,0,0,0,0,0,0],source.indices),/no usable UV/);
assert.throws(()=>assertSameTriangles(source,{positions:source.positions,indices:[0,2,1,0,1,3]}),/changed triangle/);
console.log('SE555_SHARED_REAL_UNWRAP_CORE_AND_FAIL_CLOSED_PASS');
