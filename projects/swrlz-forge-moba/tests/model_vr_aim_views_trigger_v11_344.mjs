#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION,'169');
const helper=fs.readFileSync(ROOT+'/runtime/model_vr_aim_views_v11_344.js','utf8');
const ui=fs.readFileSync(ROOT+'/runtime/model_studio_vr_ui_v11_344.js','utf8');
const bridge=fs.readFileSync(ROOT+'/runtime/model_vr_bridge_v11_344.js','utf8');
new vm.Script(helper);new vm.Script(ui);new vm.Script(bridge);
const stored=new Map(),events=[];
const a={ray:{quaternion:new THREE.Quaternion()},input:{handedness:'right'},index:1,nextHoverAt:123,hit:{id:'part'},hoverKey:'part'};
const state={aim:{left:{yaw:0,pitch:0},right:{yaw:0,pitch:0}},aimHand:'right',
 controllers:[a],forward:new THREE.Vector3(0,0,-1),gesture:null,
 yaw:0,pitch:0,viewMode:'orbit',};
const context={THREE,se340XR:state,se340Notice:x=>events.push(x),
 localStorage:{getItem:k=>stored.get(k)||null,setItem:(k,v)=>stored.set(k,v)}};
vm.createContext(context);
vm.runInContext(helper+String.raw`
this.api={read:se344ReadAim,quaternion:se344AimQuat,view:se344SetView,aim:se344AimAction};`,context);
assert.equal(context.api.quaternion(a).angleTo(new THREE.Quaternion()),0);
assert(context.api.aim('aim-yaw-plus'));
assert.equal(state.aim.right.yaw,2);
assert.equal(state.aim.left.yaw,0,'calibration must be per-hand');
assert(a.ray.quaternion.angleTo(new THREE.Quaternion())>0,'visible ray must match corrected direction');
assert.equal(a.nextHoverAt,0,'calibration immediately invalidates stale hover');
assert.equal(context.api.read().right.yaw,2,'aim correction persists in the local browser');
assert(context.api.aim('aim-hand'));assert.equal(state.aimHand,'left');
assert(context.api.aim('aim-pitch-minus'));assert.equal(state.aim.left.pitch,-2);
assert.equal(context.api.read().left.pitch,-2);
assert(context.api.aim('aim-reset-all'));assert.equal(state.aim.left.pitch,0);
assert.equal(state.aim.right.yaw,0);
for(const [name,yaw,pitch] of [
 ['front',0,0],['back',Math.PI,0],['left',-Math.PI/2,0],
 ['right',Math.PI/2,0],['top',0,-Math.PI/2+.035],['bottom',0,Math.PI/2-.035],
 ['iso',-Math.PI/4,-.62]
]){
 assert(context.api.view(name));assert(Math.abs(state.yaw-yaw)<.00001,name+' yaw');
 assert(Math.abs(state.pitch-pitch)<.00001,name+' pitch');
}
state.gesture={};assert.equal(context.api.view('front'),false,'active grip cannot recenter');
assert(ui.includes('const slots=[];let currentPage='));
assert(ui.includes("'aim-yaw-minus','Yaw -2°'"));
assert(ui.includes("'view-top','Top'"));
assert(ui.includes("page:'tools'"));
assert(bridge.includes('if (selection === id)'));
const patch=fs.readFileSync(ROOT+'/patches/v11_344_model_vr_aim_views_trigger.py','utf8');
assert(patch.includes("se340Hit(record,false);record.hit=hit;"));
assert(patch.includes("const hit=se340Hit(record,false);if(!hit?.id||hit.ui)return false;"));
assert(patch.includes("record.ray.quaternion.copy(correction)"));
console.log('MODEL_VR_344_AIM_VIEWS_NO_TRIGGER_STALL_PASS');
