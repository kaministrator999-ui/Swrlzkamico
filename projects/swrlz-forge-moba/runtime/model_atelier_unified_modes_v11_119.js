// §E v11.119: one movable inspector, a mode ribbon above the category rail,
// and compact top controls. All actual model mutations remain native.
function seAtelierModeNames(api,category){
 const groups=api?.groups?.()||{};
 return [...new Set((groups[category]||[]).filter(name=>
  typeof name==='string'&&name.trim()).map(s=>s.trim()))];
}
function seAtelierModeChoose(panel,category,mode){
 const api=window.SWYRL_E_CONTEXT;
 if(!api?.activate?.(category,mode))return false;
 const inspector=panel.querySelector('.atelier-inspector');
 panel.classList.add('se-inspector-mode-view');
 panel.classList.remove('atelier-tools-closed');
 inspector?.setAttribute('aria-hidden','false');
 return true;
}
function seAtelierModeToolbarInstall(panel){
 if(panel.querySelector('#seAtelierModes'))return;
 const rail=panel.querySelector('#modelAtelierToolRail');
 const inspector=panel.querySelector('.atelier-inspector');
 const api=window.SWYRL_E_CONTEXT;
 if(!rail||!inspector||!api?.activate)return;
 const modeBar=document.createElement('nav');
 modeBar.id='seAtelierModes';
 modeBar.className='se-atelier-modes';
 modeBar.setAttribute('role','toolbar');
 modeBar.setAttribute('aria-label','Modes for current Model Atelier tool');
 modeBar.hidden=true;
 panel.append(modeBar);
 const handle=inspector.querySelector('.atelier-tool-handle');
 const label=document.createElement('span');
 label.className='se-inspector-mode-label';
 label.setAttribute('aria-live','polite');
 handle?.querySelector('strong')?.after(label);
 let currentCategory='',currentMode='';
 const categories=['Meshes','Sculpt','Lasso','Topology','Face',
                   'Appearance','Motion','References'];
 const rerender=()=>{
  const names=seAtelierModeNames(api,currentCategory);
  modeBar.hidden=names.length<=1;
  modeBar.setAttribute('aria-label',currentCategory+' modes');
  modeBar.replaceChildren();
  for(const name of names){
   const button=document.createElement('button');
   button.type='button';
   button.textContent=name;
   button.dataset.mode=name;
   button.setAttribute('aria-pressed',String(name===currentMode));
   button.addEventListener('click',()=>{
    if(!seAtelierModeChoose(panel,currentCategory,name))return;
    currentMode=api.current()?.operation||name;
    rerender();
   });
   modeBar.append(button);
  }
  label.textContent=currentCategory+(currentMode?' · '+currentMode:'');
 };
 const chooseCategory=(category,mode)=>{
  if(!categories.includes(category))return;
  const choices=seAtelierModeNames(api,category);
  if(!seAtelierModeChoose(panel,category,mode||choices[0]))return;
  currentCategory=category;
  currentMode=api.current()?.operation||choices[0]||'';
  rerender();
 };
 rail.addEventListener('click',event=>{
  const button=event.target?.closest?.('button');
  if(!button||!rail.contains(button))return;
  const category=button.textContent.trim();
  if(category==='More'){
   currentCategory='';currentMode='';
   modeBar.hidden=true;
   modeBar.replaceChildren();
   panel.classList.remove('se-inspector-mode-view');
   label.textContent='';
   return;
  }
  if(categories.includes(category))chooseCategory(category);
 });
 // The existing native header's Context button is redundant once settings are
 // inline. If activated via a keyboard shortcut, keep it in this same inspector.
 handle?.querySelector('#atelierContextToggle')?.addEventListener('click',()=>{
  if(!currentCategory)chooseCategory('Meshes');
 });
 window.SWYRL_E_UNIFIED_TOOLS=Object.freeze({
  select:(category,mode)=>chooseCategory(category,mode),
  current:()=>({category:currentCategory,mode:currentMode,showModes:!modeBar.hidden})
 });
}
function seAtelierTopBarArrange(panel){
 const header=panel.querySelector('.atelier-head');
 const actions=header?.querySelector('.atelier-actions');
 if(actions&&!actions.querySelector('#seAtelierExportMenu')){
  const buttons=Array.from(actions.children).filter(n=>n.tagName==='BUTTON');
  const save=buttons.find(b=>/save model/i.test(b.textContent))||buttons[0];
  const close=buttons.find(b=>/^close$/i.test(b.textContent.trim()));
  const exports=buttons.filter(b=>b!==save&&b!==close);
  if(exports.length){
   const menu=document.createElement('details');
   menu.id='seAtelierExportMenu';
   const summary=document.createElement('summary');
   summary.textContent='Export ▾';
   summary.setAttribute('aria-label','Export and render model');
   const box=document.createElement('div');
   box.className='se-export-options';
   for(const b of exports)box.append(b);
   menu.append(summary,box);
   if(close)close.before(menu);else actions.append(menu);
  }
 }
 const bar=panel.querySelector('#modelAtelierViewportModes');
 const cameras=bar?.querySelector('.atelier-top-camera');
 if(cameras&&!bar.querySelector('#seAtelierViewMenu')){
  const menu=document.createElement('details');
  menu.id='seAtelierViewMenu';
  const summary=document.createElement('summary');
  summary.textContent='Views ▾';
  summary.setAttribute('aria-label','Camera view presets');
  cameras.before(menu);
  menu.append(summary,cameras);
 }
}
