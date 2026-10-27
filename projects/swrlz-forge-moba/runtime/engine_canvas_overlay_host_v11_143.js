// §E v11.143: the renderer's #viewport is a CANVAS, not an HTML container.
// Children appended to a <canvas> are fallback content: invisible even if
// present in the DOM. Mount editable GUI and runtime menus in its MAIN wrapper.
function se143ViewportHost(){
 const canvas=$('viewport');
 if(!canvas)return null;
 return canvas.tagName==='CANVAS'?canvas.parentElement:canvas;
}
function se143Mount(element){
 const host=se143ViewportHost();
 if(!host||!element)return false;
 if(element.parentElement!==host)host.appendChild(element);
 return true;
}
function se143FitCanvasRect(){
 const canvas=$('viewport'),host=se143ViewportHost();
 if(!canvas||!host)return;
 const a=canvas.getBoundingClientRect(),b=host.getBoundingClientRect();
 if(a.width<1||a.height<1)return;
 for(const overlay of [seLevels.preview,seLevels.overlay]){
  if(!overlay||overlay.parentElement!==host)continue;
  overlay.classList.toggle('se143-compact',a.height<350);
  // The native MAIN container can be content-sized on mobile even while
  // WebGL's canvas occupies the full editor panel. Constrain HTML to the
  // ACTUAL displayed canvas bounds, never the parent's intrinsic height.
  const style=overlay.style;
  style.setProperty('position','absolute','important');
  style.setProperty('inset','auto','important');
  style.setProperty('left',(a.left-b.left)+'px','important');
  style.setProperty('top',(a.top-b.top)+'px','important');
  style.setProperty('width',a.width+'px','important');
  style.setProperty('height',a.height+'px','important');
  style.setProperty('max-height','none','important');
  style.setProperty('box-sizing','border-box','important');
 }
}
function se143RehomeProjectGui(){
 se143Mount(seLevels.bar);        // editor Project Levels/New Map/Play Game
 se143Mount(seLevels.preview);    // noninteractive editable menu layout
 se143Mount(seLevels.overlay);    // actual clickable Start Game in Play
 se143FitCanvasRect();
}
// Supersede the v11.142 relocation, which placed the toolbar inside CANVAS.
se142MoveLevelBar=function(){
 return se143Mount(seLevels.bar);
};
const se143EnsureUIBase=seLevelsEnsureUI;
seLevelsEnsureUI=function(...args){
 const result=se143EnsureUIBase(...args);
 se143RehomeProjectGui();
 return result;
};
const se143RefreshBase=seLevelsRefresh;
seLevelsRefresh=function(...args){
 const result=se143RefreshBase(...args);
 se143RehomeProjectGui();
 return result;
};
const se143MenuPlayBase=seLevelsPlayMenu;
seLevelsPlayMenu=function(...args){
 const result=se143MenuPlayBase(...args);
 if(result){
  se143RehomeProjectGui();
  // Keep native menu actor dynamics/camera; change DOM parent ONLY.
  seLevels.overlay?.querySelector('#st141StartGame')?.removeAttribute('disabled');
 }
 return result;
};
// On device rotation/resize the camera canvas changes size; keep its
// interface aligned without creating another render/game simulation loop.
window.addEventListener('resize',se143FitCanvasRect,{passive:true});
if(typeof ResizeObserver!=='undefined'){
 const canvas=$('viewport');
 if(canvas)new ResizeObserver(se143FitCanvasRect).observe(canvas);
}
// Handoff Stop relies on seLevelsStopMenu, which owns its own teardown and
// reverts authored transforms. Do not alter Save/Load, gameplay or physics.
const se143PreviousStatus=window.SWYRL_ENGINE_LEVELS.status;
window.SWYRL_ENGINE_LEVELS.status=function(){
 const original=se143PreviousStatus();
 const host=se143ViewportHost(),menu=seLevels.overlay;
 const bounds=menu?.getBoundingClientRect();
 return {...original,
  editorGuiHost:host?.tagName||null,
  editorGuiMounted:!!host&&seLevels.bar?.parentElement===host,
  runtimeGuiMounted:!!host&&!!menu&&menu.parentElement===host,
  runtimeGuiVisible:!!bounds&&bounds.width>1&&bounds.height>1
 };
};
