/* SE502_UV_TOUCH_RESIZE_START
   Extends the existing se355UVEditor popup in place. No UV editor reparenting. */
let se502Maximized=false,se502RestoreBox=null,se502ResizeState=null;
const se502MinSize=()=>({width:210,height:210});
function se502Bounds(){
 const b=safeBounds();
 return {left:b.left,top:b.top,right:Math.max(b.left+1,b.right),bottom:Math.max(b.top+1,b.bottom)};
}
function se502ApplyBox(left,top,width,height){
 if(!popup)return;
 const b=se502Bounds(),min=se502MinSize();
 const maxW=b.right-b.left,maxH=b.bottom-b.top;
 const w=se473Clamp(width,Math.min(min.width,maxW),maxW);
 const h=se473Clamp(height,Math.min(min.height,maxH),maxH);
 const x=se473Clamp(left,b.left,Math.max(b.left,b.right-w));
 const y=se473Clamp(top,b.top,Math.max(b.top,b.bottom-h));
 Object.assign(popup.style,{
  left:x+'px',top:y+'px',width:w+'px',height:h+'px',
  right:'auto',bottom:'auto',maxWidth:maxW+'px',maxHeight:maxH+'px'
 });
}
function se502CurrentBox(){
 const r=popup.getBoundingClientRect();
 return {left:r.left,top:r.top,width:r.width,height:r.height};
}
function se502ApplyMax(){
 const b=se502Bounds();
 se502ApplyBox(b.left,b.top,b.right-b.left,b.bottom-b.top);
}
function se502UpdateMaxButton(){
 const btn=popup?.querySelector('#se502UVMax');
 if(!btn)return;
 btn.textContent=se502Maximized?'▢ Restore':'□ Max';
 btn.title=se502Maximized?'Restore previous UV window size':'Expand UV Editor to available screen';
 btn.setAttribute('aria-pressed',String(se502Maximized));
 btn.setAttribute('aria-label',btn.title);
 popup.classList.toggle('se502-uv-maximized',se502Maximized);
}
function se502ToggleMax(){
 if(!popup||popup.hidden)return;
 if(!se502Maximized){
  se502RestoreBox=se502CurrentBox();
  se502Maximized=true;
  se502ApplyMax();
 }else{
  se502Maximized=false;
  const box=se502RestoreBox;
  if(box)se502ApplyBox(box.left,box.top,box.width,box.height);
  else fitWindow(true);
  se502RestoreBox=null;
  se473RememberWindow();
 }
 se502UpdateMaxButton();
}
function se502CalculateResize(box,dir,dx,dy){
 const b=se502Bounds(),min=se502MinSize();
 const mw=Math.min(min.width,b.right-b.left),mh=Math.min(min.height,b.bottom-b.top);
 let left=box.left,top=box.top,right=box.left+box.width,bottom=box.top+box.height;
 if(dir.includes('w'))left=se473Clamp(box.left+dx,b.left,right-mw);
 if(dir.includes('e'))right=se473Clamp(box.left+box.width+dx,left+mw,b.right);
 if(dir.includes('n'))top=se473Clamp(box.top+dy,b.top,bottom-mh);
 if(dir.includes('s'))bottom=se473Clamp(box.top+box.height+dy,top+mh,b.bottom);
 return {left,top,width:right-left,height:bottom-top};
}
function se502AttachGrip(handle,dir){
 let active=null;
 handle.addEventListener('pointerdown',e=>{
  if(popup.hidden||se502Maximized||e.button!==0)return;
  e.preventDefault();e.stopPropagation();
  active={id:e.pointerId,x:e.clientX,y:e.clientY,box:se502CurrentBox()};
  se502ResizeState=active;
  popup.classList.add('se502-uv-resizing');
  try{handle.setPointerCapture(e.pointerId);}catch(_){}
 });
 handle.addEventListener('pointermove',e=>{
  if(!active||active.id!==e.pointerId)return;
  e.preventDefault();e.stopPropagation();
  const next=se502CalculateResize(active.box,dir,e.clientX-active.x,e.clientY-active.y);
  se502ApplyBox(next.left,next.top,next.width,next.height);
 });
 const end=e=>{
  if(!active||active.id!==e.pointerId)return;
  active=null;se502ResizeState=null;
  popup.classList.remove('se502-uv-resizing');
  try{if(handle.hasPointerCapture(e.pointerId))handle.releasePointerCapture(e.pointerId);}catch(_){}
  se473RememberWindow();
  e.stopPropagation();
 };
 handle.addEventListener('pointerup',end);
 handle.addEventListener('pointercancel',end);
 handle.addEventListener('keydown',e=>{
  const step=e.shiftKey?48:16;
  const d=e.key==='ArrowLeft'?[-step,0]:e.key==='ArrowRight'?[step,0]:
   e.key==='ArrowUp'?[0,-step]:e.key==='ArrowDown'?[0,step]:null;
  if(!d||popup.hidden||se502Maximized)return;
  e.preventDefault();e.stopPropagation();
  const current=se502CurrentBox();
  const next=se502CalculateResize(current,dir,...d);
  se502ApplyBox(next.left,next.top,next.width,next.height);
  se473RememberWindow();
 });
}
function se502InstallResizable(el){
 if(!el||el.dataset.se502UVResizeInstalled==='1')return;
 el.dataset.se502UVResizeInstalled='1';
 const title=el.querySelector('#se355UVHandle');
 const close=el.querySelector('#se355UVClose');
 if(title&&close){
  const max=document.createElement('button');max.type='button';
  max.id='se502UVMax';max.className='se502-uv-max-button';
  max.addEventListener('click',e=>{e.stopPropagation();se502ToggleMax();});
  close.before(max);
 }
 for(const dir of ['n','s','e','w','ne','nw','se','sw']){
  const grip=document.createElement('div');
  grip.className='se502-uv-grip se502-uv-'+dir;
  grip.dataset.se502Resize=dir;
  grip.setAttribute('role','separator');
  grip.setAttribute('tabindex','0');
  grip.setAttribute('aria-label','Resize UV Editor '+({n:'top',s:'bottom',e:'right',w:'left',ne:'top right',nw:'top left',se:'bottom right',sw:'bottom left'}[dir]));
  grip.title='Drag to resize UV Editor';
  se502AttachGrip(grip,dir);
  el.append(grip);
 }
 se502UpdateMaxButton();
 if(window.visualViewport&&!el.dataset.se502ViewportBound){
  el.dataset.se502ViewportBound='1';
  window.visualViewport.addEventListener('resize',()=>{if(el===popup&&!el.hidden)fitWindow(false);});
 }
}
const se502PriorFitWindow=fitWindow;
fitWindow=function(reset=false){
 if(se502Maximized&&popup&&!popup.hidden){se502ApplyMax();return;}
 se502PriorFitWindow(reset);
};
/* SE502_UV_TOUCH_RESIZE_END */