(()=>{"use strict";
if(window.__swrlzActivityExpansionStateInstalled)return;
window.__swrlzActivityExpansionStateInstalled=true;
const CONTRACT='activity-expansion-state-v4';
const userChoice=new Map();
function dbg(message,data={}){try{window.__swrlzClientDebug?.('activity-log',message,{contract:CONTRACT,...data})}catch(_){}}
function messageById(id){try{for(const thread of state?.threads||[]){const message=(thread?.messages||[]).find(m=>String(m?.id||'')===String(id||''));if(message)return message}}catch(_){ }return null}
function keyFor(message){const requestId=String(message?.meta?.requestId||'').trim();const messageId=String(message?.id||'').trim();return requestId?`request:${requestId}`:messageId?`message:${messageId}`:''}
function desiredOpen(message){const key=keyFor(message);if(key&&userChoice.has(key))return userChoice.get(key);if(message?.meta&&typeof message.meta.activityExpanded==='boolean')return message.meta.activityExpanded;return String(message?.state||'')==='streaming'}
function persist(details,open){const article=details?.closest?.('.message[data-message-id]');const current=messageById(article?.dataset?.messageId);if(!current)return;const key=keyFor(current);if(key)userChoice.set(key,!!open);current.meta=current.meta||{};current.meta.activityExpanded=!!open;current.meta.activityExpandedAt=Date.now();try{typeof saveState==='function'&&saveState()}catch(_){ }dbg('user-expansion-changed',{messageId:String(current.id||''),requestId:String(current.meta?.requestId||''),open:!!open,key})}

// The user's latest choice is an independent presentation authority. Streaming
// and canonical hydration can replace the message object many times, so storing
// the preference only on message.meta lets a fresh canonical object erase it.
// The request/message keyed map survives those rerenders and always wins.
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

// Own summary activation synchronously. The browser never gets a second native
// toggle, and subsequent streaming rerenders reapply the same explicit choice.
document.addEventListener('click',(event)=>{
  const summary=event.target?.closest?.('details.trace > summary');
  if(!summary)return;
  const details=summary.parentElement;
  if(!(details instanceof HTMLDetailsElement)||!details.isConnected)return;
  event.preventDefault();
  event.stopPropagation();
  const next=!details.open;
  details.open=next;
  persist(details,next);
},true);

window.__swrlzActivityExpansionState={version:4,contract:CONTRACT,policy:'user-choice-map-wins-across-streaming-and-canonical-rerenders'};
})();
