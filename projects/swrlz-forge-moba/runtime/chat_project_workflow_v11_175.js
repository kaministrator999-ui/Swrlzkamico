// Native project creation is one explicit, typed transition. Starter builders
// remain immutable. Local snapshots are independent of Google account storage.
let se175Transition=false,se175LocalLoading=false,se175Saving=null,se175SaveTimer=null,se175ProjectLabel=null,se175LocalList=null,se175LocalStatus=null;
const SE175_DB='swyrl-engine-projects-v1';
const se175StarterKinds={
 'blank-scene':['Blank scene','sandbox','scene'],
 'blank-model':['Blank 3D model','model-atelier','model-atelier'],
 'glitch-dragons-den':["Dragon Den",'dragons-den','scene'],
 'starforge-observatory':['Starforge Observatory','spatial-workspace','scene'],
 'anime-ghosts-ep01':['Anime Episode 01','anime-production-set','scene'],
 'sheep-tag-meadow':['Sheep Tag','sheep-tag','scene'],
 'maul-frostveil':['Maul Frostveil','maul','scene'],
 'festival-girl-saved':['Saved Festival Girl','model-atelier','model-atelier'],
 'model-atelier':['Model Atelier','model-atelier','model-atelier'],
 'wolf-model':['Wolf model','model-atelier','model-atelier'],
 'sheep-model':['Sheep model','model-atelier','model-atelier']
};
// Starter definitions keep their native canonical identity for model/game
// tools. Editable workspace drafts and exports belong to the independent copy.
const se175NativeWorkspaceKey=workspaceStorageKey;
workspaceStorageKey=function(stationId){return currentProject?.instanceId?'swyrl.workspace.v1:'+encodeURIComponent(currentProject.instanceId)+':'+encodeURIComponent(stationId):se175NativeWorkspaceKey(stationId);};
const se175NativeResetWorkspace=resetWorkspaceState;
resetWorkspaceState=function(allowLocal=false){return se175NativeResetWorkspace(allowLocal&&!se175Transition);};
function se175Starters(){return Object.entries(se175StarterKinds).map(([id,[name,kind,workspace]])=>({id,name,kind,workspace}));}
function se175LocalMessage(text){if(se175LocalStatus)se175LocalStatus.textContent=text;}
async function se175Db(){
 return new Promise((resolve,reject)=>{
  if(!globalThis.indexedDB){reject(Error('LOCAL_PROJECT_STORAGE_UNAVAILABLE'));return;}
  const request=indexedDB.open(SE175_DB,2);
  request.onupgradeneeded=event=>{
   const db=request.result;if(!db.objectStoreNames.contains('projects'))db.createObjectStore('projects',{keyPath:'id'});
   if(!db.objectStoreNames.contains('metadata')){
    const meta=db.createObjectStore('metadata',{keyPath:'id'});
    // A preview database can already hold snapshots. Upgrade one row at a
    // time; listing never clones all complete projects into browser memory.
    if(event.oldVersion>0){const cursor=request.transaction.objectStore('projects').openCursor();cursor.onsuccess=()=>{const item=cursor.result;if(!item)return;const {data,...row}=item.value;meta.put(row);item.continue();};}
   }
  };
  request.onerror=()=>reject(Error('LOCAL_PROJECT_STORAGE_UNAVAILABLE'));
  request.onblocked=()=>reject(Error('LOCAL_PROJECT_STORAGE_BLOCKED'));
  request.onsuccess=()=>resolve(request.result);
 });
}
async function se175Store(records){
 const db=await se175Db();
 try{await new Promise((resolve,reject)=>{
  const tx=db.transaction(['projects','metadata'],'readwrite');
  tx.oncomplete=resolve;tx.onerror=tx.onabort=()=>reject(Error('LOCAL_PROJECT_SAVE_FAILED'));
  const store=tx.objectStore('projects'),meta=tx.objectStore('metadata');for(const row of records){store.put(row);const {data,...metadata}=row;meta.put(metadata);}
 });}finally{db.close();}
}
async function se175Read(key){
 const db=await se175Db();
 try{return await new Promise((resolve,reject)=>{
  const tx=db.transaction(key?'projects':'metadata','readonly'),request=key?tx.objectStore('projects').get(key):tx.objectStore('metadata').getAll(undefined,1000);
  request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(Error('LOCAL_PROJECT_READ_FAILED'));
 });}finally{db.close();}
}
function se175Snapshot(){
 const data=structuredClone(window.SWYRL_ENGINE_AGENT.inspectScene());
 const projectId=getProjectId();data.project.instanceId=projectId;
 data.project.projectName=currentProject.projectName||currentProject.name;
 return {id:projectId,name:summaryName(data.project.projectName),starterId:summaryName(data.project.sourceStarterId||data.project.template),updatedAt:new Date().toISOString(),data};
}
function se175ScheduleSave(){
 se175UpdateLabel();if(se175Transition||!currentProject?.instanceId)return;
 clearTimeout(se175SaveTimer);se175SaveTimer=setTimeout(()=>{
  const snapshot=se175Snapshot();
  se175Saving=se175Store([snapshot]).then(()=>se175LocalMessage('Saved on this device.')).catch(()=>{se175LocalMessage('Local autosave failed. Use Save Project to download a copy.');}).finally(()=>{se175Saving=null;});
 },350);
}
function se175UpdateLabel(){
 if(!se175ProjectLabel)return;
 const name=summaryName(currentProject?.projectName||currentProject?.name)||'Untitled project';
 const level=typeof seLevels!=='undefined'?seLevelsCurrent():null;
 se175ProjectLabel.textContent='Active project · '+name+(level?' · '+summaryName(level.name):'')+(dirty?' · unsaved changes':'');
 se175ProjectLabel.title='This is the project Chat inspects before each request.';
}
function se175StampProject(projectId,name,starterId){
 const stamp=meta=>{meta.instanceId=projectId;meta.projectName=name;meta.sourceStarterId=starterId;};
 stamp(currentProject);currentProject.name=name;
 if(typeof seLevels!=='undefined'&&seLevels.records.size){
  const root='project-'+projectId;seLevels.root=root;currentProject.levelProjectRoot=root;
  for(const record of seLevels.records.values()){stamp(record.data.project);record.data.project.levelProjectRoot=root;}
  delete currentProject.levelPack;delete currentProject.levelSystem;
  seLevelsRefresh();
 }
 projectIds.set(currentProject,projectId);
 const nameEl=document.getElementById('currentProjectName');if(nameEl)nameEl.textContent=name;
 const statusEl=document.getElementById('projectStatus');if(statusEl)statusEl.textContent=name;
 if(currentProject.modelAtelier)currentProject.modelAtelier.name=name;
}
async function se175Create(op,active,before){
 if(se175Transition||se175LocalLoading||cloudBusy)throw Error('PROJECT_OPERATION_IN_PROGRESS');
 if(!Object.hasOwn(se175StarterKinds,op.starterId))throw Error('UNSUPPORTED_STARTER');
 const recovery=se175Snapshot(),recoveryState={dirty,history:structuredClone(history),historyIndex,revision};
 // Do not replace an unsaved workspace until a complete recovery copy has
 // actually committed. Quota/storage failures stop before the native builder.
 if(se175Saving)await se175Saving;
 await se175Store([recovery]);
 if(!isVisible()||lease!==active||JSON.stringify(context())!==JSON.stringify(before))throw Error('STALE_NATIVE_PRECONDITIONS');
 const projectId=id(),restoreInert=[];
 const block=document.createElement('dialog');block.id='se175ProjectProgress';block.setAttribute('aria-label','Creating project');block.textContent='Creating '+op.name+'…';block.addEventListener('cancel',event=>event.preventDefault());document.body.append(block);block.showModal();
 for(const element of [document.getElementById('app'),document.getElementById('modelAtelierPanel')])if(element){restoreInert.push([element,element.inert]);element.inert=true;}
 se175Transition=true;
 try{
  if(op.starterId==='blank-scene'){
   ModelAtelier.close();loadProject({project:{name:op.name,template:'blank-scene',kind:'sandbox',environment:'spatial-workspace',environmentSettings:{background:'#101827',showTerrain:false,showScenery:false}},editor:{},scene:{background:'#101827',paths:{},actors:[]}},{workspaceLocal:true});
  }else{
   const loaded=await Promise.resolve(createProjectFromTemplate(op.starterId,true));
   if(loaded===false)throw Error('STARTER_LOAD_FAILED');
  }
  if(!isVisible()||lease!==active)throw Error('EDITOR_DETACHED');
  se175StampProject(projectId,op.name,op.starterId);workspaceLocalAllowed=true;
  ModelAtelier.syncProject();if(currentProject.kind==='model-atelier')ModelAtelier.open();else ModelAtelier.close();
  initializeHistory('Created '+op.name+' from '+se175StarterKinds[op.starterId][0]);markDirty();
  const created=se175Snapshot();await se175Store([created]);
  if(!isVisible()||lease!==active||getProjectId()!==projectId)throw Error('EDITOR_DETACHED');
  se175UpdateLabel();se175LocalMessage('Created '+op.name+' · saved on this device.');
  return {changed:true,projectId,name:op.name,starterId:op.starterId,previousProjectId:recovery.id,localSaved:true};
 }catch(error){
  // Restore the exact previous project if a loader or new-project save failed.
  try{se175Restore(recovery,recoveryState);}catch{throw Error('PROJECT_CREATE_FAILED_RECOVERY_COPY_SAVED');}
  throw error;
 }finally{
  se175Transition=false;for(const [element,value] of restoreInert)element.inert=value;block.close();block.remove();
 }
}
async function se175RefreshLocal(){
 if(!se175LocalList)return;
 try{
  const records=await se175Read();se175LocalList.replaceChildren();
  const empty=document.createElement('option');empty.value='';empty.textContent=records.length?'Choose a project on this device':'No local projects yet';se175LocalList.append(empty);
  for(const record of records.sort((a,b)=>b.updatedAt.localeCompare(a.updatedAt))){const option=document.createElement('option');option.value=record.id;option.textContent=summaryName(record.name);se175LocalList.append(option);}
  se175LocalMessage((records.length===1000?'Showing up to 1,000 local project names. ':'')+'Local copies stay in this browser. Save to account separately to sync devices.');
 }catch{se175LocalMessage('Local project storage unavailable. Native file Save/Load is still available.');}
}
function se175Restore(recovery,state){
 loadProject(structuredClone(recovery.data),{workspaceLocal:true});
 ModelAtelier.syncProject();if(currentProject.kind==='model-atelier')ModelAtelier.open();else ModelAtelier.close();
 history=state.history;historyIndex=state.historyIndex;revision=state.revision;updateHistoryUI();
 if(state.dirty)markDirty();else markSaved();se175UpdateLabel();
}
async function se175LoadLocal(){
 if(se175Transition||se175LocalLoading||cloudBusy||!se175LocalList?.value)return;
 se175LocalLoading=true;let recovery=null,recoveryState=null,started=false;
 try{
  const wanted=await se175Read(se175LocalList.value);if(!wanted?.data?.project||!Array.isArray(wanted.data.scene?.actors))throw Error('LOCAL_PROJECT_NOT_FOUND');
  const before=context();recovery=se175Snapshot();recoveryState={dirty,history:structuredClone(history),historyIndex,revision};await se175Store([recovery]);
  if(JSON.stringify(context())!==JSON.stringify(before))throw Error('PROJECT_CHANGED_BEFORE_LOCAL_LOAD');
  revoke('Loading another local project.');started=true;
  loadProject(structuredClone(wanted.data),{workspaceLocal:true});ModelAtelier.syncProject();if(currentProject.kind==='model-atelier')ModelAtelier.open();else ModelAtelier.close();
  document.getElementById('projectHub')?.classList.remove('show');se175UpdateLabel();se175LocalMessage('Loaded '+wanted.name+'.');
 }catch(error){
  if(started&&recovery)try{se175Restore(recovery,recoveryState);}catch{se175LocalMessage('Load failed. The previous project recovery copy is saved on this device.');return;}
  se175LocalMessage('Could not load local project: '+summaryName(error.message));
 }finally{se175LocalLoading=false;}
}
function se175Install(){
 const account=document.querySelector('#seChatAccountPanel .se-chat-account');
 if(account&&!document.getElementById('se175ActiveProject')){se175ProjectLabel=document.createElement('div');se175ProjectLabel.id='se175ActiveProject';se175ProjectLabel.setAttribute('role','status');se175ProjectLabel.setAttribute('aria-live','polite');account.prepend(se175ProjectLabel);se175UpdateLabel();}
 const pane=document.getElementById('se170-pane-mine');if(!pane||document.getElementById('se175LocalProjects'))return;
 const section=document.createElement('section');section.id='se175LocalProjects';section.className='se170-my-tools';section.setAttribute('aria-label','Projects on this device');
 const title=document.createElement('strong');title.textContent='On this device';
 se175LocalList=document.createElement('select');se175LocalList.id='se175LocalProjectList';se175LocalList.setAttribute('aria-label','Local projects');
 const refresh=document.createElement('button');refresh.type='button';refresh.textContent='Refresh local projects';refresh.onclick=se175RefreshLocal;
 const load=document.createElement('button');load.type='button';load.id='se175LoadLocal';load.textContent='Load local project';load.onclick=se175LoadLocal;
 se175LocalStatus=document.createElement('p');se175LocalStatus.id='se175LocalStatus';se175LocalStatus.setAttribute('role','status');
 section.append(title,se175LocalList,refresh,load,se175LocalStatus);pane.prepend(section);
 document.getElementById('se170-tab-mine')?.addEventListener('click',se175RefreshLocal);
}
