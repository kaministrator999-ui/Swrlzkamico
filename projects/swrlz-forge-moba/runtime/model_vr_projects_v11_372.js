/* SE372_VR_PROJECTS_IN_CHAT_CLOSURE_START */
// A native §E facade for the existing authenticated project library.
// No credential leaves this closure. The immersive renderer owns no cloud RPC.
async function se372StoreVRProjectAsNew(){
 const source=se371SourceId(),name=se371NewName(se371ProjectName());
 const previous=se175Snapshot(),newId=id(),data=structuredClone(previous.data);
 data.project={...data.project,instanceId:newId,name,projectName:name,
  sourceStarterId:source,se371TemplateSource:false};
 delete data.project.cloudRef;
 if(data.project.levelPack?.schema==='se-levels-v1'){
  data.project.levelProjectRoot='project-'+newId;
  for(const level of data.project.levelPack.levels||[]){
   if(level?.data?.project)Object.assign(level.data.project,{
    instanceId:newId,projectName:name,name,levelProjectRoot:'project-'+newId});
  }
 }
 await se175Store([{id:newId,name,starterId:source,
  updatedAt:new Date().toISOString(),data}]);
 // Preserve the currently borrowed native geometry and XR session. Only
 // switch the active document's project identity after storage succeeds.
 se175StampProject(newId,name,source);
 currentProject.se371TemplateSource=false;workspaceLocalAllowed=true;
 cloudRefs.delete(newId);se371CloudLinks.delete(newId);
 await se371SaveLocal();
 return {id:newId,name};
}
async function se372VRSaveLocal(){
 if(!se371HasSavedIdentity())await se372StoreVRProjectAsNew();
 else await se371SaveLocal();
 return {ok:true,name:se371ProjectName(),scope:'device'};
}
async function se372VRSaveAccount(){
 if(!ready||!se176AccountConnected){
  if(!ready&&frame&&!frame.src)frame.src=CHAT_ORIGIN+'/?forgeEmbed=1';
  return {ok:false,error:'ACCOUNT_NOT_CONNECTED'};
 }
 await se372VRSaveLocal();
 const synced=await saveCloud()===true;
 return {ok:synced,name:se371ProjectName(),scope:synced?'account':'device',
  error:synced?null:'ACCOUNT_SYNC_NOT_CONFIRMED'};
}
async function se372VRCloneDetached(){
 const original=se175Snapshot(),clone=structuredClone(original.data),
  newId=id(),name=se371NewName(se371ProjectName()),source=se371SourceId();
 clone.project={...clone.project,instanceId:newId,name,projectName:name,
  sourceStarterId:source,se371TemplateSource:false};
 delete clone.project.cloudRef;
 if(clone.project.levelPack?.schema==='se-levels-v1'){
  clone.project.levelProjectRoot='project-'+newId;
  for(const level of clone.project.levelPack.levels||[])
   if(level?.data?.project)Object.assign(level.data.project,{
    instanceId:newId,projectName:name,name,levelProjectRoot:'project-'+newId});
 }
 await se175Store([{id:newId,name,starterId:source,
  updatedAt:new Date().toISOString(),data:clone}]);
 // This is a detached copy, not an active-project replacement.
 return {ok:true,name,scope:'device',id:newId};
}
window.SWYRL_ENGINE_VR_PROJECTS_372=Object.freeze({
 connect:()=>{if(!frame.src)frame.src=CHAT_ORIGIN+'/?forgeEmbed=1';
  return {ready,connected:!!(ready&&se176AccountConnected)};},
 status:()=>({ready,connected:!!(ready&&se176AccountConnected),name:se371ProjectName()}),
 saveLocal:se372VRSaveLocal,saveAccount:se372VRSaveAccount,clone:se372VRCloneDetached
});
/* SE372_VR_PROJECTS_IN_CHAT_CLOSURE_END */
