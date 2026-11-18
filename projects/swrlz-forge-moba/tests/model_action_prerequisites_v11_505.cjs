#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('node:assert/strict');
const code=fs.readFileSync(path.join(__dirname,'../runtime/model_action_prerequisites_v11_505.js'),'utf8');
function harness(kind){
 const objects={a:{id:'a',name:'Test cloth',kind:kind==='topology'?'topologyMesh':'sphere',position:[0,0,0]},b:{id:'b',kind:'topologyMesh'}};
 const project={parts:Object.values(objects)},calls={confirm:0,native:0,copy:0,switch:0,resume:0,status:[]},pending=[];
 let selectedId='a',nativeAvailable=kind==='native'||kind==='cancel',copyAvailable=kind==='textured';
 if(kind==='reuse')objects.a.se481WorkId='b';
 if(kind==='auto'){objects.b.se481WorkHidden=true;selectedId=null;}
 if(kind==='textured')objects.a.uvPaintPNG='data:image/png;base64,Z';
 const runtime={
  window:{
   confirm:()=>{calls.confirm++;return kind!=='cancel';},
   SWYRL_ENGINE_MODEL_WORKSHOP:{
    inspect:()=>({preview:{active:false},convert:{available:nativeAvailable,reason:'Protected mesh'},selection:{mode:'mesh'}}),
    convert:()=>{calls.native++;objects.a.kind='topologyMesh';return {ok:true};},
    setComponentMode:()=>({ok:true})
   },
   SWYRL_ENGINE_TEXTURED_TOPOLOGY_481:{
    inspect:()=>({available:copyAvailable,reason:'Conversion unsupported'}),
    prepare:()=>{calls.copy++;objects.b.kind='topologyMesh';selectedId='b';return {ok:true};},
    switchSource:()=>{calls.switch++;selectedId='b';return {ok:true};}
   },
   SWYRL_ENGINE_PROGRESSIVE_TOOLS_474:{inspect:()=>({tool:'Vertex',toolType:'vertex'}),
    chooseTool:()=>calls.resume++,chooseMode:()=>calls.resume++}
  },
  document:{readyState:'loading',addEventListener:()=>{},getElementById:()=>null},
  atelierMeshIds:['a'],partById:id=>objects[id],
  model:()=>project,status:s=>calls.status.push(s),select:id=>{selectedId=id;},
  se503Install:()=>{},se503Refresh:()=>{},se503Prepare:()=>{calls.resume++},
  ensurePanel:()=>{},queueMicrotask:fn=>pending.push(fn)
 };
 Object.defineProperty(runtime,'selection',{get:()=>selectedId,set:v=>selectedId=v});
 vm.runInNewContext(code,runtime,{filename:'se505.js'});
 const api=runtime.window.SWYRLZ_E_REQUIREMENTS_505;
 return {api,objects,calls,flush:()=>{while(pending.length)pending.shift()();},select:id=>{selectedId=id}};
}
for(const kind of ['native','textured','reuse','topology','auto','cancel','blocked']){
 const h=harness(kind);const res=h.api.requireEditable('Preview UV atlas',()=>h.calls.resume++);
 h.flush();
 if(kind==='native'){assert.equal(h.calls.native,1);assert.equal(h.calls.resume,1);assert.equal(h.calls.confirm,1);assert.equal(res.ok,true);}
 if(kind==='textured'){assert.equal(h.calls.copy,1);assert.equal(h.calls.native,0);assert.equal(h.calls.resume,1);}
 if(kind==='reuse'){assert.equal(h.calls.switch,1);assert.equal(h.calls.copy,0);assert.equal(h.calls.resume,1);}
 if(kind==='topology'){assert.equal(h.calls.confirm,0);assert.equal(h.calls.resume,1);}
 if(kind==='auto'){assert.equal(h.calls.confirm,0);assert.equal(h.calls.resume,1);assert.equal(res.kind,'auto-select');}
 if(kind==='cancel'||kind==='blocked'){
  assert.equal(h.calls.native,0);assert.equal(h.calls.copy,0);assert.equal(h.calls.resume,0);assert.equal(res.ok,false);
 }
}
console.log('SE505_PREREQUISITE_GATE_PASS: native conversion, protected copy, reuse, ready, cancel and refusal');
