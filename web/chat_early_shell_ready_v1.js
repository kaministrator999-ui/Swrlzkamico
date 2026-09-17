(()=>{"use strict";
if(window.__swrlzChatEarlyShellReadyV1)return;
const startedAt=performance.now();
let theme='ice-dragon';
try{theme=localStorage.getItem('swrlz.chat.theme')||'ice-dragon'}catch(_){ }
if(theme==='ice-dragon')document.body?.setAttribute('data-swrlz-theme','ice-dragon');else document.body?.removeAttribute('data-swrlz-theme');
document.documentElement.classList.add('swrlz-main-chat-ready');
window.__swrlzChatEarlyShellReadyV1={version:1,contract:'swrlz-mask-early-shell-ready-v1',theme,startedAt,readyAt:performance.now(),policy:'Mask shell readiness is independent of network, account hydration, reconciliation, LALM status, and decorative settlement'};
window.dispatchEvent(new CustomEvent('swrlz:main-chat-ready',{detail:{revision:'early-shell-v1',at:performance.now(),source:'early-shell'}}));
})();
