import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';
const read=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const vmc=vm.createContext({THREE,console,structuredClone});
vm.runInContext([
 'model_atelier_surface_targeting_v11_22.js','model_atelier_sculpt_brush_v11_21.js',
 'model_atelier_surface_lasso_v11_22.js','model_atelier_local_refinement_v11_23.js'
].map(read).join('\n'),vmc);
const pin=(x,y)=>({point:[x,y,0],tri:0,bary:[1,0,0]});
const rectangle=(id,xmin,xmax)=>({id,name:id,axis:[0,0,1],
 pins:[pin(xmin,-.21),pin(xmax,-.21),pin(xmax,.21),pin(xmin,.21)],
 feather:0,morph:0,enabled:true,resolution:[0,0]});
const base=rectangle('base',-.3,.15);
const rhs=rectangle('rhs',-.05,.3);
const part=(op)=>({sculptLassos:[{
 ...base,morph:.08,...(op?{selectionOp:op,operandRegionId:'rhs'}:{})
},rhs]});
const a=part(null);
assert(vmc.atelierLassoValid(a),'Legacy regions without optional Boolean fields remain valid');
for(const op of ['add','subtract','intersect'])
 assert(vmc.atelierLassoValid(part(op)),'Native named Boolean '+op);
for(const bad of [
 {...base,selectionOp:'fake',operandRegionId:'rhs'},
 {...base,selectionOp:'add'},
 {...base,operandRegionId:'rhs'},
 {...base,selectionOp:'subtract',operandRegionId:'base'},
 {...base,selectionOp:'intersect',operandRegionId:'unknown'}])
 assert(!vmc.atelierLassoValid({sculptLassos:[bad,rhs]}),'Invalid composition must reject');
assert(!vmc.atelierLassoValid({sculptLassos:[
 {...base,selectionOp:'add',operandRegionId:'rhs'},
 {...rhs,selectionOp:'add',operandRegionId:'base'}
]}),'Cyclic composition rejected');
assert(!vmc.atelierLassoValid({sculptLassos:[
 {...base,selectionOp:'add',operandRegionId:'rhs'}, {...rhs,axis:[0,0,-1]}
]}),'Opposite-facing operands rejected');
assert(!vmc.atelierLassoValid({sculptLassos:[
 {...base,selectionOp:'add',operandRegionId:'rhs'}, {...rhs,resolution:[30,20]}
]}),'Mixed sampling grids rejected');
const g=new THREE.PlaneGeometry(1,1,40,40),origin=Float32Array.from(g.attributes.position.array);
const indexAt=(x,y)=>{const p=g.attributes.position;let best=-1,d=Infinity;
 for(let i=0;i<p.count;i++){const dd=Math.hypot(p.getX(i)-x,p.getY(i)-y);
  if(dd<d){best=i;d=dd;}}return best;};
const indexFor=[[-.2,0],[.05,0],[.25,0],[.4,0]].map(v=>indexAt(...v));
const positions=op=>vmc.atelierLassoApply(g.clone(),part(op)).attributes.position;
const legacy=positions(null),add=positions('add'),subtract=positions('subtract'),
 intersection=positions('intersect');
const changed=(attr,index)=>attr.getZ(index)>.04;
assert(changed(legacy,indexFor[0]));
assert(changed(legacy,indexFor[1]));
assert(!changed(legacy,indexFor[2]));
assert(changed(add,indexFor[0])&&changed(add,indexFor[1])&&changed(add,indexFor[2]));
assert(changed(subtract,indexFor[0])&&!changed(subtract,indexFor[1])
 &&!changed(subtract,indexFor[2]));
assert(!changed(intersection,indexFor[0])&&changed(intersection,indexFor[1])
 &&!changed(intersection,indexFor[2]));
for(const attr of [legacy,add,subtract,intersection])
 assert(!changed(attr,indexFor[3]),'Unselected vertices must not be modified');
const layer={id:'detail-mask',regionId:'base',level:1,enabled:true};
const refine=op=>{
 const p={...part(op),refinementLayers:[layer]};
 assert(vmc.atelierRefineValid(p));
 const result=vmc.atelierRefineApply(g.clone(),p);
 const candidate=vmc.atelierRefineCandidate({geometry:g},p.sculptLassos[0],1,p);
 assert(candidate.ok);
 assert.equal(candidate.after,vmc.atelierRefineCount(result),
  'Boolean region preview and committed topology must match');
 return {triangles:vmc.atelierRefineCount(result),candidate};
};
const basic=refine(null),combined=refine('add'),cut=refine('subtract'),both=refine('intersect');
assert(combined.triangles>basic.triangles,
 'Union must refine more actual mesh triangles than the base lasso');
assert(cut.triangles<basic.triangles&&both.triangles<basic.triangles,
 'Difference and intersection must refine fewer actual triangles');
assert.deepEqual(Array.from(g.attributes.position.array),Array.from(origin),
 'All region and refinement evaluation is nondestructive to the input geometry');
const persisted=JSON.parse(JSON.stringify(part('add')));
assert(vmc.atelierLassoValid(persisted));
assert.deepEqual(Array.from(vmc.atelierLassoApply(g.clone(),persisted).attributes.position.array),
 Array.from(vmc.atelierLassoApply(g.clone(),part('add')).attributes.position.array),
 'Native JSON composition must replay deterministically');
console.log('V1134_BOOLEAN_REGION_UNION_SUBTRACT_INTERSECT_REAL_MORPH_REFINEMENT_PASS',
 basic.triangles,combined.triangles,cut.triangles,both.triangles);
