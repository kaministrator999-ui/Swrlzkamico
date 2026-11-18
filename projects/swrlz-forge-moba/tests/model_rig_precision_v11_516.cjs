#!/usr/bin/env node
'use strict';
// Native v11.516 math validation independent of any named starter.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const assert=require('node:assert/strict');
const sandbox={window:{}};
const root=path.resolve(__dirname,'../runtime');
for(const file of ['model_rig_skin_math_v11_513.js','model_rig_precision_v11_516.js'])
 vm.runInNewContext(fs.readFileSync(path.join(root,file),'utf8'),sandbox);
const precise=sandbox.window.SWYRL_ENGINE_RIG_PRECISION_516;
const math=sandbox.window.SWYRL_ENGINE_RIG_SKIN_MATH_513;
function skin(n){
 const indices=[],weights=[];
 for(let i=0;i<n;i++){indices.push(0,0,0,0);weights.push(1,0,0,0);}
 return {indices,weights};
}
let checks=0;
{
 // Two UV islands may duplicate a vertex at the same spatial position.
 const positions=[0,0,0,0,0,0,.03,0,0,.5,0,0];
 const s=skin(4);
 const out=precise.region(positions,s.indices,s.weights,[.0005,0,0],.1,1,.4,3,null,'vertex');
 assert.equal(out.changed,2);
 assert(Math.abs(out.weights[1]-.4)<1e-8);
 assert(Math.abs(out.weights[5]-.4)<1e-8);
 assert.deepEqual(Array.from(out.weights.slice(8,12)),[1,0,0,0]);
 assert.deepEqual(Array.from(out.weights.slice(12,16)),[1,0,0,0]);
 assert(math.validSkin({schema:'swyrl-explicit-skin-v1',...out},4,3));
 assert.deepEqual(s.weights,[1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0]);
 checks++;
}
{
 const positions=[0,0,0,0,0,0,.03,0,0,.5,0,0],s=skin(4);
 const out=precise.region(positions,s.indices,s.weights,[0,0,0],.1,1,.4,3,null,'region');
 assert.equal(out.changed,3,'region falloff reaches neighboring vertex');
 assert(math.validSkin({schema:'swyrl-explicit-skin-v1',...out},4,3));
 checks++;
}
{
 // The nearest vertex is found in deformed local coordinates and can be
 // edited even when its rest coordinate was far from the ray intersection.
 const s=skin(3),positions=[0,0,0,1,0,0,2,0,0];
 const pose=i=>[[0,0,0],[.12,0,0],[.70,0,0]][i];
 const out=precise.region(positions,s.indices,s.weights,[.12,0,0],.03,2,.55,3,pose,'vertex');
 assert.equal(out.changed,1);
 assert(out.indices.slice(4,8).includes(2));
 assert(math.validSkin({schema:'swyrl-explicit-skin-v1',...out},3,3));
 checks++;
}
{
 const s=skin(1),positions=[0,0,0];
 const miss=precise.region(positions,s.indices,s.weights,[1,0,0],.03,1,.5,3,null,'vertex');
 assert.equal(miss.changed,0);
 assert.deepEqual(Array.from(miss.weights),s.weights);
 assert.equal(precise.region(positions,s.indices,s.weights,[0,0,0],.03,10,.5,3,null,'vertex'),null);
 assert.equal(precise.region(positions,s.indices,s.weights,[0,0,0],.03,1,.5,3,null,'bogus'),null);
 checks++;
}
{
 // Repeated add/erase must keep every four-slot row normalized and nonnegative.
 const n=128,positions=Array.from({length:n},(_,i)=>[(i%16)/15,Math.floor(i/16)/7,0]).flat();
 let state=skin(n);
 for(let tick=0;tick<20;tick++){
  const bone=tick%4,delta=tick%3===0?-.4:.37;
  const r=precise.region(positions,state.indices,state.weights,[.5,.5,0],.8,bone,delta,7,null,tick%2?'vertex':'region');
  assert(r);
  state={indices:r.indices,weights:r.weights};
  assert(math.validSkin({schema:'swyrl-explicit-skin-v1',...state},n,7));
 }
 checks++;
}
console.log('SE516_SKIN_PRECISION_PASS',JSON.stringify({checks,seamSafe:true,vertexIsolated:true,posedTarget:true,normalized:true}));
