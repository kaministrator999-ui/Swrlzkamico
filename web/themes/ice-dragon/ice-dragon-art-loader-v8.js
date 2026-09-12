/* SWRLZ Ice Dragon asset hydrator v10 — deterministic theme package assets */
(()=>{'use strict';
const root=document.documentElement;
const body=document.body;
const read=async path=>{const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}`);return (await r.text()).trim().replace(/\s+/g,'')};
const asImage=b64=>`url("data:image/jpeg;base64,${b64}")`;
let ready=false;
let failed=false;
let assets=null;
function paint(){
  const active=body?.dataset.swrlzTheme==='ice-dragon';
  if(active&&assets){
    body.style.setProperty('--ice-dragon-companion',asImage(assets.companion));
    body.style.setProperty('--ice-dragon-adult',asImage(assets.adult));
  }else{
    body.style.removeProperty('--ice-dragon-companion');
    body.style.removeProperty('--ice-dragon-adult');
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
    assets={companion,adult};ready=true;root.classList.add('swrlz-ice-dragon-art-ready');paint();return true;
  }catch(error){
    failed=true;root.classList.add('swrlz-ice-dragon-art-failed');console.warn('Ice Dragon asset hydration failed',error);return false;
  }
}
window.__swrlzIceDragonArtReady=ensure();
window.IceDragonAssets={ensure,paint,get ready(){return ready},get failed(){return failed}};
window.addEventListener('swrlz-theme-change',event=>{
  if(event?.detail?.theme==='ice-dragon')ensure();else paint();
});
new MutationObserver(()=>{if(body?.dataset.swrlzTheme==='ice-dragon')ensure();else paint()}).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});
})();
