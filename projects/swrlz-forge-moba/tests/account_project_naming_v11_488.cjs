/* §E v11.488 — first save naming, stable IDs, model rename regression. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const code=name=>fs.readFileSync(path.join(root,'runtime',name),'utf8');
const patch=fs.readFileSync(path.join(root,'patches/v11_488_account_project_naming.py'),'utf8');
assert.match(patch,/Save cancelled. Project name was not supplied/);
assert.match(patch,/se488NameAssetBeforeCloudSave/);
assert.match(patch,/se488InstallNameAction/);
assert.match(patch,/se371SaveLocal/);
const stampCalls=[],cloneCalls=[],cloudCalls=[];
const w={prompt:()=> 'The Sorting Hat',SWYRL_ENGINE_WORKSPACES:{modelerActive:()=>false}};
const ctx={
 window:w,currentProject:{name:'Untitled project',projectName:'Untitled project',instanceId:'original'},
 ready:true,se176AccountConnected:true,cloudBusy:false,
 cloudRefs:new Map(),se371CloudLinks:new Map(),
 se371VersionedLink:value=>value&&value.id?value:null,
 se371HasSavedIdentity:()=>true,getProjectId:()=> 'original',
 se371ProjectName:()=> 'Untitled project',se371SafeName:n=>{n=String(n||'').trim();if(!n)throw Error('Required');return n},
 se371NewName:n=>n+' Copy',se371SourceId:()=> 'sorting-hat',
 se175StampProject:(id,name,source)=>{stampCalls.push({id,name,source});ctx.currentProject.projectName=name},
 se371Clone:async name=>{cloneCalls.push(name)},
 se371Display:()=>{},saveCloud:async()=>{cloudCalls.push('saved');return true},
 Promise,Map,Date,JSON,console,
};
vm.createContext(ctx);
vm.runInContext(code('account_project_naming_v11_488.js'),ctx);
assert.equal(ctx.se488NeedsProjectName(),true);
(async()=>{
 assert.equal(await ctx.saveCloud(),true);
 assert.deepEqual(stampCalls,[{id:'original',name:'The Sorting Hat',source:'sorting-hat'}]);
 assert.equal(cloudCalls.length,1);
 assert.equal(cloneCalls.length,0,'renaming saved project must not duplicate it');
 w.prompt=()=>null;ctx.currentProject.projectName='Untitled project';
 assert.equal(await ctx.saveCloud(),false,'cancel must stop account overwrite');
 assert.equal(cloudCalls.length,1);
 w.prompt=()=> 'Named Hat';ctx.se371HasSavedIdentity=()=>false;
 assert.equal(await ctx.saveCloud(),true);
 assert.equal(cloneCalls[0],'Named Hat');
 const source={schema:'swyrl-model-atelier-v1',name:'Prism Jester',parts:[{id:'hat'}]};
 const statuses=[];
 const aw={prompt:()=> 'The Sorting Hat',SWYRL_ENGINE_WORKSPACES:{usingScratch:()=>true,draftEdited:()=>{}}};
 const a={window:aw,mode:()=> 'modeler',se470Source:()=>source,
  cloudRows:[],document:{},status:(message)=>statuses.push(message),markDirty:()=>{},String,console};
 vm.createContext(a);vm.runInContext(code('account_asset_naming_v11_488.js'),a);
 const record={name:'Prism Jester',data:{schema:'swyrl-model-atelier-v1',parts:[{id:'hat'}]}};
 assert.equal(a.se488NameAssetBeforeCloudSave('modeler',record,{id:'same-asset',remote:null}),true);
 assert.equal(record.name,'The Sorting Hat');
 assert.equal(source.name,'The Sorting Hat');
 assert.equal(record.data.name,'The Sorting Hat');
 aw.prompt=()=> 'Rebranded Hat';
 a.se488RenameActiveModel();
 assert.equal(source.name,'Rebranded Hat');
 aw.prompt=()=>null;
 assert.equal(a.se488NameAssetBeforeCloudSave('modeler',{name:'Untitled model',data:{}},{id:'asset2',remote:null}),false);
 console.log('SE488_ACCOUNT_NAMING_PASS: first project save, cancellation, same ID, model name, explicit rename');
})().catch(e=>{console.error(e);process.exitCode=1});
