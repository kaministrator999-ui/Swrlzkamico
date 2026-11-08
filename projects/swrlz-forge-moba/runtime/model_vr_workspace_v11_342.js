/* SE340_MODEL_VR_WORKSPACE_START */
// Immersive Model Studio uses the existing main XR renderer and loop. Its
// presentation rig borrows the native Modeler root, never the Game actors.
const se340XR={session:null,busy:false,supported:null,scene:null,camera:null,
 rig:null,presentation:null,pivot:null,platform:null,ui:null,controllers:[],
 owned:new Set(),previous:null,documentToken:null,frameCount:0,lastTime:0,
 anchored:false,mode:'inspect',precision:false,snap:false,paletteVisible:true,
 helpVisible:false,gesture:null,fit:1,zoom:1,yaw:0,pan:new THREE.Vector2(),
 anchor:null,lastViewer:null,platformOffset:.38,right:new THREE.Vector3(1,0,0),forward:new THREE.Vector3(0,0,-1),
  selectedOutline:null,hoverOutline:null,hoverId:null,frameEntries:null,cachedEntries:null,projectionRevision:-1,pickMatrixFrame:-1,boxCache:new WeakMap(),pickStats:{hoverCount:0,preciseCount:0,preciseCandidates:0,lastHoverMs:0,maxHoverMs:0},pitch:0,lastAction:'',error:'',
 ending:false,message:'',stateKey:'',lastPulse:0,reference:null,referenceReset:null};
