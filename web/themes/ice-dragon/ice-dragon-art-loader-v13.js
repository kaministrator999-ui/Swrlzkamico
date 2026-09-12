/* SWRLZ Ice Dragon asset hydrator v13 — normalized base64 + single-flight hydration */
(()=>{'use strict';
const root=document.documentElement;
const body=document.body;
const debug=window.SWRLZThemeDebug||{log:(event,detail='')=>console.debug('[SWRLZ theme]',event,detail)};
const messagesNow=()=>document.querySelector('.messages');

const read=async path=>{
  debug.log('asset-fetch-start',path);
  const r=await fetch(path,{cache:'no-store'});
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
  let normalized=body64;
  const mod=normalized.length%4;
  if(mod===1)throw new Error(`${label} base64 length invalid after normalization (${normalized.length})`);
  if(mod)normalized+='='.repeat(4-mod);
  debug.log('asset-base64-normalized',`${label} raw=${String(raw||'').length} compact=${compact.length} clean=${body64.length} padded=${normalized.length}`);
  return normalized;
}

const companionImage=b64=>`url("data:image/jpeg;base64,${b64}")`;
const blobUrl=b64=>{
  const binary=atob(b64);
  const bytes=new Uint8Array(binary.length);
  for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
  return URL.createObjectURL(new Blob([bytes],{type:'image/jpeg'}));
};

let companion='';let companionReady=false;let companionFailed=false;let companionPromise=null;
let adultUrl='';let adultReady=false;let adultFailed=false;let adultPromise=null;
let ensurePromise=null;

function active(){return body?.dataset.swrlzTheme==='ice-dragon'}
function paintCompanion(){
  if(active()&&companionReady&&companion){body.style.setProperty('--ice-dragon-companion',companionImage(companion));debug.log('companion-painted')}
  else{body?.style.removeProperty('--ice-dragon-companion');debug.log('companion-cleared',`active=${active()} ready=${companionReady}`)}
}
function clearAdult(messages){
  if(!messages)return;
  for(const key of ['background-image','background-position','background-size','background-repeat','background-color'])messages.style.removeProperty(key);
}
function paintAdult(){
  const messages=messagesNow();
  debug.log('adult-paint-attempt',`active=${active()} ready=${adultReady} messages=${Boolean(messages)} url=${Boolean(adultUrl)}`);
  if(active()&&adultReady&&adultUrl&&messages){
    messages.style.setProperty('background-image',`url("${adultUrl}")`,'important');
    messages.style.setProperty('background-position','50% 42%','important');
    messages.style.setProperty('background-size','cover','important');
    messages.style.setProperty('background-repeat','no-repeat','important');
    messages.style.setProperty('background-color','#010812','important');
    const computed=getComputedStyle(messages);
    debug.log('adult-painted',`inline=${messages.style.backgroundImage}; computed=${computed.backgroundImage.slice(0,140)}`);
  }else if(messages){clearAdult(messages);debug.log('adult-cleared')}
}
function paint(){paintCompanion();paintAdult()}

function ensureCompanion(){
  if(companionReady){paintCompanion();return Promise.resolve(true)}
  if(companionPromise){debug.log('companion-ensure-join');return companionPromise}
  companionPromise=(async()=>{
    try{
      companion=normalizeBase64(await read('/live/assets/themes/ice-dragon/assets/companion-96.jpg.b64'),'companion');
      companionReady=true;companionFailed=false;root.classList.add('swrlz-ice-dragon-companion-ready');debug.log('companion-ready');paintCompanion();return true;
    }catch(error){companionFailed=true;root.classList.add('swrlz-ice-dragon-companion-failed');debug.log('companion-failed',String(error));return false}
    finally{companionPromise=null}
  })();
  return companionPromise;
}

function ensureAdult(){
  if(adultReady){paintAdult();return Promise.resolve(true)}
  if(adultPromise){debug.log('adult-ensure-join');return adultPromise}
  adultPromise=(async()=>{
    try{
      const adult=normalizeBase64(await read('/live/assets/themes/ice-dragon/assets/adult-180x320.jpg.b64'),'adult');
      if(adultUrl)URL.revokeObjectURL(adultUrl);
      adultUrl=blobUrl(adult);debug.log('adult-blob-created',adultUrl.slice(0,48));
      const probe=new Image();
      await new Promise((resolve,reject)=>{probe.onload=()=>{debug.log('adult-decode-ok',`${probe.naturalWidth}x${probe.naturalHeight}`);resolve()};probe.onerror=()=>reject(new Error('adult wallpaper JPEG failed browser decode'));probe.src=adultUrl});
      adultReady=true;adultFailed=false;root.classList.add('swrlz-ice-dragon-adult-ready');paintAdult();return true;
    }catch(error){adultFailed=true;root.classList.add('swrlz-ice-dragon-adult-failed');debug.log('adult-failed',String(error));return false}
    finally{adultPromise=null}
  })();
  return adultPromise;
}

function ensure(){
  if(ensurePromise){debug.log('assets-ensure-join');return ensurePromise}
  debug.log('assets-ensure-start',`readyState=${document.readyState} messages=${Boolean(messagesNow())}`);
  ensurePromise=(async()=>{
    try{
      const result=await Promise.allSettled([ensureCompanion(),ensureAdult()]);
      paint();
      const ok=result.some(r=>r.status==='fulfilled'&&r.value===true);
      root.classList.toggle('swrlz-ice-dragon-art-ready',ok);
      debug.log('assets-ensure-complete',`companion=${companionReady} adult=${adultReady} messages=${Boolean(messagesNow())}`);
      return ok;
    }finally{ensurePromise=null}
  })();
  return ensurePromise;
}

window.__swrlzIceDragonArtReady=ensure();
window.IceDragonAssets={ensure,paint,ensureCompanion,ensureAdult,get companionReady(){return companionReady},get adultReady(){return adultReady},get companionFailed(){return companionFailed},get adultFailed(){return adultFailed}};
window.addEventListener('swrlz-theme-change',event=>{debug.log('asset-theme-event',event?.detail?.theme||'unknown');if(event?.detail?.theme==='ice-dragon')ensure();else paint()});
new MutationObserver(()=>{debug.log('theme-attribute-observed',body?.dataset.swrlzTheme||'default');if(active())ensure();else paint()}).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});
document.addEventListener('DOMContentLoaded',()=>{debug.log('dom-ready',`messages=${Boolean(messagesNow())}`);if(active())ensure();else paint()},{once:true});
window.addEventListener('load',()=>{debug.log('window-load',`messages=${Boolean(messagesNow())}`);if(active())paint()},{once:true});
window.addEventListener('pagehide',()=>{if(adultUrl)URL.revokeObjectURL(adultUrl)},{once:true});
})();
