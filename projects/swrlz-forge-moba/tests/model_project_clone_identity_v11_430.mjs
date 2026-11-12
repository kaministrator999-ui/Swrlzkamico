// Exercise the ACTUAL assembled native clone/save functions. Persistence,
// editor loading and stamping are controlled adapters; no account or user
// project is touched. In particular, load hydrates nested level metadata.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
assert.ok(process.argv[2],'Usage: node model_project_clone_identity_v11_430.mjs <assembled.html>');
const source=fs.readFileSync(path.resolve(process.argv[2]),'utf8');
function section(start,end){const a=source.indexOf(start),b=source.indexOf(end,a+start.length);assert.ok(a>=0&&b>a,start);return source.slice(a,b);}
const nativeCode=[
 section('function se371SourceId(){','function se371HasSavedIdentity(){'),
 section('function se371HasSavedIdentity(){','function se371Display('),
 section('function se371SafeName(value){','async function se371SaveLocal(){'),
 section('async function se371SaveLocal(){','async function se371Clone('),
 section('async function se371Clone(name){','async function se371Save(){')
].join('\n');
const clone=value=>structuredClone(value);
const normalized=value=>JSON.parse(JSON.stringify(value));
function practice(){
 const model={schema:'swyrl-model-atelier-v1',name:'Starter cube',parts:[{
  id:'source-cube',name:'Cube',kind:'box',position:[0,1,0],rotation:[0,0,0],
  scale:[.6,.6,.6],color:'#b6a2dd',material:'matte',group:'Source'}]};
 const level=(id,label)=>({id,name:label,data:{project:{kind:'model-atelier',instanceId:'starter-original',
  canonicalId:'blank-model',name:label,projectName:label,template:'blank-model',se371TemplateSource:true,
  modelAtelier:clone(model)},editor:{studioWorkspace:'modeler'},scene:{actors:[]}}});
 return {project:{kind:'model-atelier',instanceId:'starter-original',canonicalId:'starter-original',
  name:'Original starter',projectName:'Original starter',template:'blank-model',se371TemplateSource:true,
  sourceStarterId:'blank-model',cloudRef:{id:'source-account-row',revision:8},modelAtelier:model,
  levelPack:{schema:'se-levels-v1',activeId:'first',levels:[level('first','First level'),level('second','Second level')]}},
  editor:{studioWorkspace:'modeler'},scene:{actors:[]}};
}
function fixture(options={}){
 const original=practice(),originalBytes=JSON.stringify(original),events=[],rows=new Map();let serial=0,stores=0;
 const live=clone(original),initialHistory=[{label:'Source history'}];
 let records=clone(live.project.levelPack.levels),documentData=live;
 const context={console,structuredClone,Date,Set,Map,Error,
  currentProject:live.project,dirty:true,history:clone(initialHistory),historyIndex:0,revision:19,
  se175Transition:false,se175LocalLoading:false,cloudBusy:false,playing:false,simulating:false,
  se175Saving:null,workspaceLocalAllowed:false,
  se371CloudLinks:new Map([['starter-original',{id:'source-account-row',revision:8}]]),
  cloudRefs:new Map([['starter-original',{id:'source-account-row',revision:8}]]),
  bounded:(value,max)=>typeof value==='string'&&value.length>0&&value.length<=max,
  summaryName:value=>String(value??''),id:()=>`independent-${++serial}`,
  document:{getElementById:()=>({classList:{remove:name=>events.push(['hide',name])}})},
  ModelAtelier:{syncProject:()=>events.push(['model-sync']),open:()=>events.push(['model-open'])},
  initializeHistory:label=>{events.push(['history',label]);context.history=[{label}];context.historyIndex=0;},
  markSaved:()=>{events.push(['saved']);context.dirty=false;},
  se175UpdateLabel:()=>events.push(['label'])
 };
 context.se175Snapshot=()=>{
  const data={...clone(documentData),project:{...clone(context.currentProject)}};
  data.project.levelPack={schema:'se-levels-v1',activeId:'first',levels:clone(records)};
  return {id:context.currentProject.instanceId,name:context.currentProject.name,
   starterId:context.currentProject.sourceStarterId||'blank-model',data};
 };
 context.se175Store=async batch=>{
  stores++;events.push(['store',batch[0].id]);
  if(options.failFirstStore&&stores===1)throw Error('Store unavailable');
  // The first independent row must exist before live editor replacement.
  if(stores===1)assert.equal(context.currentProject.instanceId,'starter-original');
  for(const row of batch)rows.set(row.id,clone(row));
 };
 function hydrate(index){
  const root=clone(documentData.project),active=clone(records[index].data.project);
  // Native level loading overlays the active level's own project metadata.
  // A false flag only on the outer envelope cannot protect the live identity.
  context.currentProject={...root,...active};
 }
 context.loadProject=(data,config)=>{
  assert.ok(rows.has(data.project.instanceId),'Independent row must be stored before loading');
  assert.equal(config.workspaceLocal,true);events.push(['load',data.project.instanceId]);
  documentData=clone(data);records=clone(data.project.levelPack.levels);hydrate(0);
 };
 context.se175StampProject=(id,name,sourceStarterId)=>{
  events.push(['stamp',id]);
  const stamp=project=>Object.assign(project,{instanceId:id,projectName:name,sourceStarterId});
  stamp(context.currentProject);context.currentProject.name=name;context.currentProject.levelProjectRoot='project-'+id;
  for(const record of records){stamp(record.data.project);record.data.project.levelProjectRoot='project-'+id;}
  delete context.currentProject.levelPack;
  if(options.stampRefreshesTemplate)context.currentProject.se371TemplateSource=true;
 };
 context.se175Restore=(recovery,savedState)=>{
  events.push(['restore']);documentData=clone(recovery.data);records=clone(documentData.project.levelPack.levels);
  context.currentProject=clone(documentData.project);Object.assign(context,clone(savedState));
 };
 vm.createContext(context);vm.runInContext(nativeCode,context,{filename:'actual-native-clone-save430'});
 return {context,events,rows,original,originalBytes,hydrate,
  clone:name=>context.se371Clone(name),save:()=>context.se371SaveLocal(),
  current:()=>normalized(context.currentProject),records:()=>normalized(records)};
}
let groups=0;
{
 const f=fixture();const id=await f.clone('Independent manual model');assert.equal(id,'independent-1');
 const firstStore=f.events.findIndex(e=>e[0]==='store'),load=f.events.findIndex(e=>e[0]==='load');
 assert.ok(firstStore>=0&&load>firstStore);assert.ok(f.rows.has(id));assert.ok(!f.rows.has('starter-original'));
 assert.equal(f.context.currentProject.instanceId,id);assert.equal(f.context.currentProject.sourceStarterId,'blank-model');
 assert.equal(f.context.currentProject.se371TemplateSource,false);assert.equal(f.context.se371HasSavedIdentity(),true);
 assert.ok(!Object.hasOwn(f.rows.get(id).data.project,'cloudRef'));
 assert.equal(JSON.stringify(f.original),f.originalBytes,'Cloning must not mutate the source envelope');groups++;
}
{
 const f=fixture();const id=await f.clone('Nested identity');
 for(const level of f.records()){
  assert.equal(level.data.project.instanceId,id);assert.equal(level.data.project.se371TemplateSource,false);
  assert.equal(level.data.project.sourceStarterId,'blank-model');assert.equal(level.data.project.levelProjectRoot,'project-'+id);
 }
 const saved=f.rows.get(id);assert.equal(saved.data.project.se371TemplateSource,false);
 assert.ok(saved.data.project.levelPack.levels.every(level=>level.data.project.se371TemplateSource===false));
 groups++;
}
{
 const f=fixture({stampRefreshesTemplate:true});const id=await f.clone('Active level guard');
 assert.equal(f.context.currentProject.se371TemplateSource,false,'Live template marker must be cleared after native stamping');
 assert.equal(f.context.se371HasSavedIdentity(),true);assert.equal((await f.save()).id,id);groups++;
}
{
 const f=fixture();const id=await f.clone('Rehydration');const expectedParts=normalized(f.context.currentProject.modelAtelier.parts);
 for(let i=0;i<2;i++){
  f.hydrate(i);assert.equal(f.context.currentProject.instanceId,id);assert.equal(f.context.currentProject.se371TemplateSource,false);
  assert.equal(f.context.se371HasSavedIdentity(),true);const saved=await f.save();assert.equal(saved.id,id);
  assert.deepEqual(normalized(saved.data.project.modelAtelier.parts),expectedParts);
 }
 assert.deepEqual([...f.rows.keys()],[id],'Rehydrating another cloned level must not create another project identity');
 assert.equal(JSON.stringify(f.original),f.originalBytes);groups++;
}
{
 const f=fixture({failFirstStore:true}),before=f.current();await assert.rejects(f.clone('Rejected clone'),/Store unavailable/);
 assert.deepEqual(f.current(),before);assert.equal(f.rows.size,0);
 assert.ok(!f.events.some(e=>['load','stamp','model-open','model-sync','restore'].includes(e[0])),'Failed first store must not replace the workspace');
 assert.equal(f.context.dirty,true);assert.equal(f.context.history[0].label,'Source history');
 assert.equal(JSON.stringify(f.original),f.originalBytes);groups++;
}
{
 const f=fixture();await assert.rejects(f.save(),/starter must be cloned/i);
 assert.equal(f.rows.size,0);assert.equal(f.events.length,0,'Direct save must retain starter protection');
 await assert.rejects(f.clone('   '),/Project name is required/);assert.equal(f.rows.size,0);
 assert.equal(JSON.stringify(f.original),f.originalBytes);groups++;
}
console.log('MODEL_PROJECT_CLONE_IDENTITY_V11_430_PASS',JSON.stringify({groups,
 source:'actual assembled se371Clone and se371SaveLocal',nestedLevelHydration:true,
 independentStoreBeforeLoad:true,starterUnchanged:true,failedStoreNoLoad:true}));
