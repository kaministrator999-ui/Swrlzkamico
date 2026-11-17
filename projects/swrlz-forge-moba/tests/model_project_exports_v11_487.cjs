/* §E v11.487 export identity and exact selected-card regression tests. */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=file=>fs.readFileSync(path.join(root,'runtime',file),'utf8');
const active={name:'Wrong internal Prism Jester label',schema:'swyrl-model-atelier-v1',parts:[{id:'mesh',uvPaintPNG:'UVIMAGE'}]};
const objCtx={window:{SWYRL_ENGINE_WORKSPACES:{modelerActive:()=>true,usingScratch:()=>false}},
 currentProject:{projectName:'The Sorting Hat',name:'Prism Jester'},model:()=>active};
vm.createContext(objCtx);
vm.runInContext(read('model_export_identity_v11_487.js'),objCtx);
assert.equal(objCtx.se487ExportStem(),'The-Sorting-Hat');
assert.equal(objCtx.se487ExportOBJName(),'The_Sorting_Hat');
objCtx.window.SWYRL_ENGINE_WORKSPACES.usingScratch=()=>true;
active.name='My Sculpt';
assert.equal(objCtx.se487ExportStem(),'My-Sculpt');
objCtx.currentProject.projectName='Wrong';
active.name='';active.title='';
assert.equal(objCtx.se487ExportStem(),'Untitled-Model');

const scene=(name='The Sorting Hat')=>({
 project:{kind:'model-atelier',name,projectName:name,instanceId:'user-model-one',
  modelAtelier:{schema:'swyrl-model-atelier-v1',name,parts:[{id:'hat',uvPaintPNG:'PRESERVED_UV'}]}},
 scene:{actors:[]},editor:{native:true}
});
const rows={local1:{id:'local1',name:'My Local Hat',data:scene('My Local Hat')}};
const names=[],updates=[],rpcCalls=[];
let cloudDoc=scene(),cloudRevision=5;
const ctx={
 window:{SWYRL_ENGINE_REVISIONS_486:{download:(name,data)=>updates.push({name,data})}},
 se184ProjectCard:()=>({querySelector:()=>null}),
 se175Read:async id=>rows[id],bounded:(id,len)=>typeof id==='string'&&id.length>0&&id.length<=len,
 ready:true,se176AccountConnected:true,
 rpc:async(type,params)=>{
  rpcCalls.push({type,...params});
  assert.equal(type,'cloud.load');
  assert.equal(params.projectId,'cloud-hat');
  return {project:{id:'cloud-hat',name:'The Sorting Hat',revision:cloudRevision},
    bytes:new TextEncoder().encode(JSON.stringify(cloudDoc)).buffer};
 },
 MAX_RAW:96*1024*1024,
 TextDecoder,TextEncoder,ArrayBuffer,Blob,URL:{createObjectURL:()=> 'blob:test',revokeObjectURL:()=>{}},
 document:{body:{append:()=>{}},createElement:tag=>{
  assert.equal(tag,'a');
  return {set href(value){},set download(value){this._name=value;},click(){names.push(this._name)},remove(){}};
 }},
 setTimeout:()=>0,JSON,Date,structuredClone,console
};
vm.createContext(ctx);vm.runInContext(read('my_projects_export_v11_487.js'),ctx);
const api=ctx.window.SWYRL_ENGINE_MY_PROJECTS_EXPORT_487;
assert.equal(api.filename('The Sorting Hat'),'The-Sorting-Hat');
(async()=>{
 const local=await api.exportNative({id:'local1',name:'My Local Hat'},'local');
 assert.match(local,/My Local Hat/);
 assert.equal(names.pop(),'My-Local-Hat.swyrl.json');
 assert.equal(rpcCalls.length,0,'Local card export must never read the cloud or active model');
 const cloud=await api.exportNative({id:'cloud-hat',name:'The Sorting Hat',revision:5},'cloud');
 assert.match(cloud,/The Sorting Hat/);
 assert.equal(names.pop(),'The-Sorting-Hat.swyrl.json');
 assert.equal(rpcCalls.length,1);
 await api.exportUpdate({id:'cloud-hat',name:'The Sorting Hat',revision:5},'cloud');
 assert.equal(updates[0].name,'The Sorting Hat');
 assert.equal(updates[0].data.schema,'se-model-project-update-v1');
 assert.equal(updates[0].data.target.projectId,'user-model-one');
 assert.equal(updates[0].data.target.accountId,'cloud-hat');
 assert.equal(updates[0].data.target.baseRevision,5);
 assert.equal(updates[0].data.model.parts[0].uvPaintPNG,'PRESERVED_UV');
 const bad=JSON.parse(JSON.stringify(cloudDoc));bad.project.modelAtelier=null;
 cloudDoc=bad;
 await assert.rejects(()=>api.exportUpdate({id:'cloud-hat',name:'The Sorting Hat',revision:5},'cloud'),/does not contain an editable Model Studio asset/);
 cloudDoc=scene();cloudRevision=6;
 await assert.rejects(()=>api.exportUpdate({id:'cloud-hat',name:'The Sorting Hat',revision:5},'cloud'),/saved again on another device/);
 cloudRevision=5;
 cloudDoc={...scene(),assetRecord:{schema:'swrlz-asset-record-v1',id:'asset-hat-one',type:'modeler',name:'The Sorting Hat'}};
 await api.exportUpdate({id:'cloud-hat',name:'The Sorting Hat',revision:5},'cloud');
 assert.equal(updates[1].data.schema,'se-asset-update-v1');
 assert.equal(updates[1].data.target.id,'asset-hat-one');
 assert.equal(updates[1].data.target.accountId,'cloud-hat');
 console.log('SE487_EXPORT_IDENTITY_PASS: active names, JSON/OBJ names, isolated selected-card export, native backup, compatible updates, stale revisions, UV preserved');
})().catch(e=>{console.error(e);process.exitCode=1});
