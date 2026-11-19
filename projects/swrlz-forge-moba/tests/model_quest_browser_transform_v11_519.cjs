#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),
 path=require('node:path'),vm=require('node:vm');
const code=fs.readFileSync(path.resolve(__dirname,'../runtime/model_quest_browser_transform_v11_519.js'),'utf8');
let quest=true,selected='sphere',gizmo=null,render=0,inspector=0,list=0;
const history=[],messages=[],bounds={type:'BoxHelper',visible:true},mesh={type:'Mesh',visible:true},
 wireframe={type:'LineSegments',visible:true};
const ui={children:[],append(node){this.children.push(node);node.isConnected=true;}};
const panel={hidden:false,querySelector:selector=>selector==='.atelier-viewport-controls'?ui:null};
const canvas={getBoundingClientRect:()=>({left:5,top:10,right:1005,bottom:610,width:1000,height:600})};
const world={traverse:callback=>[bounds,mesh,wireframe].forEach(callback)};
const snap={
 window:{},document:{createElement:()=>({isConnected:false,attributes:{},setAttribute(k,v){this.attributes[k]=v;},
  addEventListener(event,fn){this[event]=fn;},textContent:'',title:''})},
 renderer:{domElement:canvas},panel,world,
 selection:selected,atelierMeshAdding:false,atelierComponentMode:'mesh',
 atelierMeshDrag:null,atelierComponentDrag:null,
 se512QuestBrowser2D:()=>quest,se512QuestTapPick:e=>e.hit||null,
 partById:id=>id==='sphere'||id==='cone'?{id}:null,
 select:id=>{snap.selection=id;},atelierMeshSelected:id=>{},
 atelierMeshGizmoClear:()=>{gizmo=null;},refreshInspector:()=>{inspector++;},
 refreshList:()=>{list++;},renderParts:()=>{render++;},
 atelierMeshGizmoBuild:()=>{},open:()=>true,close:()=>{},
 pointerDown:e=>{if(e.gizmo)snap.atelierMeshDrag={pointerId:e.pointerId};},
 pointerMove:()=>{},pointerUp:e=>{snap.atelierMeshDrag=null;},
 status:t=>messages.push(t),queueMicrotask:fn=>fn(),
};
const ctx=vm.createContext(snap);
vm.runInContext(code,ctx);
const api=snap.window.SWYRL_ENGINE_QUEST_BROWSER_TRANSFORMS_519;
assert(api);
const e=(hit='sphere',x=320,y=350,extras={})=>({pointerId:8,clientX:x,clientY:y,
 button:0,target:canvas,isPrimary:true,hit,...extras});
const tap=(a,b=a)=>{vm.runInContext('pointerDown(EV)',Object.assign(ctx,{EV:a}));
 vm.runInContext('pointerUp(EV)',Object.assign(ctx,{EV:b}));};
tap(e());
assert.equal(snap.selection,null,'same visible mesh tap must deselect');
assert(messages.at(-1).includes('cleared'));
snap.selection='sphere';tap(e('cone'));
assert.equal(snap.selection,'sphere','different mesh remains controlled by native picker');
snap.selection='sphere';tap(e('sphere',315,350),e('sphere',400,350));
assert.equal(snap.selection,'sphere','drag must not deselect');
snap.selection='sphere';tap(e('sphere',315,350,{gizmo:true}),e('sphere',315,350,{gizmo:true}));
assert.equal(snap.selection,'sphere','gizmo Trigger must not toggle selected mesh');
assert.equal(api.inspect().boundsVisible,true);
api.toggleBounds();
assert.equal(bounds.visible,false,'native outline hidden');
assert.equal(mesh.visible,true,'authored geometry unaffected');
assert.equal(wireframe.visible,true,'mesh wireframe unaffected');
assert.equal(api.inspect().boundsVisible,false);
vm.runInContext('renderParts()',ctx);
assert.equal(bounds.visible,false,'visibility persists after scene rendering');
api.toggleBounds();
assert.equal(bounds.visible,true,'native outline shown again');
vm.runInContext('open()',ctx);
assert.equal(ui.children.length,1,'reuse existing 2D viewport toolbar; no duplicate UI');
assert.equal(ui.children[0].attributes['aria-pressed'],'true');
quest=false;snap.selection='sphere';tap(e('sphere'));
assert.equal(snap.selection,'sphere','desktop/immersive model handling unchanged');
assert.equal(history.length,0,'UI selection/visibility cannot create model Undo');
console.log('SE519_QUEST_BROWSER_TRANSFORMS_PASS',JSON.stringify({
 selectedTapDeselect:true,dragPreserved:true,gizmoPriority:true,
 boundsToggle:true,wireframeUnchanged:true,desktopUnaffected:true,
 renders:render,inspectorRefreshes:inspector,listRefreshes:list
}));
