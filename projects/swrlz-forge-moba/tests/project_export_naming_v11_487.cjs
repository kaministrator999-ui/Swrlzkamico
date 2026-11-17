/* §E v11.487 — model/account project filename and selected-export checks. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const helper=fs.readFileSync(path.join(root,'runtime/project_export_naming_v11_487.js'),'utf8');
const patch=fs.readFileSync(path.join(root,'patches/v11_487_project_export_naming.py'),'utf8');
const legacy=fs.readFileSync(path.join(root,'runtime/model_atelier.js'),'utf8');
assert.match(legacy,/prism-jester\.model\.json/,'legacy template issue remains identified in immutable baseline');
assert.match(patch,/se487ModelExportBase\(\)\+'\.model\.json'/,'patch must correct native JSON export');
assert.match(patch,/se487ModelExportBase\(\)\+'\.mesh\.obj'/,'patch must correct OBJ export');
assert.match(patch,/se487DownloadProject/,'My Projects must export selected document');
assert.match(patch,/se487DownloadModelUpdate/,'model cards must export a revision-bound update');
assert.match(patch,/se487NameAssetForAccount/,'unnamed standalone assets must ask before account save');
let captured;
const ctx={
 window:{prompt:()=> 'The Sorting Hat',SWYRL_ENGINE_WORKSPACES:{modelerActive:()=>false}},
 saveCloud:async()=>true,
 se371SafeName:x=>String(x||'').trim(),
 se371VersionedLink:x=>x||null,
 se371ProjectName:()=> 'Test Project',
 se371NewName:x=>x+' Copy',
 se371HasSavedIdentity:()=>true,
 currentProject:{projectName:'Test Project',name:'Test Project'},
 se486Rev:{download:(name,body)=>{captured={name,body}}},
 cloudRefs:new Map(),
 se371CloudLinks:new Map(),
 getProjectId:()=> 'local-project',
 bounded:(x,max)=>typeof x==='string'&&x.length>0&&x.length<=max,
 se175Read:async id=>({id,name:'Hat On Device',data:{project:{instanceId:id,modelAtelier:{schema:'swyrl-model-atelier-v1',parts:[{id:'hat'}]}},editor:{},scene:{actors:[]}}}),
 rpc:async (op,payload)=>{assert.equal(op,'cloud.load');assert.equal(payload.projectId,'cloud-asset');
  return {project:{id:'cloud-asset',revision:4},bytes:new TextEncoder().encode(JSON.stringify({project:{kind:'model-atelier',modelAtelier:{schema:'swyrl-model-atelier-v1',parts:[{id:'hat'}]}},assetRecord:{schema:'swrlz-asset-record-v1',id:'asset-internal',type:'modeler'},scene:{actors:[]},editor:{}})).buffer}},
 ready:true,MAX_RAW:96*1024*1024,
 TextDecoder,TextEncoder,Date,JSON,structuredClone,Map,console,
 Blob,URL,document:{createElement:()=>({}),body:{append:()=>{}}},setTimeout:()=>{}
};
vm.runInNewContext(helper,ctx,{filename:'project_export_naming_v11_487.js'});
assert.equal(ctx.se487SafeExportName('§E Asset · [Model] The Sorting Hat'),'The-Sorting-Hat');
assert.equal(ctx.se487AskProjectName(''),'The Sorting Hat');
(async()=>{
 const local=await ctx.se487FetchCardProject({id:'local-project'},'local');
 assert.equal(local.payload.project.instanceId,'local-project');
 const cloud=await ctx.se487FetchCardProject({id:'cloud-asset',revision:4},'cloud');
 assert.equal(cloud.payload.assetRecord.id,'asset-internal');
 ctx.se487DownloadModelUpdate('§E Asset · [Model] The Sorting Hat',cloud.payload,'cloud',{id:'cloud-asset',revision:4});
 assert.equal(captured.name,'The-Sorting-Hat');
 assert.equal(captured.body.schema,'se-asset-update-v1');
 assert.equal(captured.body.target.id,'asset-internal');
 assert.equal(captured.body.target.accountId,'cloud-asset');
 assert.equal(captured.body.target.baseRevision,4);
 const doc={project:{instanceId:'native-id',modelAtelier:{schema:'swyrl-model-atelier-v1',parts:[{id:'hat'}]}}};
 ctx.se487DownloadModelUpdate('Sorting Hat',doc,'cloud',{id:'native-cloud-id',revision:6});
 assert.equal(captured.body.schema,'se-model-project-update-v1');
 assert.equal(captured.body.target.projectId,'native-id');
 assert.equal(captured.body.target.accountId,'native-cloud-id');
 assert.equal(captured.body.target.baseRevision,6);
 console.log('SE487_PROJECT_EXPORT_NAMING_PASS: project identity, account revision, sanitized names, update packages');
})().catch(e=>{console.error(e);process.exitCode=1});
