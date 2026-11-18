#!/usr/bin/env node
/* Three.js r169 interaction assertions for v11.515 native spatial XR changes.
   Does not count emulator checks as Quest headset acceptance. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {pathToFileURL,fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION,'169');
let disconnects=0,priorOrbit=0,remembers=0,makes=0,draws=0,loads=0;
const camera=new THREE.PerspectiveCamera(65,1,.015,60);
const scene=new THREE.Scene(),ui=new THREE.Group(),base=new THREE.Vector3(-.50,1.30,-1.03);
const state={session:{},ui:{root:ui},scene,paletteVisible:true,frameCount:1,
 se372MenuBase:{position:base.clone(),quaternion:new THREE.Quaternion()},
 lastViewer:{position:new THREE.Vector3(0,1.3,0)},gesture:null,
 yaw:0,pitch:0,controllers:[]};
ui.position.copy(base);scene.add(ui);
function fakeCanvas(){return {width:512,height:144,getContext:()=>({
 clearRect(){},beginPath(){},roundRect(){},rect(){},fill(){},stroke(){},
 fillText(){},measureText:(s)=>({width:String(s).length*15})
 })};}
const keyset={left:[['LT','trigger'],['LG','squeeze'],['LS','thumbstick'],['X','x_button'],['Y','y_button']],
 right:[['RT','trigger'],['RG','squeeze'],['RS','thumbstick'],['A','a_button'],['B','b_button']]};
const moduleSrc=fs.readFileSync(path.join(root,'runtime/model_vr_spatial_polish_v11_515.js'),'utf8');
const profiles=new Map();
const sandbox={
 THREE,console,
 window:{},
 se340XR:state,se340VisibleSession:()=>true,
 se362Keys:keyset,
 se361ControllerCache:profiles,
 se362PartCenter:part=>new THREE.Vector3(.06,1.85,.12),
 se362FallbackPoint:()=>new THREE.Vector3(.01,.01,.01),
 se362CleanLabel:(action)=>action,
 se362DrawHint:(hint,title)=>{hint.text=title;draws++;},
 se362MakeVisual:record=>{
  makes++;
  const root=new THREE.Group(),hints=new Map(),side=record.input.handedness;
  record.grip.add(root);
  for(const [key] of keyset[side]){
   const mesh=new THREE.Mesh(new THREE.PlaneGeometry(.094,.0264),new THREE.MeshBasicMaterial());
   const hint={key,mesh,canvas:fakeCanvas(),texture:{needsUpdate:false},material:mesh.material};
   hints.set(key,hint);root.add(mesh);
  }
  const visual={root,hints,side};record.se362Visual=visual;return visual;
 },
 se362LoadVisual:async(record,visual)=>{loads++;visual.ready=true;},
 se362Frame:s=>{
  for(const record of s.controllers){
   for(const h of record.se362Visual.hints.values()){
    sandbox.se362DrawHint(h,'Select part',!!s.inputSample?.buttons?.[h.key]?.physical,false);
   }
  }
 },
 se362ControllerDisconnected:record=>{disconnects++;record.se362Visual?.root?.removeFromParent();record.se362Visual=null;},
 se372MenuOrbit:()=>{priorOrbit++;},
 se372MenuDragFinish:()=>{throw Error('Old orbit-based drag commit must not be used');},
 se372MenuRemember:()=>{remembers++}
};
const ctx=vm.createContext(sandbox);
vm.runInContext(moduleSrc,ctx);
const api=sandbox.window.SWYRL_ENGINE_VR_SPATIAL_POLISH_515;
assert(api?.inspect);
const before=base.clone();
for(let i=0;i<13;i++){
 state.yaw+=.14;state.pitch+=.04;
 state.lastViewer.position.set(.5,1.6+.01*i,.3);
 vm.runInContext('se372MenuOrbit()',ctx);
 assert(ui.position.distanceToSquared(before)<1e-12,'orbit and headset change must not translate menu anchor');
 assert(ui.getWorldDirection(new THREE.Vector3()).dot(state.lastViewer.position.clone().sub(ui.position).normalize())>.99,
  'native menu front faces current viewer without moving');
}
assert.equal(priorOrbit,0,'broken orbit-based menu adapter is bypassed');
const moved=new THREE.Vector3(-.3,1.2,-.75);
ui.position.copy(moved);
vm.runInContext('se372MenuDragFinish({},true)',ctx);
assert(state.se372MenuBase.position.distanceToSquared(moved)<1e-12,'user Grip-drag saves actual world position');
assert.equal(remembers,1,'native saved menu placement path used');
vm.runInContext('se372MenuOrbit()',ctx);
assert(ui.position.distanceToSquared(moved)<1e-12,'post-drag orbit must preserve new position');
const records=[];
for(const side of ['left','right']){
 const grip=new THREE.Group();scene.add(grip);
 const record={input:{handedness:side},grip,gripTracked:true};
 state.controllers.push(record);records.push(record);
 const visual=sandbox.se362MakeVisual(record);
 assert.equal(visual.se515Parts.length,10,'five hardware button leaders plus five glow cues');
 for(const [key] of keyset[side]){
  const h=visual.hints.get(key);
  assert(Math.abs(h.mesh.geometry.parameters.width-.070)<1e-12,'label width reduced');
  assert(h.leader&&h.glow,'matching thin leader and button glow on each actuator');
  assert.equal(h.leader.material.color.getHex(),h.glow.material.color.getHex(),'label line and button glow share same color');
  assert(h.leader.geometry.attributes.position.count===2,'leader points exactly button to label');
 }
}
state.inputSample={buttons:{LT:{physical:true},RT:{physical:true}}};
sandbox.se362Frame(state);
for(const record of records){
 const key=record.input.handedness==='left'?'LT':'RT',hint=record.se362Visual.hints.get(key);
 assert(hint.mesh.visible&&hint.leader.visible&&hint.glow.visible,'visible profile label shows linked line and glow');
 assert.equal(hint.glow.scale.x,1.38,'press increases button glow');
 assert.equal(hint.text,'Select part','native profile text still owns labels');
}
const record=records[0],visual=record.se362Visual;
profiles.set('left',{parts:[{key:'trigger',mesh:{positions:[0,0,0,1,0,0,0,1,0]}}]});
await sandbox.se362LoadVisual(record,visual);
assert.equal(loads,1,'underlying controller model loading preserved');
const h=visual.hints.get('LT');
const at=new THREE.Vector3(.06,1.85,.12).sub(new THREE.Vector3(0,1.79,0)).multiplyScalar(.09);
assert(h.buttonAnchor.distanceToSquared(at)<1e-10,'model source button center selected as leader anchor');
assert(h.leader.geometry.attributes.position.count===2);
sandbox.se362ControllerDisconnected(record);
assert.equal(disconnects,1,'native controller disconnect lifecycle preserved');
assert.equal(record.se362Visual,null);
assert.equal(api.inspect().activeControllerGuides,10);
console.log('SE515_SPATIAL_MENU_CONTROLLERS_PASS',JSON.stringify({
 anchorStable:true,faceHeadset:true,dragSaved:true,
 smallerLabels:true,preciseSourceButtonCenters:true,
 colorMatchedLineAndGlow:true,triggerPressFeedback:true,
 controllerCleanup:true,guides:10,draws,makes,remembers
}));
