/* SE442_SATCHEL_DIALOG_START
 * Reuse the native lesson panel and its listeners in an independent flat UI.
 * This adapter owns local window layout only; lesson/model/save/XR data stay native.
 */
(function se442SatchelDialog(){
 'use strict';
 const STORAGE='se442:satchel:dialog-layout:v1',GAP=8;
 const q=(selector,root=document)=>root?.querySelector(selector);
 let panel=null,handle=null,fold=null,launcher=null,model=null,drag=null,queued=false;
 let modelObserver=null,resizeObserver=null;
 const layouts={desktop:{collapsed:false,closed:false,x:null,y:null},mobile:{collapsed:true,closed:false,x:null,y:null}};
 try{
  const saved=JSON.parse(localStorage.getItem(STORAGE)||'null');
  if(saved?.version===1)for(const mode of ['desktop','mobile']){
   const row=saved[mode];if(!row||typeof row!=='object')continue;
   for(const name of ['collapsed','closed'])if(typeof row[name]==='boolean')layouts[mode][name]=row[name];
   for(const name of ['x','y'])if(Number.isFinite(row[name]))layouts[mode][name]=row[name];
  }
 }catch(_){}
 function mode(){return innerWidth<=700||(innerWidth<=980&&matchMedia('(pointer:coarse)').matches)?'mobile':'desktop';}
 function layout(){return layouts[mode()];}
 function persist(){try{localStorage.setItem(STORAGE,JSON.stringify({version:1,...layouts}));}catch(_){}}
 function viewport(){
  const v=window.visualViewport,left=v?.offsetLeft||0,top=v?.offsetTop||0;
  const width=Math.max(1,v?.width||innerWidth),height=Math.max(1,v?.height||innerHeight);
  return {left:left+GAP,top:top+GAP,right:left+width-GAP,bottom:top+height-GAP,width,height};
 }
 function active(){
  return !!panel&&window.SWYRL_ENGINE_TUTORIAL_412?.status?.().active===true&&
   !!model&&!model.hidden&&model.getClientRects().length>0&&getComputedStyle(model).visibility!=='hidden';
 }
 function inXR(){return window.SWYRL_ENGINE_MODEL_VR?.read?.().active===true;}
 function visibleRect(element){
  if(!element||element.hidden||!element.getClientRects().length)return null;
  const rect=element.getBoundingClientRect();return rect.width>0&&rect.height>0?rect:null;
 }
 function bottomAnchor(v){
  if(mode()!=='mobile')return v.bottom;
  // The compact native toolbar can sit above an inspector or at screen bottom.
  // Anchor above its real horizontal row, rather than obscuring its buttons.
  const bars=['#modelAtelierToolRail','#seAtelierModes'].map(s=>visibleRect(q(s,model)))
   .filter(r=>r&&r.width>r.height*2&&r.top>v.top+110&&r.top<v.bottom);
  return bars.length?Math.min(v.bottom,...bars.map(r=>r.top-GAP)):v.bottom-48;
 }
 function place(element,x,y,v){
  const rect=element.getBoundingClientRect();
  const left=Math.max(v.left,Math.min(x,Math.max(v.left,v.right-rect.width)));
  const top=Math.max(v.top,Math.min(y,Math.max(v.top,v.bottom-rect.height)));
  element.style.left=Math.round(left)+'px';element.style.top=Math.round(top)+'px';
  element.style.right='auto';element.style.bottom='auto';
 }
 function fit(){
  if(!panel||!launcher)return;
  const v=viewport(),row=layout(),mobile=mode()==='mobile';
  const width=Math.max(1,Math.min(mobile?350:366,v.width-GAP*2));
  panel.style.setProperty('--se442-window-width',width+'px');
  // Retain a useful work area even when the on-screen keyboard is present.
  panel.style.setProperty('--se442-window-height',Math.max(54,Math.min(580,(v.height-GAP*2)*(mobile?.68:.78)))+'px');
  panel.dataset.se442Layout=mobile?'mobile':'desktop';
  const bottom=bottomAnchor(v);
  if(!launcher.hidden){
   // Keep the restore control away from the global Chat button and bottom
   // toolbars. It occupies a compact corner of the actual modeling viewport.
   const canvas=visibleRect(q('#modelAtelierViewport > canvas',model));
   const box=launcher.getBoundingClientRect();
   const transforms=visibleRect(q('#se320ModelTransform',model));
   const top=canvas?Math.max(canvas.top+GAP,transforms&&transforms.height<100?transforms.bottom+GAP:0):bottom-box.height;
   place(launcher,canvas?canvas.left+GAP:v.left,top,v);
  }
  if(panel.hidden)return;
  const rect=panel.getBoundingClientRect(),scene=visibleRect(q('.atelier-scene',model));
  const x=Number.isFinite(row.x)?row.x:(mobile?v.right-rect.width:Math.min(v.right,scene?.right||v.right)-rect.width-GAP);
  let y;
  if(Number.isFinite(row.y))y=row.y;
  else if(mobile)y=bottom-rect.height;
  else{
   const bar=visibleRect(q('#se320ModelTransform',model));
   y=Math.max(v.top,(scene?.top||v.top)+GAP,(bar?.bottom||0)+GAP);
  }
  place(panel,x,y,v);
 }
 function sync(){
  if(!panel||!launcher)return;
  const row=layout(),available=active()&&!inXR();
  const hide= !available||row.closed;
  if(panel.hidden!==hide)panel.hidden=hide;
  if(launcher.hidden!==( !available||!row.closed))launcher.hidden= !available||!row.closed;
  panel.classList.toggle('collapsed',row.collapsed);
  fold.textContent=row.collapsed?'+':'−';
  fold.setAttribute('aria-expanded',String(!row.collapsed));
  fold.setAttribute('aria-label',row.collapsed?'Expand satchel tutorial':'Collapse satchel tutorial');
  fold.title=row.collapsed?'Expand current task':'Collapse current task';
  launcher.setAttribute('aria-expanded',String(!panel.hidden&&!row.collapsed));
  const task=q('#se412Step',panel)?.textContent?.trim();
  launcher.title=task?'Open satchel tutorial · '+task:'Open the current satchel tutorial task';
  fit();
 }
 function schedule(){
  if(queued)return;queued=true;
  requestAnimationFrame(()=>{queued=false;sync();});
 }
 function rememberPosition(){
  if(!panel||panel.hidden)return;
  const rect=panel.getBoundingClientRect(),row=layout();row.x=rect.left;row.y=rect.top;persist();
 }
 function collapse(value=true){
  if(!panel)return;
  cancelDrag();
  const focusInside=panel.contains(document.activeElement),row=layout();
  row.closed=false;row.collapsed=!!value;persist();sync();
  if(value&&focusInside)fold.focus({preventScroll:true});
 }
 function open(){
  if(!panel)return;
  const row=layout();row.closed=false;row.collapsed=false;persist();sync();
  if(!panel.hidden)fold.focus({preventScroll:true});
 }
 function close(){
  if(!panel)return;
  cancelDrag();
  layout().closed=true;persist();sync();
  if(!launcher.hidden)launcher.focus({preventScroll:true});
 }
 function reset(){
  cancelDrag();
  const row=layout();row.x=null;row.y=null;persist();sync();
 }
 function cancelDrag(){
  if(!drag)return;
  const id=drag.id;drag=null;panel?.classList.remove('se442-dragging');
  try{if(handle.hasPointerCapture(id))handle.releasePointerCapture(id);}catch(_){}
 }
 function finish(event){
  if(!drag||event.pointerId!==drag.id)return;
  cancelDrag();
  rememberPosition();
 }
 function button(id,label,text,handler){
  const el=document.createElement('button');el.type='button';el.id=id;
  el.textContent=text;el.setAttribute('aria-label',label);el.title=label;el.addEventListener('click',handler);return el;
 }
 function installPanel(){
  handle=q('#se412Drag',panel);fold=q('#se412Fold',panel);
  const title=q('strong',handle),count=q('#se412Count',handle),body=q('.se412-content',panel);
  if(!handle||!fold||!title||!body)return false;
  panel.classList.add('se442-satchel-dialog');panel.setAttribute('role','dialog');
  panel.setAttribute('aria-modal','false');panel.removeAttribute('aria-label');
  title.id='se442SatchelTitle';panel.setAttribute('aria-labelledby',title.id);
  body.id='se442SatchelContent';fold.setAttribute('aria-controls',body.id);
  const heading=document.createElement('div');heading.className='se442-satchel-heading';
  handle.insertBefore(heading,title);heading.append(title);if(count)heading.append(count);
  handle.tabIndex=0;handle.setAttribute('aria-label','Move satchel tutorial. Drag or use the arrow keys.');
  handle.title='Drag to move · arrow keys move · Shift + arrows move farther · Home resets position';
  handle.insertBefore(button('se442SatchelReset','Reset tutorial window position','↺',reset),fold);
  handle.append(button('se442SatchelClose','Minimize tutorial to its launcher','×',close));
  fold.addEventListener('click',()=>collapse(!layout().collapsed));
  // Integration removes the old scene-relative drag and fold listeners first.
  handle.addEventListener('pointerdown',event=>{
   if(event.button!==0||event.isPrimary===false||event.target.closest('button'))return;
   const box=panel.getBoundingClientRect();
   drag={id:event.pointerId,x:event.clientX,y:event.clientY,left:box.left,top:box.top};
   try{handle.setPointerCapture(event.pointerId);}catch(_){}
   handle.focus({preventScroll:true});panel.classList.add('se442-dragging');event.preventDefault();event.stopPropagation();
  });
  handle.addEventListener('pointermove',event=>{
   if(!drag||event.pointerId!==drag.id)return;
   place(panel,drag.left+event.clientX-drag.x,drag.top+event.clientY-drag.y,viewport());
   event.preventDefault();event.stopPropagation();
  });
  for(const name of ['pointerup','pointercancel','lostpointercapture'])handle.addEventListener(name,finish);
  handle.addEventListener('keydown',event=>{
   if(event.target!==handle)return;
   if(event.key==='Home'){event.preventDefault();event.stopPropagation();reset();return;}
   const directions={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]},direction=directions[event.key];
   if(!direction||event.altKey||event.ctrlKey||event.metaKey)return;
   const box=panel.getBoundingClientRect(),distance=event.shiftKey?32:8;
   place(panel,box.left+direction[0]*distance,box.top+direction[1]*distance,viewport());
   rememberPosition();event.preventDefault();event.stopPropagation();
  });
  panel.addEventListener('keydown',event=>{
   if(event.key==='Escape'){
    collapse(true);event.preventDefault();
   }
   event.stopPropagation();
  });
  // Events inside the window must not reach the editor's viewport shortcuts.
  // There is no backdrop, global pointer capture, or Tab/focus trap.
  for(const name of ['pointerdown','pointermove','pointerup','click','dblclick','wheel','keyup'])
   panel.addEventListener(name,event=>event.stopPropagation());
  if(typeof ResizeObserver!=='undefined'){
   resizeObserver=new ResizeObserver(schedule);resizeObserver.observe(panel);
  }
  return true;
 }
 function mount(next=q('#se412Panel')){
  if(!next||next.id!=='se412Panel')return false;
  if(next!==panel){
   resizeObserver?.disconnect();panel=next;
   if(!installPanel()){panel=null;return false;}
  }
  const nextModel=q('#modelAtelierPanel');
  if(model!==nextModel){
   modelObserver?.disconnect();model=nextModel;
   if(model&&typeof MutationObserver!=='undefined'){
    modelObserver=new MutationObserver(schedule);
    modelObserver.observe(model,{attributes:true,attributeFilter:['hidden','class','style']});
   }
  }
  if(!launcher){
   launcher=button('se442SatchelLauncher','Open satchel tutorial','✦ Satchel tutorial',open);
   launcher.setAttribute('aria-controls','se412Panel');launcher.setAttribute('aria-haspopup','dialog');
   launcher.hidden=true;document.body.append(launcher);
  }
  if(panel.parentElement!==document.body)document.body.append(panel);
  sync();return true;
 }
 window.addEventListener('resize',schedule);window.addEventListener('orientationchange',schedule);
 window.visualViewport?.addEventListener('resize',schedule);window.visualViewport?.addEventListener('scroll',schedule);
 window.addEventListener('swrlz:model-vr-state',()=>{cancelDrag();sync();});
 window.addEventListener('swrlz:project-loaded',schedule);
 window.addEventListener('swrlz:model-workshop-change',schedule);
 window.SWYRL_E_SATCHEL_DIALOG_442=Object.freeze({mount,open,collapse,close,reset,
  status:()=>({mounted:!!panel,active:active(),xr:inXR(),open:!!panel&&!panel.hidden,
   collapsed:layout().collapsed,closed:layout().closed,layout:mode(),
   launcher:!!launcher&&!launcher.hidden,parent:panel?.parentElement?.tagName||null})});
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>mount(),{once:true});
 else queueMicrotask(()=>mount());
})();
/* SE442_SATCHEL_DIALOG_END */
