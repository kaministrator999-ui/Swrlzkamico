import assert from 'node:assert/strict';
import {deriveSeamCharts,flattenSeamedMesh} from '../runtime/uv_lscm_core_v11_555.mjs';
import {assertSameTriangles,distortionStats} from '../runtime/uv_atlas_core_v11_555.mjs';
const quad={positions:[0,0,0,1,0,0,1,1,0,0,1,0],
  uvs:[0,0,1,0,1,1,0,1],indices:[0,1,2,0,2,3]};
assert.equal(deriveSeamCharts(quad).length,1);
const flat=flattenSeamedMesh(quad);
assert.equal(flat.charts,1);
assert.equal(flat.indices.length,6);
assert.equal(flat.faceMaterialData.length,2);
assert.ok(flat.totalIterations>=0);
assertSameTriangles(quad,flat);
assert.ok(flat.uvs.every(Number.isFinite));
const ratio=distortionStats(flat.positions,flat.uvs,flat.indices).p95P05;
assert.ok(ratio<=1.1,ratio);
const split=flattenSeamedMesh(quad,new Uint32Array([0,1]));
assert.equal(split.charts,2);
assertSameTriangles(quad,split);
const tetra={
 positions:[0,0,0,1,0,0,0,1,0,0,0,1],
 uvs:[0,0,1,0,0,1,1,1],
 indices:[0,2,1,0,1,3,0,3,2,1,2,3]
};
assert.throws(()=>flattenSeamedMesh(tetra),/no usable seam boundary/i);
console.log('SE555_LSCM_CHART_CONFORMAL_AND_SEAM_TEST_PASS');
