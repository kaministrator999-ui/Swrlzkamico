// Player-proposed Archive experiments. All state and effects belong to the
// current native Play session; authored meshes and material objects are kept.
const ST_ARCHIVE_HOUSES = new Set(['st-farm','st-income','st-fort','st-totem']);
const ST_ARCHIVE_DECKS = new Set(['st-wall','st-ramp']);
function stArchiveRandom(s){
  let x=s.archive.seed>>>0;x^=x<<13;x^=x>>>17;x^=x<<5;
  s.archive.seed=x>>>0;return (s.archive.seed>>>0)/4294967296;
}
function stArchiveRadius(unit){
  return typeof stUnitRadius==='function'?stUnitRadius(unit):unit.kind==='wolf'?(stSession.rules.wolfRadius||.68):(stSession.rules.sheepRadius||.27);
}
function stArchiveMaterialState(actor){
  const nodes=[];
  actor.traverse(node=>{
    if(!node.material)return;
    const original=node.material,materials=Array.isArray(original)?original:[original];
    const clones=materials.map(material=>material.clone());
    node.material=Array.isArray(original)?clones:clones[0];
    nodes.push({node,original,clones,castShadow:node.castShadow,receiveShadow:node.receiveShadow});
  });return nodes;
}
function stArchiveRestoreMaterials(entries){
  for(const entry of entries||[]){entry.node.material=entry.original;entry.node.castShadow=entry.castShadow;entry.node.receiveShadow=entry.receiveShadow;entry.clones.forEach(material=>material.dispose());}
}
function stArchiveRing(radius,color){
  const mesh=new THREE.Mesh(new THREE.RingGeometry(Math.max(.02,radius-.09),radius,32),new THREE.MeshBasicMaterial({color,transparent:true,opacity:.65,side:THREE.DoubleSide,depthWrite:false}));
  mesh.rotation.x=-Math.PI/2;mesh.renderOrder=5;scene.add(mesh);return mesh;
}
function stArchiveStart(s){
  const requested=Number(s.rules.seed)||0;
  s.archive={seed:(requested>0?requested:Math.floor(Math.random()*4294967295))>>>0||0x9e3779b9,thorns:[],scentClues:[],materialStates:new Map(),conversions:new Map(),effects:new Set(),decoys:new Set(),routeVersion:0,event:null,supply:null,nextEvent:Math.max(s.rules.headstart+30,s.rules.eventInterval||150),speedMultiplier:kind=>kind==='wolf'&&s.archive.event?.state==='active'&&s.archive.event.kind==='pressure'?1.15:1,damageMultiplier:1,visionMultiplier:1};
  for(const unit of s.units){
    unit.archiveXp=0;unit.archiveLevel=1;unit.archiveTotemUsed=false;unit.archiveTotemAt=-Infinity;unit.archiveSplitAt=-Infinity;unit.archiveScentUntil=0;unit.archiveNextScent=0;unit.archiveThornCooldown=0;unit.archiveThornContacts=new Set();unit.concealAmount=0;unit.archiveOnUpper=false;unit.archiveHeight=null;unit.archiveRoute=null;unit.archiveFalling=false;
    s.archive.materialStates.set(unit.actor,stArchiveMaterialState(unit.actor));
  }
  for(const actor of actors){
    if(actor.userData.actorType!=='st-thorn'||actor.userData.baked===false||!walkingObjectVisible(actor))continue;
    const pos=stWorldPosition(actor),scale=new THREE.Vector3();actor.getWorldScale(scale);
    s.archive.thorns.push({id:actor.userData.id,pos,radius:1.2*Math.max(Math.abs(scale.x),Math.abs(scale.z))});
  }
}
function stArchiveConcealment(unit){return THREE.MathUtils.clamp(unit?.concealAmount||0,0,1);}
function stArchiveUnitHeight(unit){
  return Number.isFinite(unit.archiveHeight)?unit.archiveHeight:terrainHeight(unit.pos.x,unit.pos.z);
}
function stArchiveDensity(s,building){
  // The transformed house still counts as its original supporting footprint.
  return s.buildings.filter(b=>b.hp>0&&b.progress>=1&&ST_ARCHIVE_HOUSES.has(b.kind)&&Math.hypot(b.pos.x-building.pos.x,b.pos.z-building.pos.z)<=s.rules.densityRadius).length;
}
function stArchiveTotemReady(s,unit,building){
  return !!(s.rules.totems&&unit&&!unit.captured&&!unit.isIllusion&&unit.kind==='sheep'&&building&&building.owner===unit.id&&building.hp>0&&building.progress>=1&&ST_ARCHIVE_HOUSES.has(building.kind)&&building.kind!=='st-totem'&&stArchiveDensity(s,building)>8&&(s.rules.totemLimit!=='once'||!unit.archiveTotemUsed)&&s.elapsed>=unit.archiveTotemAt+(s.rules.totemLimit==='cooldown'?s.rules.totemCooldown:0));
}
function stArchiveStatus(unit){
  const s=stSession;if(!s||!unit||!s.archive)return null;
  const next=Math.max(1,s.rules.progressionSeconds||45),selected=s.buildings.find(b=>b.id===s.selectedId&&b.hp>0);
  return {level:unit.archiveLevel||1,xp:Math.floor(unit.archiveXp||0),nextLevelXp:(unit.archiveLevel||1)*next,splitUnlocked:!!(s.rules.split&&(unit.archiveLevel||1)>=s.rules.splitUnlock),splitCooldownRemaining:Math.max(0,unit.archiveSplitAt+s.rules.splitCooldown-s.elapsed),splitLifetime:s.rules.splitLifetime,totemCooldownRemaining:s.rules.totemLimit==='cooldown'?Math.max(0,unit.archiveTotemAt+s.rules.totemCooldown-s.elapsed):0,totemUsed:!!unit.archiveTotemUsed,canTotem:stArchiveTotemReady(s,unit,selected),totemCount:s.buildings.filter(b=>b.hp>0&&b.kind==='st-totem'&&b.owner===unit.id).length,density:selected?stArchiveDensity(s,selected):0,densityRequired:9,upper:!!unit.archiveOnUpper,height:stArchiveUnitHeight(unit),scentRemaining:Math.max(0,unit.archiveScentUntil-s.elapsed),concealment:stArchiveConcealment(unit)};
}
function stArchivePublicStatus(s,unit){
  if(!s?.archive)return {};
  const e=s.archive.event,event=e?{kind:e.kind,state:e.state,label:e.label,startAt:e.startAt,endAt:e.endAt,warningRemaining:e.state==='warning'?Math.max(0,e.startAt-s.elapsed):0,remaining:e.state==='active'?Math.max(0,e.endAt-s.elapsed):0}:null;
  return {progression:stArchiveStatus(unit),event,scentClues:s.role==='wolf'||s.simulate?s.archive.scentClues.map(c=>({x:c.x,z:c.z,expires:c.expires,radius:c.radius})):[],upperHeight:s.rules.wallHeight};
}
function stArchiveConvertTotem(s,unit,building){
  if(!s.rules.totems)return stResult(false,'Stealth totems are disabled in Classic rules.');
  if(!building||building.owner!==unit.id||!ST_ARCHIVE_HOUSES.has(building.kind)||building.kind==='st-totem')return stResult(false,'Select one of your existing houses to transform.');
  if(building.progress<1)return stResult(false,'Finish the house before transforming it.');
  const count=stArchiveDensity(s,building);if(count<=8)return stResult(false,'This settlement needs nine allied houses inside the density radius.',{density:count,required:9});
  if(s.rules.totemLimit==='once'&&unit.archiveTotemUsed)return stResult(false,'This experimental preset allows one transformation per sheep per match.');
  const wait=Math.max(0,unit.archiveTotemAt+(s.rules.totemLimit==='cooldown'?s.rules.totemCooldown:0)-s.elapsed);if(wait>0)return stResult(false,'Your transformation is recharging.',{cooldown:wait});
  const original={mesh:building.mesh,kind:building.kind,income:building.income,colors:building.colors,visible:building.mesh.visible};
  const visual=stMakeVisual('st-totem');visual.position.copy(building.pos);visual.rotation.y=building.rotation||0;
  if(building.authored){original.mesh.updateWorldMatrix(true,false);original.mesh.getWorldQuaternion(visual.quaternion);original.mesh.getWorldScale(visual.scale);}
  scene.add(visual);original.mesh.visible=false;building.mesh=visual;building.kind='st-totem';building.income=0;
  const materials=new Set();visual.traverse(n=>{for(const material of Array.isArray(n.material)?n.material:[n.material])if(material?.color)materials.add(material);});building.colors=[...materials].map(material=>({material,color:material.color.clone()}));
  s.archive.conversions.set(building.id,{building,original,visual});unit.archiveTotemUsed=true;unit.archiveTotemAt=s.elapsed;
  s.message='The house became a stealth-shifting totem. Protect its nine-house settlement.';return stResult(true,'',{id:building.id,density:count});
}
function stArchiveRestoreConversion(s,id){
  const conversion=s.archive.conversions.get(id);if(!conversion)return;
  const {building,original,visual}=conversion;stDisposeVisual(visual);
  building.mesh=original.mesh;building.kind=original.kind;building.income=original.income;building.colors=original.colors;
  // A demolished authored original stays hidden until native Stop restores it.
  building.mesh.visible=building.hp>0?original.visible:false;s.archive.conversions.delete(id);
}

