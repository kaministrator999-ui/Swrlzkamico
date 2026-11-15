#!/usr/bin/env node
// v11.450: actual component touch dispatch, responsive model dock geometry,
// and safe rebake of a source-indexed edited topology cube. No fake buttons.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
for(const m of [
 'SE449_MODEL_DOCK_TOUCH_LAYOUT_START','SE449_DOCK_SIZE_GUARD_START',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_451_GUIDED_FACE_WORKFLOW',
 "if(e.pointerType==='touch'&&atelierCameraPointerDown(e))",
 "atelierComponentMode!=='mesh'&&e.pointerType==='touch'&&atelierCameraPointerMove(e)",
 "se449ComponentPinchIds.delete(e.pointerId)"
])assert(html.includes(m),'Missing v11.450 model input or layout source '+m);
const slice=(start,end)=>{
 const a=html.indexOf(start),b=html.indexOf(end,a);
 assert(a>=0&&b>a,'Missing source fragment '+start);
 return html.slice(a,b+end.length);
};
const camera=slice('function atelierCameraTouchMetrics(){','function atelierViewportInstall(){').replace(/function atelierViewportInstall\(\)\{$/,'');
const component=slice('const se449ComponentPinchIds=new Set();','function atelierComponentSnapshot(){').replace(/function atelierComponentSnapshot\(\)\{$/,'');
const smooth=slice('/* SE447_FACE_CAMERA_ORBIT_START */','/* SE447_FACE_CAMERA_ORBIT_END */');
const frames=new Map();let seq=0,cameraUpdates=0,pans=0,picks=0;
const orbit={yaw:0,pitch:0,distance:8};
const saved={inverted:false};
const sandbox=vm.createContext({
 THREE:{MathUtils:{clamp:(v,min,max)=>Math.max(min,Math.min(max,v))}},
 orbit,se433CameraPrefs:saved,renderer:{domElement:{setPointerCapture:()=>{}}},
 atelierCameraTouches:new Map(),atelierCameraConsumedTouches:new Set(),
 atelierCameraGesture:null,atelierCameraMousePan:null,
 atelierCameraMinDistance:()=>.5,atelierCameraPanByPixels:()=>pans++,cameraUpdate:()=>cameraUpdates++,
 pressed:null,atelierViewportGizmoCancel:()=>{},atelierPrecisionGizmoDrag:null,atelierMeshDrag:null,
 atelierPrecisionGizmoCancel:()=>{},atelierMeshGizmoCancel:()=>{},atelierSculptDrag:null,
 atelierLassoDrag:null,atelierLassoFreehand:null,
 atelierComponentMode:'face',atelierComponentTool:'tap',atelierComponentMulti:false,
 atelierComponentGesture:null,atelierComponentDrag:null,
 atelierComponentGizmoDown:()=>false,atelierComponentGizmoMove:()=>true,atelierComponentGizmoUp:()=>true,
 atelierComponentChoose:()=>picks++,atelierComponentHit:()=>0,
 selection:'cube',se430ModelWorkshop:{selectRegion:()=>{picks++;return {ok:true,faceIds:[0,1]};}},
 atelierComponentRegionPick:()=>[],atelierComponentIds:[],
 atelierComponentMax:512,atelierComponentRefresh:()=>{},
 atelierMeshClamp:(v,a,b)=>Math.min(b,Math.max(a,v)),
 se446SelectPlanarFace:()=>{picks++;return true;},
 renderParts:()=>{},
 requestAnimationFrame:f=>{const n=++seq;frames.set(n,f);return n;},
 cancelAnimationFrame:id=>frames.delete(id)
});
vm.runInContext(smooth+'\n'+camera+'\n'+component+
 '\nthis.down=atelierComponentPointerDown;this.move=atelierComponentPointerMove;this.up=atelierComponentPointerUp;this.cancel=atelierComponentCancel;',sandbox);
const e=(id,x,y)=>({pointerId:id,pointerType:'touch',button:0,clientX:x,clientY:y,cancelable:true,preventDefault(){this.prevented=true;}});
assert.equal(sandbox.down(e(1,100,100)),true);
assert.equal(sandbox.atelierCameraTouches.size,1,'First Face pointer must reach touch tracker');
assert.equal(sandbox.down(e(2,200,100)),true);
assert.equal(sandbox.atelierCameraTouches.size,2,'Second Face pointer must reach touch tracker');
assert.equal(sandbox.atelierComponentGesture,null,'Second finger cancels pending Face orbit/selection');
const before=orbit.distance;
assert.equal(sandbox.move(e(2,260,100)),true);
assert(orbit.distance<before,'Separating fingers zooms closer while in Face mode');
assert(cameraUpdates>0,'Pinch should update native camera');
assert.equal(sandbox.move(e(1,100,110)),true);
assert(pans>0,'Two-finger drag reaches native pan');
assert.equal(sandbox.up(e(2,260,100)),true);
assert.equal(sandbox.up(e(1,100,110)),true);
assert.equal(sandbox.atelierCameraTouches.size,0);
assert.equal(sandbox.atelierCameraConsumedTouches.size,0);
assert.equal(picks,0,'Multitouch cannot inadvertently select a triangle');
assert.equal(frames.size,0,'No stale one-finger orbit frames');
assert.equal(sandbox.down(e(3,120,110)),true);
assert.equal(sandbox.up(e(3,120,110)),true);
assert.equal(picks,1,'Single-finger Face tap selection still works');
assert.equal(sandbox.down(e(4,120,110)),true);
assert.equal(sandbox.move(e(4,151,130)),true);
for(const f of frames.values())f();frames.clear();
assert(orbit.yaw!==0,'One-finger Face orbit must update before finger release');
sandbox.up(e(4,151,130));
assert.equal(picks,1,'Orbit swipe must not select a face');

// Dock fit and resize bounds are grounded in the body, native rail and actual
// persisted widths. The prior CSS's 19vw/30vw caps made handles unresponsive.
const size=slice('/* SE449_DOCK_SIZE_GUARD_START */','/* SE449_DOCK_SIZE_GUARD_END */');
let bodyWidth=832;
const panel={querySelector:()=>({getBoundingClientRect:()=>({width:bodyWidth})})};
const state={model:{left:205,right:305}};
const dock=vm.createContext({q:()=>panel,innerWidth:832,state,getComputedStyle:()=>({getPropertyValue:()=> '78px'})});
vm.runInContext(size+
 '\nthis.fit=se449ModelDockFit;this.max=se449ModelDockMax;this.metric=se449ModelDockMetrics;',dock);
assert.equal(dock.metric().budget,564);
assert.equal(dock.max('left'),259);
assert(dock.max('left')>state.model.left,'Left splitter has room to expand');
state.model.left=220;assert(dock.max('right')<350);
bodyWidth=700;dock.fit();
assert(state.model.left+state.model.right<=dock.metric().budget);
assert(state.model.left>=145&&state.model.right>=145);
const style=slice('/* SE449_MODEL_DOCK_TOUCH_LAYOUT_START */','/* SE449_MODEL_DOCK_TOUCH_LAYOUT_END */');
for(const rule of [
 'grid-column:1!important;grid-row:1!important',
 'grid-column:2!important;grid-row:1!important',
 'grid-column:3!important;grid-row:1!important',
 'grid-column:4!important;grid-row:1!important',
 'position:absolute!important','left:calc(var(--se320-left) - 7px)!important',
 'right:calc(var(--se320-right) - 7px)!important',
 'grid-auto-rows:0px!important','touch-action:none!important',
 'data-se251-layout=compact','data-se320-inspector-collapsed=true'
])assert(style.includes(rule),'Missing layout anchor '+rule);
assert(html.includes("node.addEventListener('pointerdown',e=>")&&html.includes('node.setPointerCapture?.(e.pointerId)'),
 'Existing splitter handlers must remain interactive');
assert(html.includes("const bound=what==='model'?se449ModelDockMax(side)"));

// Native edit-layer baking on a topologyMesh must neither strip UVs nor
// reinterpret face triangles. The source edit layer must remain in Undo.
const bridge=html.slice(html.indexOf('/* SE430_MODEL_WORKSHOP_BRIDGE_START */'),
 html.indexOf('/* SE430_MODEL_WORKSHOP_BRIDGE_END */'));
const begin=bridge.indexOf(' function convert(){'),end=bridge.indexOf(' function create(',begin);
assert(begin>=0&&end>begin);
const fn=bridge.slice(begin,end);
function rebake(resolution=[0,0]){
 const data={positions:[0,0,0,1,0,0,1,1,0,0,1,0],uvs:[0,0,1,0,1,1,0,1],indices:[0,1,2,0,2,3]};
 const part={id:'cube',kind:'topologyMesh',topologyMesh:structuredClone(data),
  sculptVertexEdits:[{indices:[0],delta:[.1,0,0],resolution}]};
 let snapshots=[],converted=0,rebuilds=0;
 const attr={count:4,getX:i=>[.1,1,1,0][i],getY:i=>[0,0,1,1][i],getZ:i=>0};
 const c=vm.createContext({
  active:null,selection:'cube',fail:r=>({ok:false,reason:r}),busy:()=>false,
  partById:()=>part,availability:()=>({convert:{available:true}}),
  atelierCourierBaseGeometry:()=>({getAttribute:()=>attr,dispose(){}}),
  atelierSculptApply:()=>{},
  atelierSculptResolution:()=>[0,0],
  se430MeshOps:{audit:d=>({ok:true}),convert:()=>{converted++;return {ok:false,reason:'must not remesh topology'}}},
  clone:x=>structuredClone(x),checkPart:p=>!p.sculptVertexEdits,
  checkpoint:()=>snapshots.push(structuredClone(part)),
  atelierComponentMode:'face',atelierComponentIds:[],atelierComponentPartId:null,atelierMeshIds:[],
  signalEdited:()=>rebuilds++,refreshComponents:()=>{},publish:()=>{}
 });
 vm.runInContext(fn+'\nthis.perform=convert;',c);
 return {result:c.perform(),part,data,snapshots,converted,rebuilds};
}
let bake=rebake();
assert.equal(bake.result.ok,true);
assert.equal(bake.part.topologyMesh.positions[0],.1,'Visible deformations should persist');
assert.deepEqual(bake.part.topologyMesh.uvs,bake.data.uvs,'UVs remain byte-identical');
assert.deepEqual(bake.part.topologyMesh.indices,bake.data.indices,'Triangles remain unchanged');
assert.equal(bake.part.sculptVertexEdits,undefined,'Baked edits cannot be applied twice');
assert.equal(bake.snapshots.length,1,'Exactly one Undo checkpoint');
assert.equal(bake.snapshots[0].sculptVertexEdits.length,1,'Original saved edits remain in Undo');
assert.equal(bake.converted,0,'Existing topology cannot be remeshed');
bake=rebake([10,10]);
assert.equal(bake.result.ok,false,'Invalid old resolution must be rejected');
assert.equal(bake.snapshots.length,0,'Invalid edits must not checkpoint or mutate source');
console.log('SE449_MODEL_TOUCH_LAYOUT_PASS: four-column hierarchy, live resizers, face pinch/pan/orbit, topology bake/Undo');
