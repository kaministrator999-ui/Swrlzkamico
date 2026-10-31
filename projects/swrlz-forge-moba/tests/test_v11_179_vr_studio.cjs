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
assert.throws(()=>a.validateProfile({schema:'swyrl-engine-vr-controls-v1',profileVersion:1}),/Invalid profile identity/);
a.testInput({type:'reset',time:0});
assert.deepEqual(Array.from(a.testInput({type:'down',key:'X',time:0})),[]);
assert.equal(a.testInput({type:'down',key:'A',time:80})[0]?.action,'duplicate');
assert.equal(a.testInput({type:'up',key:'A',time:90}).length,0);
assert.equal(a.testInput({type:'up',key:'X',time:95}).length,0);
a.testInput({type:'reset',time:0});
a.testInput({type:'down',key:'Y',time:0});
a.testInput({type:'down',key:'B',time:50});
assert.equal(a.testInput({type:'tick',time:550})[0]?.action,'save-project');
assert.equal(a.testInput({type:'up',key:'B',time:600}).length,0);
assert.equal(a.testInput({type:'up',key:'Y',time:620}).length,0);
a.testInput({type:'reset',time:0},'play');
a.testInput({type:'down',key:'Y',time:0},'play');
assert.equal(a.testInput({type:'up',key:'Y',time:25},'play')[0]?.action,'pause');

console.log('VR_STUDIO_FOCUSED_TESTS_PASS');
