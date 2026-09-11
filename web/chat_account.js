(()=>{
"use strict";
if(window.__swrlzHotChatBootstrap)return;
window.__swrlzHotChatBootstrap=true;
const assets=["chat_account.js","chat_stream_focus.js"];
let loadedRevision="";
const load=name=>fetch(`/api/chat/assets/${name}`,{credentials:"same-origin",cache:"no-store"})
  .then(r=>{if(!r.ok)throw Error(`HOT_CHAT_ASSET_${name}_${r.status}`);return r.text()})
  .then(code=>{const s=document.createElement("script");s.textContent=`//# sourceURL=/api/chat/assets/${name}\n${code}`;document.head.append(s)});
const mountThemePack=()=>{
  if(!document.querySelector('link[data-swrlz-theme-pack="ice-dragon"]')){
    const link=document.createElement("link");
    link.rel="stylesheet";
    link.href="/themes/ice-dragon/ice-dragon-theme.css";
    link.dataset.swrlzThemePack="ice-dragon";
    document.head.append(link);
  }
  if(!document.querySelector('script[data-swrlz-theme-pack="ice-dragon"]')){
    const script=document.createElement("script");
    script.src="/themes/ice-dragon/ice-dragon-theme.js";
    script.defer=true;
    script.dataset.swrlzThemePack="ice-dragon";
    document.head.append(script);
  }
};
const refreshIfChanged=()=>fetch("/api/hot/status",{credentials:"same-origin",cache:"no-store"})
  .then(r=>r.ok?r.json():null)
  .then(status=>{
    const revision=String(status?.activeRevision||status?.autoSync?.revision||"");
    if(!revision)return;
    if(loadedRevision && revision!==loadedRevision){window.location.reload();return;}
    loadedRevision=revision;
  }).catch(()=>{});
mountThemePack();
Promise.resolve()
  .then(()=>load("chat_account.js"))
  .then(()=>load("chat_stream_focus.js"))
  .then(()=>refreshIfChanged())
  .catch(error=>console.warn("§wyrlz hot chat assets unavailable",error));
setInterval(refreshIfChanged,5000);
})();
