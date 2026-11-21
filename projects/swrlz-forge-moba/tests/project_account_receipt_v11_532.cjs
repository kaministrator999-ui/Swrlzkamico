#!/usr/bin/env node
'use strict';
// Run without arguments against the actual repository save-function chain, or
// pass the canonical assembled HTML/module to verify its shipped composition.
// Only DOM, IndexedDB transport and authenticated RPC are harness boundaries;
// native save, revision preparation, wrappers and receipt validation are real.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {spawnSync}=require('node:child_process');
const {webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'..');
const read=rel=>fs.readFileSync(path.join(root,rel),'utf8');
const clone=value=>structuredClone(value);
function between(text,start,end){
 const a=text.indexOf(start),b=text.indexOf(end,a+start.length);
 assert(a>=0&&b>a,'Missing save-chain boundary '+start);
 return text.slice(a,b);
}
function nativeSave(text){
 const hit=/async\s+function\s+saveCloud\s*\(\s*\)\s*\{/.exec(text);
 assert(hit,'Native declared saveCloud is missing');
 const rest=text.slice(hit.index+hit[0].length);
 const next=/^[ \t]*(?:async[ \t]+)?function[ \t]+[A-Za-z_$][\w$]*[ \t]*\(/m.exec(rest);
 assert(next,'Native saveCloud following function is missing');
 return text.slice(hit.index,hit.index+hit[0].length+next.index);
}
function sourceChain(){
 const patch=read('patches/v11_486_project_revisions.py');
 const native=between(patch,'save_replacement="""','"""').slice('save_replacement="""'.length);
 const safe=read('runtime/project_safe_save_v11_371.js');
 return native+'\n'+safe.slice(0,safe.indexOf('const se371PreviousLoadCloud='))+'\n'+
  between(safe,'async function se371SaveLocal(){','async function se371Clone(')+'\n'+
  read('runtime/account_project_naming_v11_488.js')+'\n'+
  read('runtime/project_account_save_v11_529.js');
}
function repair(source){
 const script='import importlib.util,sys\n'+
  'p=sys.argv[1]\n'+
  's=importlib.util.spec_from_file_location("account532",p)\n'+
  'm=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n'+
  'sys.stdout.write(m.apply_save_repair(sys.stdin.read()))\n';
 const result=spawnSync('python',['-c',script,path.join(root,'patches/v11_532_project_account_save_receipt.py')],
  {input:source,encoding:'utf8',maxBuffer:20*1024*1024});
 assert.equal(result.status,0,result.stderr);
 return result.stdout;
}
const original=sourceChain();
let fixed;
if(process.argv[2]){
 const compiled=fs.readFileSync(process.argv[2],'utf8');
 const safe=between(compiled,'const se371CloudLinks=new Map();','const se371PreviousLoadCloud=');
 const local=between(compiled,'async function se371SaveLocal(){','async function se371Clone(');
 const naming=between(compiled,'/* §E v11.488 — naming guard around existing account writes.',
  'window.SWYRL_ENGINE_SAFE_PROJECTS_371=Object.freeze');
 fixed=nativeSave(compiled)+'\n'+safe+'\n'+local+'\n'+naming+'\n'+
  between(compiled,'/* SE532_PROJECT_ACCOUNT_SAVE_RECEIPT_START */','/* SE532_PROJECT_ACCOUNT_SAVE_RECEIPT_END */')+'\n'+
  between(compiled,'/* SE529_NATIVE_PROJECT_ACCOUNT_SAVE_START */','/* SE529_NATIVE_PROJECT_ACCOUNT_SAVE_END */');
 assert(fixed.includes('se532ProjectSaveRpc(\'cloud.save\''));
}else fixed=repair(original);

function backend(){return {records:new Map(),sequence:0};}
function harness(source,{db=new Map(),remote=backend(),project=null}={}){
 const calls=[],events=[];
 const state={failList:0,failLoad:0,loseNextAck:false,failNextPendingStore:false,
  afterPendingStore:null,hiddenIds:new Set(),asset:0,localWrites:0};
 const projectData=project||{instanceId:'local-dragon-test',name:'Receipt regression project',
  projectName:'Receipt regression project',canonicalId:'blank-model',se371TemplateSource:false,
  sourceStarterId:'blank-model',kind:'model-atelier',testNote:'initial'};
 const bytes=doc=>new TextEncoder().encode(JSON.stringify(doc)).buffer;
 const resultFor=record=>({project:{id:record.id,name:record.name,revision:record.revision},
  bytes:record.bytes.slice(0)});
 const sandbox={
  console:{warn(){}},TextEncoder,TextDecoder,ArrayBuffer,Uint8Array,structuredClone,crypto:webcrypto,
  btoa,atob,Blob,Response,CompressionStream,DecompressionStream,
  CustomEvent:class{constructor(name,opts){this.type=name;this.detail=opts.detail;}},
  document:{getElementById(){return null;}},
  window:{dispatchEvent:event=>events.push(event),prompt:()=>{throw Error('Unexpected naming prompt');},
   SWYRL_ENGINE_WORKSPACES:{modelerActive:()=>true},
   SWYRL_ENGINE_ASSET_LIBRARY:{save:async()=>{state.asset++;return true;}},
   SWYRL_ENGINE_AGENT:{inspectScene:()=>({project:clone(sandbox.currentProject),editor:{},scene:{actors:[]}})}},
  currentProject:clone(projectData),cloudRefs:new Map(),status:{textContent:'',dataset:{}},
  ready:true,se176AccountConnected:true,cloudBusy:false,se175Transition:false,se175LocalLoading:false,
  playing:false,simulating:false,se175Saving:null,se170Active:'starter',se528SaveAccount:null,
  frame:{src:'https://kamiloki-swyrlz.hf.space'},CHAT_ORIGIN:'https://kamiloki-swyrlz.hf.space',MAX_RAW:96*1024*1024,
  bounded:(value,max)=>typeof value==='string'&&value.length>0&&value.length<=max,
  summaryName:value=>String(value||''),getProjectId:()=>sandbox.currentProject.instanceId,
  revoke:()=>{},markSaved:()=>{},se175UpdateLabel:()=>{},se175LocalMessage:()=>{},
  se176RefreshProjects:async()=>{},se175RefreshLocal:async()=>{},se170Refresh:async()=>{},
  se175StampProject:(id,name,starter)=>Object.assign(sandbox.currentProject,{instanceId:id,name,projectName:name,sourceStarterId:starter}),
  se371Clone:async()=>{throw Error('Unexpected starter cloning');},
  setStatus:(message,error=false)=>{sandbox.status.textContent=message;sandbox.status.dataset.error=String(error);},
  se175Snapshot:()=>({id:sandbox.currentProject.instanceId,name:sandbox.currentProject.projectName,
   starterId:sandbox.currentProject.sourceStarterId,data:sandbox.window.SWYRL_ENGINE_AGENT.inspectScene()}),
  se175Read:async key=>key?clone(db.get(key)):clone([...db.values()].map(({data,...row})=>row)),
  se175Store:async rows=>{
   if(state.failNextPendingStore&&rows.some(row=>row.se532PendingAccountSave)){
    state.failNextPendingStore=false;throw Error('LOCAL_PROJECT_SAVE_FAILED');
   }
   for(const row of rows)db.set(row.id,clone(row));state.localWrites++;
   if(rows.some(row=>row.se532PendingAccountSave)&&state.afterPendingStore){
    const hook=state.afterPendingStore;state.afterPendingStore=null;hook();
   }
  },
  se175Db:async()=>({close(){},transaction(){
   const tx={objectStore(name){return {
    get(id){const request={};queueMicrotask(()=>{
     request.result=clone(db.get(id));request.onsuccess();queueMicrotask(()=>tx.oncomplete());
    });return request;},
    put(row){if(name==='projects')db.set(row.id,clone(row));}
   };}};return tx;
  }}),
  rpc:async(type,payload={})=>{
   calls.push({type,projectId:payload.projectId||null,expectedRevision:payload.expectedRevision});
   if(type==='cloud.list'){
    if(state.failList-->0)throw Error('HTTP 503');
    return {projects:[...remote.records.values()].filter(r=>!state.hiddenIds.has(r.id))
     .map(({id,name,revision})=>({id,name,revision}))};
   }
   if(type==='cloud.load'){
    if(state.failLoad-->0)throw Error('HTTP 503');
    const record=remote.records.get(payload.projectId);
    if(!record||state.hiddenIds.has(record.id))throw Error('PROJECT_NOT_FOUND');
    return resultFor(record);
   }
   assert.equal(type,'cloud.save','Unexpected RPC');
   let record;
   if(payload.projectId){
    record=remote.records.get(payload.projectId);
    if(!record||state.hiddenIds.has(record.id))throw Error('PROJECT_NOT_FOUND');
    assert.equal(record.revision,payload.expectedRevision,'CAS must target current account revision');
   }else{
    assert.equal(payload.expectedRevision,0);
    record={id:'account-project-'+(++remote.sequence),revision:0};remote.records.set(record.id,record);
   }
   record.revision++;record.name=payload.name;record.bytes=payload.bytes.slice(0);
   if(state.loseNextAck){state.loseNextAck=false;throw Error('Chat connection timed out.');}
   return {durable:true,project:{id:record.id,name:record.name,revision:record.revision}};
  }
 };
 vm.createContext(sandbox);
 vm.runInContext(read('runtime/project_revisions_v11_486.js')+
  '\nwindow.SWYRL_ENGINE_REVISIONS_486={...SWYRL_ENGINE_REVISIONS_486,recordLocal:async()=>{}};',sandbox);
 vm.runInContext(source+'\nthis.testSave=se529SaveNativeProjectToAccount;'+
  '\nthis.testAssetSave=()=>saveCloud();'+
  '\nthis.testCheckedSave=()=>se488PreviousAccountSave();'+
  '\nthis.testLinks=se371CloudLinks;'+
  '\nthis.testPending=typeof se532PendingProjectSaves===\'undefined\'?new Map():se532PendingProjectSaves;'+
  '\nthis.testExplicitLoad=async remoteId=>{const loaded=await rpc(\'cloud.load\',{projectId:remoteId});'+
  'currentProject=JSON.parse(new TextDecoder().decode(loaded.bytes)).project;'+
  'cloudRefs.set(getProjectId(),loaded.project);await se371RememberLink(getProjectId(),loaded.project);};',sandbox);
 return {sandbox,state,calls,events,db,remote,save:()=>sandbox.testSave(),
  writes:()=>calls.filter(c=>c.type==='cloud.save').length,
  row:()=>db.get(sandbox.currentProject.instanceId),bytes};
}
async function main(){
 // Negative control exercises the historical raw function rather than a stub
 // that fabricates a true return and hides the original shipping defect.
 const old=harness(original),oldResult=await old.save();
 assert.equal(oldResult.ok,false);assert.equal(oldResult.error,'ACCOUNT_SAVE_UNCONFIRMED');
 assert.equal(old.writes(),1);assert.equal(old.remote.records.size,1);

 const good=harness(fixed),first=await good.save();
 assert.equal(first.ok,true);assert.equal(first.revision,1);assert.equal(good.writes(),1);
 assert.equal(good.row().cloudRef.id,first.projectId);assert.equal(good.row().cloudRef.revision,1);
 assert.equal(good.row().se532PendingAccountSave,undefined);assert.equal(good.state.asset,0);
 good.sandbox.currentProject.testNote='second revision';
 const second=await good.save();
 assert.equal(second.ok,true);assert.equal(second.projectId,first.projectId);assert.equal(second.revision,2);
 assert.equal(good.remote.records.size,1);assert.equal(good.writes(),2);
 const stored=JSON.parse(new TextDecoder().decode(good.remote.records.get(first.projectId).bytes));
 assert.equal(stored.se486History.entries.length,1,'Native rolling revision preparation must run');
 assert.equal(good.row().cloudRef.revision,2);
 await good.sandbox.testAssetSave();assert.equal(good.state.asset,1,'Separate model asset dispatcher remains reachable');

 const otherNativeRoute=harness(fixed);
 assert.equal(await otherNativeRoute.sandbox.testCheckedSave(),true);
 assert.equal(otherNativeRoute.row().se532PendingAccountSave,undefined,
  'All checked native routes clear a durable acknowledgement at the shared link boundary');
 assert.equal(await otherNativeRoute.sandbox.testCheckedSave(),true);
 assert.equal(otherNativeRoute.writes(),2);assert.equal(otherNativeRoute.remote.records.size,1);
 assert.equal(otherNativeRoute.row().cloudRef.revision,2);
 assert.equal(otherNativeRoute.sandbox.testPending.size,0);

 // Default startup has not called se175Read: both maps start empty. Restore
 // the persisted link BEFORE v529 can overwrite that row with a local save.
 const restarted=harness(fixed,{db:good.db,remote:good.remote,project:good.row().data.project});
 assert.equal(restarted.sandbox.cloudRefs.size,0);assert.equal(restarted.sandbox.testLinks.size,0);
 const resumed=await restarted.save();
 assert.equal(resumed.ok,true);assert.equal(resumed.projectId,first.projectId);assert.equal(resumed.revision,3);
 assert.equal(restarted.remote.records.size,1);assert.equal(restarted.calls[0].type,'cloud.list');
 assert.equal(restarted.row().cloudRef.revision,3);

 // Authenticated preflight read failure never becomes a pending write and can
 // safely be retried. A newer account revision must stop before cloud.save.
 const readFail=harness(fixed,{db:good.db,remote:good.remote,project:restarted.row().data.project});
 readFail.state.failList=1;
 assert.equal((await readFail.save()).ok,false);assert.equal(readFail.writes(),0);
 assert.equal(readFail.sandbox.testPending.size,0);assert.equal((await readFail.save()).ok,true);
 const stale=harness(fixed,{db:good.db,remote:good.remote,project:readFail.row().data.project});
 stale.remote.records.get(first.projectId).revision++;
 assert.equal((await stale.save()).ok,false);assert.equal(stale.writes(),0);
 assert.match(stale.sandbox.status.textContent,/revision changed/i);
 assert.equal(stale.sandbox.testPending.size,0);

 const foreign=harness(fixed,{db:good.db,remote:good.remote,project:readFail.row().data.project});
 foreign.state.hiddenIds.add(first.projectId);
 assert.equal((await foreign.save()).ok,false);assert.equal(foreign.writes(),0);
 assert.match(foreign.sandbox.status.textContent,/not in the signed-in account/i);

 const pendingKnown=harness(fixed);const knownFirst=await pendingKnown.save();
 pendingKnown.sandbox.currentProject.testNote='acknowledgement lost';pendingKnown.state.loseNextAck=true;
 assert.equal((await pendingKnown.save()).ok,false);assert.equal(pendingKnown.writes(),2);
 assert(pendingKnown.row().se532PendingAccountSave,'Persist intent before cloud dispatch');
 const recovered=harness(fixed,{db:pendingKnown.db,remote:pendingKnown.remote,project:pendingKnown.row().data.project});
 const receipt=await recovered.save();
 assert.equal(receipt.ok,true);assert.equal(receipt.projectId,knownFirst.projectId);assert.equal(receipt.revision,2);
 assert.equal(recovered.writes(),0,'Recover confirmed bytes/revision without replaying cloud.save');
 assert.equal(recovered.row().se532PendingAccountSave,undefined);assert.equal(recovered.row().cloudRef.revision,2);

 const pendingNew=harness(fixed);pendingNew.state.loseNextAck=true;
 assert.equal((await pendingNew.save()).ok,false);assert.equal(pendingNew.writes(),1);
 const newId=[...pendingNew.remote.records.keys()][0];
 assert.equal((await pendingNew.save()).ok,false);assert.equal(pendingNew.writes(),1,'Unknown new-project outcome must not create a duplicate');
 const pendingReload=harness(fixed,{db:pendingNew.db,remote:pendingNew.remote,project:pendingNew.row().data.project});
 assert.equal((await pendingReload.save()).ok,false);assert.equal(pendingReload.writes(),0);
 assert.equal(pendingReload.calls.length,0,'Do not search remote names to guess a new project ID');
 await pendingReload.sandbox.testExplicitLoad(newId);
 const loadedReceipt=await pendingReload.save();
 assert.equal(loadedReceipt.ok,true);assert.equal(loadedReceipt.projectId,newId);assert.equal(loadedReceipt.revision,1);
 assert.equal(pendingReload.writes(),0,'Explicit authenticated load supplies identity; receipt recovery adds no revision');
 assert.equal(pendingReload.remote.records.size,1);

 const mismatch=harness(fixed);const mismatchFirst=await mismatch.save();mismatch.state.loseNextAck=true;
 assert.equal((await mismatch.save()).ok,false);
 const wrong=mismatch.remote.records.get(mismatchFirst.projectId),wrongDoc=JSON.parse(new TextDecoder().decode(wrong.bytes));
 wrongDoc.project.testNote='different remote content';wrong.bytes=mismatch.bytes(wrongDoc);
 const before=mismatch.writes();assert.equal((await mismatch.save()).ok,false);assert.equal(mismatch.writes(),before);
 assert(mismatch.row().se532PendingAccountSave,'Mismatched content must retain the uncertainty guard');

 const localFail=harness(fixed);localFail.state.failNextPendingStore=true;
 assert.equal((await localFail.save()).ok,false);assert.equal(localFail.writes(),0);
 assert.equal(localFail.row().se532PendingAccountSave,undefined);assert.equal(localFail.sandbox.testPending.size,0);
 assert.equal((await localFail.save()).ok,true,'Failure before dispatch permits a safe retry');
 const switched=harness(fixed);
 switched.state.afterPendingStore=()=>{
  const latest=clone(switched.row());latest.data.project.testNote='newer local autosave';
  switched.db.set(latest.id,latest);switched.sandbox.currentProject.testNote='newer local autosave';
  switched.sandbox.se176AccountConnected=false;
 };
 assert.equal((await switched.save()).ok,false);assert.equal(switched.writes(),0);
 assert.equal(switched.row().data.project.testNote,'newer local autosave','Abort cleanup must preserve later local edits');
 assert.equal(switched.row().se532PendingAccountSave,undefined);
 switched.sandbox.se176AccountConnected=true;
 assert.equal((await switched.save()).ok,true,'Account switch before dispatch leaves no ambiguous write');
 const offline=harness(fixed);offline.sandbox.se176AccountConnected=false;
 assert.equal((await offline.save()).error,'ACCOUNT_NOT_CONNECTED');assert.equal(offline.calls.length,0);
 console.log('SE532_ACCOUNT_RECEIPT_PASS: actual native/wrapper chain, durable receipt, same ID/revisions, startup linkage, account ownership/CAS, persisted uncertainty, exact-byte recovery, no write replay, asset isolation');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
