// §E v11.469 regression: true UV Jacobians on indexed and procedural buffers.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../runtime/',import.meta.url);
const math=fs.readFileSync(new URL('model_uv_distortion_math_v11_469.js',root),'utf8');
const ui=fs.readFileSync(new URL('model_uv_shape_fit_v11_469.js',root),'utf8');
new vm.Script(math);new vm.Script(ui);
const engine=vm.runInNewContext(math+'\nse469Math;');
function attr(values,dim){return {
 count:values.length/dim,
 getX:i=>values[i*dim],getY:i=>values[i*dim+1],getZ:i=>values[i*dim+2]
};}
const xyz=[0,0,0,1,0,0,1,1,0,0,1,0],uv=[0,0,1,0,1,1,0,1];
function square(indexed=true){
 const p=attr(indexed?xyz:[...xyz.slice(0,9),...xyz.slice(0,3),...xyz.slice(6)],3);
 const t=attr(indexed?uv:[...uv.slice(0,6),...uv.slice(0,2),...uv.slice(4)],2);
 return {
  getAttribute:k=>k==='uv'?t:p,
  getIndex:()=>indexed?{count:6,getX:i=>[0,1,2,0,2,3][i]}:null
 };
}
const matrix=(sx,sy,sz)=>({elements:[sx,0,0,0,0,sy,0,0,0,0,sz,0,0,0,0,1]});
const flat=engine.measure(square(),matrix(1,.25,1));
assert.equal(flat.triangles,2);assert.equal(flat.sampled,2);
assert.ok(Math.abs(flat.suggested[0]-1)<1e-10);
assert.ok(Math.abs(flat.suggested[1]-.25)<1e-10);
assert.ok(Math.abs(flat.peakRatio-4)<1e-6);
assert.equal(flat.highStretch,2);
const uniform=engine.measure(square(false),matrix(3,3,3));
assert.equal(uniform.peakRatio,1);
assert.deepEqual([...uniform.suggested],[1,1]);
const tall=engine.measure(square(),matrix(.5,2,1));
assert.deepEqual([...tall.suggested],[.25,1]);
const severe=engine.measure(square(),matrix(1,.01,1));
assert.deepEqual([...severe.suggested],[1,.15]);
const preserved=engine.anchoredOffset([.2,-.1],[1,1],[1,.25],[.3,.7]);
assert.ok(Math.abs(preserved[0]-.2)<1e-10);
assert.ok(Math.abs(preserved[1]-.05)<1e-10); // Keeps the pinned texel stationary.
assert.throws(()=>engine.measure({getAttribute:()=>null},matrix(1,1,1)),/matching UV/);
for(const mark of [
 'const se469OriginalPartCheck=checkPart',
 'const se469OriginalMaterial=material',
 'se469OriginalUVPaintImage',
 'se469OriginalInstallPreview',
 'checkpoint();',
 'signalEdited();select(t.part.id);',
 'se469Discard()',
 'se469Candidate',
 'se469UVApply',
 'se469UVReset',
 'se469UVAnalyze'
]) assert.ok(ui.includes(mark),mark);
console.log('§E v11.469 UV shape-fit: geometry, mapping, regression and syntax PASS');
