// Physical traffic and construction share native match state. No second clock,
// saved helper actors, or editor transforms are used for gameplay displacement.
const ST_LANE_HOUSES = new Set(['st-farm','st-income','st-fort','st-totem']);
const ST_LANE_GAP = .6;
const stLanesCleanRulesBase = stCleanRules;
stCleanRules = function(value={}) {
  const rules = stLanesCleanRulesBase(value);
  if (Math.abs(rules.wolfRadius-.68)<1e-6) rules.wolfRadius=.78;
  return rules;
};
const stLanesVisualBase = stMakeVisual;
stMakeVisual = function(type) {
  const visual = stLanesVisualBase(type);
  if (type==='st-wolf') for (const child of visual.children) {
    child.position.multiplyScalar(.78/.68); child.scale.multiplyScalar(.78/.68);
  }
  return visual;
};

function stLanesSnapHouse(kind,x,z,snap=.15) {
  const point={x:Math.round(Number(x)/snap)*snap,z:Math.round(Number(z)/snap)*snap};
  const s=stSession;
  if (!s||!ST_LANE_HOUSES.has(kind)||![point.x,point.z].every(Number.isFinite)) return point;
  // Nearby edges have two intentional positions: touching or a .6-unit lane.
  // Never magnetize a tap deep inside an already occupied house footprint.
  for (const axis of ['x','z']) {
    const other=axis==='x'?'z':'x',half=axis==='x'?'halfX':'halfZ',cross=axis==='x'?'halfZ':'halfX';
    let best=null;
    for (const b of s.buildings) {
      if (b.hp<=0||!ST_LANE_HOUSES.has(b.kind)) continue;
      const d=point[axis]-b.pos[axis],extent=1.2+b[half];
      if (Math.abs(point[other]-b.pos[other])>=1.2+b[cross]-.02||Math.abs(d)<extent-.32||Math.abs(d)>extent+.91) continue;
      for (const gap of [0,ST_LANE_GAP]) {
        const value=b.pos[axis]+Math.sign(d||1)*(extent+gap),delta=Math.abs(value-point[axis]);
        if (delta<=.32&&(!best||delta<best.delta)) best={value,delta};
      }
    }
    if (best) point[axis]=best.value;
  }
  return point;
}

