/* §E v11.488 — naming guard around existing account writes.
   A name changes metadata, never the account project ID or revision. */
function se488NeedsProjectName(){
 const label=String(currentProject?.projectName||currentProject?.name||'').trim();
 if(!label||/^(?:untitled(?:\s+(?:model|project|scene))?|new (?:model|project)|blank (?:model|scene|project))$/i.test(label))
  return true;
 const id=currentProject?.instanceId;
 const linked=typeof id==='string'&&se371VersionedLink(cloudRefs.get(id)||se371CloudLinks.get(id));
 if(!linked&&(/(?:\s+Copy)$/i.test(label)||/^Prism Jester$/i.test(label)))return true;
 return false;
}
function se488AskProjectName(defaultName=''){
 const answer=window.prompt('Name this project before saving to your account',String(defaultName||'').slice(0,100));
 if(answer===null)return null;
 return se371SafeName(answer);
}
async function se488EnsureProjectNameForAccount(){
 if(!ready||!se176AccountConnected)return true;
 if(!se371HasSavedIdentity()){
  const name=se488AskProjectName(
   se488NeedsProjectName()?'':se371ProjectName());
  if(name===null){se371Display('Save cancelled. The starter project was not changed.');return false;}
  await se371Clone(name);
 }else if(se488NeedsProjectName()){
  const name=se488AskProjectName('');
  if(name===null){se371Display('Save cancelled. No project was overwritten.');return false;}
  se175StampProject(getProjectId(),name,se371SourceId());
 }
 return true;
}
const se488PreviousAccountSave=saveCloud;
saveCloud=async function(...args){
 if(window.SWYRL_ENGINE_WORKSPACES?.modelerActive?.()){
  const assets=window.SWYRL_ENGINE_ASSET_LIBRARY;
  if(!assets?.save){se371Display('Model account library is unavailable.',true);return false;}
  return await assets.save('modeler',true);
 }
 if(ready&&se176AccountConnected&&!cloudBusy){
  if(!(await se488EnsureProjectNameForAccount()))return false;
 }
 return await se488PreviousAccountSave.apply(this,args);
};
