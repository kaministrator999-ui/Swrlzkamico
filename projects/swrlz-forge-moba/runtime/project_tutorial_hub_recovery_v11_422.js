/* SE422_PROJECT_TUTORIAL_HUB_RECOVERY_START
 * This snippet belongs inside se412SatchelTutorial's existing closure.
 * Native se170 Projects remains the owner; this is a third tab and recovery
 * hook, not a second project hub or an account-storage replacement.
 */
 let se422Observer=null,se422ObservedHub=null,se422Pending=false;
 let se422Repairs=0,se422LastIssue='';
 const se422OriginalSelect=se170Select;
 se170Select=function se422SelectProjectTab(name){
   const response=se422OriginalSelect(name);
   const hub=document.getElementById('projectHub');
   const pane=hub?.querySelector('#se412Tutorials');
   const tab=hub?.querySelector('#se412Tab');
   if(pane)pane.hidden=name!=='tutorial';
   if(tab){tab.setAttribute('aria-selected',String(name==='tutorial'));tab.tabIndex=name==='tutorial'?0:-1;}
   return response;
 };
 function installLibrary(){
   const hub=document.getElementById('projectHub');
   if(!hub)return false;
   // The original se170 installer can run after the one-shot tutorial startup.
   // Invoke it on demand when the native hub exists but its tabs do not.
   if(!hub.querySelector('.se170-hub-tabs')&&hub.querySelector('.project-window .project-head')){
     try{se170Install();}catch(error){se422LastIssue='Native project tabs: '+String(error?.message||error).slice(0,100);}
   }
   const tabs=hub.querySelector('.se170-hub-tabs');
   const starter=hub.querySelector('#se170-pane-starter');
   if(!tabs||!starter){se422LastIssue='Waiting for the native Projects tablist';return false;}
   let tab=hub.querySelector('#se412Tab'),pane=hub.querySelector('#se412Tutorials');
   // Repair a partially rebuilt library: a surviving tab without its pane
   // must not prevent reinstall, and a detached pane does not count as ready.
   if(tab&&!pane){tab.remove();tab=null;}
   if(pane&&!tab){pane.remove();pane=null;}
   if(tab&&pane){
     if(tab.parentElement!==tabs)tabs.append(tab);
     if(pane.parentElement!==starter.parentElement)starter.after(pane);
     se422LastIssue='';return true;
   }
   pane=document.createElement('section');pane.className='se170-hub-pane';
   pane.id='se412Tutorials';pane.hidden=true;
   pane.setAttribute('role','tabpanel');pane.setAttribute('aria-labelledby','se412Tab');
   pane.innerHTML='<h3>Modeling tutorials</h3><p>Build the Apprentice Satchel yourself, one real modeling operation at a time. A separate project is saved in My Projects, never into the original starter.</p><div class="se412-library-actions" id="se412LibraryActions"></div><p id="se412LibraryNotice" role="status"></p>';
   const actionRow=pane.querySelector('#se412LibraryActions');
   actionRow.append(button('Start new satchel quest',()=>void newLesson()),button('Resume satchel quest',()=>void resume()));
   starter.after(pane);
   tab=button('Tutorials',()=>se170Select('tutorial'));
   tab.id='se412Tab';tab.setAttribute('role','tab');
   tab.setAttribute('aria-controls',pane.id);tab.setAttribute('aria-selected','false');
   tab.tabIndex=-1;tabs.append(tab);
   tab.addEventListener('keydown',event=>{
     if(event.key!=='ArrowLeft'&&event.key!=='ArrowRight')return;
     const all=[...tabs.querySelectorAll('button[role="tab"]')];
     const currentIndex=all.indexOf(tab);
     const next=all[(currentIndex+(event.key==='ArrowLeft'?-1:1)+all.length)%all.length];
     if(!next)return;
     event.preventDefault();next.focus();next.click();
   });
   se422Repairs++;se422LastIssue='';
   return true;
 }
 function se422QueueRepair(){
   if(se422Pending)return;
   se422Pending=true;
   queueMicrotask(()=>{se422Pending=false;schedule();});
 }
 function se422ObserveHub(hub){
   if(!hub||se422ObservedHub===hub||typeof MutationObserver!=='function')return;
   se422Observer?.disconnect();
   se422ObservedHub=hub;
   se422Observer=new MutationObserver(records=>{
     if(!hub.isConnected)return;
     const missing=!hub.querySelector('#se412Tab')||
      !hub.querySelector('#se412Tutorials')||
      !hub.querySelector('.se170-hub-tabs')||
      !hub.querySelector('#se170-pane-starter');
     // Listen to reconstruction of the native dialog and its open state;
     // ordinary account-card mutations never force a re-render of the tutorial.
     if(missing||records.some(r=>r.type==='attributes'&&r.target===hub))se422QueueRepair();
   });
   se422Observer.observe(hub,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});
 }
 function schedule(){
   const hub=document.getElementById('projectHub');
   if(hub){
     se422ObserveHub(hub);
     installLibrary();
   }
   if(belongs())attachPanel();
 }
 function se422Inspect(){
   const hub=document.getElementById('projectHub');
   const tabs=hub?.querySelector('.se170-hub-tabs');
   const tab=hub?.querySelector('#se412Tab'),pane=hub?.querySelector('#se412Tutorials');
   return {hub:!!hub,hubOpen:!!hub?.classList.contains('show'),
     nativeTabs:!!tabs,starter:!!hub?.querySelector('#se170-pane-starter'),
     mine:!!hub?.querySelector('#se170-pane-mine'),
     tutorialTab:!!tab,tutorialPane:!!pane,
     tutorialSelected:tab?.getAttribute('aria-selected')==='true',
     projectSaved:belongs(),repairs:se422Repairs,lastIssue:se422LastIssue};
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',schedule,{once:true});
 else queueMicrotask(schedule);
 document.addEventListener('click',event=>{
   if(event.target?.closest?.('#projectBtn,#se320ModelProjects,#modelAtelierPanel .atelier-head'))
    requestAnimationFrame(schedule);
 },true);
 window.addEventListener('swrlz:project-loaded',()=>requestAnimationFrame(schedule));
 // If a Project hub is mounted after document-ready, install once when it
 // becomes available. The focused hub observer then owns future recovery.
 if(!document.getElementById('projectHub')&&typeof MutationObserver==='function'){
   const readyObserver=new MutationObserver(()=>{
     if(document.getElementById('projectHub')){readyObserver.disconnect();se422QueueRepair();}
   });
   readyObserver.observe(document.documentElement,{childList:true,subtree:true});
 }
 window.SWYRL_ENGINE_PROJECT_TUTORIAL_HUB_422=Object.freeze({inspect:se422Inspect,
  repair:()=>{schedule();return se422Inspect();}});
 /* SE422_PROJECT_TUTORIAL_HUB_RECOVERY_END */