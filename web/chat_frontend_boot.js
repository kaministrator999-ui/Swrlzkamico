(()=>{"use strict";
const root=document.documentElement;
const body=document.body;
const START=performance.now();
const THEME_KEY='swrlz.chat.theme';
const CACHE_NAME='swrlz-static-theme-v5';
const FAST_COMPANION_KEY='swrlz.theme.iceDragon.companionPreview.v2';
const LEGACY_ADULT_KEY='swrlz.theme.iceDragon.adultPreview.v2';
const DIRECT_WALLPAPER='https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/main/file_00000000b13c81f5a7f9fe99c0264ef0.png?v=20260913i';
const CRITICAL_STYLE_ID='swrlz-canonical-first-paint-v3';
let theme='ice-dragon';let fastWallpaper=false;let fastCompanion=false;
try{theme=localStorage.getItem(THEME_KEY)||'ice-dragon';localStorage.setItem(THEME_KEY,theme);localStorage.removeItem(LEGACY_ADULT_KEY)}catch(_){}
if(!document.getElementById(CRITICAL_STYLE_ID)){
  const style=document.createElement('style');style.id=CRITICAL_STYLE_ID;style.textContent=`
  body[data-swrlz-theme="ice-dragon"] .workspace{background-color:#010812!important;background-image:url("${DIRECT_WALLPAPER}")!important;background-position:50% 42%!important;background-size:cover!important;background-repeat:no-repeat!important}
  body[data-swrlz-theme="ice-dragon"] .messages{background:transparent!important}
  body[data-swrlz-theme="ice-dragon"] .composer-shell{background:rgba(82,140,190,.10)!important;backdrop-filter:blur(9px) saturate(114%)!important;-webkit-backdrop-filter:blur(9px) saturate(114%)!important}
  body[data-swrlz-theme="ice-dragon"] .composer-box{background:rgba(3,15,27,.68)!important;backdrop-filter:blur(8px) saturate(116%)!important;-webkit-backdrop-filter:blur(8px) saturate(116%)!important}
  body[data-swrlz-theme="ice-dragon"] .message.user .bubble{backdrop-filter:blur(4px) saturate(112%)!important;-webkit-backdrop-filter:blur(4px) saturate(112%)!important}
  body[data-swrlz-theme="ice-dragon"] .message.assistant .bubble{backdrop-filter:blur(5px) saturate(114%)!important;-webkit-backdrop-filter:blur(5px) saturate(114%)!important}
  body[data-swrlz-theme="ice-dragon"] .message-stack{position:relative!important;isolation:isolate!important}
  body[data-swrlz-theme="ice-dragon"] .message-stack::before{content:"";position:absolute;inset:0;z-index:0;pointer-events:none;background:linear-gradient(180deg,rgba(1,7,16,.16),rgba(1,8,18,.27) 58%,rgba(1,6,14,.44))}
  body[data-swrlz-theme="ice-dragon"] .message-stack>*{position:relative;z-index:1}
  body[data-swrlz-theme="ice-dragon"] .welcome p{color:#f1fbff!important;text-shadow:0 2px 12px rgba(0,0,0,.95),0 0 4px rgba(0,0,0,.8)!important;font-weight:520!important}
  `;document.head.appendChild(style);
}
if(theme==='ice-dragon'){
  body?.setAttribute('data-swrlz-theme','ice-dragon');
  try{
    const workspace=document.querySelector('.workspace');const messages=document.querySelector('.messages');
    if(workspace){workspace.style.setProperty('background-image',`url("${DIRECT_WALLPAPER}")`,'important');workspace.style.setProperty('background-position','50% 42%','important');workspace.style.setProperty('background-size','cover','important');workspace.style.setProperty('background-repeat','no-repeat','important');workspace.style.setProperty('background-color','#010812','important');fastWallpaper=true;root.classList.add('swrlz-frontend-wallpaper-ready')}
    if(messages){for(const key of ['background-image','background-position','background-size','background-repeat','background-color'])messages.style.removeProperty(key);messages.style.setProperty('background','transparent','important')}
    const companion=localStorage.getItem(FAST_COMPANION_KEY)||'';if(companion.startsWith('data:image/')&&companion.length>1000){body?.style.setProperty('--ice-dragon-companion',`url("${companion}")`);fastCompanion=true;root.classList.add('swrlz-frontend-companion-ready')}
  }catch(_){}
}else body?.removeAttribute('data-swrlz-theme');
root.classList.add('swrlz-frontend-local-ready','swrlz-chat-ready');
window.SWRLZFrontend=Object.freeze({contractId:'swrlz_frontend_first_v6',cacheName:CACHE_NAME,bootStartedAt:START,initialTheme:theme,fastWallpaper,fastCompanion,directWallpaper:DIRECT_WALLPAPER,legacyAdultFallback:false});
window.dispatchEvent(new CustomEvent('swrlz-frontend-ready',{detail:{theme,cacheName:CACHE_NAME,fastWallpaper,fastCompanion,at:performance.now()}}));
})();