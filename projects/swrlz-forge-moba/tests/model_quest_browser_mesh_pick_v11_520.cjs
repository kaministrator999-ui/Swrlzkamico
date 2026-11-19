#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(path.resolve(process.argv[2]),'utf8');
const section=(a,b)=>{const i=html.indexOf(a),j=html.indexOf(b,i);
 assert(i>0&&j>i,'Compiled Quest source missing '+a);return html.slice(i,j+b.length);};
const browser=section('/* SE520_QUEST_BROWSER_PICK_START','/* SE520_QUEST_BROWSER_PICK_END */');
const controls=section('/* SE519_QUEST_BROWSER_TRANSFORM_START','/* SE519_QUEST_BROWSER_TRANSFORM_END */');
assert(controls.includes('if(quest())outline.raycast=function(){};'),
 'regular Quest Browser helper must never intercept model geometry picking');
let quest=true,selection=null,cleared=0,captured=false;
const canvas={};
const ctx=vm.createContext({window:{},renderer:{domElement:canvas},pressed:null,selection,
 atelierMeshDrag:null,atelierComponentDrag:null,atelierMeshAdding:false,atelierComponentMode:'mesh',
 se512QuestBrowser2D:()=>quest,se512QuestTapPick:e=>e.hit||null,
 select:id=>{ctx.selection=id;},atelierMeshSelected:()=>{},atelierMeshGizmoClear:()=>{cleared++;},
 renderParts:()=>{},refreshInspector:()=>{},refreshList:()=>{},
 pointerUp:e=>{if(!captured)ctx.selection='boundary-helper';}});
vm.runInContext(browser,ctx);
const pointer=(hit,old,opts={})=>{
 ctx.selection=old;ctx.pressed={x:180,y:155,moved:!!opts.moved};
 captured=!!opts.gizmo;ctx.atelierMeshDrag=captured?{axis:'x'}:null;
 ctx.pointerUp({target:canvas,button:0,clientX:181,clientY:155,hit});
};
pointer('sphere',null);
assert.equal(ctx.selection,'sphere','selected mesh must override misleading bounding-helper hit');
pointer('sphere','sphere');
assert.equal(ctx.selection,null,'second same-mesh selection deselects even if legacy helper was hit');
assert(cleared>0,'native gizmo and selection outlines cleared on deselection');
pointer('sphere','sphere',{gizmo:true});
assert.equal(ctx.selection,'sphere','true gizmo drag cannot be stolen by surface picker');
pointer('sphere','sphere',{moved:true});
assert.equal(ctx.selection,'boundary-helper','actual pointer drag cannot be converted into a selection tap');
quest=false;pointer('sphere','sphere');
assert.equal(ctx.selection,'boundary-helper','desktop or immersive modes bypass Quest Browser adapter');
console.log('SE520_QUEST_BROWSER_MESH_PICK_PASS',JSON.stringify({
 helperExclusion:true,actualMeshPriority:true,sameMeshDeselect:true,gizmoCapturePriority:true,
 actualDragNotTapped:true,nonQuestUnaffected:true}));
