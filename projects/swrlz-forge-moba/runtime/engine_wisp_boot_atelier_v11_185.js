// §E v11.185 — lightweight startup fragments/wisps and native Atelier header toggle.
// Decorative effects never create a renderer, download an asset or delay boot.
(function se185BootVisual(){
 function mount(){
  if(document.getElementById('se185Init'))return;
  const splash=document.createElement('div');
  splash.id='se185Init';splash.className='se185-init';
  splash.setAttribute('role','status');splash.setAttribute('aria-label','§E is initializing');
  splash.innerHTML='<div class="se185-halo" aria-hidden="true"><span class="se185-ring se185-ring-a"></span><span class="se185-ring se185-ring-b"></span><span class="se185-core" data-ghost="§E">§E</span><span class="se185-wisp se185-wisp-a"></span><span class="se185-wisp se185-wisp-b"></span><span class="se185-wisp se185-wisp-c"></span><div class="se185-particles"></div></div><div class="se185-boot-copy"><strong>§wyrl§ ENGINE</strong><span class="se185-boot-sub">GLITCH · WISP · INITIALIZATION</span><span id="se185BootStage" class="se185-boot-stage" aria-live="polite">Preparing your workspace</span></div><span class="se185-boot-track" aria-hidden="true"></span>';
  const particles=splash.querySelector('.se185-particles');
  const fragment=document.createDocumentFragment();
  for(let i=0;i<32;i++){
   const node=document.createElement('i');
   const angle=(i*137.508)%360;
   const radius=48+(i*29)%130;
   node.style.setProperty('--se185-angle',angle+'deg');
   node.style.setProperty('--se185-radius-out',(radius*1.3)+'px');
   node.style.setProperty('--se185-delay',(-((i*17)%31)/10)+'s');
   node.style.setProperty('--se185-speed',(2.6+((i*7)%11)/10)+'s');
   fragment.append(node);
  }
  particles.append(fragment);
  document.body.append(splash);
  const stage=splash.querySelector('#se185BootStage');
  const update=()=>{
   if(document.documentElement.classList.contains('se127-editor-ready')){
    stage.textContent='Workspace ready';
    clearInterval(loop);
    return;
   }
   if(window.se128StartupPending){stage.textContent='Restoring selected project';return;}
   if(document.readyState!=='complete'){stage.textContent='Loading engine interface';return;}
   if(document.getElementById('mainToolbar')||document.querySelector('.app>.topbar')){
    stage.textContent='Synchronizing scene and tools';return;
   }
   stage.textContent='Preparing your workspace';
  };
  const loop=setInterval(update,350);
  update();
  setTimeout(()=>clearInterval(loop),16000);
 }
 if(document.body)mount();else document.addEventListener('DOMContentLoaded',mount,{once:true});
})();
function se185InstallAtelierToggle(panel){
 if(!panel||panel.querySelector('#se185AtelierTopToggle'))return;
 const header=panel.querySelector('.atelier-head');
 const actions=header?.querySelector('.atelier-actions');
 const controls=panel.querySelector('#modelAtelierViewportModes');
 if(!header||!actions||!controls)return;
 const toggle=document.createElement('button');
 toggle.type='button';toggle.id='se185AtelierTopToggle';
 toggle.setAttribute('aria-controls','modelAtelierViewportModes');
 toggle.setAttribute('title','Show or hide rendering, view and reference settings');
 const key='swrlz-atelier-top-settings-open-v1';
 let saved=null;
 try{saved=localStorage.getItem(key)}catch(_){}
 const defaultOpen=!window.matchMedia('(max-width:700px), (pointer:coarse)').matches;
 let open=saved===null?defaultOpen:saved==='1';
 const apply=()=>{
  panel.classList.toggle('se185-top-collapsed',!open);
  toggle.setAttribute('aria-expanded',String(open));
  toggle.textContent=open?'Settings ▴':'Settings ▾';
  toggle.setAttribute('aria-label',open?'Collapse modeling top settings':'Expand modeling top settings');
  controls.setAttribute('aria-hidden',String(!open));
  // Native menu nodes stay mounted and their handlers remain attached.
  if(!open)for(const details of controls.querySelectorAll('details[open]'))details.open=false;
 };
 toggle.addEventListener('click',()=>{
  open=!open;
  try{localStorage.setItem(key,open?'1':'0')}catch(_){}
  apply();
 });
 actions.insertBefore(toggle,actions.firstChild);
 apply();
 window.SWYRL_ATELIER_TOP_SETTINGS=Object.freeze({
  read:()=>({expanded:open,installed:toggle.isConnected})
 });
}