// Upper routes are a connected graph of actual walkable surfaces. A ground
// creature must walk to a ramp's external entry, ascend its slope, and follow
// connected decks. Clicking a roof never changes a creature's position.
function stArchiveSurface(building){
  if(building.hp<=0||building.progress<1||!ST_ARCHIVE_DECKS.has(building.kind))return null;
  const mesh=building.mesh;mesh.updateWorldMatrix(true,false);
  const matrix=mesh.matrixWorld.clone(),inverse=matrix.clone().invert(),scale=new THREE.Vector3();mesh.getWorldScale(scale);
  // Visuals have a fixed local 3.3-unit deck; configured runtime height and
  // authored Inspector scaling are already represented by matrixWorld.
  const height=3.3;
  const local=(x,z)=>new THREE.Vector3(x,building.kind==='st-ramp'?(3-z)/6*height:height,z).applyMatrix4(matrix);
  return {id:building.id,building,matrix,inverse,width:2.4*Math.abs(scale.x),height,point:local,base:local(0,3),top:local(0,-3),ends:[local(0,3),local(0,-3)],entry:new THREE.Vector3(0,0,3+1.05).applyMatrix4(matrix)};
}
function stArchiveSurfaceAt(point,radius=0){
  const s=stSession;if(!s?.archive||!s.rules.elevated)return null;
  let best=null;
  for(const building of s.buildings){const surface=stArchiveSurface(building);if(!surface)continue;const local=point.clone().applyMatrix4(surface.inverse);const margin=radius/Math.max(.1,surface.width/2.4);if(Math.abs(local.x)>1.2-margin+.015||Math.abs(local.z)>3.015)continue;
    const expected=surface.point(local.x,local.z);if(!best||Math.abs(expected.y-point.y)<Math.abs(best.point.y-point.y))best={surface,local,point:expected};
  }return best;
}
function stArchiveRouteGraph(s,radius){
  const surfaces=s.buildings.map(stArchiveSurface).filter(v=>v&&v.width>radius*2+.05),nodes=[],edges=[];
  const add=(surface,point)=>{const id=nodes.length;nodes.push({id,surface,point});edges.push([]);return id;};
  const connect=(a,b)=>{if(a===b)return;const distance=nodes[a].point.distanceTo(nodes[b].point);if(!edges[a].some(e=>e.id===b)){edges[a].push({id:b,distance});edges[b].push({id:a,distance});}};
  for(const surface of surfaces){surface.nodeIds=surface.ends.map(p=>add(surface,p));connect(...surface.nodeIds);}
  for(let i=0;i<surfaces.length;i++)for(let j=i+1;j<surfaces.length;j++){
    const a=surfaces[i],b=surfaces[j];
    for(const an of [...a.nodeIds])for(const bn of [...b.nodeIds])if(nodes[an].point.distanceTo(nodes[bn].point)<=.08)connect(an,bn);
    // T junctions connect only when a high endpoint is physically on another
    // deck. A low ramp entrance is never an upper shortcut.
    for(const [from,to] of [[a,b],[b,a]])for(const source of [...from.nodeIds]){
      const p=nodes[source].point,local=p.clone().applyMatrix4(to.inverse),project=to.point(0,THREE.MathUtils.clamp(local.z,-3,3));
      if(Math.abs(local.x)>1.2-radius/(to.width/2.4)+.015||Math.abs(local.z)>3.015||Math.abs(project.y-p.y)>.08)continue;
      if(p.distanceTo(project)>1.2-radius+.12)continue;
      const joint=add(to,project);for(const endpoint of to.nodeIds)connect(joint,endpoint);to.nodeIds.push(joint);connect(source,joint);
    }
  }
  return {surfaces,nodes,edges,add,connect};
}
function stArchiveGraphPath(graph,first,last){
  const dist=new Float64Array(graph.nodes.length);dist.fill(Infinity);const parent=new Int32Array(graph.nodes.length);parent.fill(-1);const done=new Uint8Array(graph.nodes.length);dist[first]=0;
  for(let iteration=0;iteration<graph.nodes.length;iteration++){
    let id=-1,min=Infinity;for(let i=0;i<dist.length;i++)if(!done[i]&&dist[i]<min){id=i;min=dist[i];}if(id<0)return null;if(id===last)break;done[id]=1;
    for(const edge of graph.edges[id])if(dist[id]+edge.distance<dist[edge.id]){dist[edge.id]=dist[id]+edge.distance;parent[edge.id]=id;}
  }
  if(!Number.isFinite(dist[last]))return null;const result=[];for(let id=last;id>=0;id=parent[id]){result.push(graph.nodes[id]);if(id===first)break;}return result.reverse();
}
function stArchiveGraphAttach(graph,surfaceId,point){
  const surface=graph.surfaces.find(v=>v.id===surfaceId);if(!surface)return -1;const id=graph.add(surface,point.clone());for(const node of surface.nodeIds)graph.connect(id,node);return id;
}
function stArchivePlanUpper(unit,x,z){
  const s=stSession,radius=stArchiveRadius(unit),requested=new THREE.Vector3(x,terrainHeight(x,z)+s.rules.wallHeight,z),hit=stArchiveSurfaceAt(requested,radius);
  if(!hit)return stResult(false,'Choose a completed wall deck or ramp with room for your creature.');
  const graph=stArchiveRouteGraph(s,radius),last=stArchiveGraphAttach(graph,hit.surface.id,hit.point);if(last<0)return stResult(false,'That deck is too narrow.');
  const currentHit=unit.archiveOnUpper?stArchiveSurfaceAt(unit.pos,radius):null,current=currentHit&&Math.abs(currentHit.point.y-unit.pos.y)<.25?currentHit:null;
  if(current){const first=stArchiveGraphAttach(graph,current.surface.id,unit.pos),route=stArchiveGraphPath(graph,first,last);if(!route)return stResult(false,'The decks are disconnected. Connect a ramp or wall segment first.');return stResult(true,'',{waypoints:route.slice(1).map(n=>({point:n.point.clone(),surfaceId:n.surface.id})),ground:[],target:hit.point.clone()});}
  let best=null;
  for(const surface of graph.surfaces){if(surface.building.kind!=='st-ramp')continue;const entry=surface.entry.clone();entry.y=terrainHeight(entry.x,entry.z);if(stBlocked(entry.x,entry.z,radius))continue;
    const ground=stPath(unit.pos,entry,radius);if(!ground||ground.length&&ground[ground.length-1].distanceTo(new THREE.Vector3(entry.x,0,entry.z))>.5)continue;
    const first=surface.nodeIds[0],route=stArchiveGraphPath(graph,first,last);if(!route)continue;
    const groundLength=ground.reduce((length,p,i)=>length+p.distanceTo(i?ground[i-1]:unit.pos),0),length=groundLength+route.reduce((n,node,i)=>n+(i?node.point.distanceTo(route[i-1].point):0),0);
    if(!best||length<best.length)best={length,ground:[...ground,entry],waypoints:route.map(n=>({point:n.point.clone(),surfaceId:n.surface.id})),target:hit.point.clone()};
  }
  return best?stResult(true,'',best):stResult(false,'No reachable ground entrance connects to that deck. Build a connected ramp and keep its entrance open.');
}
function stArchivePlanExit(unit,target=null){
  const s=stSession,radius=stArchiveRadius(unit),current=stArchiveSurfaceAt(unit.pos,radius);if(!current||Math.abs(current.point.y-unit.pos.y)>.25)return stResult(false,'No completed deck supports your creature here.');
  const graph=stArchiveRouteGraph(s,radius),first=stArchiveGraphAttach(graph,current.surface.id,unit.pos);let best=null;
  for(const surface of graph.surfaces){if(surface.building.kind!=='st-ramp')continue;const entry=surface.entry.clone();entry.y=terrainHeight(entry.x,entry.z);if(stBlocked(entry.x,entry.z,radius))continue;
    const route=stArchiveGraphPath(graph,first,surface.nodeIds[0]);if(!route)continue;
    const ground=target?stPath(entry,target,radius):[];if(target&&!ground)continue;
    const length=route.reduce((n,node,i)=>n+(i?node.point.distanceTo(route[i-1].point):0),0)+(target?entry.distanceTo(target)*.15:0);
    if(!best||length<best.length)best={length,ground,entry,target:target?.clone()||entry.clone(),waypoints:[...route.slice(1).map(n=>({point:n.point.clone(),surfaceId:n.surface.id})),{point:entry.clone(),surfaceId:surface.id,exit:true}]};
  }
  return best?stResult(true,'',best):stResult(false,'No connected ramp has an open ground exit. The wolf can still demolish this route.');
}
function stArchiveSetRoute(unit,plan,action='upper-move'){
  unit.archiveRoute={ground:plan.ground?.map(p=>p.clone())||[],groundEntry:plan.ground?.length?plan.ground[plan.ground.length-1].clone():null,waypoints:plan.waypoints,phase:unit.archiveOnUpper?'upper':'ground',target:plan.target.clone(),version:stSession.navVersion,exit:action==='exit-wall',resume:plan.resume||null};
  stSetOrder(unit,{action,x:plan.target.x,z:plan.target.z,y:plan.target.y,layer:'upper'});
}
function stArchiveAdvance(unit,points,dt,upper){
  const s=stSession,radius=stArchiveRadius(unit);let budget=unit.speed*s.archive.speedMultiplier(unit.kind)*dt,moved=false;
  while(points.length&&budget>0){const waypoint=points[0],next=upper?waypoint.point:waypoint,delta=next.clone().sub(unit.pos);if(!upper)delta.y=0;const distance=delta.length();
    if(distance<.015){points.shift();if(upper&&waypoint.exit){unit.archiveOnUpper=false;unit.archiveHeight=null;}continue;}
    const step=Math.min(budget,distance),candidate=unit.pos.clone().addScaledVector(delta,step/distance);
    const groundBlocked=!upper&&stBlocked(candidate.x,candidate.z,radius),entryBlocked=upper&&(waypoint.exit||candidate.y-terrainHeight(candidate.x,candidate.z)<.4)&&stBlocked(candidate.x,candidate.z,radius,waypoint.surfaceId);
    if(groundBlocked||entryBlocked){points.length=0;return moved;}
    unit.pos.copy(candidate);unit.actor.rotation.y=Math.atan2(delta.x,delta.z);if(upper){unit.archiveHeight=candidate.y;unit.archiveOnUpper=!waypoint.exit||distance>step+.015;}
    budget-=step;moved=true;if(step>=distance-.00001){points.shift();if(upper&&waypoint.exit){unit.archiveOnUpper=false;unit.archiveHeight=null;}}
  }
  stPlaceUnit(unit);return moved;
}
function stArchiveMoveUnit(unit,target,dt){
  const s=stSession;if(!s?.archive||!s.rules.elevated||unit.captured)return null;
  if(unit.archiveFalling)return false;
  if(!unit.archiveOnUpper&&!unit.archiveRoute&&target&&target.y-terrainHeight(target.x,target.z)>1.2&&(unit.kind!=='wolf'||s.rules.wolvesUseRamps)){
    const plan=stArchivePlanUpper(unit,target.x,target.z);if(plan.ok){plan.resume=unit.order;stArchiveSetRoute(unit,plan);}
  }
  if(unit.archiveOnUpper&&!unit.archiveRoute){
    // Ground orders, rescues and attacks descend through a connected entrance.
    const hit=target&&Math.abs(target.y-unit.pos.y)<1.2?stArchiveSurfaceAt(target,stArchiveRadius(unit)):null;
    const plan=hit?stArchivePlanUpper(unit,target.x,target.z):stArchivePlanExit(unit,target);
    if(!plan.ok)return false;const original=unit.order;plan.resume=original;stArchiveSetRoute(unit,plan,hit?'upper-move':'exit-wall');
  }
  const route=unit.archiveRoute;if(!route)return null;
  if(route.waypoints.some(p=>!s.buildings.some(b=>b.id===p.surfaceId&&b.hp>0&&b.progress>=1))){unit.archiveRoute=null;return false;}
  let moved=false;
  if(route.phase==='ground'){
    moved=stArchiveAdvance(unit,route.ground,dt,false);
    if(!route.ground.length){const base=route.waypoints[0]?.point,entry=route.groundEntry;if(!base){unit.archiveRoute=null;return moved;}if(!entry||Math.hypot(unit.pos.x-entry.x,unit.pos.z-entry.z)>.06){unit.archiveRoute=null;stSetOrder(unit,null);s.message='The ramp entrance became blocked. Choose another route.';return moved;}route.phase='upper';}
    return moved;
  }
  moved=stArchiveAdvance(unit,route.waypoints,dt,true);
  if(!route.waypoints.length){const resume=route.resume;unit.archiveRoute=null;if(resume&&resume.action!=='move'){stSetOrder(unit,resume);}else if(route.exit&&target&&Math.hypot(unit.pos.x-route.target.x,unit.pos.z-route.target.z)>.4){stSetOrder(unit,{action:'move',x:route.target.x,z:route.target.z});}else stSetOrder(unit,null);}
  return moved;
}
function stArchiveBuildingRemoved(building){
  const s=stSession;if(!s?.archive)return;
  if(s.archive.conversions.has(building.id))stArchiveRestoreConversion(s,building.id);
  if(!ST_ARCHIVE_DECKS.has(building.kind))return;s.archive.routeVersion++;
  for(const unit of s.units){if(unit.archiveRoute?.waypoints.some(p=>p.surfaceId===building.id))unit.archiveRoute=null;
    if(!unit.archiveOnUpper)continue;const surviving=s.buildings.filter(b=>b.id!==building.id&&b.hp>0),old=s.buildings;s.buildings=surviving;const beneath=stArchiveSurfaceAt(unit.pos,stArchiveRadius(unit));s.buildings=old;
    if(!beneath||Math.abs(beneath.point.y-unit.pos.y)>.25){unit.archiveFalling=true;unit.archiveRoute=null;stSetOrder(unit,null);}
  }
}
function stArchiveCloneSheep(s,unit){
  const actor=unit.actor.clone(true);actor.name=unit.name;actor.userData={stRuntime:true};
  // A decoy owns its geometry/material clones; removing it cannot dispose the
  // authored sheep's buffers or mutate the real sheep's expressions/colors.
  const originals=new Map((s.archive.materialStates.get(unit.actor)||[]).map(entry=>[entry.node,entry.original]));
  const cloneResources=(source,node)=>{if(node.geometry)node.geometry=node.geometry.clone();if(node.material){const material=originals.get(source)||source.material;node.material=Array.isArray(material)?material.map(m=>m.clone()):material.clone();}for(let i=0;i<node.children.length;i++)cloneResources(source.children[i],node.children[i]);};cloneResources(unit.actor,actor);
  actor.position.copy(unit.pos);actor.quaternion.copy(unit.actor.getWorldQuaternion(new THREE.Quaternion()));unit.actor.getWorldScale(actor.scale);scene.add(actor);
  const pivots=[];actor.traverse(node=>{if(/^stLeg|^stHead$|^stTail$/.test(node.name))pivots.push({node,rotation:node.rotation.clone()});});
  const decoy={id:'st-runtime-decoy-'+(++s.serial),name:unit.name,kind:'sheep',actor,pos:unit.pos.clone(),home:unit.pos.clone(),captured:false,isIllusion:true,sourceId:unit.id,spirit:null,spiritOrder:null,order:null,destination:null,path:[],pathVersion:-1,pathTarget:null,repathAt:0,botAt:Infinity,nextBuildAt:Infinity,nextWanderAt:Infinity,botIndex:unit.botIndex,phase:unit.phase,speed:unit.speed,damage:0,level:unit.level,attackAt:0,invulnerableUntil:unit.invulnerableUntil,captureAt:0,walkDistance:unit.walkDistance,walkBlend:unit.walkBlend,pivots,archiveXp:unit.archiveXp,archiveLevel:unit.archiveLevel,archiveSplitAt:unit.archiveSplitAt,archiveTotemUsed:true,archiveTotemAt:Infinity,archiveScentUntil:0,archiveNextScent:Infinity,archiveThornCooldown:Infinity,archiveThornContacts:new Set(),concealAmount:unit.concealAmount,archiveOnUpper:unit.archiveOnUpper,archiveHeight:unit.archiveHeight,archiveRoute:null,archiveFalling:false,archiveExpires:s.elapsed+s.rules.splitLifetime};actor.userData.id=decoy.id;
  s.units.push(decoy);s.archive.decoys.add(decoy);s.archive.materialStates.set(actor,stArchiveMaterialState(actor));return decoy;
}
function stArchiveRemoveDecoy(s,unit){
  if(!s.archive.decoys.has(unit))return;
  stArchiveRestoreMaterials(s.archive.materialStates.get(unit.actor));s.archive.materialStates.delete(unit.actor);stDisposeVisual(unit.actor);
  s.archive.decoys.delete(unit);const index=s.units.indexOf(unit);if(index>=0)s.units.splice(index,1);delete s.resources[unit.id];
}
function stArchiveCapture(unit,wolf){
  const s=stSession;if(!s?.archive||!unit.isIllusion)return false;
  stArchiveRemoveDecoy(s,unit);s.message='Contact dissolved the mirrored sheep.';return true;
}
function stArchiveRescue(unit,rescuer){
  const s=stSession;if(!s?.archive||!rescuer||rescuer.isIllusion)return;
  rescuer.archiveXp=(rescuer.archiveXp||0)+(s.rules.rescueXp||0);stArchiveUpdateLevel(s,rescuer);
  if(unit.id!==s.controlledId&&s.rules.elevated){unit.archiveEscortId=rescuer.id;unit.archiveEscortUntil=s.elapsed+15;}
}
function stArchiveUpdateLevel(s,unit){
  const before=unit.archiveLevel||1;unit.archiveLevel=1+Math.floor((unit.archiveXp||0)/Math.max(1,s.rules.progressionSeconds||45));
  if(unit.kind==='sheep')unit.level=unit.archiveLevel;
  if(unit.archiveLevel>before&&unit.id===s.controlledId)s.message=unit.name+' reached level '+unit.archiveLevel+(s.rules.split&&unit.archiveLevel>=s.rules.splitUnlock?'. Illusive Split is available.':'.');
}
function stArchiveDashTarget(unit,angle,length){
  const s=stSession,radius=stArchiveRadius(unit);
  for(let distance=length;distance>=1;distance-=.5){const x=unit.pos.x+Math.sin(angle)*distance,z=unit.pos.z+Math.cos(angle)*distance;
    if(Math.abs(x)>s.rules.bounds-radius||Math.abs(z)>s.rules.bounds-radius)continue;
    if(unit.archiveOnUpper){const plan=stArchivePlanUpper(unit,x,z);if(plan.ok)return {x,z,plan};}
    else if(!stBlocked(x,z,radius)&&stPath(unit.pos,new THREE.Vector3(x,0,z),radius))return {x,z};
  }return null;
}
function stArchiveSplit(s,unit,payload){
  if(!s.rules.split)return stResult(false,'Illusive Split is disabled in Classic rules.');
  if(unit.kind!=='sheep'||unit.captured||unit.isIllusion)return stResult(false,'Only a living sheep can use Illusive Split.');
  if(unit.archiveLevel<s.rules.splitUnlock)return stResult(false,'Illusive Split unlocks at level '+s.rules.splitUnlock+'.',{level:unit.archiveLevel,unlock:s.rules.splitUnlock});
  const wait=Math.max(0,unit.archiveSplitAt+s.rules.splitCooldown-s.elapsed);if(wait>0)return stResult(false,'Illusive Split is recharging.',{cooldown:wait});
  const requested=Number(payload.angle),heading=Number.isFinite(requested)?requested:unit.actor.rotation.y;
  let real=null,mirror=null;
  for(const turn of [Math.PI/3,-Math.PI/3,Math.PI/2,-Math.PI/2,Math.PI*.8]){real=stArchiveDashTarget(unit,heading-turn,7);mirror=stArchiveDashTarget(unit,heading+turn,7);if(real&&mirror&&Math.hypot(real.x-mirror.x,real.z-mirror.z)>1.8)break;real=null;mirror=null;}
  if(!real||!mirror)return stResult(false,'Find room for two separate escape paths before splitting.');
  unit.archiveSplitAt=s.elapsed;const copy=stArchiveCloneSheep(s,unit);
  if(real.plan)stArchiveSetRoute(unit,real.plan);else{unit.archiveRoute=null;stSetOrder(unit,{action:'move',x:real.x,z:real.z});}
  if(mirror.plan)stArchiveSetRoute(copy,mirror.plan);else stSetOrder(copy,{action:'move',x:mirror.x,z:mirror.z});
  s.message='Illusive Split! Two matching sheep dash along different paths.';return stResult(true,'',{cooldown:s.rules.splitCooldown,lifetime:s.rules.splitLifetime});
}
function stArchiveCommand(action,payload,unit){
  const s=stSession;if(!s?.archive)return null;
  if(action==='totem'){
    if(unit.kind!=='sheep'||unit.captured)return stResult(false,'Only a living sheep can transform its house.');
    const building=s.buildings.find(b=>b.id===(payload.id||s.selectedId)&&b.hp>0);return stArchiveConvertTotem(s,unit,building);
  }
  if(action==='split')return stArchiveSplit(s,unit,payload);
  const upper=action==='upper-move'||action==='move'&&payload.layer==='upper',exit=action==='exit-wall'||action==='move'&&unit.archiveOnUpper;
  if(!upper&&!exit){if(['move','build','attack','rescue'].includes(action))unit.archiveRoute=null;return null;}
  if(!s.rules.elevated)return stResult(false,'Elevated routes are disabled in Classic rules.');
  if(unit.captured)return stResult(false,'A rescued sheep can use ramps after leaving the spirit pen.');
  if(s.selectedId!==unit.id)return stResult(false,'Select your creature to give a route order.');
  if(unit.kind==='wolf'&&!s.rules.wolvesUseRamps)return stResult(false,'Wolf ramp traversal is disabled in this experimental preset.');
  if(unit.kind==='wolf'&&s.elapsed<s.rules.headstart)return stResult(false,'The wolves are released after the head start.');
  const x=Number(payload.x),z=Number(payload.z);if(action!=='exit-wall'&&(!Number.isFinite(x)||!Number.isFinite(z)))return stResult(false,'Choose a destination on the map.');
  const target=action==='exit-wall'?null:new THREE.Vector3(x,terrainHeight(x,z),z);
  if(!upper&&target&&(stBlocked(x,z,stArchiveRadius(unit))||Math.abs(x)>s.rules.bounds||Math.abs(z)>s.rules.bounds))return stResult(false,'Choose an open ground destination beyond a connected ramp.');
  const plan=upper?stArchivePlanUpper(unit,x,z):stArchivePlanExit(unit,target);if(!plan.ok)return plan;stArchiveSetRoute(unit,plan,upper?'upper-move':'exit-wall');return stResult(true,'Follow the connected ramp and deck route.',{destination:plan.target.toArray(),waypoints:plan.waypoints.length});
}

