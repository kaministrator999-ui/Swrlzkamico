// §E v11.187 — separate routed modeler page, in-place workspace tabs and untitled draft.
// One engine instance, native rendering/handlers retained. Switching tabs never
// reloads the page or swaps the game scene/currentProject.
(function se187WorkspaceTabs(){
 const key='swrlz.engine.untitled-model-v1',limit=1500000;
 const gameURL=()=>new URL('index.html',location.href);
 const modelURL=()=>new URL('modeler.html',location.href);
 const isModelRoute=()=>/\/modeler\.html$/i.test(location.pathname);
 let active=isModelRoute()?'modeler':'game',preferScratch=false;
 let scratch=null,saveTimer=null,draftChanged=false,writeFailure='';
 let lastGameProject=null,gameBootSkipped=isModelRoute(),initializedGame=!gameBootSkipped;
 let observer=null,watchBody=null,transitioning=false;
 const blank=()=>{
  // Keep native editable schema options, but never import the canonical starter's meshes.
  const base=typeof MODEL_ATELIER_CANONICAL_PROJECT!=='undefined'
   ?structuredClone(MODEL_ATELIER_CANONICAL_PROJECT?.project?.modelAtelier||{}):{};
  return {...base,schema:'swyrl-model-atelier-v1',parts:[],editedAt:'local',name:'Untitled model'};
 };
 function validDraft(v){
  if(!v||v.schema!=='swyrl-model-atelier-v1'||!Array.isArray(v.parts)||
     v.parts.length>MODEL_ATELIER_LIMIT)return false;
  const ids=new Set();
  return v.parts.every(p=>{
   if(!p||typeof p.id!=='string'||p.id.length>100||ids.has(p.id)||!MODEL_ATELIER_KINDS.includes(p.kind)||!/^#[0-9a-fA-F]{6}$/.test(p.color))return false;
   ids.add(p.id);
   return ['position','rotation','scale'].every(k=>
    Array.isArray(p[k])&&p[k].length===3&&p[k].every(n=>typeof n==='number'&&Number.isFinite(n)&&Math.abs(n)<=100))
    &&p.scale.every(n=>n>.005&&n<=20);
  });
 }
 function readDraft(){
  if(scratch)return scratch;
  scratch=blank();
  try{
   const raw=localStorage.getItem(key);
   if(raw&&raw.length<=limit){
    const value=JSON.parse(raw);
    if(validDraft(value))scratch=value;
   }
  }catch(error){writeFailure=String(error?.name||'Storage error');}
  return scratch;
 }
 function flushDraft(){
  clearTimeout(saveTimer);saveTimer=null;
  if(!scratch||!draftChanged)return;
  try{
   const raw=JSON.stringify(scratch);
   if(raw.length>limit)throw Error('Draft exceeds local storage safety limit; export JSON');
   localStorage.setItem(key,raw);
   draftChanged=false;writeFailure='';
  }catch(error){writeFailure=String(error?.message||error).slice(0,100);}
  renderTabs();
 }
 function draftEdited(){
  if(!usingScratch())return;
  readDraft().editedAt='local';
  draftChanged=true;
  clearTimeout(saveTimer);
  saveTimer=setTimeout(flushDraft,650);
  renderTabs();
 }
 function usingScratch(){
  return active==='modeler'&&(preferScratch||currentProject?.kind!=='model-atelier'||!currentProject?.modelAtelier);
 }
 function scratchModel(){return readDraft();}
 function onNativeLoad(data){
  if(data?.project?.kind==='model-atelier')preferScratch=false;
  renderTabs();
 }
 function renderTabs(){
  const actual=active;
  for(const nav of document.querySelectorAll('.se187-workspace-tabs')){
   for(const button of nav.querySelectorAll('[data-se187-tab]')){
    const on=button.dataset.se187Tab===actual;
    button.classList.toggle('active',on);
    button.setAttribute('aria-selected',String(on));
    button.tabIndex=on?0:-1;
   }
   const status=nav.querySelector('.se187-draft-state');
   if(status){
    const draft=usingScratch();
    const count=draft?readDraft().parts.length:currentProject?.modelAtelier?.parts?.length||0;
    status.textContent=actual==='modeler'
     ?(draft?'Untitled model · '+count+' meshes'+(writeFailure?' · Export JSON to save':''):'Loaded model · '+count+' meshes')
     :'Scene editor';
   }
   const blankButton=nav.querySelector('.se187-new-model');
   if(blankButton)blankButton.hidden=actual!=='modeler';
  }
 }
 function makeTabs(where){
  const nav=document.createElement('nav');
  nav.className='se187-workspace-tabs '+(where==='modeler'?'se187-model-tabs':'se187-game-tabs');
  nav.setAttribute('role','tablist');
  nav.setAttribute('aria-label','§E editor workspaces');
  for(const [id,label] of [['game','Game Engine'],['modeler','Modeler']]){
   const button=document.createElement('button');
   button.type='button';button.dataset.se187Tab=id;
   button.textContent=label;button.setAttribute('role','tab');
   button.setAttribute('aria-label','Switch to '+label+' workspace');
   button.addEventListener('click',()=>void change(id,true));
   nav.append(button);
  }
  nav.addEventListener('keydown',event=>{
   if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
   const tabs=[...nav.querySelectorAll('[data-se187-tab]')];
   if(!tabs.length)return;
   const current=tabs.indexOf(document.activeElement);
   const index=event.key==='Home'?0:event.key==='End'?tabs.length-1:
    (current+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
   event.preventDefault();
   tabs[index].click();tabs[index].focus();
  });
  const status=document.createElement('span');
  status.className='se187-draft-state';
  nav.append(status);
  if(where==='modeler'){
   const newModel=document.createElement('button');
   newModel.className='se187-new-model';
   newModel.textContent='+ Blank model';
   newModel.type='button';
   newModel.title='Begin an untitled mesh draft, separate from saved projects';
   newModel.addEventListener('click',newBlankModel);
   nav.append(newModel);
  }
  return nav;
 }
 function installTabs(){
  const topbar=document.querySelector('.app > .topbar');
  if(topbar&&!topbar.querySelector('.se187-workspace-tabs'))
   topbar.prepend(makeTabs('game'));
  const panel=document.getElementById('modelAtelierPanel');
  if(panel&&!panel.querySelector('.se187-model-tabs')){
   panel.prepend(makeTabs('modeler'));
   if(!panel.dataset.se187Observed){
    panel.dataset.se187Observed='1';
    observer=new MutationObserver(()=>{
     if(transitioning||active!=='modeler'||!panel.hidden)return;
     // Native Close may close asynchronously during a model project reload;
     // defer tab navigation until the panel has actually stayed closed.
     setTimeout(()=>{if(active==='modeler'&&panel.hidden&&!transitioning)void change('game',true);},80);
    });
    observer.observe(panel,{attributes:true,attributeFilter:['hidden']});
   }
  }
  renderTabs();
 }
 function newBlankModel(){
  const old=usingScratch()?readDraft().parts.length:currentProject?.modelAtelier?.parts?.length||0;
  if(old>0&&!confirm('Start a blank untitled model? Your existing model remains in its saved project, but your current untitled draft will be replaced. Export any unsaved work first.'))return;
  scratch=blank();
  preferScratch=true;
  draftChanged=true;flushDraft();
  if(typeof ModelAtelier!=='undefined'&&active==='modeler'){
   // Reopen the existing native viewport so its geometry/selection truly
   // reflects the new empty model; never replace its renderer or handlers.
   ModelAtelier.close();
   ModelAtelier.syncProject();
   ModelAtelier.open();
  }
  renderTabs();
 }
 function urlFor(mode){
  const url=mode==='modeler'?modelURL():gameURL();
  // Keep the editor route independent from any ?project= deep-link.
  return url.pathname;
 }
 function updateRoute(mode){
  if(location.pathname!==urlFor(mode))
   try{history.pushState({se187Workspace:mode},'',urlFor(mode));}catch(error){console.warn('§E workspace URL routing unavailable',error);}
 }
 function change(mode,push=false){
  if(mode!=='game'&&mode!=='modeler')return false;
  transitioning=true;
  try{
   if(mode==='modeler'){
    active='modeler';readDraft();
    const ok=ModelAtelier.open();
    if(ok===false){active='game';renderTabs();return false;}
    document.getElementById('projectHub')?.classList.remove('show');
    installTabs();
   }else{
    active='game';
    ModelAtelier.close();
    // Commit visible tab/URL before costly native scene initialization.
    // This also prevents a transient active=game while URL stays modeler.
    if(push)updateRoute(mode);
    renderTabs();
    if(!initializedGame){
     initializedGame=true;
     try{loadCanonicalGlitchDen();}catch(error){
      console.error('§E game scene initialization',error);
      if(typeof toast==='function')toast('Could not create a default game scene. Open Projects to retry.');
     }
    }
   }
   if(push&&mode==='modeler')updateRoute(mode);
   renderTabs();
   return true;
  }finally{transitioning=false;}
 }
 function boot(){
  installTabs();
  if(active==='modeler')change('modeler',false);
  renderTabs();
 }
 const controller=Object.freeze({
  active:()=>active,modelerActive:()=>active==='modeler',
  scratchModel,usingScratch,isScratchModel:data=>data===scratch,
  draftEdited,onNativeLoad,newBlankModel,
  change:(mode)=>change(mode,true),
  inspect:()=>({active,route:location.pathname,gameBootSkipped,initializedGame,
    draftParts:scratch?.parts?.length||0,draftChanged,storageError:writeFailure,
    projectKind:currentProject?.kind||null})
 });
 window.SWYRL_ENGINE_WORKSPACES=controller;
 window.addEventListener('popstate',()=>change(isModelRoute()?'modeler':'game',false));
 window.addEventListener('pagehide',flushDraft);
 // Mount against the original editor's DOM once its module has initialized.
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(boot,0),{once:true});
 else setTimeout(boot,0);
})();
