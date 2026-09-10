(()=>{
"use strict";
if(window.__swrlzHotChatBootstrap)return;
window.__swrlzHotChatBootstrap=true;
const assets=["chat_account.js","chat_stream_focus.js"];
const load=name=>fetch(`/api/chat/assets/${name}`,{credentials:"same-origin",cache:"no-store"})
  .then(r=>{if(!r.ok)throw Error(`HOT_CHAT_ASSET_${name}_${r.status}`);return r.text()})
  .then(code=>{const s=document.createElement("script");s.textContent=`//# sourceURL=/api/chat/assets/${name}\n${code}`;document.head.append(s)});
Promise.resolve()
  .then(()=>load("chat_account.js"))
  .then(()=>load("chat_stream_focus.js"))
  .catch(error=>console.warn("§wyrlz hot chat assets unavailable",error));
})();
