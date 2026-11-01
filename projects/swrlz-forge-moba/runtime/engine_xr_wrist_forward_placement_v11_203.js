// §E v11.203 — Quest Sheep Tag: near-center forward view, reachable ground
// placement, and cached wrist/capture menu pages. No new frame/render loop.
// Source-of-truth: native stCanBuild still validates EVERY final site.
const se203={
 vertical:6.5,menuTextures:new Map(),menuPages:new Map(),
 activePage:null,textureCreates:0,menuBuilds:0,menuReuses:0,
 menuDisposals:0,menuBuildMs:0,menuLastBuildMs:0,
 aimSamples:0,forwardSamples:0,physicalSamples:0,
 skippedSparks:0,handEffectsMuted:false,releaseCount:0
};
// An elevated free-look eye cannot place the sheep near eye-level at neutral
// headset orientation. Keep the v11.202 rearward distance and lower ONLY the
// vertical offset. At default zoom the eye is ~9.1 world units above the
// sheep and ~31.9 back: about 16 degrees down rather than ~49 degrees.
// The HMD's native pose/rotation remains untouched, including while moving.
se200.vertical=se203.vertical;
se202.vertical=se203.vertical;
// Visible game has two independent input spaces: a physical ground ray for
// steep down-aim and a forward-facing, sheep-centered aim plane for typical
// neutral hand/head posture. Neither modifies VR camera tracking or physics.
const se203PhysicalGround=se193XRGameGround;
function se203GroundFromForwardRay(record){
 const s=stSession,unit=s?.units?.find(u=>u.id===s.controlledId);
 if(!unit?.pos)return null;
 const cast=se192Ray(record),pose=se191XRHeadPose();
 if(!cast?.origin||!cast?.direction||!pose?.eye)return null;
 const heading=se193.angle||0,forward=new THREE.Vector3(
  Math.sin(heading),0,Math.cos(heading));
 const dot=cast.direction.dot(forward);
 if(dot<.26)return null; // looking away/down: ordinary ray wins
 const centerDistance=4;
 const base=unit.pos.clone().addScaledVector(forward,centerDistance);
 const t=((base.x-cast.origin.x)*forward.x+
          (base.z-cast.origin.z)*forward.z)/dot;
 if(!Number.isFinite(t)||t<.2||t>120)return null;
 const p=cast.origin.clone().addScaledVector(cast.direction,t);
 const sideX=forward.z,sideZ=-forward.x;
 const lateral=(p.x-base.x)*sideX+(p.z-base.z)*sideZ;
 // Higher aim => farther ahead; lower aim => closer. Typical Quest forward
 // controller posture maps around the actual sheep rather than the horizon.
 const depth=THREE.MathUtils.clamp(
  centerDistance+(p.y-pose.eye.y)*.56,-5.5,11);
 const x=unit.pos.x+forward.x*depth+sideX*THREE.MathUtils.clamp(lateral,-10,10);
 const z=unit.pos.z+forward.z*depth+sideZ*THREE.MathUtils.clamp(lateral,-10,10);
 if(!Number.isFinite(x)||!Number.isFinite(z))return null;
 return new THREE.Vector3(x,terrainHeight(x,z),z);
}
se193XRGameGround=function(record){
 if(!se200Active()||!stUi.build||se195.visible||se195.photo)
  return se203PhysicalGround(record);
 se203.aimSamples++;
 const cast=se192Ray(record);
 // A steep downward aim remains a literal ground ray. This also protects
 // users who intentionally point at a particular distant ground feature.
 if(cast?.direction?.y<-.65){
  se203.physicalSamples++;return se203PhysicalGround(record);
 }
 const aimed=se203GroundFromForwardRay(record);
 if(aimed){se203.forwardSamples++;return aimed;}
 se203.physicalSamples++;
 return se203PhysicalGround(record);
};
// Cache small, readable menu label textures for the entire VR session,
// instead of recreating 512x256 canvases and uploading many new GPU textures
// every time the player opens BUILD/CAPTURE/SESSION/BACK.
se195Text=function(label,header=false){
 const key=(header?'h:':'b:')+label;
 const existing=se203.menuTextures.get(key);
 if(existing)return existing;
 const c=document.createElement('canvas');c.width=256;c.height=128;
 const g=c.getContext('2d');if(!g)return null;
 // Half-resolution backing while preserving the original visual coordinates.
 g.scale(.5,.5);
 g.clearRect(0,0,512,256);
 const grad=g.createLinearGradient(0,0,512,256);
 grad.addColorStop(0,header?'#27445d':'#133346');
 grad.addColorStop(1,header?'#17253d':'#15243a');
 g.fillStyle=grad;g.beginPath();g.roundRect(9,9,494,238,38);g.fill();
 g.lineWidth=12;g.strokeStyle=header?'#88f1ef':'#578d9e';g.stroke();
 g.textAlign='center';g.textBaseline='middle';
 g.font=header?'bold 48px sans-serif':'bold 51px sans-serif';
 g.fillStyle='#eafcff';g.fillText(label,256,132,450);
 const tex=new THREE.CanvasTexture(c);
 tex.colorSpace=THREE.SRGBColorSpace;
 se203.menuTextures.set(key,tex);
 se203.textureCreates++;
 // Do not push into se195.textures: that array gets disposed on every page.
 // Dispose the cached textures once, on actual immersive session cleanup.
 return tex;
};
function se203DisposeCached(root){
 if(!root)return;
 scene.remove(root);
 root.traverse(o=>{
  o.geometry?.dispose?.();
  if(Array.isArray(o.material))o.material.forEach(m=>m?.dispose?.());
  else o.material?.dispose?.();
 });
 se203.menuDisposals++;
}
const se203OriginalMakeRadial=se195MakeRadial;
se195MakeRadial=function(reposition=true){
 const key=se195.mode+'|'+se195.page;
 const old=se195.radial,oldKey=se203.activePage;
 const oldPos=old?.position?.clone(),oldQuaternion=old?.quaternion?.clone();
 if(old&&oldKey===key){
  old.visible=se195.visible;
  if(reposition)se195PositionRadial(true);
  return;
 }
 if(old&&oldKey){
  scene.remove(old);
  se203.menuPages.set(oldKey,{root:old,buttons:se195.buttons.slice()});
  se195.radial=null;se195.buttons=[];se195.hover=null;
 }
 const cached=se203.menuPages.get(key),start=performance.now();
 if(cached){
  se195.radial=cached.root;se195.buttons=cached.buttons.slice();
  se195.hover=null;cached.root.visible=se195.visible;
  scene.add(cached.root);
  if(reposition)se195PositionRadial(true);
  else if(oldPos){
   cached.root.position.copy(oldPos);
   cached.root.quaternion.copy(oldQuaternion);
  }
  se203.menuReuses++;
 }else{
  se203OriginalMakeRadial(reposition);
  if(!reposition&&oldPos&&se195.radial){
   se195.radial.position.copy(oldPos);
   se195.radial.quaternion.copy(oldQuaternion);
  }
  se203.menuBuilds++;
 }
 se203.activePage=key;
 const elapsed=performance.now()-start;
 se203.menuLastBuildMs=elapsed;se203.menuBuildMs+=elapsed;
};
function se203HandEffects(){
 const muted=!!se195.visible;
 if(se203.handEffectsMuted===muted)return;
 se203.handEffectsMuted=muted;
 for(const record of se181XR.controllers){
  const hand=record?.se195;if(!hand)continue;
  if(hand.halo)hand.halo.visible=!muted;
  if(hand.points)hand.points.visible=!muted;
 }
}
const se203OriginalSetVisible=se195SetVisible;
se195SetVisible=function(value){
 const result=se203OriginalSetVisible(value);
 se203HandEffects();
 return result;
};
const se203OriginalHand=se195UpdateHand;
se195UpdateHand=function(record,t,dist){
 if(se195.visible){se203.skippedSparks++;return;}
 return se203OriginalHand(record,t,dist);
};
const se203OriginalAcquireHand=se195AcquireHand;
se195AcquireHand=function(record){
 const result=se203OriginalAcquireHand(record);
 if(se195.visible&&record?.se195){
  record.se195.halo.visible=false;record.se195.points.visible=false;
 }
 return result;
};
const se203OriginalCleanup=se193XRCleanup;
se193XRCleanup=function(){
 // The previous cleanup owns the active page; cached pages are detached.
 const current=se195.radial;
 const result=se203OriginalCleanup();
 for(const entry of se203.menuPages.values()){
  if(entry.root!==current)se203DisposeCached(entry.root);
 }
 se203.menuPages.clear();
 for(const tex of se203.menuTextures.values())tex.dispose();
 se203.menuTextures.clear();
 se203.activePage=null;se203.handEffectsMuted=false;
 se203.releaseCount++;
 return result;
};
window.SWYRL_ENGINE_QUEST_SHEEP_AIM_203=Object.freeze({
 diagnose:()=>({
  active:se200Active(),cameraAbove:se200.vertical*se193.zoom,
  cameraBehind:se200.horizontal*se193.zoom+se202.rearBias,
  neutralDownAngleDeg:Math.round(Math.atan2(se200.vertical*se193.zoom,
   se200.horizontal*se193.zoom+se202.rearBias)*180/Math.PI),
  forwardAimSamples:se203.forwardSamples,physicalAimSamples:se203.physicalSamples,
  menuPagesBuilt:se203.menuBuilds,menuPageReuses:se203.menuReuses,
  menuTextures:se203.menuTextures.size,
  menuTextureUploads:se203.textureCreates,
  menuPageBuildMs:Math.round(se203.menuLastBuildMs*100)/100,
  menuResourcesDisposed:se203.menuDisposals,
  handSparksSkipped:se203.skippedSparks,
  estimatedXrFps:se195.fps
 })
});
