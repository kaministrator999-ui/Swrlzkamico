(()=>{"use strict";
if(window.__swrlzActivityExpansionStateInstalled)return;
window.__swrlzActivityExpansionStateInstalled=true;
const CONTRACT='activity-expansion-state-v3';
function dbg(message,data={}){try{window.__swrlzClientDebug?.('activity-log',message,{contract:CONTRACT,...data})}catch(_){}}
function messageById(id){try{for(const thread of state?.threads||[]){const message=(thread?.messages||[]).find(m=>String(m?.id||'')===String(id||''));if(message)return message}}catch(_){ }return null}
function desiredOpen(message){if(message?.meta&&typeof message.meta.activityExpanded==='boolean')return message.meta.activityExpanded;return String(message?.state||'')==='streaming'}
function persist(details,open){const article=details?.closest?.('.message[data-message-id]');const current=messageById(article?.dataset?.messageId);if(!current)return;current.meta=current.meta||{};current.meta.activityExpanded=!!open;current.meta.activityExpandedAt=Date.now();try{typeof saveState==='function'&&saveState()}catch(_){ }dbg('user-expansion-changed',{messageId:String(current.id||''),requestId:String(current.meta?.requestId||''),open:!!open})}

// Apply the saved preference while the message DOM is constructed. The browser
// never has to chase an expansion state after a render.
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

// Own the summary activation itself. Native <details> toggle notifications are
// asynchronous/coalesced, which let a fast tap race a rerender and appear to
// reopen. Prevent the native default, flip once synchronously, then persist the
// exact user choice. Keyboard activation also arrives as click.
document.addEventListener('click',(event)=>{
  const summary=event.target?.closest?.('details.trace > summary');
  if(!summary)return;
  const details=summary.parentElement;
  if(!(details instanceof HTMLDetailsElement)||!details.isConnected)return;
  event.preventDefault();
  const next=!details.open;
  details.open=next;
  persist(details,next);
},true);

window.__swrlzActivityExpansionState={version:3,contract:CONTRACT,policy:'synchronous-user-owned-summary-activation-render-time-expansion'};
})();
