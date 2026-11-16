/* SE473_UV_SCREEN_DRAG_START */
// Lives inside se355UVEditor. Keep the popup and UV widgets parented to the
// model editor, preserving native event listeners and styling. Position is
// fixed to the browser content viewport, not the 3D rendering surface.
const se473UVWindowKey='swyrl.engine.modeler.uv-window.v1';
function safeBounds(){
 const v=window.visualViewport;
 const left=(v?.offsetLeft||0)+6,top=(v?.offsetTop||0)+6;
 const width=v?.width||innerWidth,height=v?.height||innerHeight;
 return {left,top,right:left+Math.max(0,width-12),bottom:top+Math.max(0,height-12)};
}
function se473SavedWindow(){
 try{
  const saved=JSON.parse(localStorage.getItem(se473UVWindowKey)||'null');
  if(!saved||!['left','top','width','height'].every(key=>
      Number.isFinite(saved[key])))return null;
  return saved;
 }catch{return null;}
}
function se473RememberWindow(){
 if(!popup||popup.hidden)return;
 const rect=popup.getBoundingClientRect();
 if(rect.width<100||rect.height<100)return;
 try{
  localStorage.setItem(se473UVWindowKey,JSON.stringify({
   left:rect.left,top:rect.top,width:rect.width,height:rect.height
  }));
 }catch{}
}
function se473Clamp(value,low,high){
 return Math.max(low,Math.min(high,value));
}
function fitWindow(reset=false){
 if(!popup||popup.hidden)return;
 const b=safeBounds();
 const freeWidth=Math.max(1,b.right-b.left),freeHeight=Math.max(1,b.bottom-b.top);
 const saved=reset?se473SavedWindow():null;
 const rect=popup.getBoundingClientRect();
 const desiredW=saved?.width??(reset?Math.min(440,freeWidth):rect.width||440);
 const desiredH=saved?.height??(reset?Math.min(650,freeHeight*.72):rect.height||650);
 const width=se473Clamp(desiredW,Math.min(140,freeWidth),freeWidth);
 const height=se473Clamp(desiredH,Math.min(116,freeHeight),freeHeight);
 const initialLeft=reset?b.right-width-10:rect.left;
 const initialTop=reset?Math.min(b.top+70,b.bottom-height):rect.top;
 const x=se473Clamp(saved?.left??initialLeft,b.left,Math.max(b.left,b.right-width));
 const y=se473Clamp(saved?.top??initialTop,b.top,Math.max(b.top,b.bottom-height));
 Object.assign(popup.style,{
  width:width+'px',height:height+'px',
  maxWidth:freeWidth+'px',maxHeight:freeHeight+'px',
  left:x+'px',top:y+'px',right:'auto',bottom:'auto'
 });
}
/* SE473_UV_SCREEN_DRAG_END */
