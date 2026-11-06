// Focused data-boundary/native-host tests. No model inference is simulated.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';

const html=fs.readFileSync(process.argv[2],'utf8');
const source=fs.readFileSync(new URL('../runtime/chat_character_tools_v11_293.js',import.meta.url),'utf8');
const section=name=>source.split(`/* SE293_${name}_START */`)[1].split(`/* SE293_${name}_END */`)[0];
const between=(start,end)=>html.slice(html.indexOf(start),html.indexOf(end,html.indexOf(start)));
const base=()=>({id:'seed',name:'Original',kind:'sphere',position:[0,1,0],rotation:[0,0,0],scale:[1,1,1],color:'#ffffff',material:'matte'});
const model={parts:[base()]};let checkpoints=0;
const native={crypto:webcrypto,Math,Number,Object,Array,structuredClone,model:()=>model,
  panel:{hidden:false},MODEL_ATELIER_LIMIT:100,MODEL_ATELIER_KINDS:['sphere','box','cone','cylinder','loft','topologyMesh'],MODEL_ATELIER_MATERIALS:['matte','silk','gloss','metal','emissive'],
  atelierLODSavedVertices:300000,atelierLODSavedTriangles:600000,
  atelierCourierBindingValid:()=>true,atelierMeshPrimitiveDensityValid:()=>true,
  atelierSculptValid:()=>true,atelierFaceSheetValid:()=>true,atelierHeadAnatomyValid:()=>true,
  partById:id=>model.parts.find(p=>p.id===id),checkpoint:()=>checkpoints++,signalEdited(){},selection:null,
  atelierCourierCamera:view=>view==='front',undo:[],redo:[]};
vm.createContext(native);
vm.runInContext(between('function atelierTopologyValid(part){','function atelierTopologyGeometry(part){')+
  between('  function checkPart(p){','  function validParts(parts){')+
  between('/* ATELIER_BRIDGE_START */','/* ATELIER_BRIDGE_END */'),native);
const action=op=>JSON.parse(JSON.stringify(native.seChatAtelierApply(op)));
const loft={op:'mesh.add',kind:'loft',name:'Tapered bent stem',path:[[0,0,0],[.2,1,.1],[0,2,0]],radii:[.1,.08,.02],segments:24,scale:[1,1,1]};
const made=action(loft);assert.equal(made.kind,'loft');assert.equal(model.parts.at(-1).segments,24);
assert.notEqual(model.parts.at(-1).path,loft.path,'input arrays are copied');
const shell={op:'mesh.add',kind:'lathe',name:'Open curved shell',profile:[[1,0],[.8,1],[0,2]],arcStart:.6,arcLength:5,segments:16,scale:[1,1,1]};
const lathe=action(shell);assert.equal(lathe.kind,'topologyMesh');
const geom=model.parts.at(-1).topologyMesh;
assert.equal(geom.positions.length/3,35);assert.equal(geom.indices.length/3,48);
assert(native.atelierTopologyValid(model.parts.at(-1)));
// Ascending profiles have outward radial normals at the first strip.
const point=i=>geom.positions.slice(i*3,i*3+3);
const [a,b,c]=geom.indices.slice(0,3).map(point),u=b.map((n,i)=>n-a[i]),v=c.map((n,i)=>n-a[i]);
const normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
assert(normal[0]*a[0]+normal[2]*a[2]>0,'shell triangle faces outward');
const count=model.parts.length,prior=checkpoints;
for(const invalid of [
  {...loft,path:[[0,0,0],[0,0,0]]},{...loft,radii:[.1]},
  {...loft,radii:[.1,0,.1]},{...loft,segments:65},{...loft,profile:[[0,0],[1,1]]},
  {...shell,arcLength:0},{...shell,profile:[[0,0],[0,1]]},
  {...shell,profile:[[1,0],[1,0]]},{...shell,path:[[0,0,0],[0,1,0]]},
  {...shell,profile:[[Infinity,0],[1,1]]}
])assert.throws(()=>action(invalid));
assert.equal(model.parts.length,count);assert.equal(checkpoints,prior,'invalid geometry records no history');
assert.throws(()=>action({op:'mesh.set',id:'seed',scale:[0,1,1]}),/INVALID_NATIVE_PART/);
assert.equal(checkpoints,prior,'invalid full candidate is rejected before native checkpoint');
assert.deepEqual(action({op:'editor.frame',view:'front'}),{framed:true,view:'front'});
assert.throws(()=>action({op:'editor.frame',view:'unknown'}),/MODEL_FRAME/);

