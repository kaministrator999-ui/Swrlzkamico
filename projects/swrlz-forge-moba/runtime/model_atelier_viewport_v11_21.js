// v11.21 opt-in display and mobile navigation tools for Model Atelier.
// View modes are NONDESTRUCTIVE editor state; saved mesh/materials remain intact.
// One finger orbits/selects; two fingers pinch/translate the camera target.
// Shift+left drag or middle-button drag pans on desktop.
const atelierViewModes=['shaded','wireframe','overlay','xray'];
let atelierViewGlobal='shaded',atelierViewOverrides=new Map();
let atelierViewColors=true,atelierViewTextures=true;
const atelierViewMaterialOverrides=new Map();
let atelierViewWireContrast=true,atelierViewWireTint='#d9f5ff';
const atelierCameraPan=new THREE.Vector3(),atelierCameraTouches=new Map();
const atelierCameraConsumedTouches=new Set();
let atelierCameraGesture=null,atelierCameraMousePan=null;
function atelierViewportBounds(){
 return renderer?.domElement?.getBoundingClientRect()||{width:1,height:1};
}
function atelierViewportCameraInfoUpdate(){
 const viewport=$m('Viewport');
 if(!viewport||!camera)return;
 viewport.dataset.cameraDistance=orbit.distance.toFixed(5);
 viewport.dataset.cameraPan=atelierCameraPan.toArray().map(x=>x.toFixed(5)).join(',');
 viewport.dataset.cameraYaw=orbit.yaw.toFixed(5);
 viewport.dataset.cameraPitch=orbit.pitch.toFixed(5);
 const hint=$m('ViewportNavHint');
 if(hint)hint.textContent='Zoom '+orbit.distance.toFixed(2)
    +' · Pan '+atelierCameraPan.length().toFixed(2)
    +' · 1 finger orbit · 2 fingers pinch/pan · Shift-drag pan';
}
function atelierViewModeFor(p){return atelierViewOverrides.get(p.id)||atelierViewGlobal;}
function atelierViewFlagsFor(p){
 return atelierViewMaterialOverrides.get(p.id)||{colors:atelierViewColors,textures:atelierViewTextures};
}
function atelierViewDisabledMaps(mat){
 // Keep alpha maps for silhouette/cutout safety. Disable cosmetic maps,
 // including procedural vertex dye, without destroying saved originals.
 for(const key of ['map','normalMap','bumpMap','roughnessMap','metalnessMap',
  'emissiveMap','aoMap','lightMap','specularMap','clearcoatMap',
  'clearcoatNormalMap','clearcoatRoughnessMap','iridescenceMap',
  'iridescenceThicknessMap','sheenColorMap','sheenRoughnessMap',
  'anisotropyMap','displacementMap']){
   if(key in mat)mat[key]=null;
 }
}
function atelierViewModeApply(mesh,part){
 const mode=atelierViewModeFor(part),flags=atelierViewFlagsFor(part);
 if(part.kind==='faceSheet'&&atelierFaceHeatmap&&mode==='shaded'){
   atelierFaceVolumeHeatmap(mesh,part);return mesh;
 }
 const isContrastingWire=mode==='wireframe'&&atelierViewWireContrast;
 if(isContrastingWire){
   // Basic wire shader is lighting-independent. In particular, dark hair and
   // other highly saturated vertex colors can no longer conceal topology.
   mesh.material=new THREE.MeshBasicMaterial({
     color:atelierViewWireTint,wireframe:true,side:THREE.DoubleSide,
     depthTest:true,depthWrite:true
   });
   mesh.material.userData.atelierViewportClone=true;
 }else if(mode!=='shaded'||!flags.colors||!flags.textures){
   // v11.20 HD materials are shared/cached; never mutate originals.
   const original=mesh.material;
   mesh.material=original.clone();
   mesh.material.userData={...original.userData,atelierHDMaterial:false,atelierViewportClone:true};
   if(!flags.colors){
     if(mesh.material.color)mesh.material.color.set('#cad3de');
     if(mesh.material.emissive)mesh.material.emissive.set('#000000');
     if('vertexColors' in mesh.material)mesh.material.vertexColors=false;
   }
   if(!flags.textures)atelierViewDisabledMaps(mesh.material);
   if(mode==='wireframe'){
     mesh.material.wireframe=true;
     mesh.material.side=THREE.DoubleSide;
   }else if(mode==='xray'){
     mesh.material.transparent=true;
     mesh.material.opacity=.27;
     mesh.material.depthWrite=false;
     mesh.material.side=THREE.DoubleSide;
   }else if(mode==='overlay'){
     // Offset the shaded triangles *backward* just enough so the independent
     // high-contrast wire overlay is not hidden by its coplanar face.
     mesh.material.polygonOffset=true;
     mesh.material.polygonOffsetFactor=2;
     mesh.material.polygonOffsetUnits=2;
   }
   mesh.material.needsUpdate=true;
 }
 if(mode==='overlay'){
   const material=new THREE.MeshBasicMaterial({
     wireframe:true,color:atelierViewWireTint,
     transparent:true,opacity:.95,side:THREE.DoubleSide,
     depthTest:true,depthWrite:false,
     polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2
   });
   const overlay=new THREE.Mesh(mesh.geometry,material);
   overlay.name='Viewport wireframe overlay';
   overlay.userData.atelierHelper=true;
   overlay.renderOrder=3;
   mesh.add(overlay);
 }
 return mesh;
}
function atelierViewRebuild(){if(modelRoot)renderParts();}
function atelierViewportControlsRefresh(){
 const mode=$m('ViewportMode'),scope=$m('ViewportScope');
 if(!mode||!scope)return;
 const p=partById(selection),selected=scope.value==='selected'&&p;
 const flags=selected?atelierViewFlagsFor(p):{colors:atelierViewColors,textures:atelierViewTextures};
 mode.value=selected?atelierViewModeFor(p):atelierViewGlobal;
 $m('ViewportColors').checked=flags.colors;
 $m('ViewportTextures').checked=flags.textures;
 $m('ViewportWireContrast').checked=atelierViewWireContrast;
 $m('ViewportWireTint').value=atelierViewWireTint;
}
function atelierViewApplyChoice(){
 const mode=$m('ViewportMode').value,scope=$m('ViewportScope').value;
 if(!atelierViewModes.includes(mode))return;
 if(scope==='selected'){
   const p=partById(selection);
   if(!p){status('Choose a mesh before setting a selected-only view.',true);atelierViewportControlsRefresh();return;}
   atelierViewOverrides.set(p.id,mode);
   status('Viewport: '+mode+' on selected mesh '+p.name+'. Geometry unchanged.');
 }else{
   atelierViewGlobal=mode;
   atelierViewOverrides.clear();
   status('Viewport: '+mode+' on all model meshes. Geometry unchanged.');
 }
 atelierViewRebuild();
}
function atelierViewAppearanceApply(){
 const p=partById(selection),scope=$m('ViewportScope').value;
 const flags={colors:$m('ViewportColors').checked,textures:$m('ViewportTextures').checked};
 if(scope==='selected'){
   if(!p){status('Select a mesh before changing its appearance.',true);atelierViewportControlsRefresh();return;}
   atelierViewMaterialOverrides.set(p.id,flags);
 }else{
   atelierViewColors=flags.colors;atelierViewTextures=flags.textures;
   atelierViewMaterialOverrides.clear();
 }
 atelierViewRebuild();
 status('Viewport: '+(flags.colors?'colors on':'neutral color')
   +' / '+(flags.textures?'textures on':'textures hidden')+' for '
   +(scope==='selected'?'the selected mesh':'all meshes')
   +'. Saved model materials unchanged.');
}
function atelierViewStatus(){
 const objs=modelRoot?.children.filter(x=>x.isMesh)||[];
 const material=objs.find(x=>x.userData.atelierId===selection)?.material;
 return {
   global:atelierViewGlobal,overrides:atelierViewOverrides.size,
   shaded:objs.length-objs.filter(o=>o.material.wireframe||o.material.transparent).length,
   wireframe:objs.filter(o=>o.material.wireframe).length,
   overlay:objs.filter(o=>o.children.some(c=>c.isMesh&&c.userData.atelierHelper)).length,
   xray:objs.filter(o=>o.material.transparent).length,
   originalColors:objs.filter(o=>atelierViewFlagsFor(partById(o.userData.atelierId)).colors).length,
   originalTextures:objs.filter(o=>atelierViewFlagsFor(partById(o.userData.atelierId)).textures).length,
   contrastWire:atelierViewWireContrast,wireTint:atelierViewWireTint,
   selectedMaterial:material?{
     color:material.color?.getHexString()||null,
     vertexColors:!!material.vertexColors,
     hasMap:!!material.map,
     basic:material.isMeshBasicMaterial===true,
     wireframe:!!material.wireframe
   }:null,
   distance:orbit.distance,pan:atelierCameraPan.toArray(),
   yaw:orbit.yaw,pitch:orbit.pitch,activeTouchCount:atelierCameraTouches.size
 };
}
function atelierCameraPanByPixels(dx,dy){
 if(!camera||!renderer||!Number.isFinite(dx)||!Number.isFinite(dy))return;
 const size=atelierViewportBounds();
 const worldPerPixel=2*orbit.distance*Math.tan(camera.fov*Math.PI/360)/Math.max(size.height,1);
 camera.updateMatrixWorld(true);
 const right=new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld,0);
 const up=new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld,1);
 atelierCameraPan.addScaledVector(right,-dx*worldPerPixel);
 atelierCameraPan.addScaledVector(up,dy*worldPerPixel);
 cameraUpdate();
}
function atelierCameraTouchMetrics(){
 const pts=[...atelierCameraTouches.values()].slice(0,2);
 if(pts.length<2)return null;
 return {x:(pts[0].x+pts[1].x)/2,y:(pts[0].y+pts[1].y)/2,
   separation:Math.max(8,Math.hypot(pts[1].x-pts[0].x,pts[1].y-pts[0].y))};
}
function atelierCameraPointerDown(e){
 if(e.pointerType!=='touch'){
   if(e.button!==1&&!(e.button===0&&e.shiftKey))return false;
   atelierCameraMousePan={id:e.pointerId,x:e.clientX,y:e.clientY};
   pressed=null;
   renderer.domElement.setPointerCapture?.(e.pointerId);
   return true;
 }
 if(e.button!==0)return false;
 atelierCameraTouches.set(e.pointerId,{x:e.clientX,y:e.clientY});
 renderer.domElement.setPointerCapture?.(e.pointerId);
 if(atelierCameraTouches.size>=2){
   // A second finger cancels a possible one-finger tap, orbit or vertex drag;
   // a gesture must NEVER click a part or commit an unintended vertex edit.
   pressed=null;
   if(atelierSculptDrag){atelierSculptDrag=null;renderParts();}
   if(atelierLassoDrag){atelierLassoDrag=null;atelierLassoTempPin=null;atelierLassoOverlayRefresh();}
   if(atelierLassoFreehand){atelierLassoFreehand=null;atelierLassoPending=[];atelierLassoArm=null;atelierLassoRefresh();}
   for(const id of atelierCameraTouches.keys())atelierCameraConsumedTouches.add(id);
   atelierCameraGesture=atelierCameraTouchMetrics();
   return true;
 }
 return false; // preserve original one-finger orbit and tap selection
}
function atelierCameraPointerMove(e){
 if(atelierCameraMousePan?.id===e.pointerId){
   const p=atelierCameraMousePan;
   atelierCameraPanByPixels(e.clientX-p.x,e.clientY-p.y);
   p.x=e.clientX;p.y=e.clientY;
   return true;
 }
 if(e.pointerType!=='touch'||!atelierCameraTouches.has(e.pointerId))return false;
 atelierCameraTouches.set(e.pointerId,{x:e.clientX,y:e.clientY});
 if(atelierCameraTouches.size>=2){
   const now=atelierCameraTouchMetrics(),old=atelierCameraGesture;
   if(old&&now){
     const ratio=old.separation/now.separation;
     orbit.distance=THREE.MathUtils.clamp(orbit.distance*ratio,.45,24);
     cameraUpdate();
     atelierCameraPanByPixels(now.x-old.x,now.y-old.y);
   }
   atelierCameraGesture=now;
   return true;
 }
 return atelierCameraConsumedTouches.has(e.pointerId);
}
function atelierCameraPointerUp(e){
 if(atelierCameraMousePan?.id===e.pointerId){
   atelierCameraMousePan=null;return true;
 }
 if(e.pointerType!=='touch'||!atelierCameraTouches.has(e.pointerId))return false;
 const consumed=atelierCameraConsumedTouches.has(e.pointerId);
 atelierCameraTouches.delete(e.pointerId);
 atelierCameraConsumedTouches.delete(e.pointerId);
 atelierCameraGesture=atelierCameraTouches.size>=2?atelierCameraTouchMetrics():null;
 if(!atelierCameraTouches.size)atelierCameraConsumedTouches.clear();
 return consumed;
}
function atelierCameraPointerCancel(e){
 atelierCameraPointerUp(e);
 pressed=null;
}
function atelierViewportInstall(){
 const mode=$m('ViewportMode'),scope=$m('ViewportScope');
 if(!mode||!scope)return;
 mode.addEventListener('change',atelierViewApplyChoice);
 scope.addEventListener('change',atelierViewportControlsRefresh);
 $m('ViewportColors').addEventListener('change',atelierViewAppearanceApply);
 $m('ViewportTextures').addEventListener('change',atelierViewAppearanceApply);
 $m('ViewportWireContrast').addEventListener('change',()=>{
   atelierViewWireContrast=$m('ViewportWireContrast').checked;
   atelierViewRebuild();
   status(atelierViewWireContrast?'High contrast wireframe active.':'Original mesh colored wireframe active.');
 });
 $m('ViewportWireTint').addEventListener('input',()=>{
   const color=$m('ViewportWireTint').value;
   if(!/^#[0-9a-fA-F]{6}$/.test(color))return;
   atelierViewWireTint=color;
   atelierViewRebuild();
 });
 atelierViewportControlsRefresh();
 for(const btn of $m('ViewportModes').querySelectorAll('[data-at-view]'))
   btn.addEventListener('click',()=>{
     const preset=btn.getAttribute('data-at-view');
     if(preset==='top'||preset==='bottom'){
       atelierDetailTarget=null;
       orbit.yaw=0;orbit.pitch=preset==='top'?1.53:-1.53;
       orbit.distance=8.1;cameraUpdate();
     }else{
       atelierSetPoseCamera(preset);
     }
     if(preset==='front'||preset==='back'||preset==='left'||preset==='right'
       ||preset==='top'||preset==='bottom'){
       status('Camera '+preset+' view. Pan/pinch gestures remain available.');
     }
   });
 $m('ViewportPanReset').addEventListener('click',()=>{
   atelierCameraPan.set(0,0,0);cameraUpdate();
   status('Camera pan reset; sculpt geometry unchanged.');
 });
 window.SWYRL_ENGINE_VIEW=Object.freeze({status:atelierViewStatus});
 atelierViewportCameraInfoUpdate();
}
