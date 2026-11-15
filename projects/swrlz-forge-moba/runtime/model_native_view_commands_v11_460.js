/* SE460_NATIVE_VIEW_COMMANDS_START */
// Native-authoritative public view bridge. This code is inserted inside
// ModelAtelier's closure, where renderer, camera and viewport state exist.
// No DOM scraping, second scene or history changes.
const se460ModelView=Object.freeze((()=>{
 const allowed=new Set(['solid','shaded','overlay','wireframe','xray','flat','clay']);
 function inspect(){
  return {mode:atelierViewGlobal,available:!!modelRoot,
   camera:se430ModelCamera.inspect()?.view||'orbit',
   previewActive:typeof se430BeginnerAPI==='function'&&
      !!se430BeginnerAPI()?.inspect?.()?.preview?.active};
 }
 function setMode(next){
  if(!allowed.has(next)||!modelRoot)return false;
  if(atelierCameraInterior){
   status('Exit interior inspection before changing viewport shading.',true);
   return false;
  }
  if(atelierViewGlobal===next)return true;
  atelierViewGlobal=next;
  atelierViewOverrides.clear();
  const isPreview=inspect().previewActive;
  if(isPreview){
   // Do not call atelierViewRebuild/renderParts during a topology preview:
   // that would cancel Inset/Extrude. Apply only disposable presentation data.
   for(const mesh of modelRoot.children){
    if(!mesh?.isMesh||!mesh.userData?.atelierId)continue;
    const part=partById(mesh.userData.atelierId);
    if(!part)continue;
    const original=mesh.userData.se455OriginalMaterial||mesh.material;
    for(const child of [...mesh.children]){
     if(child.name!=='Viewport wireframe overlay'&&!child.userData?.se455DisplayEdges)continue;
     mesh.remove(child);
     if(child.userData?.se455OwnedGeometry)child.geometry?.dispose?.();
     child.material?.dispose?.();
    }
    if(mesh.material&&mesh.material!==original&&mesh.material.userData?.atelierViewportClone)
     mesh.material.dispose?.();
    mesh.material=original;
    atelierViewModeApply(mesh,part);
   }
   if(typeof renderPreview==='function')renderPreview();
  }else{
   atelierViewRebuild();
  }
  status('Viewport '+next+' · display only; model and Undo unchanged.');
  return true;
 }
 function setCamera(view){
  if(!['front','right','top','three'].includes(view))return false;
  if(inspect().previewActive){
   status('Set or cancel the mesh preview before changing the camera.',true);
   return false;
  }
  return se430ModelCamera.setView(view);
 }
 return {version:'v11.460',inspect,setMode,setCamera};
})());
/* SE460_NATIVE_VIEW_COMMANDS_END */