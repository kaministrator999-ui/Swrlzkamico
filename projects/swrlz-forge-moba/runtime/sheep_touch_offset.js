// Touch construction aims in screen space above the finger. The native ground
// picker, collision check, preview and build command still share one target.
const stTouchPlacement = {
  gesture:null, context:null, blockedPointers:new Set(), touchPointers:new Set(), desiredOffsetPx:64,
  rawScreen:null, targetScreen:null, offsetPx:0, ground:null, fit:null,
  valid:false, clamped:false, reason:null, resetReason:'initial', lastCommitted:null
};
function stTouchPlacementEnabled() {
  if (!stSession || stSession.simulate || !stUi.shown || !stUi.build || paused || stSession.winner ||
      stSession.role !== 'sheep') return false;
  const unit=stSession.units.find(item=>item.id===stSession.controlledId);
  return !!unit && unit.kind==='sheep' && !unit.captured;
}
function stTouchPlacementHide(reason) {
  if (stUi.preview) stUi.preview.visible=false;
  if (stUi.footprint) stUi.footprint.visible=false;
  if (stPlacementGridState.guide) stPlacementGridState.guide.root.visible=false;
  stUi.placement=null; stUi.placementPoint=null;
  if (reason) {
    stUiText('stPlacement',reason); $('stPlacement')?.classList.add('error');
  }
}
function stTouchPlacementReset(reason, suppressRelease=false, clearReceipt=false) {
  const gesture=stTouchPlacement.gesture;
  if (suppressRelease && gesture) stTouchPlacement.blockedPointers.add(gesture.id);
  stTouchPlacement.gesture=null; stTouchPlacement.context=null;
  stTouchPlacement.rawScreen=null; stTouchPlacement.targetScreen=null;
  stTouchPlacement.ground=null; stTouchPlacement.fit=null; stTouchPlacement.offsetPx=0;
  stTouchPlacement.valid=false; stTouchPlacement.clamped=false; stTouchPlacement.reason=null;
  stTouchPlacement.resetReason=reason;
  if (gesture && stUi.drag?.id===gesture.id) stUi.drag=null;
  if (clearReceipt) stTouchPlacement.lastCommitted=null;
}
function stTouchPlacementSync() {
  const gesture=stTouchPlacement.gesture;
  if (gesture && (!stTouchPlacementEnabled() || gesture.session!==stSession || gesture.kind!==stUi.build))
    stTouchPlacementReset('session or build mode changed',true);
}
function stTouchPlacementClearCanvas(x,y) {
  const viewport=$('viewport'), rect=viewport?.getBoundingClientRect();
  return !!rect && x>=rect.left && x<rect.right && y>=rect.top && y<rect.bottom &&
    document.elementFromPoint(x,y)===viewport;
}
function stTouchPlacementScreen(clientX,clientY) {
  const rect=$('viewport').getBoundingClientRect();
  let top=rect.top+12;
  // Keep the target below the top readouts. Near their edge the offset becomes
  // smaller, rather than pushing the ghost into the score and phase controls.
  for (const selector of ['.st-score','.st-phase','.st-event','.st-attack-feedback']) {
    const node=$('sheepTagHUD')?.querySelector(selector);
    if (!node || node.hidden || !node.getClientRects().length) continue;
    const bounds=node.getBoundingClientRect();
    if (clientX>=bounds.left-16 && clientX<=bounds.right+16) top=Math.max(top,bounds.bottom+24);
  }
  const targetY=Math.min(clientY,Math.max(clientY-stTouchPlacement.desiredOffsetPx,top));
  const target=[clientX,targetY];
  const valid=stTouchPlacementClearCanvas(clientX,clientY) && stTouchPlacementClearCanvas(...target);
  return {raw:[clientX,clientY],target,offsetPx:clientY-targetY,
    clamped:targetY>clientY-stTouchPlacement.desiredOffsetPx+.01,valid,
    reason:valid?null:'Aim on clear ground, away from the controls.'};
}
const stTouchPlacementOriginalGround=stUiGround;
function stTouchPlacementGround(clientX,clientY) {
  const screen=stTouchPlacementScreen(clientX,clientY);
  Object.assign(stTouchPlacement,{rawScreen:screen.raw,targetScreen:screen.target,
    offsetPx:screen.offsetPx,clamped:screen.clamped,valid:screen.valid,reason:screen.reason,ground:null,fit:null});
  if (!screen.valid) {stTouchPlacementHide(screen.reason); return null;}
  let point=stTouchPlacementOriginalGround(...screen.target);
  // Solve against the native terrain height so sloped ground also appears at
  // the screen target. This changes only touch building aim, never movement.
  for (let step=0;point && step<6;step++) {
    const height=terrainHeight(point.x,point.z);
    if (!Number.isFinite(height)) {point=null; break;}
    const next=stTouchPlacementOriginalGround(...screen.target,height);
    if (!next) {point=null; break;}
    const difference=next.distanceToSquared(point); point=next;
    if (difference<1e-8) break;
  }
  if (!point || ![point.x,point.y,point.z].every(Number.isFinite)) {
    stTouchPlacement.valid=false; stTouchPlacement.reason='Aim at visible ground.';
    stTouchPlacementHide(stTouchPlacement.reason); return null;
  }
  stTouchPlacement.ground=point.toArray();
  return point;
}
stUiGround=function(clientX,clientY,height=0) {
  const context=stTouchPlacement.context;
  if (height===0 && context && stTouchPlacementEnabled() &&
      Math.abs(clientX-context.x)<.01 && Math.abs(clientY-context.y)<.01)
    return stTouchPlacementGround(clientX,clientY);
  return stTouchPlacementOriginalGround(clientX,clientY,height);
};
const stTouchPlacementOriginalPreview=stUiPlacePreview;
stUiPlacePreview=function(point) {
  const result=stTouchPlacementOriginalPreview(point);
  if (stTouchPlacement.gesture && stTouchPlacement.context && stUi.placement) {
    const fit=stUi.placement;
    stTouchPlacement.fit={x:fit.x,z:fit.z,rotation:fit.rotation ?? stUi.rotation,
      ok:!!fit.ok,corners:fit.corners?structuredClone(fit.corners):null};
  }
  if (stTouchPlacement.gesture && !stTouchPlacement.valid) stTouchPlacementHide(stTouchPlacement.reason);
  return result;
};
const stTouchPlacementOriginalOrder=stUiOrderAt;
stUiOrderAt=function(clientX,clientY) {
  const context=stTouchPlacement.context;
  const released=context?.type==='pointerup' ? stTouchPlacement.gesture : null;
  try {
    if (context && stUi.build && !stTouchPlacement.valid) {
      stUiFeedback(stTouchPlacement.reason || 'Aim on clear ground, away from the controls.',true); return;
    }
    return stTouchPlacementOriginalOrder(clientX,clientY);
  } finally {
    // End the gesture synchronously after the native release order. Timer
    // cleanup remains a fallback when the viewport does not receive an order.
    if (released && stTouchPlacement.gesture===released) stTouchPlacementReset('touch released');
    if (released) stTouchPlacement.blockedPointers.delete(released.id);
  }
};
const stTouchPlacementOriginalCommand=stUiCommand;
stUiCommand=function(action,payload={}) {
  const context=stTouchPlacement.context;
  const receipt=action==='build' && context?.type==='pointerup' && stTouchPlacement.valid ? {
    kind:payload.kind,x:payload.x,z:payload.z,rotation:payload.rotation ?? stUi.rotation,
    rawScreen:[...stTouchPlacement.rawScreen],targetScreen:[...stTouchPlacement.targetScreen],
    ground:[...stTouchPlacement.ground],offsetPx:stTouchPlacement.offsetPx,
    clamped:stTouchPlacement.clamped
  }:null;
  const result=stTouchPlacementOriginalCommand(action,payload);
  if (receipt && result?.ok) stTouchPlacement.lastCommitted=receipt;
  return result;
};
const stTouchPlacementOriginalClear=stUiClearPreview;
stUiClearPreview=function() {
  // A touch that began before a mode change must finish before it can place
  // the newly chosen building. Normal mouse drag behavior remains unchanged.
  for (const id of stTouchPlacement.touchPointers) stTouchPlacement.blockedPointers.add(id);
  if (stUi.drag?.touch) stUi.drag=null;
  stTouchPlacementReset('preview or build mode cleared',true);
  return stTouchPlacementOriginalClear();
};
const stTouchPlacementOriginalCamera=stUpdateCamera;
stUpdateCamera=function(dt=0) {
  const result=stTouchPlacementOriginalCamera(dt);
  stTouchPlacementSync();
  const gesture=stTouchPlacement.gesture;
  // The regular native frame updates this ghost while the camera follows,
  // zooms or resizes. There is no second render loop or fixed world offset.
  if (gesture) {
    const point=stTouchPlacementGround(gesture.x,gesture.y);
    if (point) {
      const previous=stTouchPlacement.context;
      stTouchPlacement.context={x:gesture.x,y:gesture.y,type:'camera'};
      try {stUiPlacePreview(point);} finally {stTouchPlacement.context=previous;}
    }
  }
  return result;
};
const stTouchPlacementOriginalHUD=stRefreshHUD;
stRefreshHUD=function(force=false) {
  stTouchPlacementSync(); const result=stTouchPlacementOriginalHUD(force);
  if (stUi.build && (stTouchPlacement.gesture || matchMedia('(pointer:coarse)').matches))
    stUiText('stTip','Drag to aim above your finger; release to place. Green fits; red is blocked.');
  return result;
};
const stTouchPlacementOriginalStatus=stUiStatus;
stUiStatus=function() {
  stTouchPlacementSync();
  return {...stTouchPlacementOriginalStatus(),touchPlacement:{
    active:!!stTouchPlacement.gesture,desiredOffsetPx:stTouchPlacement.desiredOffsetPx,
    offsetPx:stTouchPlacement.offsetPx,rawScreen:stTouchPlacement.rawScreen?[...stTouchPlacement.rawScreen]:null,
    targetScreen:stTouchPlacement.targetScreen?[...stTouchPlacement.targetScreen]:null,
    ground:stTouchPlacement.ground?[...stTouchPlacement.ground]:null,
    fit:stTouchPlacement.fit?structuredClone(stTouchPlacement.fit):null,
    valid:stTouchPlacement.valid,clamped:stTouchPlacement.clamped,reason:stTouchPlacement.reason,
    resetReason:stTouchPlacement.resetReason,
    lastCommitted:stTouchPlacement.lastCommitted?structuredClone(stTouchPlacement.lastCommitted):null
  }};
};
const stTouchPlacementOriginalShow=stShowHUD;
stShowHUD=function(show) {
  stTouchPlacementReset('HUD session changed',true,true);
  return stTouchPlacementOriginalShow(show);
};
const stTouchPlacementOriginalDispose=stDisposeUI;
stDisposeUI=function() {
  stTouchPlacementReset('Stop',true,true); return stTouchPlacementOriginalDispose();
};
function stTouchPlacementConsume(event) {
  event.preventDefault(); event.stopImmediatePropagation();
}
function stTouchPlacementContext(event) {
  const context={x:event.clientX,y:event.clientY,type:event.type};
  stTouchPlacement.context=context;
  // A task runs after the complete native event dispatch. A microtask can run
  // between capture listeners for real browser input and would clear too soon.
  setTimeout(()=>{if(stTouchPlacement.context===context)stTouchPlacement.context=null;},0);
}
window.addEventListener('pointerdown',event=>{
  stTouchPlacementSync();
  // A new press is a new gesture even when a browser reuses a cancelled ID.
  stTouchPlacement.blockedPointers.delete(event.pointerId);
  if (event.pointerType==='touch') stTouchPlacement.touchPointers.add(event.pointerId);
  const gesture=stTouchPlacement.gesture;
  if (event.pointerType==='touch' && (event.isPrimary===false || stTouchPlacement.touchPointers.size>1) &&
      (gesture || stTouchPlacementEnabled())) {
    stTouchPlacement.blockedPointers.add(event.pointerId);
    stTouchPlacementReset('multiple touch pointers',true);
    stTouchPlacementHide('Use one finger to aim; release, then try again.');
    stTouchPlacementConsume(event); return;
  }
  if (gesture && (event.pointerType!=='touch' || event.target!==$('viewport'))) {
    stTouchPlacementReset('another input or control',true);
  }
  if (!stTouchPlacementEnabled() || event.pointerType!=='touch' || event.target!==$('viewport') ||
      event.button!==0 || stUi.keys.has(' ')) return;
  stTouchPlacement.gesture={id:event.pointerId,x:event.clientX,y:event.clientY,
    session:stSession,kind:stUi.build};
  stTouchPlacementContext(event);
},true);
window.addEventListener('pointermove',event=>{
  stTouchPlacementSync();
  if (stTouchPlacement.blockedPointers.has(event.pointerId)) {stTouchPlacementConsume(event); return;}
  let gesture=stTouchPlacement.gesture;
  if (gesture && event.pointerType!=='touch' && event.target===$('viewport')) {
    stTouchPlacementReset('mouse input',true); gesture=null;
  }
  if (!gesture || gesture.id!==event.pointerId) return;
  gesture.x=event.clientX; gesture.y=event.clientY; stTouchPlacementContext(event);
},true);
window.addEventListener('pointerup',event=>{
  stTouchPlacementSync();
  stTouchPlacement.touchPointers.delete(event.pointerId);
  if (stTouchPlacement.blockedPointers.delete(event.pointerId)) {stTouchPlacementConsume(event); return;}
  const gesture=stTouchPlacement.gesture;
  if (!gesture || gesture.id!==event.pointerId) return;
  gesture.x=event.clientX; gesture.y=event.clientY; stTouchPlacementContext(event);
  // Validate release coordinates even when the last move was somewhere else.
  stTouchPlacementGround(event.clientX,event.clientY);
  setTimeout(()=>{
    if (stTouchPlacement.gesture===gesture) stTouchPlacementReset('touch released');
    if (!stTouchPlacement.touchPointers.has(event.pointerId))
      stTouchPlacement.blockedPointers.delete(event.pointerId);
  },0);
},true);
window.addEventListener('pointercancel',event=>{
  stTouchPlacement.touchPointers.delete(event.pointerId);
  stTouchPlacement.blockedPointers.delete(event.pointerId);
  if (stTouchPlacement.gesture?.id!==event.pointerId) return;
  stTouchPlacementReset('touch cancelled'); stTouchPlacementHide(null);
},true);
window.addEventListener('blur',()=>{
  stTouchPlacement.touchPointers.clear();
  stTouchPlacementReset('window blur',true); stTouchPlacementHide(null);
});
document.addEventListener('visibilitychange',()=>{
  if (document.hidden) {
    stTouchPlacement.touchPointers.clear();
    stTouchPlacementReset('document hidden',true); stTouchPlacementHide(null);
  }
});
// On a short landscape phone the original full-width command panel covers
// the playfield. Keep controls scrollable to one side while the finger aims.
const stTouchPlacementStyle=document.createElement('style');
stTouchPlacementStyle.id='sheepTouchPlacementStyles';
stTouchPlacementStyle.textContent=`
@media (pointer:coarse) and (min-width:621px) and (max-height:520px){
  .sheep-tag-runtime #sheepTagHUD .st-commandbar{left:auto;right:12px;width:344px;max-width:calc(100vw - 24px);max-height:calc(100vh - 215px);overflow-y:auto;display:block;box-sizing:border-box;margin:0}
  .sheep-tag-runtime #sheepTagHUD .st-commandbar .st-map{display:none}
  .sheep-tag-runtime #sheepTagHUD .st-commandbar .st-camera{flex-wrap:wrap}
  .sheep-tag-runtime #sheepTagHUD .st-commandbar .st-camera>span{display:none}
}`;
document.head.append(stTouchPlacementStyle);
