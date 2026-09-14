(()=>{'use strict';
if(window.__swrlzThreadBrandV1Installed)return;window.__swrlzThreadBrandV1Installed=true;
const ID='swrlz-thread-brand';
const getStack=()=>document.querySelector('#messageStack')||document.querySelector('.message-stack');
function ensure(){const stack=getStack();if(!stack)return;let brand=stack.querySelector(`#${ID}`);if(!brand){brand=document.createElement('div');brand.id=ID;brand.className='swrlz-thread-brand';brand.setAttribute('aria-hidden','true');brand.innerHTML='<span>§wyrlz</span>'}if(stack.firstElementChild!==brand)stack.insertBefore(brand,stack.firstElementChild)}
function boot(){ensure();new MutationObserver(()=>ensure()).observe(document.documentElement,{childList:true,subtree:true});document.addEventListener('click',e=>{if(e.target.closest?.('.new-chat,.thread'))requestAnimationFrame(ensure)},true);['swrlz:thread-change','swrlz:thread-loaded','swrlz:new-thread','swrlz:transcript-sync','swrlz:chat-functional-ready'].forEach(name=>window.addEventListener(name,()=>requestAnimationFrame(ensure)));window.addEventListener('pageshow',()=>requestAnimationFrame(ensure))}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();