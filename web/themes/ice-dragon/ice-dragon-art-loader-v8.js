/* SWRLZ Ice Dragon asset hydrator v11 — direct chamber wallpaper ownership */
(()=>{'use strict';
const root=document.documentElement;
const body=document.body;
const messages=document.querySelector('.messages');
const read=async path=>{const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}`);return (await r.text()).trim().replace(/\s+/g,'')};
const companionImage=b64=>`url("data:image/jpeg;base64,${b64}")`;
const blobUrl=b64=>{const binary=atob(b64);const bytes=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);return URL.createObjectURL(new Blob([bytes],{type:'image/jpeg'}))};
let ready=false;
let failed=false;
let assets=null;
let adultUrl='';
function paint(){
  const active=body?.dataset.swrlzTheme==='ice-dragon';
  if(active&&assets){
    body.style.setProperty('--ice-dragon-companion',companionImage(assets.companion));
    if(messages&&adultUrl){
      messages.style.setProperty('background-image',`url("${adultUrl}")`,'important');
      messages.style.setProperty('background-position','50% 42%','important');
      messages.style.setProperty('background-size','cover','important');
      messages.style.setProperty('background-repeat','no-repeat','important');
      messages.style.setProperty('background-color','#010812','important');
    }
  }else{
    body.style.removeProperty('--ice-dragon-companion');
    if(messages){
      messages.style.removeProperty('background-image');
      messages.style.removeProperty('background-position');
      messages.style.removeProperty('background-size');
      messages.style.removeProperty('background-repeat');
      messages.style.removeProperty('background-color');
    }
  }
}
async function ensure(){
  if(ready){paint();return true}
  if(failed)return false;
  try{
    const [companion,adult]=await Promise.all([
      read('/live/assets/themes/ice-dragon/assets/companion-96.jpg.b64'),
      read('/live/assets/themes/ice-dragon/assets/adult-180x320.jpg.b64')
    ]);
    assets={companion,adult};
    adultUrl=blobUrl(adult);
    const probe=new Image();
    await new Promise((resolve,reject)=>{probe.onload=resolve;probe.onerror=()=>reject(new Error('adult wallpaper JPEG failed browser decode'));probe.src=adultUrl});
    ready=true;
    root.classList.add('swrlz-ice-dragon-art-ready');
    paint();
    return true;
  }catch(error){
    failed=true;
    root.classList.add('swrlz-ice-dragon-art-failed');
    console.warn('Ice Dragon asset hydration failed',error);
    return false;
  }
}
window.__swrlzIceDragonArtReady=ensure();
window.IceDragonAssets={ensure,paint,get ready(){return ready},get failed(){return failed}};
window.addEventListener('swrlz-theme-change',event=>{if(event?.detail?.theme==='ice-dragon')ensure();else paint()});
new MutationObserver(()=>{if(body?.dataset.swrlzTheme==='ice-dragon')ensure();else paint()}).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});
window.addEventListener('pagehide',()=>{if(adultUrl)URL.revokeObjectURL(adultUrl)},{once:true});
})();
