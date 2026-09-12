(()=>{"use strict";
const reveal=()=>window.__swrlzChatReveal?.();
const ready=()=>requestAnimationFrame(()=>requestAnimationFrame(reveal));
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
})();
