#!/usr/bin/env node
'use strict';
// Exercise the actual composed native loader, checked link wrapper, outer
// project-ID adapter and revision cache. The harness supplies only UI,
// authorized transport and the already separate native import boundary.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(process.argv[2], 'utf8');
const remoteId = 'a'.repeat(32);
const original = {
 project: {instanceId:'original-local',kind:'model-atelier',name:'Open workspace'},
 editor: {}, scene: {actors:[]},
};
const saved = {
 project: {instanceId:'saved-local',kind:'model-atelier',name:'Saved model',modelAtelier:{parts:[]}},
 editor: {}, scene: {actors:[]},
};

function between(text,start,end){
 const first = text.indexOf(start);
 const last = text.indexOf(end,first+start.length);
 assert(first>=0&&last>first,`Missing composed source boundary: ${start}`);
 return text.slice(first,last);
}

const loader = between(source,'async function loadCloud(requestedId){','const SE184_SVG=');
const link = between(source,'const se371PreviousLoadCloud=loadCloud;','function se371NewName(');
const adapter = between(source,'const se528PriorLoadCloud=loadCloud;','let se528SaveBusy=false;');
const cache = between(source,'/* SE518_REVISION_CACHE_START','/* SE518_REVISION_CACHE_END');
const previous = fs.readFileSync(path.join(__dirname,'../runtime/model_account_project_repair_v11_528.js'),'utf8');
const priorAdapter = between(previous,'const se528PriorLoadCloud=loadCloud;','let se528SaveBusy=false;');

function harness(outer = adapter){
 const calls = {downloads:[],imports:[],links:[],startup:[],localLoads:[]};
 const state = {confirm:true,error:'',remoteRevision:5,rawProject:saved,metas:[],localRows:new Map()};
 const options=[{value:'active'},{value:`cloud:${remoteId}`}];
 const cloudList={
  options,
  append(option){options.push(option);option.remove=()=>options.splice(options.indexOf(option),1);},
  get value(){return state.choice||'';},
  set value(choice){state.choice=options.some(option=>option.value===choice)?choice:'';},
 };
 cloudList.value=`cloud:${remoteId}`;
 const diagnostics = {
  reset(){state.error='';},
  failure(error){state.error=String(error.message||error);return state.error;},
  getError(){return state.error;},
  async fetchProject(id){
   calls.downloads.push(id);
   if(state.networkError)throw Error(state.networkError);
   state.onFetch?.();
   const bytes=new TextEncoder().encode(JSON.stringify(state.rawProject)).buffer;
   return {bytes,project:{id:state.returnedId??id,revision:state.remoteRevision,name:saved.project.name}};
  },
 };
 const sandbox={
  ArrayBuffer,TextDecoder,MAX_RAW:96*1024*1024,ready:true,se176AccountConnected:true,
  cloudBusy:false,se175Transition:false,se175LocalLoading:false,
  currentProject:structuredClone(original.project),revision:1,dirty:false,
  cloudList,cloudRefs:new Map(),se494TrustedLoadCache:new Map(),se176CloudRows:[],
  se175LocalList:{value:''},document:{createElement:()=>({})},
  se175RefreshLocal:async()=>{},se176RefreshProjects:async()=>{},
  se175Read:async id=>id?state.localRows.get(id):state.metas,
  se175LoadLocal:async()=>{
   const id=sandbox.se175LocalList.value;
   calls.localLoads.push(id);sandbox.currentProject=state.localRows.get(id).data.project;
  },
  getProjectId:()=>sandbox.currentProject.instanceId,
  bounded:(value,max)=>typeof value==='string'&&value.length>0&&value.length<=max,
  summaryName:String,setStatus:message=>{state.status=message;},
  se371HasSavedIdentity:()=>true,se371RememberLink:async (id,receipt)=>calls.links.push([id,receipt.revision]),
  revoke:()=>{},se183StartLoad:()=>1,se183LoadStep:()=>{},se183PaintNext:async()=>{},
  se183FinishLoad:(_ticket,ok)=>{state.finished=ok;},
  ModelAtelier:{syncProject(){},open(){}},
  window:{confirm:()=>state.confirm,SWYRL_ENGINE_PROJECT_LOAD_493:diagnostics,
   SWYRL_ENGINE_STARTUP_476:{markLoaded:(...args)=>calls.startup.push(args)},
   SWYRL_ENGINE_AGENT:{inspectScene:()=>structuredClone(original),loadScene(data){
    calls.imports.push(data.project.instanceId);
    if(state.badImport&&data.project.instanceId===saved.project.instanceId)throw Error('Invalid model data');
    sandbox.currentProject=data.project;
   }},
  },
 };
 vm.runInNewContext([loader,link,outer,cache,'this.openNative=loadCloud;'].join('\n'),sandbox);
 return {calls,state,sandbox,cloudList,diagnostics,open:sandbox.openNative,
  cached:sandbox.window.SWYRL_ENGINE_CLOUD_CACHE_518};
}

