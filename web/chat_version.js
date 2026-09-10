(()=>{"use strict";
const CHAT_VERSION="1.4.4";
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
  render();
  Promise.allSettled([
    fetch("/api/server/status",{cache:"no-store"}).then(r=>r.ok?r.json():null),
    fetch("/api/lalm/status",{cache:"no-store"}).then(r=>r.ok?r.json():null)
  ]).then(([server,lalm])=>{
    const serverVersion=server.status==="fulfilled"&&server.value?.version?server.value.version:"";
    const lalmVersion=lalm.status==="fulfilled"&&lalm.value?.uiVersion?lalm.value.uiVersion:"";
    render(serverVersion,lalmVersion);
  });
};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",apply,{once:true});
else apply();
})();