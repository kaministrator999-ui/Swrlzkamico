/* SE461_HARD_SURFACE_ORBIT_START */
// All functions here run INSIDE ModelAtelier's native closure. Display-only
// helpers must not replace source topology, UVs, selection IDs or Undo state.
function se461LowPolyEditable(part,mesh){
 const g=mesh?.geometry,i=g?.getIndex?.();
 return part?.kind==='topologyMesh'&&i?.count>=3&&i.count<=360
   &&g?.getAttribute?.('position')?.count<=240;
}
function se461ModelOrbitBounds(){
 if(!modelRoot)return null;
 const meshes=modelRoot.children.filter(m=>m?.isMesh&&m.visible!==false&&m.userData?.atelierId);
 const chosen=meshes.find(m=>m.userData.atelierId===selection);
 const list=chosen?[chosen]:meshes;
 if(!list.length)return null;
 modelRoot.updateWorldMatrix?.(true,true);
 const box=new THREE.Box3();
 for(const mesh of list)box.expandByObject(mesh);
 if(box.isEmpty())return null;
 return {center:box.getCenter(new THREE.Vector3()),radius:box.getSize(new THREE.Vector3()).length()*.5,selected:!!chosen};
}
function se461AlignOrbitPivot(){
 if(atelierCameraInterior||!camera||!modelRoot)return false;
 const bounds=se461ModelOrbitBounds();
 if(!bounds)return false;
 const target=(atelierDetailTarget||new THREE.Vector3(0,model()?.assemblies?2.8:2.35,0)).clone().add(atelierCameraPan);
 const drift=target.distanceTo(bounds.center);
 // Orbit is object-centered by default. Pan remains a two-finger gesture,
 // but a NEW orbit gesture reacquires the selected mesh / whole model.
 if(drift<=.065)return false;
 atelierDetailTarget=bounds.center;
 atelierCameraPan.set(0,0,0);
 cameraUpdate(); // changes center only, NEVER yaw/pitch/distance.
 return true;
}
// Native View pipelines own the surface. Solid and Flat receive a small,
// depth-tested silhouette/crease overlay even when the user hasn't selected
// the part yet. Shaded Wire already owns its own native edge renderer.
const se461PreviousViewApply=atelierViewModeApply;
atelierViewModeApply=function(mesh,part){
 const result=se461PreviousViewApply.apply(this,arguments);
 if(!se461LowPolyEditable(part,mesh))return result;
 const mode=atelierViewModeFor(part);
 if(mode==='overlay'){
  // Preserve the actual authored base colour/material, just display correct
  // planar shading on an independent VIEW-ONLY material clone.
  const original=mesh.material;
  if(original&&!Array.isArray(original)&&!original.flatShading){
   const copy=original.clone();
   copy.flatShading=true;
   copy.needsUpdate=true;
   copy.userData={...original.userData,atelierViewportClone:true,se461SharpSurface:true};
   mesh.material=copy;
  }
 }else if(['solid','flat','clay'].includes(mode)){
  // The native Solid/Flat material uses per-face normals on bounded
  // editable meshes; this line overlay distinguishes outer and inset edges.
  if(!mesh.children.some(c=>c.userData?.se461HardEdges)){
   const geom=new THREE.EdgesGeometry(mesh.geometry,25);
   const mat=new THREE.LineBasicMaterial({color:0x27435a,
    transparent:true,opacity:.88,depthTest:true,depthWrite:false});
   const line=new THREE.LineSegments(geom,mat);
   line.name='Editable hard edge guide';
   line.userData.atelierHelper=true;
   line.userData.se455DisplayEdges=true;
   line.userData.se455OwnedGeometry=true;
   line.userData.se461HardEdges=true;
   line.renderOrder=8;
   mesh.add(line);
  }
 }
 return result;
};
window.SWYRL_ENGINE_MODEL_HARD_SURFACE_461=Object.freeze({
 version:'v11.461',
 alignOrbit:se461AlignOrbitPivot,
 inspect:()=>({bounds:se461ModelOrbitBounds()?.center.toArray()||null,
  cameraPivot:(atelierDetailTarget||new THREE.Vector3(0,model()?.assemblies?2.8:2.35,0)).clone().add(atelierCameraPan).toArray(),
  distance:orbit.distance,yaw:orbit.yaw,pitch:orbit.pitch})
});
/* SE461_HARD_SURFACE_ORBIT_END */