/* SE529_MY_PROJECTS_BROWSER_UI_START */
// Refactor the existing (not duplicated) My Projects DOM into one command bar,
// two clear project collections, and per-card advanced actions. All legacy
// selectors and event listeners remain attached to their original nodes.
const se529PriorProjectCard=se184ProjectCard;
se184ProjectCard=function(...args){
 const card=se529PriorProjectCard.apply(this,args);
 if(!card||card.querySelector('.se529-card-more'))return card;
 const actions=card.querySelector('.se184-card-actions');
 if(actions){
  const existing=[...actions.children].filter(el=>el.tagName==='BUTTON');
  const advanced=existing.slice(2);
  if(advanced.length){
   const details=document.createElement('details');details.className='se529-card-more';
   const summary=document.createElement('summary');summary.textContent='More actions';
   const inner=document.createElement('div');inner.className='se529-card-more-actions';
   for(const control of advanced)inner.append(control); // preserve native handlers
   details.append(summary,inner);actions.after(details);
  }
 }
 return card;
};
const se529PriorInstallAccount=se528InstallAccountSave;
// Stop the older dynamic installer from adding project-save buttons to
// whichever .se170-my-tools container happens to be first after reorder.
se528InstallAccountSave=function(){
 const chat=document.getElementById('seChatSave');
 if(chat){chat.onclick=()=>void se529SaveNativeProjectToAccount();
  chat.dataset.se528SaveBound='true';}
};
let se529LibraryPolishing=false;
function se529Button(text,kind,id,fn){
 const button=document.createElement('button');button.type='button';
 button.id=id;button.className='se529-command '+(kind||'');
 button.textContent=text;button.addEventListener('click',fn);
 return button;
}
async function se529SaveDeviceOnly(){
 const button=document.getElementById('se529SaveLocal');
 if(button)button.disabled=true;
 try{
  if(se175Transition||se175LocalLoading||cloudBusy||playing||simulating)
   throw Error('Another editor operation is active. Stop it before saving.');
  if(se175Saving)await se175Saving;
  if(!se371HasSavedIdentity())await se371Clone(se371NewName(se371ProjectName()));
  else await se371SaveLocal();
  const note='Saved on this device · '+se371ProjectName()+'.';
  se371Display(note);await se175RefreshLocal();
 }catch(error){se371Display('Device save failed: '+String(error.message||error),true);}
 finally{if(button)button.disabled=false;se529PolishLibrary();}
}
async function se529RefreshLibrary(){
 const button=document.getElementById('se529Refresh');
 if(button)button.disabled=true;
 try{
  await se175RefreshLocal();
  await se170Refresh();
 }finally{if(button)button.disabled=false;se529PolishLibrary();}
}
function se529PolishLibrary(){
 if(se529LibraryPolishing)return;
 const pane=document.getElementById('se170-pane-mine');
 if(!pane)return;
 se529LibraryPolishing=true;
 try{
  let shell=document.getElementById('se529LibraryHero');
  if(!shell){
   shell=document.createElement('section');
   shell.id='se529LibraryHero';
   shell.setAttribute('aria-label','My Projects actions');
   const head=document.createElement('div');head.className='se529-library-heading';
   const caption=document.createElement('div');
   const title=document.createElement('h2');title.textContent='Your projects';
   const sub=document.createElement('p');sub.id='se529CurrentProject';
   caption.append(title,sub);
   const connect=document.createElement('button');
   connect.id='se529AccountConnect';connect.type='button';
   connect.className='se529-connect';connect.onclick=()=>{
    document.getElementById('projectHub')?.classList.remove('show');
    openPanel();
   };
   head.append(caption,connect);
   const controls=document.createElement('div');controls.className='se529-commandbar';
   controls.append(
    se529Button('Save to account','primary','se529SaveAccount',
     ()=>void se529SaveNativeProjectToAccount().then(se529PolishLibrary)),
    se529Button('Save on device','','se529SaveLocal',()=>void se529SaveDeviceOnly()),
    se529Button('Refresh','','se529Refresh',()=>void se529RefreshLibrary())
   );
   const advanced=document.createElement('details');advanced.id='se529Advanced';
   const summary=document.createElement('summary');summary.textContent='More project tools';
   const items=document.createElement('div');items.className='se529-advanced-contents';
   advanced.append(summary,items);
   const state=document.createElement('p');state.id='se529AccountFeedback';
   state.setAttribute('role','status');state.setAttribute('aria-live','polite');
   shell.append(head,controls,advanced,state);
   pane.prepend(shell);
  }
  const local=document.getElementById('se175LocalProjects');
  let gallery=document.getElementById('se184LocalCards');
  // Force the existing native local-card gallery to be created beside its
  // original section BEFORE moving the control section under Advanced.
  if(local&&!gallery&&typeof se184InstallLocalGallery==='function'){
   gallery=se184InstallLocalGallery();
  }
  const advancedBody=shell.querySelector('.se529-advanced-contents');
  if(local&&local.parentElement!==advancedBody)advancedBody.append(local);
  const legacyTools=[...pane.children].find(el=>el!==shell&&el.classList.contains('se170-my-tools'));
  if(legacyTools&&legacyTools.parentElement!==advancedBody)advancedBody.append(legacyTools);
  // Keep legacy controls for native events, but do not present redundant
  // Refresh / Sign in / Save Project / Save to Account buttons.
  advancedBody.querySelectorAll('button').forEach(button=>{
   const val=button.textContent?.trim()||'';
   if(/^(?:refresh(?: local projects)?|open § chat \/ sign in|save project|save(?: active project)? to account)$/i.test(val)){
    button.hidden=true;button.setAttribute('aria-hidden','true');button.tabIndex=-1;
   }
  });
  if(gallery){
   if(gallery.parentElement!==pane)pane.append(gallery);
   let heading=document.getElementById('se529LocalHeading');
   if(!heading){heading=document.createElement('h3');
    heading.id='se529LocalHeading';heading.className='se529-group-heading';}
   heading.textContent='On this device';
   pane.insertBefore(heading,gallery);
  }
  const cloudList=se170Cards;
  if(cloudList){
   let heading=document.getElementById('se529CloudHeading');
   if(!heading){heading=document.createElement('h3');
    heading.id='se529CloudHeading';heading.className='se529-group-heading';}
   heading.textContent='Saved to account';
   pane.insertBefore(heading,cloudList);
   if(se170Status&&se170Status.nextSibling!==cloudList)
    pane.insertBefore(se170Status,cloudList);
  }
  const oldCloudHeading=document.getElementById('se184CloudHeading');
  if(oldCloudHeading)oldCloudHeading.hidden=true;
  const active=se371ProjectName();
  const projectCaption=document.getElementById('se529CurrentProject');
  if(projectCaption)projectCaption.textContent='Editing now: '+active;
  const connected=!!(ready&&se176AccountConnected);
  const connect=document.getElementById('se529AccountConnect');
  if(connect){
   connect.textContent=connected?'Account connected':'Connect §Chat';
   connect.classList.toggle('connected',connected);
   connect.title=connected?'Open your connected §Chat account':'Sign in to your §Chat account';
  }
  const command=document.getElementById('se529SaveAccount');
  if(command){
   command.disabled=!connected||se529ProjectSaveBusy||cloudBusy;
   command.title=connected?'Save the full active project and its revision to your account':
    'Connect your account to enable project saving';
  }
  const localCount=gallery?.children.length||0,cloudCount=cloudList?.children.length||0;
  const state=document.getElementById('se529AccountFeedback');
  if(state){
   const outcome=se529ProjectSaveResult;
   if(outcome?.ok===true){
    state.textContent='Account save confirmed · Revision '+outcome.revision+'.';
    state.dataset.state='success';
   }else if(outcome){
    state.textContent='Account save not completed · '+String(outcome.detail||outcome.error).slice(0,180);
    state.dataset.state='error';
   }else{
    state.textContent=localCount+' on this device · '+cloudCount+' in account';
    state.dataset.state='neutral';
   }
  }
  const h1=document.getElementById('se529LocalHeading');
  const h2=document.getElementById('se529CloudHeading');
  if(h1)h1.textContent='On this device · '+localCount;
  if(h2)h2.textContent='Saved to account · '+cloudCount;
 }finally{se529LibraryPolishing=false;}
}
const se529PriorLocalRender=se184RenderLocalProjects;
se184RenderLocalProjects=function(...args){
 const out=se529PriorLocalRender.apply(this,args);
 queueMicrotask(se529PolishLibrary);return out;
};
const se529PriorCloudRender=se184RenderCloudProjects;
se184RenderCloudProjects=function(...args){
 const out=se529PriorCloudRender.apply(this,args);
 queueMicrotask(se529PolishLibrary);return out;
};
const se529PriorSelectLibrary=se170Select;
se170Select=function(...args){
 const out=se529PriorSelectLibrary.apply(this,args);
 if(args[0]==='mine')queueMicrotask(se529PolishLibrary);
 return out;
};
if(document.readyState==='loading')
 document.addEventListener('DOMContentLoaded',()=>queueMicrotask(se529PolishLibrary),{once:true});
else queueMicrotask(se529PolishLibrary);
document.addEventListener('click',()=>requestAnimationFrame(se529PolishLibrary),true);
window.addEventListener('swrlz:account-save-result',se529PolishLibrary);
window.addEventListener('swrlz:project-loaded',()=>queueMicrotask(se529PolishLibrary));
window.SWYRL_ENGINE_MY_PROJECTS_529=Object.freeze({
 refresh:se529RefreshLibrary,saveToDevice:se529SaveDeviceOnly,
 inspect:()=>({polished:!!document.getElementById('se529LibraryHero'),
  duplicatesHidden:document.querySelectorAll('#se529Advanced button[hidden]').length})
});
/* SE529_MY_PROJECTS_BROWSER_UI_END */