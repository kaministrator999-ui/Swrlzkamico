(()=>{'use strict';
if(window.__swrlzGestureScrollV1)return;window.__swrlzGestureScrollV1=true;
let bound=null,dragging=false,cooldownUntil=0,endTimer=0;
const now=()=>performance.now();
function finishGesture(){dragging=false;cooldownUntil=now()+260;clearTimeout(endTimer);endTimer=setTimeout(()=>{cooldownUntil=0},280)}
function bind(){const el=document.querySelector('.messages');if(!el||el===bound)return;if(bound)bound.removeAttribute('data-swrlz-gesture-scroll');bound=el;el.dataset.swrlzGestureScroll='true';el.style.touchAction='pan-y';el.style.overscrollBehaviorY='contain';el.style.webkitOverflowScrolling='touch';el.style.scrollBehavior='auto';
  el.addEventListener('touchstart',()=>{dragging=true;cooldownUntil=Infinity;clearTimeout(endTimer)},{capture:true,passive:true});
  el.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'){dragging=true;cooldownUntil=Infinity;clearTimeout(endTimer)}},{capture:true,passive:true});
  el.addEventListener('touchend',finishGesture,{capture:true,passive:true});el.addEventListener('touchcancel',finishGesture,{capture:true,passive:true});
  el.addEventListener('pointerup',e=>{if(e.pointerType==='touch')finishGesture()},{capture:true,passive:true});el.addEventListener('pointercancel',e=>{if(e.pointerType==='touch')finishGesture()},{capture:true,passive:true});
  el.addEventListener('scroll',e=>{if(dragging||now()<cooldownUntil)e.stopImmediatePropagation()},{capture:true,passive:true});
}
function boot(){bind();new MutationObserver(bind).observe(document.documentElement,{childList:true,subtree:true});window.addEventListener('swrlz-theme-change',()=>requestAnimationFrame(bind))}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();