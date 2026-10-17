// v11.21 opt-in display and mobile navigation tools for Model Atelier.
// View modes are NONDESTRUCTIVE editor state; saved mesh/materials remain intact.
// One finger orbits/selects; two fingers pinch/translate the camera target.
// Shift+left drag or middle-button drag pans on desktop.
const atelierViewModes=['shaded','wireframe','overlay','xray'];
let atelierViewGlobal='shaded',atelierViewOverrides=new Map();
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
function atelierViewModeFor(p){
 return atelierViewOverrides.get(p.id)||atelierViewGlobal;
}
function atelierViewModeApply(mesh,part){
 const mode=atelierViewModeFor(part);
 if(mode==='wireframe'){
   mesh.material.wireframe=true;
   mesh.material.side=THREE.DoubleSide;
 }else if(mode==='xray'){
   mesh.material.transparent=true;
   mesh.material.opacity=.27;
   mesh.material.depthWrite=false;
   mesh.material.side=THREE.DoubleSide;
 }else if(mode==='overlay'){
   // Shaded surface + a thin wire overlay for exactly the same indexed
   // geometry. The overlay is a CHILD, so raycasts / OBJ export only operate
   // on real root meshes; the renderer and source geometry remain unchanged.
   const material=new THREE.MeshBasicMaterial({
     wireframe:true,color:0x39ddf7,transparent:true,opacity:.43,
     depthWrite:false,depthTest:true,polygonOffset:true,polygonOffsetFactor:-1
   });
   const overlay=new THREE.Mesh(mesh.geometry,material);
   overlay.name='Viewport wireframe overlay';
   overlay.userData.atelierHelper=true;
   overlay.renderOrder=3;
   mesh.add(overlay);
 }
 return mesh;
}
function atelierViewRebuild(){
 if(!modelRoot)return;
 // The overlay shares parent geometry; only its *material* needs separate
 // disposal. Existing root-mesh geometry disposal remains the owner's code.
 for(const mesh of modelRoot.children){
   if(!mesh.isMesh)continue;
   for(const child of mesh.children)if(child.isMesh&&child.userData.atelierHelper)
     child.material?.dispose();
 }
 renderParts();
}
function atelierViewApplyChoice(){
 const mode=$m('ViewportMode').value,scope=$m('ViewportScope').value;
 if(!atelierViewModes.includes(mode))return;
 if(scope==='selected'){
   const p=partById(selection);
   if(!p){status('Choose a mesh before setting a selected-only view.',true);return;}
   atelierViewOverrides.set(p.id,mode);
   status('Viewport: '+mode+' on selected mesh '+p.name+'. Geometry unchanged.');
 }else{
   atelierViewGlobal=mode;
   atelierViewOverrides.clear();
   status('Viewport: '+mode+' on all model meshes. Geometry unchanged.');
 }
 atelierViewRebuild();
}
function atelierViewStatus(){
 const objs=modelRoot?.children.filter(x=>x.isMesh)||[];
 return {
   global:atelierViewGlobal,overrides:atelierViewOverrides.size,
   shaded:objs.length-objs.filter(o=>o.material.wireframe||o.material.transparent).length,
   wireframe:objs.filter(o=>o.material.wireframe).length,
   overlay:objs.filter(o=>o.children.some(c=>c.isMesh&&c.userData.atelierHelper)).length,
   xray:objs.filter(o=>o.material.transparent).length,
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
 scope.addEventListener('change',()=>{
   const p=partById(selection);
   mode.value=scope.value==='selected'&&p?atelierViewModeFor(p):atelierViewGlobal;
 });
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
