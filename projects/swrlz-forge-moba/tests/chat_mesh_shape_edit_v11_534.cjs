#!/usr/bin/env node
'use strict';

const assert = require('node:assert/strict');
const {webcrypto} = require('node:crypto');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync(process.argv[2], 'utf8');
const plain = (id, kind = 'box') => ({id,name:id,kind,group:'Test group',position:[0,1,0],rotation:[0,.2,0],
 scale:[.7,.5,1],color:'#392245',material:'silk'});
const copy = value => JSON.parse(JSON.stringify(value));

function between(start, end){
 const a = source.indexOf(start), b = source.indexOf(end, a + start.length);
 assert(a >= 0 && b > a, `Missing assembled anchor: ${start}`);
 return source.slice(a,b);
}

function harness(){
 const state = {contextMode:'model-atelier',scratch:false,gesture:false,visible:true,downloads:0,finishes:[],dirty:0,renders:0};
 const editable = plain('example-part');
 const painted = {...plain('painted'),uvPaintPNG:'fixture'};
 const untouched = plain('another-piece');
 const doc = {schema:'swyrl-model-atelier-v1',parts:[editable,painted,untouched],assemblies:[{id:'example',partIds:[editable.id]}],
  meshGroups:[{id:'example-group',ids:[editable.id,untouched.id]}]};
 const project = {instanceId:'project',kind:'model-atelier',name:'Synthetic shape test',modelAtelier:doc};
 const nothing = ()=>{};
 const okay = ()=>true;
 const sandbox = {TextEncoder,structuredClone,crypto:webcrypto,MODEL_ATELIER_LIMIT:100,
  queueMicrotask:nothing,setTimeout:callback=>{callback();return 1;},clearTimeout:nothing,
  currentProject:project,model:()=>project.modelAtelier,partById:id=>project.modelAtelier.parts.find(p=>p.id===id),
  panel:{hidden:false},playing:false,simulating:false,selection:editable.id,window:{SWYRL_ENGINE_WORKSPACES:{usingScratch:()=>state.scratch,
   scratchModel:()=>project.modelAtelier}},
  se340ModelBridge:{inspect:()=>({gesture:state.gesture})},se350ModelTools:{inspect:()=>({gesture:false})},
  se350ModelSurface:{inspect:()=>({active:false})},se390ModelCreate:{inspect:()=>({pending:false})},
  se410ModelAccessory:{inspect:()=>({pending:false})},se430ModelWorkshop:{hasGeometryPreview:()=>false},
  atelierMeshDrag:null,atelierComponentDrag:null,atelierComponentGesture:null,atelierSculptDrag:null,
  atelierCourierBindingValid:okay,atelierMeshPrimitiveDensityValid:okay,atelierSculptValid:okay,
  atelierFaceSheetValid:okay,atelierTopologyValid:okay,atelierHeadAnatomyValid:okay,
  MODEL_ATELIER_KINDS:['sphere','box','cone','cylinder','loft','topologyMesh'],MODEL_ATELIER_MATERIALS:['silk','matte','gloss'],
  atelierViewEnsureAfterGeometryEdit:nothing,atelierGroupsPrune:nothing,atelierGroupsUIRefresh:nothing,
  renderParts:()=>state.renders++,atelierSculptOverlayRefresh:nothing,atelierLassoOverlayRefresh:nothing,refreshList:nothing,
  refreshInspector:nothing,status:nothing,markDirty:()=>state.dirty++,se220RigBind:nothing,se220RigRefresh:nothing,
  MAX_META:48,MAX_BATCH:64,KINDS:new Set(['sphere','box','cone','cylinder','loft','lathe']),actors:[],dirty:false,selected:null,
  document:{getElementById:()=>null},atelierOpen:()=>state.contextMode==='model-atelier',
  studioSnapshot:()=>({studio:state.contextMode==='model-atelier'?'modeler':'game',details:state.summaryDetails}),getProjectId:()=>project.instanceId,
  se175Starters:()=>[],se178EnrichContext:nothing,se175UpdateLabel:nothing,se175ScheduleSave:nothing,
  summaryName:v=>String(v??'').slice(0,100),bounded:(v,max=100)=>typeof v==='string'&&v.length>0&&v.length<=max,
  seenBatches:new Set(),isVisible:()=>state.visible,port:null,setStatus:message=>{state.status=message;},
  revoke:nothing,heartbeat:nothing,hostRequest:async (path,fields)=>{
   if(path.endsWith('/take')){state.downloads++;return state.pending;}
   if(path.endsWith('/finish')){state.finishes.push(copy(fields));return;}
   throw Error(`Unexpected transport: ${path}`);
  },
 };
 const shapeValidator = between('function se293ShapeData(op){','function se293ChatNativePart(op){');
 const priorNativeCreator = between('function se293ChatNativePart(op){','const se534ShapeSchema=');
 const shapeAdapter = between('const se534ShapeSchema=','/* SE340_MODEL_VR_BRIDGE_START */');
 const atelierValidator = between('function checkPart(p){','function validParts(parts){');
 const atelierCheckpoint = 'function checkpoint(){se521Journal.before();}';
 assert(source.includes(atelierCheckpoint));
 const atelierSignal = between('function signalEdited(){','function historyStep(backward){');
 const journal = between('/* SE521_PERSISTENT_EDIT_JOURNAL_START','/* SE521_PERSISTENT_EDIT_JOURNAL_END');
 const context = between('function context(){','function setStatus(message,error=false){');
 const hostValidator = between('function se534ShapeCapability(rows){','function validateStudioOperation(op,ctx){');
 const hostExecute = between('function execute(op){','const se293MeshTools=');
 const hostBatch = between('const se293MeshTools=','async function receive(message){');
 const dirtyWrapper = between('const nativeMarkDirty=markDirty;','const nativeLoadProject=');
 const prioritized = between('function prioritized(items,selectedId){','function studioSnapshot(workspace){');
 const nativeCode = [shapeValidator,priorNativeCreator,shapeAdapter,atelierValidator,atelierCheckpoint,atelierSignal,journal,
  'this.native={chatShapeEditable:se534ChatShapeEditable,chatAction:seChatAtelierApply,signalEdited,checkpoint};'];
 const hostCode = ['(()=>{let epoch=0,heartbeatTimer=null;const lease={leaseId:"lease",threadId:"thread",projectId:"project"};',
  shapeValidator,between('const se534ShapeSchema=','const se534PlainPartFields='),prioritized,context,hostValidator,hostExecute,hostBatch,dirtyWrapper,
  'this.host={context,applyBatch,lease};})()'];
 vm.createContext(sandbox);
 vm.runInContext(nativeCode.join('\n'),sandbox);
 sandbox.ModelAtelier = {...sandbox.native,status:()=>({selected:sandbox.selection})};
 vm.runInContext(hostCode.join('\n'),sandbox);
 const {host,native} = sandbox;
 const history = sandbox.window.SWYRL_ENGINE_EDIT_JOURNAL_521;
 history.bind();
 function dispatch(batchId, operations, frozen=host.context()){
  state.pending={operations,receiptNonce:'approved-nonce',preconditions:{leaseId:'lease',threadId:'thread',
   generationId:'generation',projectId:frozen.projectId,context:frozen}};
  return host.applyBatch({batchId,leaseId:'lease',generationId:'generation'});
 }
 return {state,doc,editable,painted,untouched,host,native,history,dispatch,sandbox};
}