function stLanesPhysical(unit) {return !unit.captured&&!unit.isIllusion&&!unit.archiveFalling;}
function stLanesSameLevel(unit,other,y=unit.pos.y) {return Math.abs(y-other.pos.y)<1.2;}
function stLanesOccupant(unit,x,z,y=unit.pos.y) {
  const s=stSession,r=stUnitRadius(unit);
  return s?.units.find(other=>other!==unit&&stLanesPhysical(other)&&stLanesSameLevel(unit,other,y)&&
    Math.hypot(x-other.pos.x,z-other.pos.z)<r+stUnitRadius(other)+.015-1e-6)||null;
}
function stLanesSegmentOccupant(unit,a,b) {
  const r=stUnitRadius(unit),dx=b.x-a.x,dz=b.z-a.z,den=dx*dx+dz*dz;
  for (const other of stSession.units) {
    if (other===unit||!stLanesPhysical(other)) continue;
    const t=den?THREE.MathUtils.clamp(((other.pos.x-a.x)*dx+(other.pos.z-a.z)*dz)/den,0,1):0;
    const y=a.y+(b.y-a.y)*t;
    if (stLanesSameLevel(unit,other,y)&&Math.hypot(a.x+dx*t-other.pos.x,a.z+dz*t-other.pos.z)<r+stUnitRadius(other)+.015-1e-6) return other;
  }
  return null;
}
function stLanesEjection(unit,footprint) {
  const radius=stUnitRadius(unit),[lx,lz]=stLocalPoint(unit.pos.x,unit.pos.z,footprint);
  const hx=footprint.localHalfX??footprint.halfX,hz=footprint.localHalfZ??footprint.halfZ;
  const c=Math.cos(footprint.rotation||0),sn=Math.sin(footprint.rotation||0),points=[];
  const world=(x,z)=>new THREE.Vector3(footprint.x+x*c+z*sn,unit.pos.y,footprint.z-x*sn+z*c);
  const tx=THREE.MathUtils.clamp(lx,-hx,hx),tz=THREE.MathUtils.clamp(lz,-hz,hz);
  for (const side of [-1,1]) {
    points.push(world(side*(hx+radius+.025),tz),world(tx,side*(hz+radius+.025)));
    // If a neighbour occupies the nearest projection, slide along that side.
    for (let offset=.15;offset<=Math.max(hx,hz)*2+.01;offset+=.15) for (const sign of [-1,1]) {
      if (Math.abs(tz+offset*sign)<=hz) points.push(world(side*(hx+radius+.025),tz+offset*sign));
      if (Math.abs(tx+offset*sign)<=hx) points.push(world(tx+offset*sign,side*(hz+radius+.025)));
    }
  }
  points.sort((a,b)=>a.distanceToSquared(unit.pos)-b.distanceToSquared(unit.pos));
  const context={rules:stSession.rules,obstacles:stObstacles()};
  return points.find(p=>!stIntersectsObstacle(p.x,p.z,radius,footprint)&&!stBlocked(p.x,p.z,radius)&&
    !stLanesOccupant(unit,p.x,p.z)&&stSegmentClear(context,unit.pos,p,radius)&&!stLanesSegmentOccupant(unit,unit.pos,p))||null;
}
const stLanesCanBuildBase = stCanBuild;
stCanBuild = function(kind,x,z,ownerId=null,rotation=0) {
  const fit=stLanesCanBuildBase(kind,x,z,ownerId,rotation);
  if (!fit.ok) return fit;
  const owner=stSession.units.find(u=>u.id===(ownerId||stSession.controlledId));
  const overlaps=stIntersectsObstacle(owner.pos.x,owner.pos.z,stUnitRadius(owner),fit);
  if (overlaps) {
    const exit=stLanesEjection(owner,fit);
    if (!exit) return stResult(false,'No clear side can safely move your sheep out of this structure.',fit);
    fit.builderExit=exit.toArray();
  }
  fit.warnings=(fit.warnings||[]).filter(text=>!text.startsWith('A gap here is too tight'));
  return fit;
};
const stLanesNewBuildingBase = stNewBuilding;
stNewBuilding = function(kind,x,z,owner,authored=null,rotation=0) {
  const unit=stSession.units.find(u=>u.id===owner),fp=stFootprint(x,z,1.2,ST_BUILDINGS[kind]?.length?3:1.2,rotation);
  const needsExit=!authored&&unit&&!unit.captured&&
    stIntersectsObstacle(unit.pos.x,unit.pos.z,stUnitRadius(unit),fp);
  const exit=needsExit?stLanesEjection(unit,fp):null;
  if (needsExit&&!exit) return null;
  const building=stLanesNewBuildingBase(kind,x,z,owner,authored,rotation);
  if (exit) {
    unit.pos.copy(exit);stPlaceUnit(unit);unit.path=[];unit.pathVersion=-1;
    unit.traffic=null;stLanesRemember(unit,true);
    stSession.lastBuilderExit={unitId:unit.id,buildingId:building.id,pos:exit.toArray()};
  }
  return building;
};
const stLanesIssueBuildBase = stIssueBuild;
stIssueBuild = function(unit,kind,x,z,rotation=0) {
  const fit=stCanBuild(kind,x,z,unit.id,rotation);
  if (!fit.ok) return fit;
  if (fit.builderExit) {
    const building=stNewBuilding(fit.kind,fit.x,fit.z,unit.id,null,fit.rotation);
    if (!building) return stResult(false,'The clear building side became occupied.',fit);
    stSession.resources[unit.id]-=fit.cost;unit.archiveRoute=null;stSetOrder(unit,null);
    stSession.message=unit.name+' is building a '+ST_BUILDINGS[fit.kind].name+'.';
    return stResult(true,'',{...fit,buildingId:building.id});
  }
  return stLanesIssueBuildBase(unit,fit.kind,fit.x,fit.z,fit.rotation);
};

