'use strict';
const assert=require('node:assert/strict');
const vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
function harness(){
 const record={input:{handedness:'right'},targetTracked:true,gripTracked:true};
 const state={mode:'move',gesture:null,controllers:[record],se390Creation:null,se372Sweep:null};
 const calls=[];let hit={gizmo:true,axis:'x'};
 const tools={selection:()=>({ids:['sphere'],primaryId:'sphere'}),
  beginGroup:(id,mode)=>{calls.push(['begin',mode]);return {ok:true};},
  cancel:()=>calls.push(['cancel'])};
 const ctx={window:{},se340XR:state,se340VisibleSession:()=>true,
  se374GizmoContact:()=>hit,se350Tools:()=>tools,se340GripPose:()=>({}),
  se350Root:()=>({updateWorldMatrix(){},matrixWorld:{clone:()=>({invert:()=>({})})},
   getWorldQuaternion:()=>({})}),
  THREE:{Quaternion:class{}},se390BeginPose:()=>{},se372GuideStart:()=>{},
  se340Notice:()=>{},se340Pulse:()=>{},se390NoticeError:()=>{},
  se340FinishGesture:()=>{calls.push(['finish']);state.gesture=null;return true;},
  se340CancelGesture:()=>{calls.push(['cancelGesture']);state.gesture=null;return true;},
  se350Dispatch:sample=>calls.push(['dispatch',sample.events.map(e=>e.action)]),
  se340Cleanup:()=>calls.push(['cleanup']),se372MenuOrbit:()=>calls.push(['orbit'])};
 vm.runInNewContext(fs.readFileSync(path.resolve(__dirname,'../runtime/model_vr_trigger_gizmo_v11_512.js'),'utf8'),ctx);
 const frame=(physical,events=[],opts={})=>ctx.se350Dispatch({
  buttons:{RT:{physical},LT:{physical:false}},events,...opts});
 return {frame,state,calls,record,ctx,setHit:x=>hit=x};
}
for(const [mode,axis] of [['move','x'],['rotate','y'],['scale','uniform'],['grab','z']]){
 const h=harness();h.state.mode=mode;h.setHit({gizmo:true,axis});
 h.frame(true);assert.equal(h.state.gesture.mode,mode==='grab'?'move':mode);
 assert.equal(h.state.gesture.axis,axis);
 h.frame(true);assert.equal(h.calls.filter(c=>c[0]==='begin').length,1);
 h.frame(false,[{action:'select',keys:['RT']}]);
 assert.equal(h.calls.filter(c=>c[0]==='finish').length,1);
 assert.deepEqual(h.calls.at(-1),['dispatch',[]]);
}
{
 const h=harness();h.setHit(null);h.frame(true);assert.equal(h.state.gesture,null);
 h.frame(false,[{action:'select',keys:['RT']}]);
 assert.deepEqual(h.calls.at(-1),['dispatch',['select']]);
}
{
 const h=harness();h.frame(true);h.frame(true,[],{cancel:true});
 assert.equal(h.calls.filter(c=>c[0]==='cancelGesture').length,1);
 assert.equal(h.calls.filter(c=>c[0]==='finish').length,0);
}
{
 const h=harness();h.frame(true);h.record.targetTracked=false;h.frame(true);
 assert.equal(h.calls.filter(c=>c[0]==='cancelGesture').length,1);
}
{
 const h=harness();h.frame(true);h.ctx.se340Cleanup();
 assert.equal(h.ctx.window.SWYRL_ENGINE_MODEL_VR_TRIGGER_GIZMO_512.inspect().active,0);
}
{
 const h=harness();let faces=0;
 h.state.ui={root:{visible:true,position:{},lookAt:()=>{faces++;},updateWorldMatrix:()=>{}}};
 h.state.lastViewer={position:{isVector3:true,distanceToSquared:()=>1}};
 h.state.se372MenuBase={position:{}};
 h.ctx.se372MenuOrbit();assert.equal(faces,1);
 h.state.lastViewer=null;h.ctx.se372MenuOrbit();assert.equal(faces,1);
}
console.log('8 scenario families passed');
