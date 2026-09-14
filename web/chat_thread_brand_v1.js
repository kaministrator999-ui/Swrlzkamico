(()=>{'use strict';
if(window.__swrlzThreadBrandV1Installed)return;window.__swrlzThreadBrandV1Installed=true;
const ID='swrlz-thread-brand';
function ensure(){const stack=document.querySelector('#messageStack')||document.querySelector('.message-stack');if(!stack)return;let brand=stack.querySelector(`#${ID}`);if(!brand){brand=document.createElement('div');brand.id=ID;brand.className='swrlz-thread-brand';brand.setAttribute('aria-hidden','true');brand.textContent='§wyrlz';stack.prepend(brand)}else if(stack.firstElementChild!==brand)stack.prepend(brand)}
function boot(){ensure();const stack=document.querySelector('#messageStack')||document.querySelector('.message-stack');if(stack)new MutationObserver(()=>{if(!stack.querySelector(`#${ID}`))ensure()}).observe(stack,{childList:true});window.addEventListener('swrlz:thread-change',()=>requestAnimationFrame(ensure));window.addEventListener('swrlz:thread-loaded',()=>requestAnimationFrame(ensure));window.addEventListener('swrlz:new-thread',()=>requestAnimationFrame(ensure))}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
