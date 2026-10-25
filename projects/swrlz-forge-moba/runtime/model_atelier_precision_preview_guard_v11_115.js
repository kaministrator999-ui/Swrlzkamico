// §E v11.115 — precision-cut preview cannot become a stranded "second ball".
// A cut preview is NOT a saved mesh; it must never masquerade as a selectable,
// independent object while the source moves. Neither guard creates checkpoints.
let atelierPrecisionGuardTap=null,atelierPrecisionGuardInstalled=false;
function atelierPrecisionGuardActive(){
 return !!(atelierPrecisionCircleDraft?.ghost&&
           atelierPrecisionCircleDraft?.sourceMesh);
}
function atelierPrecisionGuardWarn(){
 status('The holed ball is a PREVIEW, not a second mesh. Use the yellow Radius/purple Depth handles, then Apply this hole. Hide preview before moving/scaling the whole object.',true);
 const label=document.getElementById('modelAtelierBoreInfo');
 if(label)label.textContent='PREVIEW ONLY · Press Apply this hole to make the hole real. Mesh Move/Scale changes the entire sphere, not its hole.';
}
function atelierPrecisionGuardClear(reason){
 if(!atelierPrecisionGuardActive())return false;
 atelierPrecisionCircleClear();
 if(typeof atelierPrecisionGizmoQueue==='function')atelierPrecisionGizmoQueue();
 const label=document.getElementById('modelAtelierBoreInfo');
 if(label)label.textContent=reason||
  'The temporary cut preview was hidden when the editable model changed. Select the sphere and preview your cut again.';
 return true;
}
function atelierPrecisionGuardPreviewClick(){
 if(!atelierPrecisionGuardActive())return;
 const label=document.getElementById('modelAtelierBoreInfo');
 if(label)label.textContent+=' · PREVIEW ONLY — Apply this hole before treating it as saved geometry. Mesh tools move the whole part.';
}
function atelierPrecisionGuardPointerDown(event){
 if(event.target!==renderer?.domElement||!atelierPrecisionGuardActive()||
    event.button!==0||event.isPrimary===false||atelierSculptArmed||
    atelierPrecisionGizmoDrag)return;
 // Radius/depth handles already have their own document capture listeners.
 if(typeof atelierPrecisionGizmoHit==='function'&&
    atelierPrecisionGizmoHit(event))return;
 atelierPrecisionGuardTap={id:event.pointerId,x:event.clientX,y:event.clientY};
}
function atelierPrecisionGuardPointerUp(event){
 const tap=atelierPrecisionGuardTap;
 if(!tap||event.pointerId!==tap.id)return;
 atelierPrecisionGuardTap=null;
 if(!atelierPrecisionGuardActive()||atelierSculptArmed||
   Math.hypot(event.clientX-tap.x,event.clientY-tap.y)>9)return;
 const d=atelierPrecisionCircleDraft;
 if(!renderer||!camera||!d.ghost||!d.ghost.parent)return;
 const rect=renderer.domElement.getBoundingClientRect();
 if(!rect.width||!rect.height)return;
 const ndc=new THREE.Vector2(
  (event.clientX-rect.left)/rect.width*2-1,
  1-(event.clientY-rect.top)/rect.height*2);
 const ray=new THREE.Raycaster();
 ray.setFromCamera(ndc,camera);
 if(!ray.intersectObject(d.ghost,false).length)return;
 const id=d.originalId;
 atelierPrecisionGuardClear('Tapped the preview. Original editable part reselected; preview again to inspect, or Apply to save a new cut.');
 select(id);
 status('Selected the original editable sphere. The hole was a temporary preview; switch to Sculpt → Precision circle cut, preview again, and Apply to save it.');
 event.preventDefault?.();
 event.stopImmediatePropagation?.();
}
function atelierPrecisionGuardInstall(){
 if(atelierPrecisionGuardInstalled)return;
 atelierPrecisionGuardInstalled=true;
 // RenderParts is the central invalidation path for selecting, Undo, inspector
 // transforms, project import, deleting, and rebuilding mesh geometry.
 const priorRenderParts=renderParts;
 renderParts=function(...args){
  atelierPrecisionGuardClear();
  return priorRenderParts(...args);
 };
 // Mesh Move/Rotate/Scale gizmo must never drag the hidden source underneath
 // a stationary off-root preview. Block only actual hit on transform handles.
 if(typeof atelierMeshGizmoDown==='function'){
  const nativeMeshDown=atelierMeshGizmoDown;
  atelierMeshGizmoDown=function(event){
   if(atelierPrecisionGuardActive()&&renderer&&camera&&atelierMeshGizmo&&
      event.button===0){
    const q=point(event);
    const pickRay=new THREE.Raycaster();
    pickRay.setFromCamera(new THREE.Vector2(q.x,q.y),camera);
    const handles=atelierMeshGizmo.children.filter(x=>x.userData.meshGizmoAxis);
    if(pickRay.intersectObjects(handles,false).length){
     atelierPrecisionGuardWarn();
     event.preventDefault?.();
     return true;
    }
   }
   return nativeMeshDown(event);
  };
 }
 // Quick-strip +/- invokes this directly, bypassing viewport hit-testing.
 if(typeof atelierMeshNudge==='function'){
  const nativeNudge=atelierMeshNudge;
  atelierMeshNudge=function(...args){
   if(atelierPrecisionGuardActive()){
    atelierPrecisionGuardWarn();return;
   }
   return nativeNudge(...args);
  };
 }
 // Handle opening other model tools without leaving unselectable ghost mesh
 // behind. Preview only loses its temporary state; source data is untouched.
 const parts=document.getElementById('modelAtelierParts');
 parts?.addEventListener('change',()=>atelierPrecisionGuardClear());
 const preview=document.getElementById('modelAtelierBorePreview');
 preview?.addEventListener('click',atelierPrecisionGuardPreviewClick);
 document.addEventListener('pointerdown',atelierPrecisionGuardPointerDown,true);
 document.addEventListener('pointerup',atelierPrecisionGuardPointerUp,true);
 document.addEventListener('pointercancel',()=>{atelierPrecisionGuardTap=null;},true);
 const panel=document.getElementById('modelAtelierPanel');
 panel?.addEventListener('click',event=>{
  if(!atelierPrecisionGuardActive())return;
  const changeTool=event.target?.closest?.('[data-mode],[data-mesh-join],[data-mesh-group]');
  if(changeTool&&changeTool.hasAttribute('data-mode')){
   const mode=changeTool.getAttribute('data-mode');
   if(mode==='move'||mode==='rotate'||mode==='scale'){
    atelierPrecisionGuardWarn();
   }
  }
 },true);
}