function stLanesRemember(unit,reset=false) {
  if (reset||!unit.traffic) unit.traffic={trail:[unit.pos.clone()],blockedBy:null,mode:'moving',yieldTarget:null,retryAt:0};
  const t=unit.traffic,last=t.trail.at(-1);
  if (last.distanceToSquared(unit.pos)>.0225) t.trail.push(unit.pos.clone());
  if (t.trail.length>100) t.trail.shift();
  return t;
}
function stLanesDynamicPath(unit,target) {
  const radius=stUnitRadius(unit),base=stNavigation(radius),others=stSession.units.filter(other=>other!==unit&&stLanesPhysical(other)&&stLanesSameLevel(unit,other));
  const bodies=others.map(other=>({id:other.id,x:other.pos.x,z:other.pos.z,radius:stUnitRadius(other)+.02}));
  const context={rules:stSession.rules,obstacles:[...stObstacles(),...bodies]};
  const nav={...base,context,blocked:base.blocked.slice(),components:new Int32Array(base.count),componentSerial:0};
  for (const body of bodies) {
    const extent=body.radius+radius,minX=Math.max(-nav.extent,Math.floor((body.x-extent)/ST_GRID)),maxX=Math.min(nav.extent,Math.ceil((body.x+extent)/ST_GRID));
    const minZ=Math.max(-nav.extent,Math.floor((body.z-extent)/ST_GRID)),maxZ=Math.min(nav.extent,Math.ceil((body.z+extent)/ST_GRID));
    for(let z=minZ;z<=maxZ;z++)for(let x=minX;x<=maxX;x++)if(stIntersectsObstacle(x*ST_GRID,z*ST_GRID,radius,body))nav.blocked[(z+nav.extent)*nav.width+x+nav.extent]=1;
  }
  return stFindPath(nav,unit.pos,target);
}
function stLanesYield(unit,blocker,target) {
  const t=stLanesRemember(unit),radius=stUnitRadius(unit);
  // The creature already ahead has priority; head-on ties are stable by ID.
  const mine=target.clone().sub(unit.pos),otherTarget=stOrderTarget(blocker),theirs=otherTarget?.clone().sub(blocker.pos);
  if (theirs&&mine.dot(theirs)<0&&String(unit.id)<String(blocker.id)&&blocker.order) return false;
  const context={rules:stSession.rules,obstacles:stObstacles()},candidates=[];
  for (let i=t.trail.length-1;i>=0;i--) {
    const p=t.trail[i],d=p.distanceTo(unit.pos);
    if (d<radius*2+.1||d>8||stLanesOccupant(unit,p.x,p.z)||!stSegmentClear(context,unit.pos,p,radius)) continue;
    const direction=p.clone().sub(unit.pos).normalize(),nx=-direction.z,nz=direction.x;
    const room=[-1,1].some(sign=>!stBlocked(p.x+nx*(radius*2+.1)*sign,p.z+nz*(radius*2+.1)*sign,radius));
    candidates.push({p:p.clone(),room,d});
  }
  // A new move can meet traffic before recording a trail. Step backwards on
  // clear ground; never push the other creature or tunnel through a building.
  const away=unit.pos.clone().sub(blocker.pos);away.y=0;if(away.lengthSq())away.normalize();
  for (const distance of [1.2,2.4,3.6]) {
    const p=unit.pos.clone().addScaledVector(away,distance);
    if (!stBlocked(p.x,p.z,radius)&&stSegmentClear(context,unit.pos,p,radius)&&!stLanesOccupant(unit,p.x,p.z)) candidates.push({p,room:false,d:distance});
  }
  candidates.sort((a,b)=>Number(b.room)-Number(a.room)||a.d-b.d);
  for (const candidate of candidates) {
    const route=stLanesDynamicPath(unit,candidate.p);
    if (route?.length) {t.yieldTarget=candidate.p;t.mode='backing out';unit.path=route;unit.pathTarget=candidate.p.clone();unit.repathAt=stSession.elapsed+.8;return true;}
  }
  return false;
}
stMoveUnit = function(unit,target,dt) {
  const s=stSession;if(!target||!stLanesPhysical(unit))return false;
  if (typeof stArchiveMoveUnit==='function') {const handled=stArchiveMoveUnit(unit,target,dt);if(handled!==null&&handled!==undefined)return handled;}
  const radius=stUnitRadius(unit),traffic=stLanesRemember(unit),context={rules:s.rules,obstacles:stObstacles()};
  if (traffic.yieldTarget&&Math.hypot(unit.pos.x-traffic.yieldTarget.x,unit.pos.z-traffic.yieldTarget.z)<.12) {
    traffic.yieldTarget=null;traffic.mode='waiting';traffic.retryAt=s.elapsed+.6;unit.path=[];unit.pathVersion=-1;
  }
  if (s.elapsed<traffic.retryAt) return false;
  const aim=traffic.yieldTarget||target,movedTarget=!unit.pathTarget||unit.pathTarget.distanceToSquared(aim)>.45;
  if(unit.pathVersion!==s.navVersion||movedTarget||s.elapsed>=unit.repathAt) {
    unit.path=(traffic.mode==='alternate lane'?stLanesDynamicPath(unit,aim):stPath(unit.pos,aim,radius))||[];
    unit.pathVersion=s.navVersion;unit.pathTarget=aim.clone();unit.repathAt=s.elapsed+.9;
  }
  let budget=unit.speed*(s.archive?.speedMultiplier?.(unit.kind)??1)*dt,moved=false;
  while(unit.path.length&&budget>0) {
    const next=unit.path[0],dx=next.x-unit.pos.x,dz=next.z-unit.pos.z,d=Math.hypot(dx,dz);
    if(d<.015){unit.path.shift();continue;}
    const step=Math.min(budget,d,.09),candidate=new THREE.Vector3(unit.pos.x+dx/d*step,unit.pos.y,unit.pos.z+dz/d*step);
    if(!stSegmentClear(context,unit.pos,candidate,radius)){unit.path=[];unit.repathAt=0;break;}
    const blocker=stLanesSegmentOccupant(unit,unit.pos,candidate);
    if(blocker) {
      traffic.blockedBy=blocker.id;traffic.mode='waiting';
      if(s.elapsed>=traffic.retryAt) {
        const route=stLanesDynamicPath(unit,aim);
        if(route?.length){unit.path=route;traffic.mode='alternate lane';unit.repathAt=s.elapsed+1.2;}
        else if(blocker.kind===unit.kind)stLanesYield(unit,blocker,target);
        traffic.retryAt=s.elapsed+.3;
      }
      break;
    }
    unit.pos.copy(candidate);unit.actor.rotation.y=Math.atan2(dx,dz);budget-=step;moved=true;
    traffic.blockedBy=null;if(!traffic.yieldTarget&&traffic.mode!=='alternate lane')traffic.mode='moving';
    stLanesRemember(unit);
    if(step>=d-1e-6)unit.path.shift();
  }
  stPlaceUnit(unit);return moved;
};

