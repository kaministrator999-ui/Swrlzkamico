// §E v11.226 candidate — one context-aware browser, native controls only.
// The source panels are temporarily portaled, never cloned. No game renderer,
// project model, WebXR controller, Sheep Tag input or studio controller is replaced.
(function se226Browser() {
 'use strict';
 if (window.SWYRL_ENGINE_BROWSER) return;
 const s={open:false,tab:'',mode:'',host:null,pane:null,nav:null,search:null,
   moved:null,anchor:null,drag:null,rect:null,tabs:{},init:false};
 const defaults={game:'assets',modeler:'model',particles:'particles',materials:'materials'};
 const names={assets:'Assets',scene:'Scene & Details',model:'Model Inspector',
   tools:'Tools & Actions',materials:'Materials',particles:'Particles',
   rig:'Rig & Animation',projects:'Projects'};
 const sets={game:['assets','scene','tools','materials','particles','projects'],
   modeler:['model','rig','tools','materials','particles','projects'],
   materials:['materials','assets','tools','particles','projects'],
   particles:['particles','assets','tools','materials','projects']};
 function context(){return window.SWYRL_ENGINE_STUDIOS?.active?.()
   ||window.SWYRL_ENGINE_WORKSPACES?.active?.()||'game';}
 function target(tab,mode){
   if(tab==='assets'&&mode==='game')return document.querySelector('.app > .workspace > .panel.left');
   if(tab==='scene'&&mode==='game')return document.querySelector('.app > .workspace > .panel.right');
   if(['model','rig'].includes(tab)&&mode==='modeler')
     return document.querySelector('#modelAtelierPanel .atelier-inspector');
   if(tab==='materials'&&mode==='materials')return document.getElementById('se225MaterialsPanel');
   if(tab==='particles'&&mode==='particles')return document.getElementById('se223Panel');
   return null;
 }
 function restore(){
   if(!s.moved)return;
   const el=s.moved,anchor=s.anchor;
   el.classList.remove('se226-portaled');
   if(anchor?.parentNode){anchor.parentNode.insertBefore(el,anchor);anchor.remove();}
   s.moved=null;s.anchor=null;
 }
 function portal(el){
   if(!el||el===s.moved)return;
   restore();
   const anchor=document.createComment('§E native tool panel return point');
   el.parentNode.insertBefore(anchor,el);
   s.anchor=anchor;s.moved=el;s.pane.append(el);el.classList.add('se226-portaled');
 }
 function size(){
   if(!s.host||!s.open)return;
   const box=s.host.getBoundingClientRect();
   if(s.rect){
     const top=Math.max(48,Math.min(innerHeight-110,s.rect.y));
     const width=Math.min(Math.max(280,s.rect.w),innerWidth-12);
     const height=Math.min(Math.max(220,s.rect.h),innerHeight-top-8);
     const left=Math.min(Math.max(6,s.rect.x),innerWidth-width-6);
     s.host.style.left=left+'px';s.host.style.top=top+'px';
     s.host.style.right='auto';s.host.style.width=width+'px';s.host.style.height=height+'px';
   }else if(box.right>innerWidth||box.bottom>innerHeight){
     s.host.style.right='6px';s.host.style.top='54px';
   }
 }
 function storage(){
   try{sessionStorage.setItem('se226-browser-tabs',JSON.stringify(s.tabs));}catch(_){}
 }
 function renderTabs(){
   s.nav.replaceChildren();
   for(const id of sets[s.mode]||sets.game){
     const b=document.createElement('button');b.type='button';b.textContent=names[id];
     b.className=id===s.tab?'active':'';b.dataset.se226Select=id;
     b.setAttribute('role','tab');b.setAttribute('aria-selected',String(id===s.tab));
     b.tabIndex=id===s.tab?0:-1;
     b.addEventListener('click',()=>select(id));
     s.nav.append(b);
   }
 }
 function showMessage(message,action){
   const p=document.createElement('p');p.className='se226-note';p.textContent=message;
   s.pane.append(p);
   if(action){
     const b=document.createElement('button');b.type='button';b.className='se226-card';
     b.textContent=action.label;b.addEventListener('click',action.run);s.pane.append(b);
   }
 }
 function actionItems(){
   const selectors=s.mode==='modeler'
     ?['#modelAtelierPanel .atelier-head button','#modelAtelierPanel .atelier-inspector button',
       '#modelAtelierPanel .atelier-tool-rail button','#modelAtelierPanel .atelier-scene button']
     :['.app > .topbar button','.viewport-toolbar button',
       '.app > .workspace > .panel button'];
   const found=[],used=new Set();
   for(const selector of selectors)for(const el of document.querySelectorAll(selector)){
     if(el.closest('#se226Browser')||el.classList.contains('se226-launch')||el.disabled)continue;
     const label=(el.getAttribute('aria-label')||el.title||el.textContent||'').trim().replace(/\s+/g,' ').slice(0,75);
     if(!label||used.has(el))continue;
     used.add(el);found.push({el,label});
   }
   return found.slice(0,110);
 }
 function renderActions(){
   const q=s.search.value.trim().toLowerCase();
   const items=actionItems().filter(x=>x.label.toLowerCase().includes(q));
   const grid=document.createElement('div');grid.className='se226-gallery';
   for(const item of items){
     const b=document.createElement('button');b.type='button';b.className='se226-card';
     b.textContent=item.label;b.title='Use existing §E control: '+item.label;
     b.addEventListener('click',()=>{const el=item.el;close();setTimeout(()=>el.isConnected&&el.click(),0);});
     grid.append(b);
   }
   s.pane.append(grid);
   if(!items.length)showMessage(q?'No matching native tools.':'No tools available in this workspace.');
 }
 function navigate(mode){
   const change=window.SWYRL_ENGINE_STUDIOS?.change;
   if(typeof change!=='function'){showMessage('Studio navigation is not available yet.');return;}
   restore();change(mode);
   s.mode=mode;s.tab=defaults[mode];s.search.value='';render();
 }
 function projectAction(){
   close();
   const b=document.querySelector('.se-main-project-button,#openProjects,[data-action="projects"]');
   if(b)setTimeout(()=>b.click(),0);
   else if(typeof window.openProjectHub==='function')window.openProjectHub();
 }
 function render(){
   restore();s.pane.replaceChildren();renderTabs();
   const t=target(s.tab,s.mode);
   if(t){portal(t);if(s.search.value.trim())findInPanel();return;}
   if(s.tab==='tools'){renderActions();return;}
   if(s.tab==='materials'||s.tab==='particles'){
     showMessage('Open '+names[s.tab]+' in the native §E workspace to edit real project assets.',
       {label:'Open '+names[s.tab]+' Studio',run:()=>navigate(s.tab)});
     return;
   }
   if(s.tab==='projects'){
     showMessage('Use the existing project library, imports, starters and saved projects.',
       {label:'Open Projects',run:projectAction});return;
   }
   if(s.tab==='assets'){
     showMessage('Your existing asset browser is available in Game Engine.',
       {label:'Open Game assets',run:()=>{window.SWYRL_ENGINE_STUDIOS?.change?.('game');s.mode='game';s.tab='assets';render();}});
     return;
   }
   if(s.tab==='rig'){
     showMessage('Select a model part or hand bone in the native inspector. The existing rig, pose, and animation tools remain connected to the same model.');
     return;
   }
   showMessage('No native editor panel is available for this selection.');
 }
 function findInPanel(){
   if(!s.moved)return;
   const q=s.search.value.trim().toLowerCase();
   if(!q)return;
   const nodes=s.moved.querySelectorAll('h3,h4,label,button,option,strong,[title]');
   for(const el of nodes){
     if((el.textContent||el.title||'').toLowerCase().includes(q)){
       if(el.tagName==='OPTION')el.parentElement?.scrollIntoView({block:'nearest'});
       else el.scrollIntoView({block:'nearest'});
       break;
     }
   }
 }
 function select(tab){
   if(!(sets[s.mode]||sets.game).includes(tab))return;
   s.tab=tab;s.tabs[s.mode]=tab;storage();s.search.value='';
   render();
 }
 function syncButtons(){
   for(const b of document.querySelectorAll('.se226-launch'))
     b.setAttribute('aria-expanded',String(s.open));
 }
 function open(tab){
   if(!s.init)init();
   if(!s.host)return;
   s.mode=context();
   const allowed=sets[s.mode]||sets.game;
   s.tab=allowed.includes(tab)?tab:allowed.includes(s.tabs[s.mode])?s.tabs[s.mode]:defaults[s.mode]||'tools';
   s.open=true;s.host.hidden=false;document.body.dataset.se226Open='true';
   s.host.setAttribute('aria-label','§E browser · '+s.mode);
   s.search.value='';render();size();syncButtons();s.search.focus({preventScroll:true});
 }
 function close(){
   if(!s.open)return;
   restore();s.open=false;s.host.hidden=true;
   delete document.body.dataset.se226Open;
   s.rect=null;s.host.removeAttribute('style');
   syncButtons();
 }
 function installLaunchers(){
   for(const nav of document.querySelectorAll('.se187-workspace-tabs,.se225-studio-tabs')){
     if(nav.querySelector('.se226-launch'))continue;
     const b=document.createElement('button');b.type='button';b.className='se226-launch';
     b.textContent='☷ Browser';b.title='Browse tools and assets · one panel';
     b.setAttribute('aria-controls','se226Browser');b.setAttribute('aria-expanded','false');
     b.addEventListener('click',()=>s.open?close():open());
     nav.append(b);
   }
 }
 function pointerDown(event,kind){
   if(event.button!==0)return;
   const box=s.host.getBoundingClientRect();
   s.rect={x:box.left,y:box.top,w:box.width,h:box.height};
   s.drag={kind,x:event.clientX,y:event.clientY,from:{...s.rect}};
   event.currentTarget.setPointerCapture?.(event.pointerId);event.preventDefault();
 }
 function pointerMove(event){
   if(!s.drag)return;
   const d=s.drag,dx=event.clientX-d.x,dy=event.clientY-d.y;
   if(d.kind==='drag'){s.rect.x=d.from.x+dx;s.rect.y=d.from.y+dy;}
   else{s.rect.w=d.from.w+dx;s.rect.h=d.from.h+dy;}
   size();
 }
 function init(){
   if(s.init)return;s.init=true;
   try{const value=JSON.parse(sessionStorage.getItem('se226-browser-tabs')||'{}');
     if(value&&typeof value==='object')for(const key of Object.keys(sets))
       if(sets[key].includes(value[key]))s.tabs[key]=value[key];
   }catch(_){}
   const host=document.createElement('section');host.id='se226Browser';host.hidden=true;
   host.setAttribute('role','dialog');host.setAttribute('aria-modal','false');
   host.innerHTML='<header class="se226-head"><span class="se226-grab" title="Drag browser">☷ §E Browser</span><button class="se226-close" type="button" aria-label="Close browser">✕</button></header><nav class="se226-tabs" role="tablist" aria-label="Tool categories"></nav><div class="se226-search-row"><input type="search" aria-label="Search browser tools" placeholder="Find assets or tools…" autocomplete="off"></div><div class="se226-pane"></div><div class="se226-resize" title="Resize browser" role="presentation"></div>';
   document.body.append(host);s.host=host;s.pane=host.querySelector('.se226-pane');
   s.nav=host.querySelector('.se226-tabs');s.search=host.querySelector('input');
   host.querySelector('.se226-close').addEventListener('click',close);
   s.search.addEventListener('input',()=>{if(s.tab==='tools'){s.pane.replaceChildren();renderActions();}else findInPanel();});
   host.querySelector('.se226-grab').addEventListener('pointerdown',e=>pointerDown(e,'drag'));
   host.querySelector('.se226-resize').addEventListener('pointerdown',e=>pointerDown(e,'resize'));
   host.addEventListener('pointermove',pointerMove);
   host.addEventListener('pointerup',()=>s.drag=null);
   host.addEventListener('pointercancel',()=>s.drag=null);
   document.addEventListener('keydown',event=>{
     if(event.key==='Escape'&&s.open){event.preventDefault();close();}
     if((event.ctrlKey||event.metaKey)&&event.code==='Space'&&!event.repeat
       &&!event.target.closest('input,textarea,[contenteditable=true]')){
       event.preventDefault();s.open?close():open();
     }
   });
   document.addEventListener('pointerdown',event=>{
     if(s.open&&!host.contains(event.target)&&!event.target.closest('.se226-launch'))close();
   },true);
   document.addEventListener('click',event=>{
     if(event.target.closest('[data-se187-tab],[data-se225-tab]'))close();
   },true);
   window.addEventListener('resize',()=>{if(s.open)size();});
   document.body.dataset.se226Ready='true';
   installLaunchers();
   // Native workspace bars are mounted asynchronously. Mount the launcher
   // after their standard bootstrap without keeping a scene-wide DOM observer.
   setTimeout(installLaunchers,120);setTimeout(installLaunchers,800);
 }
 window.SWYRL_ENGINE_BROWSER=Object.freeze({
   open,close,select,inspect:()=>({open:s.open,workspace:s.mode,tab:s.tab,
     nativePortaled:!!s.moved,rendererReplaced:false})
 });
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(init,0),{once:true});
 else setTimeout(init,0);
})();
