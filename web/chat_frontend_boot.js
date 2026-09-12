(()=>{"use strict";
const root=document.documentElement;
const body=document.body;
const START=performance.now();
const THEME_KEY='swrlz.chat.theme';
const CACHE_NAME='swrlz-static-theme-v1';
let theme='default';
try{theme=localStorage.getItem(THEME_KEY)||'default'}catch(_){}
if(theme==='ice-dragon')body?.setAttribute('data-swrlz-theme','ice-dragon');
else body?.removeAttribute('data-swrlz-theme');
root.classList.add('swrlz-frontend-local-ready');
window.SWRLZFrontend=Object.freeze({contractId:'swrlz_frontend_first_v1',cacheName:CACHE_NAME,bootStartedAt:START,initialTheme:theme});
window.dispatchEvent(new CustomEvent('swrlz-frontend-ready',{detail:{theme,cacheName:CACHE_NAME,at:performance.now()}}));
})();
