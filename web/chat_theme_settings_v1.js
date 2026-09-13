(()=>{'use strict';if(window.__swrlzThemeSettingsV1Installed)return;window.__swrlzThemeSettingsV1Installed=true;
const THEME_KEY='swrlz.chat.theme';
function removeTop(){document.querySelector('#swrlzThemeSelect')?.remove()}
function value(){try{return localStorage.getItem(THEME_KEY)||'default'}catch{return'default'}}
function addTheme(detail){if(!detail||detail.querySelector('[data-swrlz-theme-setting]'))return;const h3=detail.querySelector('h3');if(h3?.textContent!=='Personalization')return;const grid=detail.querySelector('.swrlz-setting-grid')||detail;const label=document.createElement('label');label.dataset.swrlzThemeSetting='true';label.textContent='Chat theme';const select=document.createElement('select');select.className='swrlz-settings-theme-select';select.innerHTML='<option value="default">Default</option><option value="ice-dragon">❄ Ice Dragon</option>';select.value=value();select.addEventListener('change',()=>window.IceDragonTheme?.set?.(select.value,true));label.appendChild(select);grid.appendChild(label)}
function patch(){removeTop();document.querySelectorAll('.swrlz-settings-detail').forEach(addTheme)}
const obs=new MutationObserver(()=>patch());function boot(){patch();obs.observe(document.documentElement,{childList:true,subtree:true});window.addEventListener('swrlz-theme-change',e=>{document.querySelectorAll('.swrlz-settings-theme-select').forEach(s=>s.value=e?.detail?.theme||'default');removeTop()})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();})();