(async()=>{
 const previous=harness(priorAdapter);
 assert.equal(await previous.open(remoteId),false);
 assert.deepEqual(previous.calls.downloads,[]);
 assert.equal(previous.state.status,'Choose a Google-saved project first.');
 assert.equal(previous.diagnostics.getError(),'','Historical card had no diagnostic to display');
 previous.sandbox.cloudRefs.set('original-local',{id:remoteId,revision:5});
 assert.equal(await previous.open(remoteId),true,'Historical linked state could mask a failed open');
 assert.deepEqual(previous.calls.downloads,[]);

 for(const openId of [remoteId,`cloud:${remoteId}`,undefined]){
  const candidate=harness();
  assert.equal(await candidate.open(openId),true);
  assert.deepEqual(candidate.calls.downloads,[remoteId]);
  assert.deepEqual(candidate.calls.imports,['saved-local']);
  assert.deepEqual(candidate.calls.links,[['saved-local',5]]);
  assert.equal(candidate.sandbox.cloudRefs.get('saved-local').revision,5);
  assert.equal(candidate.cloudList.value,`cloud:${remoteId}`);
  assert.equal(candidate.cloudList.options.length,2);
 }

 const cancelled=harness();
 cancelled.sandbox.dirty=true;
 cancelled.state.confirm=false;
 cancelled.sandbox.cloudRefs.set('original-local',{id:remoteId,revision:4});
 assert.equal(await cancelled.open(remoteId),false);
 assert.deepEqual(cancelled.calls.downloads,[]);
 assert.match(cancelled.diagnostics.getError(),/cancelled to preserve unsaved changes/);

 for(const [fields,error] of [
   [{networkError:'Account download unavailable'},/Account download unavailable/],
   [{remoteRevision:0},/Invalid account project download or revision/],
   [{returnedId:'wrong-project'},/Invalid account project download or revision/],
   [{rawProject:{project:{}}},/Invalid native project/],
 ]){
  const candidate=harness();
  Object.assign(candidate.state,fields);
  candidate.sandbox.cloudRefs.set('original-local',{id:remoteId,revision:4});
  assert.equal(await candidate.open(remoteId),false);
  assert.deepEqual(candidate.calls.imports,[]);
  assert.equal(candidate.sandbox.currentProject.instanceId,'original-local');
  assert.match(candidate.diagnostics.getError(),error);
 }

 const changed=harness();
 changed.state.onFetch=()=>{changed.sandbox.revision++;};
 assert.equal(await changed.open(remoteId),false);
 assert.deepEqual(changed.calls.imports,[]);
 assert.match(changed.diagnostics.getError(),/WORKSPACE_CHANGED_DURING_ACCOUNT_DOWNLOAD/);

 const rollback=harness();
 rollback.state.badImport=true;
 assert.equal(await rollback.open(remoteId),false);
 assert.deepEqual(rollback.calls.imports,['saved-local','original-local']);
 assert.equal(rollback.sandbox.currentProject.instanceId,'original-local');
 assert.match(rollback.diagnostics.getError(),/Invalid model data/);

 const busy=harness();
 busy.sandbox.cloudBusy=true;
 assert.equal(await busy.open(remoteId),false);
 assert.deepEqual(busy.calls.downloads,[]);
 assert.match(busy.diagnostics.getError(),/Another account operation is in progress/);

 for(const cachedRevision of [4,5]){
  const candidate=harness();
  const cachedRow={id:'saved-local',cloudRef:{id:remoteId,revision:cachedRevision},data:saved};
  candidate.state.metas=[cachedRow];candidate.state.localRows.set(cachedRow.id,cachedRow);
  candidate.sandbox.se176CloudRows=[{id:remoteId,revision:5}];
  assert.equal(await candidate.cached.load(remoteId),true);
  assert.equal(candidate.sandbox.currentProject.instanceId,'saved-local');
  assert.equal(candidate.cached.inspect().status,cachedRevision===5?'cache-hit':'network-loaded');
  assert.deepEqual(candidate.calls.downloads,cachedRevision===5?[]:[remoteId]);
 }
 console.log('SE533_ACCOUNT_OPEN_PASS: legacy rejection reproduced, confirmed import, error retention, rollback and revision cache');
})().catch(error=>{console.error(error);process.exitCode=1;});
