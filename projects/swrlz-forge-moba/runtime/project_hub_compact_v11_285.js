// §E v11.285: native starter category repair, independent of Chat account host.
// Reparent existing card/checkbox nodes: never clone or replace project handlers.
(()=>{
 'use strict';
 const gameIds=new Set(['blank-vr-hands']);
 const modelIds=new Set([
  'plain-hand-base','rocky-anime-hand','floating-hand-glove','arcane-glove-left',
  'comet-courier','blank-model','festival-girl-saved',
  'sheep-free-shelter','sheep-thatched-hut','sheep-cottage',
  'sheep-barn','sheep-ram-house','sheep-model','wolf-model'
 ]);
 function modelCard(card){
  const id=card?.dataset?.projectTemplate||'';
  if(!id||gameIds.has(id))return false;
  if(modelIds.has(id))return true;
  const tag=(card.querySelector('.template-tag')?.textContent||'').toLowerCase();
  if(/starter game|game starter|playable game/.test(tag))return false;
  if(/starter model|native 3d model|model atelier|model starter|rigged model/.test(tag))return true;
  return /(?:^|[-_])(?:model|atelier|sculpt|ferret|glove|character|festival)(?:$|[-_])/.test(id);
 }
 function cardIn(node){
  return node?.matches?.('button[data-project-template]')?node:
   node?.querySelector?.('button[data-project-template]');
 }
 function makeTabs(hub,grid){
  if(hub.querySelector('#se236StarterGroups'))return;
  const models=document.createElement('div');
  models.id='se236StarterModels';models.className=grid.className+' se236-starter-grid';
  models.hidden=true;
  grid.id='se236StarterGames';grid.classList.add('se236-starter-grid');
  const tabs=document.createElement('div');tabs.id='se236StarterGroups';
  tabs.className='se236-starter-tabs';tabs.setAttribute('role','tablist');
  tabs.setAttribute('aria-label','Starter project types');
  function choose(which){
   for(const [key,panel] of [['games',grid],['models',models]]){
    const selected=which===key;
    panel.hidden=!selected;
    const button=tabs.querySelector('#se236StarterTab-'+key);
    button.setAttribute('aria-selected',String(selected));
    button.tabIndex=selected?0:-1;
   }
   const win=hub.querySelector('.project-window');
   if(win)win.scrollTop=0;
  }
  for(const [key,title,panel] of [['games','Starter Games',grid],['models','Starter Models',models]]){
   panel.setAttribute('role','tabpanel');
   const button=document.createElement('button');
   button.type='button';button.id='se236StarterTab-'+key;
   button.textContent=title;button.setAttribute('role','tab');
   button.setAttribute('aria-controls',panel.id);
   panel.setAttribute('aria-labelledby',button.id);
   button.onclick=()=>choose(key);
   button.onkeydown=event=>{
    if(!['ArrowLeft','ArrowRight'].includes(event.key))return;
    event.preventDefault();
    const next=key==='games'?'models':'games';choose(next);
    tabs.querySelector('#se236StarterTab-'+next)?.focus();
   };
   tabs.append(button);
  }
  grid.before(tabs);grid.after(models);choose('games');
 }
 function repair(){
  const hub=document.getElementById('projectHub');
  if(!hub)return false;
  let games=hub.querySelector('#se236StarterGames');
  let models=hub.querySelector('#se236StarterModels');
  if(!games||!models){
   const grid=hub.querySelector('#se170-pane-starter .project-grid')||hub.querySelector('.project-grid');
   if(!grid)return false;
   makeTabs(hub,grid);
   games=hub.querySelector('#se236StarterGames');
   models=hub.querySelector('#se236StarterModels');
  }
  if(!games||!models)return false;
  for(const child of [...games.children]){
   const card=cardIn(child);
   if(card&&modelCard(card))models.append(child);
  }
  for(const child of [...models.children]){
   const card=cardIn(child);
   if(card&&!modelCard(card))games.append(child);
  }
  return true;
 }
 function install(){
  const hub=document.getElementById('projectHub');
  if(!hub)return;
  // Move the modal out of app/inspector stacking contexts without cloning nodes.
  if(hub.parentNode!==document.body)document.body.appendChild(hub);
  let queued=false,openPreviously=false;
  const schedule=()=>{
   if(queued)return;queued=true;
   requestAnimationFrame(()=>{
    queued=false;repair();
    const open=hub.classList.contains('show');
    if(open&&!openPreviously){
     const win=hub.querySelector('.project-window');
     if(win)win.scrollTop=0;
    }
    openPreviously=open;
   });
  };
  new MutationObserver(schedule).observe(hub,{subtree:true,childList:true,attributes:true,attributeFilter:['class']});
  schedule();
  window.SWYRL_ENGINE_PROJECT_HUB_285=Object.freeze({repair,status:()=>({
   games:hub.querySelectorAll('#se236StarterGames [data-project-template]').length,
   models:hub.querySelectorAll('#se236StarterModels [data-project-template]').length,
   miscModelsInGames:[...hub.querySelectorAll('#se236StarterGames [data-project-template]')]
    .filter(modelCard).map(card=>card.dataset.projectTemplate),
   misplacedGamesInModels:[...hub.querySelectorAll('#se236StarterModels [data-project-template]')]
    .filter(card=>!modelCard(card)).map(card=>card.dataset.projectTemplate)
  })});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});
 else queueMicrotask(install);
})();
