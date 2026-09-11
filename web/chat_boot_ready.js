(()=>{"use strict";
const reveal=()=>window.__swrlzChatReveal?.();
const settleArt=async()=>{
  if(document.body?.getAttribute('data-swrlz-theme')!=='ice-dragon')return;
  const art=window.__swrlzIceDragonArtReady;
  if(!art||typeof art.then!=='function')return;
  await Promise.race([art,new Promise(resolve=>setTimeout(resolve,700))]);
};
const ready=async()=>{await settleArt();requestAnimationFrame(()=>requestAnimationFrame(reveal))};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
})();
