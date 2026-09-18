(()=>{'use strict';
if(window.__swrlzThreadBrandV1Installed)return;window.__swrlzThreadBrandV1Installed=true;
const ID='swrlz-thread-brand';
const getMessages=()=>document.querySelector('#messages')||document.querySelector('.messages');
function ensure(){const messages=getMessages();if(!messages)return;let brand=document.getElementById(ID);if(!brand){brand=document.createElement('div');brand.id=ID;brand.className='swrlz-thread-brand';brand.setAttribute('aria-hidden','true');brand.innerHTML='<span>𓆩𓆩⁽§⁾𓆪wyrlz𓆪</span>'}if(brand.parentElement!==messages)messages.insertBefore(brand,messages.firstChild)}
function boot(){ensure();new MutationObserver(()=>ensure()).observe(document.documentElement,{childList:true,subtree:true});['swrlz:thread-change','swrlz:thread-loaded','swrlz:new-thread','swrlz:transcript-sync','swrlz:chat-functional-ready'].forEach(name=>window.addEventListener(name,()=>requestAnimationFrame(ensure)));window.addEventListener('pageshow',()=>requestAnimationFrame(ensure))}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();