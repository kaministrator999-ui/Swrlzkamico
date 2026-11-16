/* SE467_QUEST_BROWSER_INPUT_START */
function se467ViewportPointerAllowed(event){
 const canvas=renderer?.domElement;
 if(!canvas||!event||event.target!==canvas)return false;
 const top=document.elementFromPoint?.(event.clientX,event.clientY);
 return !top||top===canvas;
}
function se467QuestInstall(host){
 if(!host||host.dataset.se467QuestInstall)return;
 host.dataset.se467QuestInstall='1';
 const inspector=host.querySelector('.atelier-inspector');
 if(!inspector)return;
 inspector.tabIndex=inspector.tabIndex<0?0:inspector.tabIndex;
 inspector.setAttribute('aria-label','Model Studio tools. Scroll with wheel, drag empty areas or use controller stick when available.');
 let scrollDrag=null,over=false,focus=false,swallowClick=false;
 const interactive='button,input,textarea,select,summary,a,[role="button"],.atelier-tool-handle,.se251-resize-grip,[contenteditable="true"]';
 const stop=(event)=>{
  if(!scrollDrag||event?.pointerId!==scrollDrag.id)return;
  const moved=scrollDrag.moved;
  try{inspector.releasePointerCapture?.(scrollDrag.id);}catch(_){}
  scrollDrag=null;
  if(moved)swallowClick=true;
 };
 inspector.addEventListener('pointerenter',()=>{over=true;});
 inspector.addEventListener('pointerleave',()=>{over=false;});
 inspector.addEventListener('focusin',()=>{focus=true;});
 inspector.addEventListener('focusout',()=>{focus=inspector.contains(document.activeElement);});
 inspector.addEventListener('pointerdown',e=>{
  if(e.button!==0||e.target.closest(interactive)||inspector.scrollHeight<=inspector.clientHeight+1)return;
  scrollDrag={id:e.pointerId,x:e.clientX,y:e.clientY,top:inspector.scrollTop,moved:false};
  inspector.focus({preventScroll:true});
  // Capture only an inspector-origin gesture, never a viewport pointer.
  try{inspector.setPointerCapture(e.pointerId);}catch(_){}
 },true);
 inspector.addEventListener('pointermove',e=>{
  const drag=scrollDrag;
  if(!drag||drag.id!==e.pointerId)return;
  const delta=e.clientY-drag.y;
  if(Math.abs(delta)>5)drag.moved=true;
  if(drag.moved){
   inspector.scrollTop=drag.top-delta;
   if(e.cancelable)e.preventDefault();
   e.stopPropagation();
  }
 });
 inspector.addEventListener('pointerup',stop);
 inspector.addEventListener('pointercancel',stop);
 inspector.addEventListener('lostpointercapture',stop);
 inspector.addEventListener('click',e=>{
  if(!swallowClick)return;
  swallowClick=false;
  e.preventDefault();e.stopImmediatePropagation();
 },true);
 inspector.addEventListener('wheel',e=>{
  if(inspector.scrollHeight<=inspector.clientHeight+1)return;
  const before=inspector.scrollTop;
  inspector.scrollTop+=e.deltaY;
  if(inspector.scrollTop!==before){e.preventDefault();e.stopPropagation();}
 },{passive:false});
 inspector.addEventListener('keydown',e=>{
  if(e.target.closest('input,select,textarea,[contenteditable="true"]'))return;
  const amount=e.key==='PageDown'?240:e.key==='PageUp'?-240:e.key==='ArrowDown'?50:e.key==='ArrowUp'?-50:0;
  if(!amount)return;
  inspector.scrollTop+=amount;e.preventDefault();e.stopPropagation();
 });
 let previous=performance.now(),rAF=0;
 function gamepadScroll(now){
  rAF=requestAnimationFrame(gamepadScroll);
  const dt=Math.min(50,Math.max(0,now-previous));previous=now;
  if(host.hidden||(!over&&!focus)||inspector.scrollHeight<=inspector.clientHeight+1)return;
  if(typeof navigator.getGamepads!=='function')return;
  let strongest=0;
  for(const pad of navigator.getGamepads()||[]){
   if(!pad?.connected)continue;
   const axes=pad.axes||[],v=[axes[3],axes[1]].filter(Number.isFinite);
   const axis=v.reduce((best,x)=>Math.abs(x)>Math.abs(best)?x:best,0);
   if(Math.abs(axis)>Math.abs(strongest))strongest=axis;
  }
  if(Math.abs(strongest)>.28)inspector.scrollTop+=strongest*dt*.82;
 }
 rAF=requestAnimationFrame(gamepadScroll);
 // Native editor owns all geometry edits and account/project state.
 const ring=host.querySelector('#se466RingControls');
 if(ring&&!host.querySelector('#se467VertexQuickMode')){
  const control=document.createElement('button');
  control.id='se467VertexQuickMode';control.type='button';
  control.textContent='Switch to Vertex selection';
  control.title='Use native Vertex mode for radius, ring outline or half-ring (180 degree) selection.';
  control.addEventListener('click',()=>{
   const api=window.SWYRL_ENGINE_MODEL_WORKSHOP||ModelAtelier?.workshop;
   const result=api?.setComponentMode?.('vertex');
   se466RingUIRefresh(host);
   if(result?.ok===false&&typeof status==='function')status(result.reason||'Vertex selection unavailable',true);
  });
  ring.prepend(control);
 }
 host.addEventListener('pointerdown',event=>{
  // UI presses never start new viewport gestures, even when a panel floats
  // over the 3D canvas. Do not intercept controls or prevent their defaults.
  if(event.target.closest('.atelier-inspector,.atelier-head,[role="dialog"],.atelier-tool-handle,.se251-resize-grip')){
   if(pressed)pressed=null;
  }
 },true);
}
 /* SE467_QUEST_BROWSER_INPUT_END */