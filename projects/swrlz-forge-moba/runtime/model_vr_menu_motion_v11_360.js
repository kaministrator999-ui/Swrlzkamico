/* SE360_MODEL_VR_MENU_MOTION_START */
// Model VR owns the sole XR loop. The menu advances only inside that frame;
// geometric modeling and camera controls remain in their native dispatchers.
const se360MenuMotionPreference=typeof window.matchMedia==='function'
 ?window.matchMedia('(prefers-reduced-motion: reduce)'):null;
function se360AdvanceMenu(dt){
 const s=se340XR,ui=s.ui;if(!ui)return;
 ui.tick?.(Math.max(0,Math.min(.05,Number(dt)||0)),{
  visible:!!s.paletteVisible&&!!ui.root.visible&&se340VisibleSession(),
  reducedMotion:!!se360MenuMotionPreference?.matches
 });
}
function se360MenuContact(record){
 const ui=se340XR.ui;
 if(!ui?.root.visible||!se340VisibleSession())return null;
 const cast=se340Cast(record);if(!cast)return null;
 const hit=ui.hitTest(cast);if(!hit)return null;
 return {ui:true,target:hit.object,action:hit.object.userData.se340Action||null,
  distance:hit.distance,point:hit.point};
}
/* SE360_MODEL_VR_MENU_MOTION_END */
