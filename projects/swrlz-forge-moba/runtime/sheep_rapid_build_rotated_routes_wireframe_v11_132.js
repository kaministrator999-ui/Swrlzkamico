// §E v11.132 · Rapid placement, brief interruptible construction recovery,
// varied permanent raised crossing angles, ground passage beneath decks,
// and camera-aware sheep wireframe visibility.
let st132Rapid=false,st132LastWireCheck=-Infinity;
const st132Wire=new Map();
function st132SetRapid(enabled){
 st132Rapid=!!enabled;
 const btn=$('st132RapidBuild');
 if(btn){btn.setAttribute('aria-pressed',String(st132Rapid));btn.classList.toggle('active',st132Rapid);
  btn.setAttribute('aria-label',st132Rapid?'Rapid build ON: keep selected house tool':'Rapid build OFF: place one house at a time');
  const label=btn.querySelector('small');if(label)label.textContent=st132Rapid?'ON':'OFF';}
}
function st132InstallRapid(){
 if($('st132RapidBuild'))return;
 const panel=$('sheepTagHUD');if(!panel)return;
 const btn=document.createElement('button');
 btn.id='st132RapidBuild';btn.type='button';btn.className='st132-rapid';
 btn.innerHTML='<span aria-hidden="true">⌂⌂</span><b>RAPID</b><small>OFF</small>';
 btn.addEventListener('click',event=>{event.stopPropagation();st132SetRapid(!st132Rapid);
  stUiFeedback(st132Rapid?'Rapid building enabled. Drag repeatedly to place houses.':'Rapid building disabled.');});
 panel.appendChild(btn);st132SetRapid(st132Rapid);
}
const st132InstallBase=stInstallUI;
stInstallUI=function(){st132InstallBase();st132InstallRapid();};
const st132HudBase=stRefreshHUD;
stRefreshHUD=function(...args){
 const result=st132HudBase(...args),btn=$('st132RapidBuild');
 if(btn){const s=stSession,unit=s?.units?.find(u=>u.id===s.controlledId);
  btn.hidden=!s||!stUi.shown||s.simulate||s.winner||unit?.kind!=='sheep'||!!unit?.captured;
  btn.disabled=!!paused||!btn.hidden&&!!s?.winner;
  st132SetRapid(st132Rapid);}
 return result;
};
// Native building created after actual valid sheep action, not merely when
// selecting the skill or ordering a construction site.
const st132NewBuildingBase=stNewBuilding;
stNewBuilding=function(kind,x,z,owner,authored=null,rotation=0){
 const built=st132NewBuildingBase(kind,x,z,owner,authored,rotation);
 if(built&&!authored&&owner){
  const sheep=stSession?.units.find(u=>u.id===owner&&u.kind==='sheep');
  if(sheep&&!sheep.captured)sheep.st132RecoveryUntil=(stSession.elapsed||0)+.28;
 }
 return built;
};
// Preserve other frame processing (captures, animation, abilities); during
// recovery merely pause the automatic travel order. New movement bypasses it.
const st132UpdateSheepBase=stUpdateSheep;
stUpdateSheep=function(unit,dt){
 if(unit.st132RecoveryUntil>stSession?.elapsed &&
    !(stMobile?.pointer!==null&&stMobile?.unit===unit&&stMobile?.strength>0) &&
    !unit.order?.joystick&&unit.order?.action!=='move'){
  const hold=unit.order;unit.order=null;
  try{return st132UpdateSheepBase(unit,dt);}
  finally{if(unit.order===null)unit.order=hold;}
 }
 return st132UpdateSheepBase(unit,dt);
};
const st132SetOrderBase=stSetOrder;
stSetOrder=function(unit,order){
 if(order?.action==='move'||order?.joystick)unit.st132RecoveryUntil=0;
 return st132SetOrderBase(unit,order);
};
// Do NOT let elevated deck geometry block ground movement. Native upper
// navigation still follows raised surfaces via stArchiveSurface/route graph;
// ramps still occupy ground and must be approached at their low ends.
const st132ObstacleBase=stObstacles;
stObstacles=function(){
 return st132ObstacleBase().filter(o=>o.kind!=='st-wall');
};
// Prebuilt Moonbell crossings were all rotated 0 degrees. Retain their
// original permanent IDs, but lay out each local axis at a different angle.
// Two actual ramp upper ends touch the two six-metre deck endpoints.
function st132RotateCanonicalCrossings(){
 const sceneProject=typeof ST_CANONICAL_PROJECT!=='undefined'?ST_CANONICAL_PROJECT:null;
 const actors=sceneProject?.scene?.actors;if(!actors)return 0;
 const axes={pinewatch:0,moonflower:Math.PI/2,amberglade:-Math.PI/2};
 const centers={pinewatch:[-52.5,-45],moonflower:[60,-52.5],amberglade:[-52.5,60]};
 let changed=0;
 for(const [name,rotation] of Object.entries(axes)){
  const [x,z]=centers[name],dx=6*Math.sin(rotation),dz=6*Math.cos(rotation);
  for(const [piece,ox,oz,angle] of [
    ['south-ramp',dx,dz,rotation],
    ['center-deck',0,0,rotation],
    ['north-ramp',-dx,-dz,rotation+Math.PI]]){
   const actor=actors.find(a=>a.id==='st-permanent-route-'+name+'-'+piece);
   if(!actor)continue;
   actor.position=[x+ox,0,z+oz];actor.rotation=[0,angle,0];
   changed++;
  }
 }
 return changed;
}
st132RotateCanonicalCrossings();
const st132StarterBase=stLoadStarter;
stLoadStarter=function(){const result=st132StarterBase();st132RotateCanonicalCrossings();return result;};
// A top-depth-disabled wireframe copy of the real animated sheep. Clone on
// demand and share existing organic mesh GEOMETRIES; only materials are new.
const st132WireMaterial=new THREE.MeshBasicMaterial({
 color:'#74faff',wireframe:true,transparent:true,opacity:.9,
 depthTest:false,depthWrite:false,side:THREE.DoubleSide
});
const st132Ray=new THREE.Ray(),st132Box=new THREE.Box3();
const st132Eye=new THREE.Vector3(),st132Target=new THREE.Vector3(),st132Dir=new THREE.Vector3(),st132Hit=new THREE.Vector3();
function st132EnsureWire(unit){
 if(st132Wire.has(unit.id))return st132Wire.get(unit.id);
 const overlay=new THREE.Group();overlay.name='st132OccludedSheepWireframe';
 const pairs=[];
 for(const original of unit.actor.children){
  if(original===overlay||original.name==='st132OccludedSheepWireframe')continue;
  const copy=original.clone(true);
  const recurse=(a,b)=>{
   pairs.push([a,b]);
   if(b.isMesh){b.material=st132WireMaterial;b.castShadow=false;b.receiveShadow=false;b.renderOrder=9999;}
   for(let i=0;i<a.children.length;i++)if(b.children[i])recurse(a.children[i],b.children[i]);
  };
  recurse(original,copy);overlay.add(copy);
 }
 overlay.visible=false;overlay.renderOrder=9999;unit.actor.add(overlay);
 const entry={actor:unit.actor,overlay,pairs};st132Wire.set(unit.id,entry);return entry;
}
function st132GroundUnderDeck(unit,s){
 if(unit.archiveOnUpper)return false;
 return s.buildings.some(b=>b.kind==='st-wall'&&b.hp>0&&b.progress>=1&&
  stIntersectsObstacle(unit.pos.x,unit.pos.z,0,stBuildingObstacle(b)) &&
  unit.pos.y<terrainHeight(unit.pos.x,unit.pos.z)+1.5);
}
function st132CameraBlocked(unit,s){
 const cam=typeof perspectiveCamera!=='undefined'?perspectiveCamera:camera;
 cam.getWorldPosition(st132Eye);
 unit.actor.getWorldPosition(st132Target);st132Target.y+=.6;
 st132Dir.subVectors(st132Target,st132Eye);
 const distance=st132Dir.length();if(distance<.4)return false;
 st132Ray.set(st132Eye,st132Dir.normalize());
 for(const b of s.buildings){
  if(b.hp<=0||b.progress<.12||!b.mesh?.visible)continue;
  st132Box.setFromObject(b.mesh);
  if(st132Ray.intersectBox(st132Box,st132Hit)&&st132Hit.distanceTo(st132Eye)<distance-.28)return true;
 }
 return false;
}
const st132AfterBase=stArchiveAfterUpdate;
stArchiveAfterUpdate=function(s,dt,t){
 const result=st132AfterBase(s,dt,t);
 if(!s||!stUi.shown)return result;
 // Throttle occlusion detection, but synchronize actual limb/head pose every
 // frame on visible overlays, including the Clover organic animated model.
 if(s.elapsed-st132LastWireCheck>.12){
  st132LastWireCheck=s.elapsed;
  const alive=new Set();
  for(const unit of s.units){
   if(unit.kind!=='sheep'||unit.captured||unit.isIllusion)continue;
   alive.add(unit.id);
   const occluded=st132GroundUnderDeck(unit,s)||st132CameraBlocked(unit,s);
   if(occluded)st132EnsureWire(unit).overlay.visible=true;
   else if(st132Wire.has(unit.id))st132Wire.get(unit.id).overlay.visible=false;
  }
  for(const [id,entry] of st132Wire)if(!alive.has(id)||!entry.actor.parent){entry.actor.remove(entry.overlay);st132Wire.delete(id);}
 }
 for(const entry of st132Wire){} // intentionally no gameplay mutation
 for(const {overlay,pairs} of st132Wire.values())if(overlay.visible)
  for(const [from,to] of pairs){
   to.visible=from.visible;to.position.copy(from.position);
   to.quaternion.copy(from.quaternion);to.scale.copy(from.scale);
  }
 return result;
};
const st132DisposeBase=stDisposeUI;
stDisposeUI=function(){
 for(const {actor,overlay} of st132Wire.values())actor.remove(overlay);
 st132Wire.clear();st132LastWireCheck=-Infinity;st132SetRapid(false);
 return st132DisposeBase();
};
const st132StatusBase=stUiStatus;
stUiStatus=function(){const base=st132StatusBase();return {...base,
 rapidBuild:{enabled:st132Rapid},occludedSheep:[...st132Wire.keys()]};};
