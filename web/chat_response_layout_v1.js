(()=>{'use strict';
if(window.__swrlzResponseLayoutV1Installed)return;window.__swrlzResponseLayoutV1Installed=true;
function fix(node){if(!node?.matches?.('.message.assistant'))return;const body=node.querySelector('.message-body'),label=body?.querySelector('.message-label'),trace=body?.querySelector('.trace'),bubble=body?.querySelector('.bubble'),avatar=node.querySelector('.avatar');if(!body||!label||!bubble)return;
  let identity=node.querySelector('.swrlz-assistant-identity');if(!identity){identity=document.createElement('div');identity.className='swrlz-assistant-identity';body.insertBefore(identity,label);if(avatar)identity.appendChild(avatar);identity.appendChild(label)}else{if(avatar&&avatar.parentElement!==identity)identity.prepend(avatar);if(label.parentElement!==identity)identity.appendChild(label)}
  if(trace&&trace.nextElementSibling!==identity)body.insertBefore(trace,identity);
  if(identity.nextElementSibling!==bubble)body.insertBefore(bubble,identity.nextSibling);
  if(avatar&&!avatar.querySelector('.swrlz-companion-fallback')){const fallback=document.createElement('span');fallback.className='swrlz-companion-fallback';fallback.textContent='🐉';fallback.setAttribute('aria-hidden','true');avatar.appendChild(fallback)}
}
function fixAll(root=document){root.querySelectorAll?.('.message.assistant').forEach(fix)}
const obs=new MutationObserver(()=>fixAll());function boot(){fixAll();const stack=document.querySelector('#messageStack');if(stack)obs.observe(stack,{childList:true,subtree:true});window.addEventListener('swrlz-theme-change',()=>setTimeout(fixAll,0))}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
