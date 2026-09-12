/* SWRLZ Ice Dragon asset hydrator v12 — independent assets + diagnostics */
(()=>{'use strict';
const root=document.documentElement;
const body=document.body;
const debug=window.SWRLZThemeDebug||{log:(event,detail='')=>console.debug('[SWRLZ theme]',event,detail)};
const read=async path=>{debug.log('asset-fetch-start',path);const r=await fetch(path,{cache:'no-store'});debug.log('asset-fetch-response',`${path} status=${r.status}`);if(!r.ok)throw new Error(`HTTP ${r.status} ${path}`);const text=(await r.text()).trim().replace(/\s+/g,'');debug.log('asset-fetch-complete',`${path} chars=${text.length}`);return text};
const companionImage=b64=>`url("data:image/jpeg;base64,${b64}")`;
const blobUrl=b64=>{const binary=atob(b64);const bytes=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);return URL.createObjectURL(new Blob([bytes],{type:'image/jpeg'}))};
const messagesNow=()=>document.querySelector('.messages');
let companion='';let companionReady=false;let companionFailed=false;
let adultUrl='';let adultReady=false;let adultFailed=false;

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

async function ensureCompanion(){
  if(companionReady){paintCompanion();return true}
  if(companionFailed)return false;
  try{companion=await read('/live/assets/themes/ice-dragon/assets/companion-96.jpg.b64');companionReady=true;root.classList.add('swrlz-ice-dragon-companion-ready');debug.log('companion-ready');paintCompanion();return true}
  catch(error){companionFailed=true;root.classList.add('swrlz-ice-dragon-companion-failed');debug.log('companion-failed',String(error));return false}
}
async function ensureAdult(){
  if(adultReady){paintAdult();return true}
  if(adultFailed)return false;
  try{
    const adult=await read('/live/assets/themes/ice-dragon/assets/adult-180x320.jpg.b64');
    adultUrl=blobUrl(adult);debug.log('adult-blob-created',adultUrl.slice(0,48));
    const probe=new Image();
    await new Promise((resolve,reject)=>{probe.onload=()=>{debug.log('adult-decode-ok',`${probe.naturalWidth}x${probe.naturalHeight}`);resolve()};probe.onerror=()=>reject(new Error('adult wallpaper JPEG failed browser decode'));probe.src=adultUrl});
    adultReady=true;root.classList.add('swrlz-ice-dragon-adult-ready');paintAdult();return true;
  }catch(error){adultFailed=true;root.classList.add('swrlz-ice-dragon-adult-failed');debug.log('adult-failed',String(error));return false}
}
async function ensure(){
  debug.log('assets-ensure-start',`readyState=${document.readyState} messages=${Boolean(messagesNow())}`);
  const result=await Promise.allSettled([ensureCompanion(),ensureAdult()]);
  paint();
  const ok=result.some(r=>r.status==='fulfilled'&&r.value===true);
  root.classList.toggle('swrlz-ice-dragon-art-ready',ok);
  debug.log('assets-ensure-complete',`companion=${companionReady} adult=${adultReady} messages=${Boolean(messagesNow())}`);
  return ok;
}
window.__swrlzIceDragonArtReady=ensure();
window.IceDragonAssets={ensure,paint,ensureCompanion,ensureAdult,get companionReady(){return companionReady},get adultReady(){return adultReady},get companionFailed(){return companionFailed},get adultFailed(){return adultFailed}};
window.addEventListener('swrlz-theme-change',event=>{debug.log('asset-theme-event',event?.detail?.theme||'unknown');if(event?.detail?.theme==='ice-dragon')ensure();else paint()});
new MutationObserver(()=>{debug.log('theme-attribute-observed',body?.dataset.swrlzTheme||'default');if(active())ensure();else paint()}).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});
document.addEventListener('DOMContentLoaded',()=>{debug.log('dom-ready',`messages=${Boolean(messagesNow())}`);if(active())ensure();else paint()},{once:true});
window.addEventListener('load',()=>{debug.log('window-load',`messages=${Boolean(messagesNow())}`);if(active())paint()},{once:true});
window.addEventListener('pagehide',()=>{if(adultUrl)URL.revokeObjectURL(adultUrl)},{once:true});
})();
