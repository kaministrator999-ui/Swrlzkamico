// §E v11.132 — rotate the permanent crossings as connected assemblies,
// treat elevated permanent walkways as actual overhead surfaces, and render
// an occluded sheep as wireframe through a house or walkway only when needed.
const ST132_ROUTE_HEADING=Object.freeze({pinewatch:0,moonflower:Math.PI/2,amberglade:-Math.PI/4});
function st132OrientWorldRoutes(){
 const project=typeof ST_CANONICAL_PROJECT==='undefined'?null:ST_CANONICAL_PROJECT;
 if(!project?.scene?.actors)return 0;
 let count=0;
 for(const [name,,cx,cz] of ST126_ROUTES){
  const angle=ST132_ROUTE_HEADING[name]||0;
  for(const [piece,dz,reverse] of [['south-ramp',6,false],['center-deck',0,false],['north-ramp',-6,true]]){
   const actor=project.scene.actors.find(a=>a.id==='st-permanent-route-'+name+'-'+piece);
   if(!actor)continue;
   const px=cx+Math.sin(angle)*dz,pz=cz+Math.cos(angle)*dz;
   actor.position=[px,0,pz];
   actor.rotation=[0,angle+(reverse?Math.PI:0),0];
   count++;
  }
 }
 return count;
}
st132OrientWorldRoutes();
const st132InstallWorldRoutesBase=st126InstallStarterRoutes;
st126InstallStarterRoutes=function(){
 const n=st132InstallWorldRoutesBase();st132OrientWorldRoutes();return n;
};
// A preconstructed raised walkway is 3.3m up. Its upper deck remains a
// full collision/navigation surface; on the *ground* it no longer behaves as
// a wall. Ramps remain blocked near ground because they slope downward.
// Player-built walls and normal houses still block as before.
function st132GroundUnderpass(building){
 return !!building&&st126PermanentRoute(building)&&building.kind==='st-wall'&&
   building.hp>0&&building.progress>=1;
}
const st132ObstaclesBase=stObstacles;
stObstacles=function(){
 const obstacles=st132ObstaclesBase();
 if(!stSession)return obstacles;
 const underpassIds=new Set(stSession.buildings.filter(st132GroundUnderpass).map(b=>b.id));
 return underpassIds.size?obstacles.filter(o=>!underpassIds.has(o.id)):obstacles;
};
// Source sheep remains unchanged; overlay is a shared-geometry wireframe
// rendering with depthTest disabled only when an authored house or elevated
// route lies between the camera and an already visible sheep.
const st132WireMaterial=new THREE.MeshBasicMaterial({
 color:0x7fffea,wireframe:true,transparent:true,opacity:.44,
 depthTest:false,depthWrite:false,side:THREE.DoubleSide
});
const st132Wireframes=new Map(),st132Raycaster=new THREE.Raycaster();
const st132RayOrigin=new THREE.Vector3(),st132RayTarget=new THREE.Vector3();
let st132NextOcclusionCheck=-Infinity;
function st132ClearWireframes(){
 for(const item of st132Wireframes.values())item.overlay.removeFromParent();
 st132Wireframes.clear();st132NextOcclusionCheck=-Infinity;
}
function st132WireFor(unit){
 const cached=st132Wireframes.get(unit.id);
 if(cached?.source===unit.actor)return cached;
 if(cached){cached.overlay.removeFromParent();st132Wireframes.delete(unit.id);}
 const overlay=unit.actor.clone(true);
 overlay.name='st132-wireframe-sheep-'+unit.id;
 overlay.traverse(node=>{
  if(node.isMesh){
   node.material=st132WireMaterial;node.castShadow=false;
   node.receiveShadow=false;node.renderOrder=1600;node.frustumCulled=false;
  }else if(node.isSprite||node.isLight){node.visible=false;}
 });
 overlay.visible=false;
 scene.add(overlay);
 const item={source:unit.actor,overlay};
 st132Wireframes.set(unit.id,item);
 return item;
}
function st132SyncWire(item){
 const sources=[],targets=[];
 item.source.traverse(node=>sources.push(node));
 item.overlay.traverse(node=>targets.push(node));
 for(let i=0;i<Math.min(sources.length,targets.length);i++){
  const from=sources[i],to=targets[i];
  to.position.copy(from.position);to.quaternion.copy(from.quaternion);to.scale.copy(from.scale);
  to.visible=from.visible;
 }
 item.overlay.visible=true;
}
function st132OccludedByStructure(unit){
 const camera=perspectiveCamera;
 if(!camera||!unit?.actor||!stSession)return false;
 camera.getWorldPosition(st132RayOrigin);
 unit.actor.getWorldPosition(st132RayTarget);
 st132RayTarget.y+=.55;
 const direction=st132RayTarget.clone().sub(st132RayOrigin),distance=direction.length();
 if(distance<.7)return false;
 st132Raycaster.set(st132RayOrigin,direction.multiplyScalar(1/distance));
 st132Raycaster.near=.15;st132Raycaster.far=distance-.2;
 for(const building of stSession.buildings){
  if(building.hp<=0||!building.mesh||!building.mesh.visible)continue;
  if(!ST_ARCHIVE_HOUSES.has(building.kind)&&!ST_ARCHIVE_DECKS.has(building.kind))continue;
  // Cheap XZ broadphase excludes distant geometry before 3D raycasts.
  const a=st132RayOrigin,c=st132RayTarget,b=building.pos;
  const dx=c.x-a.x,dz=c.z-a.z,denom=dx*dx+dz*dz||1;
  const t=Math.max(0,Math.min(1,((b.x-a.x)*dx+(b.z-a.z)*dz)/denom));
  if(Math.hypot(b.x-(a.x+dx*t),b.z-(a.z+dz*t))>5)continue;
  building.mesh.updateWorldMatrix(true,true);
  if(st132Raycaster.intersectObject(building.mesh,true).some(hit=>hit.distance<distance-.12))return true;
 }
 return false;
}
const st132AfterUpdateBase=stArchiveAfterUpdate;
stArchiveAfterUpdate=function(s,dt,t){
 const result=st132AfterUpdateBase(s,dt,t);
 if(!s||s.simulate||s.winner||s.role!=='sheep')return result;
 // Only player-visible sheep can reveal an outline. Fog-hidden opponents
 // never receive wireframe or new information.
 const seen=s.units.filter(u=>u.kind==='sheep'&&!u.captured&&!u.isIllusion&&stSeenByRole(u)).slice(0,12);
 const aliveIds=new Set(seen.map(u=>u.id));
 for(const [id,item] of st132Wireframes)if(!aliveIds.has(id)){item.overlay.removeFromParent();st132Wireframes.delete(id);}
 const check=s.elapsed>=st132NextOcclusionCheck;
 if(check)st132NextOcclusionCheck=s.elapsed+.17;
 for(const unit of seen){
  let item=st132Wireframes.get(unit.id);
  if(check){
   const hide=!st132OccludedByStructure(unit);
   if(hide){if(item)item.overlay.visible=false;continue;}
   item=st132WireFor(unit);
  }
  if(item?.overlay.visible){st132SyncWire(item);}
 }
 return result;
};
const st132StopRouteBase=stStop;
stStop=function(...args){
 st132ClearWireframes();
 return st132StopRouteBase(...args);
};
