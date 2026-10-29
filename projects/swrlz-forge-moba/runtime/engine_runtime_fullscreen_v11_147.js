// §E v11.147 — remeasure the EXISTING canvas / menu after Play layout.
// Never start a second rendering loop or move project data. Preserve Stop.
const se147PriorSyncRuntime=se145SyncRuntime;
let se147RefitCount=0;
function se147RefitViewport(){
 const canvas=$('viewport'),host=se143ViewportHost();
 if(!canvas||!host)return false;
 // CSS body.se145-runtime now owns the fullscreen viewport. The WebGL
 // renderer's native resize handler owns its physical drawing buffer.
 if(typeof se143FitCanvasRect==='function')se143FitCanvasRect();
 if(typeof window.dispatchEvent==='function')window.dispatchEvent(new Event('resize'));
 if(typeof se143FitCanvasRect==='function')se143FitCanvasRect();
 se147RefitCount++;
 return true;
}
se145SyncRuntime=function(...args){
 const before=se145.mode;
 const result=se147PriorSyncRuntime(...args);
 if(before!==se145.mode){
  // Refit synchronously so Start Game/LAN are never left with a stale
  // compact 40px overlay. Do one native resize on the next paint as well.
  se147RefitViewport();
  if(typeof requestAnimationFrame==='function')
   requestAnimationFrame(()=>se147RefitViewport());
 }
 return result;
};
const se147PriorStatus=window.SWYRL_ENGINE_LEVELS.status;
window.SWYRL_ENGINE_LEVELS.status=function(){
 const original=se147PriorStatus();
 const host=se143ViewportHost(),canvas=$('viewport');
 const bounds=canvas?.getBoundingClientRect();
 return {...original,runtimeViewportRepair:{
  mode:se145.mode,fullscreen:!!se145.mode&&document.body.classList.contains('se145-runtime'),
  canvasWidth:bounds?.width||0,canvasHeight:bounds?.height||0,
  refits:se147RefitCount,hostMatchesCanvas:!!host&&canvas?.parentElement===host}};
};
