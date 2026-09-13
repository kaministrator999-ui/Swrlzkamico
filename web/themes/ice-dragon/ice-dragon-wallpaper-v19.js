/* SWRLZ Ice Dragon wallpaper v19 — direct source first, deterministic quality-safe fallback. */
(()=>{'use strict';
const body=document.body;
const root=document.documentElement;
const debug=window.SWRLZThemeDebug||{log:(e,d='')=>console.debug('[SWRLZ theme]',e,d)};
const ASSET='/live/assets/themes/ice-dragon/assets/ice-dragon-adult-wallpaper.jpg?v=20260913b';
const CACHE='swrlz-static-theme-direct-v2';
const CACHE_KEY='/__swrlz-cache__/themes/ice-dragon/direct-wallpaper-20260913b.jpg';
let url='';let promise=null;
const active=()=>body?.dataset.swrlzTheme==='ice-dragon';
const chamber=()=>document.querySelector('.messages');
function applyFit(el=chamber()){
  if(!el||!active())return false;
  el.style.setProperty('background-position','50% 50%','important');
  el.style.setProperty('background-size','contain','important');
  el.style.setProperty('background-repeat','no-repeat','important');
  el.style.setProperty('background-color','#010812','important');
  return true;
}
function paintDirect(){const el=chamber();if(!el||!active()||!url)return false;el.style.setProperty('background-image',`url("${url}")`,'important');applyFit(el);debug.log('wallpaper-v19-painted-direct',ASSET);return true}
async function decode(blob){const next=URL.createObjectURL(blob);const img=new Image();await new Promise((ok,bad)=>{img.onload=ok;img.onerror=()=>bad(new Error('wallpaper v19 browser decode failed'));img.src=next});if(img.naturalWidth<800||img.naturalHeight<1400){URL.revokeObjectURL(next);throw new Error(`wallpaper v19 resolution too low ${img.naturalWidth}x${img.naturalHeight}`)}debug.log('wallpaper-v19-decode-ok',`${img.naturalWidth}x${img.naturalHeight} bytes=${blob.size}`);if(url)URL.revokeObjectURL(url);url=next;return blob}
async function direct(){let blob=null;if('caches'in window){const c=await caches.open(CACHE);const hit=await c.match(CACHE_KEY);if(hit){blob=await hit.blob();debug.log('wallpaper-v19-cache-hit',`${blob.size}`)}else{const r=await fetch(ASSET,{cache:'no-cache'});if(!r.ok)throw new Error(`direct asset HTTP ${r.status}`);blob=await r.blob();await c.put(CACHE_KEY,new Response(blob,{headers:{'Content-Type':blob.type||'image/jpeg','Cache-Control':'public, max-age=31536000, immutable'}}));debug.log('wallpaper-v19-cache-store',`${blob.size}`)}}else{const r=await fetch(ASSET,{cache:'no-cache'});if(!r.ok)throw new Error(`direct asset HTTP ${r.status}`);blob=await r.blob()}await decode(blob);paintDirect();root.classList.add('swrlz-ice-dragon-wallpaper-v19-direct');return true}
function settleFallback(){[0,80,240,700].forEach(ms=>setTimeout(()=>{if(active()&&!url){applyFit();debug.log('wallpaper-v19-fallback-fit',`delay=${ms}`)}},ms))}
async function fallback(error){debug.log('wallpaper-v19-direct-unavailable',String(error));try{if(window.IceDragonAssets?.ensureAdult)await window.IceDragonAssets.ensureAdult();else if(window.__swrlzIceDragonArtReady)await window.__swrlzIceDragonArtReady}catch(e){debug.log('wallpaper-v19-fallback-loader-error',String(e))}settleFallback();root.classList.add('swrlz-ice-dragon-wallpaper-v19-fallback');return false}
async function load(){if(promise)return promise;promise=(async()=>{try{return await direct()}catch(error){return fallback(error)}finally{promise=null}})();return promise}
window.IceDragonWallpaperV19={load,paint:()=>url?paintDirect():applyFit(),asset:ASSET};
window.addEventListener('swrlz-theme-change',e=>{if(e?.detail?.theme==='ice-dragon')load()});
new MutationObserver(()=>{if(active())load()}).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});
if(active())load();
window.addEventListener('load',()=>{if(active())url?paintDirect():settleFallback()},{once:true});
window.addEventListener('pagehide',()=>{if(url)URL.revokeObjectURL(url)},{once:true});
})();
