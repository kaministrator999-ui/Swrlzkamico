'use strict';
/* v11.494 regression: exact account reply can be reopened without cloud.load;
 * project mismatch and cancelled open leave no cached payload behind. */
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../runtime/model_update_account_workflow_v11_494.js'),'utf8');
const context=vm.createContext({
 window:{},performance:{now:()=>1000},
 requestAnimationFrame:fn=>fn(),
 setTimeout:fn=>{fn();return 1},clearTimeout:()=>{},
 setInterval:()=>1,clearInterval:()=>{},
 document:{getElementById:()=>({classList:{remove:()=>{}}})},
 ArrayBuffer,Uint8Array,Map,Promise,Math,Number,String,Error,
});
vm.runInContext(source,context);
vm.runInContext(`globalThis.se494Harness={
 open:se494OpenConfirmedCloud,cache:se494TrustedLoadCache,
 refresh:se494AfterCloudSave,paint:se494NextPaint
}`,context);
const h=context.se494Harness;
(async()=>{
 let requests=0,foundRevision=null;
 vm.runInContext(`globalThis.loadCloud=async id=>{
  const value=se494TrustedLoadCache.get(id);
  if(!value)return false;
  if(value.project.id!==id)throw Error('WRONG_PROJECT_ID');
  globalThis._verifiedRevision=value.project.revision;
  return true;
 }`,context);
 const payload=vm.runInContext('new Uint8Array([1,2,3,4]).buffer',context);
 const project=vm.runInContext('({id:"hat-id",revision:7})',context);
 assert.equal(await h.open('hat-id',project,payload,()=>{}),true);
 assert.equal(context._verifiedRevision,7);
 assert.equal(h.cache.size,0,'verified bytes do not remain after opening');
 await assert.rejects(()=>h.open('wrong-id',project,payload,()=>{}),/cannot be opened safely/);
 assert.equal(h.cache.size,0,'mismatch never caches');
 vm.runInContext(`globalThis.loadCloud=async()=>false`,context);
 await assert.rejects(()=>h.open('hat-id',project,payload,()=>{}),/cancelled or failed/);
 assert.equal(h.cache.size,0,'failed open cannot leave stale saved bytes');
 assert.equal(typeof h.refresh,'function');
 console.log('SE494_MODEL_UPDATE_LIFECYCLE_PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
