/* SE519_QUEST_BROWSER_TRANSFORM_START
  REGULAR 2D QUEST BROWSER ONLY. Immersive WebXR gets no new controller
  handlers, object transforms, project loader, or selection interactions. */
const se519QuestBrowserModel=(()=>{
 'use strict';
 let tap=null,boundsVisible=true,boundsButton=null,boundsApplied=0,toggleCount=0;
 const quest=()=>typeof se512QuestBrowser2D==='function'&&se512QuestBrowser2D();
 const canvas=()=>renderer?.domElement;
 const primary=e=>e&&e.button===0&&e.isPrimary!==false&&e.target===canvas();
 function onCanvas(e){
  const c=canvas(),r=c?.getBoundingClientRect();
  return !!c&&!!r&&r.width>0&&r.height>0&&
   e.clientX>=r.left&&e.clientX<=r.right&&e.clientY>=r.top&&e.clientY<=r.bottom&&
   primary(e);
 }
 function isObjectSelection(){
  return typeof atelierComponentMode==='undefined'||atelierComponentMode==='mesh';
 }
 function isGizmoGesture(){
  return !!(atelierMeshDrag||atelierComponentDrag||
   (typeof atelierPrecisionGizmoDrag!=='undefined'&&atelierPrecisionGizmoDrag));
 }
 function bounds(){
  if(!world?.traverse)return [];
  const result=[];
  world.traverse(o=>{
   // The native selection outline is a Three.js BoxHelper. Never hide
   // actual geometry, wireframe overlay, vertex markers, or workbench grid.
   if(o?.type==='BoxHelper'||o?.isBoxHelper||
    o?.constructor?.name==='BoxHelper')result.push(o);
  });
  return result;
 }
 function applyBounds(){
  for(const outline of bounds()){outline.visible=boundsVisible;boundsApplied++;}
  if(boundsButton){
   boundsButton.setAttribute('aria-pressed',String(boundsVisible));
   boundsButton.textContent=boundsVisible?'▧ Hide bounds':'▧ Show bounds';
   boundsButton.title=boundsVisible?'Hide selection boundary box only':'Show selection boundary box';
  }
 }
 function toggleBounds(){
  boundsVisible=!boundsVisible;toggleCount++;applyBounds();
  return boundsVisible;
 }
 function install(){
  if(!panel||panel.hidden)return;
  const host=panel.querySelector('.atelier-viewport-controls');
  if(!host)return;
  if(boundsButton&&!boundsButton.isConnected)boundsButton=null;
  if(!boundsButton){
   const button=document.createElement('button');
   button.id='se519SelectionBoundsToggle';button.type='button';
   button.setAttribute('aria-label','Show or hide the selected model bounding box');
   button.addEventListener('click',e=>{e.stopPropagation();toggleBounds();});
   host.append(button);boundsButton=button;
  }
  applyBounds();
 }
 function down(e){
  tap=null;
  if(!quest()||!onCanvas(e)||!isObjectSelection()||atelierMeshAdding)return;
  const before=selection;
  if(!before||!partById(before))return;
  const hit=se512QuestTapPick(e,{x:e.clientX,y:e.clientY});
  tap={pointerId:e.pointerId,x:e.clientX,y:e.clientY,part:before,
   hit,startedOnGizmo:isGizmoGesture(),wasDragged:false};
 }
 function afterDown(e){
  if(tap?.pointerId===e.pointerId&&isGizmoGesture())tap.startedOnGizmo=true;
 }
 function move(e){
  if(tap?.pointerId===e.pointerId&&Math.hypot(e.clientX-tap.x,e.clientY-tap.y)>12)
   tap.wasDragged=true;
 }
 function consume(e,wasGesture){
  const down=tap;tap=null;
  if(!down||!quest()||!onCanvas(e)||!isObjectSelection()||
   atelierMeshAdding||wasGesture||down.startedOnGizmo||down.wasDragged||
   down.pointerId!==e.pointerId||Math.hypot(e.clientX-down.x,e.clientY-down.y)>12)return false;
  if(down.hit!==down.part||selection!==down.part)return false;
  // Must still be clicking the same *visible mesh*, not blank space.
  if(se512QuestTapPick(e,down)!==down.part)return false;
  select(null);
  atelierMeshSelected(null);
  // Native select() also owns inspector/selection UI and gizmo cleanup.
  if(selection===down.part){
   // Older native variants ignore select(null). Complete deselection
   // through the existing source model and inspector rebuild path.
   selection=null;atelierMeshGizmoClear();renderParts();refreshInspector();refreshList();
  }
  if(typeof status==='function')status('Selection cleared.');
  return true;
 }
 const oldDown=pointerDown;
 pointerDown=function(e){
  down(e);const result=oldDown.apply(this,arguments);afterDown(e);return result;
 };
 const oldMove=pointerMove;
 pointerMove=function(e){move(e);return oldMove.apply(this,arguments);};
 const oldUp=pointerUp;
 pointerUp=function(e){
  const active=isGizmoGesture();
  const result=oldUp.apply(this,arguments);
  consume(e,active);return result;
 };
 const oldRender=renderParts;
 renderParts=function(...args){
  const result=oldRender.apply(this,args);
  queueMicrotask(()=>{if(world){applyBounds();install();}});
  return result;
 };
 const oldBuild=atelierMeshGizmoBuild;
 atelierMeshGizmoBuild=function(...args){
  const result=oldBuild.apply(this,args);applyBounds();return result;
 };
 const oldOpen=open;
 open=function(...args){const result=oldOpen.apply(this,args);
  queueMicrotask(install);return result;
 };
 const oldClose=close;
 close=function(...args){tap=null;return oldClose.apply(this,args);};
 return Object.freeze({isQuestBrowser2D:quest,toggleBounds,
  inspect:()=>({boundsVisible,boundsCount:bounds().length,
   boundsApplied,toggleCount,tapActive:!!tap,gizmoDragging:isGizmoGesture()})});
})();
window.SWYRL_ENGINE_QUEST_BROWSER_TRANSFORMS_519=se519QuestBrowserModel;
/* SE519_QUEST_BROWSER_TRANSFORM_END */