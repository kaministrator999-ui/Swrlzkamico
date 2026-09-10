(()=>{
"use strict";
const HOT="/api/chat/assets/chat_stream_focus.js";
if(window.__swrlzHotStreamFocusBoot)return;
window.__swrlzHotStreamFocusBoot=true;
fetch(HOT,{credentials:"same-origin",cache:"no-store"})
  .then(r=>{if(!r.ok)throw Error(`HOT_STREAM_FOCUS_ASSET_${r.status}`);return r.text()})
  .then(code=>{const s=document.createElement("script");s.textContent=`//# sourceURL=${HOT}\n${code}`;document.head.append(s)})
  .catch(error=>{console.warn("§wyrlz hot stream-focus asset unavailable",error)});
})();
