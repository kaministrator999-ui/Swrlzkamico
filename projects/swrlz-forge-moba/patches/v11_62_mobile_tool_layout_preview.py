"""§E v11.62 preview: responsive single-surface mobile tool management.

Additive source patch atop v11.61. No native mesh or tool operations are replaced.
"""
CSS=r"""
/* Narrow phone: a single tool surface, not two competing popups. */
@media(max-width:700px),(pointer:coarse) and (max-width:900px){
 .model-atelier.atelier-tools-docked.atelier-mobile-tools .atelier-inspector{
   display:none!important;
 }
 .model-atelier.atelier-tools-docked.atelier-mobile-tools:not(.atelier-context-active) .atelier-scene{
   min-height:55dvh!important;
 }
 .model-atelier.atelier-mobile-tools .atelier-context-workbench{
   left:0!important;right:0!important;bottom:env(safe-area-inset-bottom,0px)!important;
   top:auto!important;width:100vw!important;
   height:min(45dvh,420px)!important;max-height:calc(100dvh - 130px)!important;
   border-radius:15px 15px 0 0!important;
   border-left:0;border-right:0;
   box-shadow:0 -12px 40px #000a;
 }
 .model-atelier.atelier-mobile-tools.atelier-mobile-expanded .atelier-context-workbench{
   height:min(74dvh,740px)!important;max-height:calc(100dvh - 90px)!important;
 }
 .model-atelier.atelier-mobile-tools.atelier-mobile-collapsed .atelier-context-workbench{
   height:54px!important;
 }
 .model-atelier.atelier-mobile-tools.atelier-mobile-collapsed .atelier-context-title,
 .model-atelier.atelier-mobile-tools.atelier-mobile-collapsed .atelier-context-body{
   display:none!important;
 }
 .model-atelier.atelier-mobile-tools .atelier-context-header{
   min-height:50px!important;touch-action:manipulation;
 }
 .model-atelier.atelier-mobile-tools .atelier-context-body{
   display:flex!important;flex-direction:column;gap:0;
 }
 .model-atelier.atelier-mobile-tools .atelier-context-left{
   min-height:0!important;flex:0 0 auto;max-height:38%;border-right:0;
   border-bottom:1px solid #456b90;
 }
 .model-atelier.atelier-mobile-tools .atelier-context-left label{display:none}
 .model-atelier.atelier-mobile-tools #atelierContextFind{margin-bottom:5px;min-height:44px;font-size:16px}
 .model-atelier.atelier-mobile-tools #atelierContextOperations{
   flex-direction:row!important;overflow-x:auto;overscroll-behavior-x:contain;
   flex-wrap:nowrap;padding-bottom:3px;scrollbar-width:thin;
 }
 .model-atelier.atelier-mobile-tools .atelier-context-op{
   flex:0 0 auto;width:auto;max-width:170px;min-height:44px!important;
   padding:8px 12px;font-size:13px!important;text-align:center;
 }
 .model-atelier.atelier-mobile-tools .atelier-context-right{
   flex:1 1 auto;min-height:0;padding:9px 13px;
 }
 .model-atelier.atelier-mobile-tools #atelierContextFields{
   display:grid;grid-template-columns:1fr;gap:12px;
 }
 .model-atelier.atelier-mobile-tools .atelier-context-field :is(input,select,textarea,button),
 .model-atelier.atelier-mobile-tools .atelier-context-preset button{
   min-height:44px;font-size:16px;
 }
 .model-atelier.atelier-mobile-tools .atelier-tool-rail{
   top:auto!important;right:5px!important;bottom:calc(50px + env(safe-area-inset-bottom,0px))!important;
   left:auto!important;max-height:55dvh!important;z-index:2150;
 }
 .model-atelier.atelier-mobile-tools .atelier-tool-rail button{
   min-width:48px;min-height:46px;font-size:11px;
 }
 .model-atelier.atelier-mobile-tools.atelier-context-active .atelier-tool-rail{
   bottom:calc(min(45dvh,420px) + 9px)!important;max-height:35dvh!important;
 }
 .model-atelier.atelier-mobile-tools.atelier-mobile-expanded .atelier-tool-rail{
   bottom:calc(min(74dvh,740px) + 9px)!important;max-height:18dvh!important;
 }
 .model-atelier.atelier-mobile-tools.atelier-mobile-collapsed .atelier-tool-rail{
   bottom:calc(58px + env(safe-area-inset-bottom,0px))!important;max-height:60dvh!important;
 }
 .model-atelier.atelier-mobile-tools .atelier-viewport-controls{
   left:8px;bottom:calc(8px + env(safe-area-inset-bottom,0px));z-index:2180;
 }
 .model-atelier.atelier-mobile-tools.atelier-context-active .atelier-viewport-controls{
   bottom:calc(min(45dvh,420px) + 8px);
 }
 .model-atelier.atelier-mobile-tools.atelier-mobile-expanded .atelier-viewport-controls{
   bottom:calc(min(74dvh,740px) + 8px);
 }
 .model-atelier.atelier-mobile-tools.atelier-mobile-collapsed .atelier-viewport-controls{
   bottom:62px;
 }
 .model-atelier.atelier-mobile-tools .atelier-viewport-controls button{min-height:44px;min-width:44px}
}
@media (max-width:700px) and (orientation:landscape){
 .model-atelier.atelier-mobile-tools .atelier-context-workbench{
  height:min(58dvh,250px)!important;max-height:calc(100dvh - 65px)!important;
 }
 .model-atelier.atelier-mobile-tools.atelier-mobile-expanded .atelier-context-workbench{
  height:min(82dvh,350px)!important;
 }
 .model-atelier.atelier-mobile-tools .atelier-tool-rail{max-height:54dvh!important}
}
"""
JS=r"""
(function atelierMobileLayoutInstall(){
 const mq=window.matchMedia('(max-width:700px), (pointer:coarse) and (max-width:900px)');
 let panel=null,ui=null,rail=null,observer=null,installed=false;
 const nativeOpen=()=>document.querySelector('#modelAtelierPanel .atelier-inspector');
 function isMobile(){return mq.matches}
 function sync(){
  panel=document.getElementById('modelAtelierPanel');
  ui=panel?.querySelector('#atelierContextWorkbench');
  rail=panel?.querySelector('#modelAtelierToolRail');
  if(!panel||!ui||!rail)return false;
  panel.classList.toggle('atelier-mobile-tools',isMobile());
  if(!isMobile()){
    panel.classList.remove('atelier-mobile-collapsed','atelier-mobile-expanded');
    // Preserve v11.61 desktop native inline display state; only mobile CSS hides it.
  }else{
    // Tool families on the main rail should reveal native operation proxies.
    // Keep native inspector mounted and editable for event/state authority.
    const open=panel.classList.contains('atelier-context-active');
    if(open&&!ui.hidden){
      ui.style.removeProperty('left');ui.style.removeProperty('top');
      ui.style.removeProperty('right');ui.style.removeProperty('bottom');
    }
  }
  return true;
 }
 function setHeight(mode){
  if(!panel)return;
  panel.classList.toggle('atelier-mobile-collapsed',mode==='collapsed');
  panel.classList.toggle('atelier-mobile-expanded',mode==='expanded');
  for(const [name,button] of [['collapsed',panel.querySelector('#atelierMobileCollapse')],['expanded',panel.querySelector('#atelierMobileExpand')]])
   button?.setAttribute('aria-pressed',String(mode===name));
 }
 function attach(){
  if(!sync())return false;
  if(installed)return true;
  installed=true;
  const header=ui.querySelector('.atelier-context-header>div');
  if(!header)return false;
  const btn=(id,name,title)=>{const b=document.createElement('button');b.type='button';b.id=id;b.textContent=name;b.title=title;b.setAttribute('aria-label',title);header.prepend(b);return b;};
  const half=btn('atelierMobileHalf','◧','Set tool drawer to half height');
  const expanded=btn('atelierMobileExpand','⛶','Expand mobile tool drawer');
  const collapsed=btn('atelierMobileCollapse','▁','Collapse mobile tool drawer');
  half.addEventListener('click',()=>setHeight('half'));
  expanded.addEventListener('click',()=>setHeight('expanded'));
  collapsed.addEventListener('click',()=>setHeight('collapsed'));
  // Original dock Context toggle appears in the native inspector, which is
  // intentionally hidden while mobile uses the sole contextual drawer.
  // Provide independent access from the rail, including when closed.
  const openBtn=document.createElement('button');openBtn.type='button';
  openBtn.id='atelierMobileOpenTools';openBtn.textContent='☷ Tools';
  openBtn.setAttribute('aria-label','Open mobile contextual tools');
  rail.prepend(openBtn);
  openBtn.addEventListener('click',()=>{
   if(!isMobile())return;
   panel.querySelector('#atelierContextToggle')?.click();
   setHeight('half');
  });
  // On mobile tapping any existing primary family opens contextual operations
  // rather than the redundant original native inspector.
  rail.addEventListener('click',e=>{
    if(!isMobile()||e.target===openBtn)return;
    const b=e.target.closest('button');
    if(!b||b.id==='atelierMobileOpenTools')return;
    const selected=b.textContent.trim();
    if(!['Meshes','Sculpt','Lasso','Face','Topology','References','Motion','Appearance'].includes(selected))return;
    if(!panel.classList.contains('atelier-context-active'))
      panel.querySelector('#atelierContextToggle')?.click();
    setHeight('half');
    // v11.61 already routes this category via its rail listener when open.
    // When it was closed, its first click happens after the old listener.
    if(ui&&!ui.hidden)window.SWYRL_E_CONTEXT?.select?.(selected);
  });
  mq.addEventListener?.('change',sync);
  window.addEventListener('resize',()=>{if(!isMobile())return;sync()},{passive:true});
  window.visualViewport?.addEventListener('resize',()=>{
   if(!isMobile()||!ui||ui.hidden)return;
   // Keyboard raised: shrink the drawer rather than leave focused fields hidden.
   const avail=window.visualViewport.height;
   ui.style.maxHeight=Math.max(140,avail-72)+'px';
  },{passive:true});
  sync();
  return true;
 }
 observer=new MutationObserver(()=>{if(attach()){observer.disconnect();observer=null;}});
 observer.observe(document.body,{subtree:true,childList:true});
 queueMicrotask(()=>{if(attach()){observer?.disconnect();observer=null;}});
})();
"""
def apply(html):
    assert html.count("SWYRL_ENGINE_DEPLOY_MARKER: V11_61_ADAPTIVE_CONTEXT_TOOL_WORKBENCH")==1
    assert "function atelierMobileLayoutInstall" not in html
    assert html.count('</head>')>=1
    assert html.count("const ModelAtelier=(()=>{")==1
    # Extend navigation-only public registry (not model state authority).
    old='window.SWYRL_E_CONTEXT=Object.freeze({groups:'
    new='window.SWYRL_E_CONTEXT=Object.freeze({select:(name)=>{if(allGroupNames.includes(name)){if(!open)setOpen(true);pickGroup(name)}},groups:'
    assert html.count(old)==1
    html=html.replace(old,new,1)
    html=html.replace("const ModelAtelier=(()=>{",JS+"\nconst ModelAtelier=(()=>{",1)
    return html.replace('</head>','<style id="atelierMobileToolLayoutPreview">'+CSS+'</style>\n</head>',1)
