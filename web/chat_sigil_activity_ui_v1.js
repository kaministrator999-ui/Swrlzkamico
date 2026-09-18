(()=>{"use strict";
if(window.__swrlzSigilActivityUiV1)return;
const CONTRACT="sigil-activity-ui-v1";window.__swrlzSigilActivityUiV1={version:1,contract:CONTRACT};
const RESPONSE="𓆩𓆩⁽§⁾𓆪wyrlz𓆪",COMPACT="𓆩𓆩⁽§⁾𓆪wyrlz𓆪",FULL="𓆩𓆩⁽§⁾𓆪wyrlz𓆪",SEND="〘§〙";
function clock(at){if(!Number.isFinite(Number(at))||Number(at)<=0)return"";try{return new Intl.DateTimeFormat(undefined,{hour:"numeric",minute:"2-digit",second:"2-digit"}).format(new Date(Number(at)))}catch(_){return""}}
function elapsed(at,start){const a=Number(at||0),s=Number(start||0);if(!a||!s||a<s)return"";const ms=a-s;return ms<1000?`+${ms}ms`:`+${(ms/1000).toFixed(ms<10000?2:1)}s`}
function decorate(article,message){if(message?.role!=="assistant")return article;const who=article.querySelector(".message-label strong");if(who)who.textContent=RESPONSE;const details=article.querySelector("details.trace");if(details&&Array.isArray(message.meta?.trail)){const items=details.querySelectorAll(".trace-item"),steps=message.meta.trail.slice(-12),start=Number(message.createdAt||steps[0]?.at||0);items.forEach((item,index)=>{const step=steps[index];if(!step)return;const stamp=clock(step.at),delta=elapsed(step.at,start);if(stamp||delta){const time=document.createElement("span");time.className="swrlz-activity-time";time.textContent=[stamp,delta].filter(Boolean).join(" · ");time.style.cssText="display:block;font-size:10px;opacity:.72;margin-bottom:2px;font-variant-numeric:tabular-nums";item.prepend(time)}});if(["complete","failed","cancelled"].includes(String(message.state||"").toLowerCase()))details.dataset.terminal="true"}return article}
try{const base=renderMessage;renderMessage=function(message){return decorate(base(message),message)}}catch(_){ }
function paintStatic(){document.querySelectorAll(".brand-copy strong").forEach(el=>el.textContent=FULL);const send=document.querySelector("#sendButton");if(send&&!send.classList.contains("stop")){send.replaceChildren(document.createTextNode(SEND));send.setAttribute("aria-label","Send message");send.title=`Send message · ${COMPACT}`}}
const observer=new MutationObserver(()=>paintStatic());observer.observe(document.documentElement,{subtree:true,childList:true});paintStatic();
window.addEventListener("swrlz:canonical-turn-terminal",()=>setTimeout(paintStatic,0));
})();
