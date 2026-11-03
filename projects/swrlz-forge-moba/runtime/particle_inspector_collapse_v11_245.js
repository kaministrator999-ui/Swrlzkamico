// §E v11.245 — actually minimize the mobile Particle Studio inspector.
// Three distinct states: expanded (v11.243), compact, and header-only collapse.
// No project, emitter, studio selection, or renderer data is changed.
(function(){
  'use strict';
  const state={toggle:null,scroll:null,collapsed:false,transitions:0};
  const active=()=>document.body.dataset.se225Workspace==='particles';
  const button=()=>document.getElementById('se245ParticleCollapse');
  function setCollapsed(value){
    if(!active())return false;
    const panel=document.getElementById('se223Panel');
    if(!panel||panel.hidden||!panel.classList.contains('se225-docked'))return false;
    const collapsed=!!value;
    state.collapsed=collapsed;
    if(collapsed)document.body.dataset.se245ParticleCollapsed='true';
    else delete document.body.dataset.se245ParticleCollapsed;
    const scroll=state.scroll||panel.querySelector('.se223-scroll');
    if(scroll){
      scroll.inert=collapsed;
      if(collapsed)scroll.setAttribute('aria-hidden','true');
      else scroll.removeAttribute('aria-hidden');
    }
    const control=button();
    if(control){
      control.textContent=collapsed?'▴ Show controls':'▾ Collapse';
      control.setAttribute('aria-expanded',String(!collapsed));
      control.setAttribute('aria-label',collapsed?'Show Particle Studio controls':'Collapse Particle Studio controls');
      control.title=collapsed?'Restore Particle Studio controls':'Minimize controls to the bottom bar';
    }
    state.transitions++;
    return true;
  }
  function reset(){
    state.collapsed=false;
    delete document.body.dataset.se245ParticleCollapsed;
    const scroll=state.scroll||document.getElementById('se223Panel')?.querySelector('.se223-scroll');
    if(scroll){scroll.inert=false;scroll.removeAttribute('aria-hidden');}
    const control=button();
    if(control){
      control.textContent='▾ Collapse';
      control.setAttribute('aria-expanded','true');
      control.setAttribute('aria-label','Collapse Particle Studio controls');
    }
  }
  function install(){
    const panel=document.getElementById('se223Panel');
    const heading=panel?.querySelector('.se223-title');
    const scroll=panel?.querySelector('.se223-scroll');
    if(!heading||!scroll)return false;
    if(button())return true;
    scroll.id=scroll.id||'se245ParticleSettings';
    const control=document.createElement('button');
    control.id='se245ParticleCollapse';control.type='button';
    control.textContent='▾ Collapse';
    control.setAttribute('aria-controls',scroll.id);
    control.setAttribute('aria-expanded','true');
    control.setAttribute('aria-label','Collapse Particle Studio controls');
    control.title='Minimize controls to the bottom bar';
    control.addEventListener('click',event=>{
      event.stopPropagation();
      setCollapsed(!state.collapsed);
    });
    // The original panel has pointer-driven draggable chrome. Our button
    // must remain an ordinary touch target, never initiate a panel drag.
    control.addEventListener('pointerdown',event=>event.stopPropagation());
    heading.insertBefore(control,heading.querySelector('#se223Close'));
    state.toggle=control;state.scroll=scroll;
    return true;
  }
  function boot(){
    if(install())return;
    // Studio panel is assembled asynchronously; observe only until it appears.
    const observer=new MutationObserver(()=>{
      if(install())observer.disconnect();
    });
    observer.observe(document.body,{childList:true,subtree:true});
  }
  window.SWYRL_ENGINE_PARTICLE_COLLAPSE_245=Object.freeze({
    collapse:()=>setCollapsed(true),
    show:()=>setCollapsed(false),
    reset,
    inspect:()=>({collapsed:state.collapsed,transitions:state.transitions,
      installed:!!button(),workspace:document.body.dataset.se225Workspace||null})
  });
  if(document.readyState==='loading')
    document.addEventListener('DOMContentLoaded',boot,{once:true});
  else boot();
})();
