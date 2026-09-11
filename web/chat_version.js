(()=>{"use strict";
const VERSION_REGISTRY="https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/runtime/VERSION.txt";
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
  const parseRegistry=(text)=>Object.fromEntries(String(text||"").split(/\r?\n/).map(x=>x.trim()).filter(x=>x&&!x.startsWith("#")&&x.includes("=")).map(x=>{const i=x.indexOf("=");return [x.slice(0,i).trim(),x.slice(i+1).trim()];}));
  const render=(v={})=>{
    const parts=[];
    if(v.CHAT)parts.push(`Chat v${v.CHAT}`);
    if(v.STREAM)parts.push(`Stream ${v.STREAM}`);
    if(v.SERVER_RUNTIME)parts.push(`Server runtime v${v.SERVER_RUNTIME}`);
    if(v.LALM_UI)parts.push(`LALM v${v.LALM_UI}`);
    const text=parts.join(" · ");
    if(text&&line.textContent!==text)line.textContent=text;
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
  fetch(`${VERSION_REGISTRY}?ts=${Date.now()}`,{cache:"no-store"})
    .then(r=>r.ok?r.text():Promise.reject(new Error(`HTTP ${r.status}`)))
    .then(text=>render(parseRegistry(text)))
    .catch(()=>{});
  paintLalm();
  window.setInterval(paintLalm,15000);
};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",apply,{once:true});
else apply();
})();
