(()=>{"use strict";
const CHAT_VERSION="1.4.7";
const STREAM_VERSION="V2";
const apply=()=>{
  const foot=document.querySelector(".sidebar-foot");
  if(!foot)return;
  let line=document.querySelector("#swrlzChatVersion");
  if(!line){
    line=document.createElement("div");
    line.id="swrlzChatVersion";
    line.className="swrlz-version-line";
    line.style.cssText="padding:4px 9px 2px;color:var(--muted);font-size:10px;letter-spacing:.05em;opacity:.9;line-height:1.45;";
    foot.appendChild(line);
  }
  const render=(serverVersion,lalmVersion)=>{
    const parts=[`Chat v${CHAT_VERSION}`,`Stream ${STREAM_VERSION}`];
    if(serverVersion)parts.push(`Server v${serverVersion}`);
    if(lalmVersion)parts.push(`LALM v${lalmVersion}`);
    const text=parts.join(" · ");
    if(line.textContent!==text)line.textContent=text;
  };
  const paintLalm=async()=>{
    const title=document.querySelector("#nodeTitle");
    const detail=document.querySelector("#nodeDetail");
    const light=document.querySelector("#nodeLight");
    const pill=document.querySelector("#statusPill");
    const pillText=document.querySelector("#statusText");
    if(!title||!detail||!light)return;
    try{
      const r=await fetch("/api/lalm/status",{cache:"no-store"});
      if(!r.ok)throw new Error(`HTTP ${r.status}`);
      const s=await r.json();
      const ready=Boolean(s?.readiness?.interactiveReady);
      const failed=s?.readiness?.ok===false;
      light.classList.remove("ready","error");
      if(pill){pill.classList.remove("ready","error");}
      if(ready){
        light.classList.add("ready");
        if(pill)pill.classList.add("ready");
        if(pillText&&pillText.textContent!=="LALM ready")pillText.textContent="LALM ready";
        if(title.textContent!=="Local LALM ready")title.textContent="Local LALM ready";
        if(detail.textContent!=="R39 resident · native backend")detail.textContent="R39 resident · native backend";
      }else if(failed){
        light.classList.add("error");
        if(pill)pill.classList.add("error");
        if(pillText&&pillText.textContent!=="LALM unavailable")pillText.textContent="LALM unavailable";
        if(title.textContent!=="Local LALM unavailable")title.textContent="Local LALM unavailable";
        const value=String(s?.readiness?.detail||s?.readiness?.code||"Check LALM status");
        if(detail.textContent!==value)detail.textContent=value;
      }else{
        if(pillText&&pillText.textContent!=="LALM warming")pillText.textContent="LALM warming";
        if(title.textContent!=="Local LALM warming")title.textContent="Local LALM warming";
        if(detail.textContent!=="R39 is being prepared")detail.textContent="R39 is being prepared";
      }
    }catch(_){
      light.classList.remove("ready");
      light.classList.add("error");
      if(pill){pill.classList.remove("ready");pill.classList.add("error");}
      if(pillText&&pillText.textContent!=="LALM unavailable")pillText.textContent="LALM unavailable";
      if(title.textContent!=="Local LALM unavailable")title.textContent="Local LALM unavailable";
      if(detail.textContent!=="LALM status unavailable")detail.textContent="LALM status unavailable";
    }
  };
  render();
  Promise.allSettled([
    fetch("/api/server/status",{cache:"no-store"}).then(r=>r.ok?r.json():null),
    fetch("/api/lalm/status",{cache:"no-store"}).then(r=>r.ok?r.json():null)
  ]).then(([server,lalm])=>{
    const serverVersion=server.status==="fulfilled"&&server.value?.version?server.value.version:"";
    const lalmVersion=lalm.status==="fulfilled"&&lalm.value?.uiVersion?lalm.value.uiVersion:"";
    render(serverVersion,lalmVersion);
  });
  paintLalm();
  window.setInterval(paintLalm,15000);
};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",apply,{once:true});
else apply();
})();