const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(require('node:path').join(__dirname,'../runtime/vr_controller_studio_v11_179.js'),'utf8');
const listeners={};
const store=new Map();
const context={
 window:{addEventListener(type,fn){listeners[type]=fn;},SWYRL_ENGINE_DEVICE:{read:()=>({profile:'quest-browser'})}},
 document:{readyState:'loading',addEventListener(type,fn){listeners['document:'+type]=fn;},querySelector:()=>null},
 navigator:{},localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v)},
 prompt:()=>null,confirm:()=>false,console,Date,JSON,Number,Set,Object,Array,Map,RegExp,Error
};
vm.runInNewContext(source,context,{timeout:1500});
const a=context.window.SWYRL_VR_CONTROLS;
assert.equal(a.schema,'swyrl-engine-vr-controls-v1');
assert.equal(a.read().profileId,'kami-precision');
assert.equal(a.read().immersiveCommandsActive,false);
assert.equal(a.inspectBinding('chord:X+A').canonical,a.inspectBinding('chord:A+X').canonical);
assert.throws(()=>a.inspectBinding('tap:MENU'),/Reserved/);
assert.throws(()=>a.inspectBinding('axis:RT'),/Axis/);
assert.throws(()=>a.inspectBinding('chord:Y+Y'),/repeated/);
assert.throws(()=>a.inspectBinding('tap:Y+B'),/Single-input/);
assert.equal(a.diagnose().liveNativeDispatch,false);
console.log('VR_STUDIO_FOCUSED_TESTS_PASS');
