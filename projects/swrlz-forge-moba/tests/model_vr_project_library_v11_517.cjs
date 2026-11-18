#!/usr/bin/env node
'use strict';
// Existing account bridge, no OAuth mock replacement. Assertions target
// real §E native names/transaction contract: backup-before-switch, rollback,
// project identity, starter clone and cloud access control.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const source=fs.readFileSync(path.resolve(__dirname,'../runtime/model_vr_project_library_v11_517.js'),'utf8');
const doc=(name,kind='model-atelier')=>({project:{
 name,projectName:name,kind,instanceId:name,template:kind,
 modelAtelier:kind==='model-atelier'?{parts:[]}:undefined},
 scene:{actors:[]},editor:{}});
const records=new Map([
 ['local-model',{id:'local-model',name:'Local Model',starterId:'model-atelier',data:doc('Local Model')}],
 ['local-game',{id:'local-game',name:'Game scene',starterId:'sheep-tag-meadow',data:doc('Game scene','sheep-tag')}]
]);
let current=structuredClone(records.get('local-model').data),saved=true,modified=false,
 opened=0,failSave=false,failLoader=false,recovered=0,cloudAuth=true,firstRecoveryAt=0,loadAt=0;
const snapshots=[],loads=[],history=[];
const vmctx=vm.createContext({window:{},structuredClone,Date,Math,
 se175Transition:false,se175LocalLoading:false,cloudBusy:false,playing:false,simulating:false,
 ready:true,se176AccountConnected:true,se176CloudRows:[{id:'cloud-model',name:'Cloud Model',revision:3}],
 se176RefreshProjects:async()=>{},
 se175Starters:()=>[{id:'model-atelier',name:'Model Atelier',workspace:'model-atelier'},
  {id:'sheep-tag',name:'Sheep Tag',workspace:'scene'}],
 se175Read:async id=>id?structuredClone(records.get(id)):Array.from(records.values()).map(({data,...metadata})=>metadata),
 se175Store:async rows=>{if(failSave)throw Error('Disk full');
  for(const row of rows){records.set(row.id,structuredClone(row));snapshots.push(row.id);}
  firstRecoveryAt=Date.now();},
 se175Snapshot:()=>({id:current.project.instanceId,name:current.project.projectName,
  starterId:current.project.template,data:structuredClone(current)}),
 se371ProjectName:()=>current.project.projectName,
 se371SourceId:()=>current.project.template,
 se175Saving:null, dirty:false,history,historyIndex:0,revision:2,
 id:()=>('se517-'+(++vmctx.__n)), __n:0,
 se175StampProject:(id,n,starter)=>{Object.assign(current.project,{instanceId:id,name:n,projectName:n,sourceStarterId:starter});},
 loadProject:d=>{loadAt=Date.now();if(failLoader)throw Error('Native model invalid');current=structuredClone(d);loads.push(d.project.projectName);},
 initializeHistory:()=>{},markDirty:()=>{modified=true;vmctx.dirty=true;},markSaved:()=>{saved=true;vmctx.dirty=false;},
 se175UpdateLabel:()=>{},se175RefreshLocal:async()=>{},workspaceLocalAllowed:false,
 ModelAtelier:{syncProject:()=>{},open:()=>{opened++;}},
 createProjectFromTemplate:async id=>{current=doc('Source starter');return id==='model-atelier';},
 se175StarterKinds:{'model-atelier':['Model Atelier','model-atelier','model-atelier']},
 summaryName:x=>String(x||''),se175Restore:(row,state)=>{recovered++;current=structuredClone(row.data);vmctx.dirty=state.dirty;},
 loadCloud:async id=>{if(!cloudAuth)throw Error('Cloud disconnected');current=doc('Cloud Model');return id==='cloud-model';},
});
Object.defineProperty(vmctx,'currentProject',{get:()=>current.project});
const run=async()=>{
 vm.runInContext(source,vmctx);
 const api=vmctx.window.SWYRL_ENGINE_VR_PROJECT_LIBRARY_517;
 assert(api?.list&&api?.open);
 const result=await api.list();
 assert.equal(result.local.length,2);assert.equal(result.cloud.length,1);assert.equal(result.starters.length,1);
 const initialName=current.project.projectName;
 await assert.rejects(api.open('local','local-game'),/Only Model Atelier/);
 assert.equal(current.project.projectName,initialName);
 const local=await api.open('local','local-model');
 assert(local.ok);assert(firstRecoveryAt<=loadAt,'recovery must be committed BEFORE native document load');
 assert.equal(opened,1);
 assert.equal(current.project.instanceId,'local-model');
 assert(snapshots.some(x=>x.startsWith('se517-')));
 const starter=await api.open('starter','model-atelier');
 assert(starter.ok);assert.notEqual(current.project.instanceId,'model-atelier','starter must become new user project');
 assert(records.has(current.project.instanceId),'new starter independently saved');
 assert.equal(modified,true);
 const cloud=await api.open('cloud','cloud-model');
 assert(cloud.ok);assert.equal(current.project.projectName,'Cloud Model');
 failLoader=true;
 await assert.rejects(api.open('local','local-model'),/Native model invalid/);
 assert.equal(recovered,1,'must roll back if loader fails after backup');
 assert.equal(current.project.projectName,'Cloud Model');
 failLoader=false;failSave=true;const before=current.project.instanceId;
 await assert.rejects(api.open('starter','model-atelier'),/Disk full/);
 assert.equal(current.project.instanceId,before,'storage failure must leave active scene unchanged');
 failSave=false;
 vmctx.se176AccountConnected=false;
 await assert.rejects(api.open('cloud','cloud-model'),/not connected/);
 console.log('SE517_PROJECT_LIBRARY_PASS',JSON.stringify({
  local:result.local.length,cloud:result.cloud.length,starters:result.starters.length,
  committedRecoveryBeforeOpen:true,starterCloned:true,rollback:true,diskFailurePreservesCurrent:true}));
};
run().catch(err=>{console.error(err);process.exitCode=1;});
