#!/usr/bin/env node
// §E v11.456: conversion never depends on selecting a face of a primitive.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const js=fs.readFileSync(new URL('../runtime/model_guided_primitive_conversion_v11_456.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../runtime/model_guided_primitive_conversion_v11_456.css',import.meta.url),'utf8');
new vm.Script(js,{filename:'model_guided_primitive_conversion_v11_456.js'});
assert(js.includes('api()?.convert()'),'Must delegate conversion to existing native bridge');
assert(js.includes("window.confirm("),'Saved vertex edits require explicit permission');
assert(!js.includes('checkpoint('),'Only native conversion can create an Undo checkpoint');
assert(!js.includes('new THREE.'),'No independent mesh construction');
assert(!js.includes('renderParts('),'No camera/preview destruction');
assert(css.includes('#se456MakeEditable[hidden]')&&css.includes('max-width:699px'),'Responsive control and true hidden state');

class Element {
 constructor(name){this.name=name;this.dataset={};this.hidden=false;this.disabled=false;this.listeners={};this.attributes={};this.textContent='';this.value='';}
 setAttribute(name,value){this.attributes[name]=value;}
 addEventListener(name,cb){this.listeners[name]=cb;}
 before(...els){this.beforeNodes=els;}
}
function run({editable=false,protectedSource=false,edits=false,multiple=false,confirm=false}={}){
 const top=new Element('top'),slider=new Element('slider'),quick=new Element('quick'),hint=new Element('hint');
 top.querySelector=s=>s==='.se454-slider-row'?slider:null;
 const panel=new Element('panel');panel.querySelector=s=>({
  '#se454InsetTopBar':top,
  '#se445ShapeQuick':quick,
  '#se454Hint':hint
 })[s]||null;
 const state={selection:{partId:'cube',objectCount:multiple?2:1,mode:editable?'face':'mesh',faceIds:[],ids:[]},
  preview:{active:false},convert:{available:!editable&&!protectedSource,
   reason:protectedSource?'This mesh has authored texture and rig data. Keep source intact.':
   edits?'Bake saved vertex edits into editable topology.':'Creates welded editable topology.'}};
 const events=[],api={
  inspect:()=>state,
  convert:()=>{
   events.push('convert');
   state.convert={available:false,reason:'Already editable topology'};
   state.selection.mode='face';
   return {ok:true,id:'cube'};
  },
  setComponentMode:mode=>{events.push('mode:'+mode);state.selection.mode=mode;return {ok:true};}
 };
 let stage='rim',allowed=confirm;
 const window={
  confirm:()=>{events.push('confirm');return allowed;},
  addEventListener:()=>{},
  SWYRL_ENGINE_INSET_TOP_STEPS_454:{inspect:()=>({step:stage})}
 };
 const doc={createElement:name=>new Element(name)};
 const context=vm.createContext({se430BeginnerInstall:()=>true,
  se430BeginnerRefresh:()=>true,se430BeginnerAPI:()=>api,
  se430BeginnerResult:x=>events.push(x?.ok?'native result ok':'native result fail'),
  window,document:doc,queueMicrotask:f=>f()});
 vm.runInContext(js,context);
 assert(context.se430BeginnerInstall(panel));
 const addon=window.SWYRL_ENGINE_GUIDED_CONVERSION_456;
 assert.equal(addon.inspect().installed,true);
 const [button,note]=slider.beforeNodes;
 assert.equal(button.id,'se456MakeEditable');
 return {addon,button,note,state,events,window,stage:x=>{stage=x;addon.refresh();},allow:()=>{allowed=true}};
}
let s=run();
assert.equal(s.button.hidden,false,'Single plain cube offers conversion BEFORE any face is selected');
assert.equal(s.button.disabled,false,'Convert button must not depend on faceIds');
assert.match(s.button.textContent,/Make Editable/);
assert.equal(s.addon.convert().ok,true);
assert.deepEqual(s.events,['convert','native result ok'],'Exactly one native conversion; no extra geometry');
assert.equal(s.state.selection.mode,'face');
assert.equal(s.button.hidden,true,'No duplicate button after conversion');
assert.match(s.note.textContent,/Tap its square face/,'Continue by tapping face');
assert.equal(s.state.selection.faceIds.length,0,'No invented face selection');
s.stage('depth');assert.equal(s.button.hidden,true,'Depth stage cannot reconvert');
s=run({edits:true});
assert.match(s.button.textContent,/Bake Edits/);
assert.equal(s.addon.convert().ok,false);
assert.deepEqual(s.events,['confirm'],'Refused bake does not edit geometry');
s.allow();assert.equal(s.addon.convert().ok,true);
assert.deepEqual(s.events,['confirm','confirm','convert','native result ok']);
s=run({protectedSource:true});assert.equal(s.button.hidden,true);
assert.match(s.note.textContent,/authored/);
assert.equal(s.events.length,0);
s=run({multiple:true});assert.equal(s.button.hidden,true,'Multi object selection blocked');
s=run({editable:true});assert.equal(s.button.hidden,true,'Already editable mesh cannot reconvert');

if(process.argv[2]){
 const html=fs.readFileSync(process.argv[2],'utf8');
 for(const token of ['SWYRL_ENGINE_DEPLOY_MARKER: V11_456_GUIDED_PRIMITIVE_CONVERSION',
  "window.SWRLZ_FORGE_BUILD={version:'v11.456'",
  'SE456_GUIDED_PRIMITIVE_CONVERSION_START',
  'SE456_GUIDED_PRIMITIVE_CONVERSION_STYLES_START',
  'SE454_INSET_TOP_STEPS_START',
  'SE446_PLANAR_FACE_TAP_START',
  'SE430_MODEL_WORKSHOP_BRIDGE_START']){
  assert(html.includes(token),'Bundled release missing '+token);
 }
}
console.log('SE456_GUIDED_PRIMITIVE_CONVERSION_PASS: visible before face, one native convert, Undo native, edits consent, protected/multi source refusal, rim-stage only');
