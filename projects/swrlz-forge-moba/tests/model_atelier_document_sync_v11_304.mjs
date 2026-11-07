// Native document -> open viewport/list/GLB regression. No browser, inference,
// authoring operation, history mutation or extra renderer is needed by sync.
// Usage: node THIS_TEST ASSEMBLED_HTML THREE_169_ESM [PRIVATE_NATIVE_FIXTURE]
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {pathToFileURL} from 'node:url';
const html=fs.readFileSync(process.argv[2],'utf8');
const THREE=await import(pathToFileURL(process.argv[3]).href);
assert.equal(THREE.REVISION,'169');
const scopeStart=html.indexOf('const ModelAtelier=(()=>{');
assert(scopeStart>=0);
function sourceFunction(name){
 const at=html.indexOf('function '+name+'(',scopeStart);
 assert(at>=0,name);
 const sourceStart=html.slice(at-6,at)==='async '?at-6:at;
 let quote='',comment='',depth=0,started=false;
 for(let i=html.indexOf('{',at);i<html.length;i++){
  const c=html[i],n=html[i+1];
  if(comment==='line'){if(c==='\n')comment='';continue;}
  if(comment==='block'){if(c==='*'&&n==='/'){comment='';i++;}continue;}
  if(quote){if(c==='\\'){i++;continue;}if(c===quote)quote='';continue;}
  if(c==='/'&&n==='/'){comment='line';i++;continue;}
  if(c==='/'&&n==='*'){comment='block';i++;continue;}
  if(c==='"'||c==="'"||c==='`'){quote=c;continue;}
  if(c==='{'){depth++;started=true;}
  if(c==='}'&&--depth===0&&started)return html.slice(sourceStart,i+1);
 }
 throw Error('Unclosed '+name);
}
const start='/* SE304_MODELER_DOCUMENT_VIEW_SYNC_START */',end='/* SE304_MODELER_DOCUMENT_VIEW_SYNC_END */';
const begin=html.indexOf(start),finish=html.indexOf(end,begin);
assert(begin>=0&&finish>begin);
assert.equal(html.split(start).length-1,1);
const runtime=html.slice(begin,finish);
class Element{
 constructor(tag){this.tagName=tag;this.children=[];this.value='';this.textContent='';this.hidden=false;this.disabled=false;this.classList={remove(){}};}
 replaceChildren(...items){this.children=[];this.append(...items);}
 append(...items){for(const item of items){if(item.tagName==='fragment')this.children.push(...item.children);else this.children.push(item);}}
 get options(){return this.children.filter(item=>item.tagName==='option');}
}
const elements=new Map();
for(const id of ['Reopen','CourierStudio','Parts','PartCount','Undo','Redo','SelectionName','InspectorControls','Name','Kind','Color','Material'])elements.set(id,new Element(id==='Parts'?'select':'div'));
for(const prefix of ['position','rotation','scale'])for(let i=0;i<3;i++)elements.set(prefix+i,new Element('input'));
const hooks=['atelierRuntimeLODStart','atelierMeshToolbarRefresh','atelierGroupsOutline','atelierComponentRefresh','atelierDesktopWireRefresh','atelierRuntimeLODDispose','refreshModelMetrics','atelierBindAssemblyMeshes','se220RigBind','se224WolfRigBind','se220RigRefresh','atelierMeshListSync','atelierSurfaceRefresh','atelierDensityRefresh','atelierHDRefresh','atelierReferenceFinishRefresh','atelierReferenceLegRefresh','atelierPortraitRefresh','atelierHeadAnatomyRefresh','atelierCourierRefresh','atelierSculptRefresh','atelierViewportControlsRefresh','atelierRefPaint','atelierFaceSheetRefresh','atelierFaceLandmarkRefresh','atelierFaceProfileRefresh','atelierLODRefresh','atelierRuntimeLODRefresh','atelierTopologyAuditRefresh','atelierAdaptiveRefresh','atelierBoundaryCapRefresh','atelierUVRefresh','atelierExtrudeRefresh'];
const context={THREE,console,TextEncoder,TextDecoder,structuredClone,
 document:{createDocumentFragment:()=>new Element('fragment'),createElement:tag=>new Element(tag)},
 $m:id=>elements.get(id)||null,queueMicrotask:fn=>fn(),status:()=>{},
 counters:{render:0,loop:0,close:0,open:0,dirty:0,checkpoint:0,camera:0,helpers:0},downloads:[],
 window:{SWYRL_ENGINE_WORKSPACES:{usingScratch:()=>context.useScratch,scratchModel:()=>context.scratch,modelerActive:()=>true}},
 useScratch:true,scratch:{schema:'swyrl-model-atelier-v1',parts:[]},
};
for(const name of hooks)context[name]=()=>{};
const ctx=vm.createContext(context);
vm.runInContext(`
let currentProject={kind:'scene',name:'Background game preserved'},selection=null,pressed=null;
let panel={hidden:false,classList:{remove(){}}};
let renderer={domElement:{identity:'existing-canvas'},render(){counters.render++}},camera=new THREE.PerspectiveCamera(44,1,.1,100);
let world=new THREE.Scene(),modelRoot=new THREE.Group();world.add(modelRoot);
let undo=['old-history'],redo=['old-redo'],updating=false,raf=101;
let orbit={yaw:.3,pitch:.19,distance:9};
let atelierMeshIds=[],atelierMeshAdding=false,atelierGroupCurrent=null,atelierMeshDrag=null,atelierMeshPivot=null,atelierMeshDensityShownPart=null;
let atelierComponentIds=[],atelierComponentPartId=null,atelierComponentGesture=null,atelierComponentDrag=null,atelierComponentPivot=null;
let atelierSculptVertexIDs=[],atelierSculptLastVertexPart=null,atelierSculptDrag=null,atelierSculptHit=null;
let atelierLassoArm=null,atelierLassoPending=[],atelierLassoActive=null,atelierLassoDrag=null,atelierLassoTempPin=null,atelierLassoSelectedPin=0,atelierLassoFreehand=null;
let atelierViewportGizmoDrag=null,atelierDesktopDrag=null,atelierPaintDrag=null,atelierPrecisionGizmoDrag=null,atelierPrecisionGuardTap=null;
let atelierCameraTouches=new Map(),atelierCameraConsumedTouches=new Set(),atelierCameraGesture=null,atelierCameraMousePan=null;
let atelierCameraInterior=false,atelierInteriorPartId=null,atelierInteriorPreviousMode=null,atelierInteriorPreviousCamera=null,atelierDetailTarget=null;
let atelierCameraPan=new THREE.Vector3(),atelierViewOverrides=new Map(),atelierViewMaterialOverrides=new Map(),atelierViewGlobal='overlay';
const safeName=n=>String(n??'Part').slice(0,100);
function cameraUpdate(){counters.camera++;camera.updateMatrixWorld();}
function close(){counters.close++;panel.hidden=true;}
function open(){counters.open++;throw Error('sync must not close/reopen');}
function checkpoint(){counters.checkpoint++;throw Error('sync must not checkpoint');}
function markDirty(){counters.dirty++;throw Error('sync must not mutate document state');}
function requestAnimationFrame(){counters.loop++;throw Error('sync must not create another loop');}
function download(name,body){downloads.push({name,body});}
// Isolate synchronization from unrelated rig/material systems. Mesh objects,
// geometry buffers, transforms and the production GLB exporter remain real.
function se224WolfRigMesh(p){
 const g=p.kind==='box'?new THREE.BoxGeometry(1,1,1):p.kind==='cone'?new THREE.ConeGeometry(1,1,9):p.kind==='cylinder'?new THREE.CylinderGeometry(1,1,1,10):new THREE.SphereGeometry(1,8,6);
 return new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:p.color,roughness:.7}));
}
function atelierViewModeApply(){}
function atelierComponentOverlayClear(){counters.helpers++;}
function atelierSculptOverlayClear(){counters.helpers++;}
function atelierLassoOverlayClear(){counters.helpers++;}
function atelierMeshGizmoClear(){counters.helpers++;}
${['model','partById','wipeModel','renderParts','refreshList','refreshInspector','syncProject','atelierCourierGLB'].map(sourceFunction).join('\n')}
${runtime}
globalThis.api={
 sync:()=>syncProject(),render:()=>renderParts(),exportGLB:()=>atelierCourierGLB(),
 replace:(doc,scratch=false)=>{currentProject=doc;useScratch=scratch;},
 setScratch:doc=>{scratch=doc;useScratch=true;},
 setSelection:id=>{selection=id;atelierMeshIds=[id];atelierGroupCurrent='old-group';atelierComponentPartId=id;atelierComponentIds=[7];atelierComponentDrag={partId:id};atelierSculptVertexIDs=[3];atelierSculptLastVertexPart=id;atelierMeshDrag={old:true};atelierViewOverrides.set(id,'xray');atelierViewMaterialOverrides.set(id,{colors:false});},
 state:()=>({renderer,canvas:renderer.domElement,camera,world,root:modelRoot,meshes:modelRoot.children.filter(o=>o.isMesh&&o.userData.atelierId),selection,componentPart:atelierComponentPartId,componentIds:atelierComponentIds.slice(),drag:atelierMeshDrag,viewOverrides:atelierViewOverrides.size,materialOverrides:atelierViewMaterialOverrides.size,display:atelierViewGlobal,undo:undo.slice(),redo:redo.slice(),raf,project:currentProject}),
 hide:()=>{panel.hidden=true;},show:()=>{panel.hidden=false;},
 replaceParts:parts=>{model().parts=parts;}
};
`,ctx);
const api=ctx.api;
const part=(id,name='Part '+id)=>({id,name,kind:'box',group:'Test',position:[.2,1,.1],rotation:[0,0,0],scale:[.4,.5,.6],color:'#f4ece0',material:'matte'});
const doc=(name,parts)=>({kind:'model-atelier',name,modelAtelier:{schema:'swyrl-model-atelier-v1',parts}});
const owned=()=>Array.from(api.state().meshes,m=>m.userData.atelierId);
const list=()=>elements.get('Parts').options.map(o=>o.value);
const initial=api.state();
api.render(); // The existing open viewport initially contains an empty scratch.
assert.equal(owned().length,0);
const first=doc('Loaded model',[part('shared'),part('second')]);const frozen=JSON.stringify(first);
api.setSelection('shared');api.replace(first);api.sync();
assert.deepEqual(owned(),['shared','second']);assert.deepEqual(list(),['shared','second']);
assert(elements.get('PartCount').textContent.includes('2 individually editable'));
assert.equal(api.state().selection,null);assert.equal(api.state().componentPart,null);assert.equal(api.state().componentIds.length,0);assert.equal(api.state().drag,null);
assert.equal(api.state().viewOverrides,0);assert.equal(api.state().materialOverrides,0);assert.equal(api.state().display,'overlay');
assert.equal(JSON.stringify(first),frozen);
for(const key of ['renderer','canvas','camera','world','root'])assert.equal(api.state()[key],initial[key],key+' must be reused');
assert.equal(api.state().raf,101);assert.equal(ctx.counters.loop,0);assert.equal(ctx.counters.open,0);assert.equal(ctx.counters.dirty,0);assert.equal(ctx.counters.checkpoint,0);
assert.equal(JSON.stringify(api.state().undo),'["old-history"]');assert.equal(JSON.stringify(api.state().redo),'["old-redo"]');
async function exportedCount(){
 await api.exportGLB();const body=ctx.downloads.at(-1).body;
 const view=new DataView(body.buffer,body.byteOffset,body.byteLength);
 assert.equal(view.getUint32(0,true),0x46546c67);assert.equal(view.getUint32(4,true),2);
 const jsonLength=view.getUint32(12,true);const data=JSON.parse(new TextDecoder().decode(body.subarray(20,20+jsonLength)));
 assert.equal(data.meshes.length,owned().length);assert.equal(data.nodes.length,owned().length);
 return data.meshes.length;
}
assert.equal(await exportedCount(),2);
// An ordinary repeat must not discard a valid selection or rebuild mesh objects.
api.setSelection('shared');const repeated=api.state();const draws=ctx.counters.render;
api.sync();assert.equal(api.state().selection,'shared');assert.equal(api.state().componentPart,'shared');assert.equal(api.state().meshes[0],repeated.meshes[0]);assert.equal(ctx.counters.render,draws);
const second=doc('Another model',[{...part('shared','Different shared ID'),kind:'sphere',position:[2,3,4]}]);const frozenSecond=JSON.stringify(second);
api.replace(second);api.sync();assert.deepEqual(owned(),['shared']);assert.deepEqual(list(),['shared']);assert.equal(api.state().selection,null);assert.equal(JSON.stringify(second),frozenSecond);assert.equal(await exportedCount(),1);
// Same-model replacement of the array still requires derived reconstruction.
api.replaceParts([part('replacement')]);api.sync();assert.deepEqual(owned(),['replacement']);assert.deepEqual(list(),['replacement']);
// Empty scratch is a valid model, not permission to close/bootstrap Game.
api.setScratch({schema:'swyrl-model-atelier-v1',parts:[]});api.sync();assert.equal(owned().length,0);assert.equal(list().length,0);assert.equal(ctx.counters.close,0);
const scratchMesh=part('scratch');ctx.scratch.parts=[scratchMesh];api.sync();api.setSelection('scratch');const scratchState=api.state();
api.replace({kind:'scene',name:'Different background game'},true);api.sync();assert.equal(api.state().selection,'scratch');assert.equal(api.state().meshes[0],scratchState.meshes[0]);assert.equal(api.state().project.name,'Different background game');
// A closed view stays closed; true non-Modeler context retains legacy close logic.
api.hide();const beforeClosed=ctx.counters.render;api.replace(first);api.sync();assert.equal(ctx.counters.render,beforeClosed);
api.show();api.replace({kind:'scene',name:'Game remains Game'});api.sync();assert.equal(ctx.counters.close,1);assert.equal(api.state().project.name,'Game remains Game');assert.equal(ctx.counters.open,0);
// Optional task-owned fixture: check every cached native part reaches the scene
// and production GLB exporter without committing the private model to the repo.
if(process.argv[4]){
 const native=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));const loaded=native.project||native;
 assert(Array.isArray(loaded.modelAtelier?.parts));const expectedCount=loaded.modelAtelier.parts.length;assert(expectedCount>0);
 const original=JSON.stringify(loaded);api.show();api.replace(loaded);api.sync();
 assert.equal(owned().length,expectedCount);assert.equal(list().length,expectedCount);assert.equal(await exportedCount(),expectedCount);assert.equal(JSON.stringify(loaded),original);
 assert.deepEqual([...owned()].sort(),loaded.modelAtelier.parts.map(p=>p.id).sort());
 console.log('MODELER_CACHED_NATIVE_PROJECTION_AND_GLB_PASS',expectedCount);
}
console.log('MODELER_DOCUMENT_VIEW_SYNC_V11_304_PASS');
