/* §E v11.543 — find existing model tools, not copies of those tools.
   Insert a compact finder in the real Model Studio header, navigate to
   mounted native controls/modes, and RE-PARENT the one native UV Export button
   next to the preview (preserving its original listener/state). */
(function se543ToolFinder(){
 'use strict';
 let root=null,results=null,input=null,open=false,queued=false,lastHit=null;
 const marker='se543-find-target';
 const aliases={
  'se336UVExport':'export uv wireframe download png coordinate guide mesh texture map',
  'se336UVImport':'import painted image png jpeg artwork uv texture',
  'se336UVRemove':'remove texture clear painted uv',
  'se355UVEditorOpen':'uv editor open texture atlas mapping',
  'se356UVRefresh':'refresh uv preview wireframe',
  'se356UVPick3D':'pick model uv locate vertex triangle',
  'se503AtlasPrepare':'experimental front back brim unwrap candidate',
  'se503AtlasApply':'apply experimental uv candidate (may detach paint)',
  'se320ModelProjects':'projects starter models project library',
  'modelAtelierExport':'save model json',
  'modelAtelierOBJ':'export obj mesh',
  'seAtelierExportMenu':'export mesh project file',
  'seAtelierViewMenu':'camera view perspectives',
  'se355UVWhole':'whole model uv atlas',
  'se473RailFold':'toggle expand tools rail categories'
 };
 const curated=[
  {key:'uv-export',name:'Export UV wireframe',terms:'uv download export png wireframe layout current guide texture map',target:'se336UVExport',section:'uv',place:'UV Editor · UV preview'},
  {key:'uv-editor',name:'UV Editor',terms:'open uv window texture atlas unwrap paint',target:'se355UVEditorOpen',section:'uv',place:'Model Studio'},
  {key:'uv-import',name:'Import painted image',terms:'uv import painted texture png jpeg',target:'se336UVImport',section:'uv',place:'UV Editor'},
  {key:'uv-guide',name:'UV wireframe preview',terms:'uv wireframe preview view mode',selector:'[data-se356-mode="guide"]',section:'uv',place:'UV Editor'},
  {key:'uv-stretch',name:'UV stretch heatmap',terms:'uv distortion stretch heatmap',selector:'[data-se356-mode="stretch"]',section:'uv',place:'UV Editor'},
  {key:'projects',name:'Projects',terms:'my projects starter project model library',target:'se320ModelProjects',place:'Model Studio'},
  {key:'tools-rail',name:'Tools panel',terms:'open expand tool rail',target:'se473RailFold',place:'Model Studio'},
  {key:'save-model',name:'Save model JSON',terms:'save export json project',target:'modelAtelierExport',place:'Model Studio'}
 ];
 function panel(){return document.getElementById('modelAtelierPanel');}
 const norm=s=>String(s||'').toLowerCase().normalize('NFKD')
   .replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,' ').trim();
 function entries(){
  const all=curated.map(e=>({...e}));
  const registered=new Set(all.map(e=>e.key));
  const context=window.SWYRL_E_CONTEXT;
  let groups={};
  try{groups=context?.groups?.()||{};}catch(err){console.debug('§E tool groups',err);}
  for(const [category,modes] of Object.entries(groups)){
   if(!Array.isArray(modes))continue;
   const key='category:'+category;
   if(!registered.has(key)){
    all.push({key,name:category,terms:'tool mode category '+category,place:'Tools · '+category,category,mode:null});
    registered.add(key);
   }
   for(const name of modes){
    if(typeof name!=='string'||!name.trim())continue;
    const key='mode:'+category+':'+name;
    if(registered.has(key))continue;
    registered.add(key);
    all.push({key,name,terms:'tool mode '+category+' '+name,
      place:'Tools · '+category,category,mode:name});
   }
  }
  const p=panel();
  if(!p)return all;
  // Inspect mounted *real* controls. Do not fabricate click implementations.
  for(const node of p.querySelectorAll('button[id], button[data-mode], summary, select[id]')){
   if(root?.contains(node)||node.closest('#se543FindRoot'))continue;
   const id=node.id;
   const raw=(node.getAttribute('aria-label')||node.textContent||node.title||'')
     .replace(/\s+/g,' ').trim();
   const label=raw.slice(0,72);
   if(!label||label.length>72||/^[-+−＋]$/.test(label))continue;
   const key='native:'+(id||node.dataset.mode||label);
   if(registered.has(key))continue;
   registered.add(key);
   const section=node.closest('#se355UVPopup')?'uv':null;
   const place=section?'UV Editor':node.closest('.atelier-inspector')?
       'Model Studio · Inspector':'Model Studio';
   all.push({key,name:label,terms:(aliases[id]||'')+' '+id+' '+place,
     target:id||null,node,section,place});
  }
  return all;
 }
 function find(query){
  const words=norm(query).split(' ').filter(Boolean);
  if(!words.length)return [];
  return entries().map(e=>{
   const name=norm(e.name),terms=norm(e.terms),place=norm(e.place);
   const hay=name+' '+terms+' '+place;
   if(!words.every(word=>hay.includes(word)))return null;
   let points=0;
   for(const w of words)points+=name===w?40:name.startsWith(w)?25:name.includes(w)?16:
      terms.includes(w)?8:3;
   if(e.key==='uv-export'&&words.includes('uv'))points+=3;
   return {...e,score:points};
  }).filter(Boolean).sort((a,b)=>b.score-a.score||a.name.localeCompare(b.name)).slice(0,14);
 }
 function targetFor(e){
  return e.node?.isConnected?e.node:
    (e.target?document.getElementById(e.target):null)||
    (e.selector?panel()?.querySelector(e.selector):null);
 }
 function showDetails(node){
  for(let parent=node?.parentElement;parent;parent=parent.parentElement){
   if(parent.tagName==='DETAILS')parent.open=true;
   if(parent.id==='modelAtelierPanel')break;
  }
 }
 function highlight(el){
  if(!el)return;
  if(lastHit?.isConnected)lastHit.classList.remove(marker);
  lastHit=el;el.classList.add(marker);
  try{el.scrollIntoView({block:'center',inline:'nearest',behavior:'auto'});}catch{}
  try{el.focus({preventScroll:true});}catch{}
 }
 function navigate(entry){
  const e=typeof entry==='string'?entries().find(x=>x.key===entry):entry;
  if(!e)return false;
  const p=panel();
  if(!p||p.hidden)return false;
  if(e.category){
   let ok=false;
   try{ok=!!window.SWYRL_E_UNIFIED_TOOLS?.select?.(e.category,e.mode||undefined);}catch{}
   if(!ok){
    const rail=p.querySelector('#modelAtelierToolRail');
    const button=Array.from(rail?.querySelectorAll('button')||[]).find(b=>b.textContent.trim()===e.category);
    if(button){button.click();ok=true;}
   }
   if(!ok)return false;
   if(lastHit?.isConnected)lastHit.classList.remove(marker);
   const mode=e.mode?Array.from(p.querySelectorAll('#seAtelierModes button')).find(b=>b.textContent.trim()===e.mode):null;
   const category=Array.from(p.querySelectorAll('#modelAtelierToolRail button')).find(b=>b.textContent.trim()===e.category);
   highlight(mode||category||p.querySelector('.atelier-inspector'));
   close();
   return true;
  }
  if(e.section==='uv'){
   const api=window.SWYRLZ_E_UV_POPUP;
   if(!api?.open)return false;
   api.open();
  }
  const target=targetFor(e);
  if(!target)return false;
  showDetails(target);
  if(target.closest('.atelier-inspector')){
   p.classList.remove('atelier-tools-closed');
   p.querySelector('.atelier-inspector')?.setAttribute('aria-hidden','false');
  }
  highlight(target);
  close();
  return true;
 }
 function render(){
  if(!results)return;
  results.replaceChildren();
  const found=find(input.value);
  if(!found.length){
   const p=document.createElement('p');p.className='se543-empty';
   p.textContent=input.value.trim()?'No matching controls in this studio.':'Search UV, sculpt, extrude, material, export…';
   results.append(p);return;
  }
  for(const entry of found){
   const item=document.createElement('button');
   item.type='button';item.className='se543-result';
   const label=document.createElement('strong');label.textContent=entry.name;
   const place=document.createElement('small');place.textContent=entry.place||'Model Studio';
   item.append(label,place);
   item.addEventListener('click',()=>{if(!navigate(entry))feedback('Tool unavailable in the current project or mode.');});
   results.append(item);
  }
 }
 function feedback(message){
  const el=results?.querySelector('.se543-empty')||document.createElement('p');
  el.className='se543-empty';el.textContent=message;
  if(!el.isConnected)results?.prepend(el);
 }
 function position(){
  if(!root||!open)return;
  const menu=root.querySelector('#se543FindMenu'),anchor=root.querySelector('#se543FindToggle');
  if(!menu||!anchor)return;
  const b=anchor.getBoundingClientRect();
  const width=Math.min(350,Math.max(220,innerWidth-16));
  menu.style.width=width+'px';
  menu.style.left=Math.max(8,Math.min(b.left,innerWidth-width-8))+'px';
  menu.style.top=Math.min(Math.max(8,b.bottom+6),Math.max(8,innerHeight-245))+'px';
 }
 function close(){
  open=false;
  const box=root?.querySelector('#se543FindMenu');
  if(box)box.hidden=true;
  const btn=root?.querySelector('#se543FindToggle');
  btn?.setAttribute('aria-expanded','false');
 }
 function toggle(){
  if(open){close();return;}
  open=true;root.querySelector('#se543FindMenu').hidden=false;
  root.querySelector('#se543FindToggle').setAttribute('aria-expanded','true');
  render();position();
  input.focus({preventScroll:true});
 }
 function style(){
  if(document.getElementById('se543FindCSS'))return;
  const css=document.createElement('style');css.id='se543FindCSS';
  css.textContent=
   '#se543FindRoot{display:inline-flex;align-items:center;flex:0 0 auto}'+
   '#se543FindToggle{min-height:32px;white-space:nowrap}'+
   '#se543FindMenu{position:fixed;z-index:2147483000;box-sizing:border-box;'+
     'max-width:calc(100vw - 16px);max-height:min(55vh,360px);background:#1d2338;'+
     'border:1px solid #766398;border-radius:10px;padding:9px;'+
     'box-shadow:0 14px 38px #000a;color:#f2f4ff}'+
   '#se543FindMenu[hidden]{display:none!important}'+
   '#se543FindInput{width:100%;box-sizing:border-box;font:inherit;padding:10px;'+
     'border:1px solid #8b78b0;border-radius:7px;background:#10182b;color:white}'+
   '#se543FindResults{max-height:min(37vh,250px);overflow:auto;overscroll-behavior:contain;'+
     'margin-top:7px}'+
   '.se543-result{display:flex!important;flex-direction:column!important;'+
     'align-items:flex-start!important;gap:2px!important;width:100%!important;'+
     'min-height:43px!important;text-align:left!important;margin:2px 0!important;'+
     'padding:6px 9px!important;background:#2b3150!important;color:#f1f5fc!important;'+
     'border:1px solid #445775!important;border-radius:6px!important}'+
   '.se543-result small{font-size:11px;color:#a6bed6}'+
   '.se543-result:focus-visible,.se543-result:hover{border-color:#bca6ff!important}'+
   '.se543-empty{font-size:12px;margin:8px;color:#c9d0df}'+
   '.'+marker+'{outline:3px solid #ebc76b!important;outline-offset:3px!important;'+
     'box-shadow:0 0 0 5px #dfb95b55!important}'+
   '#modelAtelierUVLayout #se336UVExport{min-height:31px;white-space:nowrap}'+
   '@media(max-width:570px){#se543FindToggle{font-size:12px;padding:5px 7px}'+
     '#se543FindMenu{max-height:58vh}}';
  document.head.append(css);
 }
 function moveExport(){
  const p=panel();if(!p)return false;
  const destination=p.querySelector('#se356UVPreview .se356-uv-preview-actions');
  const original=p.querySelector('#se336UVExport');
  if(!destination||!original)return false;
  if(original.parentElement!==destination){
   destination.prepend(original); // MOVE, do not clone or bind a second handler.
   original.title='Export the actual selected-mesh UV wireframe as a PNG';
  }
  return true;
 }
 function mount(){
  const p=panel();if(!p)return;
  style();moveExport();
  const head=p.querySelector('.atelier-head');if(!head)return;
  if(root?.isConnected)return;
  root=document.createElement('div');root.id='se543FindRoot';
  root.innerHTML=
   '<button type="button" id="se543FindToggle" aria-controls="se543FindMenu"'+
    ' aria-expanded="false" aria-label="Find model tool">⌕ Find tool</button>'+
   '<div id="se543FindMenu" hidden role="search" aria-label="Find a Model Studio tool">'+
    '<input type="search" id="se543FindInput" placeholder="Search tools, panels, actions…"'+
    ' autocomplete="off" aria-label="Search Model Studio tools">'+
    '<div id="se543FindResults" aria-live="polite"></div></div>';
  const uv=p.querySelector('#se355UVEditorOpen');
  if(uv)uv.after(root);
  else head.querySelector('.atelier-actions')?.before(root)||head.append(root);
  input=root.querySelector('#se543FindInput');
  results=root.querySelector('#se543FindResults');
  root.querySelector('#se543FindToggle').addEventListener('click',toggle);
  input.addEventListener('input',render);
  root.addEventListener('keydown',event=>{
   if(event.key==='Escape'){
    event.preventDefault();event.stopImmediatePropagation();close();
    root.querySelector('#se543FindToggle').focus({preventScroll:true});
   }else if(event.key==='Enter'&&open&&document.activeElement===input){
    event.preventDefault();const top=find(input.value)[0];
    if(top&&!navigate(top))feedback('Tool unavailable in the current project or mode.');
   }
  },true);
  render();
 }
 function schedule(){
  if(queued)return;queued=true;
  queueMicrotask(()=>{queued=false;mount();});
 }
 function init(){
  mount();
  new MutationObserver(records=>{
   if(records.some(r=>Array.from(r.addedNodes).some(n=>
       n.nodeType===1&&!n.closest?.('#se543FindRoot'))))schedule();
  }).observe(document.body,{subtree:true,childList:true});
  document.addEventListener('pointerdown',e=>{
   if(open&&root&&!root.contains(e.target))close();
  },true);
  window.addEventListener('resize',position);
  document.addEventListener('keydown',e=>{
   if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'&&!panel()?.hidden){
    e.preventDefault();if(!open)toggle();
   }
  });
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
 else queueMicrotask(init);
 window.SWYRL_ENGINE_FIND_TOOLS_543=Object.freeze({
  search:find,navigate,open:()=>{mount();if(!open)toggle();},
  state:()=>({installed:!!root?.isConnected,open,exportNearPreview:
   !!panel()?.querySelector('#se356UVPreview .se356-uv-preview-actions #se336UVExport')})
 });
})();
/* SE543_FIND_TOOLS_END */
