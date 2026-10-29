// §E v11.128: one persistently selected starter to open on future launches.
// Selection only changes an independent preference, never writes project JSON,
// edits autosave, or overwrites the owner's authored project files.
const SE128_DEFAULT_KEY='swyrl.engine.defaultStarter.v1';
const se128StarterValues=new Set(
 [...document.querySelectorAll('#projectHub button[data-project-template]')]
 .map(button=>button.dataset.projectTemplate).filter(Boolean));
function se128ReadDefault(){
 try{
  const saved=localStorage.getItem(SE128_DEFAULT_KEY);
  return se128StarterValues.has(saved)?saved:null;
 }catch{return null;}
}
function se128SetDefault(template){
 if(template!==null&&!se128StarterValues.has(template))return false;
 try{
  if(template===null)localStorage.removeItem(SE128_DEFAULT_KEY);
  else localStorage.setItem(SE128_DEFAULT_KEY,template);
 }catch{
  toast('Browser storage unavailable. Default was not changed.');
  se128SyncChoices();
  return false;
 }
 se128SyncChoices();
 if(window.SWRLZ_FORGE_BUILD)window.SWRLZ_FORGE_BUILD.defaultProject=template||'glitch-dragons-den';
 return true;
}
function se128SyncChoices(){
 const active=se128ReadDefault();
 for(const input of document.querySelectorAll('#projectHub input[data-se128-default]')){
  input.checked=input.dataset.se128Default===active;
  const label=input.closest('label');
  label?.classList.toggle('se128-selected-default',input.checked);
 }
}
function se128InstallStarterChoices(){
 const cards=[...document.querySelectorAll('#projectHub button[data-project-template]')];
 for(const card of cards){
  if(card.closest('.se128-starter-choice'))continue;
  const id=card.dataset.projectTemplate;
  if(!se128StarterValues.has(id))continue;
  const wrapper=document.createElement('div');
  wrapper.className='se128-starter-choice';
  const label=document.createElement('label');
  label.className='se128-default-checkbox';
  const checkbox=document.createElement('input');
  checkbox.type='checkbox';checkbox.dataset.se128Default=id;
  const title=card.querySelector('strong')?.textContent?.trim()||id;
  checkbox.setAttribute('aria-label','Set '+title+' as startup project');
  const text=document.createElement('span');text.textContent='Load this project by default';
  label.append(checkbox,text);
  card.replaceWith(wrapper);wrapper.append(card,label);
  // A checkbox is a sibling, never an interactive descendant of a button.
  label.addEventListener('click',event=>event.stopPropagation());
  checkbox.addEventListener('change',()=>{
   const next=checkbox.checked?id:null;
   const ok=se128SetDefault(next);
   if(ok)toast(next?title+' will open when §E starts.':'Automatic starter cleared.');
  });
 }
 se128SyncChoices();
}
se128InstallStarterChoices();
// A user-supplied ?project= link always overrides the remembered preference,
// but never silently rewrites that preference.
function se128LaunchStartupProject(){
 const query=new URLSearchParams(location.search).get('project');
 // Explicit URL routes always win, including specialist Model Atelier loaders.
 // Do not invoke a second model load for ?project=sheep-model/wolf-model.
 if(query!==null){
  if(query==='starforge-observatory'){loadCanonicalStarforge();return;}
  if(query==='anime-ghosts-ep01'){loadCanonicalAnimeEpisode();return;}
  if(query==='sheep-tag-meadow'){stLoadStarter();return;}
  if(query==='maul-frostveil'){maulLoadStarter();return;}
  loadCanonicalGlitchDen();return;
 }
 const requested=se128ReadDefault();
 window.se128StartupPending=true;
 // The original default is Dragon Den; preserve it if preference is unset.
 if(!requested||requested==='glitch-dragons-den'){
  loadCanonicalGlitchDen();window.se128StartupPending=false;return;
 }
 if(requested==='starforge-observatory'){
  loadCanonicalStarforge();window.se128StartupPending=false;return;
 }
 if(requested==='anime-ghosts-ep01'){
  loadCanonicalAnimeEpisode();window.se128StartupPending=false;return;
 }
 if(requested==='sheep-tag-meadow'){
  stLoadStarter();window.se128StartupPending=false;return;
 }
 if(requested==='maul-frostveil'){
  maulLoadStarter();window.se128StartupPending=false;return;
 }
 // Other card types have their own Model Atelier/starter bootstrap. The
 // native template router runs after those panels/installers are initialized.
 loadCanonicalGlitchDen();
 queueMicrotask(()=>{
  try{
   const result=createProjectFromTemplate(requested,true);
   Promise.resolve(result).then(ok=>{
    if(ok===false)toast('Starter could not load. Open it again from Projects.');
   }).catch(error=>{console.error(error);toast('Default starter failed to load.');})
    .finally(()=>{window.se128StartupPending=false;});
  }catch(error){
   window.se128StartupPending=false;
   console.error(error);
   toast('Default starter failed to load.');
  }
 });
}
