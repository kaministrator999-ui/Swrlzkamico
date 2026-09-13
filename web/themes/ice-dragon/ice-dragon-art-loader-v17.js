/* SWRLZ Ice Dragon asset hydrator v17.2 — wallpaper purge only; companion is a static CSS-owned runtime asset. */
(()=>{'use strict';
const root=document.documentElement;
const body=document.body;
const debug=window.SWRLZThemeDebug||{log:(event,detail='')=>console.debug('[SWRLZ theme]',event,detail)};
const LEGACY_ADULT_KEY='swrlz.theme.iceDragon.adultPreview.v2';
const OLD_COMPANION_KEYS=['swrlz.theme.iceDragon.companionPreview.v2','swrlz.theme.iceDragon.companionPreview.v3'];
function active(){return body?.dataset.swrlzTheme==='ice-dragon'}
function purgeLegacyAdult(){try{localStorage.removeItem(LEGACY_ADULT_KEY)}catch(_){ }const messages=document.querySelector('.messages');if(messages){for(const key of ['background-image','background-position','background-size','background-repeat','background-color'])messages.style.removeProperty(key);messages.style.setProperty('background','transparent','important')}debug.log('adult-wallpaper-retired','workspace-is-canonical-owner')}
function purgeLegacyCompanionPreviews(){for(const key of OLD_COMPANION_KEYS){try{localStorage.removeItem(key)}catch(_){ }}debug.log('companion-cache-retired','static-css-owner')}
function paintCompanion(){if(active())root.classList.add('swrlz-ice-dragon-companion-ready');else root.classList.remove('swrlz-ice-dragon-companion-ready')}
async function ensureCompanion(){paintCompanion();return true}
async function ensure(){purgeLegacyAdult();purgeLegacyCompanionPreviews();paintCompanion();root.classList.toggle('swrlz-ice-dragon-art-ready',active());debug.log('assets-ensure-complete','companion=static-css adult=retired workspaceWallpaper=true');return true}
window.__swrlzIceDragonArtReady=ensure();
window.IceDragonAssets={ensure,paint:()=>{purgeLegacyAdult();paintCompanion()},ensureCompanion,ensureAdult:async()=>{purgeLegacyAdult();return true},get companionReady(){return active()},get adultReady(){return true},get adultTier(){return'canonical-workspace'}};
window.addEventListener('swrlz-theme-change',event=>{if(event?.detail?.theme==='ice-dragon')ensure();else paintCompanion()});
new MutationObserver(()=>paintCompanion()).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});
document.addEventListener('DOMContentLoaded',()=>{purgeLegacyAdult();purgeLegacyCompanionPreviews();paintCompanion()},{once:true});
})();
