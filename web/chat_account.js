(()=>{
"use strict";
if(window.__swrlzHotChatBootstrap)return;
window.__swrlzHotChatBootstrap=true;
const assets=["chat_account.js","chat_stream_focus.js"];
let loadedRevision="";
const load=name=>fetch(`/api/chat/assets/${name}`,{credentials:"same-origin",cache:"no-store"})
  .then(r=>{if(!r.ok)throw Error(`HOT_CHAT_ASSET_${name}_${r.status}`);return r.text()})
  .then(code=>{const s=document.createElement("script");s.textContent=`//# sourceURL=/api/chat/assets/${name}\n${code}`;document.head.append(s)});
const refreshIfChanged=()=>fetch("/api/hot/status",{credentials:"same-origin",cache:"no-store"})
  .then(r=>r.ok?r.json():null)
  .then(status=>{
    const revision=String(status?.activeRevision||status?.autoSync?.revision||"");
    if(!revision)return;
    if(loadedRevision && revision!==loadedRevision){window.location.reload();return;}
    loadedRevision=revision;
  }).catch(()=>{});
Promise.resolve()
  .then(()=>load("chat_account.js"))
  .then(()=>load("chat_stream_focus.js"))
  .then(()=>refreshIfChanged())
  .catch(error=>console.warn("§wyrlz hot chat assets unavailable",error));
setInterval(refreshIfChanged,5000);
})();