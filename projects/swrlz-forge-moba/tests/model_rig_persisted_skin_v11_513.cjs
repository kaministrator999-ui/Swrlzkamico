#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const old=fs.readFileSync(path.join(__dirname,'../runtime/model_atelier_cloth_rig_v11_489.js'),'utf8');
const start=old.indexOf('function se489AuthoredSkinWeights(');
const end=old.indexOf('function se489ClothSkinWeights(',start);
assert(start>=0&&end>start);
let fallbacks=0;
const fallback=()=>{fallbacks++;return {indices:[0,0,0,0],weights:[1,0,0,0]};};
const read=new Function('se489ClothSkinWeights',old.slice(start,end)+';return se489AuthoredSkinWeights;')(fallback);
const rig={targetPartId:'generic',bones:[{id:'root'},{id:'middle'},{id:'tip'}]};
const part={id:'generic',topologyMesh:{positions:[0,0,0,0,1,0]},skinning:{
 schema:'swyrl-explicit-skin-v1',indices:[0,1,0,0,2,0,0,0],weights:[.2,.8,0,0,.6,.4,0,0]}};
const bottom=read(part,0,rig,[0,0,0]),top=read(part,1,rig,[0,1,0]);
assert.deepEqual(bottom.indices,[0,1,0,0]);
assert.deepEqual(top.indices,[2,0,0,0]);
assert(Math.abs(bottom.weights[1]-.8)<1e-9);
assert(Math.abs(top.weights[0]-.6)<1e-9);
assert.equal(fallbacks,0,'valid author-authored weights must not be replaced by procedural weights');
const other=read({...part,id:'other'},0,rig,[0,0,0]);
assert.deepEqual(other.indices,[0,0,0,0]);
const malformed=read({...part,skinning:{...part.skinning,indices:[99]}},0,rig,[0,0,0]);
assert.equal(fallbacks,1,'mismatched topology must safely fall back to procedural weights');
assert.deepEqual(malformed.weights,[1,0,0,0]);
console.log('SE513_PERSISTED_SKIN_RELOAD_PASS',JSON.stringify({topologyPreserved:true,
 authoredWeightsUsed:true,unrelatedModelStable:true,malformedSafeFallback:true}));
