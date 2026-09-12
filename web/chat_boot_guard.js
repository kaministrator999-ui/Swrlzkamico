(()=>{"use strict";
const root=document.documentElement;
const READY='swrlz-chat-ready';
try{if(localStorage.getItem('swrlz.chat.theme')==='ice-dragon')document.body?.setAttribute('data-swrlz-theme','ice-dragon')}catch(_){}
window.__swrlzChatBootStarted=performance.now();
window.__swrlzChatReveal=()=>root.classList.add(READY);
requestAnimationFrame(()=>window.__swrlzChatReveal?.());
})();