// Use actual assembled context routines to ensure scratch/native authority and
// UTF-8 budget are truthful even with long names and maximum sampled records.
const sampleLimits=html.match(/const MAX_RAW=96\*1024\*1024,MAX_META=(\d+),MAX_BATCH=(\d+);/);
assert(sampleLimits,'assembled native snapshot/operation bounds are present');
const nativeSampleLimit=Number(sampleLimits[1]);
assert.equal(nativeSampleLimit,48,'both domains retain the existing metadata contract');
assert.equal(Number(sampleLimits[2]),64,'operation count is independent of metadata sampling');
let usingScratch=true,atelierOpened=true,scratchSelected='scratch-63';
const scratch={parts:Array.from({length:64},(_,i)=>({...base(),id:'scratch-'+i,name:'界'.repeat(100),position:[99.99999999999999,99.99999999999999,99.99999999999999]}))};
const ctx={window:{SWYRL_ENGINE_WORKSPACES:{usingScratch:()=>usingScratch,scratchModel:()=>scratch}},
  TextEncoder,crypto:webcrypto,id:()=>webcrypto.randomUUID(),projectIds:new WeakMap(),MAX_META:nativeSampleLimit,
  summaryName:v=>String(v??'').slice(0,100),bounded:v=>typeof v==='string'&&!!v,
  ModelAtelier:{status:()=>({open:atelierOpened,selected:scratchSelected})},actors:[],selected:null,playing:false,simulating:false,
  document:{getElementById:()=>({disabled:false})},currentProject:{name:'Unrelated scene',kind:'sheep-tag',instanceId:'loaded-instance',modelAtelier:{parts:[base()]}},
  se175Starters:()=>[],se175UpdateLabel(){},dirty:false,epoch:0};
vm.createContext(ctx);
vm.runInContext(section('HOST').split('let se293BatchTail')[0]+
  between('function getProjectId(){','function isVisible(){')+
  between('function prioritized(items,selectedId){','function studioSnapshot(workspace){'),ctx);
// v175 helpers lie between prioritized and studioSnapshot in the assembled
// source; read the required native routines explicitly to avoid re-running UI.
vm.runInContext(between('function studioSnapshot(workspace){','function se178EnrichContext(ctx){')+
  between('function se178EnrichContext(ctx){','function se178AnalyzeWorkspace(){')+
  between('function context(){','function setStatus('),ctx);
const scratchCtx=ctx.context();
assert.equal(scratchCtx.project.name,'Untitled model');assert.equal(scratchCtx.project.kind,'model-atelier');
assert.equal(scratchCtx.totalMeshes,64);assert.equal(scratchCtx.meshes[0].id,'scratch-63');
assert(scratchCtx.meshes.every(p=>p.id.startsWith('scratch-')));
assert(new TextEncoder().encode(JSON.stringify(scratchCtx)).length<=32768);
assert.equal(scratchCtx.workspaceAudit.sampled,scratchCtx.meshes.length);
assert.equal(scratchCtx.meshTools.schema,'swrlz-forge-mesh-tools-v2');
// Both old and new Chat backends receive at most 48 mesh metadata rows.
// Building 64 parts still reports true totals and keeps the selected final part.
for(let meshCount=49;meshCount<=64;meshCount++){
  scratch.parts=Array.from({length:meshCount},(_,i)=>({...base(),id:'scratch-'+i,name:'Model mesh '+i}));
  scratchSelected='scratch-'+(meshCount-1);
  const modelCtx=ctx.context();
  assert.equal(modelCtx.workspace,'model-atelier');assert.equal(modelCtx.meshes.length,48);
  assert.equal(modelCtx.totalMeshes,meshCount);assert.equal(modelCtx.selectedId,scratchSelected);
  assert.equal(modelCtx.meshes[0].id,scratchSelected);assert.equal(modelCtx.workspaceAudit.sampled,48);
}
usingScratch=false;const loadedCtx=ctx.context();assert.equal(loadedCtx.projectId,'loaded-instance');
assert.notEqual(scratchCtx.projectId,loadedCtx.projectId);assert.equal(loadedCtx.meshes[0].id,'seed');

