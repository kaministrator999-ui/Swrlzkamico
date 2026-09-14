(()=>{"use strict";
if(window.__swrlzResponsePolishInstalled)return;
window.__swrlzResponsePolishInstalled=true;

/*
 * Mask/Human/Brain compatibility layer.
 * This file intentionally performs no semantic interpretation or prose rewriting.
 * It exists only as a stable presentation hook for other Chat/UI code that may
 * expect the response-polish lifecycle marker to be present.
 */
function polishBubble(bubble){
  if(!bubble)return;
  bubble.dataset.swrlzPresentationPolish='ready';
}
function scan(root=document){root.querySelectorAll?.('.message.assistant .bubble').forEach(polishBubble)}
function install(){
  scan();
  const target=document.querySelector('.messages')||document.querySelector('.message-stack')||document.body;
  if(!target)return;
  const observer=new MutationObserver(records=>{for(const record of records){for(const added of record.addedNodes||[]){if(added.nodeType!==1)continue;if(added.matches?.('.message.assistant .bubble'))polishBubble(added);else added.querySelectorAll?.('.message.assistant .bubble').forEach(polishBubble)}}});
  observer.observe(target,{childList:true,subtree:true});
  window.__swrlzResponsePolishObserver=observer;
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
window.__swrlzResponsePolish={version:2,policy:'presentation-hook-only-no-semantic-rewrite',polishBubble,scan};
})();