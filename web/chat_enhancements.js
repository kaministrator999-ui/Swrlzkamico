(()=>{"use strict";
const UI_VERSION='1.4.6';
const apply=()=>{
  const title=document.querySelector('#nodeTitle');
  const detail=document.querySelector('#nodeDetail');
  const light=document.querySelector('#nodeLight');
  if(!title||!detail||!light)return;
  const refresh=async()=>{
    try{
      const r=await fetch('/api/lalm/status',{cache:'no-store'});
      if(!r.ok)throw new Error(`HTTP ${r.status}`);
      const s=await r.json();
      const ready=Boolean(s?.readiness?.interactiveReady);
      const error=s?.readiness?.ok===false;
      light.classList.remove('ready','error');
      if(ready){
        light.classList.add('ready');
        if(title.textContent!=='Local LALM ready')title.textContent='Local LALM ready';
        const value='R39 resident · native backend';
        if(detail.textContent!==value)detail.textContent=value;
      }else if(error){
        light.classList.add('error');
        const value='Local LALM unavailable';
        if(title.textContent!==value)title.textContent=value;
        const reason=String(s?.readiness?.detail||s?.readiness?.code||'Check LALM status');
        if(detail.textContent!==reason)detail.textContent=reason;
      }else{
        const value='Local LALM warming';
        if(title.textContent!==value)title.textContent=value;
        const reason='R39 is being prepared';
        if(detail.textContent!==reason)detail.textContent=reason;
      }
    }catch(_){
      light.classList.remove('ready');
      light.classList.add('error');
      if(title.textContent!=='Local LALM unavailable')title.textContent='Local LALM unavailable';
      if(detail.textContent!=='LALM status unavailable')detail.textContent='LALM status unavailable';
    }
  };
  refresh();
  window.setInterval(refresh,15000);
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',apply,{once:true});
else apply();
})();