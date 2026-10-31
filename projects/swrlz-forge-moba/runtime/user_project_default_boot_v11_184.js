// §E v11.184 — one native startup preference across templates, local projects
// and account projects. No project bytes or credentials are put in localStorage.
// Explicit ?project= routes continue to take precedence.
(function se184SavedDefaultInstall(){
 const PREF='swyrl.engine.defaultStarter.v1',PREFIX='saved:';
 let boot=null;
 const validId=id=>typeof id==='string'&&id.length>0&&id.length<=160&&!/[\u0000-\u001f\u007f]/.test(id);
 function read(){
  let value;
  try{value=localStorage.getItem(PREF)}catch{return null}
  if(typeof value!=='string'||!value.startsWith(PREFIX))return null;
  const source=value.startsWith('saved:local:')?'local':value.startsWith('saved:cloud:')?'cloud':'';
  const id=source?value.slice(('saved:'+source+':').length):'';
  return source&&validId(id)?{source,id,key:value}:null;
 }
 function sync(){
  const selected=read()?.key||'';
  for(const box of document.querySelectorAll('#projectHub input[data-se184-default]')){
   box.checked=box.dataset.se184Default===selected;
   const card=box.closest('.se184-project-card');
   card?.classList.toggle('se184-is-default',box.checked);
  }
 }
 function set(source,id){
  const value=source===null?null:(['local','cloud'].includes(source)&&validId(id)?'saved:'+source+':'+id:undefined);
  if(value===undefined)return false;
  try{
   if(value===null)localStorage.removeItem(PREF);
   else localStorage.setItem(PREF,value);
  }catch{if(typeof toast==='function')toast('Could not save a default on this device.');sync();return false}
  if(typeof se128SyncChoices==='function')se128SyncChoices();
  sync();
  if(window.SWRLZ_FORGE_BUILD)window.SWRLZ_FORGE_BUILD.defaultProject=value||'glitch-dragons-den';
  return true;
 }
 function status(label){
  let el=document.getElementById('se184DefaultBoot');
  if(!el){
   el=document.createElement('div');el.id='se184DefaultBoot';
   el.setAttribute('role','status');el.setAttribute('aria-live','polite');
   document.body.append(el);
  }
  el.hidden=!label;
  el.textContent=label||'';
 }
 function complete(state,success,reason=''){
  if(boot!==state||!state.pending)return;
  state.pending=false;clearTimeout(state.timeout);
  window.se128StartupPending=false;
  if(!success){
   // A saved default is a user preference, not a reason to strand §E if
   // IndexedDB or the account is unavailable. Do not mutate that preference.
   try{loadCanonicalGlitchDen()}catch(e){console.error('§E saved default fallback',e)}
   if(reason&&typeof toast==='function')toast(reason.slice(0,150));
  }
  status('');
 }
 async function readLocal(id){
  const db=await new Promise((resolve,reject)=>{
   if(!window.indexedDB)return reject(Error('On-device project storage unavailable'));
   const req=indexedDB.open('swyrl-engine-projects-v1',2);
   req.onupgradeneeded=()=>{
    const db=req.result;
    if(!db.objectStoreNames.contains('projects'))
     db.createObjectStore('projects',{keyPath:'id'});
    if(!db.objectStoreNames.contains('metadata')){
     const meta=db.createObjectStore('metadata',{keyPath:'id'});
     if(req.transaction&&req.oldVersion>0){
      const cursor=req.transaction.objectStore('projects').openCursor();
      cursor.onsuccess=()=>{
       const item=cursor.result;if(!item)return;
       const {data,...record}=item.value;meta.put(record);item.continue();
      };
     }
    }
   };
   req.onsuccess=()=>resolve(req.result);
   req.onerror=()=>reject(Error('Could not read on-device project storage'));
   req.onblocked=()=>reject(Error('On-device project storage is busy'));
  });
  try{return await new Promise((resolve,reject)=>{
   const tx=db.transaction('projects','readonly'),request=tx.objectStore('projects').get(id);
   request.onsuccess=()=>resolve(request.result);
   request.onerror=()=>reject(Error('Saved project could not be read'));
  })}finally{db.close()}
 }
 async function loadLocal(state){
  try{
   status('Opening default project · Reading saved scene…');
   const row=await readLocal(state.id);
   if(!row?.data?.project||!Array.isArray(row.data.scene?.actors))throw Error('Saved project not found on this device');
   if(!state.pending||boot!==state)return;
   status('Opening default project · Building scene…');
   if(document.visibilityState!=='hidden')await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
   if(!state.pending||boot!==state)return;
   if(typeof dirty!=='undefined'&&dirty&&currentProject!==state.before)
    throw Error('Workspace changed during default loading');
   loadProject(structuredClone(row.data),{workspaceLocal:true});
   if(typeof ModelAtelier!=='undefined'){
    ModelAtelier.syncProject();
    if(currentProject?.kind==='model-atelier')ModelAtelier.open();
    else ModelAtelier.close();
   }
   if(typeof markSaved==='function')markSaved();
   complete(state,true);
  }catch(error){
   console.error('§E local default load',error);
   complete(state,false,'Default saved project unavailable; opened Dragon Den. Choose another default in Projects.');
  }
 }
 function launch(){
  const choice=read();
  if(!choice)return false;
  const state={...choice,pending:true,loading:false,before:typeof currentProject!=='undefined'?currentProject:null,timeout:null};
  boot=state;window.se128StartupPending=true;
  if(choice.source==='local'){
   status('Opening default project · Reading from this device…');
   queueMicrotask(()=>void loadLocal(state));
  }else{
   status('Opening default account project · Connecting to § Chat…');
   state.timeout=setTimeout(()=>{
    complete(state,false,'Account project not available yet. Sign in through § Chat, then load it in My Projects.');
   },11000);
  }
  return true;
 }
 async function openCloud(loader){
  const state=boot;
  if(!state?.pending||state.source!=='cloud'||state.loading||typeof loader!=='function')return false;
  state.loading=true;
  status('Opening default account project · Downloading saved scene…');
  try{
   const result=await loader(state.id);
   if(!state.pending||boot!==state)return false;
   complete(state,result===true,result===true?'':'Could not open the account default; open it from My Projects.');
   return result===true;
  }catch(error){
   console.error('§E cloud default load',error);
   complete(state,false,'Account project could not be opened; use My Projects to retry.');
   return false;
  }
 }
 window.SWYRL_ENGINE_SAVED_DEFAULT=Object.freeze({read,set,sync,launch,openCloud,
  pending:()=>boot?.pending?{source:boot.source,id:boot.id,loading:boot.loading}:null
 });
})();
