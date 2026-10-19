// §E v11.52: camera-plane-exact pixel brush sizing at the user's chosen point.
// This is an authoring-time conversion, not a saved camera-dependent brush.
// Both local radii are frozen into the standard native stroke data on Apply.
function atelierBrushLocalRadiusFromPixels(mesh,view,element,localCenter,pixels){
 if(!mesh?.isMesh||!view||!element||!(localCenter instanceof THREE.Vector3)||
   !Number.isFinite(pixels)||pixels<4||pixels>200)return null;
 const rect=element.getBoundingClientRect();
 if(!(rect.width>20&&rect.height>20))return null;
 view.updateMatrixWorld();
 if(view.updateProjectionMatrix)view.updateProjectionMatrix();
 mesh.updateWorldMatrix(true,false);
 const center=mesh.localToWorld(localCenter.clone());
 const ndc=center.clone().project(view);
 if(![ndc.x,ndc.y,ndc.z].every(Number.isFinite)||
   ndc.z<=-1||ndc.z>=1||Math.abs(ndc.x)>1.1||Math.abs(ndc.y)>1.1)return null;
 const normal=view.getWorldDirection(new THREE.Vector3());
 if(normal.lengthSq()<.999)return null;
 const plane=new THREE.Plane().setFromNormalAndCoplanarPoint(normal,center);
 const caster=new THREE.Raycaster();
 const sample=(dx,dy)=>{
  caster.setFromCamera(new THREE.Vector2(ndc.x+dx,ndc.y+dy),view);
  return caster.ray.intersectPlane(plane,new THREE.Vector3());
 };
 const horizontal=sample(2*pixels/rect.width,0);
 const vertical=sample(0,2*pixels/rect.height);
 if(!horizontal||!vertical)return null;
 const localX=mesh.worldToLocal(horizontal).distanceTo(localCenter);
 const localY=mesh.worldToLocal(vertical).distanceTo(localCenter);
 if(!Number.isFinite(localX)||!Number.isFinite(localY)||
   localX<=0||localY<=0)return null;
 // A circular CSS-pixel footprint is not a local-space sphere on a heavily
 // nonuniformly scaled object. Refuse rather than silently exaggerate radius.
 if(Math.max(localX,localY)/Math.min(localX,localY)>1.12)return null;
 const radius=(localX+localY)*.5;
 return radius>=.03&&radius<=2.5?radius:null;
}
function atelierBrushSizingRefresh(){
 const screen=$m('SculptBrushRadiusUnits')?.value==='screen';
 for(const id of ['SculptBrushRadiusScreen','SculptBrushSelectRadiusScreen']){
  const input=$m(id);if(input){input.parentElement.hidden=!screen;input.parentElement.style.display=screen?'':'none';}
 }
 for(const id of ['SculptBrushRadius','SculptBrushSelectRadius']){
  const input=$m(id);if(input){input.parentElement.hidden=screen;input.parentElement.style.display=screen?'none':'';}
 }
 const note=$m('SculptBrushSizingNote');
 if(note)note.textContent=screen?
  'Pixels measured in the camera plane at the picked center; baked as local radii when applied. Nonuniform mesh scale is rejected.':
  'Local radii are fixed model units, independent of screen size.';
}
