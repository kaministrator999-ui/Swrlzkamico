/* §E v11.486 — original-project export/update and explicit revision actions.
   Injected inside the existing authenticated Chat-host closure, not a new app. */
const se486Rev=window.SWYRL_ENGINE_REVISIONS_486;
async function se486NativeProjectHistory(){
 if(!se371HasSavedIdentity())throw Error('Open a saved user project first');
 if(playing||simulating||se175Transition||se175LocalLoading||cloudBusy)throw Error('Finish the active project operation first');
 const localId=getProjectId(),link=se371VersionedLink(cloudRefs.get(localId)||se371CloudLinks.get(localId));
 let snapshots=[],account=false;
 if(link&&ready&&se176AccountConnected){
  const response=await rpc('cloud.load',{projectId:link.id});
  if(response.project?.id!==link.id||response.project?.revision!==link.revision)
   throw Error('Account revision changed. Reopen the newest account project before restoring.');
  const document=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(response.bytes));
  snapshots=[...se486Rev.history(document),{number:link.revision,savedAt:'Current account version',current:true}];
  account=true;
 }else{
  const history=await se486Rev.readLocal(localId);
  snapshots=[...(history?.entries||[]),...(history?.latest?[{...history.latest,current:true}]:[])];
 }
 if(!snapshots.length)throw Error('No explicit saves are recorded for this project yet');
 se486Rev.present((account?'Account':'On-device')+' history · '+se371ProjectName(),snapshots,async item=>{
  const old=await se486Rev.unpack(item);
  if(!old?.project||!old.editor||!Array.isArray(old.scene?.actors))throw Error('Invalid saved scene');
  if(old.project.instanceId&&old.project.instanceId!==localId)throw Error('Revision belongs to another project');
  if(getProjectId()!==localId)throw Error('Active project changed');
  const recovery=se175Snapshot(),savedState={dirty,history:structuredClone(history),historyIndex,revision};
  try{
   window.SWYRL_ENGINE_AGENT.loadScene(old);
   se175StampProject(localId,recovery.name,recovery.starterId);
   if(typeof ModelAtelier!=='undefined'){ModelAtelier.syncProject();if(currentProject.kind==='model-atelier')ModelAtelier.open();}
   if(link)cloudRefs.set(localId,link);
   markDirty();
   const synced=await se371Save();
   if(account&&!synced)throw Error('Recovered on this device, but account synchronization was not confirmed');
   se371Display('Restored revision '+item.number+' as a new save in the same project.');
  }catch(error){
   if(!/synchronization was not confirmed/.test(String(error?.message||''))){
    try{se175Restore(recovery,savedState);if(link)cloudRefs.set(localId,link)}catch{}
   }
   throw error;
  }
 });
}
function se486ExportProjectUpdate(){
 if(!se371HasSavedIdentity())throw Error('Open your saved project first');
 if(!Array.isArray(currentProject?.modelAtelier?.parts))throw Error('This project has no editable model');
 const localId=getProjectId(),link=se371VersionedLink(cloudRefs.get(localId)||se371CloudLinks.get(localId));
 const output={schema:'se-model-project-update-v1',exportedAt:new Date().toISOString(),
  target:{projectId:localId,accountId:link?.id||null,baseRevision:link?.revision||null},
  model:structuredClone(currentProject.modelAtelier)};
 se486Rev.download(se371ProjectName(),output);
 se371Display('Exported update package for '+se371ProjectName()+'.');
}
async function se486ImportProjectUpdate(){
 if(!se371HasSavedIdentity()||playing||simulating||se371ActionBusy||cloudBusy)throw Error('Open an idle saved user project first');
 if(!Array.isArray(currentProject?.modelAtelier?.parts))throw Error('This project has no editable model to update');
 const file=await se486Rev.choose();if(!file)return;
 if(file.size>32*1024*1024)throw Error('Model update exceeds the 32 MiB import limit');
 const doc=JSON.parse(await file.text());
 if(doc?.schema!=='se-model-project-update-v1'||!Array.isArray(doc.model?.parts))throw Error('Not a compatible model update package');
 const localId=getProjectId(),link=se371VersionedLink(cloudRefs.get(localId)||se371CloudLinks.get(localId));
 if(doc.target?.projectId!==localId||doc.target?.accountId!==(link?.id||null)||doc.target?.baseRevision!==(link?.revision||null))
  throw Error('Export is for another project or an older account revision. Re-export from the current project.');
 if(doc.model.parts.length>5000||!doc.model.parts.length)throw Error('Invalid model mesh count');
 if(!confirm('Update '+se371ProjectName()+' in place with this file? Your previous save remains available through Revision History.'))return;
 const oldModel=structuredClone(currentProject.modelAtelier);
 try{
  if(getProjectId()!==localId)throw Error('Project changed while importing');
  currentProject.modelAtelier=structuredClone(doc.model);
  ModelAtelier.syncProject();
  markDirty();
  const synced=await se371Save();
  if(link&&!synced)se371Display('Model updated on device, but account sync needs attention.',true);
  else se371Display('Model updated in the same project. Revision saved.');
 }catch(error){
  currentProject.modelAtelier=oldModel;ModelAtelier.syncProject();
  throw error;
 }
}
function se486NativeAction(label,method){
 Promise.resolve().then(method).catch(error=>se371Display(label+': '+String(error?.message||error).slice(0,170),true));
}
const se486PriorButtons=se371Buttons;
se371Buttons=function(host,scope){
 se486PriorButtons(host,scope);
 if(!host||!['game','my-projects'].includes(scope)||host.querySelector('[data-se486-actions]'))return;
 const wrap=document.createElement('div');wrap.dataset.se486Actions=scope;wrap.className='se371-project-actions';
 const actions=[['Revision History','history',()=>se486NativeProjectHistory()],
  ['Export Model Update','export',()=>se486ExportProjectUpdate()],
  ['Update This Project','update',()=>se486ImportProjectUpdate()]];
 for(const [title,action,fn] of actions){
  const button=document.createElement('button');button.type='button';button.textContent=title;
  button.dataset.se486Action=action;button.className='se371-project-button';
  button.onclick=()=>se486NativeAction(title,fn);wrap.append(button);
 }
 host.append(wrap);
};
window.SWYRL_ENGINE_PROJECT_REVISIONS_486=Object.freeze({
 history:()=>se486NativeProjectHistory(),exportUpdate:()=>se486ExportProjectUpdate(),
 update:()=>se486ImportProjectUpdate()
});
