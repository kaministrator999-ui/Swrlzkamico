(()=>{"use strict";
if(window.__swrlzActivityExpansionStateInstalled)return;
window.__swrlzActivityExpansionStateInstalled=true;
const CONTRACT='activity-expansion-state-v1';
function dbg(message,data={}){try{window.__swrlzClientDebug?.('activity-log',message,{contract:CONTRACT,...data})}catch(_){}}
function messageById(id){try{for(const thread of state?.threads||[]){const message=(thread?.messages||[]).find(m=>String(m?.id||'')===String(id||''));if(message)return message}}catch(_){ }return null}
function desiredOpen(message){if(message?.meta&&typeof message.meta.activityExpanded==='boolean')return message.meta.activityExpanded;return String(message?.state||'')==='streaming'}
function bind(details){if(!(details instanceof HTMLDetailsElement)||!details.classList.contains('trace'))return;const article=details.closest('.message[data-message-id]');const message=messageById(article?.dataset?.messageId);if(!message)return;const wanted=desiredOpen(message);if(details.open!==wanted){details.__swrlzProgrammaticToggle=true;details.open=wanted;queueMicrotask(()=>{details.__swrlzProgrammaticToggle=false})}if(details.dataset.swrlzExpansionBound==='1')return;details.dataset.swrlzExpansionBound='1';details.addEventListener('toggle',()=>{if(details.__swrlzProgrammaticToggle)return;const currentArticle=details.closest('.message[data-message-id]');const current=messageById(currentArticle?.dataset?.messageId);if(!current)return;current.meta=current.meta||{};current.meta.activityExpanded=details.open;current.meta.activityExpandedAt=Date.now();try{typeof saveState==='function'&&saveState()}catch(_){ }dbg('user-expansion-changed',{messageId:String(current.id||''),requestId:String(current.meta?.requestId||''),open:details.open})})}
function sync(){try{document.querySelectorAll('details.trace').forEach(bind)}catch(_){}}
let queued=false;function queue(){if(queued)return;queued=true;queueMicrotask(()=>{queued=false;sync()})}
const observer=new MutationObserver(queue);
function boot(){observer.observe(document.body,{subtree:true,childList:true});sync()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
window.__swrlzActivityExpansionState={version:1,contract:CONTRACT,sync,policy:'user-owned-activity-log-expanded-state-survives-message-rerenders-and-stream-updates'};
})();
