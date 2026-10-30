// Measure existing native controls only; no scene, camera or render loop.
(()=>{
 const host=document.querySelector('.workspace > .viewport-wrap:has(> #viewport)');
 const levels=document.getElementById('st141LevelBar');
 const tabs=host?.querySelector('.mobile-tabs');
 if(!host||!levels)return;
 const narrow=matchMedia('(max-width:620px)');
 function sync(){
  if(!narrow.matches){host.style.removeProperty('--se-mobile-controls-bottom');host.style.removeProperty('--se-mobile-drawer-top');return;}
  const box=levels.getBoundingClientRect(),parent=host.getBoundingClientRect();
  const visible=!levels.hidden&&getComputedStyle(levels).display!=='none';
  const bottom=visible?Math.max(8,Math.ceil(box.bottom-parent.top)+8):8;
  const next=bottom+'px';
  if(host.style.getPropertyValue('--se-mobile-controls-bottom')!==next)
   host.style.setProperty('--se-mobile-controls-bottom',next);
  const drawerTop=(bottom+Math.ceil(tabs?.getBoundingClientRect().height||0)+8)+'px';
  if(host.style.getPropertyValue('--se-mobile-drawer-top')!==drawerTop)
   host.style.setProperty('--se-mobile-drawer-top',drawerTop);
 }
 if(typeof ResizeObserver==='function'){
  const observer=new ResizeObserver(sync);observer.observe(levels);observer.observe(host);if(tabs)observer.observe(tabs);
 }
 window.addEventListener('resize',sync,{passive:true});
 narrow.addEventListener?.('change',sync);
 sync();
})();
