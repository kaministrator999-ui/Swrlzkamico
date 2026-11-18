#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const file=path.join(__dirname,'../runtime/model_rig_skin_math_v11_513.js');
const sandbox={window:{}};vm.runInNewContext(fs.readFileSync(file,'utf8'),sandbox);
const math=sandbox.window.SWYRL_ENGINE_RIG_SKIN_MATH_513;
const almost=(a,b,tol=1e-7)=>assert(Math.abs(a-b)<tol,`${a} != ${b}`);
const row=(ind,wt)=>({indices:ind,weights:wt});
let checks=0;
{
 const invalid=math.row([0,5,0,0],[1,0,0,0],3);
 assert.equal(invalid,null,'out of range bone indexes rejected');checks++;
 const blank=math.row([0,0,0,0],[0,0,0,0],3);
 assert.equal(blank.indices[0],0);almost(blank.weights[0],1);checks++;
}
{
 const original=row([0,0,0,0],[1,0,0,0]);
 const p=math.edit(original,1,.35,4);
 almost(math.edit(original,1,.35,4).weights.reduce((a,b)=>a+b,0),1);
 assert.equal(p.indices[0],0);assert.equal(p.indices[1],1);
 almost(p.weights[0],.65);almost(p.weights[1],.35);
 const diminished=math.edit(p,1,-.2,4);
 almost(diminished.weights[1],.15);almost(diminished.weights[0],.85);
 assert.deepEqual(original.indices,[0,0,0,0],'source untouched');checks++;
}
{
 const original=row([1,2,3,0],[.4,.3,.2,.1]);
 const changed=math.edit(original,4,.55,6);
 assert.equal(changed.indices.includes(4),true);
 assert.equal(changed.indices.length,4);
 almost(changed.weights.reduce((a,b)=>a+b,0),1);
 assert.equal(changed.weights.every(w=>w>=0&&w<=1),true);
 assert.equal(math.edit(original,4,-.4,6).weights.some(w=>w<0),false);checks++;
}
{
 const base=row([0,0,0,0],[1,0,0,0]);
 const unchanged=math.edit(base,0,-.5,3);
 assert.equal(unchanged.weights[0],1,'root-only vertex cannot have no owners');checks++;
}
{
 const verts=[0,0,0,0,.5,0,0,1,0,2,3,0];
 const ii=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
 const ww=[1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0];
 const painted=math.region(verts,ii,ww,[0,.5,0],.66,1,.5,3);
 assert.equal(painted.changed,3);
 assert.deepEqual(Array.from(painted.weights.slice(12,16)),[1,0,0,0],
  'distant mesh vertex must be unchanged');
 assert(Math.abs(painted.weights[5]-.5)<1e-6,'brush center gains actual skin weight');
 assert.deepEqual(ii,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],'original indices unchanged');
 assert.equal(math.validSkin({schema:'swyrl-explicit-skin-v1',
  indices:painted.indices,weights:painted.weights},4,3),true);checks++;
 const seam=math.region([0,0,0,0,0,0],ii.slice(0,8),ww.slice(0,8),
  [0,0,0],.5,1,.2,3);
 assert.equal(seam.changed,2,'duplicated UV seam vertices receive identical paint');checks++;
}
{
 const bad={schema:'swyrl-explicit-skin-v1',indices:[0,1,0,0],weights:[.2,.2,0,0]};
 assert.equal(math.validSkin(bad,1,2),false);
 assert.equal(math.region([0,0,0],[0,0,0,99],[1,0,0,0],[0,0,0],.2,1,.2,2),null);
 checks++;
}
console.log('SE513_SKIN_WEIGHT_MATH_PASS',JSON.stringify({checks,normalized:true,topFour:true,seamMatched:true,distantUntouched:true,undoSourceUntouched:true}));
