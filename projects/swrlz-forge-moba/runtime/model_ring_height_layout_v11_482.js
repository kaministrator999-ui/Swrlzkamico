/* SE482_RING_HEIGHT_LAYOUT_START */
// Viewport-owned, draggable ring height panel. Native ringTransform, Apply,
// Cancel and Undo remain in the v11.478 controller unchanged.
(function se482RingHeightLayout(){
 'use strict';
 let panelUI=null,header=null,drag=null,placed=false,userMoved=false,watching=false;
 const getViewport=()=>document.querySelector('#modelAtelierViewport')||
  document.querySelector('#modelAtelierPanel .atelier-scene');
 function bounds(){
  const view=getViewport(),card=panelUI;
  if(!view||!card)return null;
  const r=view.getBoundingClientRect();
  const width=card.offsetWidth||280,height=card.offsetHeight||150;
  const minX=r.left+6,maxX=Math.max(minX,r.right-width-6);
  const shapes=document.getElementById('se477SelectionShapes');
  const topbar=document.getElementById('se474SpecificModes');
  const lower=[shapes,topbar].filter(el=>el&&!el.hidden)
   .map(el=>el.getBoundingClientRect().bottom);
  const minY=Math.max(r.top+8,...lower.map(y=>y+8));
  const maxY=Math.max(minY,r.bottom-height-8);
  return {minX,maxX,minY,maxY,r,width,height};
 }
 const clamp=(v,a,b)=>Math.min(Math.max(v,a),b);
 function set(x,y){
  if(!panelUI)return;
  const b=bounds();if(!b)return;
  const left=Math.round(clamp(x,b.minX,b.maxX));
  const top=Math.round(clamp(y,b.minY,b.maxY));
  const setProp=(name,value)=>{
   if(panelUI.style.getPropertyValue(name)!==value)panelUI.style.setProperty(name,value);
  };
  setProp('--se482-ring-left',left+'px');
  setProp('--se482-ring-top',top+'px');
 }
 function reposition(){
  if(!panelUI||panelUI.hidden)return;
  const b=bounds();if(!b)return;
  if(!placed){
   // Start within the viewport under the selection bars, away from inspector.
   set(b.minX+4,b.minY+10);
   placed=true;return;
  }
  const left=parseFloat(panelUI.style.getPropertyValue('--se482-ring-left'));
  const top=parseFloat(panelUI.style.getPropertyValue('--se482-ring-top'));
  set(Number.isFinite(left)?left:b.minX,Number.isFinite(top)?top:b.minY);
 }
 function release(event){
  if(!drag||event.pointerId!==drag.id)return;
  try{if(header.hasPointerCapture(event.pointerId))header.releasePointerCapture(event.pointerId);}catch{}
  drag=null;
 }
 function ensure(){
  const ui=document.getElementById('se478RingHeightSlider');
  if(!ui)return;
  if(ui!==panelUI){
   panelUI=ui;header=ui.querySelector('.se478-height-header');
   if(!header)return;
   header.setAttribute('role','button');header.setAttribute('tabindex','0');
   header.setAttribute('aria-label','Move ring height controls');
   header.title='Drag to move the Ring Height controls';
   const grip=document.createElement('span');grip.id='se482HeightGrip';
   grip.textContent='⋮⋮ Drag';
   header.prepend(grip);
   header.addEventListener('pointerdown',event=>{
    if(event.button!==0||panelUI.hidden)return;
    event.stopPropagation();event.preventDefault();
    reposition();
    drag={id:event.pointerId,x:event.clientX,y:event.clientY,
     left:parseFloat(panelUI.style.getPropertyValue('--se482-ring-left')),
     top:parseFloat(panelUI.style.getPropertyValue('--se482-ring-top'))};
    try{header.setPointerCapture(event.pointerId);}catch{}
   });
   header.addEventListener('pointermove',event=>{
    if(!drag||event.pointerId!==drag.id)return;
    event.stopPropagation();event.preventDefault();
    set(drag.left+event.clientX-drag.x,drag.top+event.clientY-drag.y);
    userMoved=true;
   });
   for(const type of ['pointerup','pointercancel'])header.addEventListener(type,release);
   header.addEventListener('keydown',event=>{
    const change={ArrowUp:[0,-20],ArrowDown:[0,20],ArrowLeft:[-20,0],ArrowRight:[20,0]}[event.key];
    if(!change)return;
    event.preventDefault();
    reposition();
    set(parseFloat(panelUI.style.getPropertyValue('--se482-ring-left'))+change[0],
     parseFloat(panelUI.style.getPropertyValue('--se482-ring-top'))+change[1]);
    userMoved=true;
   });
   new MutationObserver(records=>{
    if(records.some(x=>x.attributeName==='hidden')&&!ui.hidden)
     requestAnimationFrame(reposition);
   }).observe(ui,{attributes:true,attributeFilter:['hidden']});
  }
  reposition();
 }
 function schedule(){requestAnimationFrame(ensure);}
 if(document.readyState==='loading')
  document.addEventListener('DOMContentLoaded',schedule,{once:true});
 else schedule();
 window.addEventListener('swrlz:model-workshop-change',schedule);
 window.addEventListener('resize',schedule,{passive:true});
 window.addEventListener('orientationchange',schedule,{passive:true});
 const originalInstall=se430BeginnerInstall;
 se430BeginnerInstall=function(...args){
  const r=originalInstall.apply(this,args);schedule();return r;
 };
 window.SWYRL_ENGINE_RING_HEIGHT_LAYOUT_482=Object.freeze({
  inspect:()=>({visible:!!panelUI&&!panelUI.hidden,
   attached:!!header,dragging:!!drag,userMoved,
   left:panelUI?parseFloat(panelUI.style.getPropertyValue('--se482-ring-left')):null,
   top:panelUI?parseFloat(panelUI.style.getPropertyValue('--se482-ring-top')):null}),
  setPosition:(x,y)=>{ensure();if(!Number.isFinite(x)||!Number.isFinite(y))return false;set(x,y);userMoved=true;return true;},
  sync:ensure
 });
})();
/* SE482_RING_HEIGHT_LAYOUT_END */