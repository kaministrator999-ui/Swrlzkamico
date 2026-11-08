/* SE340_MODEL_VR_WORKSPACE_START */
/* SE350_MODEL_VR_TWO_HAND_WORKSPACE */
// Immersive Model Studio uses the existing main XR renderer and loop. Its
// presentation rig borrows the native Modeler root, never the Game actors.
const se340XR={session:null,busy:false,supported:null,scene:null,camera:null,
 rig:null,presentation:null,pivot:null,platform:null,ui:null,controllers:[],
 owned:new Set(),previous:null,documentToken:null,frameCount:0,lastTime:0,
 anchored:false,mode:'inspect',precision:false,snap:false,paletteVisible:true,
 helpVisible:false,gesture:null,page:'tools',viewMode:'orbit',aimHand:'right',aim:null,displayMode:'textured',displayOriginals:new Map(),displayMaterials:new Map(),fit:1,zoom:1,yaw:0,pan:new THREE.Vector2(),
 anchor:null,lastViewer:null,platformOffset:.38,right:new THREE.Vector3(1,0,0),forward:new THREE.Vector3(0,0,-1),
  selectedOutline:null,hoverOutline:null,hoverId:null,frameEntries:null,cachedEntries:null,projectionRevision:-1,pickMatrixFrame:-1,boxCache:new WeakMap(),hoverSurfaceCache:new WeakMap(),hoverGeometries:new Set(),hoverSurfaceMaterial:null,pickStats:{hoverCount:0,preciseCount:0,preciseCandidates:0,lastHoverMs:0,maxHoverMs:0},pitch:0,lastAction:'',error:'',
 ending:false,message:'',stateKey:'',lastPulse:0,reference:null,referenceReset:null};
