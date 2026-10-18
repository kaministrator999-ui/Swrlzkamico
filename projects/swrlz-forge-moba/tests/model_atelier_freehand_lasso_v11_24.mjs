import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const root=new URL('../',import.meta.url);
const file=n=>fs.readFileSync(new URL(n,root),'utf8');
const lasso=file('runtime/model_atelier_surface_lasso_v11_22.js');
const viewport=file('runtime/model_atelier_viewport_v11_21.js');
const patch=file('patches/v11_21_vertex_sphere_brush_preview.py');
assert(patch.includes('id="modelAtelierLassoStartFreehand"'),'Freehand control must be installed in actual editor');
assert(patch.includes('atelierLassoPointerCancel(e)'),'Canvas pointercancel must reset the draft');
assert(viewport.includes('if(atelierLassoFreehand){atelierLassoFreehand=null;atelierLassoPending=[];'),
  'Second-finger camera gesture must discard active trace');

const context=vm.createContext({console});
vm.runInContext(lasso,context,{filename:'model_atelier_surface_lasso_v11_22.js'});
vm.runInContext(`
  modelRoot={children:[{isMesh:true,userData:{atelierId:'head'}}]};
  selection='head';renderer={domElement:{setPointerCapture(){}}};
  atelierLassoPointFromEvent=(e)=>({point:[e.clientX*.002,e.clientY*.002,0],tri:1,bary:[.2,.3,.5]});
  atelierLassoOverlayRefresh=()=>{};
  atelierLassoRefresh=()=>{};
  status=()=>{};pressed={};
  atelierLassoArm='freehand';
`,context);
const e=(x,y=4,id=11)=>({button:0,clientX:x,clientY:y,pointerId:id});
const invoke=(func,arg)=>{context.event=arg;return vm.runInContext(func+'(event)',context)};
assert.equal(invoke('atelierLassoPointerDown',e(0)),true);
assert.equal(vm.runInContext('atelierLassoPending.length',context),1);
assert.equal(invoke('atelierLassoPointerMove',e(2)),true,'Sub-seven-pixel move is safely consumed');
assert.equal(vm.runInContext('atelierLassoPending.length',context),1);
for(let i=1;i<=80;i++)assert.equal(invoke('atelierLassoPointerMove',e(i*10,Math.sin(i/5)*30)),true);
assert.equal(invoke('atelierLassoPointerUp',e(810)),true);
assert.equal(vm.runInContext('atelierLassoPending.length',context),32,
  'Freehand capture must remain bounded to the 32-pin saved schema');
assert.equal(vm.runInContext('atelierLassoFreehand',context),null);
assert.equal(vm.runInContext('atelierLassoArm',context),null);
assert.equal(invoke('atelierLassoPointerMove',e(820)),false,'Unarmed pointer must return to normal orbit');
assert.equal(vm.runInContext('atelierLassoPending.every(p=>p.tri===1&&p.bary.length===3)',context),true);

vm.runInContext("atelierLassoArm='freehand'",context);
assert.equal(invoke('atelierLassoPointerDown',e(0,1,12)),true);
assert.equal(invoke('atelierLassoPointerCancel',e(5,4,12)),true);
assert.equal(vm.runInContext('atelierLassoPending.length',context),0);
assert.equal(vm.runInContext('atelierLassoFreehand',context),null);

// When a draw starts off the mesh it must consume the tap, not switch selection.
vm.runInContext("atelierLassoPointFromEvent=()=>null;atelierLassoArm='freehand'",context);
assert.equal(invoke('atelierLassoPointerDown',e(0,1,13)),true);
assert.equal(vm.runInContext('atelierLassoFreehand',context),null);

console.log('V1124_FREEHAND_LASSO_SURFACE_PINS_TOUCH_CAP_CANCEL_PASS');
