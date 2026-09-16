(()=>{"use strict";
if(window.__swrlzActivityExpansionStateInstalled)return;
window.__swrlzActivityExpansionStateInstalled=true;
const CONTRACT='activity-expansion-state-v2';
function dbg(message,data={}){try{window.__swrlzClientDebug?.('activity-log',message,{contract:CONTRACT,...data})}catch(_){}}
function messageById(id){try{for(const thread of state?.threads||[]){const message=(thread?.messages||[]).find(m=>String(m?.id||'')===String(id||''));if(message)return message}}catch(_){ }return null}
function desiredOpen(message){if(message?.meta&&typeof message.meta.activityExpanded==='boolean')return message.meta.activityExpanded;return String(message?.state||'')==='streaming'}

// Render-time ownership: apply the saved user preference while the message DOM is
// being constructed. No MutationObserver, no post-render open/close chase.
try{
  const baseRenderMessage=renderMessage;
  renderMessage=function(message){
    const article=baseRenderMessage(message);
    if(message?.role==='assistant'){
      const details=article.querySelector('details.trace');
      if(details)details.open=desiredOpen(message);
    }
    return article;
  };
}catch(error){dbg('render-hook-unavailable',{error:String(error?.message||error)})}

// One delegated native toggle listener is the only writer of the user's choice.
// Ignore detached nodes so rerender teardown cannot manufacture preferences.
document.addEventListener('toggle',(event)=>{
  const details=event.target;
  if(!(details instanceof HTMLDetailsElement)||!details.classList.contains('trace')||!details.isConnected)return;
  const article=details.closest('.message[data-message-id]');
  const current=messageById(article?.dataset?.messageId);
  if(!current)return;
  const wanted=desiredOpen(current);
  // A render-created details element may emit a toggle for its initial open state.
  // If it merely matches existing authority, it is not a user mutation.
  if(details.open===wanted)return;
  current.meta=current.meta||{};
  current.meta.activityExpanded=details.open;
  current.meta.activityExpandedAt=Date.now();
  try{typeof saveState==='function'&&saveState()}catch(_){ }
  dbg('user-expansion-changed',{messageId:String(current.id||''),requestId:String(current.meta?.requestId||''),open:details.open});
},true);

window.__swrlzActivityExpansionState={version:2,contract:CONTRACT,policy:'single-owner-render-time-activity-expansion-no-mutation-observer'};
})();
