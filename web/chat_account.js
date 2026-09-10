(()=>{
"use strict";
const HOT="/api/chat/assets/chat_account.js";
if(window.__swrlzHotAccountBoot)return;
window.__swrlzHotAccountBoot=true;
fetch(HOT,{credentials:"same-origin",cache:"no-store"})
  .then(r=>{if(!r.ok)throw Error(`HOT_ACCOUNT_ASSET_${r.status}`);return r.text()})
  .then(code=>{const s=document.createElement("script");s.textContent=`//# sourceURL=${HOT}\n${code}`;document.head.append(s)})
  .catch(error=>{console.warn("§wyrlz hot account asset unavailable",error)});
})();
