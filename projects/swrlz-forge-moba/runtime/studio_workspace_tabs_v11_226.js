// §E v11.226: four first-class workspaces, one native scene/WebGL renderer.
// Game Engine and Modeling remain the unchanged native workspaces. Particle and
// Material Studios are full-screen workspaces with game scene as 3D preview.
const se225Studios={active:null,shell:null};
const SE225_STUDIO_TABS=[
 ['game','Game Engine'],['modeler','Modeling'],
 ['particles','Particle Studio'],['materials','Materials & Textures']
];
function se225UpdateTabs(){
 const current=se225Studios.active||window.SWYRL_ENGINE_WORKSPACES?.active?.()||'game';
 for(const nav of document.querySelectorAll('.se187-workspace-tabs,.se225-studio-tabs')){
  for(const [id] of SE225_STUDIO_TABS){
   const b=nav.querySelector('[data-se187-tab="'+id+'"],[data-se225-tab="'+id+'"]');
   if(!b)continue;
   const on=id===current;
   b.classList.toggle('active',on);
   b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1;
  }
 }
}
function se225DecorateNativeTabs(nav){
 if(!nav||nav.dataset.se225Enhanced==='1')return;
 nav.dataset.se225Enhanced='1';
 for(const [id,label] of SE225_STUDIO_TABS.slice(2)){
  const b=document.createElement('button');b.type='button';b.dataset.se225Tab=id;
  b.textContent=label;b.setAttribute('role','tab');
  b.setAttribute('aria-label','Switch to '+label+' workspace');
  b.addEventListener('click',()=>se225Open(id));
  const before=nav.querySelector('.se187-draft-state');
  if(before)nav.insertBefore(b,before);else nav.append(b);
 }
 // The historical keyboard handler only knew two native tabs. Capture all
 // arrows against all four buttons while keeping the native click handlers.
 nav.addEventListener('keydown',event=>{
  if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
  const buttons=[...nav.querySelectorAll('[role="tab"]')];
  const current=buttons.indexOf(document.activeElement);
  if(current<0)return;
  const next=event.key==='Home'?0:event.key==='End'?buttons.length-1:
   (current+(event.key==='ArrowRight'?1:-1)+buttons.length)%buttons.length;
  event.preventDefault();event.stopImmediatePropagation();
  buttons[next].click();buttons[next].focus();
 },true);
 // Native Game/Modeling buttons keep the native actions; close our studio
 // first without intercepting or creating a second workspace controller.
 nav.addEventListener('click',event=>{
  const b=event.target.closest('[data-se187-tab]');
  if(b)se225Hide(true);
 },true);
}
function se225Native(mode){
 se225Hide(true);
 const native=window.SWYRL_ENGINE_WORKSPACES;
 if(native?.change)native.change(mode);
 se225UpdateTabs();
 return true;
}
function se225Hide(clearRoute=false){
 if(se225Studios.active==='particles'){
  const panel=document.getElementById('se223Panel');
  if(panel){panel.hidden=true;panel.classList.remove('se225-docked');
   panel.style.left='';panel.style.right='';panel.style.top='';panel.style.bottom='';}
  se223State.panel=false;
  if(!playing&&!simulating)se223State.preview=false;
 }
 se225Studios.active=null;
 delete document.body.dataset.se225Workspace;
 if(se225Studios.shell)se225Studios.shell.hidden=true;
 document.getElementById('se225MaterialsPanel')?.setAttribute('hidden','');
 if(clearRoute&&/^#studio-(particles|materials)$/.test(location.hash)){
  const url=new URL(location.href);url.hash='';
  window.history.replaceState({se225Workspace:'game'},'',url.pathname);
 }
 se225UpdateTabs();
}
function se225Open(mode,push=true){
 if(!['particles','materials'].includes(mode))return false;
 if(!se225Studios.shell)se225Install();
 const native=window.SWYRL_ENGINE_WORKSPACES;
 if(native?.change && native.active()!=='game')native.change('game');
 const previous=se225Studios.active;
 if(previous&&previous!==mode)se225Hide(false);
 const shell=se225Studios.shell;if(!shell)return false;
 se225Studios.active=mode;
 shell.hidden=false;document.body.dataset.se225Workspace=mode;
 const isParticles=mode==='particles';
 shell.querySelector('#se225Title').textContent=isParticles?'✦ Particle Studio':'🎨 Material & Texture Studio';
 shell.querySelector('#se225Subtitle').textContent=isParticles?
  '3D emitter creator · project VFX library · live scene preview':
  'Procedural textures · paint · physically based materials · live scene preview';
 shell.querySelector('#se225ViewNote').textContent=isParticles?
  'Emitter particles render into this native game viewport. Move the scene camera to inspect the result.':
  'Your material preview sphere appears on the right. Assign a material to an actor to see the scene update.';
 const material=document.getElementById('se225MaterialsPanel');
 if(material){material.hidden=isParticles;if(!isParticles)se225MaterialUIRefresh();}
 if(isParticles){
  if(typeof se223Install==='function')se223Install();
  const panel=document.getElementById('se223Panel');
  if(panel){
   panel.hidden=false;panel.classList.add('se225-docked');panel.style.left='';panel.style.right='';
   panel.style.top='';panel.style.bottom='';
   se223State.panel=true;se223State.preview=true;se223UIRefresh();
  }
 }
 // Separate tab routes use a local hash to avoid requesting non-existent
 // static HTML pages. Shared game scene/project never reloads on tab switch.
 if(push){
  const url=new URL('index.html',location.href);url.hash='studio-'+mode;
  if(location.pathname!==url.pathname||location.hash!==url.hash)
   try{window.history.pushState({se225Workspace:mode},'',url.pathname+url.hash);}
   catch(error){console.warn('§E Studio routing',error);}
 }
 se225UpdateTabs();return true;
}
function se225StudioTabs(){
 const nav=document.createElement('nav');nav.className='se225-studio-tabs';
 nav.setAttribute('role','tablist');nav.setAttribute('aria-label','§E workspace tabs');
 for(const [id,label] of SE225_STUDIO_TABS){
  const b=document.createElement('button');b.type='button';b.dataset.se225Tab=id;
  b.setAttribute('role','tab');b.textContent=label;
  b.addEventListener('click',()=>id==='game'||id==='modeler'?se225Native(id):se225Open(id));
  nav.append(b);
 }
 nav.addEventListener('keydown',event=>{
  if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
  const tabs=[...nav.querySelectorAll('button[role=tab]')],i=tabs.indexOf(document.activeElement);
  if(i<0)return;
  const next=event.key==='Home'?0:event.key==='End'?tabs.length-1:
   (i+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
  event.preventDefault();tabs[next].click();tabs[next].focus();
 });
 return nav;
}
function se225Install(){
 if(se225Studios.shell?.isConnected)return;
 const shell=document.createElement('div');shell.id='se225Shell';
 shell.className='se225-shell';shell.hidden=true;
 const header=document.createElement('header');header.className='se225-workspace-header';
 header.append(se225StudioTabs());
 const label=document.createElement('div');label.className='se225-workspace-heading';
 label.innerHTML='<strong id="se225Title">Particle Studio</strong><span id="se225Subtitle"></span>';
 header.append(label);shell.append(header);
 const note=document.createElement('div');note.className='se225-view-note';note.id='se225ViewNote';
 shell.append(note);
 document.body.append(shell);se225Studios.shell=shell;
 if(typeof se225MaterialUIInstall==='function')se225MaterialUIInstall(shell);
 const legacyClose=document.getElementById('se223Close');
 if(legacyClose)legacyClose.addEventListener('click',e=>{
  if(se225Studios.active!=='particles')return;
  e.preventDefault();e.stopImmediatePropagation();se225Native('game');
 },true);
 se225UpdateTabs();
}
window.SWYRL_ENGINE_STUDIOS=Object.freeze({
 active:()=>se225Studios.active||window.SWYRL_ENGINE_WORKSPACES?.active?.()||'game',
 open:se225Open,change:mode=>mode==='game'||mode==='modeler'?se225Native(mode):se225Open(mode),
 inspect:()=>({active:se225Studios.active||null,native:window.SWYRL_ENGINE_WORKSPACES?.active?.()||null,
  route:location.pathname+location.hash,materialCount:window.SWYRL_ENGINE_MATERIALS?.inspect?.().materials??0,
  particleCount:window.SWYRL_ENGINE_PARTICLES?.inspect?.().emitters??0})
});
function se225Boot(){
 se225Install();
 const match=location.hash.match(/^#studio-(particles|materials)$/);
 if(match)se225Open(match[1],false);
}
// Native router's popstate handler is registered first; after it returns,
// restore the selected studio hash without changing the underlying scene.
window.addEventListener('popstate',()=>{
 const match=location.hash.match(/^#studio-(particles|materials)$/);
 if(match)se225Open(match[1],false);
 else{se225Hide(false);se225UpdateTabs();}
});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(se225Boot,0),{once:true});
else setTimeout(se225Boot,0);
