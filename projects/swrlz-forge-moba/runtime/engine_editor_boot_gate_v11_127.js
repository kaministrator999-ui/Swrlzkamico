// §E v11.127 — final-workspace boot gate. Do not reveal an obsolete
// default editor while the newer toolbars, project and authored scene restore.
(function se127InstallBootGate(){
 const ready=()=>document.documentElement.classList.add('se127-editor-ready');
 const first=performance.now();
 let quietSince=first,lastSignature='',done=false,loaded=document.readyState==='complete';
 const currentSignature=()=>{
  let project='',count=0;
  try{
   project=String(currentProject?.name||currentProject?.displayName||'');
   count=Array.isArray(actors)?actors.length:0;
  }catch(e){}
  const toolbar=document.getElementById('mainToolbar')||
    document.querySelector('.app-menu')||document.getElementById('editorTopMenu');
  const view=document.getElementById('viewLabel');
  return [project,count,view?.textContent?.trim().slice(0,90),
   toolbar?.textContent?.trim().slice(0,140),document.body?.clientWidth].join('|');
 };
 const onLoad=()=>{loaded=true;quietSince=performance.now();};
 if(!loaded)window.addEventListener('load',onLoad,{once:true});
 let interval=null,watchdog=null;
 function finish(){
  if(done)return;done=true;
  clearInterval(interval);clearTimeout(watchdog);
  window.removeEventListener('load',onLoad);
  ready();
 }
 // The existing restoration is synchronous+queued work, not a single hook.
 // Observe only project/UI signatures, avoiding canvas animation churn.
 interval=setInterval(()=>{
  const now=performance.now(),signature=currentSignature();
  if(signature!==lastSignature){lastSignature=signature;quietSince=now;}
  if(loaded&&now-first>=2600&&now-quietSince>=850)finish();
 },120);
 // A storage or shader failure must not strand users behind a splash.
 watchdog=setTimeout(finish,11000);
})();
