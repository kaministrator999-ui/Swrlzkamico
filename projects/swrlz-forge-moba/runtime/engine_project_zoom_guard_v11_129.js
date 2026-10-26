// §E v11.129: prevent Android browser *page* double-tap magnification
// across a project-picker close / new scene handoff. The existing v11.122
// touch protections remain; this only covers the dynamic hit-target change.
(function se129InstallProjectTapGuard(){
 const hub=document.getElementById('projectHub');
 if(!hub||hub.dataset.se129TapGuard==='1')return;
 hub.dataset.se129TapGuard='1';
 let lastTouchUp=-Infinity;
 let shield=null,releaseTimer=null;
 const clock=()=>performance.now();
 function release(){
  if(releaseTimer!==null)clearTimeout(releaseTimer);
  releaseTimer=null;
  shield?.remove();shield=null;
 }
 function protect(){
  release();
  shield=document.createElement('div');
  shield.id='se129-project-tap-guard';
  shield.setAttribute('aria-hidden','true');
  // Never interfere with text fields; all this layer does is consume taps
  // in the brief (420ms) transition. CSS touch-action keeps pinch available.
  shield.addEventListener('click',event=>event.preventDefault());
  shield.addEventListener('dblclick',event=>event.preventDefault());
  document.body.appendChild(shield);
  releaseTimer=setTimeout(release,420);
 }
 const isTemplate=target=>target?.closest?.('button[data-project-template]');
 // Count genuine touch interactions only. Pointer/mouse/keyboard remain
 // unchanged; tapping the adjacent "default" checkbox does not activate it.
 hub.addEventListener('pointerup',event=>{
  if(event.pointerType==='touch'&&isTemplate(event.target))lastTouchUp=clock();
 },true);
 hub.addEventListener('click',event=>{
  if(!isTemplate(event.target)||clock()-lastTouchUp>900)return;
  lastTouchUp=-Infinity;
  // Allow the native project-opening click to finish first, then install a
  // transparent shield so a second tap cannot hit a different editor button.
  queueMicrotask(protect);
 },true);
 window.addEventListener('pagehide',release,{once:true});
})();
