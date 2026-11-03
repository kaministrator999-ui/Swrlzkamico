// §E v11.246 — make the existing mobile Particle Studio bottom toggle truly collapse.
// v11.243's "Compact" action only resized the inspector; on a phone it is now
// the primary collapse/restore control. v11.245 still owns the state and aria.
// Do not rebuild emitters, the studio panel, or the WebGL test chamber.
(function(){
 'use strict';
 const wired=new WeakSet();
 const active=()=>document.body.dataset.se225Workspace==='particles';
 const panel=()=>document.getElementById('se223Panel');
 const compact=()=>document.getElementById('se243InspectorToggle');
 const properties=['height','max-height','min-height'];
 function clearSizing(p,scroll){
  for(const name of properties)p.style.removeProperty(name);
  scroll?.style.removeProperty('display');
 }
 function update(){
  const p=panel(),b=compact();
  if(b&&!wired.has(b)){
   // Capture before v11.243's click handler so Compact is not mistaken for Collapse.
   b.addEventListener('click',event=>{
    const current=panel();
    if(!active()||!current||current.hidden||!current.classList.contains('se225-docked'))return;
    event.preventDefault();event.stopImmediatePropagation();
    const controller=window.SWYRL_ENGINE_PARTICLE_COLLAPSE_245;
    if(document.body.dataset.se245ParticleCollapsed==='true')controller?.show?.();
    else controller?.collapse?.();
    update();
   },true);
   // Prevent parent draggable title from intercepting touch and pointer gestures.
   b.addEventListener('pointerdown',event=>event.stopPropagation());
   wired.add(b);
  }
  if(!p)return;
  const scroll=p.querySelector('.se223-scroll');
  const docked=active()&&!p.hidden&&p.classList.contains('se225-docked');
  const minimized=docked&&document.body.dataset.se245ParticleCollapsed==='true';
  if(minimized){
   // Inline !important beats older viewport-height rules in every mobile WebView.
   p.style.setProperty('height','59px','important');
   p.style.setProperty('max-height','59px','important');
   p.style.setProperty('min-height','0','important');
   scroll?.style.setProperty('display','none','important');
  }else clearSizing(p,scroll);
  if(b){
   b.textContent=minimized?'▴ Show controls':'▾ Collapse';
   b.setAttribute('aria-expanded',String(!minimized));
   b.setAttribute('aria-controls',scroll?.id||'se245ParticleSettings');
   b.setAttribute('aria-label',minimized?'Show Particle Studio controls':'Collapse Particle Studio controls');
   b.title=minimized?'Restore the settings panel':'Minimize the settings panel to the bottom bar';
  }
 }
 function boot(){
  update();
  const bodyObserver=new MutationObserver(update);
  bodyObserver.observe(document.body,{attributes:true,attributeFilter:[
   'data-se225-workspace','data-se245-particle-collapsed']});
  if(!compact()||!panel()){
   // Delayed studio installation; disconnect as soon as both elements exist.
   const installObserver=new MutationObserver(()=>{
    update();
    if(compact()&&panel())installObserver.disconnect();
   });
   installObserver.observe(document.body,{childList:true,subtree:true});
  }
  window.addEventListener('pagehide',()=>bodyObserver.disconnect(),{once:true});
 }
 window.SWYRL_ENGINE_PARTICLE_BOTTOM_TOGGLE_246=Object.freeze({
  sync:update,inspect:()=>({workspace:document.body.dataset.se225Workspace||null,
   minimized:document.body.dataset.se245ParticleCollapsed==='true',
   control:!!compact(),docked:!!panel()?.classList.contains('se225-docked')})
 });
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});
 else boot();
})();
