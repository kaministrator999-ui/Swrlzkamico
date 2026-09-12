/* SWRLZ Ice Dragon asset hydrator v15 — persistent device cache + non-blocking 8K promotion */
(()=>{'use strict';
const root=document.documentElement;
const body=document.body;
const debug=window.SWRLZThemeDebug||{log:(event,detail='')=>console.debug('[SWRLZ theme]',event,detail)};
const messagesNow=()=>document.querySelector('.messages');
const CACHE_NAME=window.SWRLZFrontend?.cacheName||'swrlz-static-theme-v1';
const SOURCE_KEY='/__swrlz-cache__/themes/ice-dragon/adult-864x1536-v1.jpg';
const ULTRA_KEY='/__swrlz-cache__/themes/ice-dragon/adult-4320x7680-v1.webp';
const COMPANION_KEY='/__swrlz-cache__/themes/ice-dragon/companion-96-v1.jpg';
const ADULT_PARTS=Array.from({length:6},(_,i)=>`/live/assets/themes/ice-dragon/assets/adult-864x1536.part${String(i).padStart(3,'0')}.b64`);
const COMPANION_SOURCE='/live/assets/themes/ice-dragon/assets/companion-96.jpg.b64';
const cacheOpen=()=>('caches'in window?caches.open(CACHE_NAME):Promise.resolve(null));

const read=async path=>{
  debug.log('asset-fetch-start',path);
  const r=await fetch(path,{cache:'force-cache'});
  debug.log('asset-fetch-response',`${path} status=${r.status}`);
  if(!r.ok)throw new Error(`HTTP ${r.status} ${path}`);
  const text=await r.text();
  debug.log('asset-fetch-complete',`${path} rawChars=${text.length}`);
  return text;
};
function normalizeBase64(raw,label){
  const compact=String(raw||'').replace(/\s+/g,'').replace(/-/g,'+').replace(/_/g,'/');
  const cleaned=compact.replace(/[^A-Za-z0-9+/=]/g,'');
  const firstPad=cleaned.indexOf('=');
  const body64=firstPad>=0?cleaned.slice(0,firstPad):cleaned;
  let normalized=body64;const mod=normalized.length%4;
  if(mod===1)throw new Error(`${label} base64 length invalid after normalization (${normalized.length})`);
  if(mod)normalized+='='.repeat(4-mod);
  return normalized;
}
function b64Blob(b64,type='image/jpeg'){
  const binary=atob(b64);const bytes=new Uint8Array(binary.length);
  for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
  return new Blob([bytes],{type});
}
async function decodeBlob(blob,label,minW=1,minH=1){
  const url=URL.createObjectURL(blob);const probe=new Image();
  try{
    await new Promise((resolve,reject)=>{probe.onload=resolve;probe.onerror=()=>reject(new Error(`${label} failed browser decode`));probe.src=url});
    if(probe.naturalWidth<minW||probe.naturalHeight<minH)throw new Error(`${label} resolution unexpectedly low ${probe.naturalWidth}x${probe.naturalHeight}`);
    debug.log(`${label}-decode-ok`,`${probe.naturalWidth}x${probe.naturalHeight}`);
    return{url,width:probe.naturalWidth,height:probe.naturalHeight};
  }catch(error){URL.revokeObjectURL(url);throw error}
}
async function cacheMatch(key){const cache=await cacheOpen();if(!cache)return null;const response=await cache.match(key);return response||null}
async function cachePut(key,blob){const cache=await cacheOpen();if(!cache)return false;await cache.put(key,new Response(blob,{headers:{'Content-Type':blob.type||'application/octet-stream','Cache-Control':'public, max-age=31536000, immutable'}}));return true}

let companionUrl='';let companionReady=false;let companionPromise=null;
let adultUrl='';let adultReady=false;let adultTier='';let adultPromise=null;let ensurePromise=null;let ultraBuildPromise=null;
function active(){return body?.dataset.swrlzTheme==='ice-dragon'}
function paintCompanion(){
  if(active()&&companionReady&&companionUrl){body.style.setProperty('--ice-dragon-companion',`url("${companionUrl}")`);debug.log('companion-painted','device-cache')}
  else body?.style.removeProperty('--ice-dragon-companion');
}
function clearAdult(messages){if(!messages)return;for(const key of ['background-image','background-position','background-size','background-repeat','background-color'])messages.style.removeProperty(key)}
function paintAdult(){
  const messages=messagesNow();debug.log('adult-paint-attempt',`active=${active()} ready=${adultReady} tier=${adultTier||'none'} messages=${Boolean(messages)}`);
  if(active()&&adultReady&&adultUrl&&messages){
    messages.style.setProperty('background-image',`url("${adultUrl}")`,'important');
    messages.style.setProperty('background-position','50% 42%','important');
    messages.style.setProperty('background-size','cover','important');
    messages.style.setProperty('background-repeat','no-repeat','important');
    messages.style.setProperty('background-color','#010812','important');
    debug.log('adult-painted',`tier=${adultTier}`);
  }else if(messages)clearAdult(messages);
}
function replaceAdult(decoded,tier){if(adultUrl&&adultUrl!==decoded.url)URL.revokeObjectURL(adultUrl);adultUrl=decoded.url;adultTier=tier;adultReady=true;paintAdult()}
function paint(){paintCompanion();paintAdult()}

async function ensureCompanion(){
  if(companionReady){paintCompanion();return true}
  if(companionPromise)return companionPromise;
  companionPromise=(async()=>{
    try{
      const cached=await cacheMatch(COMPANION_KEY);
      let blob;
      if(cached){blob=await cached.blob();debug.log('companion-cache-hit',`${blob.size} bytes`)}
      else{debug.log('companion-cache-miss');blob=b64Blob(normalizeBase64(await read(COMPANION_SOURCE),'companion'));await cachePut(COMPANION_KEY,blob);debug.log('companion-cache-store',`${blob.size} bytes`)}
      const decoded=await decodeBlob(blob,'companion',64,64);companionUrl=decoded.url;companionReady=true;root.classList.add('swrlz-ice-dragon-companion-ready');paintCompanion();return true;
    }catch(error){root.classList.add('swrlz-ice-dragon-companion-failed');debug.log('companion-failed',String(error));return false}
    finally{companionPromise=null}
  })();return companionPromise;
}
async function sourceBlob(){
  const cached=await cacheMatch(SOURCE_KEY);
  if(cached){const blob=await cached.blob();debug.log('adult-cache-hit',`tier=864 bytes=${blob.size}`);return blob}
  debug.log('adult-cache-miss','tier=864');
  const parts=await Promise.all(ADULT_PARTS.map(read));
  const blob=b64Blob(normalizeBase64(parts.join(''),'adult-864x1536'));
  await cachePut(SOURCE_KEY,blob);debug.log('adult-cache-store',`tier=864 bytes=${blob.size}`);return blob;
}
function ultraEligible(){
  const memory=Number(navigator.deviceMemory||0);const cores=Number(navigator.hardwareConcurrency||0);
  return memory>=6&&cores>=6&&typeof document.createElement('canvas').toBlob==='function';
}
async function buildUltra(source){
  if(ultraBuildPromise)return ultraBuildPromise;
  ultraBuildPromise=(async()=>{
    if(!ultraEligible()){debug.log('adult-8k-build-skip',`memory=${navigator.deviceMemory||'unknown'} cores=${navigator.hardwareConcurrency||'unknown'}`);return false}
    if(await cacheMatch(ULTRA_KEY)){debug.log('adult-8k-build-skip','already-cached');return true}
    debug.log('adult-8k-build-start','4320x7680 background task');
    let bitmap=null;
    try{
      bitmap=await createImageBitmap(source);
      const canvas=document.createElement('canvas');canvas.width=4320;canvas.height=7680;
      const ctx=canvas.getContext('2d',{alpha:false});ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';ctx.drawImage(bitmap,0,0,canvas.width,canvas.height);
      const blob=await new Promise((resolve,reject)=>canvas.toBlob(b=>b?resolve(b):reject(new Error('8K WebP encode failed')),'image/webp',0.78));
      const decoded=await decodeBlob(blob,'adult-8k',4000,7000);URL.revokeObjectURL(decoded.url);
      await cachePut(ULTRA_KEY,blob);debug.log('adult-8k-cache-store',`${blob.size} bytes`);return true;
    }catch(error){debug.log('adult-8k-build-failed',String(error));return false}
    finally{bitmap?.close?.()}
  })();return ultraBuildPromise;
}
function scheduleUltra(source){const run=()=>buildUltra(source);if('requestIdleCallback'in window)requestIdleCallback(run,{timeout:5000});else setTimeout(run,1800)}
async function ensureAdult(){
  if(adultReady){paintAdult();return true}
  if(adultPromise)return adultPromise;
  adultPromise=(async()=>{
    try{
      const ultra=await cacheMatch(ULTRA_KEY);
      if(ultra){const blob=await ultra.blob();debug.log('adult-cache-hit',`tier=8k bytes=${blob.size}`);replaceAdult(await decodeBlob(blob,'adult-8k',4000,7000),'8k');root.classList.add('swrlz-ice-dragon-adult-ready');return true}
      debug.log('adult-cache-miss','tier=8k');
      const source=await sourceBlob();replaceAdult(await decodeBlob(source,'adult-source',800,1400),'864');root.classList.add('swrlz-ice-dragon-adult-ready');scheduleUltra(source);return true;
    }catch(error){root.classList.add('swrlz-ice-dragon-adult-failed');debug.log('adult-failed',String(error));return false}
    finally{adultPromise=null}
  })();return adultPromise;
}
function ensure(){
  if(ensurePromise){debug.log('assets-ensure-join');return ensurePromise}
  ensurePromise=(async()=>{try{const result=await Promise.allSettled([ensureCompanion(),ensureAdult()]);paint();const ok=result.some(r=>r.status==='fulfilled'&&r.value===true);root.classList.toggle('swrlz-ice-dragon-art-ready',ok);debug.log('assets-ensure-complete',`companion=${companionReady} adult=${adultReady} tier=${adultTier}`);return ok}finally{ensurePromise=null}})();return ensurePromise;
}
window.__swrlzIceDragonArtReady=ensure();
window.IceDragonAssets={ensure,paint,ensureCompanion,ensureAdult,get companionReady(){return companionReady},get adultReady(){return adultReady},get adultTier(){return adultTier}};
window.addEventListener('swrlz-theme-change',event=>{if(event?.detail?.theme==='ice-dragon')ensure();else paint()});
new MutationObserver(()=>{if(active())ensure();else paint()}).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});
document.addEventListener('DOMContentLoaded',()=>{if(active())ensure();else paint()},{once:true});
window.addEventListener('load',()=>{if(active())paint()},{once:true});
window.addEventListener('pagehide',()=>{if(adultUrl)URL.revokeObjectURL(adultUrl);if(companionUrl)URL.revokeObjectURL(companionUrl)},{once:true});
})();
