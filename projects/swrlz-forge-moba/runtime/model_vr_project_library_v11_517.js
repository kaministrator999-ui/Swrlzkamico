/* SE517_PROJECT_LIBRARY_START
   Authenticated §E project operations, inside the existing §Chat closure.
   Lists names only; credentials, cloud RPC and actual loads never cross to XR.
   A verified recovery copy is committed before replacing any active project. */
const se517ProjectLibrary=(()=>{
 'use strict';
 const supported=meta=>meta?.kind==='model-atelier'&&!!meta.modelAtelier;
 const busy=()=>se175Transition||se175LocalLoading||cloudBusy||playing||simulating;
 const validId=value=>typeof value==='string'&&value.length>0&&value.length<=160;
 const name=value=>summaryName(value||'Untitled project').slice(0,74);
 function starters(){
  return se175Starters().filter(x=>x.workspace==='model-atelier').map(x=>({
   id:x.id,name:name(x.name),source:'starter'
  }));
 }
 async function list(){
  if(busy())throw Error('Another project operation is in progress');
  const stored=await se175Read();
  const local=(Array.isArray(stored)?stored:[]).filter(x=>validId(x?.id)).slice(0,120)
   .map(x=>({id:x.id,name:name(x.name),source:'local'}));
  let cloud=[],online=false;
  if(ready&&se176AccountConnected){
   online=true;
   try{
    await se176RefreshProjects();
    cloud=(se176CloudRows||[]).filter(x=>validId(x?.id)).slice(0,120)
     .map(x=>({id:x.id,name:name(x.name),source:'cloud',revision:x.revision}));
   }catch(error){online=false;}
  }
  return {local,cloud,starters:starters(),accountConnected:online};
 }
 async function open(source,key){
  if(!['local','cloud','starter'].includes(source)||!validId(key))
   throw Error('Invalid project selection');
  if(busy())throw Error('Finish the previous save or project operation');
  if(source==='cloud'&&(!ready||!se176AccountConnected))
   throw Error('Google account is not connected');
  const catalog=await list();
  if(!catalog[source==='starter'?'starters':source]?.some(row=>row.id===key))
   throw Error('Project is not in the available library');
  let target=null;
  // Preflight saved local documents before releasing the current model root.
  if(source==='local'){
   const row=await se175Read(key);
   if(!row?.data?.project||!Array.isArray(row.data.scene?.actors))
    throw Error('The saved project is missing or incomplete');
   if(!supported({...row.data.project,modelAtelier:row.data.project.modelAtelier||row.data.modelAtelier}))
    throw Error('Only Model Atelier projects can open in immersive Model Studio');
   target=row;
  }
  const before=se175Snapshot(),savedState={dirty,history:structuredClone(history),
   historyIndex,revision},recoveryId=id();
  const recovery=structuredClone(before);
  recovery.id=recoveryId;recovery.name=('VR recovery · '+before.name).slice(0,100);
  recovery.data.project={...recovery.data.project,instanceId:recoveryId,
   projectName:recovery.name,name:recovery.name,
   sourceStarterId:se371SourceId(),se371TemplateSource:false};
  delete recovery.data.project.cloudRef;
  recovery.updatedAt=new Date().toISOString();
  if(se175Saving)await se175Saving;
  await se175Store([recovery]);
  let attempted=false;
  se175Transition=true;
  try{
   attempted=true;
   if(source==='local'){
    loadProject(structuredClone(target.data),{workspaceLocal:true});
    se175StampProject(key,name(target.name),target.starterId||se371SourceId());
    workspaceLocalAllowed=true;
    ModelAtelier.syncProject();ModelAtelier.open();
    initializeHistory('Opened '+name(target.name));markSaved();
    window.SWYRL_ENGINE_STARTUP_476?.markLoaded?.('local',key);
   }else if(source==='cloud'){
    const loaded=await loadCloud(key);
    if(loaded!==true)throw Error('Account project loader did not confirm success');
    if(!supported(currentProject))throw Error('Account project is not a Model Atelier project');
    ModelAtelier.syncProject();ModelAtelier.open();
    window.SWYRL_ENGINE_STARTUP_476?.markLoaded?.('cloud',key);
   }else{
    const choice=se175StarterKinds[key];
    if(!choice||choice[2]!=='model-atelier')throw Error('Starter cannot run in Model Studio');
    const loaded=await Promise.resolve(createProjectFromTemplate(key,true));
    if(loaded===false||!supported(currentProject))throw Error('Starter is not a Model Atelier project');
    const newId=id(),newName=name(choice[0])+' VR';
    se175StampProject(newId,newName,key);
    workspaceLocalAllowed=true;ModelAtelier.syncProject();ModelAtelier.open();
    initializeHistory('Created from '+name(choice[0]));markDirty();
    await se175Store([se175Snapshot()]);
    window.SWYRL_ENGINE_STARTUP_476?.markLoaded?.('local',newId);
   }
   se175UpdateLabel();void se175RefreshLocal().catch(()=>{});
   return {ok:true,name:se371ProjectName(),recoveryId};
  }catch(error){
   if(attempted){
    try{se175Restore(before,savedState);}
    catch(rollback){throw Error('Load failed; recovery saved as '+recovery.name+'. '+String(error?.message||error));}
   }
   throw error;
  }finally{se175Transition=false;}
 }
 return Object.freeze({list,open,status:()=>({busy:busy(),dirty:!!dirty,
  name:se371ProjectName(),canSwitch:!!ModelAtelier})});
})();
window.SWYRL_ENGINE_VR_PROJECT_LIBRARY_517=se517ProjectLibrary;
/* SE517_PROJECT_LIBRARY_END */
