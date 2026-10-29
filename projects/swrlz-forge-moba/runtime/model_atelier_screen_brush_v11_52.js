// §E v11.52: camera-plane-exact pixel brush sizing at the user's chosen point.
// This is an authoring-time conversion, not a saved camera-dependent brush.
// Both local radii are frozen into the standard native stroke data on Apply.
let atelierBrushPixelLastReason='';
function atelierBrushLocalRadiusFromPixels(mesh,view,element,localCenter,pixels){
 const reject=reason=>{atelierBrushPixelLastReason=reason;return null;};
 if(!mesh?.isMesh||!view||!element||!(localCenter instanceof THREE.Vector3)||
   !Number.isFinite(pixels)||pixels<4||pixels>200)return reject('Invalid pixel radius or missing mesh/camera/point');
 const rect=element.getBoundingClientRect();
 if(!(rect.width>20&&rect.height>20))return reject('Viewport canvas has no measurable size');
 view.updateMatrixWorld();
 if(view.updateProjectionMatrix)view.updateProjectionMatrix();
 mesh.updateWorldMatrix(true,false);
 const center=mesh.localToWorld(localCenter.clone());
 const ndc=center.clone().project(view);
 if(![ndc.x,ndc.y,ndc.z].every(Number.isFinite)||
   ndc.z<=-1||ndc.z>=1||Math.abs(ndc.x)>1.1||Math.abs(ndc.y)>1.1)return reject('Selected center outside camera clip/projection: '+ndc.toArray().map(x=>x.toFixed(2)).join(','));
 const normal=view.getWorldDirection(new THREE.Vector3());
 if(normal.lengthSq()<.999)return reject('Camera direction invalid');
 const plane=new THREE.Plane().setFromNormalAndCoplanarPoint(normal,center);
 const caster=new THREE.Raycaster();
 const sample=(dx,dy)=>{
  caster.setFromCamera(new THREE.Vector2(ndc.x+dx,ndc.y+dy),view);
  return caster.ray.intersectPlane(plane,new THREE.Vector3());
 };
 const horizontal=sample(2*pixels/rect.width,0);
 const vertical=sample(0,2*pixels/rect.height);
 if(!horizontal||!vertical)return reject('Viewport rays do not meet camera-parallel brush plane');
 const localX=mesh.worldToLocal(horizontal).distanceTo(localCenter);
 const localY=mesh.worldToLocal(vertical).distanceTo(localCenter);
 if(!Number.isFinite(localX)||!Number.isFinite(localY)||
   localX<=0||localY<=0)return reject('Pixel-to-mesh radius nonfinite/zero '+localX+' '+localY);
 // A local-space sphere projects elliptically when the object transform is
 // nonuniform (the v11.20 anatomical head itself is mildly nonuniform).
 // Use the geometric mean at the tangent plane as a bounded approximation;
 // extreme anisotropy cannot be represented by the current scalar brush.
 const distortion=Math.max(localX,localY)/Math.min(localX,localY);
 if(distortion>2.5)return reject('Mesh projected anisotropy '+distortion.toFixed(2)+' > 2.5');
 const radius=Math.sqrt(localX*localY);
 if(radius<.03||radius>2.5)return reject('Pixel radius '+pixels+' maps to '+radius.toFixed(4)+' local units (requires .03–2.5)');
 atelierBrushPixelLastReason='Valid pixel conversion: '+radius.toFixed(4)+' local units';
 return radius;
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
  'Pixels measured in the camera plane at the picked center; baked as local radii when applied. Mildly unequal object scale is approximated; extreme anisotropy is rejected.':
  'Local radii are fixed model units, independent of screen size.';
}
