(()=>{"use strict";
const root=document.documentElement;
const body=document.body;
const START=performance.now();
const THEME_KEY='swrlz.chat.theme';
const CACHE_NAME='swrlz-static-theme-v2';
const FAST_SOURCE_KEY='swrlz.theme.iceDragon.adultPreview.v2';
const FAST_COMPANION_KEY='swrlz.theme.iceDragon.companionPreview.v2';
let theme='default';let fastWallpaper=false;let fastCompanion=false;
try{theme=localStorage.getItem(THEME_KEY)||'default'}catch(_){}
if(theme==='ice-dragon'){
  body?.setAttribute('data-swrlz-theme','ice-dragon');
  try{
    const wallpaper=localStorage.getItem(FAST_SOURCE_KEY)||'';const messages=document.querySelector('.messages');
    if(messages&&wallpaper.startsWith('data:image/')&&wallpaper.length>100000){messages.style.setProperty('background-image',`url("${wallpaper}")`,'important');messages.style.setProperty('background-position','50% 42%','important');messages.style.setProperty('background-size','cover','important');messages.style.setProperty('background-repeat','no-repeat','important');messages.style.setProperty('background-color','#010812','important');fastWallpaper=true;root.classList.add('swrlz-frontend-wallpaper-ready')}
    const companion=localStorage.getItem(FAST_COMPANION_KEY)||'';if(companion.startsWith('data:image/')&&companion.length>1000){body?.style.setProperty('--ice-dragon-companion',`url("${companion}")`);fastCompanion=true;root.classList.add('swrlz-frontend-companion-ready')}
  }catch(_){}
}else body?.removeAttribute('data-swrlz-theme');
root.classList.add('swrlz-frontend-local-ready');
window.SWRLZFrontend=Object.freeze({contractId:'swrlz_frontend_first_v3',cacheName:CACHE_NAME,bootStartedAt:START,initialTheme:theme,fastWallpaper,fastCompanion});
window.dispatchEvent(new CustomEvent('swrlz-frontend-ready',{detail:{theme,cacheName:CACHE_NAME,fastWallpaper,fastCompanion,at:performance.now()}}));
})();