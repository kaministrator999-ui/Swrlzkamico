// §E v11.195: Quest Sheep Tag stability and spatial interaction repair.
// Appends to the existing XR source; no duplicate renderer or render loop.
// Native actor/game command ownership, project saves and Meta exit remain intact.
const se195={
 mode:'',page:'main',visible:false,radial:null,buttons:[],textures:[],hover:null,
 hands:new Map(),photo:false,photoWasPaused:false,photoFormat:'clean',
 menuOrbit:true,menuT:0,menuFacing:null,menuFocus:new THREE.Vector3(),
 menuStartSeen:false,lastFrame:0,rayHits:0,fastRayHits:0,uiBlocked:0,
 fogPaints:0,fogSkips:0,fogAt:0,lastFogSession:null,
 rigPosition:new THREE.Vector3(),rigReady:false,rigAt:0,
 lastError:'',lastAction:'',lastStatusAt:0,restore:null,shadowSaved:null,
 referenceBase:null,referenceOffset:new THREE.Vector3(),referenceWrites:0
};
const se195Gameplay=()=>!!se181XR.session&&renderer.xr.isPresenting&&se193XRGameActive();
const se195Menu=()=>!!se181XR.session&&renderer.xr.isPresenting&&se193XRMenuActive();
const se195Active=()=>!!se181XR.session&&renderer.xr.isPresenting;
function se195Mode(){
 if(se195Menu())return 'menu';
 if(se195Gameplay())return 'game';
 if(se193.editorCaptureOpen)return 'editor-capture';
 return 'editor';
}
function se195FocusSheep(){
 const active=(typeof seLevelsMenuActors==='function'?seLevelsMenuActors('st-sheep'):[])||[];
 const live=active.filter(o=>o?.visible&&o.userData?.baked!==false);
 const group=live.length?live:active;
 if(!group.length)return new THREE.Vector3(0,0,0);
 const out=new THREE.Vector3();
 group.forEach(a=>out.add(a.getWorldPosition(new THREE.Vector3())));
 return out.multiplyScalar(1/group.length);
}
function se195DisposeRadial(){
 if(se195.radial){
  scene.remove(se195.radial);
  se195.radial.traverse(o=>{
   o.geometry?.dispose?.();
   if(Array.isArray(o.material))o.material.forEach(m=>m?.dispose?.());
   else o.material?.dispose?.();
  });
 }
 for(const t of se195.textures)t.dispose();
 se195.radial=null;se195.buttons.length=0;se195.textures.length=0;se195.hover=null;
}
function se195Text(label,header=false){
 const c=document.createElement('canvas');c.width=512;c.height=256;
 const g=c.getContext('2d');
 g.clearRect(0,0,c.width,c.height);
 const grad=g.createLinearGradient(0,0,512,256);
 grad.addColorStop(0,header?'#27445d':'#133346');
 grad.addColorStop(1,header?'#17253d':'#15243a');
 g.fillStyle=grad;g.beginPath();g.roundRect(9,9,494,238,38);g.fill();
 g.lineWidth=12;g.strokeStyle=header?'#88f1ef':'#578d9e';g.stroke();
 g.textAlign='center';g.textBaseline='middle';
 g.font=header?'bold 48px sans-serif':'bold 51px sans-serif';
 g.fillStyle='#eafcff';g.fillText(label,256,132,450);
 const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;
 se195.textures.push(tex);return tex;
}
function se195Options(mode=se195.mode,page=se195.page){
 if(page==='build')return [['farm','FARM'],['income','INCOME'],['fort','FORT'],['back','BACK']];
 if(page==='capture')return [['photo','PHOTO'],['capture','CLEAN'],['debug','DEBUG'],['stereo','STEREO'],['back','BACK']];
 if(page==='more')return [['pause','PAUSE'],['restart','RESTART'],['stop','STOP'],['back','BACK']];
 if(page==='help')return [['back','BACK']];
 if(page==='place')return [['wall','WALL'],['rock','ROCK'],['undo','UNDO'],['back','BACK']];
 if(page==='aim')return [['aimLeft','AIM -'],['aimRight','AIM +'],['back','BACK']];
 if(mode==='menu')return [['start','PLAY'],['cinema','CINEMA'],['capturePage','CAPTURE'],['help','CONTROLS'],['editor','EDIT']];
 if(mode==='game')return [['follow','FOLLOW'],['free','FREE'],['buildPage','BUILD'],['capturePage','CAPTURE'],['more','SESSION']];
 if(mode==='editor-capture')return [['photo','PHOTO'],['capture','CLEAN'],['debug','DEBUG'],['stereo','STEREO'],['back','BACK']];
 return [['select','SELECT'],['move','MOVE'],['place','PREFABS'],['capturePage','CAPTURE'],['aim','AIM']];
}
function se195MakeRadial(reposition=true){
 const savedPos=se195.radial?.position.clone(),savedRot=se195.radial?.quaternion.clone();
 se195DisposeRadial();
 const actions=se195Options();
 const root=new THREE.Group();root.name='§E · Quest wrist radial menu';
 const face=new THREE.Mesh(new THREE.CircleGeometry(.43,48),
  new THREE.MeshBasicMaterial({color:0x091929,transparent:true,opacity:.88,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
 face.position.z=-.026;face.renderOrder=10100;face.userData.se195Block=true;
 root.add(face);
 const border=new THREE.Mesh(new THREE.RingGeometry(.415,.424,56),
  new THREE.MeshBasicMaterial({color:0x65e5dc,transparent:true,opacity:.88,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
 border.position.z=-.017;border.renderOrder=10101;root.add(border);
 const heading=se195.page==='main'?
  (se195.mode==='menu'?'SHEEP TAG':se195.mode==='game'?'SHEEP TOOLS':'§E TOOLS'):
  se195.page.toUpperCase();
 const headingMesh=new THREE.Mesh(new THREE.PlaneGeometry(.295,.075),
  new THREE.MeshBasicMaterial({map:se195Text(heading,true),transparent:true,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
 headingMesh.position.set(0,0,.014);headingMesh.renderOrder=10103;root.add(headingMesh);
 actions.forEach(([action,label],i)=>{
  const phi=-Math.PI/2+i*2*Math.PI/actions.length;
  const mesh=new THREE.Mesh(new THREE.PlaneGeometry(.228,.121),
   new THREE.MeshBasicMaterial({map:se195Text(label),transparent:true,opacity:1,
    depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
  mesh.position.set(Math.cos(phi)*.285,Math.sin(phi)*.284,.013);
  mesh.name='§E radial '+action;mesh.userData.se195Action=action;
  mesh.renderOrder=10104;mesh.frustumCulled=false;root.add(mesh);se195.buttons.push(mesh);
 });
 if(savedPos&&!reposition)root.position.copy(savedPos);
 if(savedRot&&!reposition)root.quaternion.copy(savedRot);
 root.visible=se195.visible;
 scene.add(root);se195.radial=root;
 if(reposition)se195PositionRadial(true);
}
function se195PositionRadial(force=false){
 if(!se195.radial||!se195Active())return;
 const right=se192InputRecord('right'),pose=se191XRHeadPose();
 if(!right?.controller||!pose)return;
 right.controller.updateMatrixWorld(true);
 const origin=right.controller.getWorldPosition(new THREE.Vector3());
 const dir=new THREE.Vector3(0,0,-1).transformDirection(right.controller.matrixWorld).normalize();
 const cameraRight=new THREE.Vector3().crossVectors(pose.forward,new THREE.Vector3(0,1,0));
 if(cameraRight.lengthSq()<.02)cameraRight.set(1,0,0);
 cameraRight.normalize();
 // Place ahead of the right-hand ray, but OFFSET from the beam centre so
 // the hand can rotate freely to select the near-field spokes.
 const wanted=origin.clone().addScaledVector(dir,.86)
  .addScaledVector(cameraRight,.19).add(new THREE.Vector3(0,.08,0));
 const distance=se195.radial.position.distanceTo(origin);
 if(force||distance>1.8){
  se195.radial.position.copy(wanted);
 }else if(distance>1.35){
  se195.radial.position.lerp(wanted,.045);
 }
 const facing=new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().lookAt(
  se195.radial.position,pose.eye,new THREE.Vector3(0,1,0)));
 if(force)se195.radial.quaternion.copy(facing);
 else se195.radial.quaternion.slerp(facing,.14);
}
function se195RadialHit(record,cast=se192Ray(record)){
 if(!se195.visible||!se195.radial?.visible||!cast)return null;
 se195.radial.updateMatrixWorld(true);
 const hits=cast.ray.intersectObjects(se195.buttons,true);
 const back=se195.radial.children.find(o=>o.userData?.se195Block);
 const bh=back?cast.ray.intersectObject(back,false):[];
 if(hits.length&&(!bh.length||hits[0].distance<bh[0].distance+.05)){
  return {ui:'se195:'+hits[0].object.userData.se195Action,
   distance:hits[0].distance,point:hits[0].point,button:hits[0].object};
 }
 if(bh.length)return {ui:'se195:block',distance:bh[0].distance,point:bh[0].point};
 return null;
}
function se195SetVisible(value){
 se195.visible=!!value;
 if(se195.visible){
  if(!se195.radial)se195MakeRadial(true);
  else {se195.radial.visible=true;se195PositionRadial(true);}
 }else if(se195.radial)se195.radial.visible=false;
}
function se195Page(page){
 se195.page=page;
 se195MakeRadial(false);
 se195SetVisible(true);
}
function se195EnterPhoto(){
 if(se195.photo)return;
 se195.photo=true;se195.photoWasPaused=!!paused;
 if(se195Gameplay()&&!paused){
  // Pause the simulation for stable scene framing, restore on leaving.
  document.getElementById('pauseBtn')?.click();
 }
 se195SetVisible(false);
 se195.lastAction='Photo mode · trigger captures · X returns to tools';
}
function se195LeavePhoto(){
 if(!se195.photo)return;
 se195.photo=false;
 if(stSession&&currentProject?.kind==='sheep-tag'&&!se195.photoWasPaused&&paused)
  document.getElementById('pauseBtn')?.click();
 se195.photoWasPaused=false;
 se195SetVisible(true);
}
function se195HandleAction(action,record){
 se195.lastAction=action;
 if(action==='block')return true;
 if(action==='back'){
  if(se195.mode==='editor-capture'){
   se193XRAction('back');se195SetVisible(false);
  }else se195Page('main');
  return true;
 }
 if(action==='buildPage')return se195Page('build'),true;
 if(action==='capturePage')return se195Page('capture'),true;
 if(action==='more')return se195Page('more'),true;
 if(action==='help')return se195Page('help'),true;
 if(action==='place')return se195Page('place'),true;
 if(action==='aim')return se195Page('aim'),true;
 if(action==='photo'){se195EnterPhoto();return true;}
 if(action==='cinema'){
  se195.menuOrbit=!se195.menuOrbit;
  se195.lastAction=se195.menuOrbit?'Sheep cinematic orbit on':'Fixed viewing position';
  se195SetVisible(false);return true;
 }
 if(['start','editor','follow','free','farm','income','fort','pause','restart','stop',
   'capture','debug','stereo'].includes(action)){
  se193XRAction(action);
  if(action==='start'||action==='editor')se195SetVisible(false);
  if(action==='capture'||action==='debug'||action==='stereo')se195SetVisible(false);
  return true;
 }
 if(['select','move','wall','rock','undo','aimLeft','aimRight'].includes(action)){
  se192Action(action,record);
  if(action!=='aimLeft'&&action!=='aimRight')se195SetVisible(false);
  return true;
 }
 return false;
}
function se195Select(record){
 if(!se195Active())return false;
 if(se195.photo){
  const done=se193XRCapture(se195.photoFormat);
  se195.lastAction=done?'Capture ready after leaving XR':'VR capture unavailable';
  return true;
 }
 const hit=se195RadialHit(record);
 if(hit?.ui){
  se195.uiBlocked++;
  return se195HandleAction(hit.ui.slice(6),record);
 }
 // A visible radial is MODAL: a miss never selects a house behind it.
 if(se195.visible){se195.uiBlocked++;return true;}
 return false;
}
function se195Button(record,button){
 if(!se195Active())return false;
 if(button==='x'){
  if(se195.photo){se195LeavePhoto();return true;}
  se195SetVisible(!se195.visible);
  return true;
 }
 if(se195.photo)return true;
 if(button==='a'&&se195.visible)return true; // don't cycle houses behind a menu
 return false;
}
function se195AcquireHand(record){
 if(!record?.controller||!record?.input||!record.se192||record.se195)return;
 const color=record.input.handedness==='left'?0x67e7fc:0xfec46d;
 const grip=renderer.xr.getControllerGrip?.(record.index)||record.controller;
 if(grip!==record.controller)scene.add(grip);
 const body=new THREE.Group();body.name='§E Quest controller marker';
 const matte=new THREE.MeshStandardMaterial({color:0x24364c,roughness:.55,metalness:.42});
 const accent=new THREE.MeshBasicMaterial({color,toneMapped:false});
 const core=new THREE.Mesh(new THREE.CylinderGeometry(.027,.039,.17,10),matte);
 core.rotation.x=Math.PI/2;core.position.set(0,-.015,.025);body.add(core);
 const band=new THREE.Mesh(new THREE.TorusGeometry(.058,.008,6,24),accent);
 band.rotation.x=Math.PI/2;band.position.set(0,.025,-.035);body.add(band);
 const nozzle=new THREE.Mesh(new THREE.IcosahedronGeometry(.029,1),accent);
 nozzle.position.set(0,.04,-.072);body.add(nozzle);
 grip.add(body);
 const pivot=record.se192.pivot;
 // Share the original tapered beam geometry. One extra transparent low-cost
 // halo and 8 moving motes are cheap compared with a particle emitter.
 const halo=new THREE.Mesh(record.se192.beam.geometry,
  new THREE.MeshBasicMaterial({color,transparent:true,opacity:.19,
   depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false}));
 halo.name='§E aim aura';halo.scale.set(2.35,2.35,1);
 halo.renderOrder=10009;halo.frustumCulled=false;pivot.add(halo);
 const array=new Float32Array(8*3);
 const pointsGeom=new THREE.BufferGeometry();
 pointsGeom.setAttribute('position',new THREE.BufferAttribute(array,3));
 const points=new THREE.Points(pointsGeom,new THREE.PointsMaterial({color,
  size:.013,transparent:true,opacity:.65,depthTest:false,depthWrite:false,
  blending:THREE.AdditiveBlending,sizeAttenuation:true}));
 points.name='§E aim sparks';points.renderOrder=10010;points.frustumCulled=false;pivot.add(points);
 record.se195={body,grip,halo,points,matte,accent,pointsGeom,array};
 se195.hands.set(record.index,record.se195);
}
function se195UpdateHand(record,t,dist){
 const visual=record.se195;if(!visual)return;
 visual.halo.scale.z=Math.max(.1,Math.min(dist,2.5));
 const arr=visual.array;
 for(let i=0;i<8;i++){
  const a=i*.8+t*1.7,span=.10+i*.13;
  arr[i*3]=Math.sin(a)*(.007+i*.001);
  arr[i*3+1]=Math.cos(a*1.17)*(.005+i*.001);
  arr[i*3+2]=-Math.min(dist,1.65)*span;
 }
 visual.pointsGeom.attributes.position.needsUpdate=true;
}
function se195CleanupHands(){
 for(const record of se181XR.controllers){
  const h=record.se195;if(!h)continue;
  h.body.removeFromParent();
  for(const mesh of h.body.children)mesh.geometry?.dispose?.();
  h.matte.dispose();h.accent.dispose();
  h.halo.removeFromParent();h.halo.material.dispose();
  // Halo geometry is shared with original se192 beam; let se192 own it.
  h.points.removeFromParent();h.pointsGeom.dispose();h.points.material.dispose();
  delete record.se195;
 }
 se195.hands.clear();
}
// Reuse one XR reference space after the authored landing offset.
// Otherwise each tick nests a transform inside the previous reference space.
function se195MoveRig(dx,dy,dz){
 if(![dx,dy,dz].every(Number.isFinite))return false;
 const current=renderer.xr.getReferenceSpace?.();
 if(!current?.getOffsetReferenceSpace||typeof XRRigidTransform!=='function')
  return se192MoveBy(dx,dy,dz);
 try{
  if(!se195.referenceBase){
   se195.referenceBase=current;se195.referenceOffset.set(0,0,0);
  }
  const next=se195.referenceOffset.clone().add(new THREE.Vector3(dx,dy,dz));
  const shifted=se195.referenceBase.getOffsetReferenceSpace(new XRRigidTransform({
   x:-next.x,y:-next.y,z:-next.z
  }));
  renderer.xr.setReferenceSpace(shifted);
  se195.referenceOffset.copy(next);se195.referenceWrites++;
  return true;
 }catch(e){
  se195.lastError='XR rig: '+String(e?.message||e).slice(0,140);
  return false;
 }
}
function se195FollowCamera(dt){
 const s=stSession;
 if(!s||!se195Gameplay())return;
 const unit=s.units.find(u=>u.id===s.controlledId);
 if(!unit?.pos)return;
 const pose=se191XRHeadPose();if(!pose)return;
 if(!se195.rigReady){
  const front=pose.forward.clone().setY(0);
  if(front.lengthSq()<.01)front.set(0,0,-1);
  front.normalize();
  se193.angle=Math.atan2(front.x,front.z);
  se193.focus.copy(unit.pos).setY(0);
  se193.follow=true;
  se195.rigReady=true;se195.rigAt=performance.now();
 }
 const left=se192Stick(se192InputRecord('left'));
 const right=se192Stick(se192InputRecord('right'));
 const front=new THREE.Vector3(Math.sin(se193.angle),0,Math.cos(se193.angle));
 const side=new THREE.Vector3(front.z,0,-front.x);
 if(!se195.photo&&(Math.abs(left.x)+Math.abs(left.y)>.07)){
  se193.follow=false;
  se193.focus.addScaledVector(side,left.x*dt*18*se193.zoom)
   .addScaledVector(front,-left.y*dt*18*se193.zoom);
 }
 if(!se195.photo){
  se193.angle+=right.x*dt*.70;
  se193.zoom=THREE.MathUtils.clamp(se193.zoom+right.y*dt*.5,.75,2.15);
 }
 if(se193.follow){
  se193.focus.lerp(new THREE.Vector3(unit.pos.x,0,unit.pos.z),Math.min(1,dt*5.2));
 }
 const bound=Number(s.rules?.bounds)||40;
 se193.focus.x=THREE.MathUtils.clamp(se193.focus.x,-bound,bound);
 se193.focus.z=THREE.MathUtils.clamp(se193.focus.z,-bound,bound);
 const horizontal=new THREE.Vector3(Math.sin(se193.angle),0,Math.cos(se193.angle));
 const wanted=se193.focus.clone().addScaledVector(horizontal,-25*se193.zoom);
 wanted.y=17*se193.zoom;
 // Absolute tracked EYE target, not a camera-parent offset: preserves room
 // movement and eliminates the accumulating side drift from the prior rig.
 const delta=wanted.sub(pose.eye);
 const speed=se195.rigAt&&performance.now()-se195.rigAt<1100?22:8;
 const maximum=Math.max(0,dt*speed);
 if(maximum&&delta.length()>maximum)delta.setLength(maximum);
 if(delta.lengthSq()>.0004)se195MoveRig(delta.x,delta.y,delta.z);
}
function se195MenuCamera(dt){
 if(!se195Menu())return;
 const pose=se191XRHeadPose();if(!pose)return;
 const focus=se195FocusSheep();
 se195.menuFocus.lerp(focus,Math.min(1,dt*2.5));
 if(!se195.menuFacing){
  const front=pose.forward.clone().setY(0);
  if(front.lengthSq()<.01)front.set(0,0,-1);
  se195.menuFacing=front.normalize();
 }
 se195.menuT+=Math.max(0,dt);
 const forward=se195.menuFacing,side=new THREE.Vector3(-forward.z,0,forward.x);
 // Slow shallow orbit (~0.45m span), not a forced yaw or a full-speed
 // artificial 360-degree turn: the Quest headset keeps native head look.
 const sideways=se195.menuOrbit?Math.sin(se195.menuT*.12)*.45:0;
 const wanted=se195.menuFocus.clone().addScaledVector(forward,-13.7)
  .addScaledVector(side,sideways);
 wanted.y=7.8;
 const delta=wanted.sub(pose.eye),step=Math.max(0,dt*7);
 if(step&&delta.length()>step)delta.setLength(step);
 if(delta.lengthSq()>.0001)se195MoveRig(delta.x,delta.y,delta.z);
}
function se195FogPrepare(s){
 if(!se195Active()||!s?.fog)return;
 const f=s.fog;
 f.mesh.position.y=Math.max(.17,f.mesh.position.y);
 const mat=f.mesh.material;
 mat.depthWrite=false;mat.depthTest=true;mat.polygonOffset=true;
 mat.polygonOffsetFactor=-2;mat.polygonOffsetUnits=-4;
 mat.needsUpdate=true;
 // Keep cosmetic fog modest on the Quest; leave the logical visibility grid
 // untouched (fog doesn't confer knowledge to wolves or sheep).
 const cap=Math.min(256,f.width*3);
 if(f.canvas.width!==cap){
  f.canvas.width=f.canvas.height=cap;
  if(f.softMemory)f.softMemory.width=f.softMemory.height=cap;
 }
 f.texture.magFilter=THREE.LinearFilter;
 f.texture.minFilter=THREE.LinearFilter;
 f.texture.generateMipmaps=false;
 se195.fogAt=0;se195.lastFogSession=s;
}
// WebXR framebuffer scale must be selected BEFORE Quest presentation.
// Sheep Tag's high actor/submesh count benefits from reducing the render
// target modestly (0.72 vs 0.8, ~19% fewer pixels at otherwise equal setup).
const se195OriginalFramebuffer=se191XRPrepareFramebuffer;
se191XRPrepareFramebuffer=function(){
 se191XR.framebufferScale=currentProject?.kind==='sheep-tag'?.72:.8;
 return se195OriginalFramebuffer();
};
const se195OriginalCreateFog=stCreateFog;
stCreateFog=function(s){
 se195OriginalCreateFog(s);
 if(se195Active())se195FogPrepare(s);
};
const se195OriginalSoftFog=stSoftFogPaint;
stSoftFogPaint=function(s){
 if(!se195Gameplay())return se195OriginalSoftFog(s);
 if(se195.lastFogSession!==s)se195FogPrepare(s);
 const time=performance.now();
 if(se195.fogAt&&time-se195.fogAt<290){se195.fogSkips++;return;}
 se195.fogAt=time;se195.fogPaints++;
 return se195OriginalSoftFog(s);
};
const se195OriginalTeamFog=se156PaintTeamFog;
se156PaintTeamFog=function(s,force=false){
 if(!se195Gameplay())return se195OriginalTeamFog(s,force);
 const now=performance.now();
 if(!force&&se195.lastFogSession===s&&now-se195.fogAt<290)return;
 return se195OriginalTeamFog(s,force);
};
const se195OriginalUpdateCamera=stUpdateCamera;
stUpdateCamera=function(dt=0){
 if(se195Gameplay())return;
 return se195OriginalUpdateCamera(dt);
};
const se195OriginalHudRefresh=stRefreshHUD;
stRefreshHUD=function(force=false){
 if(se195Gameplay()){
  // The browser HUD is invisible inside immersive WebXR; game-state and
  // authoritative commands still run each frame.
  return;
 }
 return se195OriginalHudRefresh(force);
};
const se195OriginalMinimap=stUiDrawMinimap;
stUiDrawMinimap=function(state){
 if(se195Gameplay())return;
 return se195OriginalMinimap(state);
};
const se195OriginalRaycast=se192Raycast;
let se195PreciseSelection=false;
se192Raycast=function(record){
 if(!se195Active())return se195OriginalRaycast(record);
 const cast=se192Ray(record);
 if(!cast)return {empty:true,distance:1};
 if(se195.visible){
  const menu=se195RadialHit(record,cast);
  if(menu){se195.rayHits++;return menu;}
  return {ui:'se195:block',distance:Math.min(1.5,cast.ray.far||1.5),
   point:cast.origin.clone().addScaledVector(cast.direction,1.4)};
 }
 if(se195.photo)return {empty:true,distance:1.5};
 if(se195Gameplay()&&!se195PreciseSelection){
  // Avoid recursive ray tests against every detailed house/actor twice
  // each headset frame. Exact objects are tested only on trigger.
  const at=se193XRGameGround(record);
  if(at){
   const d=at.distanceTo(cast.origin);
   if(d<cast.ray.far&&d>.025){
    se195.fastRayHits++;
    return {ground:true,distance:d,point:at};
   }
  }
  return {empty:true,distance:1.8};
 }
 return se195OriginalRaycast(record);
};
const se195OldGameSelect=se193XRGameSelect;
se193XRGameSelect=function(record){
 se195PreciseSelection=true;
 try{return se195OldGameSelect(record);}
 finally{se195PreciseSelection=false;}
};
const se195PreviousSelect=se192Select;
se192Select=function(record){
 if(se195Select(record))return;
 return se195PreviousSelect(record);
};
const se195PreviousButton=se192XRGamepadButton;
se192XRGamepadButton=function(record,button){
 if(se195Button(record,button))return true;
 return se195PreviousButton(record,button);
};
// Retire the two duplicate "EXIT VR" signs. Quest's own system menu exits,
// and the existing visible browser toolbar continues to offer an Exit VR.
se181XRMakeExitPanel=function(){};
se191XRMakeBeacon=function(){};
se192CreatePanel=function(){
 se192.panel=null;se192.panelButtons.length=0;se192.panelTextures.length=0;
 se192.panelVisible=false;
};
se193XRPanelFor=function(){se193XRDisposePanel();};
se193XRPanelHit=function(){return null;};
const se195OldRenderRay=se192RenderRay;
se192RenderRay=function(record,hit){
 se195OldRenderRay(record,hit);
 if(!se195Active()||!record?.se192)return;
 const cast=se192Ray(record);if(!cast)return;
 const {beam,dot}=record.se192;
 const target=THREE.MathUtils.clamp(Number(hit?.distance)||1.5,.12,se195Gameplay()?140:24);
 beam.scale.z=Math.min(target,2.5);
 dot.position.copy(cast.origin).addScaledVector(cast.direction,target);
 dot.scale.setScalar(hit?.ui?.startsWith('se195:')?.72:THREE.MathUtils.clamp(target*.036,.7,2.5));
 dot.visible=!!hit&&!hit.empty;
 if(hit?.ui?.startsWith('se195:')){
  beam.material.color.setHex(0xa3f9dc);
 }else if(!hit?.empty)beam.material.color.setHex(0xffdc99);
 se195UpdateHand(record,performance.now()/1000,target);
};
const se195OldSnap=se193XRSnapFollow;
se193XRSnapFollow=function(){
 se195OldSnap();se195.rigReady=false;
};
const se195OldCamera=se193XRCameraFrame;
se193XRCameraFrame=function(dt){return se195FollowCamera(dt);};
const se195OldCapture=se193XRCapture;
se193XRCapture=function(mode='clean'){
 const visuals=[];
 for(const rec of se181XR.controllers){
  for(const o of [rec.se195?.body,rec.se195?.halo,rec.se195?.points]){
   if(o){visuals.push([o,o.visible]);o.visible=false;}
  }
 }
 if(se195.radial){visuals.push([se195.radial,se195.radial.visible]);se195.radial.visible=false;}
 try{return se195OldCapture(mode);}
 finally{for(const [mesh,visible] of visuals)mesh.visible=visible;}
};
const se195OldStart=se193XRStart;
se193XRStart=function(){
 se195OldStart();
 se195.mode='';se195.page='main';se195.visible=false;
 se195.menuStartSeen=false;se195.menuT=0;se195.menuFacing=null;
 se195.rigReady=false;se195.rigAt=0;se195.lastFrame=performance.now();
 se195.photo=false;se195.photoWasPaused=false;
 se195.referenceBase=null;se195.referenceOffset.set(0,0,0);
 se195.referenceWrites=0;
 if(currentProject?.kind==='sheep-tag'&&renderer.shadowMap){
  se195.shadowSaved=renderer.shadowMap.enabled;
  renderer.shadowMap.enabled=false; // no costly meadow shadow pass in stereo
 }
};
const se195OldStop=se193XRCleanup;
se193XRCleanup=function(){
 se195LeavePhoto();
 se195DisposeRadial();se195CleanupHands();
 se195.mode='';se195.visible=false;se195.rigReady=false;
 se195.menuFacing=null;se195.lastFogSession=null;se195.fogAt=0;
 se195.referenceBase=null;se195.referenceOffset.set(0,0,0);
 if(se195.shadowSaved!==null&&renderer.shadowMap){
  renderer.shadowMap.enabled=se195.shadowSaved;se195.shadowSaved=null;
 }
 se195OldStop();
};
const se195OldXRFrame=se193XRFrame;
se193XRFrame=function(){
 se195OldXRFrame();
 if(!se195Active())return;
 const now=performance.now(),dt=Math.min(.05,Math.max(0,(now-(se195.lastFrame||now))/1000));
 se195.lastFrame=now;
 const kind=se195Mode();
 if(kind!==se195.mode){
  const prior=se195.mode;se195.mode=kind;se195.page='main';
  se195.rigReady=false;se195.menuT=0;se195.menuFacing=null;
  // Menu is visible when entering the cinematic; gameplay/editor are clean
  // until X summons the wrist dial.
  se195.visible=kind==='menu';
  se195MakeRadial(true);
  if(prior==='menu')se195.menuStartSeen=false;
 }
 if(kind==='menu'){
  if(!se195.menuStartSeen && seLevelsOwns() &&
      seLevelsCurrent()?.role==='menu'&&!seLevels.playingMenu){
   // Start the REAL authored-actor cinematic rather than pointing the VR
   // camera at random buildings in the static editor scene.
   se195.menuStartSeen=true;
   seLevelsPlayMenu();
  }
  se195MenuCamera(dt);
 }
 for(const rec of se181XR.controllers)se195AcquireHand(rec);
 if(se195.visible)se195PositionRadial();
 const right=se192InputRecord('right');
 if(right&&se195.visible){
  const hover=se195RadialHit(right);
  const focus=hover?.button||null;
  if(focus!==se195.hover){
   if(se195.hover)se195.hover.material.opacity=1;
   if(focus)focus.material.opacity=.78;
   se195.hover=focus;
  }
 }
};
window.SWYRL_ENGINE_VR_POLISH=Object.freeze({
 diagnose:()=>({
  xr:se195Active(),mode:se195.mode,menuVisible:se195.visible,
  page:se195.page,photo:se195.photo,
  focusedOnSheep:se193.follow,zoom:se193.zoom,
  menuOrbit:se195.menuOrbit,
  controllers:se195.hands.size,
  fastRayHits:se195.fastRayHits,radialHits:se195.rayHits,
  uiBlocked:se195.uiBlocked,fogPaints:se195.fogPaints,
  fogThrottled:se195.fogSkips,
  referenceWrites:se195.referenceWrites,referenceDepth:'fixed-base',
  framebufferPreference:se191XR.framebufferScale,
  shadowsEnabled:!!renderer.shadowMap?.enabled,
  drawCalls:renderer.info?.render?.calls??null,
  triangles:renderer.info?.render?.triangles??null,
  lastAction:se195.lastAction,lastError:se195.lastError
 }),
 photo:se195EnterPhoto,
 capture:mode=>se193XRCapture(mode),
 menu:()=>se195SetVisible(!se195.visible)
});