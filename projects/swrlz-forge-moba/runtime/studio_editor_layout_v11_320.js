/* SE320_EDITOR_LAYOUT_START */
// Layout only: move existing controls with their native listeners intact.
(function se320EditorLayout(){
 const q=(s,root=document)=>root.querySelector(s);
 let pending=false;
 function button(text,fn){const b=document.createElement('button');b.type='button';b.textContent=text;b.addEventListener('click',fn);return b;}
 function labelProject(){
  const label=q('#se320ModelProject');if(!label)return;
  const draft=window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.();
  const name=draft?'Untitled model':currentProject?.name||'Untitled model';
  if(label.textContent!==name)label.textContent=name;label.title=name;
 }
 // Keep the native mesh transform modes visible without moving or cloning their
 // original handlers. v11.320 tucked the native strip into a closed <details>
 // panel; the unified category view then hid that entire section.
 const se320TransformSelectors=Object.freeze({
  move:'[data-mode="move"]',rotate:'[data-mode="rotate"]',
  scale:'[data-mode="scale"]',x:'[data-axis="x"]',
  y:'[data-axis="y"]',z:'[data-axis="z"]',
  minus:'[data-mesh-minus]',plus:'[data-mesh-plus]'
 });
 function se320RefreshTransformAccess(panel){
  const bar=q('#se320ModelTransform',panel);
  const native=q('#modelAtelierMeshQuickStrip',panel);
  if(!bar)return;
  for(const button of bar.querySelectorAll('[data-se320-transform]')){
   const original=native?.querySelector(se320TransformSelectors[button.dataset.se320Transform]);
   button.disabled=!original||original.disabled;
   if(button.hasAttribute('aria-pressed')){
    const pressed=original?.getAttribute('aria-pressed')==='true';
    button.setAttribute('aria-pressed',String(pressed));
   }
  }
 }
 function se320ModelTransformAccess(panel,inspector){
  const native=q('#modelAtelierMeshQuickStrip',panel);
  if(!native)return; // Native selection/gizmo module may mount after the layout.
  let bar=q('#se320ModelTransform',inspector);
  if(!bar){
   bar=document.createElement('section');
   bar.id='se320ModelTransform';
   bar.className='se320-model-transform';
   bar.setAttribute('aria-label','Selected mesh transform tools');
   bar.innerHTML=
    '<div class="se320-transform-label">Transform</div>'+
    '<div class="se320-transform-modes" role="group" aria-label="Transform mode">'+
    '<button type="button" data-se320-transform="move" aria-pressed="false">↔ Move</button>'+
    '<button type="button" data-se320-transform="rotate" aria-pressed="false">⟳ Rotate</button>'+
    '<button type="button" data-se320-transform="scale" aria-pressed="false">⤢ Scale</button></div>'+
    '<div class="se320-transform-axes" role="group" aria-label="Transform axis and nudge">'+
    '<button type="button" data-se320-transform="x" aria-pressed="false">X</button>'+
    '<button type="button" data-se320-transform="y" aria-pressed="false">Y</button>'+
    '<button type="button" data-se320-transform="z" aria-pressed="false">Z</button>'+
    '<button type="button" data-se320-transform="minus" aria-label="Nudge negative along axis">−</button>'+
    '<button type="button" data-se320-transform="plus" aria-label="Nudge positive along axis">+</button></div>';
   const handle=q('.atelier-tool-handle',inspector);
   if(handle)handle.after(bar);else inspector.prepend(bar);
   bar.addEventListener('click',event=>{
    const button=event.target.closest('button[data-se320-transform]');
    if(!button||button.disabled||!bar.contains(button))return;
    // Dispatch into the actual pre-existing control so gizmos, grouping,
    // history and native validation all remain owned by Model Atelier.
    const source=q('#modelAtelierMeshQuickStrip',panel)?.querySelector(
     se320TransformSelectors[button.dataset.se320Transform]);
    source?.click();
    se320RefreshTransformAccess(panel);
   });
   new MutationObserver(()=>se320RefreshTransformAccess(panel)).observe(native,{
    subtree:true,attributes:true,attributeFilter:['aria-pressed','disabled','hidden']
   });
  }
  se320RefreshTransformAccess(panel);
 }
 function modelLayout(){
  const panel=q('#modelAtelierPanel'),body=q('.atelier-body',panel||document);
  if(!panel||!body)return;
  const inspector=q('.atelier-inspector',panel),rail=q('#modelAtelierToolRail',panel);
  if(!inspector||!rail)return;
  if(!panel.hasAttribute('data-se320-ui')){
   panel.dataset.se320Ui='true';
   body.insertBefore(rail,inspector);
   const modes=q('#seAtelierModes',panel),handle=q('.atelier-tool-handle',inspector);
   if(modes){if(handle)handle.after(modes);else inspector.prepend(modes);}
   const selection=document.createElement('details');selection.className='se320-selection-tools';
   const selectionTitle=document.createElement('summary');selectionTitle.textContent='Selection, components & groups';selection.append(selectionTitle);
   for(const element of panel.querySelectorAll('[data-component-controls],.atelier-group-mobile,#modelAtelierMeshToolsOpen,#modelAtelierMeshQuickStrip'))selection.append(element);
   if(modes)modes.after(selection);else if(handle)handle.after(selection);else inspector.prepend(selection);
   const quick=q('#modelAtelierMeshQuickStrip',selection);
   quick?.addEventListener('pointerdown',e=>{if(e.target.closest('.amq-head')&&!e.target.closest('button,input,select'))e.stopPropagation();},true);
   const heading=q('.atelier-head',panel),title=q('strong',heading);
   if(title){title.textContent='Model Studio';title.title='§wyrlz Engine · Modeling';}
   const project=document.createElement('span');project.id='se320ModelProject';project.className='se320-project-name';
   const projects=button('Projects',()=>q('#projectBtn')?.click());projects.id='se320ModelProjects';projects.setAttribute('aria-label','Open starter projects and My Projects');
   if(title){title.after(project);title.before(projects);}else heading.prepend(projects,project);
   const strong=q('.atelier-tool-handle strong',inspector);if(strong)strong.textContent='Tool settings';
   rail.addEventListener('click',event=>{
    if(!event.target.closest('button'))return;
    if(panel.dataset.se251RightCollapsed==='true')q('.se251-external-collapse',panel)?.click();
   },true);
   new MutationObserver(schedule).observe(panel,{attributes:true,attributeFilter:['class','hidden','data-se251-layout','data-se251-right-collapsed','data-se251-collapsed']});
   new MutationObserver(schedule).observe(inspector,{attributes:true,attributeFilter:['class']});
  }
  se320ModelTransformAccess(panel,inspector);
  const tree=q('#se251ModelLibrary',panel),treeHeading=tree&&q('.se251-side-title',tree);
  if(treeHeading&&!q('.se320-tree-toggle',treeHeading)){
   const existing=q('.se251-side-actions button',tree);
   if(existing){const caption=document.createElement('span');caption.textContent='Meshes';existing.classList.add('se320-tree-toggle');treeHeading.replaceChildren(caption,existing);}
  }
  const treeToggle=treeHeading&&q('.se320-tree-toggle',treeHeading);
  if(treeToggle){const collapsed=panel.dataset.se251Collapsed==='true',text=collapsed?'›':'‹';if(treeToggle.textContent!==text)treeToggle.textContent=text;treeToggle.title=collapsed?'Show model hierarchy':'Hide model hierarchy';treeToggle.setAttribute('aria-label',treeToggle.title);treeToggle.setAttribute('aria-expanded',String(!collapsed));}
  const compact=panel.dataset.se251Layout==='compact';
  if(compact&&panel.dataset.se320WasCompact!=='true'){
   panel.dataset.se320WasCompact='true';const settings=q('#se185AtelierTopToggle',panel);
   // Compact starts with the canvas visible; the existing View settings button
   // can reopen all controls immediately. Native state/handlers own the toggle.
   if(settings?.getAttribute('aria-expanded')==='true')settings.click();
  }else if(!compact)panel.dataset.se320WasCompact='false';
  const closed=panel.dataset.se251RightCollapsed==='true'||inspector.classList.contains('atelier-tools-closed')||panel.classList.contains('atelier-tools-closed');
  const value=String(closed);if(panel.dataset.se320InspectorCollapsed!==value)panel.dataset.se320InspectorCollapsed=value;
  const toggle=q('.se251-external-collapse',panel);
  if(toggle){
   const text=closed?'Show inspector':'Hide inspector';if(toggle.textContent!==text)toggle.textContent=text;toggle.setAttribute('aria-label',text);toggle.setAttribute('aria-expanded',String(!closed));
   if(!toggle.dataset.se320Restore){
    toggle.dataset.se320Restore='true';
    const restoreNative=()=>{const api=window.SWYRL_E_UNIFIED_TOOLS,last=api?.current?.(),button=[...rail.querySelectorAll('button')].find(b=>b.textContent.trim()===last?.category)||rail.querySelector('button');button?.click();if(last?.category&&last?.mode)api?.select?.(last.category,last.mode);};
    toggle.addEventListener('click',event=>{
     if(!panel.classList.contains('atelier-tools-closed'))return;
     if(panel.dataset.se251RightCollapsed==='true'){queueMicrotask(()=>{if(panel.dataset.se251RightCollapsed!=='true'&&panel.classList.contains('atelier-tools-closed'))restoreNative();});return;}
     event.preventDefault();event.stopImmediatePropagation();restoreNative();
    },true);
   }
  }
  labelProject();
 }
 function projectHub(){
  const hub=q('#projectHub');if(!hub||hub.dataset.se320Ui)return;
  hub.dataset.se320Ui='true';
  const title=q('.project-head>b',hub);if(title)title.textContent='Project Library';
  const close=q('.project-head button',hub);if(close){close.title='Close project library';close.setAttribute('aria-label','Close project library');}
 }
 function positionExtras(details){
  const box=q('.se320-game-extras',details),rect=q('summary',details).getBoundingClientRect();
  box.style.top=Math.min(rect.bottom+6,innerHeight-100)+'px';
  box.style.left=Math.max(8,Math.min(rect.left,innerWidth-Math.min(380,innerWidth-16)-8))+'px';
 }
 function gameLayout(){
  const app=q('.app'),toolbar=q('.app>.topbar'),nav=q('.se187-game-tabs',toolbar||document),menus=q('#engineMenubar');
  if(!app||!toolbar||!nav||!menus||q('#se320GameHeader'))return;
  const header=document.createElement('header');header.id='se320GameHeader';
  app.prepend(header);header.append(nav,menus);app.dataset.se320Ui='true';
  const primary=new Set(['projectBtn','saveBtn','loadBtn','playBtn','pauseBtn','simulateBtn','stopBtn','undoBtn','redoBtn','moveBtn','rotateBtn','scaleBtn','spaceBtn']);
  const extras=document.createElement('details');extras.id='se320GameMore';
  const summary=document.createElement('summary');summary.textContent='More tools';summary.setAttribute('aria-label','Scene, build, recording and VR tools');
  const box=document.createElement('div');box.className='se320-game-extras';
  const title=document.createElement('strong');title.textContent='Scene, build & VR';box.append(title);extras.append(summary,box);
  for(const child of [...toolbar.children]){
   if(child.id==='fileInput'||primary.has(child.id))continue;
   if(child.classList.contains('sep')||child.classList.contains('spacer')){child.classList.add('se320-unused-separator');continue;}
   box.append(child);
  }
  toolbar.append(extras);
  extras.addEventListener('toggle',()=>{if(extras.open)positionExtras(extras);});
  toolbar.addEventListener('scroll',()=>{if(extras.open)positionExtras(extras);},{passive:true});
  window.addEventListener('resize',()=>{if(extras.open)positionExtras(extras);});
  document.addEventListener('pointerdown',e=>{if(extras.open&&!extras.contains(e.target))extras.open=false;});
  extras.addEventListener('keydown',e=>{if(e.key==='Escape'){extras.open=false;summary.focus();}});
  // Native menubar retains its actions; keyboard focus and Escape are explicit.
  menus.addEventListener('keydown',e=>{
   const menu=e.target.closest('.engine-menu');if(!menu)return;
   if(e.key==='Escape'){menu.classList.remove('open');q(':scope>button',menu)?.focus();}
   if(e.key==='ArrowDown'&&e.target===q(':scope>button',menu)){e.preventDefault();if(!menu.classList.contains('open'))e.target.click();q('.engine-menu-pop button',menu)?.focus();}
  });
 }
 function particles(){
  const root=q('#se249Root'),header=q('.se249-header',root||document),nav=q('.se249-workspaces',root||document);
  if(!root||!header||!nav)return;
  if(!root.dataset.se320Ui){
  root.dataset.se320Ui='true';header.prepend(nav);nav.setAttribute('aria-label','Editor studios');
  const commands=q('.se249-commandbar',root),projects=q('[data-se249-action=project]',commands),preview=q('#se249Play',commands);
  if(commands&&projects&&preview){commands.prepend(projects);projects.after(preview);}
  for(const b of root.querySelectorAll('button')){
   if(!b.getAttribute('aria-label'))b.setAttribute('aria-label',b.title||b.textContent.trim());
  }
  const menus=q('.se249-menus',root);
  if(menus){
   const place=d=>{const box=q('.se249-menu-pop',d),r=q('summary',d)?.getBoundingClientRect();if(!box||!r)return;box.style.setProperty('--se320-menu-left',Math.max(8,Math.min(r.left,innerWidth-Math.min(280,innerWidth-16)-8))+'px');box.style.setProperty('--se320-menu-top',Math.min(r.bottom+6,innerHeight-100)+'px');};
   menus.addEventListener('toggle',e=>{if(e.target.open){for(const other of menus.querySelectorAll('details[open]'))if(other!==e.target)other.open=false;place(e.target);}},true);
   window.addEventListener('resize',()=>{for(const d of menus.querySelectorAll('details[open]'))place(d);});
  }
  }
  const tools=[...root.querySelectorAll('.se249-menus details')].find(d=>q('summary',d)?.textContent==='Tools');
  const options=tools&&q('.se249-menu-pop',tools);
  if(options)for(const el of root.querySelectorAll('.se250-mode-selector,.se251-unified-mode'))if(el.parentElement!==options)options.append(el);
 }
 function sceneChrome(){
  const viewport=q('.app>.workspace>.viewport-wrap');
  if(viewport&&!q('.se320-scene-info',viewport)){
   const info=document.createElement('div');info.className='se320-scene-info';
   const levels=q('#st141LevelBar',viewport),badge=q('.badgeBox',viewport),stamp=q('#buildStamp',viewport);
   if(levels||badge){viewport.append(info);if(levels)info.append(levels);if(badge)info.append(badge);if(stamp){stamp.textContent='§wyrlz Engine · Game Studio';info.append(stamp);}
    let previous=-1;new ResizeObserver(()=>{const h=Math.ceil(info.getBoundingClientRect().height);if(h!==previous){previous=h;viewport.style.setProperty('--se320-scene-info-height',h+'px');}}).observe(info);
   }
  }
  const stats=q('#se274HUD');if(!stats)return;
  const mode=window.SWYRL_ENGINE_STUDIOS?.active?.();
  const host=mode==='modeler'?q('#modelAtelierPanel .atelier-head'):mode==='particles'?q('#se249Root .se249-commandbar'):mode==='materials'?q('#se225MaterialsPanel .se225-m-title'):q('#se320GameHeader');
  if(!host)return;
  let slot=q('.se320-diagnostics-slot',host);
  if(!slot){slot=document.createElement('div');slot.className='se320-diagnostics-slot';host.append(slot);}
  if(stats.parentElement!==slot)slot.append(stats);
  if(!stats.dataset.se320Ui){stats.dataset.se320Ui='true';stats.addEventListener('click',()=>requestAnimationFrame(()=>{
   const r=stats.getBoundingClientRect();stats.style.setProperty('--se320-stats-top',Math.min(r.bottom+8,innerHeight-100)+'px');stats.style.setProperty('--se320-stats-left',Math.max(8,Math.min(r.left,innerWidth-290))+'px');
  }));}
 }
 function arrange(){pending=false;modelLayout();projectHub();gameLayout();particles();sceneChrome();}
 function schedule(){if(!pending){pending=true;requestAnimationFrame(arrange);}}
 function install(){
  arrange();
  // Native workspaces mount lazily; observe added DOM, never per-frame state.
  new MutationObserver(records=>{if(records.some(r=>[...r.addedNodes].some(n=>n.nodeType===1)))schedule();}).observe(document.body,{childList:true,subtree:true});
  window.addEventListener('swrlz:project-loaded',()=>{labelProject();schedule();});
  new MutationObserver(schedule).observe(document.body,{attributes:true,attributeFilter:['data-se225-workspace','class']});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else queueMicrotask(install);
})();
/* SE320_EDITOR_LAYOUT_END */
