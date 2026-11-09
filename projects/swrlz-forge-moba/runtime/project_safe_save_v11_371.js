/* §E v11.371 — independent Save / Clone Project, preserving canonical starters. */
const se371CloudLinks=new Map();
let se371ActionBusy=false;
function se371ProjectName(){return summaryName(currentProject?.projectName||currentProject?.name)||'Untitled project';}
function se371SourceId(){return summaryName(currentProject?.sourceStarterId||currentProject?.template||currentProject?.canonicalId||'starter');}
function se371HasSavedIdentity(){
 return bounded(currentProject?.instanceId,160)&&
 currentProject.instanceId!==currentProject.canonicalId&&
 currentProject.se371TemplateSource!==true;
}
function se371Display(message,error=false){
 const el=document.getElementById('se371ProjectNotice');
 if(el){el.textContent=message;el.dataset.error=String(error);}
 if(typeof se175LocalMessage==='function')se175LocalMessage(message);
 if(typeof setStatus==='function')setStatus(message,error);
 if(typeof toast==='function')toast(message);
}
function se371VersionedLink(link){
 return link&&bounded(link.id,160)&&Number.isInteger(link.revision)&&link.revision>=1
 ?{id:link.id,revision:link.revision}:null;
}
// Metadata stays in the existing, independent IndexedDB project row.
const se371PriorSnapshot=se175Snapshot;
se175Snapshot=function(...args){
 const row=se371PriorSnapshot.apply(this,args);
 const link=se371VersionedLink(cloudRefs.get(row.id)||se371CloudLinks.get(row.id));
 if(link)row.cloudRef=link;
 return row;
};
const se371PriorRead=se175Read;
se175Read=async function(key){
 const result=await se371PriorRead.apply(this,arguments);
 if(key){const link=se371VersionedLink(result?.cloudRef);if(link)se371CloudLinks.set(key,link);}
 return result;
};
async function se371RememberLink(localId,remote){
 const link=se371VersionedLink(remote);
 if(!link||!bounded(localId,160))return;
 se371CloudLinks.set(localId,link);
 if(getProjectId()===localId){
  try{await se175Store([se175Snapshot()]);}
  catch(error){console.warn('§E account link local mirror unavailable',error);}
 }
}
const se371PreviousSaveCloud=saveCloud;
saveCloud=async function(...args){
 const localId=getProjectId();
 // Default project loaders can bypass the on-device project picker.
 if(!se371CloudLinks.has(localId)&&!cloudRefs.has(localId)){
  try{await se175Read(localId);}catch{}
 }
 const saved=se371CloudLinks.get(localId);
 if(!cloudRefs.has(localId)&&saved&&ready){
  try{
   const listed=await rpc('cloud.list');
   const entry=listed?.projects?.find(p=>p.id===saved.id);
   if(entry&&entry.revision===saved.revision)cloudRefs.set(localId,saved);
   else if(entry)throw Error('Account revision changed on another device. Your local project is safe; reopen the newest account version or clone it.');
   else throw Error('This project is not in the signed-in account. Your local copy is safe; clone it to make a separate copy.');
  }catch(error){se371Display('Account save stopped: '+error.message,true);return false;}
 }
 const was=cloudRefs.get(localId);
 await se371PreviousSaveCloud.apply(this,args);
 const after=cloudRefs.get(localId);
 if(after&&(after!==was||after.revision!==was?.revision)){
  await se371RememberLink(localId,after);
  return true;
 }
 return false;
};
const se371PreviousLoadCloud=loadCloud;
loadCloud=async function(...args){
 const opened=await se371PreviousLoadCloud.apply(this,args);
 if(opened===true){
  const localId=getProjectId(),link=cloudRefs.get(localId);
  // Authenticate and validate first; then fix older account documents lacking an independent ID.
  if(link&&!se371HasSavedIdentity())se175StampProject(localId,se371ProjectName(),se371SourceId());
  if(link)await se371RememberLink(localId,link);
 }
 return opened;
};
function se371NewName(base){return (base+' Copy').slice(0,100);}
function se371SafeName(value){
 const name=summaryName(value||'').trim().slice(0,100);
 if(!name)throw Error('Project name is required.');
 return name;
}
async function se371SaveLocal(){
 if(!se371HasSavedIdentity())throw Error('A starter must be cloned before saving.');
 if(se175Saving)await se175Saving;
 const row=se175Snapshot();
 if(row.id!==currentProject.instanceId)throw Error('Project identity mismatch; no data was written.');
 await se175Store([row]);
 if(typeof markSaved==='function')markSaved();
 se175UpdateLabel();
 return row;
}
async function se371Clone(name){
 if(se175Transition||se175LocalLoading||cloudBusy||playing||simulating)
  throw Error('Stop playback or loading before cloning.');
 const newName=se371SafeName(name);
 if(se175Saving)await se175Saving;
 const recovery=se175Snapshot();
 const savedState={dirty,history:structuredClone(history),historyIndex,revision};
 const clone=structuredClone(recovery.data),newId=id();
 clone.project={...clone.project,instanceId:newId,name:newName,projectName:newName,
  sourceStarterId:se371SourceId(),se371TemplateSource:false};
 delete clone.project.cloudRef;
 // Multi-level project records must point to the new project, not the source.
 if(clone.project.levelPack?.schema==='se-levels-v1'){
  clone.project.levelProjectRoot='project-'+newId;
  for(const level of clone.project.levelPack.levels||[]){
   if(level?.data?.project){
    level.data.project.instanceId=newId;
    level.data.project.projectName=newName;
    level.data.project.name=newName;
    level.data.project.levelProjectRoot='project-'+newId;
   }
  }
 }
 const draft={id:newId,name:newName,starterId:clone.project.sourceStarterId,
  updatedAt:new Date().toISOString(),data:clone};
 // Commit the independent copy before any live editor state is replaced.
 await se175Store([draft]);
 let switched=false;
 try{
  switched=true;loadProject(structuredClone(clone),{workspaceLocal:true});
  se175StampProject(newId,newName,clone.project.sourceStarterId);
  workspaceLocalAllowed=true;
  if(typeof ModelAtelier!=='undefined'){
   ModelAtelier.syncProject();
   if(currentProject.kind==='model-atelier')ModelAtelier.open();
  }
  initializeHistory('Cloned as '+newName);markSaved();
  se371CloudLinks.delete(newId);cloudRefs.delete(newId);
  await se371SaveLocal();
  se175UpdateLabel();
  document.getElementById('projectHub')?.classList.remove('show');
  return newId;
 }catch(error){
  if(switched){try{se175Restore(recovery,savedState);}catch(e){
   throw Error('Clone failed to open; the previous workspace snapshot remains saved on this device.');
  }}
  throw error;
 }
}
async function se371Save(){
 if(!se371HasSavedIdentity())await se371Clone(se371NewName(se371ProjectName()));
 else await se371SaveLocal();
 let synced=false;
 if(ready&&se176AccountConnected)synced=await saveCloud()===true;
 return synced;
}
async function se371Run(mode){
 if(se371ActionBusy)return;
 if(playing||simulating){se371Display('Stop Play/Simulate before saving project edits.',true);return;}
 if(cloudBusy||se175Transition||se175LocalLoading){se371Display('Another project operation is in progress.',true);return;}
 let name;
 if(mode==='clone'){
  const proposed=window.prompt('Name the independent cloned project',se371NewName(se371ProjectName()));
  if(proposed===null)return;
  try{name=se371SafeName(proposed);}catch(e){se371Display(e.message,true);return;}
 }
 se371ActionBusy=true;se371UpdateButtons();
 try{
  let synced=false;
  if(mode==='clone'){
   await se371Clone(name);
   if(ready&&se176AccountConnected)synced=await saveCloud()===true;
  }else synced=await se371Save();
  se371Display((mode==='clone'?'Cloned ':'Saved ')+se371ProjectName()+
   (synced?' · saved to your account and this device.':(ready&&se176AccountConnected?' · saved on this device; account sync was not completed.':' · saved on this device.')));
  await se175RefreshLocal().catch(()=>{});
 }catch(error){se371Display((mode==='clone'?'Clone':'Save')+' failed: '+error.message,true);}
 finally{se371ActionBusy=false;se371UpdateButtons();}
}
function se371Buttons(host,scope){
 if(!host||host.querySelector('[data-se371-controls]'))return;
 const wrap=document.createElement('div');wrap.className='se371-project-actions';wrap.dataset.se371Controls=scope;
 for(const [label,mode] of [['Save Project','save'],['Clone Project','clone']]){
  const button=document.createElement('button');button.type='button';
  button.className='se371-project-button';button.dataset.se371Action=mode;
  button.textContent=label;button.addEventListener('click',()=>void se371Run(mode));
  wrap.append(button);
 }
 host.append(wrap);
}
function se371UpdateButtons(){
 const disabled=se371ActionBusy||cloudBusy||se175Transition||se175LocalLoading||playing||simulating;
 document.querySelectorAll('[data-se371-action]').forEach(b=>{b.disabled=!!disabled;});
}
function se371Install(){
 se371Buttons(document.querySelector('#se170-pane-starter .project-actions')||document.querySelector('#projectHub .project-actions'),'library');
 se371Buttons(document.querySelector('#se170-pane-mine .se170-my-tools'),'my-projects');
 se371Buttons(document.querySelector('#modelAtelierPanel .atelier-head .atelier-actions'),'model');
 se371Buttons(document.querySelector('#se249Root .se249-commandbar'),'particle');
 se371Buttons(document.querySelector('.app > .topbar'),'game');
 if(!document.getElementById('se371ProjectNotice')){
  const note=document.createElement('div');note.id='se371ProjectNotice';
  note.setAttribute('role','status');
  document.getElementById('projectHub')?.querySelector('.project-window')?.append(note);
 }
 se371UpdateButtons();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',se371Install,{once:true});
else queueMicrotask(se371Install);
// Native model/particle windows can be created lazily.
document.addEventListener('click',()=>requestAnimationFrame(se371Install),true);
window.addEventListener('swrlz:project-loaded',()=>requestAnimationFrame(se371Install));
window.SWYRL_ENGINE_SAFE_PROJECTS_371=Object.freeze({
 save:()=>se371Run('save'),clone:()=>se371Run('clone'),
 status:()=>({saved:se371HasSavedIdentity(),id:currentProject?.instanceId||null,
 cloud:!!cloudRefs.get(getProjectId()),busy:se371ActionBusy})
});
