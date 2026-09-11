(()=>{"use strict";
const root=document.documentElement;
const body=document.body;
const messages=document.querySelector('.messages');
const stack=document.querySelector('.message-stack');
const read=async path=>{const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}`);return (await r.text()).trim()};
const companionData=b64=>`data:image/jpeg;base64,${b64.replace(/\s+/g,'')}`;
const jpegBlobUrl=b64=>{const clean=b64.replace(/\s+/g,'');const binary=atob(clean);const bytes=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);return URL.createObjectURL(new Blob([bytes],{type:'image/jpeg'}));};
let adultUrl='';let fallbackImg=null;
function ensureFallback(){if(!messages||fallbackImg)return;fallbackImg=document.createElement('img');fallbackImg.alt='';fallbackImg.setAttribute('aria-hidden','true');fallbackImg.className='ice-dragon-adult-fallback';Object.assign(fallbackImg.style,{position:'absolute',inset:'0',width:'100%',height:'100%',objectFit:'cover',objectPosition:'50% 42%',pointerEvents:'none',zIndex:'0',display:'block',opacity:'0'});messages.prepend(fallbackImg);messages.style.setProperty('position','relative','important');messages.style.setProperty('isolation','isolate','important');if(stack){stack.style.setProperty('position','relative','important');stack.style.setProperty('z-index','2','important');}}
function paint(){const active=body?.dataset.swrlzTheme==='ice-dragon'&&adultUrl;if(active){body.style.setProperty('--ice-dragon-adult',`url("${adultUrl}")`);ensureFallback();if(fallbackImg){if(fallbackImg.src!==adultUrl)fallbackImg.src=adultUrl;fallbackImg.style.opacity='.01';}}else{body.style.removeProperty('--ice-dragon-adult');if(fallbackImg)fallbackImg.style.opacity='0';}}
window.__swrlzIceDragonArtReady=(async()=>{try{const [companion,adult]=await Promise.all([read('/live/assets/themes/ice-dragon/assets/companion-96.jpg.b64'),read('/live/assets/themes/ice-dragon/assets/adult-180x320.jpg.b64')]);body.style.setProperty('--ice-dragon-companion',`url("${companionData(companion)}")`);adultUrl=jpegBlobUrl(adult);paint();new MutationObserver(paint).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});root.classList.add('swrlz-ice-dragon-art-ready');return true;}catch(error){console.warn('Ice Dragon art hydration failed',error);root.classList.add('swrlz-ice-dragon-art-failed');return false;}})();
window.addEventListener('pagehide',()=>{if(adultUrl)URL.revokeObjectURL(adultUrl)},{once:true});
})();