const SE340_MODES=['inspect','move','rotate','scale'];
const se340Bridge=()=>ModelAtelier?.xrBridge;
function se340ModelXRActive(){return !!window.SWYRL_ENGINE_MODEL_VR&&!!se340XR.session&&!!renderer.xr.isPresenting;}
function se340Own(resource){se340XR.owned.add(resource);return resource;}
function se340Notice(message,bad=false){
 se340XR.message=String(message||'').slice(0,160);
 if(bad)se340XR.error=se340XR.message;
 const el=document.getElementById('se340ModelVRStatus');
 if(el){el.textContent=se340XR.message;el.dataset.error=String(bad);}
}
function se340Publish(){
 window.dispatchEvent(new CustomEvent('swrlz:model-vr-state',{detail:se340ModelXRInspect()}));
}
function se340VisibleSession(){
 return !!se340XR.session&&(!se340XR.session.visibilityState||se340XR.session.visibilityState==='visible');
}
function se340Pulse(record,strength=.2,duration=25){
 const now=performance.now();if(now-(record?.pulseAt||0)<90)return;
 if(record)record.pulseAt=now;
 try{const actuator=record?.input?.gamepad?.hapticActuators?.[0]||record?.input?.gamepad?.vibrationActuator;
  const result=actuator?.pulse?.(strength,duration);result?.catch?.(()=>{});
 }catch(_){}
}
function se340PartEntries(){return se340XR.frameEntries||se340Bridge()?.projection?.()?.meshes||[];}
function se340PartBox(mesh){
 // Never CPU-skin every vertex to compute an idle hover bounding box.
 const geometry=mesh?.geometry;
 if(!geometry)return new THREE.Box3().setFromObject(mesh);
 const previous=se340XR.boxCache.get(mesh),position=geometry.getAttribute?.('position');
 const version=position?.version||0;
 if(previous&&previous.geometry===geometry&&previous.version===version&&
    previous.matrix.equals(mesh.matrixWorld))return previous.box;
 if(!geometry.boundingBox||previous&&previous.version!==version)geometry.computeBoundingBox();
 // The bind-pose proxy is approximate. On trigger/grip actual faces are tested.
 const local=mesh.isSkinnedMesh&&mesh.boundingBox&&!mesh.boundingBox.isEmpty()
   ?mesh.boundingBox:geometry.boundingBox;
 const box=local.clone().applyMatrix4(mesh.matrixWorld);
 if(mesh.isSkinnedMesh){
  const size=geometry.boundingBox.getSize(new THREE.Vector3());
  box.expandByScalar(Math.max(.01,Math.max(size.x,size.y,size.z)*.12));
 }
 se340XR.boxCache.set(mesh,{geometry,version,matrix:mesh.matrixWorld.clone(),box});
 return box;
}
function se340SourceBounds(entries=se340PartEntries()){
 const box=new THREE.Box3();
 for(const entry of entries)if(entry.mesh?.visible!==false)box.union(se340PartBox(entry.mesh));
 if(box.isEmpty())return new THREE.Box3(new THREE.Vector3(-.25,0,-.25),new THREE.Vector3(.25,1,.25));
 return box;
}
function se340ModelXRInspect(options={}){
 const native=se340Bridge()?.inspect?.()||{};
 const result={schema:'swyrl-model-vr-v1',active:se340ModelXRActive(),busy:se340XR.busy,
  supported:se340XR.supported,sessionAttached:!!se340XR.session,
  ready:!!se340XR.scene&&!!native.open,mode:se340XR.mode,precision:se340XR.precision,
  snap:se340XR.snap,paletteVisible:se340XR.paletteVisible,helpVisible:se340XR.helpVisible,
  frameCount:se340XR.frameCount,partCount:native.partCount||0,selectedId:native.selectedId||null,
  documentToken:native.documentToken??null,canUndo:!!native.canUndo,canRedo:!!native.canRedo,
  undoDepth:native.undoDepth||0,redoDepth:native.redoDepth||0,
  modelRootBorrowed:!!native.borrowed,nativeParentRestored:native.nativeParentRestored!==false,
  gesture:se340XR.gesture?{id:se340XR.gesture.id,mode:se340XR.gesture.mode,
   hand:se340XR.gesture.record.input?.handedness||'none'}:null,
  controllers:se340XR.controllers.map(r=>({index:r.index,handedness:r.input?.handedness||'none',
   targetTracked:!!r.targetTracked,gripTracked:!!r.gripTracked,hoverId:r.hit?.id||null,reticleVisible:!!r.dot.visible})),
  lastAction:se340XR.lastAction,error:se340XR.error,picking:{...se340XR.pickStats,hoverFaceRaycasts:0}};
 if(options?.geometry&&se340XR.scene){
  se340XR.scene.updateMatrixWorld(true);
  result.targetCenters=se340PartEntries().filter(e=>e.mesh?.visible!==false).map(e=>{
   const b=se340PartBox(e.mesh);return {id:e.id,name:e.name,center:b.getCenter(new THREE.Vector3()).toArray(),size:b.getSize(new THREE.Vector3()).toArray()};
  });
  result.paletteActions=(se340XR.ui?.targets||[]).filter(t=>t.userData?.se340Action&&t.visible!==false)
   .map(t=>({action:t.userData.se340Action,center:t.getWorldPosition(new THREE.Vector3()).toArray()}));
  result.presentation={position:se340XR.rig.position.toArray(),scale:se340XR.presentation.scale.toArray(),
   center:se340XR.pivot.position.toArray(),yaw:se340XR.yaw};
 }
 return result;
}
async function se340ModelXRCheckSupport(){
 try{se340XR.supported=!!navigator.xr&&typeof navigator.xr.requestSession==='function'&&
  !!await navigator.xr.isSessionSupported?.('immersive-vr');}
 catch(_){se340XR.supported=false;}
 if(!se340XR.supported)se340Notice('Model VR needs an immersive WebXR browser, such as Meta Quest Browser.',true);
 se340Publish();return se340XR.supported;
}
function se340Material(color,extra={}){
 return se340Own(new THREE.MeshBasicMaterial({color,depthWrite:false,...extra}));
}
function se340MakeStage(){
 const s=se340XR;s.scene=new THREE.Scene();s.scene.background=new THREE.Color('#101022');
 s.camera=new THREE.PerspectiveCamera(65,1,.015,60);s.scene.add(s.camera);
 s.scene.add(new THREE.HemisphereLight(0xe9dfff,0x28253d,2));
 const key=new THREE.DirectionalLight(0xffefd9,2.5);key.position.set(2,5,3);s.scene.add(key);
 const rim=new THREE.DirectionalLight(0xafbfff,1.7);rim.position.set(-3,3,-2);s.scene.add(rim);
 s.rig=new THREE.Group();s.rig.name='Model VR · presentation only';s.scene.add(s.rig);
 s.presentation=new THREE.Group();s.pivot=new THREE.Group();s.rig.add(s.presentation);s.presentation.add(s.pivot);
 const platformGeo=se340Own(new THREE.CylinderGeometry(.45,.48,.025,64));
 const platformMat=se340Own(new THREE.MeshStandardMaterial({color:'#29223f',roughness:.8,metalness:.15}));
 s.platform=new THREE.Mesh(platformGeo,platformMat);s.platform.name='Model VR · workbench';s.scene.add(s.platform);
 const outline=()=>{const line=new THREE.Box3Helper(new THREE.Box3(),0xc296ff);line.frustumCulled=false;
  line.material.depthTest=false;line.material.transparent=true;line.material.opacity=.9;line.renderOrder=100;
  se340Own(line.geometry);se340Own(line.material);line.visible=false;s.scene.add(line);return line;};
 s.selectedOutline=outline();s.hoverOutline=outline();s.hoverOutline.material.color.setHex(0x80f0e7);
 const actions=Object.fromEntries(['inspect','move','rotate','scale','undo','redo','focus','recenter','help','precision','snap','exit']
  .map(id=>[id,()=>se340ModelXRAction(id)]));
 s.ui=se340CreateModelVRUI({THREE,actions,status:se340Notice});s.scene.add(s.ui.root);
 const result=se340Bridge().borrowRoot(s.pivot);
 if(!result?.ok)throw Error('The native Modeler projection could not be borrowed.');
 s.documentToken=se340Bridge().inspect().documentToken;
}
function se340Viewer(frame){
 try{const pose=frame?.getViewerPose?.(renderer.xr.getReferenceSpace());
  if(pose){const matrix=new THREE.Matrix4().fromArray(pose.transform.matrix);
   const position=new THREE.Vector3(),orientation=new THREE.Quaternion(),scale=new THREE.Vector3();matrix.decompose(position,orientation,scale);
   return {position,forward:new THREE.Vector3(0,0,-1).applyQuaternion(orientation)};}
 }catch(_){}
 return null;
}
function se340PlacePalette(viewer){
 const s=se340XR;if(!s.ui||!viewer)return;
 const forward=viewer.forward.clone();forward.y=0;if(forward.lengthSq()<.001)forward.set(0,0,-1);forward.normalize();
 const right=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
 s.ui.root.position.copy(viewer.position).addScaledVector(forward,1.0).addScaledVector(right,-.47);
 s.ui.root.position.y=THREE.MathUtils.clamp(viewer.position.y-.08,.85,1.65);
 s.ui.root.lookAt(viewer.position);s.ui.root.visible=s.paletteVisible;s.ui.root.updateWorldMatrix(true,true);
}
function se340Recenter(viewer=null,focus=false){
 const s=se340XR;if(!s.scene)return false;
 se340CancelGesture('View recentered.');
 // Temporarily remove the presentation transform when measuring native units.
 s.rig.position.set(0,0,0);s.rig.quaternion.identity();s.presentation.scale.setScalar(1);s.pivot.position.set(0,0,0);s.scene.updateMatrixWorld(true);
 const native=se340Bridge().inspect(),entries=se340PartEntries();
 const allBounds=se340SourceBounds(entries),selected=entries.find(e=>e.id===native.selectedId);
 const bounds=focus&&selected?se340PartBox(selected.mesh):allBounds;
 const size=allBounds.getSize(new THREE.Vector3()),targetSize=bounds.getSize(new THREE.Vector3());
 const baseFit=.72/Math.max(.01,size.x,size.y,size.z);
 s.fit=Math.min(20,Math.max(.005,focus?Math.min(baseFit*4,.72/Math.max(.01,targetSize.x,targetSize.y,targetSize.z)):baseFit));
 const center=bounds.getCenter(new THREE.Vector3());
 s.platformOffset=(center.y-allBounds.min.y)*s.fit+.025;
 s.pivot.position.copy(center).negate();
 const sourceViewer=viewer||s.lastViewer||s.anchor||{position:new THREE.Vector3(0,1.6,0),forward:new THREE.Vector3(0,0,-1)};
 const forward=sourceViewer.forward.clone();forward.y=0;if(forward.lengthSq()<.001)forward.set(0,0,-1);forward.normalize();
 const right=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
 s.anchor={position:sourceViewer.position.clone(),forward:forward.clone()};s.forward.copy(forward);s.right.copy(right);
 s.rig.position.copy(sourceViewer.position).addScaledVector(forward,1.12).addScaledVector(right,.19);
 s.rig.position.y=THREE.MathUtils.clamp(sourceViewer.position.y-.22,.75,1.6);
  s.yaw=Math.atan2(-forward.x,-forward.z);s.pitch=0;s.rig.rotation.set(0,s.yaw,0);s.zoom=1;s.pan.set(0,0);s.presentation.scale.setScalar(s.fit);
 s.platform.position.copy(s.rig.position);s.platform.position.y-=s.platformOffset;
 se340PlacePalette(sourceViewer);
 s.anchored=true;s.scene.updateMatrixWorld(true);
 return true;
}
function se340Tracked(record,frame,kind){
 const space=kind==='grip'?record.input?.gripSpace:record.input?.targetRaySpace;
 if(!space||!frame?.getPose)return false;
 try{return !!frame.getPose(space,renderer.xr.getReferenceSpace());}catch(_){return false;}
}
function se340Cast(record){
 if(!record.targetTracked)return null;
 record.target.updateMatrixWorld(true);
 const origin=record.target.getWorldPosition(new THREE.Vector3());
 const direction=new THREE.Vector3(0,0,-1).transformDirection(record.target.matrixWorld).normalize();
  const cast=record.cast||(record.cast=new THREE.Raycaster());
  cast.set(origin,direction);cast.near=.01;cast.far=5;return cast;
}
function se340Hit(record,precise=true){
 const started=performance.now(),stats=se340XR.pickStats;
 const finish=hit=>{
  const elapsed=performance.now()-started;
  if(precise)stats.preciseCount++;
  else{stats.hoverCount++;stats.lastHoverMs=+elapsed.toFixed(2);stats.maxHoverMs=Math.max(stats.maxHoverMs,stats.lastHoverMs);}
  return hit;
 };
 const cast=se340Cast(record);if(!cast)return finish(null);
 // Update model transforms at most once on an XR frame that requires picking.
 if(se340XR.pickMatrixFrame!==se340XR.frameCount){
  se340XR.pivot?.updateWorldMatrix(true,true);
  se340XR.pickMatrixFrame=se340XR.frameCount;
 }
 const ui=se340XR.ui;
 if(ui?.root.visible){const hits=ui.hitTest?ui.hitTest(cast):cast.intersectObjects(ui.targets,false);
  const hit=Array.isArray(hits)?hits[0]:hits;
  if(hit)return finish({ui:true,target:hit.object,action:hit.object.userData.se340Action||null,
    distance:hit.distance,point:hit.point});}
 const entries=se340PartEntries().filter(e=>e.mesh?.visible!==false);
 if(!precise){
  // Both controller rays only touch cheap world-space boxes while hovering.
  let candidate=null,nearest=cast.far;
  for(const entry of entries){
   const point=cast.ray.intersectBox(se340PartBox(entry.mesh),new THREE.Vector3());
   if(!point)continue;
   const distance=cast.ray.origin.distanceTo(point);
   if(distance>=cast.near&&distance<nearest){
    nearest=distance;candidate={id:entry.id,name:entry.name,mesh:entry.mesh,distance,point,proxy:true};
   }
  }
  return finish(candidate||{distance:1.2,point:cast.ray.at(1.2,new THREE.Vector3())});
 }
 // Only user selection/grip calls test the triangles, including skinned faces.
 const roots=entries.filter(e=>e.mesh.isSkinnedMesh||
  cast.ray.intersectsBox(se340PartBox(e.mesh))).map(e=>e.mesh);
 stats.preciseCandidates+=roots.length;
 for(const hit of cast.intersectObjects(roots,true)){
  if(hit.object.userData?.atelierHelper)continue;
  let mesh=hit.object;while(mesh&&!roots.includes(mesh))mesh=mesh.parent;
  const entry=entries.find(e=>e.mesh===mesh);
  if(entry)return finish({id:entry.id,name:entry.name,mesh,distance:hit.distance,point:hit.point});
 }
 return finish({distance:1.2,point:cast.ray.at(1.2,new THREE.Vector3())});
}
function se340Pressed(record,index,threshold=.62){const b=record.input?.gamepad?.buttons?.[index];return !!b&&(b.pressed||b.value>=threshold);}
function se340GripPose(record){
 if(!record.gripTracked)return null;record.grip.updateMatrixWorld(true);
 return {position:record.grip.getWorldPosition(new THREE.Vector3()),quaternion:record.grip.getWorldQuaternion(new THREE.Quaternion())};
}
function se340CancelGesture(message='Edit canceled.'){
 const g=se340XR.gesture;if(!g)return false;
 se340XR.gesture=null;g.record.blockGrip=true;
 se340Bridge()?.cancel?.();se340XR.lastAction='Canceled '+g.mode;se340Notice(message);se340Publish();return true;
}
function se340FinishGesture(record){
 const g=se340XR.gesture;if(!g||g.record!==record)return false;
 if(!record.gripTracked||!se340VisibleSession())return se340CancelGesture('Tracking changed; preview canceled.');
 // Include motion sampled on this release frame, rather than committing the
 // previous frame's preview when input and release arrive together.
 se340UpdateGesture();if(se340XR.gesture!==g)return false;
 se340XR.gesture=null;
 const result=se340Bridge().end(true);
 if(result?.ok===false){se340Notice(result.error||'The edit was canceled because its source changed.',true);return false;}
  se340XR.frameEntries=null;if(result?.changed){se340XR.boxCache=new WeakMap();se340XR.cachedEntries=null;se340XR.projectionRevision=-1;}
  se340XR.lastAction=result?.changed?'Applied '+g.mode:'No transform change';
 se340Notice(se340XR.lastAction);if(result?.changed)se340Pulse(record,.4,35);se340Publish();return true;
}
function se340GripBasis(mesh,part){
 mesh.updateWorldMatrix(true,false);
 const local=new THREE.Matrix4().compose(new THREE.Vector3(...part.position),
  new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation)),new THREE.Vector3(...part.scale));
 // Preserve any native assembly/rig basis between the model root and part.
 const basis=new THREE.Matrix4().copy(mesh.matrixWorld).multiply(local.invert());
 const quaternion=new THREE.Quaternion();basis.decompose(new THREE.Vector3(),quaternion,new THREE.Vector3());
 return {inverse:basis.clone().invert(),quaternion};
}
function se340BeginGesture(record){
 if(se340XR.mode==='inspect'||se340XR.gesture||record.blockGrip||!se340VisibleSession())return false;
 const pose=se340GripPose(record);if(!pose)return false;
 const hit=se340Hit(record);if(!hit?.id||hit.ui)return false;
 const bridge=se340Bridge(),native=bridge.inspect(),id=hit.id;
 if(native.selectedId!==id)bridge.select(id);
 const part=bridge.describe(id);if(!part)return false;
 const result=bridge.begin(id,se340XR.mode);if(result?.ok===false)return false;
 const projection=bridge.projection(),mesh=projection.meshes.find(entry=>entry.id===id)?.mesh;
 if(!mesh){bridge.cancel('MODEL_PART_NOT_READY');return false;}
 const basis=se340GripBasis(mesh,part);
 se340XR.gesture={record,id,mode:se340XR.mode,start:part,hand:pose,
  rootInverse:basis.inverse,rootQuaternion:basis.quaternion};
 se340Notice(se340XR.mode==='scale'?'Grip + lift or lower your hand to size the part.':'Grip held · release to apply; B cancels.');
 se340Pulse(record,.25,25);se340Publish();return true;
}
function se340UpdateGesture(){
 const s=se340XR,g=s.gesture;if(!g)return;
 if(!g.record.gripTracked||!se340VisibleSession()){se340CancelGesture('Tracking changed; preview canceled.');return;}
 const pose=se340GripPose(g.record);if(!pose)return;
 const gain=s.precision?.25:1,base=g.start,candidate={position:[...base.position],rotation:[...base.rotation],scale:[...base.scale]};
 if(g.mode==='move'){
  const physicalDelta=pose.position.distanceTo(g.hand.position);
  const delta=physicalDelta<(s.precision?.00075:.0015)?new THREE.Vector3():
   pose.position.clone().applyMatrix4(g.rootInverse).sub(g.hand.position.clone().applyMatrix4(g.rootInverse)).multiplyScalar(gain);
  candidate.position=base.position.map((v,i)=>THREE.MathUtils.clamp(v+(s.snap?Math.round(delta.getComponent(i)/.01)*.01:delta.getComponent(i)),-100,100));
 }else if(g.mode==='rotate'){
  const worldDelta=pose.quaternion.clone().multiply(g.hand.quaternion.clone().invert());
  const localDelta=g.rootQuaternion.clone().invert().multiply(worldDelta).multiply(g.rootQuaternion);
  const precise=new THREE.Quaternion().identity().slerp(localDelta,gain);
  if(precise.angleTo(new THREE.Quaternion())>.003){
   const q=precise.multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(...base.rotation)));
   const e=new THREE.Euler().setFromQuaternion(q,'XYZ');
   candidate.rotation=base.rotation.map((v,i)=>{let d=Math.atan2(Math.sin(e.toArray()[i]-v),Math.cos(e.toArray()[i]-v));if(s.snap)d=Math.round(d/(Math.PI/12))*(Math.PI/12);return v+d;});
  }
 }else if(g.mode==='scale'){
  const physicalDelta=pose.position.y-g.hand.position.y;
  let factor=Math.abs(physicalDelta)<(s.precision?.00075:.0015)?1:Math.exp(2.4*physicalDelta*gain);
  if(s.snap)factor=1+Math.round((factor-1)/.05)*.05;
  const low=Math.max(...base.scale.map(v=>.0051/v)),high=Math.min(...base.scale.map(v=>20/v));
  factor=THREE.MathUtils.clamp(factor,low,high);candidate.scale=base.scale.map(v=>v*factor);
 }
 const result=se340Bridge().update(candidate);if(result?.ok===false)se340CancelGesture(result.error||'The source changed; preview canceled.');
}
function se340Trigger(record){
 if(!se340VisibleSession()||!record.targetTracked)return;
 const hit=se340Hit(record);record.hit=hit;
 if(hit?.ui){if(hit.action&&se340XR.ui.press(hit.target)!==false)se340ModelXRAction(hit.action,record);return;}
  if(hit?.id&&!se340XR.gesture){se340Bridge().select(hit.id);se340XR.frameEntries=null;se340XR.cachedEntries=null;se340XR.projectionRevision=-1;se340XR.boxCache=new WeakMap();se340XR.lastAction='Selected '+hit.name;
  se340Notice(se340XR.lastAction);se340Pulse(record,.3,25);se340Publish();}
}
function se340MakeController(index){
 const target=renderer.xr.getController(index),grip=renderer.xr.getControllerGrip(index);
 const geometry=se340Own(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3(0,0,-1)]));
 const ray=new THREE.Line(geometry,se340Own(new THREE.LineBasicMaterial({color:0xbda0ff,transparent:true,opacity:.62,depthTest:false,depthWrite:false})));
 ray.name='Model VR · native target ray';ray.renderOrder=9000;target.add(ray);
 const dot=new THREE.Mesh(se340Own(new THREE.RingGeometry(.006,.009,24)),se340Material(0xc9afff,{side:THREE.DoubleSide,depthTest:false}));dot.renderOrder=9001;se340XR.scene.add(dot);
 const body=new THREE.Group();body.name='Model VR · tracked grip';
 const handle=new THREE.Mesh(se340Own(new THREE.CapsuleGeometry(.022,.075,4,8)),se340Own(new THREE.MeshStandardMaterial({color:0x6d5b8c,roughness:.6,metalness:.15})));handle.rotation.x=Math.PI/2;body.add(handle);grip.add(body);
 se340XR.scene.add(target,grip);
 const r={index,target,grip,ray,dot,body,input:null,targetTracked:false,gripTracked:false,held:false,blockGrip:false,
  pendingSelect:false,eventGripDown:false,eventGripUp:false,
   buttons:[],nextHoverAt:0,cast:null,hit:null,pulseAt:0};
 r.connected=e=>{r.input=e.data||null;r.blockGrip=true;r.buttons=[];};
 r.disconnected=()=>{if(se340XR.gesture?.record===r)se340CancelGesture('Controller disconnected; preview canceled.');r.input=null;r.targetTracked=false;r.gripTracked=false;};
 // Resolve event intents in the next actual XR frame, using that frame's
 // grip/target tracking. A release after tracking loss must never commit a
 // stale last-frame pose merely because the event arrived before the frame.
 r.select=()=>{r.pendingSelect=true;};
 r.squeeze=()=>{r.eventGripDown=true;r.eventGripUp=false;};
 r.release=()=>{r.eventGripUp=true;r.eventGripDown=false;};
 target.addEventListener('connected',r.connected);target.addEventListener('disconnected',r.disconnected);
 target.addEventListener('selectstart',r.select);target.addEventListener('squeezestart',r.squeeze);target.addEventListener('squeezeend',r.release);
 return r;
}
function se340Poll(record,frame,dt){
 const wasTracked=record.gripTracked;
 record.targetTracked=se340Tracked(record,frame,'target');record.gripTracked=se340Tracked(record,frame,'grip');
 if(wasTracked&&!record.gripTracked&&se340XR.gesture?.record===record)se340CancelGesture('Controller tracking lost; preview canceled.');
 record.ray.visible=record.targetTracked;record.dot.visible=record.targetTracked;record.body.visible=record.gripTracked;
 const side=record.input?.handedness,buttons=[se340Pressed(record,4),se340Pressed(record,5)];
 const cancelWon=!!record.cancelHandled;
 if(cancelWon)record.pendingSelect=false;
 else if(record.pendingSelect){record.pendingSelect=false;se340Trigger(record);}
 const grip=record.eventGripUp?false:record.eventGripDown?true:se340Pressed(record,1);
 if(!grip){if(record.held)se340FinishGesture(record);record.held=false;record.blockGrip=false;}
 else if(!record.held){record.held=true;se340BeginGesture(record);}
 record.eventGripDown=false;record.eventGripUp=false;
 if(se340VisibleSession()&&(record.targetTracked||record.gripTracked)){
  if(buttons[0]&&!record.buttons[0])se340ModelXRAction(side==='left'?'palette':side==='right'?'next-tool':'',record);
  if(!cancelWon&&buttons[1]&&!record.buttons[1])se340ModelXRAction(side==='left'?'undo':side==='right'?'cancel':'',record);
 }
 record.buttons=buttons;
 const axes=record.input?.gamepad?.axes||[],x=Number(axes[axes.length-2])||0,y=Number(axes[axes.length-1])||0;
 if(!se340XR.gesture&&se340VisibleSession()&&record.gripTracked){
   if(side==='left'){
    const dx=Math.abs(x)>.18?x:0,dy=Math.abs(y)>.18?y:0;
    const gain=(se340XR.precision?.4:1)/Math.sqrt(Math.max(.35,se340XR.zoom));
    se340XR.pan.x=THREE.MathUtils.clamp(se340XR.pan.x+dx*dt*.42*gain,-.85,.85);
    se340XR.pan.y=THREE.MathUtils.clamp(se340XR.pan.y-dy*dt*.42*gain,-.65,.65);
   }else if(side==='right'){
    const gain=se340XR.precision?.4:1,dx=Math.abs(x)>.18?x:0,dy=Math.abs(y)>.18?y:0;
    // Smooth model-centred orbit; right stick pressed + vertical = optical zoom.
    se340XR.yaw-=dx*dt*1.35*gain;
    if(se340Pressed(record,3))
     se340XR.zoom=THREE.MathUtils.clamp(se340XR.zoom*Math.exp(-dy*dt*1.15*gain),.25,5);
    else se340XR.pitch=THREE.MathUtils.clamp(se340XR.pitch+dy*dt*1.05*gain,-1.22,1.22);
   }
 }
  if(record.targetTracked){
   // Hover runs at approximately 18Hz/hand; trigger and grip still cast immediately.
   const now=performance.now();
   if(now>=record.nextHoverAt){
    const hit=se340Hit(record,false),key=hit?.ui?hit.action:hit?.id;
    if(key&&key!==record.hoverKey)se340Pulse(record,.08,12);
    record.hoverKey=key;record.hit=hit;record.nextHoverAt=now+55;
   }
   const hit=record.hit;
   record.dot.visible=!!(hit?.id||hit?.ui)&&!!hit.point;
   record.ray.scale.z=Math.max(.04,Math.min(hit?.distance||1.2,5));
   record.ray.material.color.setHex(hit?.ui?0xe1bbff:hit?.id?0x80f0c4:0xbda0ff);
   if(hit?.point){record.dot.position.copy(hit.point);record.dot.quaternion.copy(se340XR.camera.quaternion);record.dot.lookAt(record.target.getWorldPosition(new THREE.Vector3()));}
  }else{record.hit=null;record.hoverKey=null;record.nextHoverAt=0;}
}
function se340UpdateView(){
 const s=se340XR;if(!s.anchor)return;
 s.rig.position.copy(s.anchor.position).addScaledVector(s.forward,1.12).addScaledVector(s.right,.19+s.pan.x);
 s.rig.position.y=THREE.MathUtils.clamp(s.anchor.position.y-.22,.75,1.6)+s.pan.y;
  s.rig.rotation.set(s.pitch,s.yaw,0,'YXZ');s.presentation.scale.setScalar(s.fit*s.zoom);
 s.platform.position.copy(s.rig.position);s.platform.position.y-=s.platformOffset*s.zoom;
 s.platform.scale.setScalar(THREE.MathUtils.clamp(s.zoom,.5,2));
}
function se340SyncUI(){
 const s=se340XR,native=se340Bridge().inspect(),entries=se340PartEntries();
 const selected=entries.find(e=>e.id===native.selectedId),hover=s.controllers.map(r=>r.hit).find(h=>h?.id&&h.id!==native.selectedId);
 s.selectedOutline.visible=!!selected;if(selected)s.selectedOutline.box.copy(se340PartBox(selected.mesh));
 s.hoverOutline.visible=!!hover;if(hover)s.hoverOutline.box.copy(se340PartBox(hover.mesh));
 const uiHit=s.controllers.map(r=>r.hit).find(h=>h?.ui&&h.action);s.ui.hover(uiHit?.target||null);
 s.ui.root.visible=s.paletteVisible;
 const state={mode:s.mode,selectedName:selected?.name||'',hoverName:hover?.name||'',dragging:!!s.gesture,
  canUndo:!!native.canUndo,canRedo:!!native.canRedo,message:s.message,
  tracking:s.controllers.filter(r=>r.targetTracked).length+' controllers tracked',
  precision:s.precision,snap:s.snap,helpVisible:s.helpVisible,
   controllerHint:'Left stick pan · Right stick orbit · Hold right stick click + vertical to zoom'};
 const key=JSON.stringify(state);if(key!==s.stateKey){s.stateKey=key;s.ui.update(state);}
}
function se340ModelXRAction(action,record=null){
 const s=se340XR;if(!s.session||!s.scene||!se340VisibleSession())return false;
 if(action==='exit'){void se340ModelXRExit();return true;}
 if(action==='cancel'){
  const cancelled=se340CancelGesture();if(!cancelled)s.mode='inspect';
  se340Notice(cancelled?'Preview canceled · release grip to start again.':'Inspect mode · trigger selects; no grip edits.');
  se340Publish();return true;
 }
 if(action==='palette'){s.paletteVisible=!s.paletteVisible;s.helpVisible=false;if(s.paletteVisible)se340PlacePalette(s.lastViewer||s.anchor);se340Publish();return true;}
 if(action==='next-tool')action=SE340_MODES[(SE340_MODES.indexOf(s.mode)+1)%SE340_MODES.length];
 if(SE340_MODES.includes(action)){
  se340CancelGesture('Previous preview canceled.');s.mode=action;
  se340Notice(action==='inspect'?'Inspect mode · trigger selects; no grip edits.':action==='scale'?'Scale · grip and lift/lower your hand.':action==='rotate'?'Rotate · hold grip and turn your wrist.':'Move · hold grip and move your controller.');
 }else if(action==='undo'||action==='redo'){
  if(s.gesture){se340CancelGesture('Preview canceled. Press again to '+action+'.');return true;}
   const result=se340Bridge()[action]();s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.boxCache=new WeakMap();
   se340Notice(result?.changed?action==='undo'?'Undid model edit.':'Redid model edit.':'No '+action+' step available.');
 }else if(action==='precision'){s.precision=!s.precision;se340Notice(s.precision?'Precision on · quarter-speed transforms.':'Precision off.');}
 else if(action==='snap'){s.snap=!s.snap;se340Notice(s.snap?'Snap on · model 0.01 move / 15° turn / 5% size.':'Snap off.');}
 else if(action==='help'){s.helpVisible=!s.helpVisible;}
 else if(action==='recenter'||action==='focus'){se340Recenter(null,action==='focus');se340Notice(action==='focus'?'Selected part framed for inspection.':'Model view recentered.');}
 else return false;
 s.lastAction=action;if(record)se340Pulse(record,.2,20);se340SyncUI();se340Publish();return true;
}
function se340ModelXRFrameCore(time,frame){
 const s=se340XR;if(!s.session||!s.scene)return;
 const dt=s.lastTime?THREE.MathUtils.clamp((time-s.lastTime)/1000,0,.05):0;s.lastTime=time;s.frameCount++;
 const bridge=se340Bridge(),native=bridge.inspect();
 if(!native.open||native.documentToken!==s.documentToken||!bridge.isBorrowed()){
  se340CancelGesture('The model workspace changed; leaving Model VR.');if(!s.ending)void se340ModelXRExit();return;
 }
 const viewer=se340Viewer(frame);if(viewer){s.lastViewer=viewer;if(!s.anchored)se340Recenter(viewer);}
 if(!se340VisibleSession())se340CancelGesture('Headset menu open · preview canceled.');
 // Resolve Cancel before either hand can commit a grip release this frame.
 for(const record of s.controllers){
  record.cancelHandled=false;
  if(s.gesture&&record.input?.handedness==='right'&&se340Pressed(record,5)&&!record.buttons[1]&&se340VisibleSession()){
   se340ModelXRAction('cancel',record);record.cancelHandled=true;
   for(const other of s.controllers)other.blockGrip=true;
  }
 }
  // Rebuild native projection only when mesh revision changes; XR renderer
  // owns ordinary world matrices. Queries refresh matrices when needed.
  se340UpdateView();
  if(!s.cachedEntries||s.projectionRevision!==native.revision){
   s.cachedEntries=bridge.projection().meshes;s.projectionRevision=native.revision;
   s.boxCache=new WeakMap();
  }
  s.frameEntries=s.cachedEntries;
  for(const record of s.controllers)se340Poll(record,frame,dt);
  se340UpdateGesture();
  if(s.gesture){bridge.projection();s.scene.updateMatrixWorld(true);}
  se340SyncUI();renderer.render(s.scene,s.camera);s.frameEntries=null;
}
function se340ModelXRFrame(time,frame){
 try{se340ModelXRFrameCore(time,frame);}
 catch(error){
  se340CancelGesture('The preview stopped safely.');
  se340Notice('Model VR paused: '+String(error?.message||error).slice(0,120),true);
  if(!se340XR.ending)void se340ModelXRExit();
 }
}
function se340Cleanup(expected){
 const s=se340XR;if(expected&&s.session!==expected)return;
 se340CancelGesture('VR ended · uncommitted preview canceled.');
 if(s.reference&&s.referenceReset)s.reference.removeEventListener?.('reset',s.referenceReset);
 s.reference=null;s.referenceReset=null;
 try{se340Bridge()?.releaseRoot?.();}catch(error){s.error=String(error?.message||error);}
 for(const r of s.controllers){
  r.target.removeEventListener('connected',r.connected);r.target.removeEventListener('disconnected',r.disconnected);
  r.target.removeEventListener('selectstart',r.select);r.target.removeEventListener('squeezestart',r.squeeze);r.target.removeEventListener('squeezeend',r.release);
  r.target.remove(r.ray);r.grip.remove(r.body);r.target.removeFromParent();r.grip.removeFromParent();r.dot.removeFromParent();
 }
 s.controllers=[];try{s.ui?.dispose();}catch(error){s.error=String(error?.message||error);}
 for(const resource of s.owned){try{resource.dispose();}catch(_){}}s.owned.clear();
 s.scene?.clear();s.scene=null;s.camera=null;s.ui=null;s.rig=null;s.presentation=null;s.pivot=null;
  s.session=null;s.busy=false;s.ending=false;s.anchored=false;s.gesture=null;s.documentToken=null;s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.pickMatrixFrame=-1;s.boxCache=new WeakMap();
 if(s.previous){renderer.xr.enabled=s.previous.xrEnabled;orbit.enabled=s.previous.orbitEnabled;s.previous=null;}
 try{resize();}catch(_){}
 se340Notice('Back in Model Studio. Your native model and history are ready.');se340Publish();
}
async function se340ModelXRExit(){
 const s=se340XR;if(!s.session)return false;
 se340CancelGesture('Leaving VR · preview canceled.');s.ending=true;
 try{await s.session.end();return true;}
 catch(error){s.ending=false;se340Notice('Use the headset menu to exit VR: '+String(error?.message||error),true);return false;}
}
async function se340ModelXREnter(){
 const s=se340XR,bridge=se340Bridge();
 if(s.busy||s.session)return false;
 if(playing||simulating){se340Notice('Stop Play or Simulation before entering Model VR.',true);return false;}
 if(!bridge?.inspect?.().open){se340Notice('Open a model in Model Studio first.',true);return false;}
 if(renderer.xr.isPresenting||se181XR.session){se340Notice('Exit the current VR workspace before opening Model VR.',true);return false;}
 if(!navigator.xr?.requestSession){s.supported=false;se340Notice('Use an immersive WebXR browser, such as Meta Quest Browser.',true);se340Publish();return false;}
 // requestSession is called during the original trusted button activation.
 s.busy=true;s.error='';se340Notice('Opening immersive Model Studio…');se340Publish();
 let requested=null;
 try{
  const request=navigator.xr.requestSession('immersive-vr',{requiredFeatures:['local-floor']});
  requested=await request;
  s.previous={xrEnabled:renderer.xr.enabled,orbitEnabled:orbit.enabled};
  s.session=requested;s.mode='inspect';s.precision=false;s.snap=false;s.paletteVisible=true;s.helpVisible=false;
   s.frameCount=0;s.lastTime=0;s.stateKey='';s.anchored=false;s.ending=false;s.hoverId=null;s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.pickMatrixFrame=-1;s.boxCache=new WeakMap();s.pickStats={hoverCount:0,preciseCount:0,preciseCandidates:0,lastHoverMs:0,maxHoverMs:0};s.pitch=0;
  se340MakeStage();s.controllers=[se340MakeController(0),se340MakeController(1)];
  requested.addEventListener('end',()=>queueMicrotask(()=>se340Cleanup(requested)),{once:true});
  requested.addEventListener('visibilitychange',()=>{if(!se340VisibleSession()){se340CancelGesture('Headset menu open · preview canceled.');for(const r of s.controllers)r.blockGrip=true;}});
  renderer.xr.enabled=true;renderer.xr.setReferenceSpaceType('local-floor');orbit.enabled=false;
  await renderer.xr.setSession(requested);
  s.reference=renderer.xr.getReferenceSpace();
  s.referenceReset=()=>{se340CancelGesture('Tracking origin changed; preview canceled.');s.anchored=false;
   for(const record of s.controllers)record.blockGrip=true;};
  s.reference?.addEventListener?.('reset',s.referenceReset);
  try{window.SWYRL_VR_CONTROLS?.attachSession?.(requested);}catch(_){}
  s.supported=true;s.busy=false;se340Notice('Inspect mode · trigger selects; choose Move, Rotate or Scale before gripping.');
  se340Publish();return true;
 }catch(error){
  const message='Model VR could not start: '+String(error?.message||error).slice(0,120);
  if(requested){try{await requested.end();}catch(_){}}
  se340Cleanup(requested);se340Notice(message,true);se340Publish();return false;
 }
}
window.SWYRL_ENGINE_MODEL_VR=Object.freeze({enter:se340ModelXREnter,exit:se340ModelXRExit,
 inspect:se340ModelXRInspect,read:se340ModelXRInspect,checkSupport:se340ModelXRCheckSupport,action:se340ModelXRAction});
/* SE340_MODEL_VR_WORKSPACE_END */
