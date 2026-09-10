(()=>{"use strict";
const CHAT_VERSION="1.4.2";
const STREAM_VERSION="V2";
const apply=()=>{
  const foot=document.querySelector(".sidebar-foot");
  if(!foot)return;
  let line=document.querySelector("#swrlzChatVersion");
  if(!line){
    line=document.createElement("div");
    line.id="swrlzChatVersion";
    line.className="swrlz-version-line";
    line.style.cssText="padding:4px 9px 2px;color:var(--muted);font-size:10px;letter-spacing:.05em;opacity:.9;";
    foot.appendChild(line);
  }
  const text=`Chat v${CHAT_VERSION} · Stream ${STREAM_VERSION}`;
  if(line.textContent!==text)line.textContent=text;
};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",apply,{once:true});
else apply();
})();
