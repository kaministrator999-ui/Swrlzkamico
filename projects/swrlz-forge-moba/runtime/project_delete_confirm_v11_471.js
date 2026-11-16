/* SE471_PROJECT_DELETE_CONFIRM_START */
// Native My Projects cards are account / IndexedDB metadata views.  Deletion
// requires a separate explicit confirmation and a successful storage receipt.
// Never delete game projects, asset bytes or defaults merely by hiding a card.
(function(){
 const cardBase=se184ProjectCard;
 let busy=false;
 const boundedId=id=>typeof id==='string'&&id.length>0&&id.length<=160&&!/[\u0000-\u001f\u007f]/.test(id);
 function selectionIsActive(source,id){
  if(source==='local')return getProjectId()===id;
  if(source==='cloud'){
   const ref=cloudRefs.get(getProjectId());
   return ref?.id===id;
  }
  return false;
 }
 async function deleteLocal(record){
  const id=String(record.id);
  if(!boundedId(id)||selectionIsActive('local',id))
   throw Error('Open another project before deleting the project currently being edited.');
  if(se175Saving)await se175Saving;
  if(se175Transition||se175LocalLoading)throw Error('Finish the current project operation before deleting.');
  const db=await se175Db();
  let reason=null;
  try{
   await new Promise((resolve,reject)=>{
    const tx=db.transaction(['projects','metadata'],'readwrite');
    const data=tx.objectStore('projects'),meta=tx.objectStore('metadata');
    const read=meta.get(id);
    read.onsuccess=()=>{
     const saved=read.result;
     if(!saved||saved.name!==record.name||
        (record.updatedAt&&saved.updatedAt!==record.updatedAt)){
      reason='Saved project changed or was already deleted. Refresh My Projects.';
      tx.abort();return;
     }
     // One atomic transaction removes both the scene body and its card metadata.
     data.delete(id);meta.delete(id);
    };
    tx.oncomplete=resolve;
    tx.onerror=tx.onabort=()=>reject(Error(reason||'Local storage could not confirm deletion.'));
   });
  }finally{db.close();}
  if(selectionIsActive('local',id))throw Error('Active project changed during deletion. Refresh the library.');
  return {ok:true,projectId:id};
 }
 async function deleteCloud(record){
  const id=String(record.id);
  if(!boundedId(id)||!se176AccountConnected||!ready)
   throw Error('Sign in to § Chat before deleting account projects.');
  if(selectionIsActive('cloud',id))
   throw Error('Open another project before deleting the account version currently in use.');
  if(!Number.isInteger(record.revision)||record.revision<1)
   throw Error('Current account revision unavailable. Refresh My Projects.');
  if(cloudBusy)throw Error('Another account operation is in progress.');
  const fresh=await rpc('cloud.list');
  const entry=Array.isArray(fresh.projects)?fresh.projects.find(p=>p.id===id):null;
  if(!entry||entry.revision!==record.revision||entry.name!==record.name)
   throw Error('Account project changed. Refresh My Projects before deleting.');
  // Authenticated iframe is the sole bearer of owner credentials. The host
  // never calls the Chat deletion endpoint directly, nor sends credentials.
  const receipt=await rpc('cloud.delete',{projectId:id,expectedRevision:record.revision});
  if(receipt?.ok!==true||receipt.projectId!==id||receipt.deletedRevision!==record.revision)
   throw Error('Account did not confirm the deletion; no success was assumed.');
  return receipt;
 }
 function removeDefault(source,id){
  const current=window.SWYRL_ENGINE_SAVED_DEFAULT?.read?.();
  if(current?.source===source&&current.id===id)
   window.SWYRL_ENGINE_SAVED_DEFAULT?.set?.(null);
 }
 async function removeRecord(record,source){
  if(busy)throw Error('A project deletion is already in progress.');
  busy=true;
  try{
   const receipt=source==='local'?await deleteLocal(record):await deleteCloud(record);
   if(receipt?.ok!==true)throw Error('Project deletion not confirmed.');
   removeDefault(source,record.id);
   if(source==='cloud'){
    se184CloudPreviews.delete(record.id);
    for(const [localId,link] of cloudRefs)
     if(link?.id===record.id)cloudRefs.delete(localId);
    window.dispatchEvent(new CustomEvent('swrlz:account-project-deleted',
     {detail:{id:record.id}}));
    if(typeof se170Refresh==='function')await se170Refresh();
   }else{
    se184LocalPreviews.delete(record.id);
    await se175RefreshLocal();
   }
   await se176RefreshProjects();
   return true;
  }finally{busy=false;}
 }
 function askDelete(record,source,button,feedback){
  if(busy)return;
  const dialog=document.createElement('dialog');
  dialog.className='se471-delete-dialog';
  dialog.setAttribute('aria-label','Confirm project deletion');
  const title=document.createElement('strong');
  title.textContent='Delete saved project?';
  const detail=document.createElement('p');
  detail.textContent='“'+summaryName(record.name)+'”'+
   (source==='cloud'?' will be deleted from your signed-in account.':
    ' will be removed from this device’s saved-project library.')+
   ' This does not delete the other storage location. This action cannot be undone.';
  const status=document.createElement('p');
  status.setAttribute('role','status');status.setAttribute('aria-live','polite');
  const buttons=document.createElement('div');buttons.className='se471-delete-actions';
  const cancel=document.createElement('button');cancel.type='button';cancel.textContent='Cancel';
  const approve=document.createElement('button');approve.type='button';
  approve.className='se471-confirm-danger';approve.textContent='Delete project';
  buttons.append(cancel,approve);dialog.append(title,detail,status,buttons);
  document.body.append(dialog);
  const close=()=>{if(dialog.open)dialog.close();else dialog.remove();};
  cancel.onclick=close;
  dialog.addEventListener('close',()=>dialog.remove(),{once:true});
  approve.onclick=async()=>{
   approve.disabled=true;cancel.disabled=true;
   status.textContent='Deleting selected project…';
   try{
    const removed=await removeRecord(record,source);
    if(removed){
     feedback.textContent='Project deleted.';
     close();
     if(typeof toast==='function')toast('Deleted saved project · '+summaryName(record.name));
    }
   }catch(error){
    status.textContent=String(error?.message||error).slice(0,220);
    approve.disabled=false;cancel.disabled=false;
   }
  };
  try{dialog.showModal();cancel.focus();}
  catch(error){dialog.remove();feedback.textContent='Confirmation dialog unavailable: '+error.message;}
 }
 se184ProjectCard=function(record,source){
  const card=cardBase(record,source);
  if(!['cloud','local'].includes(source)||!boundedId(record?.id))return card;
  const actions=card.querySelector('.se184-card-actions');
  if(!actions)return card;
  const button=document.createElement('button');button.type='button';
  button.className='se471-delete-project';
  button.textContent='Delete';
  button.setAttribute('aria-label','Delete saved project '+summaryName(record.name));
  const result=card.querySelector('.se184-preview-status');
  button.addEventListener('click',()=>askDelete(record,source,button,result));
  actions.append(button);
  return card;
 };
 window.SWYRL_ENGINE_PROJECT_DELETE_471=Object.freeze({
  version:'v11.471',
  available:()=>({local:true,cloud:se176AccountConnected&&ready}),
  active:()=>busy
 });
})();
/* SE471_PROJECT_DELETE_CONFIRM_END */