(async()=>{
 const h=harness(),{state,doc,editable,painted,untouched,host,native,history,dispatch}=h;
 const before=copy(doc),snapshot=host.context();
 assert.deepEqual(copy(snapshot.meshShapeEdit),{schema:'swrlz-forge-mesh-shape-edit-v1',
  kinds:['sphere','box','cone','cylinder','loft'],editableIds:[editable.id,untouched.id]});
 assert.equal(snapshot.meshTools.schema,'swrlz-forge-mesh-tools-v2');
 assert(snapshot.meshTools.kinds.includes('lathe'));

 const loft={op:'mesh.reshape',id:editable.id,kind:'loft',path:[[0,0,0],[0,1,0]],radii:[.4,.3],segments:24};
 await dispatch('reshape-first',[loft]);
 assert.deepEqual(state.finishes.at(-1).results,[{op:'mesh.reshape',ok:true,changed:true,id:editable.id,name:editable.name,kind:'loft'}]);
 assert.equal(doc.parts[0],editable);
 assert.notEqual(editable.path,loft.path,'authored path is saved as native data rather than retaining input references');
 assert.deepEqual(copy(editable),{...before.parts[0],...Object.fromEntries(['kind','path','radii','segments'].map(k=>[k,loft[k]]))});
 assert.equal(doc.parts[1],painted);
 assert.equal(doc.parts[2],untouched);
 assert.deepEqual(copy(doc.assemblies),before.assemblies);
 assert.deepEqual(copy(doc.meshGroups),before.meshGroups);
 assert.equal(history.depths('model').undoDepth,1);
 assert.equal(host.context().epoch,snapshot.epoch+1);
 await dispatch('reshape-first',[loft]);
 assert.equal(state.downloads,1,'the same batch is ignored before requesting operations');
 assert.equal(history.depths('model').undoDepth,1);

 const beforeProfile=host.context();
 const profileEdit={...loft,radii:[.5,.3]};
 await dispatch('reshape-profile',[profileEdit]);
 assert.equal(host.context().epoch,beforeProfile.epoch+1,'a geometry-only edit advances the leased epoch');
 assert.deepEqual(copy(host.context().meshes),copy(beforeProfile.meshes),'shape edits retain identity and transform metadata');
 assert.equal(history.depths('model').undoDepth,2);
 await dispatch('stale-profile',[loft],beforeProfile);
 assert.equal(state.finishes.at(-1).results[0].code,'STALE_NATIVE_PRECONDITIONS');
 assert.deepEqual(copy(editable.radii),profileEdit.radii);

 await dispatch('reshape-again',[profileEdit]);
 assert.equal(state.finishes.at(-1).results[0].changed,false);
 assert.equal(history.depths('model').undoDepth,2,'identical shape creates no history step');
 assert.equal(history.step(true,'model').changed,true);
 assert.deepEqual(copy(doc.parts[0].radii),loft.radii);
 assert.equal(history.step(false,'model').changed,true);
 assert.deepEqual(copy(doc.parts[0].radii),profileEdit.radii);
 const saved=copy(doc);
 const reopened=harness();
 reopened.sandbox.currentProject.modelAtelier=copy(saved);
 reopened.history.bind();
 assert.equal(reopened.sandbox.currentProject.modelAtelier.parts[0].id,editable.id);
 assert.deepEqual(copy(reopened.sandbox.currentProject.modelAtelier.parts[0].radii),profileEdit.radii);
 assert.equal(reopened.history.depths('model').undoDepth,2);

 for(const [batch,operations,code] of [
  ['mixed',[loft,{op:'mesh.set',id:editable.id,color:'#112233'}],'RESHAPE_REQUIRES_SEPARATE_BATCH'],
  ['painted',[{...loft,id:painted.id}],'MESH_RESHAPE_TARGET_PROTECTED'],
  ['missing',[{...loft,id:'missing'}],'MESH_RESHAPE_TARGET_PROTECTED'],
  ['lathe',[{op:'mesh.reshape',id:editable.id,kind:'lathe'}],'INVALID_MESH_RESHAPE'],
  ['nonfinite',[{...loft,radii:[0,.4]}],'INVALID_LOFT_PROFILE'],
  ['missing-field',[{op:'mesh.reshape',id:editable.id,kind:'loft',path:loft.path,radii:loft.radii}],'INVALID_MESH_RESHAPE_FIELDS'],
  ['extra-field',[{op:'mesh.reshape',id:editable.id,kind:'sphere',name:'Different'}],'INVALID_MESH_RESHAPE_FIELDS'],
 ]){
  await dispatch(batch,operations);
  assert.equal(state.finishes.at(-1).results[0].code,code);
  assert.deepEqual(copy(doc.parts),saved.parts,'invalid batch preserves the model');
 }

 state.scratch=true;
 assert.equal(host.context().meshShapeEdit,undefined);
 assert.throws(()=>native.chatAction(loft),/MESH_RESHAPE_TARGET_PROTECTED/);
 state.scratch=false;
 doc.rigging={bones:[]};
 assert.deepEqual(copy(host.context().meshShapeEdit.editableIds),[]);
 assert.throws(()=>native.chatAction(loft),/MESH_RESHAPE_TARGET_PROTECTED/);
 delete doc.rigging;
 state.contextMode='scene';
 assert.equal(host.context().meshShapeEdit,undefined);
 state.contextMode='model-atelier';
 state.gesture=true;
 await dispatch('gesture',[loft]);
 assert.equal(state.finishes.at(-1).results[0].code,'MESH_RESHAPE_GESTURE_ACTIVE');
 state.gesture=false;
 await dispatch('plain-shape',[{op:'mesh.reshape',id:editable.id,kind:'sphere'}]);
 assert.deepEqual(copy(doc.parts[0]),{...before.parts[0],kind:'sphere'});
 assert.equal(doc.parts.length,before.parts.length);
 assert.deepEqual(copy(doc.assemblies),before.assemblies);

 // A manual loft edit in the same durable document uses this native signal.
 const manual=harness();
 await manual.dispatch('loft-setup',[loft]);
 const frozen=manual.host.context();
 manual.native.checkpoint();
 manual.editable.radii=[.55,.3];
 manual.native.signalEdited();
 assert.equal(manual.host.context().epoch,frozen.epoch+1);
 assert.deepEqual(copy(manual.host.context().meshes),copy(frozen.meshes));
 await manual.dispatch('stale-after-native-edit',[loft],frozen);
 assert.equal(manual.state.finishes.at(-1).results[0].code,'STALE_NATIVE_PRECONDITIONS');
 assert.deepEqual(copy(manual.editable.radii),[.55,.3]);

 // The geometry capability follows the final sampled rows and shares the budget.
 const large=harness();
 large.state.summaryDetails='d'.repeat(8000);
 large.doc.parts.push(...Array.from({length:50},(_,i)=>({...plain(`part-${i}-${'r'.repeat(75)}`),name:'界'.repeat(100)})));
 const sampled=large.host.context();
 assert(sampled.meshes.length<48&&sampled.meshes.length>1);
 assert.deepEqual(copy(sampled.meshShapeEdit.editableIds),copy(sampled.meshes.map(p=>p.id)).filter(id=>id!==large.painted.id));
 assert(new TextEncoder().encode(JSON.stringify(sampled)).length<=24000);
 // Predecessor primitive plans continue through the same checked host batch.
 const legacy=harness();
 await legacy.dispatch('legacy-primitive',[{op:'mesh.add',kind:'box',name:'Fixture primitive'}]);
 const legacyReceipt=legacy.state.finishes.at(-1).results[0];
 assert.equal(legacyReceipt.ok,true,legacyReceipt.code);
 assert.equal(legacyReceipt.kind,'box');
 assert.equal(legacy.doc.parts.length,4);
 console.log('SE534_CHAT_MESH_SHAPE_EDIT_PASS: negotiated targets, stable identity, geometry epoch, Undo and Redo, stale/replay, protected sources and standalone approval batch');
})().catch(error=>{console.error(error);process.exitCode=1;});
