/* SWRLZ Ice Dragon direct wallpaper v18 — use the supplied artwork as-is. */
(()=>{'use strict';
const body=document.body;
const debug=window.SWRLZThemeDebug||{log:(e,d='')=>console.debug('[SWRLZ theme]',e,d)};
const ASSET='/live/assets/themes/ice-dragon/assets/ice-dragon-adult-wallpaper.jpg?v=20260912a';
const CACHE='swrlz-static-theme-direct-v1';
const CACHE_KEY='/__swrlz-cache__/themes/ice-dragon/direct-wallpaper-20260912a.jpg';
let url='';let promise=null;
const active=()=>body?.dataset.swrlzTheme==='ice-dragon';
const chamber=()=>document.querySelector('.messages');
function paint(){const el=chamber();if(!el||!active()||!url)return false;el.style.setProperty('background-image',`url("${url}")`,'important');el.style.setProperty('background-position','50% 42%','important');el.style.setProperty('background-size','cover','important');el.style.setProperty('background-repeat','no-repeat','important');el.style.setProperty('background-color','#010812','important');debug.log('direct-wallpaper-painted',ASSET);return true}
async function decode(blob){const next=URL.createObjectURL(blob);const img=new Image();await new Promise((ok,bad)=>{img.onload=ok;img.onerror=()=>bad(new Error('direct wallpaper browser decode failed'));img.src=next});if(img.naturalWidth<800||img.naturalHeight<1400){URL.revokeObjectURL(next);throw new Error(`direct wallpaper resolution too low ${img.naturalWidth}x${img.naturalHeight}`)}debug.log('direct-wallpaper-decode-ok',`${img.naturalWidth}x${img.naturalHeight} bytes=${blob.size}`);if(url)URL.revokeObjectURL(url);url=next;return blob}
async function load(){if(promise)return promise;promise=(async()=>{try{let blob=null;if('caches'in window){const c=await caches.open(CACHE);const hit=await c.match(CACHE_KEY);if(hit){blob=await hit.blob();debug.log('direct-wallpaper-cache-hit',`${blob.size}`)}else{const r=await fetch(ASSET,{cache:'force-cache'});if(!r.ok)throw new Error(`direct asset HTTP ${r.status}`);blob=await r.blob();await c.put(CACHE_KEY,new Response(blob,{headers:{'Content-Type':blob.type||'image/jpeg','Cache-Control':'public, max-age=31536000, immutable'}}));debug.log('direct-wallpaper-cache-store',`${blob.size}`)}}else{const r=await fetch(ASSET,{cache:'force-cache'});if(!r.ok)throw new Error(`direct asset HTTP ${r.status}`);blob=await r.blob()}await decode(blob);paint();document.documentElement.classList.add('swrlz-ice-dragon-direct-wallpaper-ready');return true}catch(error){debug.log('direct-wallpaper-unavailable',String(error));return false}finally{promise=null}})();return promise}
window.IceDragonDirectWallpaper={load,paint,asset:ASSET};
window.addEventListener('swrlz-theme-change',e=>{if(e?.detail?.theme==='ice-dragon')load()});
new MutationObserver(()=>{if(active())load()}).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});
if(active())load();
window.addEventListener('pagehide',()=>{if(url)URL.revokeObjectURL(url)},{once:true});
})();
