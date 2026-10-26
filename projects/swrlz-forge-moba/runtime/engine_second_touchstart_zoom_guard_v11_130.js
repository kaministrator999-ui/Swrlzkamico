// §E v11.130: protect the second *touchstart* of a rapid starter-project
// double tap, before Android Chrome can magnify the browser page.
// Previous v11.129 after-click shield remains as a secondary line of defense.
// Browser pinch zoom, native camera touch, typing and editing are NOT disabled.
(function se130InstallSecondTapProtection(){
 if(window.__se130SecondTapProtection)return;
 window.__se130SecondTapProtection=true;
 const clock=()=>performance.now(),MAX_INTERVAL=670;
 const isStarter=element=>Boolean(element?.closest?.('#projectHub button[data-project-template]'));
 const isEditable=element=>Boolean(element?.closest?.('input,textarea,select,[contenteditable]:not([contenteditable="false"]),[role="textbox"]'));
 let first=null,deadline=-Infinity,blockedId=null,multi=false;
 function touchPoint(e){return e.changedTouches?.length===1?e.changedTouches[0]:null;}
 document.addEventListener('touchstart',e=>{
  if((e.touches?.length||0)>1){
   // Two simultaneous fingers are intentional pinch-zoom. Never cancel.
   multi=true;first=null;deadline=-Infinity;blockedId=null;return;
  }
  const point=touchPoint(e),t=clock();
  if(!point)return;
  if(t<=deadline&&!multi&&!isEditable(e.target)){
   // Prevent the browser zoom decision on second contact, not just dblclick.
   if(e.cancelable)e.preventDefault();
   blockedId=point.identifier;deadline=-Infinity;first=null;return;
  }
  first=!multi&&isStarter(e.target)?{
   identifier:point.identifier,x:point.clientX,y:point.clientY,when:t
  }:null;
 },{capture:true,passive:false});
 document.addEventListener('touchend',e=>{
  const point=touchPoint(e);
  if(point?.identifier===blockedId){
   if(e.cancelable)e.preventDefault();
   blockedId=null;
  }else if(first&&point?.identifier===first.identifier){
   const recorded=first;first=null;
   if(!multi&&!(e.touches?.length)&&clock()-recorded.when<=550
     &&Math.hypot(point.clientX-recorded.x,point.clientY-recorded.y)<=18){
    // Arm at touchend, BEFORE synthetic click closes the project picker.
    deadline=clock()+MAX_INTERVAL;
   }
  }
  if(!(e.touches?.length))multi=false;
 },{capture:true,passive:false});
 document.addEventListener('touchcancel',e=>{
  const point=touchPoint(e);
  if(point?.identifier===blockedId)blockedId=null;
  if(point?.identifier===first?.identifier)first=null;
  if(!(e.touches?.length)){multi=false;deadline=-Infinity;}
 },{capture:true,passive:true});
 window.addEventListener('pagehide',()=>{first=null;deadline=-Infinity;blockedId=null;},{once:true});
})();
