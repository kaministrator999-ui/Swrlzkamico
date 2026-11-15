#!/usr/bin/env node
// §E v11.450: actual Inset shortcut behavior, optional safe bake, native Undo,
// and the 4-column desktop dock resize handles. Tests built release HTML.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const html=fs.readFileSync(process.argv[2],'utf8');
for(const marker of ['SE448_INSET_ACTION_ROUTING_START','SE448_DOCK_GRIP_ALIGNMENT_START',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_450_CAMERA_INSET_PREVIEW',
 'se448ShapeQuickActivate(faceQuick,operation);',"const bakedVertexEdits=!!p.sculptVertexEdits?.length",
 'if(bakedVertexEdits)atelierSculptApply(source,p);','delete p.sculptVertexEdits;']){
 assert(html.includes(marker),'Missing v11.450 source binding '+marker);
}
const a=html.indexOf('/* SE448_INSET_ACTION_ROUTING_START */'),b=html.indexOf('/* SE448_INSET_ACTION_ROUTING_END */',a);
assert(a>=0&&b>a,'Missing quick command code');
const quick=html.slice(a,b+'/* SE448_INSET_ACTION_ROUTING_END */'.length);
function scenario({selected=true,hasPreview=false,hasFace=true,needsBake=true,confirmed=true,convertAllowed=true,operationAllowed=true}={}){
 const events=[],message=[];
 let state={
  selection:{partId:selected?'cube':null,objectCount:selected?1:0,mode:hasFace?'face':'mesh',ids:hasFace?[7,8]:[],faceIds:hasFace&&!convertAllowed?[7,8]:[]},
  preview:{active:hasPreview},
  convert:{available:convertAllowed,reason:needsBake?'Bake saved vertex edits into welded editable topology.':'Creates welded editable topology.'},
  operations:{inset:{available:!convertAllowed&&operationAllowed,reason:operationAllowed?'Select a connected region.':'Protected paint or rig geometry.'}}
 };
 const api={
  inspect:()=>state,
  setComponentMode:mode=>{events.push(['mode',mode]);state.selection.mode=mode;return {ok:true};},
  convert:()=>{events.push(['convert']);state.convert={available:false,reason:'already topology'};state.selection.ids=[];state.selection.faceIds=[];state.operations.inset={available:operationAllowed,reason:'Create inner face'};return {ok:true,changed:true};},
  selectRegion:(seed,id)=>{events.push(['region',seed,id]);state.selection.ids=[7,8];state.selection.faceIds=[7,8];return {ok:true,faceIds:[7,8]};},
  preview:(operation,params)=>{events.push(['preview',operation,params]);return {ok:true,changed:false};}
 };
 const hint={textContent:''},faceQuick={querySelector:()=>hint};
 const sandbox=vm.createContext({
  window:{confirm:msg=>{events.push(['confirm',msg]);return confirmed;}},
  document:{getElementById:id=>id==='modelAtelierWorkshopAmount'?{value:'0.2'}:null},
  se430BeginnerAPI:()=>api,
  se430BeginnerNavigate:op=>events.push(['navigate',op]),
  se450ArmFacePreview:(op,part)=>events.push(['arm',op,part]),
  se430BeginnerWrite:(target,text)=>{target.textContent=text;message.push(text);},
  se430BeginnerQueue:()=>events.push(['refresh'])
 });
 vm.runInContext(quick+'\nthis.activate=se448ShapeQuickActivate;',sandbox);
 const result=sandbox.activate(faceQuick,'inset');
 return {events,message,result,hint:hint.textContent};
}
let r=scenario();
assert.equal(r.result.ok,true,'Edited cube should open Inset preview');
assert.deepEqual(r.events.map(x=>x[0]).filter(x=>x!=='refresh'),['navigate','confirm','convert','region','preview']);
assert.equal(r.events.find(x=>x[0]==='region')[1],7,'Face seed must survive conversion');
assert.equal(r.events.find(x=>x[0]==='region')[2],'cube');
assert.equal(r.events.find(x=>x[0]==='preview')[2].amount,.2);
assert.match(r.hint,/preview ready/i);
r=scenario({confirmed:false});
assert.equal(r.result.ok,false);assert(!r.events.some(x=>x[0]==='convert'),'Decline must not mutate');
r=scenario({needsBake:false});
assert.equal(r.result.ok,true);assert(!r.events.some(x=>x[0]==='confirm'),'Plain cube needs no extra confirmation');
r=scenario({hasFace:false});
assert.equal(r.result.ok,false);assert(!r.events.some(x=>x[0]==='convert'||x[0]==='preview'),'No face means no baked geometry');
r=scenario({hasPreview:true});
assert.equal(r.result.ok,false);assert(!r.events.some(x=>x[0]==='preview'),'Existing preview cannot be overridden');
r=scenario({convertAllowed:false,operationAllowed:false});
assert.equal(r.result.ok,false);assert.match(r.hint,/Protected paint or rig/);
assert(!r.events.some(x=>x[0]==='convert'||x[0]==='preview'),'Protected content cannot be converted');

