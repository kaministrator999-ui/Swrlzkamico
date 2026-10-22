// Snap extensions to real deck edges; the new ramp's high end faces its parent.
function stWalkIsPiece(kind){return kind==='st-wall'||kind==='st-ramp';}
function stWalkSnap(kind,x,z,rotation=0){
 if(!stSession||!stWalkIsPiece(kind))return {x,z,rotation,join:null};
 let best=null;
 for(const b of stSession.buildings){
  if(b.hp<=0||!stWalkIsPiece(b.kind))continue;
  const fp=stBuildingObstacle(b),[lx,lz]=stLocalPoint(x,z,fp),inside=Math.abs(lx)<=fp.localHalfX+.15&&Math.abs(lz)<=fp.localHalfZ+.15,c=Math.cos(fp.rotation),s=Math.sin(fp.rotation);
  const ports=b.kind==='st-ramp'?[[0,-1,fp.localHalfZ]]:[[1,0,fp.localHalfX],[-1,0,fp.localHalfX],[0,1,fp.localHalfZ],[0,-1,fp.localHalfZ]];
  for(const [dx,dz,extent] of ports){
   const nx=dx*c+dz*s,nz=-dx*s+dz*c,ax=b.pos.x+nx*extent,az=b.pos.z+nz*extent,cx=ax+nx*3,cz=az+nz*3,distance=Math.hypot(x-cx,z-cz);
   const toward=lx*dx+lz*dz;
   if(distance>2.4&&!inside)continue;if(inside&&toward<-.15)continue;
   const score=distance+(inside&&toward<0?4:0);
   if(!best||score<best.score)best={x:cx,z:cz,rotation:Math.atan2(nx,nz),score,join:{sourceId:b.id,normal:[nx,nz],anchor:[ax,az],side:dx!==0}};
  }
 }
 return best||{x,z,rotation,join:null};
}
function stWalkUpperBuilder(unit){return !!unit?.archiveOnUpper&&!unit.captured&&!!stArchiveSurfaceAt(unit.pos,0);}
const stWalkCanBuildBase=stCanBuild;stCanBuild=function(kind,x,z,ownerId=null,rotation=0){
 const snap=stWalkSnap(stBuildKind(kind),x,z,rotation),fit=stWalkCanBuildBase(kind,snap.x,snap.z,ownerId,snap.rotation);
 fit.connection=snap.join;
 const unit=stSession?.units.find(u=>u.id===(ownerId||stSession.controlledId));
 if(stWalkIsPiece(stBuildKind(kind))&&stWalkUpperBuilder(unit)&&!snap.join)return {...fit,ok:false,reason:'Extend from the edge of a connected ramp or walkway.'};
 if(fit.ok&&snap.join)fit.warnings=[...(fit.warnings||[]),'Snapped '+(snap.join.side?'side turn':'straight extension')+' · '+Math.round(snap.rotation*180/Math.PI)+'°'];
 return fit;
};
const stWalkNewBuildingBase=stNewBuilding;stNewBuilding=function(kind,x,z,owner,authored=null,rotation=0){
 const snap=authored?null:stWalkSnap(kind,x,z,rotation),building=stWalkNewBuildingBase(kind,x,z,owner,authored,rotation);
 if(building&&snap?.join)building.walkJoin=snap.join;return building;
};
const stWalkIssueBuildBase=stIssueBuild;stIssueBuild=function(unit,kind,x,z,rotation=0){
 const fit=stCanBuild(kind,x,z,unit.id,rotation);if(!fit.ok)return fit;
 if(stWalkUpperBuilder(unit)&&stWalkIsPiece(kind)){
  const parent=stSession.buildings.find(b=>b.id===fit.connection?.sourceId),surface=parent&&stArchiveSurface(parent),center=surface?.point(0,0);
  if(!center||!stArchivePlanUpper(unit,center.x,center.z).ok||Math.hypot(unit.pos.x-fit.x,unit.pos.z-fit.z)>9)return stResult(false,'Move closer along the connected walkway before extending it.',fit);
  const building=stNewBuilding(fit.kind,fit.x,fit.z,unit.id,null,fit.rotation);if(!building)return stResult(false,'The extension became occupied.',fit);
  stSession.resources[unit.id]-=fit.cost;unit.archiveRoute=null;stSetOrder(unit,null);return stResult(true,'',{...fit,buildingId:building.id});
 }
 return stWalkIssueBuildBase(unit,fit.kind,fit.x,fit.z,fit.rotation);
};
// Add physical side-edge joints to the native routing graph, used by builders,
// rescue and attack approaches. Deck endpoints need not share a center line.
const stWalkGraphBase=stArchiveRouteGraph;stArchiveRouteGraph=function(s,radius){
 const graph=stWalkGraphBase(s,radius);
 for(const from of graph.surfaces)for(const to of graph.surfaces){if(from===to)continue;
  for(const id of from.nodeIds.slice(0,2)){
   const p=graph.nodes[id].point,local=p.clone().applyMatrix4(to.inverse);
   if(Math.abs(local.x)>1.215||Math.abs(local.z)>3.015)continue;
   const q=to.point(THREE.MathUtils.clamp(local.x,-1.2,1.2),THREE.MathUtils.clamp(local.z,-3,3));
   if(q.distanceTo(p)>.035)continue;
   const joint=graph.add(to,q);for(const other of to.nodeIds)graph.connect(joint,other);graph.connect(id,joint);
  }
 }
 return graph;
};
// Open a 2.4 m doorway in a side rail only after its extension is complete.
let stWalkJointKey='';
function stWalkRefreshJoints(){
 const s=stSession;if(!s)return;const key=s.navVersion+':'+s.buildings.filter(b=>b.hp>0&&b.progress>=1).length;if(key===stWalkJointKey)return;stWalkJointKey=key;
 for(const b of s.buildings){const rails=b.mesh?.getObjectByName('stWallRails');if(!rails)continue;
  for(const child of [...rails.children]){if(child.userData.walkJointClone){rails.remove(child);continue;}if(child.userData.walkJointVisible!==undefined)child.visible=child.userData.walkJointVisible;}
  const sides=new Set(s.buildings.filter(n=>n.hp>0&&n.progress>=1&&n.walkJoin?.sourceId===b.id&&n.walkJoin.side).map(n=>{const [nx,nz]=n.walkJoin.normal;return Math.sign(nx*Math.cos(b.rotation)-nz*Math.sin(b.rotation));}));
  for(const child of [...rails.children]){if(!sides.has(Math.sign(child.position.x)))continue;const depth=child.geometry?.parameters?.depth||0;
   if(depth>4){child.userData.walkJointVisible??=child.visible;child.visible=false;for(const sign of [-1,1]){const part=child.clone();part.visible=true;part.scale.z*=.3;part.position.z=sign*2.1;part.userData={walkJointClone:true};rails.add(part);}}
   else if(Math.abs(child.position.z)<1.2){child.userData.walkJointVisible??=child.visible;child.visible=false;}
  }
 }
}
const stWalkAfterBase=stArchiveAfterUpdate;stArchiveAfterUpdate=function(...args){const r=stWalkAfterBase(...args);stWalkRefreshJoints();return r;};
// Joystick movement follows the continuous surface directly. Small sweeps keep
// the full creature footprint supported by the union of adjoining decks.
function stWalkSupport(point,surfaces,referenceY,entry=false,tolerance=.22){
 let best=null;
 for(const surface of surfaces){const local=point.clone().applyMatrix4(surface.inverse),ramp=surface.building.kind==='st-ramp';
  if(Math.abs(local.x)>1.2001||Math.abs(local.z)>3.0001){
   if(!entry||!ramp||Math.abs(local.x)>1.21||local.z<3||local.z>3+stUnitRadius(stMobile.unit)+.25)continue;
   const ground=point.clone();ground.y=terrainHeight(point.x,point.z);if(Math.abs(ground.y-referenceY)>tolerance)continue;
   const hit={point:ground,surface,entry:true};if(!best)best=hit;continue;
  }
  const p=surface.point(local.x,local.z);if(Math.abs(p.y-referenceY)>tolerance)continue;
  if(!best||Math.abs(p.y-referenceY)<Math.abs(best.point.y-referenceY))best={point:p,surface,entry:false};
 }
 return best;
}
function stWalkStick(unit,dt){
 const s=stSession;if(!s?.rules.elevated||unit.captured||unit.archiveFalling||unit.kind==='wolf'&&!s.rules.wolvesUseRamps)return false;
 const radius=stUnitRadius(unit),surfaces=s.buildings.filter(b=>Math.hypot(b.pos.x-unit.pos.x,b.pos.z-unit.pos.z)<12).map(stArchiveSurface).filter(Boolean);
 if(!unit.archiveOnUpper&&!surfaces.some(a=>{if(a.building.kind!=='st-ramp')return false;const p=unit.pos.clone().applyMatrix4(a.inverse);return Math.abs(p.x)<1.2-radius+.02&&p.z>2.4&&p.z<3+radius+.35;}))return false;
 if(unit.order?.joystick||unit.archiveRoute){unit.archiveRoute=null;stSetOrder(unit,null);}
 let budget=unit.speed*(s.archive?.speedMultiplier?.(unit.kind)??1)*stMobile.strength*dt;
 const direction=new THREE.Vector3(stMobile.x,0,stMobile.y),context={rules:s.rules,obstacles:stObstacles()};
 while(budget>.00001){const step=Math.min(.06,budget);let chosen=null;
  for(const v of [direction,new THREE.Vector3(direction.x,0,0),new THREE.Vector3(0,0,direction.z)]){
   if(v.lengthSq()<.001)continue;const p=unit.pos.clone().addScaledVector(v,step),hit=stWalkSupport(p,surfaces,unit.pos.y,true);if(!hit)continue;
   if(hit.entry){if(stContextBlocked(context,p.x,p.z,radius,hit.surface.id))continue;}
   else if(hit.point.y-terrainHeight(p.x,p.z)>.2){
    let supported=true;for(let i=0;i<12;i++){const a=i*Math.PI/6,sample=hit.point.clone();sample.x+=Math.cos(a)*radius;sample.z+=Math.sin(a)*radius;
     if(!stWalkSupport(sample,surfaces,hit.point.y,true,Math.max(.22,radius*.6+.05))){supported=false;break;}}
    if(!supported)continue;
   }
   if(stLanesSegmentOccupant(unit,unit.pos,hit.point))continue;chosen=hit;break;
  }
  if(!chosen)break;const delta=chosen.point.clone().sub(unit.pos);unit.pos.copy(chosen.point);unit.actor.rotation.y=Math.atan2(delta.x,delta.z);
  unit.archiveOnUpper=!chosen.entry&&chosen.point.y-terrainHeight(unit.pos.x,unit.pos.z)>.015;unit.archiveHeight=unit.archiveOnUpper?chosen.point.y:null;budget-=step;
 }
 stSetOrder(unit,null);stPlaceUnit(unit);stLanesRemember(unit);return true;
}
const stWalkDriveBase=stMobileDrive;stMobileDrive=function(unit,dt,update){
 if(stMobile.unit===unit&&stMobile.pointer!==null&&stMobile.strength>0&&stMobileCanMove()&&stMobile.session===stSession&&unit.captured===stMobile.captured&&stWalkStick(unit,dt))return update(unit,dt);
 return stWalkDriveBase(unit,dt,update);
};
const stWalkHudBase=stRefreshHUD;stRefreshHUD=function(...args){const result=stWalkHudBase(...args);if(!stSession||!stUi.shown)return result;stUi.route='ground';for(const id of ['stUpperRoute','stExitWall']){const b=$(id);b.hidden=true;b.disabled=true;b.tabIndex=-1;}stUiBuildNames['st-wall']='Walkway';$('stBuildWall').querySelector('b').textContent='Walkway';return result;};
const stWalkDisposeBase=stDisposeUI;stDisposeUI=function(){stWalkJointKey='';return stWalkDisposeBase();};
const stWalkStatusBase=stUiStatus;stUiStatus=function(){return {...stWalkStatusBase(),walkways:{automaticJoystick:true,edgeSnapping:true,connection:stUi.placement?.connection||null}};};
