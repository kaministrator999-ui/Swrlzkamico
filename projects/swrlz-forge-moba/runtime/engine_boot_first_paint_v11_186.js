// §E v11.186 — parser-time boot status, independent of the deferred 3D engine.
(function se186BootStatus(){
 const splash=document.getElementById('se185Init');
 const stage=document.getElementById('se185BootStage');
 const retry=document.getElementById('se186BootRetry');
 const recovery=document.getElementById('se186BootRecovery');
 if(!splash||!stage||!retry||!recovery)return;
 window.SWYRL_ENGINE_EARLY_SPLASH=true;
 let stopped=false;
 const ready=()=>document.documentElement.classList.contains('se127-editor-ready');
 const render=()=>{
  if(stopped)return;
  if(ready()){
   stage.textContent='Workspace ready';
   recovery.hidden=true;
   stopped=true;
   clearInterval(timer);
   observer.disconnect();
   return;
  }
  if(window.se128StartupPending)stage.textContent='Restoring selected project';
  else if(document.readyState!=='complete')stage.textContent='Loading engine interface';
  else if(document.querySelector('.app>.topbar')||document.getElementById('mainToolbar'))
   stage.textContent='Synchronizing scene and tools';
  else stage.textContent='Preparing your workspace';
 };
 const observer=new MutationObserver(render);
 observer.observe(document.documentElement,{attributes:true,attributeFilter:['class']});
 const timer=setInterval(render,450);
 retry.addEventListener('click',()=>window.location.reload());
 setTimeout(()=>{
  if(!ready()){
   recovery.hidden=false;
   stage.textContent='Still initializing…';
  }
 },18000);
 render();
})();
