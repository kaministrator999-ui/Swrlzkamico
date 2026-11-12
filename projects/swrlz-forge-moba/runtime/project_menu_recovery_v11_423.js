/* SE423_PROJECT_MENU_RECOVERY_START
 * Supplement v11.422 without replacing the native project hub or storage.
 * Reattach surviving account controls after a dialog reconstruction.
 */
const se423PreviousInstallLibrary=installLibrary;
function se423RepairNativeProjects(){
 const hub=document.getElementById('projectHub');
 if(!hub)return false;
 const win=hub.querySelector('.project-window');
 if(!win?.querySelector('.project-head'))return false;
 let tabs=hub.querySelector('.se170-hub-tabs');
 if(!tabs){
  try{se170Install();}catch(error){se422LastIssue='Native tabs: '+String(error?.message||error).slice(0,100);}
  tabs=hub.querySelector('.se170-hub-tabs');
 }
 if(!tabs)return false;
 const starter=hub.querySelector('#se170-pane-starter');
 if(!starter)return false;
 let startTab=hub.querySelector('#se170-tab-starter');
 if(!startTab){
  startTab=document.createElement('button');startTab.type='button';
  startTab.id='se170-tab-starter';startTab.textContent='Starter Projects';
  startTab.setAttribute('role','tab');startTab.setAttribute('aria-controls','se170-pane-starter');
  startTab.onclick=()=>se170Select('starter');tabs.prepend(startTab);
 }
 let mine=hub.querySelector('#se170-pane-mine');
 if(!mine){
  if(se170Pane)mine=se170Pane;
  else {
   mine=document.createElement('div');mine.id='se170-pane-mine';
   mine.className='se170-hub-pane';mine.hidden=true;
   mine.setAttribute('role','tabpanel');
   mine.setAttribute('aria-labelledby','se170-tab-mine');
   se170Pane=mine;
  }
  starter.after(mine);
 }
 if(!se170Status||!se170Cards){
  const tools=document.createElement('div');tools.className='se170-my-tools';
  const refresh=document.createElement('button');refresh.type='button';
  refresh.textContent='Refresh';refresh.onclick=se170Refresh;
  const signIn=document.createElement('button');signIn.type='button';
  signIn.textContent='Open § Chat / Sign in';signIn.onclick=()=>{hub.classList.remove('show');openPanel();};
  tools.append(refresh,signIn);
  se170Status=document.createElement('p');se170Status.id='se170-library-status';
  se170Status.setAttribute('role','status');se170Status.setAttribute('aria-live','polite');
  se170Cards=document.createElement('div');se170Cards.className='se170-project-list';
  mine.append(tools,se170Status,se170Cards);
  se170Message('Connect your §wyrlz Chat account to browse saved projects.');
 }
 let mineTab=hub.querySelector('#se170-tab-mine');
 if(!mineTab){
  mineTab=document.createElement('button');mineTab.type='button';
  mineTab.id='se170-tab-mine';mineTab.textContent='My Projects';
  mineTab.setAttribute('role','tab');mineTab.setAttribute('aria-controls','se170-pane-mine');
  mineTab.onclick=()=>se170Select('mine');
  const tutorial=tabs.querySelector('#se412Tab');
  if(tutorial)tabs.insertBefore(mineTab,tutorial);else tabs.append(mineTab);
 }
 return true;
}
installLibrary=function se423InstallLibrary(){
 se423RepairNativeProjects();
 return se423PreviousInstallLibrary();
};
window.SWYRL_ENGINE_PROJECTS_RECOVERY_423=Object.freeze({
 inspect:()=>{const hub=document.getElementById('projectHub');
  const win=hub?.querySelector('.project-window');
  return {starterTab:!!hub?.querySelector('#se170-tab-starter'),
   mineTab:!!hub?.querySelector('#se170-tab-mine'),
   tutorialTab:!!hub?.querySelector('#se412Tab'),
   levels:!!document.getElementById('st141LevelBar'),
   scrollable:!!win&&win.scrollHeight>win.clientHeight,
   scrollTop:win?.scrollTop||0};
 },
 repair:()=>{schedule();return window.SWYRL_ENGINE_PROJECTS_RECOVERY_423.inspect();}
});
/* SE423_PROJECT_MENU_RECOVERY_END */