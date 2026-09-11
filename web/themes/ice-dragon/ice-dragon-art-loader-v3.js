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
    messages.style.setProperty('background-image',`linear-gradient(180deg,rgba(1,7,16,.12),rgba(1,8,18,.22) 52%,rgba(1,6,14,.36)),linear-gradient(90deg,rgba(1,8,18,.18),transparent 58%),${adultUrl}`,'important');
    messages.style.setProperty('background-position','center,center,50% 42%','important');
    messages.style.setProperty('background-size','auto,auto,cover','important');
    messages.style.setProperty('background-repeat','no-repeat,no-repeat,no-repeat','important');
    messages.style.setProperty('background-attachment','local,local,local','important');
  }else{
    for(const prop of ['background-image','background-position','background-size','background-repeat','background-attachment']) messages.style.removeProperty(prop);
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
