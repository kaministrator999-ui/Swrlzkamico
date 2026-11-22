/* §E v11.543 — compact global Find Tools / jump-to-area navigation.
 * Navigation-only. Never invokes destructive modeling actions or fakes tools.
 * Reuses native workspace, model mode, project and UV popup entrypoints. */
(function se543ToolSearch(){
 'use strict';
 const CATEGORIES=['Meshes','Sculpt','Lasso','Topology','Face','Appearance','Motion','References'];
 const ITEMS=[
  {id:'workspace-modeler',label:'Model Studio',path:'Workspaces / Modeling',aliases:'model modeling atelier editor',kind:'workspace',target:'modeler'},
  {id:'workspace-game',label:'Game Engine',path:'Workspaces / Game Engine',aliases:'game level world',kind:'workspace',target:'game'},
  {id:'workspace-materials',label:'Materials & Textures',path:'Workspaces / Material Studio',aliases:'material texture pbr paint surfaces',kind:'workspace',target:'materials'},
  {id:'workspace-particles',label:'Particle Studio',path:'Workspaces / Particle Studio',aliases:'particles emitters effects vfx',kind:'workspace',target:'particles'},
  {id:'projects',label:'Starter Projects & My Projects',path:'Projects / Library',aliases:'models library load save starter project character',kind:'click',selector:'#se320ModelProjects,#projectBtn'},
  {id:'uv',label:'UV Editor',path:'Model Studio / UV Editor',aliases:'uv map paint texture unwrap',kind:'uv'},
  {id:'uv-export',label:'Export UV wireframe',path:'Model Studio / UV Editor / Export',aliases:'current uv guide export actual mesh download png save wireframe coordinate guide',kind:'uv-control'},
  {id:'uv-wireframe',label:'UV wireframe',path:'Model Studio / UV Editor',aliases:'preview display show uv layout coordinates',kind:'uv-view',value:'wireframe'},
  {id:'uv-texture',label:'Applied texture',path:'Model Studio / UV Editor',aliases:'painted image preview texture',kind:'uv-view',value:'texture'},
  {id:'uv-surface',label:'Surface map',path:'Model Studio / UV Editor',aliases:'surface directions front back top sides',kind:'uv-view',value:'surface'},
  {id:'uv-stretch',label:'Stretch heatmap',path:'Model Studio / UV Editor',aliases:'uv distortion texel density stretching',kind:'uv-view',value:'stretch'},
  {id:'uv-atlas',label:'Whole model UV atlas',path:'Model Studio / UV Editor',aliases:'islands complete model atlas',kind:'uv-section',value:'whole'},
  {id:'rig',label:'Rigging',path:'Model Studio / Rigging',aliases:'bones skeleton joints skin weights',kind:'mini',target:'rig'},
  {id:'animate',label:'Animation',path:'Model Studio / Animation',aliases:'animate keyframes timeline pose',kind:'mini',target:'animate'},
  {id:'model-mode',label:'Model editing',path:'Model Studio / Model',aliases:'mesh editing mode',kind:'mini',target:'model'},
  {id:'hierarchy',label:'Mesh hierarchy',path:'Model Studio / Meshes',aliases:'object list selection scene tree',kind:'hierarchy'},
  {id:'file',label:'File and export',path:'Model Studio / File',aliases:'import download save clone export',kind:'click',selector:'#seAtelierExportMenu > summary'},
  {id:'settings',label:'Model Studio settings',path:'Model Studio / Settings',aliases:'preferences display quality settings',kind:'header',match:'settings'},
  {id:'camera',label:'Camera views',path:'Model Studio / Views',aliases:'front side perspective top orbit camera',kind:'click',selector:'#seAtelierViewMenu > summary'}
 ];
 let mountQueued=false,open=false,previousFocus=null;
 const $=(q,root=document)=>root?.querySelector?.(q);
 const text=v=>String(v||'').trim();
 const norm=v=>text(v).toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g,'');
 function catalog(){
  const entries=ITEMS.slice();
  const context=window.SWYRL_E_CONTEXT;
  const groups=context?.groups?.()||{};
  for(const cat of CATEGORIES){
   entries.push({id:'group-'+cat,label:cat,path:'Model Studio / Tools',
    aliases:cat.toLowerCase()+' tool panel',kind:'group',category:cat});
   for(const mode of groups[cat]||[]){
    if(typeof mode!=='string'||!mode.trim())continue;
    entries.push({id:'mode-'+cat+'-'+mode,label:mode,path:'Model Studio / '+cat,
     aliases:cat+' '+mode,kind:'group',category:cat,mode});
   }
  }
  return entries;
 }
 function search(query){
  const q=norm(query),words=q.split(/\s+/).filter(Boolean);
  const matches=catalog().map(item=>{
   const name=norm(item.label),path=norm(item.path),hay=name+' '+path+' '+norm(item.aliases);
   if(words.some(w=>!hay.includes(w)))return null;
   const score=!words.length?0:(name===q?200:name.startsWith(q)?140:
    name.includes(q)?105:words.every(w=>name.includes(w))?80:words.some(w=>path.includes(w))?40:20);
   return {item,score};
  }).filter(Boolean);
  matches.sort((a,b)=>b.score-a.score||a.item.label.localeCompare(b.item.label));
  return matches.slice(0,35).map(x=>x.item);
 }
 // Keep ONE native Export UV button and its existing click listener.
 // The preview should expose that control without forcing the user to scroll.
 function relocateUVExport(){
  const action=$('#se336UVExport');
  const preview=$('#se356UVPreview .se356-uv-preview-actions');
  if(!action||!preview)return false;
  if(action.parentElement!==preview){
   preview.prepend(action);
   action.title='Export actual selected-mesh UV wireframe PNG';
  }
  return true;
 }
 function spotlight(button){
  for(let node=button?.parentElement;node;node=node.parentElement)
   if(node.tagName==='DETAILS')node.open=true;
  if(button){
   button.classList?.add('se543-export-highlight');
   reveal(button);
   button.focus?.({preventScroll:true});
  }
 }
 function activateWorkspace(mode){
  const studios=window.SWYRL_ENGINE_STUDIOS;
  if(!studios?.change)return false;
  if(studios.active?.()===mode)return true;
  return studios.change(mode)!==false;
 }
 async function modelReady(){
  if(!activateWorkspace('modeler'))return false;
  // The studio panel and its controls mount asynchronously; a bounded
  // paint-frame retry resolves this without stale timeout-dependent UI.
  for(let i=0;i<18;i++){
   const panel=$('#modelAtelierPanel');
   if(panel&&!panel.hidden)return true;
   await new Promise(resolve=>requestAnimationFrame(resolve));
  }
  return false;
 }
 function enabledClick(selector,root=document){
  const elem=$(selector,root);
  if(!elem||elem.disabled||elem.closest?.('[hidden]'))return false;
  elem.click();return true;
 }
 function reveal(target){
  try{target?.scrollIntoView?.({block:'nearest',behavior:'auto'});}catch(_){}
 }
 function clickByText(root,label){
  const expected=norm(label);
  const buttons=[...root.querySelectorAll('button')];
  const match=buttons.find(b=>norm(b.textContent)===expected)||
    buttons.find(b=>norm(b.textContent).includes(expected));
  if(!match||match.disabled)return false;
  match.click();reveal(match);return true;
 }
 async function navigate(entry){
  if(!entry)return false;
  if(entry.kind==='workspace')return activateWorkspace(entry.target);
  if(!(await modelReady()))return false;
  const panel=$('#modelAtelierPanel');
  if(!panel)return false;
  if(entry.kind==='group'){
   // Tool categories belong to Model mode, not the Rigging/Animation views.
   window.SWYRL_ENGINE_MINI_STUDIOS_496?.set?.('model');
   const tools=window.SWYRL_E_UNIFIED_TOOLS,context=window.SWYRL_E_CONTEXT;
   const modes=context?.groups?.()?.[entry.category]||[];
   if(!tools?.select||!modes.length)return false;
   tools.select(entry.category,entry.mode||modes[0]);
   const selected=context.current?.()||{};
   const succeeded=selected.group===entry.category&&
    (!entry.mode||selected.operation===entry.mode);
   if(succeeded)reveal($('.atelier-inspector',panel));
   return succeeded;
  }
  if(entry.kind==='mini'){
   const api=window.SWYRL_ENGINE_MINI_STUDIOS_496;
   return !!api?.set?.(entry.target);
  }
  if(entry.kind==='uv'||entry.kind==='uv-view'||entry.kind==='uv-section'||entry.kind==='uv-control'){
   const api=window.SWYRLZ_E_UV_POPUP;
   if(!api?.open)return false;
   api.open();
   const popup=$('#se355UVPopup',panel);
   if(!popup||popup.hidden)return false;
   relocateUVExport();
   if(entry.kind==='uv-control'){
    const actual=$('#se336UVExport',popup);
    if(!actual)return false;
    // Navigate/highlight only; file export remains an explicit user click.
    spotlight(actual);
    return true;
   }
   if(entry.kind==='uv-section'){
    return enabledClick('[data-se355-section="'+entry.value+'"]',popup);
   }
   if(entry.kind==='uv-view'){
    const names={wireframe:'UV wireframe',texture:'Applied texture',
     surface:'Surface map',stretch:'Stretch heatmap'};
    const button=[...popup.querySelectorAll('button')]
      .find(b=>norm(b.textContent).startsWith(norm(names[entry.value])));
    if(!button||button.disabled)return false;
    button.click();reveal(button);return true;
   }
   return true;
  }
  if(entry.kind==='hierarchy'){
   const tree=$('#se251ModelLibrary',panel);
   if(!tree)return false;
   if(panel.dataset.se251Collapsed==='true'){
    const toggle=$('.se320-tree-toggle',panel);
    if(!toggle||toggle.disabled)return false;
    toggle.click();
   }
   reveal(tree);return true;
  }
  if(entry.kind==='header'){
   const buttons=[...panel.querySelectorAll('.atelier-head button')];
   const b=buttons.find(x=>norm(x.textContent).startsWith(entry.match));
   if(!b||b.disabled)return false;b.click();return true;
  }
  if(entry.kind==='click'){
   if(entry.id==='projects')
    return enabledClick('#se320ModelProjects',panel)||enabledClick('#projectBtn');
   return enabledClick(entry.selector,panel);
  }
  return false;
 }
 function setStatus(message){
  const status=$('#se543SearchStatus');if(status)status.textContent=message;
 }
 function closeSearch(){
  const modal=$('#se543SearchDialog'),overlay=$('#se543SearchOverlay');
  if(modal)modal.hidden=true;
  if(overlay)overlay.hidden=true;
  open=false;
  if(previousFocus?.isConnected)previousFocus.focus({preventScroll:true});
 }
 function render(){
  const input=$('#se543SearchInput'),results=$('#se543SearchResults');
  if(!input||!results)return;
  results.replaceChildren();
  const hits=search(input.value).slice(0,18);
  if(!hits.length){const p=document.createElement('p');p.className='se543-empty';
   p.textContent='No matching destination. Try a tool name, workspace, or UV feature.';
   results.append(p);setStatus('No matching tools');return;}
  for(const item of hits){
   const b=document.createElement('button');b.type='button';b.className='se543-result';
   b.dataset.se543Id=item.id;
   const name=document.createElement('span');name.className='se543-result-name';
   name.textContent=item.label;
   const path=document.createElement('small');path.textContent=item.path;
   b.append(name,path);
   b.addEventListener('click',()=>{void choose(item);});
   results.append(b);
  }
  setStatus(hits.length+' matching destinations; choose one to open it.');
 }
 async function choose(entry){
  const results=$('#se543SearchResults');
  if(results)results.setAttribute('aria-busy','true');
  setStatus('Opening '+entry.label+'…');
  let ok=false;
  try{ok=await navigate(entry);}catch(error){console.warn('§E navigation search',error);}
  if(results)results.setAttribute('aria-busy','false');
  if(ok){closeSearch();return true;}
  setStatus('Could not open '+entry.label+'. Open its workspace and try again.');
  return false;
 }
 function openSearch(){
  install();
  const overlay=$('#se543SearchOverlay'),dialog=$('#se543SearchDialog');
  if(!overlay||!dialog)return false;
  previousFocus=document.activeElement;open=true;
  overlay.hidden=false;dialog.hidden=false;
  const input=$('#se543SearchInput');
  if(input){input.value='';render();input.focus({preventScroll:true});}
  return true;
 }
 function install(){
  if(!document.body)return;
  relocateUVExport();
  if(!$('#se543SearchDialog')){
   const shade=document.createElement('div');shade.id='se543SearchOverlay';
   shade.className='se543-search-overlay';shade.hidden=true;
   shade.addEventListener('click',closeSearch);
   const dialog=document.createElement('section');dialog.id='se543SearchDialog';
   dialog.className='se543-search-dialog';dialog.hidden=true;
   dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');
   dialog.setAttribute('aria-label','Find a tool or area');
   dialog.innerHTML='<div class="se543-search-head"><strong>Find tool or area</strong>'+
      '<button type="button" id="se543SearchClose" aria-label="Close search">✕</button></div>'+
      '<label for="se543SearchInput" class="se543-search-label">Search §E commands and destinations</label>'+
      '<input type="search" id="se543SearchInput" autocomplete="off" '+
      'placeholder="UV wireframe, sculpt, rigging…" aria-controls="se543SearchResults">'+
      '<div id="se543SearchResults" class="se543-search-results" role="group" aria-label="Matching tools"></div>'+
      '<p id="se543SearchStatus" class="se543-search-status" role="status" aria-live="polite"></p>';
   dialog.addEventListener('keydown',event=>{
    if(event.key==='Escape'){event.preventDefault();event.stopPropagation();closeSearch();return;}
    if(event.key==='Enter'&&event.target.id==='se543SearchInput'){
      const first=$('#se543SearchResults button');if(first){event.preventDefault();first.click();}
    }
    if(event.key==='Tab'){
      const focusable=[...dialog.querySelectorAll('button,input')].filter(x=>!x.disabled);
      const idx=focusable.indexOf(document.activeElement);
      if(event.shiftKey&&idx===0){event.preventDefault();focusable.at(-1)?.focus();}
      else if(!event.shiftKey&&idx===focusable.length-1){event.preventDefault();focusable[0]?.focus();}
    }
   });
   dialog.addEventListener('pointerdown',event=>event.stopPropagation());
   document.body.append(shade,dialog);
   $('#se543SearchClose').addEventListener('click',closeSearch);
   $('#se543SearchInput').addEventListener('input',render);
  }
  // Add a small Find control to the existing native workspace menu, and a
  // fallback in Model Studio header when the workspace menu is not visible.
  const menus=[...document.querySelectorAll('.se187-workspace-tabs,.se225-studio-tabs')];
  for(const nav of menus){
   if(nav.querySelector('[data-se543-find]'))continue;
   const b=document.createElement('button');b.type='button';
   b.className='se543-find-button';b.dataset.se543Find='1';
   b.setAttribute('aria-label','Find a tool or area');b.textContent='⌕ Find';
   b.addEventListener('click',openSearch);nav.append(b);
  }
  const head=$('#modelAtelierPanel .atelier-head');
  if(head&&!head.querySelector('[data-se543-find]')){
   const b=document.createElement('button');b.type='button';
   b.dataset.se543Find='1';b.className='se543-find-button';
   b.textContent='⌕ Find';b.title='Find a tool or workspace';
   b.addEventListener('click',openSearch);
   const projects=$('#se320ModelProjects',head);
   if(projects)projects.after(b);else head.prepend(b);
  }
 }
 function boot(){
  install();
  const observer=new MutationObserver(records=>{
   if(mountQueued)return;
   if(!records.some(r=>[...r.addedNodes].some(node=>node.nodeType===1&&
     (node.matches?.('.se187-workspace-tabs,.se225-studio-tabs,#modelAtelierPanel,#se356UVPreview,#modelAtelierUVLayout,#se355UVPopup')||
      node.querySelector?.('.se187-workspace-tabs,.se225-studio-tabs,#modelAtelierPanel,#se356UVPreview,#modelAtelierUVLayout,#se355UVPopup')))))return;
   mountQueued=true;queueMicrotask(()=>{mountQueued=false;install();});
  });
  observer.observe(document.body,{childList:true,subtree:true});
  document.addEventListener('keydown',event=>{
   // Ctrl/Cmd+K is a keyboard shortcut, but never capture when user is
   // composing in a text box (unless explicitly using the modifier).
   if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){
    event.preventDefault();openSearch();
   }else if(event.key==='Escape'&&open){event.preventDefault();closeSearch();}
  });
 }
 window.SWYRL_E_TOOL_SEARCH_543=Object.freeze({
  search,navigate,relocateExport:relocateUVExport,open:openSearch,close:closeSearch,
  status:()=>({open,installed:!!$('#se543SearchDialog')})
 });
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});
 else queueMicrotask(boot);
})();
/* SE543_TOOL_SEARCH_END */