// Raised routes use the same swept-body test at the actual interpolated height.
// A creature below a bridge does not block one walking on its deck.
stArchiveAdvance = function(unit,points,dt,upper) {
  const s=stSession,radius=stArchiveRadius(unit);let budget=unit.speed*s.archive.speedMultiplier(unit.kind)*dt,moved=false;
  while(points.length&&budget>0) {
    const waypoint=points[0],next=upper?waypoint.point:waypoint,delta=next.clone().sub(unit.pos);if(!upper)delta.y=0;const distance=delta.length();
    if(distance<.015){points.shift();if(upper&&waypoint.exit){unit.archiveOnUpper=false;unit.archiveHeight=null;}continue;}
    const step=Math.min(budget,distance,.09),candidate=unit.pos.clone().addScaledVector(delta,step/distance);
    const groundBlocked=!upper&&stBlocked(candidate.x,candidate.z,radius),entryBlocked=upper&&(waypoint.exit||candidate.y-terrainHeight(candidate.x,candidate.z)<.4)&&stBlocked(candidate.x,candidate.z,radius,waypoint.surfaceId);
    if(groundBlocked||entryBlocked){points.length=0;return moved;}
    const blocker=stLanesSegmentOccupant(unit,unit.pos,candidate);
    if(blocker){const traffic=stLanesRemember(unit);traffic.blockedBy=blocker.id;traffic.mode='waiting on raised route';break;}
    unit.pos.copy(candidate);unit.actor.rotation.y=Math.atan2(delta.x,delta.z);if(upper){unit.archiveHeight=candidate.y;unit.archiveOnUpper=!waypoint.exit||distance>step+.015;}
    budget-=step;moved=true;if(step>=distance-.00001){points.shift();if(upper&&waypoint.exit){unit.archiveOnUpper=false;unit.archiveHeight=null;}}
  }
  stPlaceUnit(unit);return moved;
};

