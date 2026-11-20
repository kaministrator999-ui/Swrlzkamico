/* SE528_ACCOUNT_PROJECT_REPAIR_START */
// Keep §C identity and tokens on the existing chat origin. This repair uses
// only the previously authenticated editor bridge; it creates no new cloud API.
const se528PriorGetProjectId=getProjectId;
getProjectId=function(){
 if(currentProject&&typeof currentProject==='object'&&
    bounded(currentProject.instanceId,160)&&
    currentProject.instanceId!==currentProject.canonicalId&&
    currentProject.se371TemplateSource!==true){
  projectIds.set(currentProject,currentProject.instanceId);
  return currentProject.instanceId;
 }
 return se528PriorGetProjectId();
};
// The cloud picker presents "cloud:<id>", while the original importer only
// accepted a raw ID. VR project browsing also passes the ID explicitly.
// Normalize at this one shared boundary rather than rewriting every caller.
const se528PriorLoadCloud=loadCloud;
loadCloud=async function(projectKey){
 if(typeof projectKey==='string'&&projectKey.length){
  const id=projectKey.startsWith('cloud:')?projectKey.slice(6):projectKey;
  if(!bounded(id,160)){setStatus('Invalid account project ID.',true);return false;}
  const option=[...cloudList.options].find(x=>x.value==='cloud:'+id||x.value===id);
  if(option)cloudList.value=option.value;
  else {const opt=document.createElement('option');opt.value=id;opt.textContent='Account project';cloudList.append(opt);cloudList.value=id;}
 }
 // Legacy loader reads cloudList.value, so temporarily pass the raw account ID.
 const prior=cloudList?.value||'';
 if(prior.startsWith('cloud:'))cloudList.value=prior.slice(6);
 // The select may not list a raw option. Append a scoped, temporary option.
 let transient=null;
 if(cloudList&&cloudList.value!==prior.replace(/^cloud:/,'')){
  transient=document.createElement('option');transient.value=prior.replace(/^cloud:/,'');
  transient.textContent='Loading saved account project';cloudList.append(transient);
  cloudList.value=transient.value;
 }
 try{
  await se528PriorLoadCloud.call(this);
  // The legacy importer catches its own errors and returns undefined even
  // after success. Its cloudRefs revision receipt is authoritative instead.
  const applied=cloudRefs.get(getProjectId());
  const requested=prior.replace(/^cloud:/,'');
  return !!applied?.id&&applied.id===requested&&Number.isInteger(applied.revision);
 }
 finally{
  if(transient)transient.remove();
  if(cloudList&&prior&&[...cloudList.options].some(x=>x.value===prior))cloudList.value=prior;
 }
};
let se528SaveBusy=false;
async function se528SaveAccount(){
 if(se528SaveBusy||cloudBusy||se175Transition||se175LocalLoading||playing||simulating){
  se371Display('A project operation is already active. Finish it before saving to account.',true);
  return {ok:false,error:'PROJECT_BUSY'};
 }
 if(!ready||!se176AccountConnected){
  if(!ready&&frame&&!frame.src)frame.src=CHAT_ORIGIN+'/?forgeEmbed=1';
  se371Display('Connect §wyrlz Chat and sign in with Google before saving to account.',true);
  return {ok:false,error:'ACCOUNT_NOT_CONNECTED'};
 }
 se528SaveBusy=true;
 try{
  if(!se371HasSavedIdentity())await se372StoreVRProjectAsNew();
  else await se371SaveLocal();
  const ok=await saveCloud()===true;
  if(!ok){
   const detail=status?.textContent||'Cloud save was not confirmed by the account service.';
   se371Display('Saved locally, but account sync failed: '+detail,true);
   return {ok:false,error:'CLOUD_SAVE_NOT_CONFIRMED',detail};
  }
  await se176RefreshProjects().catch(()=>{});
  se371Display('Saved '+se371ProjectName()+' to your account and this device.');
  return {ok:true,name:se371ProjectName(),scope:'account'};
 }catch(error){
  se371Display('Account save failed: '+String(error?.message||error),true);
  return {ok:false,error:String(error?.message||error)};
 }finally{se528SaveBusy=false;}
}
// Both the Chat panel's Save to account and the My Projects library button
// use the same durable cloud operation. Never report success for local-only.
function se528InstallAccountSave(){
 const chat=document.getElementById('seChatSave');
 if(chat&&!chat.dataset.se528SaveBound){
  chat.dataset.se528SaveBound='true';
  chat.onclick=()=>void se528SaveAccount();
 }
 const tools=document.querySelector('#se170-pane-mine .se170-my-tools');
 if(tools&&!tools.querySelector('[data-se528-save-account]')){
  const button=document.createElement('button');button.type='button';
  button.dataset.se528SaveAccount='true';button.textContent='Save active project to account';
  button.onclick=()=>void se528SaveAccount();tools.append(button);
 }
}
const se528PriorMount=mount;
mount=function(...args){const result=se528PriorMount.apply(this,args);se528InstallAccountSave();return result;};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',se528InstallAccountSave,{once:true});
else queueMicrotask(se528InstallAccountSave);
window.SWYRL_ENGINE_ACCOUNT_SAVE_528=Object.freeze({
 save:se528SaveAccount,status:()=>({connected:!!(ready&&se176AccountConnected),busy:se528SaveBusy||cloudBusy})
});
/* SE528_ACCOUNT_PROJECT_REPAIR_END */