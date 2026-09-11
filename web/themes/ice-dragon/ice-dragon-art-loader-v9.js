(()=>{"use strict";
const root=document.documentElement;
const body=document.body;
const messages=document.querySelector('.messages');
const stack=document.querySelector('.message-stack');
const read=async path=>{const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}`);return (await r.text()).trim()};
const clean=b64=>b64.replace(/\s+/g,'');
const dataSrc=b64=>`data:image/jpeg;base64,${clean(b64)}`;
const jpegBlobUrl=b64=>{const binary=atob(clean(b64));const bytes=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);return URL.createObjectURL(new Blob([bytes],{type:'image/jpeg'}))};
const setCompanion=b64=>body?.style.setProperty('--ice-dragon-companion',`url("${dataSrc(b64)}")`);
let adultUrl='';
let adultImg=null;
let shade=null;
function ensureLayers(){
  if(!messages)return false;
  if(!adultImg){
    adultImg=document.createElement('img');
    adultImg.className='ice-dragon-adult-image';
    adultImg.alt='';
    adultImg.setAttribute('aria-hidden','true');
    Object.assign(adultImg.style,{position:'absolute',inset:'0',width:'100%',height:'100%',objectFit:'cover',objectPosition:'50% 42%',pointerEvents:'none',zIndex:'0',opacity:'0',display:'block',transition:'opacity .18s ease'});
    shade=document.createElement('div');
    shade.className='ice-dragon-adult-shade';
    shade.setAttribute('aria-hidden','true');
    Object.assign(shade.style,{position:'absolute',inset:'0',pointerEvents:'none',zIndex:'1',background:'linear-gradient(180deg,rgba(1,7,16,.18),rgba(1,8,18,.28) 56%,rgba(1,6,14,.42)),linear-gradient(90deg,rgba(1,8,18,.24),transparent 58%)',opacity:'0',transition:'opacity .18s ease'});
    adultImg.addEventListener('load',()=>{if(body?.dataset.swrlzTheme==='ice-dragon'){adultImg.style.opacity='1';shade.style.opacity='1'}});
    adultImg.addEventListener('error',()=>{adultImg.style.opacity='0';shade.style.opacity='0';console.warn('Ice Dragon adult image failed to render')});
    messages.prepend(shade);
    messages.prepend(adultImg);
    messages.style.setProperty('position','relative','important');
    messages.style.setProperty('isolation','isolate','important');
    if(stack){stack.style.setProperty('position','relative','important');stack.style.setProperty('z-index','2','important')}
  }
  return true;
}
function paint(){
  if(!ensureLayers())return;
  const active=body?.dataset.swrlzTheme==='ice-dragon';
  if(active&&adultUrl){
    messages.style.setProperty('background','transparent','important');
    if(adultImg.src!==adultUrl)adultImg.src=adultUrl;
    if(adultImg.complete&&adultImg.naturalWidth>0){adultImg.style.opacity='1';shade.style.opacity='1'}
  }else{
    messages.style.removeProperty('background');
    adultImg.style.opacity='0';
    shade.style.opacity='0';
  }
}
window.__swrlzIceDragonArtReady=(async()=>{
  try{
    const [companion,adult]=await Promise.all([
      read('/live/assets/themes/ice-dragon/assets/companion-96.jpg.b64'),
      read('/live/assets/themes/ice-dragon/assets/adult-180x320.jpg.b64')
    ]);
    setCompanion(companion);
    adultUrl=jpegBlobUrl(adult);
    paint();
    new MutationObserver(paint).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});
    root.classList.add('swrlz-ice-dragon-art-ready');
    return true;
  }catch(error){
    console.warn('Ice Dragon art hydration failed',error);
    root.classList.add('swrlz-ice-dragon-art-failed');
    return false;
  }
})();
window.addEventListener('pagehide',()=>{if(adultUrl)URL.revokeObjectURL(adultUrl)},{once:true});
})();
