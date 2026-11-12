// Actual native gizmo builders + Three r169 projection. Browser acceptance
// separately covers real touch events and native snapshot/history semantics.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2]||'/workspace/scratch/vr340-tools/node_modules/three/build/three.module.js')).href);
assert.equal(THREE.REVISION,'169');
const html=fs.readFileSync(process.argv[3]||'/workspace/scratch/model-vr340-package/index.html','utf8');
const code=fs.readFileSync(path.join(root,'runtime/model_gizmo_access_v11_431.js'),'utf8');
function nativeFunction(name){
 const start=html.indexOf('function '+name+'(');assert.ok(start>=0,name);const open=html.indexOf('{',start);let level=0;
 for(let i=open;i<html.length;i++){if(html[i]==='{')level++;else if(html[i]==='}'&&!--level)return html.slice(start,i+1);}
 throw Error('Unterminated '+name);
}
const listeners=new Map();
const canvas={getBoundingClientRect:()=>({left:20,top:40,width:390,height:450}),addEventListener:(type,callback)=>listeners.set(type,callback)};
let covered=false,borrowed=false;
const mesh=new THREE.Mesh(new THREE.BoxGeometry(.6,.6,.6),new THREE.MeshBasicMaterial());mesh.userData.atelierId='one';
const modelRoot=new THREE.Group();modelRoot.add(mesh);
const world=new THREE.Scene();world.add(modelRoot);
const camera=new THREE.PerspectiveCamera(44,390/450,.01,100);camera.position.set(3,2.3,5);camera.lookAt(0,0,0);camera.updateMatrixWorld(true);
const context={THREE,console,Math,Number,Object,Map,WeakMap,WeakSet,Array,
 renderer:{domElement:canvas},camera,world,modelRoot,selection:'one',orbit:{distance:6},
 atelierMeshGizmo:null,atelierMeshPivot:null,atelierComponentPivot:null,atelierMeshDrag:null,atelierComponentDrag:null,
 atelierMeshMode:'move',atelierMeshAxis:'x',atelierComponentMode:'mesh',atelierComponentIds:[0],
 atelierMeshAxes:{x:[1,0,0],y:[0,1,0],z:[0,0,1]},atelierMeshClamp:(n,a,b)=>Math.max(a,Math.min(b,n)),
 atelierPrecisionGizmoEnabled:()=>false,atelierPrecisionGuardActive:()=>false,
 partById:()=>({id:'one'}),atelierMeshSelectedMeshes:()=>[mesh],
 atelierMeshCenter:meshes=>new THREE.Box3().setFromObject(meshes[0]).getCenter(new THREE.Vector3()),
 atelierComponentSelectedPivot:()=>new THREE.Vector3(),atelierComponentSupported:()=>true,
 atelierArcRings:new Map(),atelierArcAxes:[['x',0xff7585],['y',0x6af1ad],['z',0x75b5ff]],
 atelierArcLimit:120*Math.PI/180,atelierArcPhase:{x:0,y:-Math.PI/3,z:Math.PI/3},
 atelierArcLast:0,atelierArcLastAxis:'x',atelierMeshStrip:null,atelierMeshPaintModeImmediately:()=>{},
 se340ModelBridge:{isBorrowed:()=>borrowed},matchMedia:()=>({matches:true}),document:{elementFromPoint:()=>covered?{}:canvas}
};
vm.createContext(context);
vm.runInContext([
 ...['atelierMeshGizmoClear','atelierComponentGizmoBuild','atelierArcPoint','atelierArcReset','atelierArcPosition','atelierArcReadout','atelierArcVisualFocus','atelierArcThickenRulers','atelierArcCalibratedBuild','atelierMeshGizmoBuild','atelierArcPickOnScreen'].map(nativeFunction),
 code,'globalThis.api=se431GizmoAccess;'
].join('\n'),context);
const api=context.api;
const event=(p,type='touch',extra={})=>({clientX:p[0],clientY:p[1],target:canvas,pointerType:type,button:0,isPrimary:true,...extra});
const original=JSON.stringify({position:mesh.position.toArray(),rotation:mesh.rotation.toArray(),scale:mesh.scale.toArray()});
function build(mode='move',component='mesh'){
 context.atelierMeshMode=mode;context.atelierComponentMode=component;context.atelierMeshGizmoBuild();return api.inspect();
}
let groups=0;
for(const component of ['mesh','face'])for(const mode of ['move','scale']){
 const state=build(mode,component);assert.equal(state.handles.length,mode==='scale'?4:3);
 for(const row of state.handles){
  const delta=[row.point[0]-state.pivot[0],row.point[1]-state.pivot[1]],n=Math.hypot(...delta)||1;
  const padded=[row.point[0]+delta[0]/n*14,row.point[1]+delta[1]/n*14];
  const picked=api.pick(event(padded));assert.equal(picked?.axis,row.axis,component+' '+mode+' '+row.axis+' padded touch');
  assert.equal(picked.object.userData.meshGizmoAxis,row.axis);
 }
 groups++;
}
{
 const state=build('rotate','face');assert.equal(state.handles.length,3);
 for(const row of state.handles)assert.equal(api.pick(event(row.point))?.axis,row.axis);
 groups++;
}
{
 const state=build('rotate');assert.equal(state.handles.length,3);
 for(const row of state.handles){
  let passed=false;
  for(const sample of row.samples.filter(p=>p?.inside)){
   const dx=sample.point[0]-state.pivot[0],dy=sample.point[1]-state.pivot[1],n=Math.hypot(dx,dy)||1;
   const near=[sample.point[0]+dx/n*14,sample.point[1]+dy/n*14];
   if(context.atelierArcPickOnScreen(event(near))?.axis===row.axis){passed=true;break;}
  }
  assert.ok(passed,'Every real native arc has a padded, unambiguous touch region: '+row.axis);
 }
 groups++;
}
{
 const spans=[];
 for(const distance of [1.5,6,24]){
  context.camera.position.set(3,2.3,5).normalize().multiplyScalar(distance);context.camera.lookAt(0,0,0);context.camera.updateMatrixWorld(true);context.orbit.distance=distance;
  const state=build();spans.push(state.handles.find(h=>h.axis==='x').point[0]-state.pivot[0]);
 }
 assert.ok(Math.max(...spans)-Math.min(...spans)<1e-6,'Visible extent stays constant across perspective zoom');groups++;
}
{
 const ortho=new THREE.OrthographicCamera(-3,3,3*450/390,-3*450/390,.01,100);ortho.position.set(3,2.3,5);ortho.lookAt(0,0,0);ortho.updateMatrixWorld(true);context.camera=ortho;
 for(const zoom of [.25,1,4]){
  ortho.zoom=zoom;ortho.updateProjectionMatrix();const state=build('scale');
  for(const row of state.handles)assert.equal(api.pick(event(row.point))?.axis,row.axis);
 }
 groups++;
}
{
 const state=build();const row=state.handles[0];
 const h=context.atelierMeshGizmo.children.find(o=>o.userData.meshGizmoAxis===row.axis);h.visible=false;
 assert.ok(!api.inspect().handles.some(o=>o.axis===row.axis));
 h.visible=true;covered=true;assert.equal(api.pick(event(row.point)),null);covered=false;
 assert.equal(api.pick(event(row.point,'touch',{target:{}})),null);
 assert.equal(api.pick(event(row.point,'touch',{isPrimary:false})),null);
 assert.equal(api.pick(event(row.point,'mouse',{button:2})),null);
 assert.equal(api.pick(event([-50,-50])),null);
 groups++;
}
{
 // Establish mouse modality before deriving the current native handle point.
 listeners.get('pointerdown')(event([0,0],'mouse',{type:'pointerdown'}));
 const state=build();const row=state.handles[0];
 assert.ok(listeners.has('pointermove'),'Native canvas hover listener is installed');
 listeners.get('pointermove')(event(row.point,'mouse',{type:'pointermove',button:-1,buttons:0}));
 assert.equal(api.inspect().activeAxis,row.axis,'Real pointermove button=-1 enters hover and paints its handle');
 assert.equal(api.pick(event(row.point,'mouse',{type:'pointermove',button:-1,buttons:2})),null,'Right-button movement remains excluded');
 listeners.get('pointerleave')();assert.equal(api.inspect().activeAxis,null,'Leaving the canvas clears hover');groups++;
}
{
 const state=build();const row=state.handles[0];
 assert.equal(api.pick(event([row.point[0]+100,row.point[1]+100])),null,'Far mesh taps do not become a gizmo grab');
 borrowed=true;assert.equal(api.pick(event(row.point)),null);assert.equal(api.inspect().ready,false);borrowed=false;
 context.camera.position.set(0,0,5);context.camera.lookAt(0,0,10);context.camera.updateMatrixWorld(true);
 assert.equal(api.inspect().handles.length,0,'Behind-camera handles are never projected into pick targets');
 groups++;
}
assert.equal(JSON.stringify({position:mesh.position.toArray(),rotation:mesh.rotation.toArray(),scale:mesh.scale.toArray()}),original,'Resize/pick only touches editor helpers');
console.log('MODEL_GIZMO_ACCESS_V11_431_PASS '+JSON.stringify({groups,three:THREE.REVISION,nativeBuilders:true,paddedTouchDiameter:44,sourceTransformsUnchanged:true,orthographic:true,behindCameraExcluded:true,uiPriority:true}));
