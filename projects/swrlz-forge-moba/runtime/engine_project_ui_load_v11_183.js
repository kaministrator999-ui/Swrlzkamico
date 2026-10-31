// §E v11.183: responsive levels workbench, honest project-load progress,
// lightweight in-memory cloud-list dedupe and native load time diagnostics.
// Never insert a new renderer, replace project storage or replay scene clicks.
const se183Loading={
 sequence:0,active:0,stage:'idle',label:'',start:0,elapsed:0,
 lastMs:0,lastName:'',lastOutcome:'',timer:null,hideTimer:null,node:null
};
function se183LoadNode(){
 if(se183Loading.node?.isConnected)return se183Loading.node;
 const el=document.createElement('div');
 el.id='se183LoadStatus';el.hidden=true;
 el.setAttribute('role','status');el.setAttribute('aria-live','polite');
 el.innerHTML='<span class="se183-spinner" aria-hidden="true"></span>'+
  '<span class="se183-load-copy"><strong id="se183LoadTitle">Opening project</strong>'+
  '<small id="se183LoadDetail"></small></span>';
 document.body.append(el);se183Loading.node=el;return el;
}
function se183LoadRender(){
 const state=se183Loading,node=se183LoadNode();
 node.querySelector('#se183LoadTitle').textContent=state.label;
 node.querySelector('#se183LoadDetail').textContent=
  state.active?(state.stage+' · '+(Math.round((performance.now()-state.start)/100)/10).toFixed(1)+'s elapsed'):
  state.stage;
 node.classList.toggle('se183-done',!state.active);
}
function se183StartLoad(label){
 if(se183Loading.active)return null;
 const state=se183Loading;
 clearTimeout(state.hideTimer);
 state.active=++state.sequence;state.start=performance.now();
 state.label=String(label||'Opening project').slice(0,100);
 state.stage='Preparing';state.elapsed=0;
 const node=se183LoadNode();node.hidden=false;node.classList.remove('se183-done');
 se183LoadRender();
 state.timer=setInterval(()=>{if(state.active)se183LoadRender();},360);
 return state.active;
}
function se183LoadStep(ticket,phase){
 if(!ticket||se183Loading.active!==ticket)return;
 se183Loading.stage=String(phase||'Working').slice(0,100);
 se183LoadRender();
}
function se183FinishLoad(ticket,ok,label){
 if(!ticket||se183Loading.active!==ticket)return;
 const s=se183Loading;
 clearInterval(s.timer);s.timer=null;
 s.lastMs=Math.round(performance.now()-s.start);
 s.lastName=s.label;s.lastOutcome=ok?'success':'failed';
 s.active=0;
 s.label=String(label||(ok?'Project ready':'Project could not be opened')).slice(0,100);
 s.stage=(ok?'Completed':'Not completed')+' · '+(s.lastMs/1000).toFixed(1)+'s';
 se183LoadRender();
 s.hideTimer=setTimeout(()=>{if(!s.active&&s.node)s.node.hidden=true;},ok?1350:3200);
}
function se183PaintNext(){
 // Yield two frames so Chromium/Quest can actually paint the busy state
 // before synchronous model/scene reconstruction. No fake percent complete.
 if(document.visibilityState==='hidden')return Promise.resolve();
 return new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
}
async function se183OpenStarter(template){
 if(se183Loading.active)return false;
 const hub=document.getElementById('projectHub');
 if(!hub?.classList.contains('show'))return false;
 const originalProject=currentProject,originalRevision=revision;
 const wasDirty=dirty;
 if(wasDirty&&!window.confirm('Create a new project and discard unsaved scene changes?'))return false;
 const choice=hub.querySelector('button[data-project-template="'+CSS.escape(template)+'"]');
 const title=choice?.querySelector('strong')?.textContent?.trim()||template||'starter';
 const ticket=se183StartLoad('Opening '+title);
 if(!ticket)return false;
 const cards=[...hub.querySelectorAll('button[data-project-template]')];
 for(const card of cards)card.disabled=true;
 let success=false;
 try{
  se183LoadStep(ticket,'Preparing workspace');
  await se183PaintNext();
  if(currentProject!==originalProject||revision!==originalRevision)
   throw Error('Workspace changed while preparing the project. Try again.');
  se183LoadStep(ticket,'Building 3D scene / fetching starter assets');
  await se183PaintNext();
  const result=await createProjectFromTemplate(template,true);
  success=result!==false;
  return success;
 }catch(error){
  console.error('§E starter open failed',error);
  toast('Could not open '+title+': '+String(error?.message||error).slice(0,120));
  return false;
 }finally{
  for(const card of cards)card.disabled=false;
  se183FinishLoad(ticket,success,success?'Opened '+title:'Could not open '+title);
 }
}
async function se183OpenLevel(id){
 if(se183Loading.active)return false;
 if(!seLevels.records.has(id)||id===seLevels.active)return false;
 const ticket=se183StartLoad('Switching project level');
 if(!ticket)return false;
 let ok=false;
 try{
  se183LoadStep(ticket,'Saving current level / rebuilding selected scene');
  await se183PaintNext();
  ok=!!seLevelsSwitch(id);return ok;
 }catch(error){
  console.error('§E level switch failed',error);
  toast('Could not open level: '+String(error?.message||error).slice(0,120));
  return false;
 }finally{
  se183FinishLoad(ticket,ok,ok?'Level ready':'Level switch failed');
 }
}
function se183InstallLevels(bar){
 if(!bar||bar.dataset.se183Panel==='1')return;
 bar.dataset.se183Panel='1';bar.classList.add('se183-level-panel','se183-level-compact');
 const toggle=document.createElement('button');
 toggle.id='se183LevelsToggle';toggle.type='button';toggle.className='se183-level-toggle';
 toggle.setAttribute('aria-controls','se183LevelsActions');toggle.setAttribute('aria-expanded','false');
 toggle.setAttribute('aria-label','Expand project level controls');
 const actions=document.createElement('div');
 actions.id='se183LevelsActions';actions.className='se183-level-actions';
 while(bar.firstChild)actions.append(bar.firstChild);
 bar.append(toggle,actions);
 const collapse=()=>{
  if(!bar.classList.contains('se183-expanded'))return;
  bar.classList.remove('se183-expanded');bar.classList.add('se183-level-compact');
  toggle.setAttribute('aria-expanded','false');
 };
 toggle.addEventListener('click',()=>{
  const expanding=!bar.classList.contains('se183-expanded');
  bar.classList.toggle('se183-expanded',expanding);
  bar.classList.toggle('se183-level-compact',!expanding);
  toggle.setAttribute('aria-expanded',String(expanding));
 });
 document.addEventListener('pointerdown',event=>{
  if(!bar.contains(event.target))collapse();
 },true);
 bar.addEventListener('keydown',event=>{
  if(event.key==='Escape'&&bar.classList.contains('se183-expanded')){
   collapse();toggle.focus();event.stopPropagation();
  }
 });
 const selector=actions.querySelector('#st141LevelSelect');
 if(selector)selector.onchange=event=>void se183OpenLevel(event.target.value);
 se183LevelsSync();
}
function se183LevelsSync(){
 const bar=seLevels.bar,toggle=bar?.querySelector('#se183LevelsToggle');
 if(!toggle)return;
 const name=String(seLevelsCurrent()?.name||'Project Levels').slice(0,70);
 toggle.textContent='☰ Levels · '+name;
 toggle.title='Project levels: '+name+' — expand for level editing';
}
const se183CloudCache={data:null,time:0,promise:null};
function se183CloudCacheClear(){
 se183CloudCache.data=null;se183CloudCache.time=0;se183CloudCache.promise=null;
}
async function se183CloudListCached(request,force=false){
 const now=performance.now();
 if(!force&&se183CloudCache.data&&now-se183CloudCache.time<12000)
  return se183CloudCache.data;
 if(!force&&se183CloudCache.promise)return se183CloudCache.promise;
 const job=Promise.resolve().then(request).then(data=>{
  if(job===se183CloudCache.promise){
   se183CloudCache.data=data;se183CloudCache.time=performance.now();
  }
  return data;
 }).finally(()=>{if(job===se183CloudCache.promise)se183CloudCache.promise=null;});
 se183CloudCache.promise=job;
 return job;
}
window.SWYRL_ENGINE_PROJECT_LOAD=Object.freeze({
 read:()=>({
  active:!!se183Loading.active,stage:se183Loading.stage,
  elapsedMs:se183Loading.active?Math.round(performance.now()-se183Loading.start):0,
  lastMs:se183Loading.lastMs,lastOutcome:se183Loading.lastOutcome,
  lastName:se183Loading.lastName,cloudListCached:!!se183CloudCache.data
 })
});