// Test native transaction itself, not merely string presence.
const bridgeStart=html.indexOf('/* SE430_MODEL_WORKSHOP_BRIDGE_START */'),
 bridgeEnd=html.indexOf('/* SE430_MODEL_WORKSHOP_BRIDGE_END */',bridgeStart);
assert(bridgeStart>=0&&bridgeEnd>bridgeStart);
const bridge=html.slice(bridgeStart,bridgeEnd);
const first=bridge.indexOf(' function convert(){'),last=bridge.indexOf(' function create(',first);
assert(first>=0&&last>first,'Native convert function missing');
const convertFn=bridge.slice(first,last);
function convertNative({edits=true}={}){
 const part={id:'cube',name:'Cube',kind:'box',sculptVertexEdits:edits?[{indices:[0,1],moves:[[.1,0,0],[.1,0,0]],resolution:[0,0]}]:undefined};
 let snapshots=[],bakes=0,sourceSeen=null,signals=0;
 const api=vm.createContext({
  active:null,
  fail:reason=>({ok:false,reason}),
  busy:()=>false,
  selection:'cube',
  partById:()=>part,
  availability:()=>({convert:{available:true}}),
  atelierCourierBaseGeometry:()=>({positions:[[0,0,0]],dispose(){}}),
  atelierSculptApply:geo=>{bakes++;geo.positions[0][0]=.1;return geo;},
  se430MeshOps:{convert:geo=>{sourceSeen=geo.positions[0][0];return {ok:true,data:{positions:[geo.positions[0][0],1,2],uvs:[0,0,1,1],indices:[0,1,2]},stats:{facesAfter:1}};}},
  clone:value=>structuredClone(value),
  checkPart:p=>p.kind==='topologyMesh'&&p.sculptVertexEdits===undefined,
  checkpoint:()=>snapshots.push(structuredClone(part)),
  atelierComponentMode:'mesh',atelierComponentIds:[],atelierComponentPartId:null,atelierMeshIds:[],
  signalEdited:()=>signals++,
  refreshComponents:()=>{},
  publish:()=>{}
 });
 vm.runInContext(convertFn+'\nthis.runConvert=convert;',api);
 const result=api.runConvert();
 return {result,part,snapshots,bakes,sourceSeen,signals};
}
let t=convertNative();
assert.equal(t.result.ok,true);assert.equal(t.bakes,1,'Bake must run on rendered vertex edits');
assert.equal(t.sourceSeen,.1,'Topology converter must receive deformed geometry');
assert.equal(t.part.sculptVertexEdits,undefined,'Baked layers must not reapply');
assert.equal(t.part.topologyMesh.positions[0],.1);
assert.equal(t.snapshots.length,1,'One Undo checkpoint for conversion');
assert.equal(t.snapshots[0].sculptVertexEdits.length,1,'Undo stores original authored vertex edits');
assert.equal(t.signals,1);
t=convertNative({edits:false});
assert.equal(t.result.ok,true);assert.equal(t.bakes,0,'Plain conversion must stay unchanged');

// Splitter geometry: same DOM elements, placed as grid items at exact edges
// of grid column 1 (hierarchy) and 3 (tool rail), not outdated viewport pixels.
const startStyle=html.indexOf('/* SE448_DOCK_GRIP_ALIGNMENT_START */');
const endStyle=html.indexOf('/* SE448_DOCK_GRIP_ALIGNMENT_END */',startStyle);
assert(startStyle>=0&&endStyle>startStyle);
const style=html.slice(startStyle,endStyle);
for(const item of ['#se251-split-model-left','#se251-split-model-right','grid-column:1!important','grid-column:3!important',
 'grid-row:1!important','justify-self:end!important','position:relative!important','data-se320-inspector-collapsed=true',
 'data-se251-layout=compact','touch-action:none']){
 assert(style.includes(item),'Missing grid-aligned grip rule '+item);
}
assert(!/left:calc\(var\(--se251/.test(style),'Do not reintroduce stale absolute grip coordinates');
assert(html.includes('function dragResize(node,what,side,dir)'),'Native splitter event handler must survive');
console.log('SE448_INSET_DOCK_PASS: one tap preview, safe edited-cube Undo bake, protected assets, three-column boundaries');
