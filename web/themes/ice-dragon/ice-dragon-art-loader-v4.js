(()=>{"use strict";
const root=document.documentElement;
const body=document.body;
const messages=document.querySelector('.messages');
const stack=document.querySelector('.message-stack');
const read=async path=>{const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}`);return (await r.text()).trim()};
const asUrl=b64=>`url("data:image/jpeg;base64,${b64}")`;
const setVar=(name,b64)=>body?.style.setProperty(name,asUrl(b64));
let adultUrl='';
let adultLayer=null;
function ensureLayer(){
  if(!messages)return null;
  if(!adultLayer){
    adultLayer=document.createElement('div');
    adultLayer.className='ice-dragon-adult-layer';
    adultLayer.setAttribute('aria-hidden','true');
    Object.assign(adultLayer.style,{position:'absolute',inset:'0',pointerEvents:'none',zIndex:'0',backgroundPosition:'50% 42%',backgroundSize:'cover',backgroundRepeat:'no-repeat',opacity:'0',transition:'opacity .18s ease'});
    messages.prepend(adultLayer);
    messages.style.setProperty('position','relative','important');
    messages.style.setProperty('isolation','isolate','important');
    if(stack){stack.style.setProperty('position','relative','important');stack.style.setProperty('z-index','1','important')}
  }
  return adultLayer;
}
function paintAdult(){
  const layer=ensureLayer(); if(!layer)return;
  const active=body?.dataset.swrlzTheme==='ice-dragon'&&adultUrl;
  if(active){
    layer.style.backgroundImage=`linear-gradient(180deg,rgba(1,7,16,.10),rgba(1,8,18,.20) 52%,rgba(1,6,14,.34)),linear-gradient(90deg,rgba(1,8,18,.16),transparent 60%),${adultUrl}`;
    layer.style.opacity='1';
  }else{
    layer.style.opacity='0';
    layer.style.backgroundImage='none';
  }
}
window.__swrlzIceDragonArtReady=(async()=>{
  try{
    const [companion,adult]=await Promise.all([
      read('/live/assets/themes/ice-dragon/assets/companion-96.jpg.b64'),
      read('/live/assets/themes/ice-dragon/assets/adult-180x320.jpg.b64')
    ]);
    setVar('--ice-dragon-companion',companion);
    setVar('--ice-dragon-adult',adult);
    adultUrl=asUrl(adult);
    paintAdult();
    new MutationObserver(paintAdult).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});
    root.classList.add('swrlz-ice-dragon-art-ready');
    return true;
  }catch(error){
    console.warn('Ice Dragon art hydration failed',error);
    root.classList.add('swrlz-ice-dragon-art-failed');
    return false;
  }
})();
})();
