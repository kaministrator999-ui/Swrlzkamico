/* SE351_GAME_QUICK_ACTIONS_START */
// Restore accessible Game Engine controls without cloning native buttons or handlers.
(function se351GameQuickActions(){
 'use strict';
 const pick=(id)=>document.getElementById(id);
 const primary=['projectBtn','playBtn','stopBtn','se181EnterVR'];
 let scheduled=false, toolbarObserved=null, drawerObserved=null;
 const observer=new MutationObserver(()=>schedule());
 function schedule(){
  if(scheduled)return;
  scheduled=true;
  queueMicrotask(()=>{scheduled=false;reconcile();});
 }
 function reconcile(){
  const app=document.querySelector('.app[data-se320-ui]');
  const header=pick('se320GameHeader');
  const toolbar=app?.querySelector(':scope > .topbar');
  const more=pick('se320GameMore');
  const box=more?.querySelector('.se320-game-extras');
  if(!app||!header||!toolbar||!more||!box)return;
  let row=pick('se351GameQuickBar');
  if(!row){
   row=document.createElement('nav');
   row.id='se351GameQuickBar';
   row.setAttribute('aria-label','Game Engine quick actions');
   header.append(row);
  }
  const nativeAction=(id)=>{
   const el=pick(id);
   if(el&&el.parentElement!==row)row.append(el);
  };
  for(const id of primary)nativeAction(id);
  if(more.parentElement!==row)row.append(more);
  const quest=pick('se238GameTools');
  const drawer=quest?.querySelector('.se238-drawer-content');
  // On Quest the older browser layout moves toolbar nodes into this drawer
  // before the v11.320 studio header is created. Restore those exact nodes.
  if(drawer){
   for(const el of [...drawer.children]){
    if(primary.includes(el.id)){nativeAction(el.id);continue;}
    if(el.id==='engineMenubar'||el.classList.contains('se187-game-tabs'))continue;
    if(el.id!=='se238GameToolsToggle'&&el!==more)box.append(el);
   }
   if(!quest.hidden){
    quest.hidden=true;
    pick('se238GameToolsToggle')?.setAttribute('aria-expanded','false');
   }
  }
  // When Quest browser mode changes, its original-node restoration can move
  // the controls back to the topbar; reconcile again without duplicating them.
  for(const el of [...toolbar.children]){
   if(primary.includes(el.id)){nativeAction(el.id);continue;}
   if(el===more||el.id==='fileInput'||el.id==='engineMenubar'||
      el.classList.contains('se187-game-tabs')||
      el.classList.contains('sep')||el.classList.contains('spacer')||
      el.id==='se238GameToolsToggle')continue;
   box.append(el);
  }
  if(more.querySelector(':scope > summary')){
   const summary=more.querySelector(':scope > summary');
   if(summary.textContent!=='More options')summary.textContent='More options';
   summary.setAttribute('aria-label','Open more Game Engine options');
  }
  app.dataset.se351GameActions='true';
  if(toolbarObserved!==toolbar||drawerObserved!==drawer){
   observer.disconnect();
   observer.observe(toolbar,{childList:true});
   if(drawer)observer.observe(drawer,{childList:true});
   toolbarObserved=toolbar;drawerObserved=drawer||null;
  }
 }
 function boot(){
  reconcile();
  // Late mounted controller/VR buttons preserve their original listeners.
  window.addEventListener('load',schedule,{once:true});
  window.addEventListener('swrlz:project-loaded',schedule);
  const app=document.querySelector('.app');
  if(app)new MutationObserver(schedule).observe(app,{childList:true});
  new MutationObserver(schedule).observe(document.documentElement,
   {attributes:true,attributeFilter:['class','data-se-device-profile']});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});
 else queueMicrotask(boot);
})();
/* SE351_GAME_QUICK_ACTIONS_END */
