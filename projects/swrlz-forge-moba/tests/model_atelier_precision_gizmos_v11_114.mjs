// §E v11.114 native viewport pointer interaction regression.
// Standalone three.js camera and fake browser controls, no saved-model writes.
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const code=fs.readFileSync(
 'projects/swrlz-forge-moba/runtime/model_atelier_circle_gizmos_v11_114.js','utf8');
const values={
 modelAtelierBoreGizmoRadius:{getAttribute:()=> 'true'},
 modelAtelierBoreGizmoDepth:{getAttribute:()=> 'true'},
 modelAtelierBoreRadius:{value:'.12'},
 modelAtelierBoreDepth:{value:'.36'},
 modelAtelierBoreCap:{value:'.8'},
 modelAtelierBoreWhich:{value:'new'},
 modelAtelierBoreRelocate:{checked:false},
 modelAtelierBoreInfo:{textContent:''},
 modelAtelierBorePreview:{click:()=>{previewCalls++;}}
};
let previewCalls=0,savedCalls=0;
const canvas={getBoundingClientRect:()=>({left:0,top:0,width:700,height:900}),
 setPointerCapture:()=>{},releasePointerCapture:()=>{}};
const mesh=new THREE.Mesh(new THREE.SphereGeometry(1,24,12));
mesh.userData.atelierId='ball';mesh.updateMatrixWorld(true);
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(50,700/900,.1,100);
camera.position.set(0,0,5);camera.lookAt(0,0,0);camera.updateMatrixWorld(true);
const part={id:'ball',kind:'sphere'};
const ctx={
 THREE,console,document:{getElementById:id=>values[id]||null},
 world:scene,camera,renderer:{domElement:canvas},modelRoot:{children:[mesh]},
 orbit:{distance:5},selection:'ball',partById:id=>id==='ball'?part:null,
 atelierSculptHit:{partId:'ball',center:[0,0,1],axis:[0,0,1]},
 atelierSculptArmed:false,
 atelierPrecisionCircleDraft:null,
 atelierPrecisionCircleClear:()=>{},
 atelierHDDirty:false,
 checkpoint:()=>{savedCalls++;},
 requestAnimationFrame:fn=>{fn();return 0},
 atelierBoreCoordinates:()=>({x:0,y:0}),
 $m:()=>null
};
vm.createContext(ctx);vm.runInContext(code,ctx);
vm.runInContext('atelierPrecisionGizmoDraw()',ctx);
const project=(p)=>{
 const v=p.clone().project(camera);
 return {x:(v.x+1)*350,y:(1-v.y)*450};
};
const event=(x,y,id)=>({
 target:canvas,clientX:x,clientY:y,pointerId:id,
 button:0,isPrimary:true,pointerType:'touch',
 preventDefault:()=>{},stopImmediatePropagation:()=>{}
});
const state=name=>vm.runInContext(name,ctx);
let radiusPt=project(state('atelierPrecisionGizmoPick').radiusGrip);
let begin=event(radiusPt.x,radiusPt.y,1);
ctx.atelierPrecisionGizmoDown(begin);
if(!state('atelierPrecisionGizmoDrag')||state('atelierPrecisionGizmoDrag').mode!=='Radius')
 throw Error('Radius ring did not capture touch');
ctx.atelierPrecisionGizmoMove(event(radiusPt.x+55,radiusPt.y,1));
if(Number(values.modelAtelierBoreRadius.value)<=.12)
 throw Error('Outward radius drag did not grow the numeric field');
ctx.atelierPrecisionGizmoUp(event(radiusPt.x+55,radiusPt.y,1));
if(previewCalls!==1||savedCalls!==0)
 throw Error('Pointer release failed read-only preview contract');
console.log('GIZMO_RADIUS_DRAG_PASS',values.modelAtelierBoreRadius.value);
vm.runInContext('atelierPrecisionGizmoDraw()',ctx);
const depthPt=project(state('atelierPrecisionGizmoPick').depthGrip);
ctx.atelierPrecisionGizmoDown(event(depthPt.x,depthPt.y,2));
if(!state('atelierPrecisionGizmoDrag')||state('atelierPrecisionGizmoDrag').mode!=='Depth')
 throw Error('Camera-front depth handle did not capture touch');
ctx.atelierPrecisionGizmoMove(event(depthPt.x,depthPt.y+50,2));
if(Number(values.modelAtelierBoreDepth.value)<=.36)
 throw Error('Depth grip did not deepen straight-on');
ctx.atelierPrecisionGizmoUp(event(depthPt.x,depthPt.y+50,2));
if(previewCalls!==2||savedCalls!==0)
 throw Error('Depth drag called Apply or failed exact preview refresh');
console.log('GIZMO_DEPTH_DRAG_PASS',values.modelAtelierBoreDepth.value);
values.modelAtelierBoreGizmoRadius.getAttribute=()=> 'false';
values.modelAtelierBoreGizmoDepth.getAttribute=()=> 'false';
vm.runInContext('atelierPrecisionGizmoDraw()',ctx);
if(state('atelierPrecisionGizmoGroup')!==null||state('atelierPrecisionGizmoPick')!==null)
 throw Error('Toggle off did not remove editor-only gizmos');
console.log('SE_V11114_TOUCH_GIZMO_SYNC_AND_NONDESTRUCTIVE_PASS');
