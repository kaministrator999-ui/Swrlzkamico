/* SE458_MODEL_VIEWPORT_STABILITY_START */
// Non-destructive, selected-object outline and geometry-aware orbit pivot.
// Existing native camera, topology preview, renderer and model material own all
// state. No independent render loop, geometry edit or camera distance reset.
(function(){
 'use strict';
 let queued=false, lastFocusPart=null;
 const scene=()=>typeof modelRoot!=='undefined'?modelRoot:null;
 function selected(part){return part?.id===selection;}
 function eligible(mesh,part){
  if(!mesh?.isMesh||!mesh.geometry||!selected(part)||mesh.isSkinnedMesh)return false;
  const mode=atelierViewModeFor(part);
  if(!['solid','flat','clay'].includes(mode))return false;
  const triangles=(mesh.geometry.index?.count||mesh.geometry.getAttribute?.('position')?.count||0)/3;
  return triangles>0&&triangles<=5000;
 }
 function clear(mesh){
  if(!mesh?.children)return;
  for(const child of [...mesh.children]){
   if(!child.userData?.se458Contour)continue;
   mesh.remove(child);
   child.geometry?.dispose?.();child.material?.dispose?.();
  }
 }
 function update(mesh,part){
  if(!eligible(mesh,part)){clear(mesh);return;}
  const current=mesh.children.find(x=>x.userData?.se458Contour);
  if(current?.userData?.sourceGeometry===mesh.geometry)return;
  clear(mesh);
  let geometry=null,material=null;
  try{
   geometry=new THREE.EdgesGeometry(mesh.geometry,20);
   material=new THREE.LineBasicMaterial({
    color:0x18354e,transparent:true,opacity:.96,
    depthTest:true,depthWrite:false
   });
   const edge=new THREE.LineSegments(geometry,material);
   edge.name='Selected face and silhouette edges';
   edge.userData.atelierHelper=true;
   edge.userData.se455DisplayEdges=true;
   edge.userData.se455OwnedGeometry=true;
   edge.userData.se458Contour=true;
   edge.userData.sourceGeometry=mesh.geometry;
   edge.renderOrder=9;
   mesh.add(edge);
   // Only the pre-existing viewport-only solid material gets the offset.
   // Authored PBR materials, source topology and UVs remain untouched.
   if(mesh.material?.userData?.atelierViewportClone){
    mesh.material.polygonOffset=true;
    mesh.material.polygonOffsetFactor=1;
    mesh.material.polygonOffsetUnits=1;
   }
  }catch(_){geometry?.dispose?.();material?.dispose?.();}
 }
 const beforeViewApply=atelierViewModeApply;
 atelierViewModeApply=function(mesh,part){
  const result=beforeViewApply.apply(this,arguments);
  update(mesh,part);
  return result;
 };
 function syncEdges(){
  const root=scene();
  if(!root)return;
  for(const mesh of root.children){
   if(!mesh?.isMesh||!mesh.userData?.atelierId)continue;
   const part=partById(mesh.userData.atelierId);
   update(mesh,part);
  }
 }
 function selectedCenter(partId){
  const root=scene();
  const mesh=root?.children?.find?.(m=>m.isMesh&&m.userData?.atelierId===partId);
  if(!mesh)return null;
  root.updateWorldMatrix?.(true,true);
  const box=new THREE.Box3().setFromObject(mesh);
  if(box.isEmpty())return null;
  return {center:box.getCenter(new THREE.Vector3()),
    radius:box.getSize(new THREE.Vector3()).length()*.5};
 }
 function focusIfDetached(state){
  if(!state?.selection?.partId||state?.preview?.active||atelierCameraInterior)return;
  const partId=state.selection.partId;
  if(state.selection.mode!=='face'&&state.selection.mode!=='edge')return;
  const geometry=selectedCenter(partId);
  if(!geometry)return;
  const cameraInfo=se430ModelCamera.inspect?.();
  const target=cameraInfo?.target;
  if(!Array.isArray(target)||target.length<3)return;
  const pivot=new THREE.Vector3(...target);
  const delta=pivot.distanceTo(geometry.center);
  // A mesh may move legitimately. Correct only a pivot demonstrably outside
  // the selected object's local geometry, not ordinary slight camera pans.
  if(delta<=Math.max(.75,geometry.radius*.78))return;
  atelierDetailTarget=geometry.center;
  atelierCameraPan.set(0,0,0);
  cameraUpdate(); // preserves orbit yaw, pitch and distance (zoom).
  lastFocusPart=partId;
 }
 function onNativeChange(event){
  const state=event?.detail;
  if(queued)return;
  const needsFocus=!!state&&/^Applied (?:inset|extrude) to native geometry\b/i.test(state.message||'');
  queued=true;
  queueMicrotask(()=>requestAnimationFrame(()=>{
   queued=false;
   syncEdges();
   if(needsFocus)focusIfDetached(state);
  }));
 }
 window.addEventListener('swrlz:model-workshop-change',onNativeChange);
 window.SWYRL_ENGINE_MODEL_VIEW_STABILITY_458=Object.freeze({
  version:'v11.458',refresh:syncEdges,correctFocus:focusIfDetached,
  inspect:()=>({lastFocusedPart:lastFocusPart,hasModel:!!scene()})
 });
})();
/* SE458_MODEL_VIEWPORT_STABILITY_END */
