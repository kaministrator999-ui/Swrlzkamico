/* SWRLZ Ice Dragon wallpaper v22 — one deferred paint, no duplicate probe/decode. */
(()=>{'use strict';
const body=document.body;
const ASSET=window.SWRLZFrontend?.directWallpaper||'https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/main/file_00000000b13c81f5a7f9fe99c0264ef0.png?v=20260913i';
const active=()=>body?.dataset.swrlzTheme==='ice-dragon';
const workspace=()=>document.querySelector('.workspace');
function paint(){
  const el=workspace();if(!el||!active())return false;
  el.style.setProperty('background-image',`url("${ASSET}")`,'important');
  el.style.setProperty('background-position','50% 42%','important');
  el.style.setProperty('background-size','cover','important');
  el.style.setProperty('background-repeat','no-repeat','important');
  el.style.setProperty('background-color','#010812','important');
  document.documentElement.classList.add('swrlz-frontend-wallpaper-ready');
  return true;
}
window.IceDragonWallpaperV22={paint,asset:ASSET};
window.addEventListener('swrlz-theme-change',e=>{if(e?.detail?.theme==='ice-dragon')paint()});
if(active())paint();
})();