(()=>{"use strict";
const root=document.documentElement;
const body=document.body;
const START=performance.now();
const THEME_KEY='swrlz.chat.theme';
const CACHE_NAME='swrlz-static-theme-v6';
const DIRECT_WALLPAPER='https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/main/file_00000000b13c81f5a7f9fe99c0264ef0.png?v=20260913i';
const LEGACY_KEYS=['swrlz.theme.iceDragon.adultPreview.v2','swrlz.theme.iceDragon.companionPreview.v2','swrlz.theme.iceDragon.companionPreview.v3'];
const CRITICAL_STYLE_ID='swrlz-canonical-first-paint-v4';
let theme='ice-dragon';
try{
  theme=localStorage.getItem(THEME_KEY)||'ice-dragon';
  localStorage.setItem(THEME_KEY,theme);
  for(const key of LEGACY_KEYS)localStorage.removeItem(key);
}catch(_){}
if(!document.getElementById(CRITICAL_STYLE_ID)){
  const style=document.createElement('style');style.id=CRITICAL_STYLE_ID;style.textContent=`
  body[data-swrlz-theme="ice-dragon"] .workspace{background-color:#010812!important}
  body[data-swrlz-theme="ice-dragon"] .messages{background:transparent!important}
  body[data-swrlz-theme="ice-dragon"] .composer-shell{background:rgba(82,140,190,.10)!important;backdrop-filter:blur(9px) saturate(114%)!important;-webkit-backdrop-filter:blur(9px) saturate(114%)!important}
  body[data-swrlz-theme="ice-dragon"] .composer-box{background:rgba(3,15,27,.68)!important;backdrop-filter:blur(8px) saturate(116%)!important;-webkit-backdrop-filter:blur(8px) saturate(116%)!important}
  body[data-swrlz-theme="ice-dragon"] .message.user .bubble{backdrop-filter:blur(4px) saturate(112%)!important;-webkit-backdrop-filter:blur(4px) saturate(112%)!important}
  body[data-swrlz-theme="ice-dragon"] .message.assistant .bubble{backdrop-filter:blur(5px) saturate(114%)!important;-webkit-backdrop-filter:blur(5px) saturate(114%)!important}`;document.head.appendChild(style);
}
if(theme==='ice-dragon')body?.setAttribute('data-swrlz-theme','ice-dragon');else body?.removeAttribute('data-swrlz-theme');
root.classList.add('swrlz-frontend-local-ready','swrlz-chat-ready');
window.SWRLZFrontend=Object.freeze({contractId:'swrlz_frontend_first_v7',cacheName:CACHE_NAME,bootStartedAt:START,initialTheme:theme,fastWallpaper:false,fastCompanion:false,directWallpaper:DIRECT_WALLPAPER,legacyImageHydration:false});
window.dispatchEvent(new CustomEvent('swrlz-frontend-ready',{detail:{theme,cacheName:CACHE_NAME,fastWallpaper:false,fastCompanion:false,at:performance.now()}}));
})();