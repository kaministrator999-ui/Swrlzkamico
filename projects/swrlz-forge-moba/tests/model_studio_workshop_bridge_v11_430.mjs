#!/usr/bin/env node
// Actual native topology factories, validators, selection and history exercise
// the workshop transaction. The test owns only the surrounding editor fixture.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const threeFile=process.argv[2]||process.env.SWYRLZ_THREE_MODULE;
assert(threeFile,'Pass a local Three r169 ES module');
const THREE=await import(pathToFileURL(path.resolve(threeFile)).href);
assert.equal(THREE.REVISION,'169');
const read=name=>fs.readFileSync(path.join(ROOT,'runtime',name),'utf8');
const source=read('model_atelier.js');
function nativeFunction(name){
 const start=source.indexOf('function '+name+'(');assert(start>=0,name);
 let end=source.indexOf('{',start),depth=1;
 for(end++;depth;end++){if(source[end]==='{')depth++;else if(source[end]==='}')depth--;}
 return source.slice(start,end);
}
const clone=x=>structuredClone(x),plain=x=>JSON.parse(JSON.stringify(x));
const same=(a,b,message)=>assert.deepEqual(plain(a),plain(b),message);
const part=(id='cube')=>({id,name:'Plain cube',kind:'box',group:'Custom',position:[0,1,0],rotation:[0,0,0],scale:[1,1,1],color:'#9981ba',material:'matte'});
function fixture(parts=[part()]){
 let uuid=0,draws=0,componentRefreshes=0,pointerCalls=0,dirty=0;
 const events=[],root=new THREE.Group(),world=new THREE.Scene();world.add(root);
 const ctx={THREE,structuredClone,queueMicrotask,console,CustomEvent:class{constructor(type,{detail}){this.type=type;this.detail=detail;}},
  crypto:{randomUUID:()=>String(++uuid).padStart(32,'0')},MODEL_ATELIER_LIMIT:400,
  MODEL_ATELIER_KINDS:['sphere','box','cylinder','cone'],MODEL_ATELIER_MATERIALS:['matte','silk','gloss','metal','emissive'],
  currentProject:{kind:'model-atelier',modelAtelier:{name:'Native workshop fixture',parts:clone(parts),editedAt:'local',metadata:{keep:'project metadata'}}},
  modelRoot:root,world,panel:{hidden:false,querySelector:()=>null},renderer:{render:()=>draws++},camera:new THREE.PerspectiveCamera(44,1,.1,100),
  selection:parts[0]?.id||null,atelierMeshIds:parts[0]?[parts[0].id]:[],undo:[],redo:[],
  atelierGroupScope:'child',atelierGroupCurrent:null,atelierMeshAdding:false,atelierHDDirty:false,
  atelierMeshDrag:null,atelierSculptDrag:null,window:{dispatchEvent:event=>{events.push(event);return true;}},
  refreshList:()=>{},refreshInspector:()=>{},markDirty:()=>dirty++,status:()=>{},
  atelierMeshToolbarRefresh:()=>{},atelierMeshGizmoClear:()=>{},
  close:()=>{ctx.panel.hidden=true;return 'native-close';},pointerDown:()=>{pointerCalls++;return 'native-pointer';},
  model:()=>ctx.currentProject.kind==='model-atelier'?ctx.currentProject.modelAtelier:null,
  partById:id=>ctx.model()?.parts.find(p=>p.id===id)||null};
 vm.createContext(ctx);
 const initial=['checkPart','geometry','material','wipeModel','renderParts','modelSnapshot','checkpoint','signalEdited','historyStep','select'].map(nativeFunction).join('\n');
 vm.runInContext(initial.replace('function checkPart(','function nativeCheckPart(').replace('function geometry(','function nativePrimitiveGeometry('),ctx);
 for(const file of ['model_atelier_topology_lod_v11_38.js','model_atelier_topology_audit_v11_44.js','model_atelier_adaptive_topology_v11_46.js','model_atelier_boundary_cap_v11_48.js','model_atelier_components_v11_75.js'])vm.runInContext(read(file),ctx);
 ctx.checkPart=p=>ctx.nativeCheckPart(p)&&ctx.atelierTopologyValid(p);
 const nativeTopologyGeometry=ctx.atelierTopologyGeometry;
 ctx.atelierTopologyGeometry=p=>{if(ctx.failTopologyFactory)throw Error('native allocation failed');return nativeTopologyGeometry(p);};
 ctx.geometry=p=>p.kind==='topologyMesh'?ctx.atelierTopologyGeometry(p):ctx.nativePrimitiveGeometry(p);
 ctx.atelierCourierBaseGeometry=p=>{if(ctx.failPrimitiveFactory)throw Error('native primitive unavailable');return ctx.geometry(p);};
 ctx.atelierComponentRefresh=()=>{componentRefreshes++;ctx.atelierComponentUIRefresh();};
 ctx.atelierComponentUIRefresh=()=>{};
 ctx.atelierComponentOverlayClear=()=>{};
 ctx.renderParts();
 vm.runInContext(read('model_vr_bridge_v11_340.js')+'\nglobalThis.nativeBridge=se340ModelBridge;',ctx);
 vm.runInContext(read('model_vr_native_tools_v11_350.js')+'\nglobalThis.nativeTools=se350ModelTools;',ctx);
 ctx.se350ModelSurface={inspect:()=>({active:!!ctx.surfaceActive})};
 ctx.se410ModelAccessory={inspect:()=>({pending:ctx.accessoryPending||null})};
 vm.runInContext(read('model_vr_quick_create_v11_390.js')+'\nglobalThis.nativeCreate=se390ModelCreate;',ctx);
 vm.runInContext(read('model_mesh_operations_v11_430.js')+'\nglobalThis.kernel=se430MeshOps;',ctx);
 vm.runInContext(read('model_studio_workshop_bridge_v11_430.js')+`\n
  globalThis.api=se430ModelWorkshop;
  globalThis.setComponents=(mode,ids)=>{atelierComponentMode=mode;atelierComponentIds=[...ids];atelierComponentPartId=selection;atelierComponentUIRefresh();};
  globalThis.getComponents=()=>({mode:atelierComponentMode,ids:[...atelierComponentIds],partId:atelierComponentPartId});
 `,ctx);
 const mesh=()=>root.children.find(m=>m.isMesh&&m.userData.atelierId===ctx.selection);
 return {ctx,api:ctx.api,root,world,events,mesh,document:()=>ctx.model(),counts:()=>({draws,componentRefreshes,pointerCalls,dirty}),
  setComponents:(mode,ids)=>ctx.setComponents(mode,ids),replace:next=>{ctx.currentProject={kind:'model-atelier',modelAtelier:clone(next)};ctx.renderParts();},
  convert:()=>{const r=ctx.api.convert();assert.equal(r.ok,true,r.reason);return r;},
  top:()=>{const p=ctx.partById(ctx.selection),t=p.topologyMesh;const seed=Array.from({length:t.indices.length/3},(_,i)=>i).find(f=>{
    const [a,b,c]=t.indices.slice(f*3,f*3+3).map(id=>new THREE.Vector3(...t.positions.slice(id*3,id*3+3)));return b.sub(a).cross(c.sub(a)).normalize().y>.999;});
    assert(Number.isInteger(seed));const r=ctx.api.selectRegion(seed);assert.equal(r.ok,true,r.reason);return r;}};
}
let groups=0;
{
 const f=fixture(),before=clone(f.document()),material=f.document().parts[0].material;
 assert.equal(f.api.inspect().convert.available,true);assert.equal(f.api.inspect().operations.inset.available,false);
 f.convert();assert.equal(f.document().parts[0].kind,'topologyMesh');assert.equal(f.document().parts[0].topologyMesh.positions.length/3,8);
 assert.equal(f.document().parts[0].material,material);assert.equal(f.ctx.undo.length,1);same(f.document().metadata,before.metadata);
 f.ctx.historyStep(true);same(f.document(),before);f.ctx.historyStep(false);assert.equal(f.document().parts[0].kind,'topologyMesh');groups++;
}
{
 const f=fixture();f.convert();f.top();const before=clone(f.document()),history=f.ctx.undo.length,original=f.mesh().geometry;
 const preview=f.api.preview('inset',{amount:.2});assert.equal(preview.ok,true,preview.reason);
 const shown=f.mesh().geometry;assert.notEqual(shown,original);assert.equal(shown.index.count/3,20);same(f.document(),before);assert.equal(f.ctx.undo.length,history);
 assert.equal(f.api.inspect().preview.active,true);assert.equal(f.api.inspect().preview.selectedFaces.length,2);
 let disposed=0;shown.addEventListener('dispose',()=>disposed++);assert.equal(f.api.cancel().cancelled,true);
 assert.equal(f.mesh().geometry,original);assert.equal(disposed,1);same(f.document(),before);assert.equal(f.ctx.undo.length,history);groups++;
}
{
 const f=fixture();f.convert();f.top();const before=clone(f.document()),history=f.ctx.undo.length;
 assert.equal(f.api.preview('inset',{amount:.2}).ok,true);const original=f.mesh().geometry;let disposed=0;original.addEventListener('dispose',()=>disposed++);
 assert.equal(f.api.preview('inset',{amount:.3}).ok,true);assert.equal(disposed,1,'Replaced preview geometry is disposed exactly once');
 const current=f.mesh().geometry;let currentDisposed=0;current.addEventListener('dispose',()=>currentDisposed++);
 assert.equal(f.api.preview('inset',{amount:NaN}).ok,false);assert.equal(f.mesh().geometry,current,'Rejected input preserves valid preview');
 const result=f.api.apply();assert.equal(result.ok,true,result.reason);assert.equal(currentDisposed,1);assert.equal(f.ctx.undo.length,history+1);
 assert.equal(f.api.inspect().preview.active,false);assert.equal(f.api.inspect().selection.faceIds.length,2);assert.equal(f.document().parts[0].topologyMesh.indices.length/3,20);
 const saved=clone(f.document());f.ctx.historyStep(true);same(f.document(),before);f.ctx.historyStep(false);same(f.document(),saved);groups++;
}
{
 const f=fixture();f.convert();f.top();const baseline=clone(f.document());
 assert.equal(f.api.preview('inset',{amount:.2}).ok,true);assert.equal(f.api.apply().ok,true);
 const inset=clone(f.document()),count=f.ctx.undo.length;assert.equal(f.api.preview('extrude',{amount:-.35}).ok,true);same(f.document(),inset);
 const committed=f.api.apply();assert.equal(committed.ok,true,committed.reason);assert.equal(f.ctx.undo.length,count+1);assert.equal(f.document().parts[0].topologyMesh.indices.length/3,28);
 const a=f.ctx.atelierTopologyAudit(f.document().parts[0].topologyMesh);assert.equal(a.boundaryEdges,0);assert.equal(a.nonManifoldEdges,0);assert.equal(a.zeroAreaFaces,0);assert.equal(a.oppositeWindingErrors,0);
 f.ctx.historyStep(true);same(f.document(),inset);f.ctx.historyStep(true);same(f.document(),baseline);groups++;
}
{
 const f=fixture();f.convert();f.top();const before=clone(f.document()),count=f.ctx.undo.length;f.ctx.redo.push('preserved redo');
 assert.equal(f.api.preview('inset',{amount:.2}).ok,true);f.ctx.historyStep(true);assert.equal(f.api.inspect().preview.active,false);same(f.document(),before);assert.equal(f.ctx.undo.length,count);assert.equal(f.ctx.redo.length,1);
 f.ctx.historyStep(true);assert.equal(f.document().parts[0].kind,'box');groups++;
}
{
 for(const field of ['uvPaint','textureBinding','rigWeights','sculptVertexEdits','refinementLayers','organicSurface']){
  const p=part();p[field]=field==='uvPaint'?'data:image/png;base64,AA==':{};const f=fixture([p]),before=clone(f.document());
  assert.equal(f.api.convert().ok,false,field);assert.match(f.api.inspect().convert.reason,/authored|paint|texture|rig/);same(f.document(),before);assert.equal(f.ctx.undo.length,0);
 }
 const f=fixture();f.mesh().isSkinnedMesh=true;assert.equal(f.api.convert().ok,false);assert.match(f.api.inspect().convert.reason,/skinned|animated/);groups++;
}
{
 const f=fixture();f.convert();f.top();const count=f.ctx.undo.length;assert.equal(f.api.preview('inset',{amount:.2}).ok,true);
 f.document().parts[0].color='#123456';assert.equal(f.api.apply().ok,false);assert.equal(f.document().parts[0].color,'#123456');assert.equal(f.ctx.undo.length,count);assert.equal(f.api.inspect().preview.active,false);
 f.top();assert.equal(f.api.preview('inset',{amount:.2}).ok,true);f.ctx.renderParts();assert.equal(f.api.inspect().preview.active,false);assert.equal(f.document().parts[0].topologyMesh.indices.length/3,12);groups++;
}
{
 const f=fixture([part(),part('other')]);f.convert();f.top();const before=clone(f.document()),history=f.ctx.undo.length;
 assert.equal(f.api.preview('inset',{amount:.2}).ok,true);f.ctx.atelierMeshIds=['other','cube'];
 assert.equal(f.api.inspect().selection.objectCount,2);same(f.api.inspect().selection.objectIds,['other','cube']);
 assert.equal(f.api.apply().ok,false,'Changing object selection invalidates the pending edit even if its primary part stays the same');
 same(f.document(),before);assert.equal(f.ctx.undo.length,history);assert.equal(f.api.inspect().preview.active,false);groups++;
}
{
 const f=fixture();f.convert();f.top();assert.equal(f.api.preview('inset',{amount:.2}).ok,true);
 const replacement={name:'Reopened project',parts:[part('new-source')],metadata:{keep:'replacement'},editedAt:'local'};f.replace(replacement);
 same(f.document(),replacement);assert.equal(f.api.inspect().preview.active,false);assert.equal(f.api.apply().ok,false);same(f.document(),replacement);assert.equal(f.mesh(),undefined);
 assert.equal(f.ctx.close(),'native-close');assert.equal(f.api.convert().ok,false);groups++;
}
{
 const f=fixture();f.convert();f.top();const count=f.ctx.undo.length,before=clone(f.document());
 for(const amount of [null,undefined,'0.2',Infinity,NaN,{},()=>.2])assert.equal(f.api.preview('inset',{amount}).ok,false);
 assert.equal(f.api.preview('invented').ok,false);assert.equal(f.api.preview('inset',{amount:.2,extra:1}).ok,false);
 f.ctx.failTopologyFactory=true;assert.equal(f.api.preview('inset',{amount:.2}).ok,false);assert.equal(f.api.inspect().preview.active,false);f.ctx.failTopologyFactory=false;
 same(f.document(),before);assert.equal(f.ctx.undo.length,count);
 const g=fixture();g.ctx.failPrimitiveFactory=true;assert.equal(g.api.convert().ok,false);assert.equal(g.ctx.undo.length,0);groups++;
}
{
 const f=fixture();f.convert();f.top();const shownBefore=f.counts();const xr=new THREE.Group();f.world.add(xr);assert.equal(f.ctx.nativeBridge.borrowRoot(xr).ok,true);
 const before=clone(f.document());assert.equal(f.api.preview('inset',{amount:.2}).ok,true);assert.equal(f.counts().draws,shownBefore.draws,'XR preview never draws the detached desktop scene');
 const refreshes=f.counts().componentRefreshes;f.api.setComponentMode('face');assert.equal(f.api.inspect().preview.active,false);assert.equal(f.counts().componentRefreshes,refreshes);
 assert.equal(f.counts().draws,shownBefore.draws);same(f.document(),before);
 f.top();assert.equal(f.api.preview('inset',{amount:.2}).ok,true);assert.equal(f.api.apply().ok,true);assert.equal(f.counts().draws,shownBefore.draws);
 assert.equal(f.root.parent,xr);f.ctx.nativeBridge.releaseRoot();assert.equal(f.root.parent,f.world);groups++;
}
{
 const f=fixture();const before=clone(f.document());assert.equal(f.api.create('box').ok,true);assert.equal(f.document().parts.length,2);assert.equal(f.ctx.undo.length,1);
 assert.equal(f.api.inspect().selection.mode,'mesh');assert.equal(f.api.inspect().selection.name,'Cube');assert.equal(f.document().parts[1].kind,'box');assert.notEqual(f.document().parts[1].id,f.document().parts[0].id);
 f.ctx.historyStep(true);same(f.document(),before);groups++;
}
{
 const f=fixture();f.convert();f.top();const before=clone(f.document());assert.equal(f.api.preview('deleteFaces').ok,true);assert.equal(f.api.apply().ok,true);
 const p=f.document().parts[0];assert.equal(f.ctx.atelierTopologyAudit(p.topologyMesh).boundaryEdges,4);f.setComponents('vertex',[0]);
 // Choose a real boundary vertex rather than assuming the compacted index.
 const mesh=f.mesh(),top=f.ctx.atelierComponentTopology(mesh),audit=f.ctx.atelierTopologyAudit(p.topologyMesh);
 const boundary=[...audit.edges.values()].find(list=>list.length===1)[0].from;f.setComponents('vertex',[top.vertices.indexOf(boundary)]);
 assert.equal(f.api.inspect().operations.fillHole.available,true);const cap=f.api.preview('fillHole');assert.equal(cap.ok,true,cap.reason);assert.equal(f.api.apply().ok,true);assert.equal(f.ctx.atelierTopologyAudit(p.topologyMesh).boundaryEdges,0);
 const serialized=JSON.stringify(f.document()),reopened=JSON.parse(serialized);assert(reopened.parts.every(f.ctx.checkPart));assert.equal(Object.keys(reopened.parts[0].topologyMesh).sort().join(','),'indices,positions,uvs');
 f.ctx.historyStep(true);f.ctx.historyStep(true);same(f.document(),before);groups++;
}
{
 const f=fixture();f.convert();f.setComponents('edge',[0]);assert.equal(f.api.inspect().operations.splitEdge.available,true);
 const p=f.document().parts[0],vertices=p.topologyMesh.positions.length/3;assert.equal(f.api.preview('splitEdge').ok,true);
 assert.equal(f.api.preview('splitEdge').ok,true,'Updating a split preview keeps the original edge correspondence');assert.equal(f.api.apply().ok,true);assert.equal(p.topologyMesh.positions.length/3,vertices+1);
 f.top();const sub=f.api.preview('subdivide',{amount:.5});assert.equal(sub.ok,true,sub.reason);assert.equal(f.api.apply().ok,true);assert.equal(f.ctx.atelierTopologyAudit(p.topologyMesh).boundaryEdges,0);groups++;
}
{
 const f=fixture(),plane=new THREE.PlaneGeometry(1,.8),converted=f.ctx.kernel.convert(plane);plane.dispose();assert.equal(converted.ok,true,converted.reason);
 const p={...part(),kind:'topologyMesh',topologyMesh:clone(converted.data)};f.replace({name:'Open planar flap',parts:[p],editedAt:'local',metadata:{keep:'plain'}});
 assert.equal(f.api.selectRegion(0,'cube').ok,true);assert.equal(f.api.inspect().operations.solidify.available,true);
 const before=clone(f.document());assert.equal(f.api.preview('solidify',{amount:.12}).ok,true);same(f.document(),before);
 assert.equal(f.api.apply().ok,true);assert.equal(f.ctx.atelierTopologyAudit(f.document().parts[0].topologyMesh).boundaryEdges,0);assert.equal(f.document().parts[0].topologyMesh.indices.length/3,12);
 f.ctx.historyStep(true);same(f.document(),before);groups++;
}
{
 const f=fixture();f.convert();const p=f.document().parts[0],indices=p.topologyMesh.indices;[indices[1],indices[2]]=[indices[2],indices[1]];
 f.ctx.renderParts();const before=clone(f.document());assert.equal(f.api.inspect().operations.repairNormals.available,true);
 const repair=f.api.preview('repairNormals');assert.equal(repair.ok,true,repair.reason);same(f.document(),before);assert.equal(f.api.apply().ok,true);
 const checked=f.ctx.atelierTopologyAudit(p.topologyMesh);assert.equal(checked.oppositeWindingErrors,0);assert.equal(checked.boundaryEdges,0);assert.equal(checked.nonManifoldEdges,0);
 f.ctx.historyStep(true);same(f.document(),before);groups++;
}
{
 const f=fixture();f.convert();f.top();await Promise.resolve();const before=f.events.length;
 f.setComponents('face',[0]);f.setComponents('face',[1]);f.setComponents('face',[2]);await Promise.resolve();
 assert.equal(f.events.length,before+1,'Legacy component updates coalesce into one change event');assert.equal(f.events.at(-1).type,'swrlz:model-workshop-change');same(f.events.at(-1).detail.selection.faceIds,[2]);
 assert.equal(f.api.preview('inset',{amount:.2}).ok,true);const calls=f.counts().pointerCalls;let prevented=false;f.ctx.pointerDown({cancelable:true,preventDefault:()=>prevented=true});assert.equal(prevented,true);assert.equal(f.counts().pointerCalls,calls);f.api.cancel();groups++;
}
console.log('MODEL_STUDIO_WORKSHOP_BRIDGE_V11_430_PASS',JSON.stringify({groups,three:THREE.REVISION,nativeFactory:true,nativeValidator:true,nativeHistory:true,preview:'source-safe owned geometry',schema:'ordinary native topology',xr:'borrowed projection without desktop draws'}));
