(()=>{'use strict';
if(window.__swrlzResponseLayoutV1Installed)return;window.__swrlzResponseLayoutV1Installed=true;
const root=document.documentElement;
function fix(node){if(!node?.matches?.('.message.assistant'))return;const body=node.querySelector('.message-body'),label=body?.querySelector('.message-label'),trace=body?.querySelector('.trace'),bubble=body?.querySelector('.bubble'),avatar=node.querySelector('.avatar');if(!body||!label||!bubble)return;
  let identity=node.querySelector('.swrlz-assistant-identity');if(!identity){identity=document.createElement('div');identity.className='swrlz-assistant-identity';body.insertBefore(identity,label);if(avatar)identity.appendChild(avatar);identity.appendChild(label)}else{if(avatar&&avatar.parentElement!==identity)identity.prepend(avatar);if(label.parentElement!==identity)identity.appendChild(label)}
  if(trace&&trace.nextElementSibling!==identity)body.insertBefore(trace,identity);
  if(identity.nextElementSibling!==bubble)body.insertBefore(bubble,identity.nextSibling);
  avatar?.querySelector('.swrlz-companion-fallback')?.remove();
}
function fixAll(scope=document){scope.querySelectorAll?.('.message.assistant').forEach(fix)}
const obs=new MutationObserver(records=>{for(const record of records){for(const node of record.addedNodes){if(node.nodeType!==1)continue;if(node.matches?.('.message.assistant'))fix(node);else fixAll(node)}}});
function boot(){try{fixAll();const stack=document.querySelector('#messageStack');if(stack)obs.observe(stack,{childList:true,subtree:true});window.addEventListener('swrlz-theme-change',()=>requestAnimationFrame(()=>fixAll()))}finally{root.classList.add('swrlz-response-layout-ready')}}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
