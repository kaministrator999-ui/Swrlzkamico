/* SE476_ENGINE_ACCOUNT_START_START */
(function se476EngineAccountStart(){
 'use strict';
 // Startup UI never owns login credentials or scene deserialization.
 // Only existing native §E project and §Chat account handlers can load data.
 const SESSION='swrlz.engine.last-session.v1';
 const $=id=>document.getElementById(id);
 let started=false,finished=false,account='pending',session=null,rows=[],opening=false,epoch=0,listing=false,attempt=0;
 function read(){
  try{
   const o=JSON.parse(localStorage.getItem(SESSION)||'null');
   return o&&['local','cloud'].includes(o.source)&&typeof o.id==='string'&&o.id.length>0&&o.id.length<=160?o:null;
  }catch{return null;}
 }
 session=read();
 function currentStudio(){return window.SWYRL_ENGINE_STUDIOS?.active?.()||window.SWYRL_ENGINE_WORKSPACES?.active?.()||'game';}
 function captureCamera(){
  try{
   const s=window.SWYRL_ENGINE_MODEL_CAMERA?.inspect?.();
   if(!s?.ready||!['perspective','orthographic'].includes(s.projection))return null;
   const vec=v=>Array.isArray(v)&&v.length===3&&v.every(n=>Number.isFinite(n)&&Math.abs(n)<1e5);
   return vec(s.position)&&vec(s.target)&&Number.isFinite(s.distance)?{
    position:[...s.position],target:[...s.target],projection:s.projection,
    distance:s.distance,view:s.view
   }:null;
  }catch{return null;}
 }
 function persist(){
  // Never replace an existing last-session camera/studio with background
  // startup defaults before the account/project choice has resolved.
  if(!finished||!session)return;
  session.studio=currentStudio();
  if(session.studio==='modeler')session.camera=captureCamera()||session.camera||null;
  session.updatedAt=Date.now();
  try{localStorage.setItem(SESSION,JSON.stringify(session));}catch{}
 }
 function markLoaded(source,id){
  if(!['local','cloud'].includes(source)||typeof id!=='string'||!id||id.length>160)return;
  session={source,id,studio:currentStudio(),camera:null,updatedAt:Date.now()};
  // Native project routing may complete on its next microtask.
  queueMicrotask(()=>{if(session?.source===source&&session.id===id)persist();});
 }
 function offlineScreen(show){
  const el=$('se476SignalLost');
  if(!el)return;
  const wasHidden=el.hidden;
  el.hidden=!show;
  if(show&&wasHidden){
   $('se476RetryConnection')?.focus?.({preventScroll:true});
  }else if(!show&&!wasHidden){
   $('se476SignIn')?.focus?.({preventScroll:true});
  }
 }
 function offlineDeadline(ms=16000){
  const ticket=++attempt;
  setTimeout(()=>{
   if(ticket!==attempt||finished||account!=='pending')return;
   account='offline';updateAccountStatus();offlineScreen(true);
   void list();note('§C connection unavailable. Retry or continue with your on-device projects.',true);
  },ms);
 }
 function retryConnection(){
  if(finished)return;
  account='pending';++epoch;updateAccountStatus();offlineScreen(false);
  note('Reconnecting to §C… Local projects remain safe.');
  const api=accountAPI();
  if(api?.retry?.()!==true){offlineScreen(true);note('§C connection unavailable. Continue with local projects.',true);}
  else offlineDeadline(14000);
 }
 function note(message,problem=false){
  const node=$('se476StartupStatus');
  if(node){node.textContent=message;node.dataset.error=String(!!problem);}
 }
 function accountAPI(){return window.SWYRL_ENGINE_STARTUP_ACCOUNT_476;}
 function updateAccountStatus(){
  const label=$('se476AccountLabel');
  if(label)label.textContent=account==='connected'?'Google account connected':account==='guest'?'§C connected · Sign in with Google to sync projects':account==='offline'?'§C offline · On-device projects available':'Checking Google account…';
  const login=$('se476SignIn');
  if(login){login.hidden=account==='connected';login.disabled=account==='connected';}
 }
 function defaults(){
  const chosen=window.SWYRL_ENGINE_SAVED_DEFAULT?.read?.();
  if(chosen?.source&&chosen.id)return {source:chosen.source,id:chosen.id,explicit:true};
  if(session)return {source:session.source,id:session.id,explicit:false};
  return null;
 }
 function chosenRow(){
  const id=$('se476Projects')?.value||'';
  const [source,...parts]=id.split(':');const real=parts.join(':');
  return ['local','cloud'].includes(source)&&real?{source,id:real}:null;
 }
 function paint(){
  const sel=$('se476Projects');if(!sel)return;
  const earlier=sel.value;
  sel.replaceChildren();
  const blank=document.createElement('option');blank.value='';blank.textContent='Continue current workspace';
  sel.append(blank);
  for(const row of rows){
   const o=document.createElement('option');
   o.value=row.source+':'+row.id;
   o.textContent=(row.source==='cloud'?'Google · ':'On device · ')+(row.name||'Untitled').slice(0,90);
   sel.append(o);
  }
  const wanted=defaults();
  const fallback=wanted?.source+':'+wanted?.id;
  const values=[...sel.options].map(x=>x.value);
  sel.value=values.includes(earlier)?earlier:values.includes(fallback)?fallback:'';
  const checkbox=$('se476Remember');
  if(checkbox){const chosen=chosenRow();checkbox.checked=!!chosen&&!!window.SWYRL_ENGINE_SAVED_DEFAULT?.read?.()&&
    window.SWYRL_ENGINE_SAVED_DEFAULT.read().source===chosen.source&&
    window.SWYRL_ENGINE_SAVED_DEFAULT.read().id===chosen.id;}
 }
 async function list(){
  if(listing)return;
  listing=true;const token=++epoch;
  note('Syncing saved project names…');
  try{
   const api=accountAPI();
   // Local library is available even if the Chat origin is offline.
   const data=api?.list?await api.list():{local:[],cloud:[]};
   if(token!==epoch)return;
   rows=[...(Array.isArray(data.local)?data.local:[]).filter(x=>x?.id).map(x=>({...x,source:'local'})),
     ...(account==='connected'&&Array.isArray(data.cloud)?data.cloud:[]).filter(x=>x?.id).map(x=>({...x,source:'cloud'}))];
   paint();note(account==='connected'?'Account and saved projects ready.':'On-device projects ready.');
  }catch(err){
   if(token===epoch){rows=rows.filter(x=>x.source==='local');paint();note('Account project sync unavailable. You can open locally.',true);}
  }finally{listing=false;}
 }
 function afterLoad(entry,previous){
  if(entry?.source&&entry.id&&!(session?.source===entry.source&&session.id===entry.id))markLoaded(entry.source,entry.id);
  if(previous?.studio){
   const studio=previous.studio,cam=previous.camera;
   if(session){session.studio=studio;session.camera=cam||null;}
   queueMicrotask(persist);
   if(['game','modeler','particles','materials'].includes(studio)){
    queueMicrotask(()=>{window.SWYRL_ENGINE_STUDIOS?.change?.(studio);
     if(studio==='modeler'&&cam)restoreCamera(cam,0);});
   }
  }
 }
 function restoreCamera(cam,count){
  if(finished&&session?.camera!==cam)return;
  const ok=window.SWYRL_ENGINE_STARTUP_CAMERA_476?.restore?.(cam);
  if(!ok&&count<8)setTimeout(()=>restoreCamera(cam,count+1),250);
 }
 async function openSelected(override){
  if(opening||finished)return;
  opening=true;
  const entry=override||chosenRow()||defaults();
  const previous=session?.source===entry?.source&&session?.id===entry?.id?{...session}:null;
  try{
   if(entry?.source==='cloud'&&account!=='connected')throw Error('Sign in to load this Google project.');
   if(entry){
    note('Opening '+(entry.source==='cloud'?'Google':'on-device')+' project…');
    const api=accountAPI();
    if(!api||entry.source==='cloud'&&!api.ready?.())throw Error('Project loader is not connected.');
    if(entry.explicit===true&&window.SWYRL_ENGINE_SAVED_DEFAULT?.pending?.()==null&&window.SWYRL_ENGINE_SAVED_DEFAULT?.report?.()?.success===true){
     afterLoad(entry,previous);finish();return;
    }
    const ok=entry.source==='cloud'?await api.loadCloud(entry.id):await api.loadLocal(entry.id);
    if(ok!==true)throw Error('Native project loader did not confirm success.');
    afterLoad(entry,previous);
   }
   finish();
  }catch(err){
   note(String(err?.message||err)+' Choose another project or continue locally.',true);
  }finally{opening=false;}
 }
 function finish(){
  finished=true;const gate=$('se476StartupGate');if(gate)gate.hidden=true;
  document.documentElement.dataset.se476AccountStartup='complete';
  window.dispatchEvent(new CustomEvent('swrlz:engine-startup-complete',{detail:{account:account==='connected'}}));
 }
 async function signIn(){
  const api=accountAPI();
  if(!api?.ready?.()){note('Chat account connection is not ready. You can continue locally.',true);return;}
  note('Complete Google sign-in in the secure account window.');
  // Synchronous user-click path preserves the popup user gesture.
  api.signIn();
 }
 function continueLocal(){
  ++epoch;account='offline';updateAccountStatus();
  const choice=chosenRow();
  if(choice?.source==='local')void openSelected(choice);
  else if(session?.source==='local')void openSelected(session);
  else finish();
 }
 function onAccount(event){
  if(finished)return;
  const connected=event.detail?.authenticated===true;
  account=connected?'connected':'guest';++attempt;
  updateAccountStatus();offlineScreen(false);
  if(account==='connected'){
   void list().then(()=>{
    if(finished)return;
    // An explicit default outranks the last successfully opened project.
    // When no default is checked, last session wins.
    const choice=defaults();
    if(choice)void openSelected(choice);
    else note('Signed in. Choose a project or enter your current workspace.');
   });
  }else{
   ++epoch;rows=rows.filter(x=>x.source==='local');paint();void list();
   note('§C is connected. Sign in with Google or continue with local projects.');
  }
 }
 function install(){
  if(started)return;
  if(!$('se476StartupGate'))return;
  started=true;
  // Native release notes use the browser's top layer and otherwise intercept
  // clicks even above a fixed 2-billion-z-index account/outage gate.
  const releaseDialog=$('seReleaseNotesDialog');
  if(releaseDialog){
   const defer=()=>{if(!finished&&releaseDialog.open)releaseDialog.close();};
   defer();
   new MutationObserver(defer).observe(releaseDialog,{attributes:true,attributeFilter:['open']});
  }
  updateAccountStatus();paint();
  $('se476SignIn')?.addEventListener('click',signIn);
  $('se476RetryConnection')?.addEventListener('click',retryConnection);
  $('se476ContinueLocal')?.addEventListener('click',continueLocal);
  $('se476OfflineContinue')?.addEventListener('click',continueLocal);
  $('se476Open')?.addEventListener('click',()=>void openSelected());
  $('se476Remember')?.addEventListener('change',e=>{
   const entry=chosenRow();
   if(e.target.checked&&entry)window.SWYRL_ENGINE_SAVED_DEFAULT?.set?.(entry.source,entry.id);
   else window.SWYRL_ENGINE_SAVED_DEFAULT?.set?.(null);
   paint();
  });
  $('se476Projects')?.addEventListener('change',()=>{
   const chosen=chosenRow(),pref=window.SWYRL_ENGINE_SAVED_DEFAULT?.read?.();
   $('se476Remember').checked=!!chosen&&pref?.source===chosen.source&&pref?.id===chosen.id;
  });
  window.addEventListener('swrlz:account-assets',onAccount);
  window.addEventListener('swrlz:project-loaded',()=>{
   if(session)queueMicrotask(persist);
  });
  window.addEventListener('pagehide',persist);
  window.addEventListener('visibilitychange',()=>{if(document.hidden)persist();});
  document.addEventListener('pointerup',e=>{
   if(session&&e.target?.closest?.('#modelAtelierPanel .atelier-scene'))setTimeout(persist,120);
  },{passive:true});
  document.addEventListener('wheel',e=>{
   if(session&&e.target?.closest?.('#modelAtelierPanel .atelier-scene'))setTimeout(persist,150);
  },{passive:true});
  // Prewarm the existing authenticated §Chat iframe without showing its
  // full chat panel. Never duplicate Google OAuth or transfer a credential.
  const warm=()=>{
   const f=$('seChatFrame');
   if(f&&!f.getAttribute('src')){f.src='https://kamiloki-swyrlz.hf.space/?forgeEmbed=1';return true;}
   return !!f;
  };
  if(!warm()){let n=0;const tick=()=>{if(finished)return;if(warm())return;if(++n<20)setTimeout(tick,200);};setTimeout(tick,150);}
  // Account service outages must never block the locally persisted editor.
  offlineDeadline(16000);
 }
 window.SWYRL_ENGINE_STARTUP_476=Object.freeze({
  markLoaded,retryConnection,readLast:()=>session?{...session}:null,
  inspect:()=>({ready:started,finished,account,rows:rows.length,opening,selection:chosenRow(),default:defaults()}),
  refresh:()=>void list()
 });
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});
 else queueMicrotask(install);
})();
/* SE476_ENGINE_ACCOUNT_START_END */