const SE340_MODES=['inspect','move','rotate','scale','two-hand','sculpt','draw'];
const SE350_BRUSHES=['push','smooth','flatten','inflate','pinch','translate'];
Object.assign(se340XR,{sculptTool:'push',brushRadius:.12,brushStrength:.3,wheel:null,drawLine:null,inputSample:null,frameDt:0});
const se350Input=se350CreateModelVRInput({getProfile:()=>window.SWYRL_VR_CONTROLS?.currentProfile?.()});
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
/* SE343_MODEL_VR_SURFACE_HOVER_START */
// Simplified continuous picking skin for passive XR hover. These hidden
// meshes are never rendered or persisted as part of the model document.
// Only Trigger and Grip use the original, full-resolution editable geometry.
const SE343_HOVER_FACE_BUDGET=3600;
function se343HoverGeometry(source,isSkinned){
 const pos=source?.getAttribute?.('position'),idx=source?.getIndex?.();
 if(!pos||pos.itemSize!==3)return null;
 const triangles=Math.floor((idx?idx.count:pos.count)/3);
 if(!triangles)return null;
 if(triangles<=SE343_HOVER_FACE_BUDGET)return {geometry:source,owned:false,faces:triangles};
 const skinIdx=isSkinned?source.getAttribute('skinIndex'):null;
 const skinWt=isSkinned?source.getAttribute('skinWeight'):null;
 if(isSkinned&&(!skinIdx||!skinWt))return null;
 if(!source.boundingBox)source.computeBoundingBox();
 const min=source.boundingBox.min,extent=source.boundingBox.getSize(new THREE.Vector3());
 const maxSize=Math.max(extent.x,extent.y,extent.z,.0001);
 const remap=new Int32Array(pos.count);
 const values=(a,i)=>[a.getX(i),a.getY(i),a.getZ(i),a.getW(i)];
 let chosen=null;
 // Spatial vertex clustering creates a connected shell rather than sparse
 // isolated triangles. The principal bone ID protects adjacent fingers from
 // being welded together when their positions are close in bind pose.
 for(const divisions of [32,25,20,16,12,9,7,5,3]){
  const groups=[],lookup=new Map(),scale=divisions/maxSize;
  for(let i=0;i<pos.count;i++){
   const x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i);
   let bone=0;
   if(skinIdx&&skinWt){
    const w=values(skinWt,i),b=values(skinIdx,i);
    let highest=-1;
    for(let j=0;j<4;j++)if(w[j]>highest){highest=w[j];bone=b[j];}
   }
   const key=Math.floor((x-min.x)*scale)+','+Math.floor((y-min.y)*scale)+','+Math.floor((z-min.z)*scale)+','+bone;
   let group=lookup.get(key);
   if(group===undefined){group=groups.length;lookup.set(key,group);groups.push({x:0,y:0,z:0,count:0,original:i});}
   const item=groups[group];item.x+=x;item.y+=y;item.z+=z;item.count++;remap[i]=group;
  }
  const faces=[],used=new Set();
  for(let i=0;i<triangles;i++){
   const a=remap[idx?idx.getX(i*3):i*3],b=remap[idx?idx.getX(i*3+1):i*3+1],c=remap[idx?idx.getX(i*3+2):i*3+2];
   if(a===b||a===c||b===c)continue;
   const key=[a,b,c].sort((x,y)=>x-y).join(':');
   if(used.has(key))continue;
   used.add(key);faces.push(a,b,c);
  }
  if(!faces.length)continue;
  chosen={groups,faces};
  if(faces.length/3<=SE343_HOVER_FACE_BUDGET)break;
 }
 if(!chosen)return null;
 const {groups,faces}=chosen,xyz=new Float32Array(groups.length*3);
 const joints=isSkinned?new Uint16Array(groups.length*4):null;
 const weights=isSkinned?new Float32Array(groups.length*4):null;
 for(let i=0;i<groups.length;i++){
  const g=groups[i],j=i*3;
  xyz[j]=g.x/g.count;xyz[j+1]=g.y/g.count;xyz[j+2]=g.z/g.count;
  if(joints){
   const original=g.original,ids=values(skinIdx,original),ws=values(skinWt,original);
   for(let k=0;k<4;k++){joints[i*4+k]=ids[k];weights[i*4+k]=ws[k];}
  }
 }
 const geo=new THREE.BufferGeometry();
 geo.setAttribute('position',new THREE.BufferAttribute(xyz,3));geo.setIndex(faces);
 if(joints){
  geo.setAttribute('skinIndex',new THREE.BufferAttribute(joints,4));
  geo.setAttribute('skinWeight',new THREE.BufferAttribute(weights,4));
 }
 geo.computeBoundingBox();geo.computeBoundingSphere();
 return {geometry:geo,owned:true,faces:faces.length/3};
}
function se343DropHoverSurfaces(){
 const s=se340XR;
 for(const geo of s.hoverGeometries)geo.dispose();
 s.hoverGeometries.clear();s.hoverSurfaceCache=new WeakMap();
}
function se343SurfaceMesh(mesh){
 const s=se340XR,geometry=mesh?.geometry,version=geometry?.getAttribute?.('position')?.version||0;
 if(!geometry)return null;
 let entry=s.hoverSurfaceCache.get(mesh);
 if(entry&&entry.source===geometry&&entry.version===version)return entry.proxy;
 if(entry?.owned){entry.proxy.geometry.dispose();s.hoverGeometries.delete(entry.proxy.geometry);}
 const sampled=se343HoverGeometry(geometry,!!mesh.isSkinnedMesh);
 if(!sampled)return null;
 if(!s.hoverSurfaceMaterial)s.hoverSurfaceMaterial=se340Own(new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
 const proxy=mesh.isSkinnedMesh?new THREE.SkinnedMesh(sampled.geometry,s.hoverSurfaceMaterial):
  new THREE.Mesh(sampled.geometry,s.hoverSurfaceMaterial);
 proxy.matrixAutoUpdate=false;proxy.matrixWorldAutoUpdate=false;
 if(mesh.isSkinnedMesh){
  proxy.skeleton=mesh.skeleton;proxy.bindMode=mesh.bindMode;
  proxy.bindMatrix.copy(mesh.bindMatrix);proxy.bindMatrixInverse.copy(mesh.bindMatrixInverse);
  // Three's SkinnedMesh.raycast would otherwise rebuild posed bounds by
  // transforming every proxy vertex on each pointer move.
  if(!sampled.geometry.boundingBox)sampled.geometry.computeBoundingBox();
  if(!sampled.geometry.boundingSphere)sampled.geometry.computeBoundingSphere();
  const size=sampled.geometry.boundingBox.getSize(new THREE.Vector3());
  const pad=Math.max(size.x,size.y,size.z)*.75+.04;
  proxy.boundingBox=sampled.geometry.boundingBox.clone().expandByScalar(pad);
  proxy.boundingSphere=sampled.geometry.boundingSphere.clone();
  proxy.boundingSphere.radius+=pad;
 }
 if(sampled.owned)s.hoverGeometries.add(sampled.geometry);
 s.hoverSurfaceCache.set(mesh,{source:geometry,version,proxy,owned:sampled.owned});
 return proxy;
}
function se343HoverContact(part,cast){
 const mesh=part.mesh,proxy=se343SurfaceMesh(mesh);
 if(!proxy)return null;
 proxy.matrixWorld.copy(mesh.matrixWorld);
 if(mesh.isSkinnedMesh){
  proxy.skeleton=mesh.skeleton;proxy.bindMatrix.copy(mesh.bindMatrix);
  proxy.bindMatrixInverse.copy(mesh.bindMatrixInverse);
 }
 const contacts=[];
 proxy.raycast(cast,contacts);
 let first=null;
 for(const hit of contacts)
  if(hit.distance>=cast.near&&hit.distance<=cast.far&&(!first||hit.distance<first.distance))first=hit;
 return first?{id:part.id,name:part.name,mesh,
  distance:first.distance,point:first.point,hoverSurface:true}:null;
}
/* SE343_MODEL_VR_SURFACE_HOVER_END */

function se340PartEntries(){return se340XR.frameEntries||se350Tools()?.projection?.()?.meshes||se340Bridge()?.projection?.()?.meshes||[];}
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
  selectionIds:se350Tools()?.selection?.().ids||[],selectionCount:se350Tools()?.selection?.().ids.length||0,
  surface:se350Surface()?.inspect?.(),profile:se350Input.inspect(),wheel:se340XR.wheel,brushRadius:se340XR.brushRadius,brushStrength:se340XR.brushStrength,sculptTool:se340XR.sculptTool,
  frameCount:se340XR.frameCount,partCount:native.partCount||0,selectedId:native.selectedId||null,
  documentToken:native.documentToken??null,canUndo:!!native.canUndo,canRedo:!!native.canRedo,
  undoDepth:native.undoDepth||0,redoDepth:native.redoDepth||0,
  modelRootBorrowed:!!native.borrowed,nativeParentRestored:native.nativeParentRestored!==false,
  gesture:se340XR.gesture?{kind:se340XR.gesture.kind,id:se340XR.gesture.id,mode:se340XR.gesture.mode,
   hand:se340XR.gesture.record.input?.handedness||'none'}:null,
  controllers:se340XR.controllers.map(r=>({index:r.index,handedness:r.input?.handedness||'none',
   targetTracked:!!r.targetTracked,gripTracked:!!r.gripTracked,hoverId:r.hit?.id||null,reticleVisible:!!r.dot.visible})),
  lastAction:se340XR.lastAction,error:se340XR.error,
   viewMode:se340XR.viewMode,page:se340XR.page,displayMode:se340XR.displayMode,
   aimCalibration:se340XR.aim?{left:{...se340XR.aim.left},right:{...se340XR.aim.right}}:null,
   picking:{...se340XR.pickStats,hoverFaceRaycasts:0}};
 if(options?.geometry&&se340XR.scene){
  se340XR.scene.updateMatrixWorld(true);
  result.targetCenters=se340PartEntries().filter(e=>e.mesh?.visible!==false).map(e=>{
   const b=se340PartBox(e.mesh);return {id:e.id,name:e.name,center:b.getCenter(new THREE.Vector3()).toArray(),size:b.getSize(new THREE.Vector3()).toArray()};
  });
  result.paletteActions=(se340XR.ui?.targets||[]).filter(t=>t.userData?.se340Action&&t.visible!==false)
   .map(t=>({action:t.userData.se340Action,center:t.getWorldPosition(new THREE.Vector3()).toArray()}));
  result.modelRootMatrix=se350Root().matrixWorld.toArray();
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
 const actions=Object.fromEntries(['inspect','move','rotate','scale','undo','redo','focus','recenter','help','precision','snap','exit','views','tools','aim','view-front','view-back','view-left','view-right','view-top','view-bottom','view-iso','aim-hand','aim-yaw-minus','aim-yaw-plus','aim-pitch-minus','aim-pitch-plus','aim-reset','aim-reset-all','mesh','studio','sculpt','draw','two-hand','extrude','selection-clear','next-brush','sculpt-push','sculpt-smooth','sculpt-flatten','sculpt-inflate','sculpt-pinch','sculpt-translate','brush-radius-minus','brush-radius-plus','brush-strength-minus','brush-strength-plus','draw-finish','draw-clear','lasso','lasso-clear']
  .map(id=>[id,()=>se340ModelXRAction(id)]));
 s.ui=se340CreateModelVRUI({THREE,actions,status:se340Notice});s.scene.add(s.ui.root);
 const result=se340Bridge().borrowRoot(s.pivot);
 if(!result?.ok)throw Error('The native Modeler projection could not be borrowed.');
 s.documentToken=se340Bridge().inspect().documentToken;
 const initial=se340Bridge().projection();
 s.cachedEntries=initial.meshes;s.projectionRevision=initial.revision;
 for(const entry of initial.meshes.slice(0,4))
  if(entry.mesh?.visible!==false)se343SurfaceMesh(entry.mesh);
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
  s.yaw=Math.atan2(-forward.x,-forward.z);s.pitch=0;s.viewMode='orbit';s.rig.rotation.set(0,s.yaw,0);s.zoom=1;s.pan.set(0,0);s.presentation.scale.setScalar(s.fit);
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
/* SE344_MODEL_VR_AIM_VIEWS_START */
// Per-controller WebXR target-ray calibration. Meta's OS overlay pointer is
// not exposed to WebXR; calibrate a small local aim offset only when needed.
const SE344_AIM_KEY='swrlz-model-vr-pointer-calibration-v1';
/* SE345_MODEL_VR_DISPLAY_MODES_START */
// Display modes operate on borrowed runtime materials only, never the source
// model schema. Restore exact references on mode change, rebuild and VR exit.
const SE345_DISPLAY_OPTIONS=['textured','solid','wireframe','xray','normals'];
function se345DisplayMaterial(mode){
 const s=se340XR;
 if(!s.displayMaterials)s.displayMaterials=new Map();
 if(s.displayMaterials.has(mode))return s.displayMaterials.get(mode);
 let mat=null;
 if(mode==='solid')mat=new THREE.MeshStandardMaterial({color:0xb6bbc6,roughness:.78,metalness:.06,side:THREE.DoubleSide});
 if(mode==='wireframe')mat=new THREE.MeshBasicMaterial({color:0x83f6e8,wireframe:true,side:THREE.DoubleSide,depthWrite:false});
 if(mode==='xray')mat=new THREE.MeshBasicMaterial({color:0x9dcaff,transparent:true,opacity:.24,depthWrite:false,side:THREE.DoubleSide});
 if(mode==='normals')mat=new THREE.MeshNormalMaterial({side:THREE.DoubleSide});
 if(!mat)return null;
 se340Own(mat);s.displayMaterials.set(mode,mat);return mat;
}
function se345SyncDisplay(){
 const s=se340XR;if(!s.scene)return;
 if(!s.displayOriginals)s.displayOriginals=new Map();
 const keep=new Set(),entries=s.cachedEntries||s.frameEntries||[];
 for(const entry of entries){
  const mesh=entry?.mesh;
  if(!mesh?.isMesh)continue;
  keep.add(mesh);
  if(!s.displayOriginals.has(mesh))s.displayOriginals.set(mesh,mesh.material);
  const original=s.displayOriginals.get(mesh);
  const target=s.displayMode==='textured'?original:se345DisplayMaterial(s.displayMode);
  if(target&&mesh.material!==target)mesh.material=target;
 }
 for(const [mesh,original] of [...s.displayOriginals]){
  if(!keep.has(mesh)){mesh.material=original;s.displayOriginals.delete(mesh);}
 }
}
function se345SetDisplay(mode){
 if(!SE345_DISPLAY_OPTIONS.includes(mode))return false;
 const s=se340XR;
 s.displayMode=mode;se345SyncDisplay();
 se340Notice('Model display: '+mode+'. Original materials are retained and restored when VR closes.');
 return true;
}
function se345RestoreDisplay(){
 const s=se340XR;
 for(const [mesh,material] of s.displayOriginals||[])mesh.material=material;
 s.displayOriginals?.clear();s.displayMaterials?.clear();s.displayMode='textured';
}
/* SE345_MODEL_VR_DISPLAY_MODES_END */
function se344ReadAim(){
 const empty=()=>({yaw:0,pitch:0});
 try{
  const value=JSON.parse(localStorage.getItem(SE344_AIM_KEY)||'null');
  if(!value||typeof value!=='object')return {left:empty(),right:empty()};
  const read=v=>({yaw:THREE.MathUtils.clamp(Number(v?.yaw)||0,-25,25),
   pitch:THREE.MathUtils.clamp(Number(v?.pitch)||0,-25,25)});
  return {left:read(value.left),right:read(value.right)};
 }catch(_){return {left:empty(),right:empty()};}
}
function se344WriteAim(){
 try{localStorage.setItem(SE344_AIM_KEY,JSON.stringify(se340XR.aim));}catch(_){}
}
function se344Hand(record){
 const h=record.input?.handedness;
 return h==='left'||h==='right'?h:record.index===0?'left':'right';
}
function se344AimQuat(record){
 const a=se340XR.aim?.[se344Hand(record)]||{yaw:0,pitch:0};
 return new THREE.Quaternion().setFromEuler(
  new THREE.Euler(THREE.MathUtils.degToRad(a.pitch),THREE.MathUtils.degToRad(a.yaw),0,'YXZ'));
}
function se344SetView(view){
 const s=se340XR;
 if(s.gesture){se340Notice('Release the active grip before changing view.');return false;}
 const yaw=Math.atan2(-s.forward.x,-s.forward.z);
 const presets={
  front:[0,0],back:[Math.PI,0],left:[-Math.PI/2,0],
  right:[Math.PI/2,0],top:[0,-Math.PI/2+.035],
  bottom:[0,Math.PI/2-.035],iso:[-Math.PI/4,-.62]
 };
 if(view==='orbit'){s.viewMode='orbit';se340Notice('Free orbit · use right joystick.');return true;}
 const pose=presets[view];if(!pose)return false;
 s.yaw=yaw+pose[0];s.pitch=pose[1];s.viewMode=view;
 se340Notice(view[0].toUpperCase()+view.slice(1)+' model view · right stick resumes free orbit.');
 return true;
}
function se344AimAction(action){
 const s=se340XR;
 if(action==='aim-hand'){s.aimHand=s.aimHand==='left'?'right':'left';}
 else if(action==='aim-reset-all'){
  s.aim={left:{yaw:0,pitch:0},right:{yaw:0,pitch:0}};
  se344WriteAim();
 }else{
  const a=s.aim[s.aimHand];
  const step=2;
  if(action==='aim-yaw-minus')a.yaw=THREE.MathUtils.clamp(a.yaw-step,-25,25);
  else if(action==='aim-yaw-plus')a.yaw=THREE.MathUtils.clamp(a.yaw+step,-25,25);
  else if(action==='aim-pitch-minus')a.pitch=THREE.MathUtils.clamp(a.pitch-step,-25,25);
  else if(action==='aim-pitch-plus')a.pitch=THREE.MathUtils.clamp(a.pitch+step,-25,25);
  else if(action==='aim-reset'){a.yaw=0;a.pitch=0;}
  else return false;
  se344WriteAim();
 }
 for(const record of s.controllers){
  if(record.ray)record.ray.quaternion.copy(se344AimQuat(record));
  record.nextHoverAt=0;record.hit=null;record.hoverKey=null;
 }
 const a=s.aim[s.aimHand];
 se340Notice(s.aimHand.toUpperCase()+' target-ray offset: yaw '+a.yaw+'°, pitch '+a.pitch+'°. Stored on this browser.');
 return true;
}
/* SE344_MODEL_VR_AIM_VIEWS_END */

function se340Cast(record){
 if(!record.targetTracked)return null;
 record.target.updateMatrixWorld(true);
 const origin=record.target.getWorldPosition(new THREE.Vector3());
 const correction=se344AimQuat(record);
 record.ray.quaternion.copy(correction);
 const direction=new THREE.Vector3(0,0,-1).applyQuaternion(correction)
  .transformDirection(record.target.matrixWorld).normalize();
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
  // Bounding boxes are broadphase only. The reticle hits a connected,
  // lightweight model surface (including current skin pose), not the box.
  let nearest=null;
  for(const entry of entries){
   if(!cast.ray.intersectsBox(se340PartBox(entry.mesh)))continue;
   const hit=se343HoverContact(entry,cast);
   if(hit&&(!nearest||hit.distance<nearest.distance))nearest=hit;
  }
  return finish(nearest||{distance:1.2,point:cast.ray.at(1.2,new THREE.Vector3())});
 }
 // Only user selection/grip calls test the triangles, including skinned faces.
 const roots=entries.filter(e=>e.mesh.isSkinnedMesh||
  cast.ray.intersectsBox(se340PartBox(e.mesh))).map(e=>e.mesh);
 stats.preciseCandidates+=roots.length;
 for(const hit of cast.intersectObjects(roots,true)){
  if(hit.object.userData?.atelierHelper||hit.object.userData?.se350SurfacePreview)continue;
  let mesh=hit.object;while(mesh&&!roots.includes(mesh))mesh=mesh.parent;
  const entry=entries.find(e=>e.mesh===mesh);
  if(entry)return finish({id:entry.id,name:entry.name,mesh,distance:hit.distance,point:hit.point,face:hit.face,normal:hit.normal});
 }
 return finish({distance:1.2,point:cast.ray.at(1.2,new THREE.Vector3())});
}
function se340Pressed(record,index,threshold=.62){const b=record.input?.gamepad?.buttons?.[index];return !!b&&(b.pressed||b.value>=threshold);}
function se340GripPose(record){
 if(!record.gripTracked)return null;record.grip.updateMatrixWorld(true);
 return {position:record.grip.getWorldPosition(new THREE.Vector3()),quaternion:record.grip.getWorldQuaternion(new THREE.Quaternion())};
}
function se350Tools(){return ModelAtelier.vrTools;}
function se350Surface(){return ModelAtelier.vrSurface;}
function se350Invalidate(){
 const s=se340XR;s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.pickMatrixFrame=-1;
 se343DropHoverSurfaces();s.boxCache=new WeakMap();for(const r of s.controllers){r.nextHoverAt=0;r.hit=null;}
}
function se350Root(){return se340Bridge().projection().root;}
function se350RootPoint(point){const root=se350Root();root.updateWorldMatrix(true,false);return root.worldToLocal(point.clone());}
function se350Record(hand){return se340XR.controllers.find(r=>r.input?.handedness===hand);}
function se350Result(result,label,record){
 if(result?.ok===false){
  const reason=result.error||result.reason||'Operation unavailable.',messages={
   SCULPT_REQUIRES_BIND_POSE:'Return the rig to its rest pose before sculpting.',EXTRUDE_REQUIRES_BIND_POSE:'Return the rig to its rest pose before extruding.',
   SCULPT_REQUIRES_UNREFINED_MESH:'Disable refinement before sculpting to keep saved vertex edits aligned.',
   OUTLINE_SELF_INTERSECTS:'The outline crosses itself. Draw one simple loop.',OUTLINE_REQUIRES_THREE_CORNERS:'Draw at least three corners before releasing the trigger.',
   OUTLINE_AREA_TOO_SMALL:'Draw a larger outline.',NATIVE_VERTEX_EDIT_BUDGET_REACHED:'This part reached its saved vertex-edit limit. Undo or edit another part.',
   SCULPT_PREVIEW_VERTEX_BUDGET_EXCEEDED:'This mesh exceeds the VR sculpt preview budget. Use a simpler source mesh.',
   MODEL_SELECTION_LIMIT_32:'Select up to 32 parts for one modeling gesture.'};
  se340Notice(messages[reason]||String(reason).replaceAll('_',' ').toLowerCase(),true);return false;}
 if(result?.changed){se350Invalidate();se340Pulse(record,.35,28);}
 se340XR.lastAction=result?.changed?label:'No model change';se340Notice(se340XR.lastAction);se340Publish();return true;
}
function se340CancelGesture(message='Edit canceled.'){
 const s=se340XR,g=s.gesture;
 se350Tools()?.cancel?.();se350Surface()?.cancel?.();se340Bridge()?.cancel?.();
 if(!g)return false;
 s.gesture=null;for(const r of s.controllers){r.blockGrip=true;r.blockTrigger=true;}
 if(g.kind==='view'&&g.before){s.anchor.position.copy(g.before.anchor);s.zoom=g.before.zoom;s.yaw=g.before.yaw;s.pitch=g.before.pitch;}
 if(s.drawLine)s.drawLine.visible=false;
 se350Invalidate();s.lastAction='Canceled '+g.kind;se340Notice(message);se340Publish();return true;
}
function se340FinishGesture(record){
 const s=se340XR,g=s.gesture;if(!g||!['view','group','two-hand','extrude'].includes(g.kind))return false;
 if(g.record!==record&&g.kind!=='two-hand'&&!(g.kind==='view'&&g.pair&&(record===g.pair.left||record===g.pair.right)))return false;
 if(!record.gripTracked||!se340VisibleSession())return se340CancelGesture('Tracking changed; preview canceled.');
 se340UpdateGesture();if(s.gesture!==g)return false;s.gesture=null;
 if(g.kind==='view'){se340Notice('Workbench placed · model data unchanged.');se340Publish();return true;}
 if(g.kind==='extrude')return se350Result(se350Surface().extrudeEnd(true),'Extruded outline',record);
 return se350Result(se350Tools().endGroup(true),'Applied '+g.mode,record);
}
function se350BeginView(record){
 const s=se340XR,pose=se340GripPose(record);if(!pose||!s.anchor)return false;
 s.gesture={kind:'view',record,mode:'presentation',hand:pose,before:{anchor:s.anchor.position.clone(),zoom:s.zoom,yaw:s.yaw,pitch:s.pitch}};
 se340Notice('Move workbench · both grips resize and turn the view; B cancels.');return true;
}
function se350Pair(){
 const left=se340XR.inputSample?.held.pan?.source?.record||se350Record('left'),right=se340XR.inputSample?.held.grab?.source?.record||se350Record('right');
 if(!left||!right||left===right||!se340XR.inputSample?.held.pan||!se340XR.inputSample?.held.grab)return null;
 const a=se340GripPose(left),b=se340GripPose(right);if(!a||!b)return null;
 const span=b.position.clone().sub(a.position);if(span.length()<.06)return null;
 return {left,right,a,b,mid:a.position.clone().add(b.position).multiplyScalar(.5),span,distance:span.length()};
}
function se340BeginGesture(record,purpose='grab'){
 const s=se340XR;if(s.gesture||record.blockGrip||!se340VisibleSession())return false;
 const side=record.input?.handedness,pose=se340GripPose(record);if(!pose)return false;
 if(s.mode==='two-hand'){
  const pair=se350Pair();if(!pair){se340Notice('Two-hand edit armed · hold both grips on your selection.');return false;}
  const result=se350Tools().beginGroup(undefined,'two-hand');if(result?.ok===false)return se350Result(result,'',record);
  const root=se350Root();root.updateWorldMatrix(true,false);
  s.gesture={kind:'two-hand',record:pair.right,mode:'two-hand',pair,rootInverse:root.matrixWorld.clone().invert(),rootQuaternion:root.getWorldQuaternion(new THREE.Quaternion())};
  se340Notice('Two-hand geometry edit · spread, turn, move; release either grip to apply. B cancels.');se340Pulse(record,.3,25);return true;
 }
 if(purpose==='pan')return se350BeginView(record);
 if(s.mode==='inspect')return false;
 if(!['move','rotate','scale','extrude'].includes(s.mode))return false;
 const hit=se340Hit(record,false);if(hit?.ui||!hit?.id)return false;
 if(s.mode==='extrude'){
  se350Tools().select(hit.id);
  const result=se350Surface().extrudeBegin(hit.id);if(result?.ok===false)return se350Result(result,'',record);
  result.mesh.updateWorldMatrix(true,false);se350Invalidate();
  s.gesture={kind:'extrude',record,id:hit.id,mode:'extrude',hand:pose,rootInverse:result.mesh.matrixWorld.clone().invert(),normal:new THREE.Vector3(...result.normal)};
  se340Notice('Pull grip away from the face to give it thickness · B cancels.');return true;
 }
 const tools=se350Tools();if(!tools.selection().ids.includes(hit.id))tools.select(hit.id);
 const result=tools.beginGroup(undefined,s.mode);if(result?.ok===false)return se350Result(result,'',record);
 const root=se350Root();root.updateWorldMatrix(true,false);
 s.gesture={kind:'group',record,id:hit.id,mode:s.mode,hand:pose,rootInverse:root.matrixWorld.clone().invert(),rootQuaternion:root.getWorldQuaternion(new THREE.Quaternion())};
 se340Notice(s.mode==='scale'?'Lift/lower grip to size selection · release applies; B cancels.':'Grip edits selection · release applies; B cancels.');se340Pulse(record,.25,25);return true;
}
function se340UpdateGesture(){
 const s=se340XR,g=s.gesture;if(!g)return;
 if(!se340VisibleSession()||!g.record.targetTracked||!g.record.gripTracked){se340CancelGesture('Tracking changed; preview canceled.');return;}
 const pose=se340GripPose(g.record);if(!pose)return;
 const gain=(s.precision||s.inputSample?.held.precision||s.inputSample?.held.fine)?(s.inputSample?.thresholds.precisionMultiplier??.25):1;
 if(g.kind==='sculpt'){se350UpdateStroke(g);return;}
 if(g.kind==='draw'||g.kind==='lasso'){se350UpdateDraw(g);return;}
 if(g.kind==='view'){
  let pair=se350Pair();
  if(!pair&&g.pair){const a=se340GripPose(g.pair.left),b=se340GripPose(g.pair.right);if(a&&b){const span=b.position.clone().sub(a.position);pair={a,b,span,distance:span.length(),mid:a.position.clone().add(b.position).multiplyScalar(.5)};}}
  if(pair&&!g.pair){g.pair=pair;g.pairBefore={anchor:s.anchor.position.clone(),zoom:s.zoom,yaw:s.yaw};}
  if(g.pair){
   if(!pair)return;
   const ratio=THREE.MathUtils.clamp(pair.distance/g.pair.distance,.1,10),before=g.pairBefore;
   s.zoom=THREE.MathUtils.clamp(before.zoom*ratio,.25,5);
   const angle=Math.atan2(pair.span.x,pair.span.z)-Math.atan2(g.pair.span.x,g.pair.span.z);
   s.yaw=before.yaw+Math.atan2(Math.sin(angle),Math.cos(angle));s.anchor.position.copy(before.anchor).add(pair.mid.clone().sub(g.pair.mid));
  }else s.anchor.position.copy(g.before.anchor).add(pose.position.clone().sub(g.hand.position));
  return;
 }
 if(g.kind==='extrude'){
  const delta=pose.position.clone().applyMatrix4(g.rootInverse).sub(g.hand.position.clone().applyMatrix4(g.rootInverse));
  const result=se350Surface().extrudeUpdate(delta.dot(g.normal)*gain);if(result?.ok===false)se340CancelGesture(result.error);return;
 }
 let translation=new THREE.Vector3(),rotation=new THREE.Quaternion(),scale=1;
 if(g.kind==='two-hand'){
  const pair=se350Pair();
  // A release still has a tracked final pose; sample it before commit.
  const a=se340GripPose(g.pair.left),b=se340GripPose(g.pair.right);
  if(!a||!b){se340CancelGesture('A controller lost tracking; preview canceled.');return;}
  const mid=a.position.clone().add(b.position).multiplyScalar(.5),span=b.position.clone().sub(a.position);
  if(span.length()<.04){se340CancelGesture('Hands too close; preview canceled.');return;}
  translation.copy(mid).applyMatrix4(g.rootInverse).sub(g.pair.mid.clone().applyMatrix4(g.rootInverse)).multiplyScalar(gain);
  scale=Math.pow(THREE.MathUtils.clamp(span.length()/g.pair.distance,.05,20),gain);
  const world=new THREE.Quaternion().setFromUnitVectors(g.pair.span.clone().normalize(),span.normalize());
  rotation.slerp(g.rootQuaternion.clone().invert().multiply(world).multiply(g.rootQuaternion),gain);
 }else if(g.mode==='move'){
  if(pose.position.distanceTo(g.hand.position)>.001)translation.copy(pose.position).applyMatrix4(g.rootInverse).sub(g.hand.position.clone().applyMatrix4(g.rootInverse)).multiplyScalar(gain);
 }else if(g.mode==='rotate'){
  const world=pose.quaternion.clone().multiply(g.hand.quaternion.clone().invert());
  rotation.slerp(g.rootQuaternion.clone().invert().multiply(world).multiply(g.rootQuaternion),gain);
 }else if(g.mode==='scale')scale=Math.exp(2.4*(pose.position.y-g.hand.position.y)*gain);
 if(s.snap){translation.toArray().forEach((v,i)=>translation.setComponent(i,Math.round(v/.01)*.01));scale=1+Math.round((scale-1)/.05)*.05;
  const e=new THREE.Euler().setFromQuaternion(rotation),step=THREE.MathUtils.degToRad(s.inputSample?.thresholds.snapDegrees??15);e.set(...e.toArray().slice(0,3).map(v=>Math.round(v/step)*step));rotation.setFromEuler(e);}
 const result=se350Tools().updateGroup({translation:translation.toArray(),rotation:rotation.toArray(),scale});
 if(result?.ok===false)se340CancelGesture(result.error||'Source changed; preview canceled.');
}
function se340Trigger(record,additive=false){
 if(!se340VisibleSession()||!record.targetTracked||record.blockTrigger)return;
 const start=performance.now(),hit=se340Hit(record,false);record.hit=hit;
 if(hit?.ui){if(hit.action&&se340XR.ui.press(hit.target)!==false)se340ModelXRAction(hit.action,record);return;}
 if(se340XR.gesture)return;
 if(se340XR.mode==='draw'&&!additive){se350BeginDraw(record);return;}
 if(se340XR.mode==='lasso'&&!additive){const exact=se340Hit(record,true);if(exact?.id&&!exact.ui)se350BeginLasso(record,exact);return;}
 if(se340XR.mode==='sculpt'&&!additive){const exact=se340Hit(record,true);if(exact?.id&&!exact.ui)se350BeginStroke(record,exact);return;}
 if(hit?.id){
  const result=se350Tools().select(hit.id,{additive});if(result?.ok===false){se350Result(result,'',record);return;}
  se350Invalidate();const count=se350Tools().selection().ids.length;
  se340XR.lastAction=additive?count+' parts selected':'Selected '+hit.name;
  se340Notice(se340XR.lastAction);se340Pulse(record,.3,25);se340Publish();
 }
 const stats=se340XR.pickStats;stats.lastTriggerMs=+(performance.now()-start).toFixed(2);stats.maxTriggerMs=Math.max(stats.maxTriggerMs||0,stats.lastTriggerMs);
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
function se350BeginStroke(record,hit){
 const s=se340XR;if(s.gesture||!hit?.mesh)return false;
 se350Tools().select(hit.id);
 const result=se350Surface().sculptBegin(hit.id,{operation:s.sculptTool,radius:s.brushRadius,strength:s.brushStrength});
 if(result?.ok===false)return se350Result(result,'',record);
 se350Invalidate();
 s.gesture={kind:'sculpt',mode:'sculpt',record,id:hit.id,mesh:result.mesh,lastPoint:null};
 se340Notice('Sculpt '+s.sculptTool+' · release trigger to apply; left trigger smooths; B cancels.');
 se350UpdateStroke(s.gesture);return true;
}
function se350UpdateStroke(g){
 const hit=se340Hit(g.record,true);if(!hit||hit.ui||hit.id!==g.id||!hit.point)return;
 const mesh=g.mesh;mesh.updateWorldMatrix(true,false);
 const center=mesh.worldToLocal(hit.point.clone());
 // Exact triangle normals are native local normals; normals supplied in world
 // space use the transpose linear transform, including nonuniform scale.
 const normal=hit.face?.normal?.clone?.()||hit.normal?.clone?.().applyMatrix3(new THREE.Matrix3().setFromMatrix4(mesh.matrixWorld).transpose())||se340Cast(g.record).ray.direction.clone().negate().applyMatrix3(new THREE.Matrix3().setFromMatrix4(mesh.matrixWorld).transpose());normal.normalize();
 const delta=g.lastPoint?center.clone().sub(g.lastPoint):new THREE.Vector3();g.lastPoint=center.clone();
 const result=se350Surface().sculptUpdate({center:center.toArray(),normal:normal.toArray(),delta:delta.toArray(),dt:se340XR.frameDt||1/72,radius:se340XR.brushRadius,strength:se340XR.brushStrength,smooth:!!se340XR.inputSample?.held['temporary-smooth']});
 if(result?.ok===false)se340CancelGesture(result.error||'Sculpt source changed.');
}
function se350BeginDraw(record){
 const s=se340XR,cast=se340Cast(record);if(!cast||s.gesture)return false;
 const point=cast.ray.at(.5,new THREE.Vector3()),normal=cast.ray.direction.clone().negate(),root=se350Root();root.updateWorldMatrix(true,false);
 const localNormal=normal.clone().applyMatrix3(new THREE.Matrix3().setFromMatrix4(root.matrixWorld).transpose()).normalize();
 const result=se350Surface().drawBegin({normal:localNormal.toArray(),name:'VR outline'});if(result?.ok===false)return se350Result(result,'',record);
 s.gesture={kind:'draw',mode:'draw',record,plane:new THREE.Plane().setFromNormalAndCoplanarPoint(normal,point),points:[]};
 se350UpdateDraw(s.gesture);se340Notice('Draw outline · move pointer on the plane; release trigger creates a face. B cancels.');return true;
}
function se350BeginLasso(record,hit){
 const s=se340XR;se350Tools().select(hit.id);
 const normal=hit.face?.normal?.clone?.()||new THREE.Vector3(0,0,1);
 const result=se350Surface().lassoBegin(hit.id,{normal:normal.toArray(),name:'VR lasso'});if(result?.ok===false)return se350Result(result,'',record);
 result.mesh.updateWorldMatrix(true,false);se350Invalidate();
 const worldNormal=normal.clone().applyMatrix3(new THREE.Matrix3().getNormalMatrix(result.mesh.matrixWorld)).normalize();
 s.gesture={kind:'lasso',mode:'lasso',record,id:hit.id,mesh:result.mesh,plane:new THREE.Plane().setFromNormalAndCoplanarPoint(worldNormal,hit.point),points:[]};
 se350UpdateDraw(s.gesture);se340Notice('Lasso surface region · trace a simple loop on this surface; release to save its sculpt mask.');return true;
}
function se350UpdateDraw(g){
 const cast=se340Cast(g.record);if(!cast)return;
 const point=cast.ray.intersectPlane(g.plane,new THREE.Vector3());if(!point||point.distanceTo(cast.ray.origin)>3)return;
 const previous=g.points[g.points.length-1];if(previous&&previous.distanceTo(point)<.003)return;
 if(g.points.length>=128)return;
 const result=g.kind==='lasso'?se350Surface().lassoUpdate(g.mesh.worldToLocal(point.clone()).toArray()):se350Surface().drawUpdate(se350RootPoint(point).toArray());if(result?.ok===false){se340CancelGesture(result.error);return;}
 g.points.push(point.clone());const s=se340XR;
 if(!s.drawLine){const geometry=se340Own(new THREE.BufferGeometry());geometry.setAttribute('position',new THREE.BufferAttribute(new Float32Array(257*3),3));
  s.drawLine=new THREE.Line(geometry,se340Own(new THREE.LineBasicMaterial({color:0x83ffe5,depthTest:false})));s.drawLine.renderOrder=9000;s.scene.add(s.drawLine);}
 const attr=s.drawLine.geometry.attributes.position;g.points.forEach((p,i)=>attr.setXYZ(i,p.x,p.y,p.z));
 if(g.points.length>2){const first=g.points[0];attr.setXYZ(g.points.length,first.x,first.y,first.z);}
 s.drawLine.geometry.setDrawRange(0,g.points.length+(g.points.length>2?1:0));attr.needsUpdate=true;s.drawLine.frustumCulled=false;s.drawLine.visible=true;
}
function se350FinishTrigger(record){
 const s=se340XR,g=s.gesture;if(!g||g.record!==record||!['sculpt','draw','lasso'].includes(g.kind))return false;
 if(!record.targetTracked||!record.gripTracked||!se340VisibleSession())return se340CancelGesture('Tracking changed; preview canceled.');
 se340UpdateGesture();if(s.gesture!==g)return false;s.gesture=null;if(s.drawLine)s.drawLine.visible=false;
 const result=g.kind==='sculpt'?se350Surface().sculptEnd(true):g.kind==='lasso'?se350Surface().lassoEnd(true):se350Surface().drawEnd(true);
 if(result?.ok!==false&&g.kind==='draw'&&result?.id){se350Tools().select(result.id);s.mode='extrude';s.page='draw';}
 if(result?.ok!==false&&g.kind==='lasso'){s.mode='sculpt';s.page='sculpt';}
 return se350Result(result,g.kind==='lasso'?'Lasso mask saved · Sculpt edits this region':g.kind==='draw'?'Created outline face · grip to extrude':'Applied '+s.sculptTool+' stroke',record);
}
function se350Navigate(sample,dt){
 const s=se340XR;if(!se340VisibleSession())return;
 const axes=sample.axes,gain=(s.precision?.4:1),turn=sample.thresholds.turnSensitivity;
 if(axes.radius&&s.mode==='sculpt'){
  s.brushRadius=THREE.MathUtils.clamp(s.brushRadius*Math.exp(axes.radius.x*dt*1.5*sample.thresholds.brushSensitivity),.03,2);
  s.brushStrength=THREE.MathUtils.clamp(s.brushStrength-axes.radius.y*dt*.5*sample.thresholds.brushSensitivity,.01,.5);
 }
 if(axes.strength)s.brushStrength=THREE.MathUtils.clamp(s.brushStrength-axes.strength.y*dt*.5,.01,.5);
 if(s.gesture&&s.gesture.kind!=='view')return;
 if(axes.navigate&&!s.gesture){s.pan.x=THREE.MathUtils.clamp(s.pan.x-axes.navigate.x*dt*.42*gain,-.85,.85);s.pan.y=THREE.MathUtils.clamp(s.pan.y+axes.navigate.y*dt*.42*gain,-.65,.65);}
 const orbit=axes.orbit;
 if(orbit){
  if(sample.held.pan&&!(s.gesture?.kind==='view'&&s.gesture.pair)){s.zoom=THREE.MathUtils.clamp(s.zoom*Math.exp(-orbit.y*dt*1.15*gain),.25,5);}
  else if(!s.gesture){s.viewMode='orbit';s.yaw+=orbit.x*dt*1.35*gain*turn;s.pitch=THREE.MathUtils.clamp(s.pitch-orbit.y*dt*1.05*gain*turn,-1.54,1.54);}
 }
 if(axes.zoom&&!s.gesture)s.zoom=THREE.MathUtils.clamp(s.zoom*Math.exp(-axes.zoom.y*dt*1.15*gain),.25,5);
}
function se350Dispatch(sample){
 const s=se340XR;
 if(sample.cancel){se340ModelXRAction('cancel');return;}
 if(sample.profileChanged){se340CancelGesture('Controller profile changed · release controls to continue.');s.ui.closeWheel();s.wheel=null;}
 for(const event of sample.events){
  const record=event.source?.record||se350Record(event.hand)||null;
  if(event.phase==='end'){
   if(['grab','pan','two-hand'].includes(event.action)&&record)se340FinishGesture(record);
   else if(event.action==='stroke'&&record)se350FinishTrigger(record);
   else if(['tool-wheel','category-wheel'].includes(event.action)){
    const hit=record&&se340Hit(record,false),chosen=s.ui.releaseWheel(hit?.ui?hit.target:null);s.wheel=null;
    if(chosen)se340ModelXRAction(chosen,record);
   }
   continue;
  }
  if(['select','multiselect'].includes(event.action)&&record)se340Trigger(record,event.action==='multiselect');
  else if(event.action==='stroke'&&record&&event.phase==='start')se340Trigger(record);
  else if(event.action==='sample'&&record){
   const hit=se340Hit(record,false);if(hit?.ui){se340Trigger(record);continue;}
   if(hit?.id&&!s.gesture){se350Tools().select(hit.id);se350Invalidate();se340Notice('Sampled '+hit.name+' · hold left trigger for temporary Smooth.');}
  }
  else if(event.action==='grab'&&event.phase==='start'&&record){record.held=true;se340BeginGesture(record,'grab');}
  else if(event.action==='pan'&&event.phase==='start'&&record){record.held=true;se340BeginGesture(record,'pan');}
  else if(event.action==='two-hand'){
   // Explicit geometry mode is required; this shortcut never arms it implicitly.
   if(s.mode==='two-hand'&&!s.gesture&&record)se340BeginGesture(record,'grab');
  }
  else if(['tool-wheel','category-wheel'].includes(event.action)){
   se340CancelGesture('Preview canceled before tool selection.');s.paletteVisible=true;s.helpVisible=false;s.wheel=event.action==='tool-wheel'?(s.mode==='sculpt'?'brush':'tools'):'studio';
   se340PlacePalette(s.lastViewer||s.anchor);s.ui.openWheel(s.wheel);
  }
  else{
   const alias={tool:s.mode==='sculpt'?'next-brush':'next-tool','toggle-snap':'snap','reset-camera':'recenter',wireframe:s.displayMode==='wireframe'?'display-textured':'display-wireframe','open-settings':'help'};
   if(!['temporary-smooth','fine'].includes(event.action))se340ModelXRAction(alias[event.action]||event.action,record);
  }
 }
 // Tap-to-select profiles also end sculpt/draw on the associated trigger release.
 const g=s.gesture;
 if(g&&['sculpt','draw','lasso'].includes(g.kind)){
  const activeStroke=sample.held.stroke?.source?.record;
  const trigger=sample.buttons[g.record.input?.handedness==='left'?'LT':'RT'];
  if(activeStroke!==g.record&&!trigger?.down)se350FinishTrigger(g.record);
 }
 for(const record of s.controllers){
  const grip=sample.buttons[record.input?.handedness==='left'?'LG':'RG'];record.held=!!grip?.down;
  if(!grip?.physical)record.blockGrip=false;
  const trigger=sample.buttons[record.input?.handedness==='left'?'LT':'RT'];if(!trigger?.physical)record.blockTrigger=false;
 }
 if(s.mode==='two-hand'&&!s.gesture){const pair=se350Pair();if(pair)se340BeginGesture(pair.right,'grab');}
}

function se340Poll(record,frame,dt){
 record.ray.visible=record.targetTracked;record.dot.visible=record.targetTracked;record.body.visible=record.gripTracked;
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
 const selectedIds=new Set(se350Tools().selection().ids);
 const selected=entries.find(e=>e.id===native.selectedId),hover=s.controllers.map(r=>r.hit).find(h=>h?.id&&!selectedIds.has(h.id));
 s.selectedOutline.visible=selectedIds.size>0;if(selectedIds.size){s.selectedOutline.box.makeEmpty();for(const entry of entries)if(selectedIds.has(entry.id))s.selectedOutline.box.union(se340PartBox(entry.mesh));}
 s.hoverOutline.visible=!!hover;if(hover)s.hoverOutline.box.copy(se340PartBox(hover.mesh));
 const uiHit=s.controllers.map(r=>r.hit).find(h=>h?.ui&&h.action);s.ui.hover(uiHit?.target||null);
 s.ui.root.visible=s.paletteVisible;
 const state={selectedRegionId:se350Surface().inspect().selectedRegionId,selectedCount:selectedIds.size,sculptTool:s.sculptTool,brushRadius:s.brushRadius,brushStrength:s.brushStrength,drawPointCount:['draw','lasso'].includes(s.gesture?.kind)?s.gesture.points.length:0,twoHand:s.mode==='two-hand',wheelVisible:!!s.wheel,
  mode:s.mode,selectedName:selected?.name||'',hoverName:hover?.name||'',dragging:!!s.gesture,
  canUndo:!!native.canUndo,canRedo:!!native.canRedo,message:s.message,
  tracking:s.controllers.filter(r=>r.targetTracked).length+' controllers tracked',
  precision:s.precision,snap:s.snap,helpVisible:s.helpVisible,
   page:s.page,viewMode:s.viewMode,displayMode:s.displayMode,aimHand:s.aimHand,
   aimYaw:s.aim?.[s.aimHand]?.yaw||0,aimPitch:s.aim?.[s.aimHand]?.pitch||0,
   controllerHint:'Left grip moves view · Right grip edits · Both grips in Two-hand mode · B cancels'};
 const key=JSON.stringify(state);if(key!==s.stateKey){s.stateKey=key;s.ui.update(state);}
}
function se340ModelXRAction(action,record=null){
 const s=se340XR;if(!s.session||!s.scene||!se340VisibleSession())return false;
 if(action==='exit'){void se340ModelXRExit();return true;}
 if(action.startsWith('display-')){
  if(!se345SetDisplay(action.slice(8)))return false;
  se340SyncUI();se340Publish();return true;
 }
 if(action==='tools'||action==='views'||action==='aim'||action==='cameras'){
  s.page=action;s.helpVisible=false;
  se340Notice(action==='aim'?'Aim alignment · select hand and nudge yaw/pitch to match Meta pointer.':
   action==='views'?'Model perspectives · choose front, back, side, top, bottom or isometric.':'Model tools.');
  se340SyncUI();se340Publish();return true;
 }
 if(action.startsWith('view-')){
  if(!se344SetView(action.slice(5)))return false;
  se340SyncUI();se340Publish();return true;
 }
 if(action.startsWith('aim-')){
  if(!se344AimAction(action))return false;
  se340SyncUI();se340Publish();return true;
 }
 if(action==='cancel'){
  s.ui.closeWheel();s.wheel=null;
  const cancelled=se340CancelGesture();if(!cancelled)s.mode='inspect';
  se340Notice(cancelled?'Preview canceled · release grip to start again.':'Inspect mode · trigger selects; no grip edits.');
  se340Publish();return true;
 }
 if(action==='palette'){s.paletteVisible=!s.paletteVisible;s.helpVisible=false;if(s.paletteVisible)se340PlacePalette(s.lastViewer||s.anchor);se340Publish();return true;}
 if(action==='selection-clear'){if(s.gesture)se340CancelGesture();se350Tools().select(null);se350Invalidate();se340Notice('Selection cleared.');se340SyncUI();se340Publish();return true;}
 if(action==='mesh'||action==='studio'){se340CancelGesture();s.page=action;s.helpVisible=false;if(action==='mesh')s.mode='inspect';se340SyncUI();se340Publish();return true;}
 if(action==='next-brush')action='sculpt-'+SE350_BRUSHES[(SE350_BRUSHES.indexOf(s.sculptTool)+1)%SE350_BRUSHES.length];
 if(action.startsWith('sculpt-')){const tool=action.slice(7);if(!SE350_BRUSHES.includes(tool))return false;se340CancelGesture();s.sculptTool=tool;action='sculpt';}
 if(action.startsWith('brush-')){const radius=action.includes('radius'),direction=action.endsWith('plus')?1:-1;
  if(radius)s.brushRadius=THREE.MathUtils.clamp(s.brushRadius*Math.pow(1.25,direction),.03,2);
  else s.brushStrength=THREE.MathUtils.clamp(s.brushStrength+direction*.05,.01,.5);
  se340Notice('Brush radius '+s.brushRadius.toFixed(3)+' · strength '+Math.round(s.brushStrength*100)+'%');se340SyncUI();return true;}
 if(action==='lasso'){se340CancelGesture();s.mode='lasso';s.page='draw';se340Notice('Lasso · trace a loop on one surface with the trigger; release saves a sculpt mask.');se340SyncUI();se340Publish();return true;}
 if(action==='lasso-clear'){se350Surface().lassoSelect(se340Bridge().inspect().selectedId,null);se340Notice('Whole surface · lasso mask off. Saved regions remain in the native inspector.');se340SyncUI();se340Publish();return true;}
 if(action==='draw-clear'){se340CancelGesture('Outline discarded.');se340SyncUI();return true;}
 if(action==='draw-finish'){if(s.gesture?.kind==='draw')return se350FinishTrigger(s.gesture.record);return false;}
 if(action==='extrude'){se340CancelGesture();s.mode='extrude';s.page='draw';se340Notice('Point at a drawn face, hold grip and pull to add thickness.');se340SyncUI();se340Publish();return true;}
 if(action==='next-tool')action=SE340_MODES[(SE340_MODES.indexOf(s.mode)+1)%SE340_MODES.length];
 if(SE340_MODES.includes(action)){
  se340CancelGesture('Previous preview canceled.');s.mode=action;if(action==='sculpt'||action==='draw')s.page=action;
  se340Notice(action==='sculpt'?'Sculpt · hold trigger on a surface; left stick changes radius / strength.':action==='draw'?'Draw · hold trigger and trace an outline; release creates a face.':action==='two-hand'?'Two-hand geometry edit armed · select parts, then hold both grips.':action==='inspect'?'Inspect mode · trigger selects; no grip edits.':action==='scale'?'Scale · grip and lift/lower your hand.':action==='rotate'?'Rotate · hold grip and turn your wrist.':'Move · hold grip and move your controller.');
 }else if(action==='undo'||action==='redo'){
  if(s.gesture){se340CancelGesture('Preview canceled. Press again to '+action+'.');return true;}
   const result=se340Bridge()[action]();s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;se343DropHoverSurfaces();s.boxCache=new WeakMap();
   se340Notice(result?.changed?action==='undo'?'Undid model edit.':'Redid model edit.':'No '+action+' step available.');
 }else if(action==='precision'){s.precision=!s.precision;se340Notice(s.precision?'Precision on · '+Math.round((s.inputSample?.thresholds.precisionMultiplier??.25)*100)+'% transform speed.':'Precision off.');}
 else if(action==='snap'){s.snap=!s.snap;se340Notice(s.snap?'Snap on · 0.01 move / '+(s.inputSample?.thresholds.snapDegrees??15)+'° turn / 5% size.':'Snap off.');}
 else if(action==='help'){s.helpVisible=!s.helpVisible;}
 else if(action==='recenter'||action==='focus'){se340Recenter(null,action==='focus');se340Notice(action==='focus'?'Selected part framed for inspection.':'Model view recentered.');}
 else return false;
 s.lastAction=action;if(record)se340Pulse(record,.2,20);se340SyncUI();se340Publish();return true;
}
function se350UpdateLassoGuide(){
 const s=se340XR,region=se350Surface().inspect().selectedRegion;
 if(!s.lassoGuide){const geometry=se340Own(new THREE.BufferGeometry());geometry.setAttribute('position',new THREE.BufferAttribute(new Float32Array(33*3),3));
  s.lassoGuide=new THREE.Line(geometry,se340Own(new THREE.LineBasicMaterial({color:0xffd183,depthTest:false,transparent:true,opacity:.85})));s.lassoGuide.matrixAutoUpdate=false;s.lassoGuide.frustumCulled=false;s.lassoGuide.renderOrder=9000;s.scene.add(s.lassoGuide);}
 const mesh=region&&se340PartEntries().find(e=>e.id===region.partId)?.mesh;
 s.lassoGuide.visible=!!mesh&&s.mode==='sculpt'&&!s.gesture?.kind?.includes('draw');if(!s.lassoGuide.visible)return;
 const key=JSON.stringify(region);if(key!==s.lassoGuideKey){s.lassoGuideKey=key;const attr=s.lassoGuide.geometry.attributes.position,points=region.pins.slice(0,32);[...points,points[0]].forEach((p,i)=>attr.setXYZ(i,...p));attr.needsUpdate=true;s.lassoGuide.geometry.setDrawRange(0,points.length+1);}
 mesh.updateWorldMatrix(true,false);s.lassoGuide.matrix.copy(mesh.matrixWorld);s.lassoGuide.matrixWorldNeedsUpdate=true;
}
function se350UpdateBrush(){
 const s=se340XR;if(!s.scene)return;
 if(!s.brushCursor){s.brushCursor=new THREE.Mesh(se340Own(new THREE.RingGeometry(.92,1,48)),se340Material(0x8bffe6,{side:THREE.DoubleSide,depthTest:false}));s.brushCursor.renderOrder=9002;s.scene.add(s.brushCursor);}
 const record=s.inputSample?.held.stroke?.source?.record||se350Record('right'),hit=record?.hit;
 s.brushCursor.visible=s.mode==='sculpt'&&!!hit?.id&&!hit.ui;
 if(s.brushCursor.visible){s.brushCursor.position.copy(hit.point);s.brushCursor.lookAt(record.target.getWorldPosition(new THREE.Vector3()));
  const size=hit.mesh.getWorldScale(new THREE.Vector3());s.brushCursor.scale.setScalar(s.brushRadius*Math.max(size.x,size.y,size.z));}
}

function se340ModelXRFrameCore(time,frame){
 const s=se340XR;if(!s.session||!s.scene)return;
 const dt=s.lastTime?THREE.MathUtils.clamp((time-s.lastTime)/1000,0,.05):0;s.lastTime=time;s.frameCount++;s.frameDt=dt;
 const bridge=se340Bridge(),native=bridge.inspect();
 if(!native.open||native.documentToken!==s.documentToken||!bridge.isBorrowed()){
  se340CancelGesture('The model workspace changed; leaving Model VR.');if(!s.ending)void se340ModelXRExit();return;
 }
 const viewer=se340Viewer(frame);if(viewer){s.lastViewer=viewer;if(!s.anchored)se340Recenter(viewer);}
 if(!se340VisibleSession()){se340CancelGesture('Headset menu open · preview canceled.');se350Input.reset();}
 for(const record of s.controllers){
  record.targetTracked=se340Tracked(record,frame,'target');record.gripTracked=se340Tracked(record,frame,'grip');
  record.pendingSelect=false;record.eventGripDown=false;record.eventGripUp=false;
 }
 const g=s.gesture;
 if(g&&(!g.record.targetTracked||!g.record.gripTracked||g.pair&&(!g.pair.left.gripTracked||!g.pair.right.gripTracked)))se340CancelGesture('Controller tracking lost; preview canceled.');
 se340UpdateView();
 if(!s.cachedEntries||s.projectionRevision!==native.revision){
  s.cachedEntries=se350Tools().projection().meshes;s.projectionRevision=native.revision;
  se343DropHoverSurfaces();s.boxCache=new WeakMap();se345SyncDisplay();
 }
 s.frameEntries=s.cachedEntries;
 const sample=se350Input.sample({time,context:['sculpt','draw','lasso'].includes(s.mode)?'sculpt':'model',sources:s.controllers.map(record=>({input:record.input,tracked:record.targetTracked&&record.gripTracked&&se340VisibleSession(),record}))});
 s.inputSample=sample;
 if(sample.resetRequired)se340CancelGesture(sample.trackingLost?'Controller tracking lost; preview canceled.':'Controller profile changed; preview canceled.');
 // The resolver removes release events when Cancel wins, before either hand commits.
 se350Dispatch(sample);se350Navigate(sample,dt);
 for(const record of s.controllers)se340Poll(record,frame,dt);
 se340UpdateGesture();se340UpdateView();
 if(s.gesture){se350Tools().projection();s.scene.updateMatrixWorld(true);}
 se350UpdateBrush();se350UpdateLassoGuide();se340SyncUI();renderer.render(s.scene,s.camera);s.frameEntries=null;
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
 se345RestoreDisplay();
 try{se340Bridge()?.releaseRoot?.();se350Tools()?.refreshSelection?.();}catch(error){s.error=String(error?.message||error);}
 for(const r of s.controllers){
  r.target.removeEventListener('connected',r.connected);r.target.removeEventListener('disconnected',r.disconnected);
  r.target.removeEventListener('selectstart',r.select);r.target.removeEventListener('squeezestart',r.squeeze);r.target.removeEventListener('squeezeend',r.release);
  r.target.remove(r.ray);r.grip.remove(r.body);r.target.removeFromParent();r.grip.removeFromParent();r.dot.removeFromParent();
 }
 se350Input.reset();s.inputSample=null;s.wheel=null;s.drawLine=null;s.brushCursor=null;s.lassoGuide=null;s.lassoGuideKey='';
 s.controllers=[];try{s.ui?.dispose();}catch(error){s.error=String(error?.message||error);}
 for(const resource of s.owned){try{resource.dispose();}catch(_){}}s.owned.clear();
 s.scene?.clear();s.scene=null;s.camera=null;s.ui=null;s.rig=null;s.presentation=null;s.pivot=null;
  s.session=null;s.busy=false;s.ending=false;s.anchored=false;s.gesture=null;s.documentToken=null;s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.pickMatrixFrame=-1;se343DropHoverSurfaces();s.hoverSurfaceMaterial=null;s.boxCache=new WeakMap();
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
  se350Input.reset();s.wheel=null;
  s.session=requested;s.mode='inspect';s.precision=false;s.snap=false;s.paletteVisible=true;s.helpVisible=false;
   s.page='tools';s.viewMode='orbit';s.aimHand='right';s.aim=se344ReadAim();s.displayMode='textured';s.displayOriginals=new Map();s.displayMaterials=new Map();
   s.frameCount=0;s.lastTime=0;s.stateKey='';s.anchored=false;s.ending=false;s.hoverId=null;s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.pickMatrixFrame=-1;se343DropHoverSurfaces();s.boxCache=new WeakMap();s.pickStats={hoverCount:0,preciseCount:0,preciseCandidates:0,lastHoverMs:0,maxHoverMs:0};s.pitch=0;
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
  s.supported=true;s.busy=false;se340Notice('Right trigger selects · Left trigger adds · Left grip moves view · Hold A for tools.');
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
