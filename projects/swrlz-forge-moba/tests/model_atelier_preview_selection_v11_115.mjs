// §E v11.115 regression: preview proxy selection, lifecycle and move guard.
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const script=fs.readFileSync(
 'projects/swrlz-forge-moba/runtime/model_atelier_precision_preview_guard_v11_115.js','utf8');
const viewport={getBoundingClientRect:()=>({left:0,top:0,width:800,height:700})};
const cam=new THREE.PerspectiveCamera(50,800/700,.1,100);
cam.position.set(0,0,5);cam.lookAt(0,0,0);cam.updateMatrixWorld(true);
const world=new THREE.Scene();
let nativeNudges=0,nativeDowns=0,renders=0,checkpoints=0,clears=0,
 selected=null,syncCalls=0,lastStatus='',previewClicks=0;
const listeners={};
const label={textContent:''};
const elements={
 modelAtelierBoreInfo:label,
 modelAtelierParts:{addEventListener:()=>{}},
 modelAtelierBorePreview:{addEventListener:(_,f)=>{listeners.preview=f;}}
};
let part={id:'source',kind:'sphere'};
const ctx={
 THREE,world,camera:cam,renderer:{domElement:viewport},selection:'source',
 document:{getElementById:id=>elements[id]||null,
  addEventListener:(type,fn)=>{(listeners[type]??=[]).push(fn)}},
 modelRoot:new THREE.Group(),point:e=>({x:(e.clientX/800)*2-1,y:1-(e.clientY/700)*2}),
 status:s=>{lastStatus=s},
 atelierPrecisionGizmoQueue:()=>{syncCalls++},
 atelierPrecisionGizmoHit:()=>false,
 atelierSculptArmed:false,atelierPrecisionGizmoDrag:null,
 atelierMeshGizmo:null,partById:id=>id===part.id?part:null,
 atelierPrecisionCircleClear:()=>{const d=ctx.atelierPrecisionCircleDraft;
  if(!d)return;
  ctx.atelierPrecisionCircleDraft=null;
  d.ghost.parent.remove(d.ghost);d.sourceMesh.visible=true;clears++;},
 atelierPrecisionCircleDraft:null,
 renderParts:()=>{renders++},
 select:id=>{selected=id;ctx.renderParts();},
 atelierMeshGizmoDown:()=>{nativeDowns++;return false;},
 atelierMeshNudge:()=>{nativeNudges++},
 checkpoint:()=>{checkpoints++}
};
vm.createContext(ctx);
vm.runInContext(script,ctx);
ctx.atelierPrecisionGuardInstall();
const saved=()=>({
 originalId:'source',
 sourceMesh:new THREE.Mesh(new THREE.SphereGeometry(.5,16,12)),
 ghost:new THREE.Mesh(new THREE.SphereGeometry(.5,16,12)),
});
const activate=()=>{const d=saved();
 d.ghost.position.x=-1.4;d.sourceMesh.visible=false;
 world.add(d.ghost);ctx.modelRoot.add(d.sourceMesh);
 ctx.atelierPrecisionCircleDraft=d;return d;};
activate();
ctx.atelierMeshNudge(1);
if(nativeNudges!==0||!ctx.atelierPrecisionCircleDraft||
 !lastStatus.includes('PREVIEW'))throw Error('Mesh quick-strip moved hidden sphere during active preview');
console.log('MESH_NUDGE_BLOCKED_WITH_PREVIEW_PASS');
// Fake transform handle hit: actual Raycaster against source center.
const gizmo=new THREE.Group(),handle=new THREE.Mesh(new THREE.SphereGeometry(.17,12,8));
handle.userData.meshGizmoAxis='x';gizmo.add(handle);world.add(gizmo);
ctx.atelierMeshGizmo=gizmo;
let blocked=ctx.atelierMeshGizmoDown({button:0,clientX:400,clientY:350,preventDefault:()=>{}});
if(!blocked||nativeDowns!==0||clears!==0)throw Error('Native mesh gizmo started while cut preview active');
console.log('MESH_TRANSFORM_HANDLE_BLOCKED_WITH_PREVIEW_PASS');
world.remove(gizmo);ctx.atelierMeshGizmo=null;
// Object click must reselect the source, remove orphan preview and not Apply.
const x=cam.position.clone(),proj=new THREE.Vector3(-1.4,0,0).project(cam);
const xy={x:(proj.x+1)*400,y:(1-proj.y)*350};
const tapped={target:viewport,button:0,isPrimary:true,pointerId:3,
 clientX:xy.x,clientY:xy.y,preventDefault:()=>{},stopImmediatePropagation:()=>{}};
ctx.atelierPrecisionGuardPointerDown(tapped);
ctx.atelierPrecisionGuardPointerUp(tapped);
if(selected!=='source'||clears!==1||ctx.atelierPrecisionCircleDraft||checkpoints)
 throw Error('Tapping the unselectable ghost did not restore editable selection safely');
console.log('GHOST_TAP_RESELECTS_EDITABLE_SOURCE_PASS');
activate();
ctx.renderParts();
if(clears!==2||renders<2||ctx.atelierPrecisionCircleDraft)
 throw Error('Model render/selection left a stranded preview beside moved sphere');
if(checkpoints!==0)throw Error('Preview cleanup mutated native Undo history');
console.log('RENDER_INVALIDATES_STALE_GHOST_NO_CHECKPOINT_PASS');
