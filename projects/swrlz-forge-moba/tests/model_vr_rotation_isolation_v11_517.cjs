#!/usr/bin/env node
'use strict';
// #5: verify native Rotate only touches selected authored part, with no
// synthetic camera/HMD orbit mutation. Also test a drift cancellation.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const script=fs.readFileSync(path.resolve(__dirname,'../runtime/model_vr_project_browser_v11_517.js'),'utf8');
const camera={yaw:.4,pitch:-.1,mode:'rotate',gesture:null,session:{},scene:{},ending:false,
 stateKey:'',se517ProjectBusy:false};
const parts={chosen:{rotation:0},other:{rotation:.32}};
let notice='',cancels=0,cancelReason='',actionCalls=[];
const sandbox=vm.createContext({window:{},se340XR:camera,
 se340Notice:s=>{notice=s;},se340Publish:()=>{},se340SyncUI:()=>{},
 se350Tools:()=>({selection:()=>({ids:['chosen']})}),
 se340ModelXRAction:a=>{actionCalls.push(a);return true;},
 se340UpdateGesture:()=>{
  if(camera.gesture?.mode==='rotate')parts.chosen.rotation+=.12;
  return true;
 },
 se340CancelGesture:reason=>{cancelReason=String(reason);cancels++;camera.gesture=null;return true;},
 se340Cleanup:()=>{},se340VisibleSession:()=>true});
vm.runInContext(script,sandbox);
const api=sandbox.window.SWYRL_ENGINE_VR_PROJECT_BROWSER_517;
assert(api?.operations&&api?.action);
vm.runInContext('se340ModelXRAction("rotate")',sandbox);
assert.deepEqual(actionCalls,['rotate']);
camera.gesture={kind:'group',mode:'rotate'};
const original={yaw:camera.yaw,pitch:camera.pitch,other:parts.other.rotation};
vm.runInContext('se340UpdateGesture()',sandbox);
assert(parts.chosen.rotation>.1,'selected model must rotate in authored space');
assert.equal(parts.other.rotation,original.other,'unselected object must remain stationary');
assert.equal(camera.yaw,original.yaw);assert.equal(camera.pitch,original.pitch);
camera.yaw+=.14;
vm.runInContext('se340UpdateGesture()',sandbox);
assert.equal(cancels,1,'camera drift cancels object rotation instead of combining transforms');
assert.equal(camera.yaw,original.yaw);
assert.equal(camera.pitch,original.pitch);
assert(/camera orbit changed/.test(cancelReason));
console.log('SE517_ROTATION_ISOLATION_PASS',JSON.stringify({
 selectedModelRotated:true,otherModelStationary:true,cameraOrbitUnchanged:true,
 driftCanceled:true}));
