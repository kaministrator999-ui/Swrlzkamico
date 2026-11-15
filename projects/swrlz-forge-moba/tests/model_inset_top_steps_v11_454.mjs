#!/usr/bin/env node
// v11.454: exercise two consecutive real native preview/apply checkpoints.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
const start='/* SE454_INSET_TOP_STEPS_START */',end='/* SE454_INSET_TOP_STEPS_END */';
const a=html.indexOf(start),b=html.indexOf(end,a);
assert(a>=0&&b>a,'Two-stage Inset runtime must be bundled');
assert(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_454_INSET_TOP_STEPS'));
const runtime=html.slice(a,b+end.length);
new vm.Script(runtime,{filename:'model_inset_top_steps_v11_454.js'});
const style=html.slice(html.indexOf('/* SE454_INSET_TOP_STEPS_STYLES_START */'),html.indexOf('/* SE454_INSET_TOP_STEPS_STYLES_END */'));
for(const text of ['#se454InsetTopBar','#se454Range','#se454Set','#se454Hint',
 '[data-se454-inset-stage="depth"] #se452FaceModifiers',
 '#se453RimHandle','top:53px','min-width:65px']){
 assert(style.includes(text),'Top slider CSS missing '+text);
}
assert(!runtime.includes('checkpoint('),'Only native Apply may checkpoint');
assert(!runtime.includes('new THREE.Mesh('),'Top bar must not fork geometry');
assert(runtime.includes("api()?.preview(op,{amount:depth?-value:value})"));
assert(runtime.includes("se430BeginnerSetOperation('extrude',lastGood)"));
assert(runtime.includes("api()?.apply()"));
assert(runtime.includes('invalidAttempt||!validPreview(s)'));

class Element {
 constructor(name){this.name=name;this.dataset={};this.children=new Map();this.listeners={};this.value='';this.disabled=false;this.hidden=false;this.textContent='';this.attributes={};}
 setAttribute(k,v){this.attributes[k]=v;}
 addEventListener(name,callback){this.listeners[name]=callback;}
 append(child){this.appended=child;}
 contains(target){return target===this;}
 querySelector(selector){
  if(!this.children.has(selector))this.children.set(selector,new Element(selector));
  return this.children.get(selector);
 }
}
function scenario(){
 const panel=new Element('panel'),scene=new Element('scene'),quick=new Element('quick'),op=new Element('op'),native=new Element('amount');
 op.value='inset';native.value='.2';
 const elements={'.atelier-scene':scene,'#se445ShapeQuick':quick,
  '#modelAtelierWorkshopOperation':op,'#modelAtelierWorkshopAmount':native};
 panel.querySelector=selector=>elements[selector]||null;
 const state={selection:{partId:'cube',faceIds:[0,1],ids:[0,1]},
   preview:{active:false,operation:null,stats:null},
   operations:{inset:{available:true},extrude:{available:true}}};
 const events=[],applied=[],messages=[];
 const api={
  inspect:()=>state,
  preview:(operation,params)=>{
   events.push({action:'preview',operation,amount:params.amount});
   if(operation==='extrude'&&Math.abs(params.amount)>.8)return {ok:false,reason:'Depth collides with the floor'};
   state.preview={active:true,operation,stats:{[operation==='inset'?'fraction':'depth']:params.amount}};
   return {ok:true,operation,changed:false};
  },
  apply:()=>{
   if(!state.preview.active)return {ok:false,reason:'No preview'};
   applied.push(state.preview.operation);events.push({action:'apply',operation:state.preview.operation});
   state.preview={active:false,operation:null,stats:null};
   return {ok:true,changed:true,id:'cube',selectedFaces:[2,3]};
  },
  cancel:()=>{
   const previous=state.preview.operation;events.push({action:'cancel',operation:previous});
   state.preview={active:false,operation:null,stats:null};
   return {ok:true,cancelled:true};
  }
 };
 const sandbox=vm.createContext({
  se430BeginnerInstall:()=> 'existing',
  se430BeginnerAPI:()=>api,
  se430BeginnerSetOperation:(next,value)=>{op.value=next;native.value=String(value);events.push({action:'choose',operation:next});},
  se430BeginnerResult:()=>{},
  se430MeshOps:{region:()=>({ok:true,normal:[0,1,0],origin:[0,1,0]})},
  partById:()=>({topologyMesh:{positions:[0,1,0,0,0,0,1,0,0]}}),
  window:{addEventListener(){},SWYRL_ENGINE_FACE_FLYOUTS_452:{close:()=>events.push({action:'close'})}},
  document:{activeElement:null,createElement:()=>new Element('overlay')},
  requestAnimationFrame:callback=>callback(),
  queueMicrotask:callback=>callback(),
  status:value=>messages.push(value)
 });
 vm.runInContext(runtime,sandbox);
 assert.equal(sandbox.se430BeginnerInstall(panel),'existing','Native editor installs before top slider');
 const flow=sandbox.window.SWYRL_ENGINE_INSET_TOP_STEPS_454;
 return {flow,scene,op,native,state,events,applied,messages};
}
let s=scenario();
assert.equal(s.flow.begin(),true);
assert.equal(s.flow.inspect().step,'rim');
assert.equal(s.scene.appended.hidden,false,'First stage visible at viewport top');
assert.equal(s.scene.appended.querySelector('#se454Set').textContent,'Set rim');
assert.equal(s.state.preview.operation,'inset');
const range=s.scene.appended.querySelector('#se454Range');
range.listeners.input({target:{value:'.3'}});
assert.equal(s.flow.inspect().lastGood,.3);
assert.equal(s.events.at(-1).amount,.3);
assert.equal(s.flow.set(),true);
assert.deepEqual(s.applied,['inset'],'Set rim commits exactly one native operation');
assert.equal(s.flow.inspect().step,'depth');
assert.equal(s.op.value,'extrude');
assert.equal(s.scene.appended.querySelector('#se454Set').textContent,'Set depth');
assert.equal(s.state.preview.operation,'extrude');
assert(s.events.some(e=>e.action==='preview'&&e.operation==='extrude'&&e.amount<0));
s.scene.appended.querySelector('#se454Range').listeners.input({target:{value:'.9'}});
assert.equal(s.scene.appended.querySelector('#se454Set').disabled,true,'Invalid depth disables Set');
assert.equal(s.state.preview.operation,'extrude','Invalid depth retains last valid candidate');
s.scene.appended.querySelector('#se454Range').listeners.input({target:{value:'.3'}});
assert.equal(s.scene.appended.querySelector('#se454Set').disabled,false,'Valid depth re-enables Set');
assert.equal(s.flow.set(),true);
assert.deepEqual(s.applied,['inset','extrude']);
assert.equal(s.flow.inspect().step,'idle');
assert.equal(s.scene.appended.hidden,true);
assert.equal(s.events.filter(e=>e.action==='apply').length,2,'Exactly two native Undo checkpoints');
s=scenario();
s.flow.begin();s.flow.set();
assert.equal(s.flow.inspect().step,'depth');
s.flow.cancel();
assert.deepEqual(s.applied,['inset'],'Cancel depth keeps explicitly applied rim');
assert(s.events.some(e=>e.action==='cancel'&&e.operation==='extrude'));
assert.match(s.messages.at(-1),/rim remains/i);
s=scenario();
s.flow.begin();s.flow.cancel();
assert.equal(s.applied.length,0,'Cancel rim commits nothing');
assert(s.events.some(e=>e.action==='cancel'&&e.operation==='inset'));
console.log('SE454_INSET_TOP_STEPS_PASS: rim Set -> negative depth preview -> depth Set; invalid values blocked; stage-specific Cancel/Undo');
