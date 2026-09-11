(()=>{"use strict";
const root=document.documentElement;
const body=document.body;
const messages=document.querySelector('.messages');
const read=async path=>{const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}`);return (await r.text()).trim()};
const asUrl=b64=>`url("data:image/jpeg;base64,${b64}")`;
const setVar=(name,b64)=>body?.style.setProperty(name,asUrl(b64));
let adultUrl='';
const paintAdult=()=>{
  if(!messages)return;
  if(body?.dataset.swrlzTheme==='ice-dragon'&&adultUrl){
    messages.style.backgroundImage=`linear-gradient(180deg,rgba(1,7,16,.18),rgba(1,8,18,.31) 56%,rgba(1,6,14,.46)),linear-gradient(90deg,rgba(1,8,18,.22),transparent 58%),${adultUrl}`;
    messages.style.backgroundPosition='center,center,50% 40%';
    messages.style.backgroundSize='auto,auto,cover';
    messages.style.backgroundRepeat='no-repeat,no-repeat,no-repeat';
    messages.style.backgroundAttachment='local,local,local';
  }else{
    messages.style.removeProperty('background-image');
    messages.style.removeProperty('background-position');
    messages.style.removeProperty('background-size');
    messages.style.removeProperty('background-repeat');
    messages.style.removeProperty('background-attachment');
  }
};
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
