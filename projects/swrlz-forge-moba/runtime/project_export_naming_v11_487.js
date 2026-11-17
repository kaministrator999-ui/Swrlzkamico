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
function se487DownloadProject(name,document,isAsset){
 const slug=se487SafeExportName(name);
 const blob=new Blob([JSON.stringify(document,null,2)+'\n'],{type:'application/json'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download=slug+(isAsset?'.swyrl-asset.json':'.swyrl.json');
 document.body.append(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1500);
}
