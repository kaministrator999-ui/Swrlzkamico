// §E v11.242 · UI-only mobile inspector: project and native VFX remain unchanged.
(function(){
  function install(){
    const panel=document.getElementById('se223Panel');
    if(!panel||document.getElementById('se242InspectorToggle'))return;
    const header=panel.querySelector('.se223-title');
    if(!header)return;
    const toggle=document.createElement('button');
    toggle.type='button';toggle.id='se242InspectorToggle';
    toggle.textContent='↕ Expand';toggle.setAttribute('aria-label','Expand particle controls');
    toggle.setAttribute('aria-expanded','false');
    toggle.addEventListener('click',()=>{
      const expanded=document.body.dataset.se242InspectorOpen!=='true';
      if(expanded)document.body.dataset.se242InspectorOpen='true';
      else delete document.body.dataset.se242InspectorOpen;
      toggle.textContent=expanded?'↕ Compact':'↕ Expand';
      toggle.setAttribute('aria-expanded',String(expanded));
      toggle.setAttribute('aria-label',expanded?'Compact particle controls':'Expand particle controls');
    });
    header.insertBefore(toggle,panel.querySelector('#se223Close'));
  }
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',()=>{install();setTimeout(install,100);},{once:true});
  }else{install();setTimeout(install,100);}
})();