// The existing native studio validator accepts at most 48 scene actor rows.
// Larger true scene totals must not break material assignment in 49–64-actor
// scenes, and an actor outside the first 48 must still be selected truthfully.
atelierOpened=false;
for(let actorCount=49;actorCount<=64;actorCount++){
  ctx.actors=Array.from({length:actorCount},(_,i)=>({name:'Scene actor '+i,userData:{id:'actor-'+i,actorType:'mesh'},
    position:{toArray:()=>[i,0,0]},rotation:{x:0,y:0,z:0},scale:{toArray:()=>[1,1,1]}}));
  ctx.selected=ctx.actors.at(-1);
  const sceneCtx=ctx.context();
  assert.equal(sceneCtx.workspace,'scene');assert.equal(sceneCtx.actors.length,48,'scene sample retains native studio contract');
  assert.equal(sceneCtx.totalActors,actorCount,'scene total includes every actual actor');
  assert.equal(sceneCtx.selectedId,'actor-'+(actorCount-1));assert.equal(sceneCtx.actors[0].id,sceneCtx.selectedId);
  assert.equal(sceneCtx.workspaceAudit.sampled,48);assert.equal(sceneCtx.meshes.length,0);
}
atelierOpened=true;ctx.actors=[];ctx.selected=null;

// Scratch Undo restores the draft object in place and leaves the scene project
// extension intact; the loaded model identity still follows the original path.
const unrelated=ctx.currentProject.modelAtelier;
Object.assign(ctx,{model:()=>scratch,modelSnapshot:()=>JSON.stringify(scratch),undo:[JSON.stringify({parts:[{...base(),name:'Before scratch edit'}]})],redo:[],selection:'scratch-63',
  atelierMeshIds:[],atelierMeshAdding:false,atelierGroupCurrent:null,signalEdited(){},atelierAssemblyRefresh(){},atelierRefTransient:new Map(),atelierRefPaint(){}});
usingScratch=true;
vm.runInContext(between('  function historyStep(backward){','// §wyrl§ v11.4'),ctx);
ctx.historyStep(true);
assert.equal(scratch.parts[0].name,'Before scratch edit');assert.equal(ctx.currentProject.modelAtelier,unrelated);
assert.equal(ctx.context().projectId,scratchCtx.projectId,'scratch undo retains draft lease identity');

// Run the exact new host loop with actual sequential async pauses and inspect
// receipt/progress behavior. The browser/account/model are controlled fixtures.
const events=[],requests=[];let pendingOps=[],batchContext,ownerEdit=false,cancelAfter=0,clock=0,applicationWindowMs=25000;
const current={projectId:'project',workspace:'model-atelier',mode:'edit',epoch:0,selectedId:'seed'};
const host={console,Math,Promise,Date:{now:()=>clock},setTimeout:fn=>{clock+=100;queueMicrotask(()=>{if(ownerEdit){current.epoch++;ownerEdit=false;}if(cancelAfter&&events.length>=cancelAfter)host.lease=null;fn();});return 1;},clearTimeout(){},
  context:()=>({...current}),lease:{leaseId:'lease',threadId:'thread',projectId:'project'},isVisible:()=>true,
  seenBatches:new Set(),heartbeatTimer:null,heartbeat(){},MAX_BATCH:64,port:{},hostId:'host',channelId:'channel',
  summaryName:v=>String(v).slice(0,100),setStatus(){},send:(type,value)=>events.push({type,...value}),
  validateOperation:op=>{if(op.op==='invalid')throw Error('INVALID_OPERATION');},
  execute:op=>{current.epoch++;return {changed:true,id:'made-'+current.epoch,name:op.name};},
  se175Create:async op=>{await Promise.resolve();current.projectId='new-project';return {changed:true,projectId:'new-project',name:op.name,localSaved:true};},
  se175UpdateLabel(){},revoke:()=>{host.lease=null;},currentProject:{name:'Created project'},
  hostRequest:async(path,body)=>{
    requests.push({path,body});
    if(path.endsWith('/take'))return {operations:pendingOps,...(applicationWindowMs===undefined?{}:{applicationWindowMs}),receiptNonce:'PRIVATE-NONCE',preconditions:{leaseId:'lease',threadId:'thread',projectId:batchContext.projectId,generationId:'gen',context:batchContext}};
    return {};
  }};
