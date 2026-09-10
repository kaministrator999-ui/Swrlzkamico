(()=>{"use strict";
const UI_VERSION='1.4.4';
const apply=()=>{
  const title=document.querySelector('#nodeTitle');
  const detail=document.querySelector('#nodeDetail');
  const light=document.querySelector('#nodeLight');
  if(!title||!detail||!light)return;
  let last=null;
  let painting=false;
  const paint=()=>{
    if(!last||painting)return;
    painting=true;
    light.classList.remove('ready','error');
    if(last.ready){
      light.classList.add('ready');
      title.textContent='Local LALM ready';
      detail.textContent=last.detail||'R39 resident · native backend';
    }else if(last.error){
      light.classList.add('error');
      title.textContent='Local LALM unavailable';
      detail.textContent=last.detail||'Check LALM status';
    }else{
      title.textContent='Local LALM warming';
      detail.textContent=last.detail||'R39 is being prepared';
    }
    painting=false;
  };
  const refresh=async()=>{
    try{
      const r=await fetch('/api/lalm/status',{cache:'no-store'});
      if(!r.ok)throw new Error(`HTTP ${r.status}`);
      const s=await r.json();
      const ready=Boolean(s?.readiness?.interactiveReady);
      const error=s?.readiness?.ok===false;
      last={ready,error,detail:ready?'R39 resident · native backend':error?(s?.readiness?.detail||s?.readiness?.code||'Check LALM status'):'R39 is being prepared'};
      paint();
    }catch(e){
      last={ready:false,error:true,detail:'LALM status unavailable'};
      paint();
    }
  };
  const observer=new MutationObserver(()=>paint());
  observer.observe(title,{childList:true,characterData:true,subtree:true});
  observer.observe(detail,{childList:true,characterData:true,subtree:true});
  refresh();
  window.setInterval(refresh,15000);
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',apply,{once:true});
else apply();
})();