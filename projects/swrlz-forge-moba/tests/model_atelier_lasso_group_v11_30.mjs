import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';
const read=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const ctx=vm.createContext({THREE,console});
vm.runInContext(read('model_atelier_surface_targeting_v11_22.js')+'\n'+
  read('model_atelier_surface_lasso_v11_22.js'),ctx);
vm.runInContext(`atelierLassoProjectXYZ=(mesh,xyz)=>xyz.every(Number.isFinite)?
  {point:xyz,tri:0,bary:[1,0,0]}:null;`,ctx);
const pin=(x,y)=>({point:[x,y,0],tri:0,bary:[1,0,0]});
const r={id:'area',name:'saved region',pins:[
 pin(-.1,-.1),pin(.1,-.1),pin(.1,.1),pin(-.1,.1)],
 axis:[0,0,1],feather:.04,morph:0,enabled:true,resolution:[0,0]};
const original=JSON.stringify(r);
const proposal=ctx.atelierLassoGroupCandidate(r,{},'1,2',[0,.025,0]);
assert(proposal.ok);
assert.equal(proposal.indices.length,2);
assert(Math.abs(proposal.pins[0].point[1]+.075)<1e-10);
assert(Math.abs(proposal.pins[1].point[1]+.075)<1e-10);
assert.equal(proposal.pins[2].point[1],.1);
assert.equal(JSON.stringify(r),original,'Preview result must not mutate existing region pins');
for(const [raw,delta]of[
 ['0',[.01,0,0]],['5',[.01,0,0]],['a',[.01,0,0]],
 ['1,2,3,4,5,6,7,8,9',[.01,0,0]],['1',[.151,0,0]],['1',[NaN,0,0]]
])assert(!ctx.atelierLassoGroupCandidate(r,{},raw,delta).ok);
assert(!ctx.atelierLassoGroupCandidate(r,null,'1',[.01,0,0]).ok);
const first=ctx.atelierLassoGroupCandidate(r,{},'1,2',[0,.025,0]);
const replay=ctx.atelierLassoGroupCandidate(JSON.parse(JSON.stringify(r)),{},'1,2',[0,.025,0]);
assert.deepEqual(JSON.parse(JSON.stringify(first.pins)),JSON.parse(JSON.stringify(replay.pins)));
assert(ctx.atelierLassoValid({sculptLassos:[{...r,pins:first.pins}]}));
console.log('V1130_ATOMIC_SURFACE_BOUNDARY_PIN_GROUP_VALIDATE_REPROJECT_PASS');
