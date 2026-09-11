(()=>{"use strict";
const RAW_ROOT="https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/runtime/";
const INDEX_URL=`${RAW_ROOT}VERSION.txt`;
const LALM_CACHE_KEY="swrlzLalmReadinessV1";
const LALM_CACHE_TTL_MS=10*60*1000;
const parseKV=(text)=>Object.fromEntries(String(text||"").split(/\r?\n/).map(x=>x.trim()).filter(x=>x&&!x.startsWith("#")&&x.includes("=")).map(x=>{const i=x.indexOf("=");return [x.slice(0,i).trim(),x.slice(i+1).trim()];}));
const fetchText=(url)=>fetch(`${url}${url.includes("?")?"&":"?"}ts=${Date.now()}`,{cache:"no-store"}).then(r=>r.ok?r.text():Promise.reject(new Error(`HTTP ${r.status}`)));
const apply=()=>{
  const foot=document.querySelector(".sidebar-foot");
  if(!foot)return;
  let line=document.querySelector("#swrlzChatVersion");
  if(!line){line=document.createElement("div");line.id="swrlzChatVersion";line.className="swrlz-version-line";line.style.cssText="padding:4px 9px 2px;color:var(--muted);font-size:10px;letter-spacing:.05em;opacity:.9;line-height:1.45;";foot.appendChild(line);}
  const renderVersions=(mods={})=>{const parts=[];if(mods.WEB_CHAT?.VERSION)parts.push(`Chat v${mods.WEB_CHAT.VERSION}`);if(mods.STREAM_CONTRACT?.VERSION)parts.push(`Stream ${mods.STREAM_CONTRACT.VERSION}`);if(mods.SERVER_RUNTIME?.VERSION)parts.push(`Server runtime v${mods.SERVER_RUNTIME.VERSION}`);if(mods.LALM_UI?.VERSION)parts.push(`LALM v${mods.LALM_UI.VERSION}`);const text=parts.join(" · ");if(text&&line.textContent!==text)line.textContent=text;};
  const loadVersions=async()=>{try{const index=parseKV(await fetchText(INDEX_URL));const keys=["WEB_CHAT","STREAM_CONTRACT","SERVER_RUNTIME","LALM_UI"];const pairs=await Promise.all(keys.map(async key=>{const path=index[key];if(!path)return [key,null];return [key,parseKV(await fetchText(`${RAW_ROOT}${path}`))];}));renderVersions(Object.fromEntries(pairs));}catch(_){if(!line.textContent)line.textContent="Version registry unavailable";}};
  const els=()=>({title:document.querySelector("#nodeTitle"),detail:document.querySelector("#nodeDetail"),light:document.querySelector("#nodeLight"),pill:document.querySelector("#statusPill"),pillText:document.querySelector("#statusText")});
  const paintState=(kind,detailText)=>{const {title,detail,light,pill,pillText}=els();if(!title||!detail||!light)return;light.classList.remove("ready","error");if(pill)pill.classList.remove("ready","error");if(kind==="ready"){light.classList.add("ready");if(pill)pill.classList.add("ready");if(pillText&&pillText.textContent!=="LALM ready")pillText.textContent="LALM ready";if(title.textContent!=="Local LALM ready")title.textContent="Local LALM ready";if(detail.textContent!=="R39 resident · native backend")detail.textContent="R39 resident · native backend";}else if(kind==="error"){light.classList.add("error");if(pill)pill.classList.add("error");if(pillText&&pillText.textContent!=="LALM unavailable")pillText.textContent="LALM unavailable";if(title.textContent!=="Local LALM unavailable")title.textContent="Local LALM unavailable";const value=detailText||"Check LALM status";if(detail.textContent!==value)detail.textContent=value;}else{if(pillText&&pillText.textContent!=="LALM warming")pillText.textContent="LALM warming";if(title.textContent!=="Local LALM warming")title.textContent="Local LALM warming";if(detail.textContent!=="R39 is being prepared")detail.textContent="R39 is being prepared";}};
  const readCached=()=>{try{const c=JSON.parse(sessionStorage.getItem(LALM_CACHE_KEY)||"null");if(c&&c.ready===true&&Date.now()-Number(c.at||0)<=LALM_CACHE_TTL_MS){paintState("ready");return true;}}catch(_){}return false;};
  const paintLalm=async()=>{try{const r=await fetch("/api/lalm/status",{cache:"no-store"});if(!r.ok)throw new Error(`HTTP ${r.status}`);const s=await r.json();const ready=Boolean(s?.readiness?.interactiveReady);const failed=s?.readiness?.ok===false;if(ready){paintState("ready");try{sessionStorage.setItem(LALM_CACHE_KEY,JSON.stringify({ready:true,at:Date.now()}));}catch(_){}}else if(failed){paintState("error",String(s?.readiness?.detail||s?.readiness?.code||"Check LALM status"));try{sessionStorage.removeItem(LALM_CACHE_KEY);}catch(_){}}else{paintState("warming");}}catch(_){paintState("error","LALM status unavailable");}};
  loadVersions();
  const hadFreshCache=readCached();
  if(!hadFreshCache)paintState("warming");
  paintLalm();
  window.setInterval(paintLalm,60000);
  window.addEventListener("focus",paintLalm);
};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",apply,{once:true});else apply();
})();
