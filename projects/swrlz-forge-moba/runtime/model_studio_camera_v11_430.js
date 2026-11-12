/* SE430_MODEL_STUDIO_CAMERA_START */
// One native viewport, renderer and camera binding. Projection and navigation
// are editor state; they never create model history or change saved geometry.
const se430ModelCamera=(()=>{
 const state={projection:'perspective',view:'orbit',yaw:null,pitch:null,widget:null,installedPanel:null};
 const axes={front:[0,0],back:[Math.PI,0],left:[-Math.PI/2,0],right:[Math.PI/2,0],top:[0,Math.PI/2],bottom:[0,-Math.PI/2]};
 const labels={front:'Front',back:'Back',left:'Left',right:'Right',top:'Top',bottom:'Bottom',orbit:'Free orbit',three:'Three-quarter'};
 const usable=()=>!!camera&&!!modelRoot&&!se340ModelBridge.isBorrowed();
 const aspect=()=>Math.max(.01,Number(camera?.aspect)||1);
 const fov=()=>THREE.MathUtils.clamp(Number(camera?.fov)||44,5,150);
 const target=()=>(atelierDetailTarget||new THREE.Vector3(0,model()?.assemblies?2.8:2.35,0)).clone().add(atelierCameraPan);
 function updateOrtho(){
  const half=Math.max(.0001,orbit.distance*Math.tan(THREE.MathUtils.degToRad(this.fov)/2));
  this.left=-half*this.aspect;this.right=half*this.aspect;this.top=half;this.bottom=-half;
  THREE.OrthographicCamera.prototype.updateProjectionMatrix.call(this);
 }
 function ensureProjection(){
  if(!camera)return;
  const desired=atelierCameraInterior?'perspective':state.projection;
  const isOrtho=!!camera.isOrthographicCamera;
  if((desired==='orthographic')===isOrtho){if(isOrtho)camera.updateProjectionMatrix();return;}
  const previous=camera,near=previous.near,far=previous.far,angle=fov(),ratio=aspect();
  const next=desired==='orthographic'?new THREE.OrthographicCamera(-1,1,1,-1,near,far):new THREE.PerspectiveCamera(angle,ratio,near,far);
  next.position.copy(previous.position);next.quaternion.copy(previous.quaternion);next.up.copy(previous.up);
  next.fov=angle;next.aspect=ratio;next.zoom=previous.zoom||1;next.name='Model Studio '+desired+' camera';
  // Older native fit/resize code deliberately retains its fov/aspect contract.
  // The rendered projection is a real orthographic matrix, not a distant lens.
  if(next.isOrthographicCamera)next.updateProjectionMatrix=updateOrtho;
  camera=next;camera.updateProjectionMatrix();camera.updateMatrixWorld(true);
 }
 function corners(bounds){const points=[];for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z])points.push(new THREE.Vector3(x,y,z));return points;}
 function bounds(scope){
  const box=new THREE.Box3();if(!modelRoot)return box;modelRoot.updateWorldMatrix(true,true);
  if(scope==='selected'&&atelierComponentMode!=='mesh'&&atelierComponentIds.length){
   const component=atelierComponentTopologyForActive();
   if(component){const ids=atelierComponentIndices(component.topology),positions=component.mesh.geometry.attributes.position;
    for(const id of ids)if(id>=0&&id<positions.count)box.expandByPoint(new THREE.Vector3().fromBufferAttribute(positions,id).applyMatrix4(component.mesh.matrixWorld));
    if(!box.isEmpty())return box;
   }
  }
  const meshes=scope==='selected'?atelierMeshSelectedMeshes():modelRoot.children.filter(m=>m.isMesh&&m.userData.atelierId);
  for(const mesh of meshes)if(mesh.visible!==false)box.expandByObject(mesh);
  return box;
 }
 function frame(scope='all',quiet=false){
  if(!usable()||!['all','selected'].includes(scope))return false;
  if(atelierCameraInterior)atelierViewportInsideExit();
  const box=bounds(scope);if(box.isEmpty()){if(!quiet)status(scope==='selected'?'Select a mesh or component to frame.':'Add geometry to frame the model.',true);return false;}
  const center=box.getCenter(new THREE.Vector3());atelierDetailTarget=center;atelierCameraPan.set(0,0,0);cameraUpdate();
  const inverse=camera.quaternion.clone().invert(),tanY=Math.tan(THREE.MathUtils.degToRad(fov())/2)/camera.zoom,tanX=tanY*aspect(),margin=.86;
  let distance=.08;
  for(const point of corners(box)){
   const p=point.sub(center).applyQuaternion(inverse);
   distance=Math.max(distance,p.z+camera.near+.04);
   if(camera.isOrthographicCamera)distance=Math.max(distance,Math.abs(p.x)/(tanX*margin),Math.abs(p.y)/(tanY*margin));
   else distance=Math.max(distance,p.z+Math.abs(p.x)/(tanX*margin),p.z+Math.abs(p.y)/(tanY*margin));
  }
  orbit.distance=distance;
  // Framing may pull the camera beyond its old far plane. Keep the model in
  // view while preserving the existing near clipping and interior controls.
  const radius=box.getSize(new THREE.Vector3()).length()*.5;
  camera.far=Math.max(camera.far,distance+radius*1.2+1);camera.updateProjectionMatrix();cameraUpdate();
  if(!quiet)status(scope==='selected'?'Selected geometry framed. View changes do not alter the model.':'Entire model framed. View changes do not alter the model.');
  return true;
 }
 function setProjection(value){
  if(!['perspective','orthographic'].includes(value)||!usable())return false;
  if(atelierCameraInterior&&value==='orthographic'){status('Exit interior inspection before using orthographic projection.',true);return false;}
  state.projection=value;ensureProjection();cameraUpdate();
  status(value==='orthographic'?'Orthographic projection · parallel edges keep their size at every depth.':'Perspective projection · distant geometry appears smaller.');return true;
 }
 function setView(view){
  if(!usable()||!Object.hasOwn(axes,view)&&view!=='three')return false;
  if(atelierCameraInterior)atelierViewportInsideExit();
  const pose=axes[view]||[.46,.17];state.view=view;state.yaw=pose[0];state.pitch=pose[1];orbit.yaw=pose[0];orbit.pitch=pose[1];
  cameraUpdate();frame('all',true);refresh();status((labels[view]||view)+' view · '+(camera.isOrthographicCamera?'orthographic':'perspective')+' · drag to orbit.');return true;
 }
 function inspect(){
  if(!camera)return {ready:false,projection:state.projection,view:state.view};
  camera.updateMatrixWorld(true);
  return {ready:usable(),projection:camera.isOrthographicCamera?'orthographic':'perspective',preferredProjection:state.projection,
   view:state.view,cameraType:camera.type,position:camera.position.toArray(),target:target().toArray(),up:camera.up.toArray(),
   direction:camera.getWorldDirection(new THREE.Vector3()).toArray(),projectionMatrix:camera.projectionMatrix.toArray(),matrixWorld:camera.matrixWorld.toArray(),
   near:camera.near,far:camera.far,fov:fov(),aspect:aspect(),distance:orbit.distance,pan:atelierCameraPan.toArray(),
   span:camera.isOrthographicCamera?{width:(camera.right-camera.left)/camera.zoom,height:(camera.top-camera.bottom)/camera.zoom}:null,
   selectedIds:[...atelierMeshActiveIds()],interior:!!atelierCameraInterior};
 }
 function safeTop(){
  if(!stage)return 8;const rect=stage.getBoundingClientRect();let bottom=rect.top;
  for(const node of [$m('ViewportModes'),panel?.querySelector('[data-component-controls]')]){
   if(!node||node.hidden)continue;const r=node.getBoundingClientRect();if(r.bottom>rect.top&&r.top<rect.bottom)bottom=Math.max(bottom,r.bottom);
  }
  return Math.max(8,Math.round(bottom-rect.top+8));
 }
 function refresh(){
  if(!panel||!camera)return;
  const projection=camera.isOrthographicCamera?'orthographic':'perspective',viewport=$m('Viewport');
  if(viewport){viewport.dataset.cameraProjection=projection;viewport.dataset.cameraView=state.view;}
  for(const b of panel.querySelectorAll('[data-se430-projection]')){
   b.setAttribute('aria-pressed',String(b.dataset.se430Projection===projection));b.disabled=!usable()||atelierCameraInterior&&b.dataset.se430Projection==='orthographic';
  }
  for(const b of panel.querySelectorAll('[data-se430-frame]'))b.disabled=!usable()||b.dataset.se430Frame==='selected'&&!atelierMeshActiveIds().length;
  for(const b of panel.querySelectorAll('[data-at-view]'))b.setAttribute('aria-pressed',String(b.dataset.atView===state.view));
  const widget=state.widget;if(!widget)return;
  widget.hidden=!usable();widget.style.top=safeTop()+'px';
  const output=widget.querySelector('output');output.textContent=(labels[state.view]||'Free orbit')+' · '+(projection==='orthographic'?'Ortho':'Persp');
  camera.updateMatrixWorld(true);const inverse=camera.quaternion.clone().invert();
  for(const b of widget.querySelectorAll('[data-se430-axis]')){
   const v=new THREE.Vector3(...b.dataset.se430Axis.split(',').map(Number)).applyQuaternion(inverse);
   const x=56+v.x*34,y=48-v.y*34;
   b.style.left=x+'px';b.style.top=y+'px';b.style.zIndex=String(20+Math.round(v.z*10));b.style.opacity=v.z<-.2?'.55':'1';
   b.setAttribute('aria-pressed',String(b.dataset.se430View===state.view));
   const line=widget.querySelector('[data-axis-line="'+b.dataset.se430View+'"]');line.setAttribute('x2',String(x));line.setAttribute('y2',String(y));
  }
 }
 function install(){
  if(!panel)return false;
  const host=panel.querySelector('.atelier-top-camera')||$m('ViewportModes');
  if(host&&!host.querySelector('[data-se430-camera-controls]')){
   const controls=document.createElement('div');controls.className='se430-camera-controls';controls.dataset.se430CameraControls='1';
   controls.setAttribute('role','group');controls.setAttribute('aria-label','Projection and framing');
   controls.innerHTML='<span class="se430-camera-control-label">Projection</span><button type="button" data-se430-projection="perspective">Perspective</button><button type="button" data-se430-projection="orthographic">Orthographic</button><button type="button" data-se430-frame="all">Frame all</button><button type="button" data-se430-frame="selected">Frame selection</button>';
   host.prepend(controls);
  }
  if(stage&&!stage.querySelector('[data-se430-orientation]')){
   const widget=document.createElement('aside');widget.className='se430-camera-orientation';widget.dataset.se430Orientation='1';widget.setAttribute('aria-label','Viewport orientation');
   const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 112 96');svg.setAttribute('aria-hidden','true');widget.append(svg);
   const rows=[['right','+X',[1,0,0],'x'],['left','−X',[-1,0,0],'x'],['top','+Y',[0,1,0],'y'],['bottom','−Y',[0,-1,0],'y'],['front','+Z',[0,0,1],'z'],['back','−Z',[0,0,-1],'z']];
   for(const [view,label,axis,color]of rows){
    const line=document.createElementNS(ns,'line');line.dataset.axisLine=view;line.setAttribute('x1','56');line.setAttribute('y1','48');line.classList.add('se430-axis-'+color);svg.append(line);
    const button=document.createElement('button');button.type='button';button.dataset.se430View=view;button.dataset.se430Axis=axis.join(',');button.className='se430-axis-'+color;button.textContent=label;button.title=labels[view]+' view';button.setAttribute('aria-label',labels[view]+' view ('+label+')');widget.append(button);
   }
   const output=document.createElement('output');output.setAttribute('aria-live','off');widget.append(output);
   widget.addEventListener('pointerdown',event=>event.stopPropagation());stage.append(widget);state.widget=widget;
  }else if(stage)state.widget=stage.querySelector('[data-se430-orientation]');
  if(state.installedPanel!==panel){
   state.installedPanel=panel;
   panel.addEventListener('click',event=>{
    const b=event.target?.closest?.('button');if(!b||!panel.contains(b))return;
    const projection=b.dataset.se430Projection,scope=b.dataset.se430Frame,view=b.dataset.se430View||b.dataset.atView;
    if(projection){event.preventDefault();event.stopImmediatePropagation();setProjection(projection);}
    else if(scope||b.id==='modelAtelierFrameSelected'||b.hasAttribute('data-mesh-frame')){event.preventDefault();event.stopImmediatePropagation();frame(scope||'selected');}
    else if(view&&Object.hasOwn(axes,view)){event.preventDefault();event.stopImmediatePropagation();setView(view);}
   },true);
  }
  ensureProjection();refresh();return true;
 }
 const previousPose=atelierSetPoseCamera;
 atelierSetPoseCamera=function(view){return Object.hasOwn(axes,view)?setView(view):previousPose.apply(this,arguments);};
 atelierMeshFrameSelected=function(){return frame('selected');};
 const previousPan=atelierCameraPanByPixels;
 atelierCameraPanByPixels=function(dx,dy){
  if(!camera?.isOrthographicCamera)return previousPan.apply(this,arguments);
  if(!renderer||!Number.isFinite(dx)||!Number.isFinite(dy))return;
  const pixels=Math.max(1,atelierViewportBounds().height),unit=(camera.top-camera.bottom)/camera.zoom/pixels;camera.updateMatrixWorld(true);
  atelierCameraPan.addScaledVector(new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld,0),-dx*unit);
  atelierCameraPan.addScaledVector(new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld,1),dy*unit);cameraUpdate();
 };
 cameraUpdate=function(){
  if(!camera)return;ensureProjection();
  if(state.view!=='orbit'&&(Math.abs(orbit.yaw-state.yaw)>1e-9||Math.abs(orbit.pitch-state.pitch)>1e-9))state.view='orbit';
  if(orbit.distance<.55&&camera.near>.018){camera.near=.018;camera.updateProjectionMatrix();}
  const at=target(),h=Math.cos(orbit.pitch);camera.up.set(0,1,0);
  if(state.view==='top')camera.up.set(0,0,-1);else if(state.view==='bottom')camera.up.set(0,0,1);
  camera.position.set(at.x+orbit.distance*h*Math.sin(orbit.yaw),at.y+orbit.distance*Math.sin(orbit.pitch),at.z+orbit.distance*h*Math.cos(orbit.yaw));
  camera.lookAt(at);camera.updateMatrixWorld(true);if(camera.isOrthographicCamera)camera.updateProjectionMatrix();
  atelierHDDirty=true;atelierViewportCameraInfoUpdate();
 };
 const previousInfo=atelierViewportCameraInfoUpdate;
 atelierViewportCameraInfoUpdate=function(){previousInfo.apply(this,arguments);refresh();};
 const previousResize=resize;
 resize=function(){const result=previousResize.apply(this,arguments);refresh();return result;};
 return Object.freeze({install,refresh,inspect,setProjection,setView,frame});
})();
/* SE430_MODEL_STUDIO_CAMERA_END */
