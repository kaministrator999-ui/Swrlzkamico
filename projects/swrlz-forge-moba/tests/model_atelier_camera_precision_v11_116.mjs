// §E v11.116 regression: exercise actual assembled camera + precision event functions.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const compiled=fs.readFileSync('/tmp/se-v11116.mjs','utf8');
function fn(name){
 const token='function '+name+'(';
 const i=compiled.indexOf(token);
 assert.ok(i>=0,'missing function '+name);
 const b=compiled.indexOf('{',i);
 let depth=0,stop=-1;
 for(let j=b;j<compiled.length;j++){
  if(compiled[j]==='{')depth++;
  else if(compiled[j]==='}'&&!--depth){stop=j+1;break;}
 }
 assert.ok(stop>b,'unterminated '+name);
 return compiled.slice(i,stop);
}
const names=[
 'atelierCameraTouchMetrics',
 'atelierCameraPointerDown',
 'atelierCameraPointerUp',
 'atelierPrecisionGuardPointerUp'
];
const minStart=compiled.indexOf('const atelierCameraMinDistance=()=>{');
assert.ok(minStart>=0,'missing outside-camera clip bound');
const minEnd=compiled.indexOf('\n};',minStart);
assert.ok(minEnd>minStart,'missing zoom bound terminator');
const zoom=compiled.slice(minStart,minEnd+3);
let previews=0,selected=null,released=[],stopped=0,prevented=0;
const fields={
 modelAtelierBoreRadius:{value:'.145'},
 modelAtelierBorePreview:{click:()=>{previews++}},
 modelAtelierBoreInfo:{textContent:''}
};
const mesh={isMesh:true,userData:{atelierId:'ball'},
 geometry:{boundingSphere:{radius:1},computeBoundingSphere(){}},
 matrixWorld:{getMaxScaleOnAxis:()=>1},updateMatrixWorld(){}};
const canvas={getBoundingClientRect:()=>({left:0,top:0,width:600,height:900}),
 setPointerCapture(){},releasePointerCapture:id=>released.push(id)};
class Vector2{constructor(x,y){this.x=x;this.y=y;}}
class Raycaster{setFromCamera(){} intersectObject(){return [{}];}}
const c={
 console,Math,Map,Set,Number,THREE:{Vector2,Raycaster},
 renderer:{domElement:canvas},document:{getElementById:id=>fields[id]??null},
 camera:{},modelRoot:{children:[mesh]},selection:'ball',partById:id=>id==='ball'?{id}:null,
 status:()=>{},select:id=>{selected=id},atelierPrecisionGuardClear:()=>{},
 atelierPrecisionGuardActive:()=>true,
 atelierPrecisionGizmoEnabled:()=>true,
 atelierPrecisionGizmoQueue:()=>{},
 atelierSculptArmed:false,atelierViewportGizmoCancel:()=>{},
 atelierLassoOverlayRefresh:()=>{},atelierLassoRefresh:()=>{},
 renderParts:()=>{},
};
vm.createContext(c);
vm.runInContext(String.raw`
let atelierCameraTouches=new Map(),atelierCameraConsumedTouches=new Set();
let atelierCameraGesture=null,atelierCameraMousePan=null;
let atelierPrecisionGizmoDrag=null,atelierPrecisionGuardTap=null;
let atelierPrecisionCircleDraft=null,pressed=null,orbit={distance:3,yaw:.1,pitch:.2};
let atelierCameraInterior=false,atelierDetailTarget={};
let atelierSculptDrag=null,atelierLassoDrag=null,atelierLassoTempPin=null;
let atelierLassoFreehand=null,atelierLassoPending=[],atelierLassoArm=null;
\`,c);
vm.runInContext(zoom+'\n'+names.map(fn).join('\n'),c);
const get=expr=>vm.runInContext(expr,c);
const down=id=>({pointerId:id,pointerType:'touch',clientX:id===17?100:500,
 clientY:id===17?230:550,button:0,isPrimary:true});
const up=id=>({pointerId:id,pointerType:'touch',clientX:100,clientY:230,
 preventDefault:()=>{prevented++},stopImmediatePropagation:()=>{stopped++}});
assert.equal(get('atelierCameraMinDistance()'),2.55,'precision view clips sphere at zoom');
c.atelierPrecisionGizmoEnabled=()=>false;
c.atelierPrecisionGuardActive=()=>false;
assert.equal(get('atelierCameraMinDistance()'),.16,'normal free zoom lost');
c.atelierPrecisionGizmoEnabled=()=>true;
c.atelierPrecisionGuardActive=()=>true;
vm.runInContext(String.raw`
atelierPrecisionGizmoDrag={
 id:17,mode:'Radius',changed:true,startValue:.12,
 startX:100,startY:230,lastX:150,lastY:260
};\`,c);
assert.equal(get('atelierCameraPointerDown({pointerId:23,pointerType:"touch",button:0,clientX:500,clientY:550})'),true);
assert.equal(get('atelierPrecisionGizmoDrag'),null,'second finger kept editing radius');
assert.equal(fields.modelAtelierBoreRadius.value,'0.1200','second finger failed to restore uncommitted radius');
assert.equal(previews,1,'interrupted radius should rebuild old non-destructive preview');
assert.equal(get('atelierCameraTouches.size'),2,'pinch did not receive both pointers');
assert.equal(get('atelierCameraConsumedTouches.size'),2,'pinch IDs were not consumed');
assert.deepEqual(released,[17],'old editor pointer capture not released');
get('atelierCameraPointerUp({pointerId:23,pointerType:"touch"})');
assert.equal(get('atelierCameraTouches.size'),1,'camera still counted released pointer');
assert.equal(get('atelierCameraConsumedTouches.size'),0,'remaining orbit finger remained consumed');
assert.equal(get('pressed.moved'),true,'remaining orbit would accidentally click mesh');
get('atelierCameraPointerUp({pointerId:17,pointerType:"touch"})');
assert.equal(get('atelierCameraTouches.size'),0,'pinch cleanup retained phantom pointer');
vm.runInContext(String.raw`
atelierCameraTouches.set(44,{x:310,y:460});
atelierPrecisionGuardTap={id:44,x:310,y:460};
atelierPrecisionCircleDraft={ghost:{parent:{}},originalId:'ball'};\`,c);
get('atelierPrecisionGuardPointerUp')?.(up(44));
// V8 function bindings live in context and should resolve through vm as well.
assert.equal(get('atelierCameraTouches.size'),0,'preview tap stranded finger in camera map');
assert.equal(selected,'ball','preview tap failed to reselect editable source');
assert.equal(stopped,1,'preview click did not suppress duplicate native selection');
assert.equal(prevented,1);
assert.equal(get('pressed'),null,'preview tap retained orbit start');
console.log('SE_V11116_CAMERA_POINTER_GESTURE_AND_PREVIEW_OWNERSHIP_PASS');
