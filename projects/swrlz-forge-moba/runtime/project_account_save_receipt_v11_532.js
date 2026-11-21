/* SE532_PROJECT_ACCOUNT_SAVE_RECEIPT_START */
// Keep native project saves on the checked v371 facade captured before the
// separate v488 model-asset dispatcher. A transport failure can follow a real
// commit, so persist a small receipt intent before dispatch and never replay it.
const se532PendingProjectSaves=new Map(),se532AcknowledgedProjectSaves=new Map();
let se532RecoveredProjectSave=null;
const se532PriorRememberLink=se371RememberLink;
se371RememberLink=async function(localId,remote){
 const ack=se532AcknowledgedProjectSaves.get(localId);
 if(ack&&remote?.id===ack.id&&remote.revision===ack.revision){
  // All existing native project save routes share this receipt boundary,
  // including Save Project and revision restore, not only the v529 button.
  se532PendingProjectSaves.delete(localId);se532AcknowledgedProjectSaves.delete(localId);
 }
 return await se532PriorRememberLink.apply(this,arguments);
};
function se532PendingReceipt(value,localId){
 return value?.schema==='se-project-save-pending-v1'&&value.localId===localId&&
  bounded(localId,160)&&(value.accountId===null||bounded(value.accountId,160))&&
  Number.isInteger(value.expectedRevision)&&value.expectedRevision>=0&&
  /^[a-f0-9]{64}$/.test(value.sha256||'')?{...value}:null;
}
const se532PriorSnapshot=se175Snapshot;
se175Snapshot=function(...args){
 const row=se532PriorSnapshot.apply(this,args),pending=se532PendingProjectSaves.get(row.id);
 if(pending)row.se532PendingAccountSave={...pending};
 return row;
};
const se532PriorRead=se175Read;
se175Read=async function(key){
 const row=await se532PriorRead.apply(this,arguments);
 if(key){
  const pending=se532PendingReceipt(row?.se532PendingAccountSave,key);
  if(pending)se532PendingProjectSaves.set(key,pending);
 }
 return row;
};
async function se532ProjectDigest(bytes){
 if(!globalThis.crypto?.subtle)throw Error('Account save receipt verification is unavailable. No account write was attempted.');
 return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))]
  .map(n=>n.toString(16).padStart(2,'0')).join('');
}
function se532UnknownSave(){
 return Error('Account save confirmation is unknown. No write was retried. Refresh My Projects and open the saved account project to verify it; your local copy is safe.');
}
async function se532PrepareProjectAccountSave(){
 const localId=getProjectId();
 // Read BEFORE the local save: startup can bypass the local picker, leaving
 // both maps empty while the persisted row still has its account revision.
 await se175Read(localId);
 if(getProjectId()!==localId||!ready||!se176AccountConnected)
  throw Error('Project or account changed before account save. No account write was attempted.');
}
async function se532ClearPreparedReceipt(localId,pending){
 // Remove only our metadata in the existing database transaction. Re-saving
 // the pre-dispatch snapshot here could overwrite a newer local autosave.
 const database=await se175Db();
 try{
  await new Promise((resolve,reject)=>{
   const tx=database.transaction(['projects','metadata'],'readwrite');
   tx.oncomplete=resolve;tx.onerror=tx.onabort=()=>reject(Error('Local receipt cleanup failed'));
   const projects=tx.objectStore('projects'),request=projects.get(localId);
   request.onsuccess=()=>{
    const row=request.result,stored=se532PendingReceipt(row?.se532PendingAccountSave,localId);
    if(stored&&stored.sha256===pending.sha256&&stored.accountId===pending.accountId&&
       stored.expectedRevision===pending.expectedRevision){
     delete row.se532PendingAccountSave;projects.put(row);
     const {data,...metadata}=row;tx.objectStore('metadata').put(metadata);
    }
   };
  });
 }finally{database.close();}
}
async function se532ProjectSaveRpc(type,payload,transfer){
 const localId=getProjectId();
 if(type!=='cloud.save'||!(payload.bytes instanceof ArrayBuffer)||
    !Number.isInteger(payload.expectedRevision)||payload.expectedRevision<0)
  throw Error('Invalid native project account write.');
 if(se532PendingProjectSaves.has(localId))throw se532UnknownSave();
 const native=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(payload.bytes));
 if(native.project?.instanceId!==localId)throw Error('Account project identity differs from the active project.');
 const pending={schema:'se-project-save-pending-v1',localId,
  accountId:payload.projectId||null,expectedRevision:payload.expectedRevision,
  sha256:await se532ProjectDigest(payload.bytes)};
 if(getProjectId()!==localId||!ready||!se176AccountConnected)
  throw Error('Project or account changed before account write. No account write was attempted.');
 se532PendingProjectSaves.set(localId,pending);
 const row=se175Snapshot();let prepared=false;
 try{
  if(row.id!==localId)throw Error('Project identity changed');
  await se175Store([row]);prepared=true;
  if(getProjectId()!==localId||!ready||!se176AccountConnected)throw Error('Project or account changed');
 }catch(error){
  se532PendingProjectSaves.delete(localId);
  // IndexedDB aborts failed stores atomically. Only a completed transaction
  // needs cleanup, using its latest row rather than the earlier snapshot.
  if(prepared)try{await se532ClearPreparedReceipt(localId,pending);}catch{}
  throw Error('Local account-save receipt could not be stored. No account write was attempted.');
 }
 let result;
 try{result=await rpc(type,payload,transfer);}catch(error){throw se532UnknownSave();}
 const saved=result?.project;
 if(result?.durable!==true||!bounded(saved?.id,160)||
    saved.revision!==pending.expectedRevision+1||
    (pending.accountId&&saved.id!==pending.accountId))throw se532UnknownSave();
 se532AcknowledgedProjectSaves.set(localId,{id:saved.id,revision:saved.revision});
 return result;
}
async function se532RecoverProjectSave(localId,pending){
 // A new-project request with a lost acknowledgement has no remote ID. Only
 // an explicit authenticated account load may supply one; never guess by name.
 const accountId=pending.accountId||cloudRefs.get(localId)?.id;
 if(!bounded(accountId,160))throw se532UnknownSave();
 const listed=await rpc('cloud.list');
 const entry=listed?.projects?.find(p=>p.id===accountId);
 if(entry?.revision!==pending.expectedRevision+1)throw se532UnknownSave();
 const remote=await rpc('cloud.load',{projectId:accountId});
 if(remote?.project?.id!==accountId||remote.project.revision!==entry.revision||
    !(remote.bytes instanceof ArrayBuffer)||remote.bytes.byteLength>MAX_RAW)
  throw se532UnknownSave();
 const native=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(remote.bytes));
 if(native.project?.instanceId!==localId||await se532ProjectDigest(remote.bytes)!==pending.sha256)
  throw se532UnknownSave();
 if(getProjectId()!==localId||!ready||!se176AccountConnected)
  throw Error('Project or account changed while checking the saved receipt. No account write was attempted.');
 const linked={id:accountId,revision:entry.revision};
 cloudRefs.set(localId,linked);se532PendingProjectSaves.delete(localId);
 se532AcknowledgedProjectSaves.delete(localId);
 await se371RememberLink(localId,linked);
 se532RecoveredProjectSave={localId,...linked};
 return true;
}
async function se532SaveCheckedProjectAccount(){
 const localId=getProjectId();se532RecoveredProjectSave=null;
 const pending=se532PendingProjectSaves.get(localId);
 if(pending)return await se532RecoverProjectSave(localId,pending);
 return await se488PreviousAccountSave()===true;
}
function se532RecoveredReceiptMatches(localId,linked){
 return se532RecoveredProjectSave?.localId===localId&&
  se532RecoveredProjectSave.id===linked?.id&&
  se532RecoveredProjectSave.revision===linked?.revision;
}
/* SE532_PROJECT_ACCOUNT_SAVE_RECEIPT_END */