function stLanesSheepApproach(wolf,sheep) {
  const radius=stUnitRadius(wolf),reach=radius+stUnitRadius(sheep)+.065;
  if (Math.abs(wolf.pos.y-sheep.pos.y)>=1.2) return null;
  const candidates=[sheep.pos.clone()];
  const angle=Math.atan2(wolf.pos.z-sheep.pos.z,wolf.pos.x-sheep.pos.x);
  for(let i=0;i<8;i++)candidates.push(new THREE.Vector3(sheep.pos.x+Math.cos(angle+i*Math.PI/4)*reach,sheep.pos.y,sheep.pos.z+Math.sin(angle+i*Math.PI/4)*reach));
  candidates.sort((a,b)=>a.distanceToSquared(wolf.pos)-b.distanceToSquared(wolf.pos));
  return candidates.find(p=>!stBlocked(p.x,p.z,radius)&&stPath(wolf.pos,p,radius))||null;
}
const stLanesOrderTargetBase = stOrderTarget;
stOrderTarget = function(unit) {
  if (unit.kind==='wolf'&&unit.order?.action==='attack'&&!unit.archiveOnUpper) {
    const sheep=stSession.units.find(u=>u.id===unit.order.id&&u.kind==='sheep'&&!u.captured);
    if (sheep&&stPerceives(unit,sheep)) {
      stRemember(unit,sheep);
      const cache=unit.sheepApproach;
      if(cache&&cache.id===sheep.id&&cache.version===stSession.navVersion&&cache.at>stSession.elapsed&&cache.target.distanceToSquared(sheep.pos)<.04)return cache.point.clone();
      const point=stLanesSheepApproach(unit,sheep);
      if(point){unit.sheepApproach={id:sheep.id,version:stSession.navVersion,at:stSession.elapsed+.3,target:sheep.pos.clone(),point:point.clone()};return point;}
    }
  }
  return stLanesOrderTargetBase(unit);
};
const stLanesBotWolfBase = stBotWolf;
stBotWolf = function(unit) {
  const s=stSession;if(s.elapsed<s.rules.headstart||unit.archiveRoute||s.elapsed<unit.botAt)return;
  stBotKnownEnemies(unit);
  const visible=s.units.filter(u=>u.kind==='sheep'&&!u.captured&&stPerceives(unit,u)).sort((a,b)=>a.pos.distanceToSquared(unit.pos)-b.pos.distanceToSquared(unit.pos));
  for(const sheep of visible) {
    const approach=stLanesSheepApproach(unit,sheep);
    const raised=s.rules.elevated&&s.rules.wolvesUseRamps&&
      (sheep.archiveOnUpper?stArchivePlanUpper(unit,sheep.pos.x,sheep.pos.z).ok:
       unit.archiveOnUpper&&stArchivePlanExit(unit,sheep.pos).ok);
    if(!approach&&!raised)continue;
    unit.botAt=s.elapsed+.5;unit.aiIntent='pursue a reachable sheep before buildings';
    if(unit.order?.action!=='attack'||unit.order.id!==sheep.id)stSetOrder(unit,{action:'attack',id:sheep.id});
    return;
  }
  stLanesBotWolfBase(unit);
};

