(()=>{"use strict";
const UI_VERSION="1.3.5";
const ADMIN_KEY="swrlzAdminToken";
const CHAT_TOKEN_KEY="swrlz.vercel.chat.token.v1";
const SESSION_KEY="swrlz.vercel.chat.admin-session.v1";
const SESSION_MARKER="__ADMIN_SESSION_AUTHORIZED__";
let session=sessionStorage.getItem(SESSION_KEY)||"";
const nativeFetch=window.fetch.bind(window);
function isChatRequest(input){try{const raw=typeof input==="string"?input:input.url;const u=new URL(raw,location.href);return u.origin===location.origin&&(u.pathname==="/api/chat"||u.pathname.startsWith("/api/chat/"));}catch(_){return false}}
window.fetch=function(input,init={}){if(session&&isChatRequest(input)){const headers=new Headers(init.headers||{});headers.set("X-SWRLZ-Chat-Session",session);init={...init,headers};}return nativeFetch(input,init)};
function paintReceipt(){const v=document.querySelector("#swrlzVersionLine");if(v){const current=v.textContent||"";const server=(current.match(/SERVER v([^·\s]+)/)||[])[1]||"…";v.textContent=`CHAT v${UI_VERSION} · SERVER v${server}`;}const field=document.querySelector("#accessToken")?.closest(".field");if(field&&session){field.dataset.adminSession="true";const small=field.querySelector("small");if(small)small.textContent="Admin-authorized ephemeral Chat session active. The permanent Chat secret stays server-side. Manual Chat token remains available as fallback.";}}
async function bootstrap(){const admin=(sessionStorage.getItem(ADMIN_KEY)||"").trim();if(!admin){paintReceipt();return false}try{const r=await nativeFetch("/api/chat/admin-session",{method:"POST",headers:{"X-SWRLZ-Admin-Token":admin},cache:"no-store"});const j=await r.json().catch(()=>({}));if(!r.ok||!j.session)throw Error(j.detail||`HTTP ${r.status}`);session=String(j.session);sessionStorage.setItem(SESSION_KEY,session);sessionStorage.setItem(CHAT_TOKEN_KEY,SESSION_MARKER);paintReceipt();try{if(typeof refreshStatus==="function")refreshStatus()}catch(_){}return true}catch(_){session="";sessionStorage.removeItem(SESSION_KEY);paintReceipt();return false}}
const oldSession=session;if(oldSession){sessionStorage.setItem(CHAT_TOKEN_KEY,SESSION_MARKER);paintReceipt()}bootstrap();setInterval(paintReceipt,1000);
})();
