/* §E v11.487 — readable filenames, first account-save names, and
   selected-project exports. Native geometry and account identity are unchanged. */
function se487NativeProjectUnnamed(){
 const name=String(currentProject?.projectName||currentProject?.name||'').trim();
 return !name||/^(untitled(?:\s+(?:project|model|scene))?|new (?:model|project)|blank (?:model|scene|project))$/i.test(name);
}
function se487AskProjectName(defaultName){
 const entered=window.prompt('Name this project for your account',String(defaultName||'').slice(0,100));
 if(entered===null)return null;
 return se371SafeName(entered);
}
const se487PreviousCloudSave=saveCloud;
saveCloud=async function(...args){
 if(window.SWYRL_ENGINE_WORKSPACES?.modelerActive?.()){
  const api=window.SWYRL_ENGINE_ASSET_LIBRARY;
  if(!api?.save){se371Display('Model account save is not ready.',true);return false;}
  return await api.save('modeler',true);
 }
 if(ready&&se176AccountConnected&&!cloudBusy){
  if(!se371HasSavedIdentity()){
   const name=se487AskProjectName(se371NewName(se371ProjectName()));
   if(name===null){se371Display('Account save cancelled; project unchanged.');return false;}
   await se371Clone(name);
  }else if(se487NativeProjectUnnamed()){
   const name=se487AskProjectName('');
   if(name===null){se371Display('Account save cancelled; project unchanged.');return false;}
   se175StampProject(getProjectId(),name,se371SourceId());
  }
 }
 return se487PreviousCloudSave.apply(this,args);
};
function se487SafeExportName(name){
 return String(name||'Untitled project').trim().replace(/^§E Asset · \[(?:Model|Particle)\]\s*/,'')
  .replace(/[\\/:*?"<>|\x00-\x1f]+/g,'-').replace(/\s+/g,'-').replace(/-+/g,'-')
  .replace(/^[-.]+|[-.]+$/g,'').slice(0,90)||'Untitled-project';
}
function se487DownloadProject(name,payload,isAsset){
 const slug=se487SafeExportName(name);
 const blob=new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download=slug+(isAsset?'.swyrl-asset.json':'.swyrl.json');
 document.body.append(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1500);
}

function se487DownloadModelUpdate(name,payload,source,record){
 const raw=payload?.project?.modelAtelier;
 const asset=payload?.assetRecord;
 let output;
 if(asset?.schema==='swrlz-asset-record-v1'&&asset.type==='modeler'&&
    raw?.schema==='swyrl-model-atelier-v1'&&Array.isArray(raw.parts)){
  output={schema:'se-asset-update-v1',exportedAt:new Date().toISOString(),
   target:{type:'modeler',id:asset.id,
    accountId:source==='cloud'?record.id:null,
    baseRevision:source==='cloud'?record.revision:null},
   data:structuredClone(raw)};
 }else if(raw?.schema==='swyrl-model-atelier-v1'&&Array.isArray(raw.parts)){
  const projectId=payload.project.instanceId;
  if(typeof projectId!=='string'||!projectId)throw Error('Project lacks a saved update identity');
  const linked=se371VersionedLink(record?.cloudRef);
  output={schema:'se-model-project-update-v1',exportedAt:new Date().toISOString(),
   target:{projectId,
    accountId:source==='cloud'?record.id:linked?.id||null,
    baseRevision:source==='cloud'?record.revision:linked?.revision||null},
   model:structuredClone(raw)};
 }else throw Error('This saved project has no editable Model Studio asset');
 se486Rev.download(se487SafeExportName(name),output);
}

async function se487FetchCardProject(record,source){
 const id=String(record?.id||'');
 if(!bounded(id,160))throw Error('Invalid saved project identity');
 if(source==='local'){
  const row=await se175Read(id);
  if(!row||row.id!==id||!row.data?.project||!Array.isArray(row.data.scene?.actors))
   throw Error('Local project file is unavailable');
  if(row.data.project.instanceId&&row.data.project.instanceId!==id)
   throw Error('Local project identity does not match its saved file');
  return {payload:structuredClone(row.data),record:row};
 }
 if(source==='cloud'){
  if(!ready)throw Error('Connect your account to export a saved project');
  const reply=await rpc('cloud.load',{projectId:id});
  if(reply.project?.id!==id||
     (Number.isInteger(record.revision)&&reply.project.revision!==record.revision))
   throw Error('Account project changed. Refresh My Projects first.');
  if(!(reply.bytes instanceof ArrayBuffer)||reply.bytes.byteLength>MAX_RAW)
   throw Error('Saved project data unavailable or too large');
  const payload=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(reply.bytes));
  if(!payload?.project||!payload.editor||!Array.isArray(payload.scene?.actors))
   throw Error('Saved account project does not contain a valid native document');
  return {payload,record};
 }
 throw Error('Unknown project source');
}
function se487AskNativeModelName(){
 const scratch=window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.()===true;
 const title=String(currentProject?.projectName||currentProject?.name||'').trim();
 const candidate=scratch?String(window.SWYRL_ENGINE_WORKSPACES?.scratchModel?.()?.name||'').trim():title;
 const initial=/^(untitled(?:\\s+(?:model|project))?|prism jester|model atelier)$/i.test(candidate)?'':candidate;
 const entered=window.prompt('Name the model to save',initial.slice(0,100));
 if(entered===null)return null;
 const clean=entered.trim();
 if(!clean||clean.length>100)throw Error('Choose a name between 1 and 100 characters');
 return clean;
}