const stLanesSetOrderBase = stSetOrder;
stSetOrder = function(unit,order) {
  if(order&&unit.order&&JSON.stringify(order)===JSON.stringify(unit.order))return;
  if (unit.traffic) {unit.traffic.yieldTarget=null;unit.traffic.retryAt=0;unit.traffic.blockedBy=null;unit.traffic.mode='moving';}
  return stLanesSetOrderBase(unit,order);
};
const stLanesRescueBase = stRescue;
stRescue = function(unit,rescuer) {
  // Choose a free rescue landing while the unit still exists as a wisp.
  if(!unit.captured)return false;
  const origin=unit.spirit.position.clone(),radius=stUnitRadius(unit),context={rules:stSession.rules,obstacles:stObstacles()},candidates=[];
  for(let ring=0;ring<=12;ring++)for(let i=0;i<(ring?16:1);i++) {
    const angle=i*Math.PI/8,p=origin.clone().add(new THREE.Vector3(Math.cos(angle)*ring*.3,0,Math.sin(angle)*ring*.3));
    if(!stBlocked(p.x,p.z,radius)&&!stLanesOccupant(unit,p.x,p.z,terrainHeight(p.x,p.z))&&stSegmentClear(context,origin,p,radius))candidates.push(p);
  }
  if(!candidates.length)return false;
  const result=stLanesRescueBase(unit,rescuer);
  if(result){unit.pos.copy(candidates[0]);stPlaceUnit(unit);stLanesRemember(unit,true);}
  return result;
};

const stLanesPreflightBase = stAuthoredMapPreflight;
stAuthoredMapPreflight = function(payload={}) {
  const result=stLanesPreflightBase(payload),rules=payload.rules||stRules();
  const units=(payload.pieces||[]).filter(p=>p.active!==false&&['st-sheep','st-wolf'].includes(p.type));
  for(let i=0;i<units.length;i++)for(let j=i+1;j<units.length;j++) {
    const a=units[i],b=units[j],species=a.type==='st-wolf'?'wolf':'sheep';
    if(a.type===b.type&&Math.abs(a.position[1]-b.position[1])<1.2&&Math.hypot(a.position[0]-b.position[0],a.position[2]-b.position[2])<stUnitRadius(species,rules)*2+.015-1e-6)
      result.errors.push('Move overlapping '+species+' spawns apart before Play.');
  }
  result.ok=!result.errors.length;result.reason=result.errors[0]||'';return result;
};

const stLanesViewBase = stViewStatus;
stViewStatus = function() {
  const result=stLanesViewBase();if(!stSession||stSession.simulate)return result;
  if(result.houseLanes?.lastBuilderExit&&!result.units.some(u=>u.id===result.houseLanes.lastBuilderExit.unitId))result.houseLanes.lastBuilderExit=null;
  for(const unit of result.units)if(unit.kind!==stSession.role){delete unit.traffic;}
  return result;
};
const stLanesStatusBase = stStatus;
stStatus = function() {
  const result=stLanesStatusBase();if(!stSession)return result;
  result.houseLanes={gap:ST_LANE_GAP,houseSize:2.4,wolfRadius:stUnitRadius('wolf'),sheepRadius:stUnitRadius('sheep'),lastBuilderExit:stSession.lastBuilderExit||null};
  for(const record of result.units) {
    const unit=stSession.units.find(u=>u.id===record.id);
    record.radius=stUnitRadius(unit);record.traffic=unit.traffic?{mode:unit.traffic.mode,blockedBy:unit.traffic.blockedBy,yieldTarget:unit.traffic.yieldTarget?.toArray()||null}:null;
  }
  return result;
};
