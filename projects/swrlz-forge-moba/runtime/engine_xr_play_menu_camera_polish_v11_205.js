// §E v11.205 — Sheep Tag PLAY tactical camera + wrist ray/hover polish.
// The native Quest HMD pose is never rotated. No new renderer or frame loop.
const se205={
 profile:'tactical',heights:{tactical:18,forward:10},
 root:null,focus:null,hoverAt:0,hoverChanges:0,rayHits:0,rayMisses:0,
 panelsDecorated:0,decorReuses:0,effectsFrames:0,menuPointerFrames:0,
 overlays:0,overlayFrames:0,overlayWas:false,overlayLatch:false,
 skippedFogPaints:0,skippedInputFrames:0,skippedCameraFrames:0,
 lastError:''
};
function se205OverlayActive(){
 const active=!!se181XR.session&&renderer.xr.isPresenting;
 return active&&['visible-blurred','hidden'].includes(se181XR.session.visibilityState);
}
function se205ApplyCamera(mode){
 if(!['tactical','forward'].includes(mode))return false;
 se205.profile=mode;
 // Tactical moves the camera vertically into a ~40° overhead world view
 // at default zoom, not down into the earlier 16° shallow perspective.
 // Do not tilt or relocate HMD tracking. The v11.203 forward placement
 // mapping remains independent of view height.
 se200.vertical=se202.vertical=se203.vertical=se205.heights[mode];
 return true;
}
se205ApplyCamera('tactical');
const se205PriorOptions=se195Options;
se195Options=function(mode=se195.mode,page=se195.page){
 if(mode==='game'&&page==='view')
  return [['viewTactical','TACTICAL'],['viewForward','FORWARD'],['back','BACK']];
 const opts=se205PriorOptions(mode,page);
 if(mode==='game'&&page==='main')return [...opts,['viewPage','VIEW']];
 return opts;
};
const se205PriorAction=se195HandleAction;
se195HandleAction=function(action,record){
 if(se195.mode==='game'&&action==='viewPage'){
  se195Page('view');return true;
 }
 if(se195.mode==='game'&&['viewTactical','viewForward'].includes(action)){
  se205ApplyCamera(action==='viewTactical'?'tactical':'forward');
  se195.lastAction='Sheep Tag VR view: '+se205.profile;
  se195Page('main');return true;
 }
 return se205PriorAction(action,record);
};
function se205DecorateMenu(){
 const root=se195.radial;
 if(!root)return;
 if(root.userData.se205Decor){
  se205.decorReuses++;return;
 }
 root.userData.se205Decor=true;
 root.scale.setScalar(.86);
 // One lightweight halo and one fixed ten-point sparkle ring per cached page.
 // They are disposed with the existing root when the XR session ends.
 const halo=new THREE.Mesh(new THREE.RingGeometry(.425,.452,56),
  new THREE.MeshBasicMaterial({color:0x3ccac7,transparent:true,opacity:.13,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,
   toneMapped:false,blending:THREE.AdditiveBlending}));
 halo.name='§E VR menu subtle rim';halo.position.z=-.011;
 halo.renderOrder=10102;root.add(halo);
 const positions=new Float32Array(12*3);
 for(let i=0;i<12;i++){
  const a=i*Math.PI*2/12;
  positions[i*3]=Math.cos(a)*.439;
  positions[i*3+1]=Math.sin(a)*.439;
  positions[i*3+2]=.006;
 }
 const geom=new THREE.BufferGeometry();
 geom.setAttribute('position',new THREE.BufferAttribute(positions,3));
 const glints=new THREE.Points(geom,new THREE.PointsMaterial({
  color:0x9affee,size:.012,transparent:true,opacity:.58,
  sizeAttenuation:true,depthTest:false,depthWrite:false,
  blending:THREE.AdditiveBlending}));
 glints.name='§E VR cached menu glints';glints.renderOrder=10105;
 root.add(glints);
 const backs=[];
 for(const btn of se195.buttons){
  const bg=new THREE.Mesh(new THREE.PlaneGeometry(.242,.134),
   new THREE.MeshBasicMaterial({color:0x42d6c4,transparent:true,opacity:.09,
    depthTest:false,depthWrite:false,toneMapped:false,side:THREE.DoubleSide}));
  bg.name='§E VR interactive button glow';
  bg.position.copy(btn.position);bg.position.z-=.006;
  bg.renderOrder=10103;root.add(bg);
  btn.userData.se205Glow=bg;
  backs.push(bg);
 }
 root.userData.se205Vfx={halo,glints,backs};
 se205.panelsDecorated++;
}
const se205PriorMake=se195MakeRadial;
se195MakeRadial=function(reposition=true){
 const result=se205PriorMake(reposition);
 se205DecorateMenu();
 return result;
};
function se205MenuHover(){
 if(!se195.visible||!se195.radial?.visible||se205OverlayActive()){
  if(se205.focus){
   se205.focus=null;
  }
  return;
 }
 const now=performance.now();
 if(now-se205.hoverAt<55)return;
 se205.hoverAt=now;
 const record=se192InputRecord('right');
 const hit=record?se195RadialHit(record):null;
 const focus=hit?.button||null;
 if(focus!==se205.focus){
  se205.focus=focus;se205.hoverChanges++;
  if(focus&&record){
   try{record.input?.gamepad?.hapticActuators?.[0]?.pulse?.(.12,18)?.catch?.(()=>{});}catch(_){}
  }
 }
 for(const b of se195.buttons){
  const active=b===focus;
  b.material.opacity=active?1:.89;
  b.material.color.setHex(active?0xe9fffb:0xc6e8e8);
  b.scale.setScalar(active?1.095:1);
  const bg=b.userData?.se205Glow;
  if(bg)bg.material.opacity=active?.63:.09;
 }
 const root=se195.radial,vfx=root?.userData?.se205Vfx;
 if(vfx){
  vfx.glints.rotation.z=now*.00011;
  vfx.halo.material.opacity=.13+.035*Math.sin(now*.003);
  se205.effectsFrames++;
 }
}
const se205PriorRay=se192RenderRay;
se192RenderRay=function(record,hit){
 const result=se205PriorRay(record,hit);
 if(!se195Active()||!record?.se192)return result;
 const side=record.input?.handedness|| (record.index===0?'left':'right');
 const baseColor=side==='left'?0x6ee7ff:0xffd180;
 const {beam,dot}=record.se192;
 if(se195.visible){
  // The UI has priority over the world behind it, and the rendered cursor
  // is raised just in front of the ACTUAL intersected button or backplate.
  const cursor=se205OverlayActive()?null:se195RadialHit(record);
  const cast=se192Ray(record);
  if(cursor?.point&&cast){
   dot.position.copy(cursor.point).addScaledVector(cast.direction,-.017);
   dot.visible=true;dot.scale.setScalar(.54);
   for(const ring of dot.children)ring.renderOrder=10510;
   beam.visible=true;beam.scale.z=Math.min(2.5,cursor.distance);
   beam.material.color.setHex(cursor.button?0x9affdf:baseColor);
   se205.rayHits++;se205.menuPointerFrames++;
  }else{
   dot.visible=false;beam.visible=true;beam.scale.z=.48;
   beam.material.color.setHex(baseColor);
   se205.rayMisses++;
  }
 }else{
  // Do NOT re-enable a beam the forward-placement adapter has hidden:
  // its world-space guide still owns the actual ground contact.
  beam.material.color.setHex(baseColor);
  for(const ring of dot.children)ring.renderOrder=10002;
 }
 return result;
};
const se205PriorFog=stSoftFogPaint;
stSoftFogPaint=function(s){
 if(se205OverlayActive()){se205.skippedFogPaints++;return;}
 return se205PriorFog(s);
};
const se205PriorTeamFog=se156PaintTeamFog;
se156PaintTeamFog=function(s,force=false){
 if(se205OverlayActive()){se205.skippedFogPaints++;return;}
 return se205PriorTeamFog(s,force);
};
const se205PriorCamera=se195FollowCamera;
se195FollowCamera=function(dt){
 if(se205OverlayActive()){se205.skippedCameraFrames++;return;}
 return se205PriorCamera(dt);
};
const se205PriorInput=se204InputFrame;
se204InputFrame=function(){
 const blurred=se205OverlayActive();
 if(blurred){
  se205.skippedInputFrames++;se205.overlayLatch=true;
  if(se204.wheel)se204WheelHide();
  for(const state of Object.values(se204.buttons)){
   state.held=false;state.opened=false;
  }
  return;
 }
 if(se205.overlayLatch){
  // A held controller button during a Quest overlay cannot become an
  // accidental build/skill activation when the headset returns to WebXR.
  const left=se192InputRecord('left'),right=se192InputRecord('right');
  if(se192Pressed(left,4)||se192Pressed(right,4)){
   se205.skippedInputFrames++;return;
  }
  se205.overlayLatch=false;
 }
 return se205PriorInput();
};
const se205PriorFrame=se193XRFrame;
se193XRFrame=function(){
 const blur=se205OverlayActive();
 if(blur){se205.overlayFrames++;if(!se205.overlayWas)se205.overlays++;}
 se205.overlayWas=blur;
 const result=se205PriorFrame();
 se205MenuHover();
 return result;
};
const se205PriorStart=se193XRStart;
se193XRStart=function(){
 se205.overlayWas=false;se205.overlayLatch=false;se205.focus=null;
 se205.hoverAt=0;se205ApplyCamera('tactical');
 return se205PriorStart();
};
const se205PriorCleanup=se193XRCleanup;
se193XRCleanup=function(){
 se205.focus=null;se205.root=null;se205.overlayWas=false;
 se205.overlayLatch=false;return se205PriorCleanup();
};
window.SWYRL_ENGINE_SHEEP_VR_POLISH_205=Object.freeze({
 diagnose:()=>({
  active:se195Active(),profile:se205.profile,
  tacticalAngle:Math.round(Math.atan2(se200.vertical*se193.zoom,
   se200.horizontal*se193.zoom+se202.rearBias)*180/Math.PI),
  selectedMenuButton:se205.focus?.userData?.se195Action||null,
  visibleMenu:!!se195.visible,menuPagesDecorated:se205.panelsDecorated,
  menuDecorReuses:se205.decorReuses,menuHoverChanges:se205.hoverChanges,
  menuRayHits:se205.rayHits,menuRayMisses:se205.rayMisses,
  menuParticleFrames:se205.effectsFrames,
  blurred:se205OverlayActive(),overlayTransitions:se205.overlays,
  overlayFrames:se205.overlayFrames,overlayInputSkipped:se205.skippedInputFrames,
  overlayCameraSkipped:se205.skippedCameraFrames,
  overlayFogSkipped:se205.skippedFogPaints
 }),
 setProfile:se205ApplyCamera
});
