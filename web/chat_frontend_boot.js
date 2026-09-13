(()=>{"use strict";
const root=document.documentElement;
const body=document.body;
const START=performance.now();
const THEME_KEY='swrlz.chat.theme';
const CACHE_NAME='swrlz-static-theme-v3';
const FAST_SOURCE_KEY='swrlz.theme.iceDragon.adultPreview.v2';
const FAST_COMPANION_KEY='swrlz.theme.iceDragon.companionPreview.v2';
const DIRECT_WALLPAPER='https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/main/file_00000000b13c81f5a7f9fe99c0264ef0.png?v=20260913g';
const CRITICAL_STYLE_ID='swrlz-canonical-first-paint-v1';
let theme='ice-dragon';let fastWallpaper=false;let fastCompanion=false;
try{theme=localStorage.getItem(THEME_KEY)||'ice-dragon';if(!localStorage.getItem(THEME_KEY))localStorage.setItem(THEME_KEY,theme)}catch(_){}
if(!document.getElementById(CRITICAL_STYLE_ID)){
  const style=document.createElement('style');style.id=CRITICAL_STYLE_ID;style.textContent=`
  body[data-swrlz-theme="ice-dragon"] .composer-shell{background:rgba(1,7,15,.16)!important;backdrop-filter:blur(18px) saturate(118%)!important;-webkit-backdrop-filter:blur(18px) saturate(118%)!important}
  body[data-swrlz-theme="ice-dragon"] .composer-box{background:rgba(4,17,30,.48)!important;backdrop-filter:blur(18px) saturate(122%)!important;-webkit-backdrop-filter:blur(18px) saturate(122%)!important}
  body[data-swrlz-theme="ice-dragon"] .message-stack{position:relative!important;isolation:isolate!important}
  body[data-swrlz-theme="ice-dragon"] .message-stack::before{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;background:linear-gradient(180deg,rgba(1,7,16,.18),rgba(1,8,18,.28) 55%,rgba(1,6,14,.46));backdrop-filter:blur(1.5px);-webkit-backdrop-filter:blur(1.5px)}
  body[data-swrlz-theme="ice-dragon"] .welcome p{color:#d8eef8!important;text-shadow:0 2px 12px rgba(0,0,0,.95),0 0 4px rgba(0,0,0,.8)!important}
  body[data-swrlz-theme="ice-dragon"] .messages{background-position:50% 42%!important;background-size:cover!important;background-repeat:no-repeat!important}
  `;document.head.appendChild(style);
}
if(theme==='ice-dragon'){
  body?.setAttribute('data-swrlz-theme','ice-dragon');
  try{
    const messages=document.querySelector('.messages');
    const wallpaper=localStorage.getItem(FAST_SOURCE_KEY)||'';
    const source=(wallpaper.startsWith('data:image/')&&wallpaper.length>100000)?wallpaper:DIRECT_WALLPAPER;
    if(messages){messages.style.setProperty('background-image',`url("${source}")`,'important');messages.style.setProperty('background-position','50% 42%','important');messages.style.setProperty('background-size','cover','important');messages.style.setProperty('background-repeat','no-repeat','important');messages.style.setProperty('background-color','#010812','important');fastWallpaper=true;root.classList.add('swrlz-frontend-wallpaper-ready')}
    const companion=localStorage.getItem(FAST_COMPANION_KEY)||'';if(companion.startsWith('data:image/')&&companion.length>1000){body?.style.setProperty('--ice-dragon-companion',`url("${companion}")`);fastCompanion=true;root.classList.add('swrlz-frontend-companion-ready')}
  }catch(_){}
}else body?.removeAttribute('data-swrlz-theme');
root.classList.add('swrlz-frontend-local-ready','swrlz-chat-ready');
window.SWRLZFrontend=Object.freeze({contractId:'swrlz_frontend_first_v4',cacheName:CACHE_NAME,bootStartedAt:START,initialTheme:theme,fastWallpaper,fastCompanion,directWallpaper:DIRECT_WALLPAPER});
window.dispatchEvent(new CustomEvent('swrlz-frontend-ready',{detail:{theme,cacheName:CACHE_NAME,fastWallpaper,fastCompanion,at:performance.now()}}));
})();