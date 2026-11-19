/* SE520_QUEST_BROWSER_PICK_START
 * REGULAR QUEST BROWSER 2D ONLY. Authoritative surface selection excludes
 * BoxHelper geometry; gizmo pointer capture and immersive XR stay separate.
 */
const se520QuestPick=(()=>{
 'use strict';
 let corrected=0,cleared=0;
 const nativeUp=pointerUp;
 pointerUp=function(event){
  const quest=typeof se512QuestBrowser2D==='function'&&se512QuestBrowser2D();
  const canvas=renderer?.domElement;
  const start=pressed?{x:pressed.x,y:pressed.y,moved:pressed.moved}:null;
  const before=selection;
  const transforming=!!atelierMeshDrag||!!atelierComponentDrag||
    (typeof atelierPrecisionGizmoDrag!=='undefined'&&!!atelierPrecisionGizmoDrag);
  let surface=null;
  if(quest&&canvas&&event.target===canvas&&event.button===0&&start&&!start.moved&&
    Math.hypot(event.clientX-start.x,event.clientY-start.y)<16&&
    !transforming&&!atelierMeshAdding&&atelierComponentMode==='mesh'){
    surface=se512QuestTapPick(event,start);
  }
  const result=nativeUp.apply(this,arguments);
  if(!quest||!start||!surface||transforming||
     (typeof atelierMeshDrag!=='undefined'&&!!atelierMeshDrag)||atelierMeshAdding)return result;
  if(before===surface){
   // The v11.519 toggle normally clears selection; ensure native helper
   // picking cannot immediately reselect the bounding box after it.
   if(selection!==null){
    selection=null;
    atelierMeshSelected(null);
    atelierMeshGizmoClear();renderParts();refreshInspector();refreshList();
    cleared++;
   }
  }else if(selection!==surface){
   select(surface);corrected++;
  }
  return result;
 };
 return Object.freeze({inspect:()=>({correctedSurfaceSelections:corrected,
   clearedHelperSelections:cleared})});
})();
window.SWYRL_ENGINE_QUEST_BROWSER_PICK_520=se520QuestPick;
/* SE520_QUEST_BROWSER_PICK_END */