vm.createContext(host);vm.runInContext(section('HOST'),host);
async function batch(id,ops){pendingOps=ops;batchContext={...current};await host.applyBatch({batchId:id,leaseId:'lease',generationId:'gen'});return requests.filter(r=>r.path.endsWith('/finish')).at(-1).body;}
let result=await batch('one',[{op:'mesh.add',name:'Body'},{op:'mesh.add',name:'Hood'},{op:'editor.frame',view:'front'}]);
assert.equal(result.results.filter(r=>r.ok).length,3);assert.equal(events.length,3);
assert(events.every((e,i)=>e.completed===i+1&&e.total===3&&e.batchId==='one'&&e.generationId==='gen'&&e.ok));
assert(!JSON.stringify(events).includes('PRIVATE-NONCE'));
result=await batch('sixtyfour',Array.from({length:64},(_,i)=>({op:'mesh.add',name:'Part '+i})));
assert.equal(result.results.filter(r=>r.ok).length,64);
assert(requests.some(r=>r.path==='heartbeat'),'longer progressive batches renew the host lease');
applicationWindowMs=undefined;
result=await batch('legacy-sixteen',Array.from({length:16},()=>({op:'mesh.add',name:'Legacy part'})));
assert.equal(result.results.filter(r=>r.ok).length,16,'old Chat backend without a window retains its 16-operation path');
const legacyEpoch=current.epoch;
result=await batch('legacy-seventeen',Array.from({length:17},()=>({op:'mesh.add',name:'Rejected legacy extension'})));
assert.equal(current.epoch,legacyEpoch,'missing deadline rejects an extended batch before any native edit');
assert(result.results.every(r=>!r.ok&&r.code==='MISSING_BATCH_WINDOW'));
applicationWindowMs=1300;
result=await batch('deadline',Array.from({length:6},(_,i)=>({op:'mesh.add',name:'Timed '+i})));
assert.equal(result.results.filter(r=>r.ok).length,3);
assert.equal(result.results[3].code,'EDITOR_BATCH_DEADLINE');
applicationWindowMs=25000;
ownerEdit=true;
result=await batch('two',[{op:'mesh.add',name:'First'},{op:'mesh.add',name:'Must stop'},{op:'mesh.add',name:'Skipped'}]);
assert.equal(result.results[0].ok,true);assert.equal(result.results[1].code,'EDITOR_CHANGED_DURING_BATCH');assert.equal(result.results[2].code,'PREVIOUS_OPERATION_FAILED');
cancelAfter=events.length+1;
result=await batch('cancel',[{op:'mesh.add',name:'Before Stop'},{op:'mesh.add',name:'After Stop'}]);
assert.equal(result.results[0].ok,true);assert.equal(result.results[1].code,'EDITOR_DETACHED','lease revoke stops next yielded mutation');
host.lease={leaseId:'lease',threadId:'thread',projectId:'project'};cancelAfter=0;
result=await batch('create',[{op:'project.create',name:'Created project'}]);
assert.equal(result.results[0].projectId,'new-project');assert.equal(result.results[0].localSaved,true);assert.equal(host.lease,null,'project creation retires old grant');
console.log('CHAT_CHARACTER_TOOLS_V11_293_PASS');