function stArchiveEventLabel(kind){return {pressure:'Experimental wolf pressure',fog:'Experimental dense fog',supply:'Experimental supply drop'}[kind]||'Experimental event';}
function stArchiveEndEvent(s){
  s.archive.damageMultiplier=1;s.archive.visionMultiplier=1;
  if(s.archive.supply){stDisposeVisual(s.archive.supply.mesh);s.archive.effects.delete(s.archive.supply.mesh);s.archive.supply=null;}
  s.archive.event=null;
}
function stArchiveSupply(s){
  const radius=Math.min(s.rules.bounds-6,14);let position=null;
  for(let i=0;i<16;i++){const angle=stArchiveRandom(s)*Math.PI*2,distance=8+stArchiveRandom(s)*Math.max(0,radius-8),x=s.pen.x+Math.cos(angle)*distance,z=s.pen.z+Math.sin(angle)*distance;if(Math.abs(x)>s.rules.bounds-2||Math.abs(z)>s.rules.bounds-2||stBlocked(x,z,1))continue;position=new THREE.Vector3(x,terrainHeight(x,z),z);break;}
  if(!position)return;
  const mesh=new THREE.Group();const crate=new THREE.Mesh(new THREE.BoxGeometry(1.25,1.05,1.25),new THREE.MeshStandardMaterial({color:'#dec37e',roughness:.8}));crate.position.y=.55;mesh.add(crate);
  const lid=new THREE.Mesh(new THREE.BoxGeometry(1.4,.12,1.4),new THREE.MeshStandardMaterial({color:'#5be1b2',emissive:'#156749',emissiveIntensity:.5}));lid.position.y=1.15;mesh.add(lid);mesh.position.copy(position);scene.add(mesh);s.archive.effects.add(mesh);s.archive.supply={mesh,pos:position,collected:false};
}
function stArchiveEvents(s){
  const a=s.archive;if(!s.rules.events){if(a.event)stArchiveEndEvent(s);return;}
  if(!a.event&&s.elapsed>=a.nextEvent){
    const pool=(s.rules.eventPool||[]).filter(kind=>['pressure','fog','supply'].includes(kind));if(!pool.length)return;
    const kind=pool[Math.floor(stArchiveRandom(s)*pool.length)],startAt=s.elapsed+s.rules.eventWarning,endAt=startAt+s.rules.eventDuration;
    a.event={kind,state:'warning',startAt,endAt,label:stArchiveEventLabel(kind)};
    // Warning plus event duration never eats the safe interval before another
    // warning. Values are exposed experimental candidates, not hidden balance.
    a.nextEvent=endAt+Math.max(30,s.rules.eventInterval);s.message=a.event.label+' starts in '+Math.ceil(s.rules.eventWarning)+' seconds.';
  }
  const event=a.event;if(!event)return;
  if(event.state==='warning'&&s.elapsed>=event.startAt){event.state='active';a.damageMultiplier=event.kind==='pressure'?1.2:1;a.visionMultiplier=event.kind==='fog'?.65:1;if(event.kind==='supply')stArchiveSupply(s);s.message=event.label+' is active for '+Math.ceil(s.rules.eventDuration)+' seconds.';}
  if(event.state==='active'&&s.elapsed>=event.endAt){stArchiveEndEvent(s);s.message='The experimental event ended. The usual rules return.';return;}
  const supply=a.supply;if(supply&&!supply.collected){
    supply.mesh.rotation.y=s.elapsed*.45;
    const contestant=s.units.some(u=>u.kind==='wolf'&&!u.captured&&u.pos.distanceTo(supply.pos)<4);
    if(!contestant){const sheep=s.units.find(u=>u.kind==='sheep'&&!u.isIllusion&&!u.captured&&u.pos.distanceTo(supply.pos)<1.5);if(sheep){s.resources[sheep.id]=(s.resources[sheep.id]||0)+30;supply.collected=true;stDisposeVisual(supply.mesh);a.effects.delete(supply.mesh);a.supply=null;s.message=sheep.name+' collected the experimental supply: 30 gold.';}}
    // Unseen objectives never leak through the native fog actor visibility.
    if(supply.mesh.parent)supply.mesh.visible=s.simulate||typeof stSeenByRole!=='function'||stSeenByRole({id:'archive-supply',kind:'supply',pos:supply.pos},s.role);
  }
}
function stArchiveBeforeUpdate(s,dt){
  if(!s.archive)return;stArchiveEvents(s);
  for(const unit of [...s.archive.decoys]){
    if(s.elapsed>=unit.archiveExpires){stArchiveRemoveDecoy(s,unit);continue;}
    const before=unit.pos.clone(),target=stOrderTarget(unit);if(target){const magic=stArchiveMoveUnit(unit,target,dt);if(magic===null)stMoveUnit(unit,target,dt);}unit.archiveMovedDistance=Math.hypot(unit.pos.x-before.x,unit.pos.z-before.z);unit.velocity=unit.pos.clone().sub(before).multiplyScalar(dt?1/dt:0);
  }
  for(const unit of s.units){
    if(unit.kind!=='sheep'||unit.isIllusion||unit.captured||unit.id===s.controlledId||unit.archiveRoute||!unit.archiveEscortId||s.elapsed>unit.archiveEscortUntil)continue;
    const rescuer=s.units.find(u=>u.id===unit.archiveEscortId&&!u.captured);if(!rescuer)continue;
    const target=rescuer.archiveRoute?.target||(rescuer.archiveOnUpper?rescuer.pos:null);if(!target)continue;
    const plan=target.y-terrainHeight(target.x,target.z)>1.2?stArchivePlanUpper(unit,target.x,target.z):unit.archiveOnUpper?stArchivePlanExit(unit,target):null;
    if(plan?.ok)stArchiveSetRoute(unit,plan,target.y-terrainHeight(target.x,target.z)>1.2?'upper-move':'exit-wall');
  }
  for(const unit of s.units)if(unit.archiveFalling&&!unit.captured){
    const floor=terrainHeight(unit.pos.x,unit.pos.z);unit.archiveHeight=Math.max(floor,(unit.archiveHeight??unit.pos.y)-dt*7);unit.pos.y=unit.archiveHeight;
    if(unit.archiveHeight<=floor+.001){unit.archiveHeight=null;unit.archiveFalling=false;unit.archiveOnUpper=false;}
    stPlaceUnit(unit);
  }
}
function stArchiveScent(s,unit){
  if(unit.archiveScentUntil<=s.elapsed||unit.archiveNextScent>s.elapsed)return;
  unit.archiveNextScent=s.elapsed+s.rules.scentInterval;
  const angle=stArchiveRandom(s)*Math.PI*2,offset=1+stArchiveRandom(s)*1.3;
  const clue={x:THREE.MathUtils.clamp(Math.round((unit.pos.x+Math.cos(angle)*offset)/1.5)*1.5,-s.rules.bounds+1,s.rules.bounds-1),z:THREE.MathUtils.clamp(Math.round((unit.pos.z+Math.sin(angle)*offset)/1.5)*1.5,-s.rules.bounds+1,s.rules.bounds-1),radius:3.4,expires:Math.min(unit.archiveScentUntil,s.elapsed+s.rules.scentInterval*1.4)};
  clue.mesh=stArchiveRing(clue.radius,'#e49b81');clue.mesh.position.set(clue.x,terrainHeight(clue.x,clue.z)+.06,clue.z);clue.mesh.name='Approximate thorn scent';s.archive.effects.add(clue.mesh);s.archive.scentClues.push(clue);
  // No unit identifier or evolving live position is stored in a clue. Each
  // pulse is a deliberately imprecise frozen area for hunters to investigate.
}
function stArchiveAfterUpdate(s,dt){
  if(!s.archive)return;
  const totems=s.rules.totems?s.buildings.filter(b=>b.hp>0&&b.progress>=1&&b.kind==='st-totem'&&stArchiveDensity(s,b)>8):[];
  for(const unit of s.units){
    if(unit.kind!=='sheep')continue;
    if(!unit.captured&&!unit.isIllusion){unit.archiveXp=(unit.archiveXp||0)+dt;stArchiveUpdateLevel(s,unit);}
    const inside=new Set();
    if(s.rules.thorns&&!unit.captured&&!unit.isIllusion&&!unit.archiveOnUpper)for(const thorn of s.archive.thorns){
      if(Math.hypot(unit.pos.x-thorn.pos.x,unit.pos.z-thorn.pos.z)>thorn.radius+stArchiveRadius(unit))continue;inside.add(thorn.id);
      if(unit.archiveThornContacts.has(thorn.id)||s.elapsed<unit.archiveThornCooldown)continue;
      unit.archiveThornCooldown=s.elapsed+s.rules.thornCooldown;
      if(stArchiveRandom(s)<s.rules.thornChance){unit.archiveScentUntil=s.elapsed+s.rules.thornDuration;unit.archiveNextScent=s.elapsed;if(unit.id===s.controlledId)s.message='A thorn pricked you. Wolves receive temporary approximate scent pulses.';}
    }
    unit.archiveThornContacts=inside;if(s.rules.thorns&&!unit.captured)stArchiveScent(s,unit);
    const concealed=!unit.captured&&totems.some(b=>Math.hypot(unit.pos.x-b.pos.x,unit.pos.z-b.pos.z)<=s.rules.totemRadius&&Math.abs(stArchiveUnitHeight(unit)-b.pos.y)<1.5);
    const target=concealed?1:0,seconds=concealed?s.rules.fadeSeconds:s.rules.revealSeconds;unit.concealAmount=THREE.MathUtils.clamp(unit.concealAmount+(target===1?dt:-dt)/Math.max(.1,seconds),0,1);
    const alpha=1-unit.concealAmount*.78;
    for(const entry of s.archive.materialStates.get(unit.actor)||[])for(let i=0;i<entry.clones.length;i++){
      const material=entry.clones[i],original=Array.isArray(entry.original)?entry.original[i]:entry.original;
      material.opacity=original.opacity*alpha;material.transparent=original.transparent||alpha<.999;material.depthWrite=alpha<.4?false:original.depthWrite;entry.node.castShadow=entry.castShadow&&unit.concealAmount<.4;
    }
  }
  for(const clue of [...s.archive.scentClues]){
    if(clue.expires<=s.elapsed){stDisposeVisual(clue.mesh);s.archive.effects.delete(clue.mesh);s.archive.scentClues.splice(s.archive.scentClues.indexOf(clue),1);continue;}
    clue.mesh.visible=s.role==='wolf'||s.simulate;clue.mesh.material.opacity=.55*Math.min(1,(clue.expires-s.elapsed)/Math.max(.1,s.rules.scentInterval));
  }
}
function stArchiveStop(s){
  if(!s.archive)return;
  for(const copy of [...s.archive.decoys])stArchiveRemoveDecoy(s,copy);
  for(const id of [...s.archive.conversions.keys()])stArchiveRestoreConversion(s,id);
  for(const entries of s.archive.materialStates.values())stArchiveRestoreMaterials(entries);s.archive.materialStates.clear();
  for(const effect of s.archive.effects)stDisposeVisual(effect);s.archive.effects.clear();s.archive.scentClues.length=0;
  for(const unit of s.units){unit.archiveRoute=null;unit.archiveHeight=null;unit.archiveOnUpper=false;unit.archiveFalling=false;unit.concealAmount=0;}
  s.archive=null;
}
