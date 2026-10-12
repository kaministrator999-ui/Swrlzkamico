// Match state and helpers are transient. Authored actors remain the native
// editor/save source, including during a running match.
let stSession = null;
const ST_BUILDINGS = Object.freeze({
  'st-farm':{name:'Farm',cost:0,hp:180,time:1.4,income:0,size:2.4},
  'st-income':{name:'Income Farm',cost:60,hp:240,time:3,income:3,size:2.4},
  'st-fort':{name:'Strong Farm',cost:100,hp:650,time:4,income:0,size:2.4},
  'st-wall':{name:'Castle Wall',cost:45,hp:360,time:3,income:0,size:2.4,length:6},
  'st-ramp':{name:'Ramp',cost:55,hp:300,time:3,income:0,size:2.4,length:6},
  'st-totem':{name:'Stealth Totem',cost:0,hp:180,time:1,income:0,size:2.4,conversionOnly:true}
});
const ST_GRID=.15,ST_SHEEP_RADIUS=.27,ST_WOLF_RADIUS=.68;
const stBuildKind=value=>({farm:'st-farm',income:'st-income',fort:'st-fort',strong:'st-fort',wall:'st-wall',ramp:'st-ramp',totem:'st-totem'}[value]||value);
const stResult=(ok,reason='',extra={})=>({...extra,ok,reason});
function stWorldPosition(actor){actor.updateWorldMatrix(true,false);return actor.getWorldPosition(new THREE.Vector3());}
function stUnitRadius(unitOrSpecies,rules=stSession?.rules||stRules()){return (typeof unitOrSpecies==='string'?unitOrSpecies:unitOrSpecies?.kind)==='wolf'?(rules.wolfRadius??ST_WOLF_RADIUS):(rules.sheepRadius??ST_SHEEP_RADIUS);}
function stEntityHeight(entity){return entity.spirit?.position.y??entity.pos?.y??0;}
function stPlaceUnit(unit){
  const p=unit.pos.clone();p.y=typeof stArchiveUnitHeight==='function'?stArchiveUnitHeight(unit):terrainHeight(p.x,p.z);if(!Number.isFinite(p.y))p.y=terrainHeight(p.x,p.z);unit.pos.y=p.y;
  if(unit.actor.parent&&unit.actor.parent!==scene)unit.actor.parent.worldToLocal(p);unit.actor.position.copy(p);
}
function stActorFootprint(actor,halfX,halfZ){
  const pos=stWorldPosition(actor),scale=new THREE.Vector3(),q=new THREE.Quaternion();actor.getWorldScale(scale);actor.getWorldQuaternion(q);const e=new THREE.Euler().setFromQuaternion(q,'YXZ');
  return stFootprint(pos.x,pos.z,halfX*Math.abs(scale.x),halfZ*Math.abs(scale.z),e.y,actor.userData.id);
}
function stFootprint(x,z,hx,hz,rotation=0,id=null){
  const c=Math.cos(rotation),sn=Math.sin(rotation),corners=[[-hx,-hz],[hx,-hz],[hx,hz],[-hx,hz]].map(([a,b])=>[x+a*c+b*sn,z-a*sn+b*c]);
  return {id,x,z,localHalfX:hx,localHalfZ:hz,rotation,halfX:Math.abs(c)*hx+Math.abs(sn)*hz,halfZ:Math.abs(sn)*hx+Math.abs(c)*hz,corners};
}
function stLocalPoint(x,z,o){const c=Math.cos(o.rotation||0),sn=Math.sin(o.rotation||0),dx=x-o.x,dz=z-o.z;return [dx*c-dz*sn,dx*sn+dz*c];}
function stIntersectsObstacle(x,z,radius,o){
  if(o.radius!==undefined)return Math.hypot(x-o.x,z-o.z)<radius+o.radius-1e-6;
  const [lx,lz]=stLocalPoint(x,z,o),dx=Math.max(0,Math.abs(lx)-(o.localHalfX??o.halfX)),dz=Math.max(0,Math.abs(lz)-(o.localHalfZ??o.halfZ));return dx*dx+dz*dz<radius*radius-1e-8;
}
function stRectsOverlap(a,b){
  const ac=a.corners||stFootprint(a.x,a.z,a.halfX,a.halfZ).corners,bc=b.corners||stFootprint(b.x,b.z,b.halfX,b.halfZ).corners;
  for(const angle of [a.rotation||0,(a.rotation||0)+Math.PI/2,b.rotation||0,(b.rotation||0)+Math.PI/2]){const x=Math.cos(angle),z=Math.sin(angle),ap=ac.map(p=>p[0]*x+p[1]*z),bp=bc.map(p=>p[0]*x+p[1]*z);if(Math.max(...ap)<=Math.min(...bp)+1e-6||Math.max(...bp)<=Math.min(...ap)+1e-6)return false;}return true;
}
function stStaticObstacle(actor){
  const kind=actor.userData.actorType;if(actor.userData.baked===false||!walkingObjectVisible(actor)||!['st-tree','st-rock','st-pond','st-shop'].includes(kind))return null;
  const pos=stWorldPosition(actor),scale=new THREE.Vector3();actor.getWorldScale(scale);
  if(kind==='st-tree'||kind==='st-rock')return {id:actor.userData.id,kind,x:pos.x,z:pos.z,radius:(kind==='st-tree'?1.7:1.8)*Math.max(Math.abs(scale.x),Math.abs(scale.z))};
  return {...stActorFootprint(actor,kind==='st-pond'?3:1.5,kind==='st-pond'?3:1.5),kind};
}
function stBuildingObstacle(b){return {...stFootprint(b.pos.x,b.pos.z,b.localHalfX??b.halfX,b.localHalfZ??b.halfZ,b.rotation||0,b.id),kind:b.kind};}
function stObstacles(){const s=stSession;return s?[...s.obstacles,...s.buildings.filter(b=>b.hp>0).map(stBuildingObstacle)]:[];}
function stContextBlocked(context,x,z,radius,ignore=null){
  if(Math.abs(x)>context.rules.bounds-radius||Math.abs(z)>context.rules.bounds-radius)return true;
  return context.obstacles.some(o=>o.id!==ignore&&stIntersectsObstacle(x,z,radius,o));
}
function stBlocked(x,z,radius,ignore=null){return !stSession||stContextBlocked({rules:stSession.rules,obstacles:stObstacles()},x,z,radius,ignore);}
function stSegmentClear(context,a,b,radius){
  const d=Math.hypot(b.x-a.x,b.z-a.z),steps=Math.max(1,Math.ceil(d/(ST_GRID*.45)));
  for(let i=0;i<=steps;i++){const f=i/steps;if(stContextBlocked(context,a.x+(b.x-a.x)*f,a.z+(b.z-a.z)*f,radius))return false;}return true;
}
function stInvalidateNavigation(){if(stSession){stSession.navVersion++;stSession.navigation.clear();}}
function stBuildNavigation(context,radius){
  const extent=Math.floor((context.rules.bounds-radius)/ST_GRID),width=extent*2+1,count=width*width;
  const nav={extent,width,count,radius,context,blocked:new Uint8Array(count),scores:new Float64Array(count),parents:new Int32Array(count),closed:new Uint8Array(count),components:new Int32Array(count),componentSerial:0};
  for(const o of context.obstacles){
    const hx=(o.radius??o.halfX)+radius,hz=(o.radius??o.halfZ)+radius,minX=Math.max(-extent,Math.floor((o.x-hx)/ST_GRID)),maxX=Math.min(extent,Math.ceil((o.x+hx)/ST_GRID)),minZ=Math.max(-extent,Math.floor((o.z-hz)/ST_GRID)),maxZ=Math.min(extent,Math.ceil((o.z+hz)/ST_GRID));
    for(let z=minZ;z<=maxZ;z++)for(let x=minX;x<=maxX;x++)if(stIntersectsObstacle(x*ST_GRID,z*ST_GRID,radius,o))nav.blocked[(z+extent)*width+x+extent]=1;
  }return nav;
}
function stNavigation(radius){const s=stSession,key=String(radius);if(!s.navigation.has(key))s.navigation.set(key,stBuildNavigation({rules:s.rules,obstacles:stObstacles()},radius));return s.navigation.get(key);}
function stGridCell(nav,x,z,nearby=true){
  const gx=THREE.MathUtils.clamp(Math.round(x/ST_GRID),-nav.extent,nav.extent),gz=THREE.MathUtils.clamp(Math.round(z/ST_GRID),-nav.extent,nav.extent),index=(gz+nav.extent)*nav.width+gx+nav.extent;
  const origin={x,z},usable=cell=>!nav.blocked[cell]&&stSegmentClear(nav.context,origin,stCellPoint(nav,cell),nav.radius);
  if(usable(index))return index;if(!nearby||stContextBlocked(nav.context,x,z,nav.radius))return -1;
  // Connector search stays in the same physical pocket: it cannot relocate a
  // trapped sheep through an intervening house to a convenient grid cell.
  for(let ring=1;ring<=4;ring++){let best=-1,distance=Infinity;for(let dz=-ring;dz<=ring;dz++)for(let dx=-ring;dx<=ring;dx++){if(Math.abs(dx)!==ring&&Math.abs(dz)!==ring)continue;const cx=gx+dx,cz=gz+dz;if(Math.abs(cx)>nav.extent||Math.abs(cz)>nav.extent)continue;const cell=(cz+nav.extent)*nav.width+cx+nav.extent;if(!usable(cell))continue;const d=(cx*ST_GRID-x)**2+(cz*ST_GRID-z)**2;if(d<distance){distance=d;best=cell;}}if(best>=0)return best;}return -1;
}
function stCellPoint(nav,id){return new THREE.Vector3((id%nav.width-nav.extent)*ST_GRID,0,(Math.floor(id/nav.width)-nav.extent)*ST_GRID);}
function stSameNavigationPocket(nav,first,last){
  if(!nav.components[first]){
    const component=++nav.componentSerial,queue=new Int32Array(nav.count);let head=0,tail=1;queue[0]=first;nav.components[first]=component;
    // Four-way connectivity has the same regions as our corner-safe eight-way
    // movement. Cached regions prevent a sealed house ring from triggering a
    // whole-map A* search on every wolf decision.
    while(head<tail){const id=queue[head++],x=id%nav.width,z=Math.floor(id/nav.width);for(const next of [x>0?id-1:-1,x<nav.width-1?id+1:-1,z>0?id-nav.width:-1,z<nav.width-1?id+nav.width:-1])if(next>=0&&!nav.blocked[next]&&!nav.components[next]){nav.components[next]=component;queue[tail++]=next;}}
  }
  return nav.components[first]===nav.components[last];
}
function stFindPath(nav,start,target){
  if(stContextBlocked(nav.context,start.x,start.z,nav.radius)||stContextBlocked(nav.context,target.x,target.z,nav.radius))return null;
  if(stSegmentClear(nav.context,start,target,nav.radius))return [new THREE.Vector3(target.x,0,target.z)];
  const first=stGridCell(nav,start.x,start.z),last=stGridCell(nav,target.x,target.z);if(first<0||last<0)return null;
  if(first===last)return [new THREE.Vector3(target.x,0,target.z)];if(!stSameNavigationPocket(nav,first,last))return null;nav.scores.fill(Infinity);nav.parents.fill(-1);nav.closed.fill(0);
  const heap=[],push=(id,f)=>{let i=heap.length;heap.push({id,f});while(i){const p=(i-1)>>1;if(heap[p].f<=f)break;heap[i]=heap[p];i=p;}heap[i]={id,f};},pop=()=>{const top=heap[0],tail=heap.pop();if(heap.length){let i=0;while(i*2+1<heap.length){let c=i*2+1;if(c+1<heap.length&&heap[c+1].f<heap[c].f)c++;if(heap[c].f>=tail.f)break;heap[i]=heap[c];i=c;}heap[i]=tail;}return top.id;};
  const goalX=last%nav.width,goalZ=Math.floor(last/nav.width),heuristic=id=>{const dx=Math.abs(id%nav.width-goalX),dz=Math.abs(Math.floor(id/nav.width)-goalZ);return Math.max(dx,dz)+(Math.SQRT2-1)*Math.min(dx,dz);};nav.scores[first]=0;push(first,heuristic(first));let expanded=0,found=false;
  while(heap.length&&expanded<110000){const id=pop();if(nav.closed[id])continue;if(id===last){found=true;break;}nav.closed[id]=1;expanded++;const x=id%nav.width,z=Math.floor(id/nav.width);for(let dz=-1;dz<=1;dz++)for(let dx=-1;dx<=1;dx++){if(!dx&&!dz)continue;const nx=x+dx,nz=z+dz;if(nx<0||nz<0||nx>=nav.width||nz>=nav.width)continue;const next=nz*nav.width+nx;if(nav.blocked[next]||nav.closed[next]||dx&&dz&&(nav.blocked[z*nav.width+nx]||nav.blocked[nz*nav.width+x]))continue;const score=nav.scores[id]+(dx&&dz?Math.SQRT2:1);if(score>=nav.scores[next])continue;nav.scores[next]=score;nav.parents[next]=id;push(next,score+heuristic(next));}}
  if(!found)return null;const path=[];let id=last;while(id!==first&&id>=0){path.push(stCellPoint(nav,id));id=nav.parents[id];}path.reverse();path.push(new THREE.Vector3(target.x,0,target.z));return path;
}
function stPath(start,target,radius){return stFindPath(stNavigation(radius),start,target);}
function stInspectPath(payload={}){
  const point=value=>Array.isArray(value)&&value.length>=2?new THREE.Vector3(Number(value[0]),value.length>2?Number(value[1]):0,Number(value[value.length>2?2:1])):null,from=point(payload.from),to=point(payload.to),species=payload.species==='wolf'?'wolf':'sheep';
  if(!from||!to||![from.x,from.y,from.z,to.x,to.y,to.z].every(Number.isFinite))return stResult(false,'Choose a start and destination.',{reachable:false,points:[],path:[]});
  const rules=stSession?.rules||stRules(),radius=stUnitRadius(species,rules);let context;
  if(stSession)context={rules,obstacles:stObstacles()};else{const obstacles=[];for(const actor of actors){if(actor.userData.baked===false||!walkingObjectVisible(actor))continue;const kind=actor.userData.actorType;if(ST_BUILDINGS[kind])obstacles.push(stActorFootprint(actor,1.2,(kind==='st-wall'||kind==='st-ramp')?3:1.2));else{const obstacle=stStaticObstacle(actor);if(obstacle)obstacles.push(obstacle);}}context={rules,obstacles};}
  const route=stFindPath(stBuildNavigation(context,radius),from,to),points=(route||[]).map(p=>[p.x,terrainHeight(p.x,p.z),p.z]);let length=0,previous=from;for(const p of route||[]){length+=Math.hypot(p.x-previous.x,p.z-previous.z);previous=p;}
  return stResult(!!route,route?'':'No ground route fits this species.',{reachable:!!route,species,radius,from:from.toArray(),to:to.toArray(),points,path:points,length,warnings:[]});
}
function stSetOrder(unit,order){if(!order)unit.archiveRoute=null;unit.order=order;unit.path=[];unit.pathVersion=-1;unit.repathAt=0;unit.destination=order&&order.x!==undefined?new THREE.Vector3(order.x,order.y||0,order.z):null;}
function stRemember(observer,target){if(observer.isIllusion)return;const s=stSession;observer.memory.set(target.id,{id:target.id,kind:target.kind,name:target.name,pos:target.pos.clone(),velocity:(target.velocity||new THREE.Vector3()).clone(),at:s.elapsed});}
function stPerceivesDirect(observer,target){
  const s=stSession;if(!s||!observer||observer.captured||observer.isIllusion||!target||target.captured)return false;if(observer.id===target.id||observer.kind===target.kind)return true;
  const range=(observer.kind==='wolf'?s.rules.wolfVision:s.rules.sheepVision)*(s.archive?.visionMultiplier??1),concealment=target.kind==='sheep'&&typeof stArchiveConcealment==='function'?THREE.MathUtils.clamp(stArchiveConcealment(target)||0,0,1):0,d=Math.hypot(observer.pos.x-target.pos.x,observer.pos.z-target.pos.z);
  return d<=Math.max(2.2,range*(1-.85*concealment));
}
function stPerceives(observer,target){
  const s=stSession;if(!s||observer?.isIllusion)return false;if(s.rules.fogMode==='off')return true;if(stPerceivesDirect(observer,target))return true;
  return s.rules.fogMode==='team'&&s.units.some(u=>u.kind===observer.kind&&!u.captured&&!u.isIllusion&&stPerceivesDirect(u,target));
}
function stSeenByRole(entity,role=stSession?.role){
  const s=stSession;if(!s||s.simulate||s.rules.fogMode==='off')return true;if(entity.kind===role||entity.captured&&role==='sheep'||entity.owner&&s.units.some(u=>u.id===entity.owner&&u.kind===role))return true;
  let viewers=s.units.filter(u=>u.kind===role&&!u.captured&&!u.isIllusion);if(s.rules.fogMode==='solo'&&role===s.role)viewers=viewers.filter(u=>u.id===s.controlledId);
  return viewers.some(u=>entity.actor&&!entity.captured?stPerceivesDirect(u,entity):Math.hypot(u.pos.x-(entity.spirit?.position||entity.pos).x,u.pos.z-(entity.spirit?.position||entity.pos).z)<=((role==='wolf'?s.rules.wolfVision:s.rules.sheepVision)*(s.archive?.visionMultiplier??1)));
}
function stOrderTarget(unit){
  const s=stSession,o=unit.order;if(!o)return null;
  if(o.action==='attack'){const building=s.buildings.find(b=>b.id===o.id&&b.hp>0);if(building)return stPerceives(unit,building)?stAttackApproach(unit,building):null;const target=s.units.find(u=>u.id===o.id&&!u.captured);if(target&&stPerceives(unit,target)){stRemember(unit,target);const p=target.pos.clone();if(unit.id!==s.controlledId&&target.velocity){p.x+=target.velocity.x*.3;p.z+=target.velocity.z*.3;if(stBlocked(p.x,p.z,stUnitRadius(unit)))p.copy(target.pos);}return p;}const memory=unit.memory.get(o.id);return memory&&s.elapsed-memory.at<12?memory.pos:null;}
  if(o.action==='rescue')return s.units.find(u=>u.id===o.id&&u.captured)?.spirit?.position||null;return unit.destination;
}
function stMoveUnit(unit,target,dt){
  const s=stSession;if(!target)return false;if(typeof stArchiveMoveUnit==='function'){const handled=stArchiveMoveUnit(unit,target,dt);if(handled!==null&&handled!==undefined)return handled;}
  const radius=stUnitRadius(unit),movedTarget=!unit.pathTarget||unit.pathTarget.distanceToSquared(target)>.45;
  if(unit.pathVersion!==s.navVersion||movedTarget||s.elapsed>=unit.repathAt){unit.path=stPath(unit.pos,target,radius)||[];unit.pathVersion=s.navVersion;unit.pathTarget=target.clone();unit.repathAt=s.elapsed+.9;}
  let budget=unit.speed*(s.archive?.speedMultiplier?.(unit.kind)??1)*dt,moved=false;const context={rules:s.rules,obstacles:stObstacles()};
  while(unit.path.length&&budget>0){const next=unit.path[0],dx=next.x-unit.pos.x,dz=next.z-unit.pos.z,distance=Math.hypot(dx,dz);if(distance<.015){unit.path.shift();continue;}const step=Math.min(budget,distance),x=unit.pos.x+dx/distance*step,z=unit.pos.z+dz/distance*step;if(!stSegmentClear(context,unit.pos,{x,z},radius)){unit.path=[];unit.repathAt=0;break;}unit.pos.x=x;unit.pos.z=z;unit.actor.rotation.y=Math.atan2(dx,dz);budget-=step;moved=true;if(step>=distance-1e-6)unit.path.shift();}stPlaceUnit(unit);return moved;
}
function stBuildingConfig(kind,rules=stSession?.rules||{}){const base=ST_BUILDINGS[kind];if(!base)return null;const hpKey={'st-farm':'farmHp','st-income':'incomeHp','st-fort':'fortHp','st-wall':'wallHp','st-ramp':'rampHp'}[kind],costKey={'st-wall':'wallCost','st-ramp':'rampCost'}[kind];return {...base,hp:rules[hpKey]??base.hp,cost:rules[costKey]??base.cost};}
function stCanBuild(kind,x,z,ownerId=null,rotation=0){
  kind=stBuildKind(kind);const s=stSession,config=stBuildingConfig(kind),snap=s?.rules.buildSnap??.15,snappedX=Math.round(Number(x)/snap)*snap,snappedZ=Math.round(Number(z)/snap)*snap,angle=Math.round((Number(rotation)||0)/(Math.PI/2))*Math.PI/2,footprint=stFootprint(snappedX,snappedZ,1.2,config?.length?3:1.2,angle),warnings=[];
  const extra={kind,x:snappedX,z:snappedZ,rotation:angle,cost:config?.cost??0,...footprint,warnings};if(!s)return stResult(false,'Start Play before building.',extra);if(!config||config.conversionOnly)return stResult(false,'Choose an allowed house, wall or ramp.',extra);
  if(!Number.isFinite(snappedX)||!Number.isFinite(snappedZ))return stResult(false,'Choose a place on the meadow.',extra);
  const owner=s.units.find(u=>u.id===(ownerId||s.controlledId));if(!owner||owner.kind!=='sheep'||owner.captured||owner.isIllusion)return stResult(false,'Only a living sheep can build.',extra);if(s.winner)return stResult(false,'Restart the round to build again.',extra);
  if((kind==='st-wall'||kind==='st-ramp')&&!s.rules.elevated)return stResult(false,'Enable raised routes in Archive rules to build this.',extra);if(s.rules.permittedStructures&&!s.rules.permittedStructures.includes(kind))return stResult(false,'This map does not permit this structure.',extra);
  if(footprint.corners.some(p=>Math.abs(p[0])>s.rules.bounds||Math.abs(p[1])>s.rules.bounds))return stResult(false,'The structure must fit inside the meadow.',extra);
  if(stRectsOverlap(footprint,stFootprint(s.pen.x,s.pen.z,s.pen.reserveX,s.pen.reserveZ)))return stResult(false,'Keep the spirit pen and its entrances clear.',extra);
  for(const zone of s.noBuildZones)if(stRectsOverlap(footprint,zone))return stResult(false,'This area is marked as a no-build zone.',extra);
  if(s.buildings.filter(b=>b.owner===owner.id&&b.hp>0).length>=(s.rules.houseLimit??28))return stResult(false,'Your structure limit is '+(s.rules.houseLimit??28)+'.',extra);if(s.buildings.filter(b=>b.hp>0).length>=Math.max(112,s.units.length*(s.rules.houseLimit??28)))return stResult(false,'The meadow has reached its structure limit.',extra);
  if((s.resources[owner.id]||0)<config.cost)return stResult(false,'Need '+config.cost+' gold for '+config.name+'.',extra);
  for(const obstacle of s.obstacles){if(kind==='st-wall'&&obstacle.kind==='st-pond')continue;const overlaps=obstacle.radius!==undefined?stIntersectsObstacle(obstacle.x,obstacle.z,obstacle.radius,footprint):stRectsOverlap(footprint,obstacle);if(overlaps)return stResult(false,'Choose clear ground away from trees, rocks and water.',extra);}
  for(const b of s.buildings)if(b.hp>0){const bridges=kind==='st-wall'&&!['st-wall','st-ramp'].includes(b.kind);if(!bridges&&stRectsOverlap(footprint,stBuildingObstacle(b)))return stResult(false,'A structure already occupies that space.',extra);const gap=Math.max(Math.abs(snappedX-b.pos.x)-footprint.halfX-b.halfX,Math.abs(snappedZ-b.pos.z)-footprint.halfZ-b.halfZ);if(gap>=0&&gap<stUnitRadius('sheep')*2)warnings.push('A gap here is too tight for a sheep. You may seal your own exit.');}
  for(const u of s.units)if(!u.captured&&!u.isIllusion&&!(kind==='st-wall'&&stEntityHeight(u)<(s.rules.wallHeight??3.3)-1.2)&&stIntersectsObstacle(u.pos.x,u.pos.z,stUnitRadius(u),footprint))return stResult(false,'A unit is standing in this footprint.',extra);
  if(kind==='st-ramp'){const entry=stRampEntry(footprint,stUnitRadius(owner));if(stBlocked(entry.x,entry.z,stUnitRadius(owner))||!stPath(owner.pos,entry,stUnitRadius(owner)))return stResult(false,'The lower ramp entrance needs a reachable ground path.',extra);}
  return stResult(true,'',{...extra,warnings:[...new Set(warnings)]});
}
function stRampEntry(footprint,radius){const c=Math.cos(footprint.rotation||0),sn=Math.sin(footprint.rotation||0),d=(footprint.localHalfZ??3)+radius+.15;return new THREE.Vector3(footprint.x+sn*d,0,footprint.z+c*d);}
function stNewBuilding(kind,x,z,owner,authored=null,rotation=0){
  const s=stSession,config=stBuildingConfig(kind),mesh=authored||stMakeVisual(kind),pos=new THREE.Vector3(x,terrainHeight(x,z),z),fp=authored?stActorFootprint(authored,1.2,config.length?3:1.2):stFootprint(x,z,1.2,config.length?3:1.2,rotation);
  if(!authored){mesh.position.copy(pos);mesh.rotation.y=rotation;if(kind==='st-wall'||kind==='st-ramp')mesh.scale.y=(s.rules.wallHeight??3.3)/3.3;scene.add(mesh);}const building={id:authored?.userData.id||'st-runtime-building-'+(++s.serial),kind,pos,...fp,owner,hp:config.hp,maxHp:config.hp,progress:authored?1:0,level:1,mesh,authored:!!authored,income:config.income,cost:config.cost,buildTime:config.time,attackFlash:0,damageAt:-1,baseScale:mesh.scale.clone()};building.id=authored?.userData.id||'st-runtime-building-'+s.serial;
  const materials=new Set();mesh.traverse(node=>{for(const material of Array.isArray(node.material)?node.material:[node.material])if(material?.color)materials.add(material);});building.colors=[...materials].map(material=>({material,color:material.color.clone()}));s.buildings.push(building);stInvalidateNavigation();return building;
}
function stDisposeVisual(object){if(!object)return;object.removeFromParent();const geometries=new Set(),materials=new Set();object.traverse(node=>{if(node.geometry)geometries.add(node.geometry);for(const m of Array.isArray(node.material)?node.material:[node.material])if(m)materials.add(m);});geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());}
function stRemoveBuilding(building){if(building.hp<=0)return;if(typeof stArchiveBuildingRemoved==='function')stArchiveBuildingRemoved(building);building.hp=0;if(building.authored)building.mesh.visible=false;else stDisposeVisual(building.mesh);stInvalidateNavigation();}
function stCapture(unit,wolf=null){
  const s=stSession;if(unit.captured||unit.kind!=='sheep')return;if(typeof stArchiveCapture==='function'&&stArchiveCapture(unit,wolf))return;
  unit.captured=true;unit.actor.visible=false;stSetOrder(unit,null);for(const b of s.buildings)if(b.owner===unit.id&&b.hp>0)stRemoveBuilding(b);
  unit.spirit=stMakeSpirit();const flock=s.units.filter(u=>u.kind==='sheep'&&!u.isIllusion),index=flock.indexOf(unit),angle=index*Math.PI*2/Math.max(1,flock.length);unit.spirit.position.set(s.pen.x+Math.cos(angle)*Math.min(2.3,s.pen.halfX-.8),terrainHeight(s.pen.x,s.pen.z),s.pen.z+Math.sin(angle)*Math.min(2.3,s.pen.halfZ-.8));scene.add(unit.spirit);unit.spiritOrder=null;unit.rescueBy=Object.create(null);unit.captureAt=s.elapsed;if(wolf)s.resources[wolf.id]=(s.resources[wolf.id]||0)+60;
  if(stSeenByRole(unit)||unit.id===s.controlledId)s.message=unit.name+' was tagged. Reach their glowing spirit to rescue them.';
}
function stRescue(unit,rescuer){
  const s=stSession;if(!unit.captured||!rescuer||rescuer.captured||rescuer.kind!=='sheep'||rescuer.isIllusion)return false;
  const origin=unit.spirit.position.clone();stDisposeVisual(unit.spirit);unit.spirit=null;unit.spiritOrder=null;unit.captured=false;unit.actor.visible=true;unit.invulnerableUntil=s.elapsed+(s.rules.rescueProtection??3);unit.lastRescuerId=rescuer.id;
  const radius=stUnitRadius(unit),candidates=[origin,new THREE.Vector3(origin.x+.75,0,origin.z+.75),new THREE.Vector3(origin.x-.75,0,origin.z-.75)],position=candidates.find(p=>!stBlocked(p.x,p.z,radius))||origin;unit.pos.copy(position);unit.archiveOnUpper=false;unit.archiveHeight=undefined;stPlaceUnit(unit);stSetOrder(unit,null);unit.botAt=s.elapsed+.6;s.resources[unit.id]=Math.max(s.resources[unit.id]||0,30);s.message=rescuer.name+' rescued '+unit.name+'! '+(s.rules.rescueProtection??3)+' seconds of protection.';if(typeof stArchiveRescue==='function')stArchiveRescue(unit,rescuer);return true;
}
function stBuildingDistance(unit,b){const [x,z]=stLocalPoint(unit.pos.x,unit.pos.z,stBuildingObstacle(b));return Math.hypot(Math.max(0,Math.abs(x)-b.localHalfX),Math.max(0,Math.abs(z)-b.localHalfZ));}
function stAttackApproach(unit,b){
  if(unit.attackApproach?.id===b.id&&unit.attackApproach.version===stSession.navVersion&&unit.attackApproach.from.distanceToSquared(unit.pos)<16)return unit.attackApproach.pos.clone();
  const radius=stUnitRadius(unit),fp=stBuildingObstacle(b),c=Math.cos(fp.rotation),sn=Math.sin(fp.rotation),candidates=[];
  for(let i=0;i<12;i++){const a=i*Math.PI/6,dx=Math.cos(a),dz=Math.sin(a),d=Math.min(Math.abs((fp.localHalfX+radius+.06)/(dx||1e-8)),Math.abs((fp.localHalfZ+radius+.06)/(dz||1e-8))),lx=dx*d,lz=dz*d,p=new THREE.Vector3(fp.x+lx*c+lz*sn,0,fp.z-lx*sn+lz*c);if(!stBlocked(p.x,p.z,radius))candidates.push(p);}
  candidates.sort((a,b)=>a.distanceToSquared(unit.pos)-b.distanceToSquared(unit.pos));for(const p of candidates)if(unit.archiveOnUpper||stPath(unit.pos,p,radius)){unit.attackApproach={id:b.id,version:stSession.navVersion,from:unit.pos.clone(),pos:p.clone()};return p;}return null;
}
function stAttackBuilding(wolf,b){
  const s=stSession;if(s.elapsed<wolf.attackAt||b.hp<=0)return;wolf.attackAt=s.elapsed+(s.rules.attackInterval??.65);wolf.attackTarget=b.id;wolf.actor.rotation.y=Math.atan2(b.pos.x-wolf.pos.x,b.pos.z-wolf.pos.z);
  const damage=wolf.damage*(s.archive?.damageMultiplier??1);b.hp=Math.max(0,b.hp-damage);b.attackFlash=.24;b.damageAt=s.elapsed;s.attacks.push({id:'hit-'+(++s.serial),attackerId:wolf.id,buildingId:b.id,pos:b.pos.toArray(),at:s.elapsed,damage,remainingHp:b.hp});
  if(stSeenByRole(b))s.message=wolf.name+' struck '+ST_BUILDINGS[b.kind].name+' for '+Math.round(damage)+' ('+Math.ceil(b.hp)+' HP left).';
  if(b.hp<=0){const bounty=b.kind==='st-farm'?10:b.kind==='st-income'?20:35;s.resources[wolf.id]=(s.resources[wolf.id]||0)+bounty;b.hp=1;stRemoveBuilding(b);if(stSeenByRole(b))s.message=wolf.name+' broke a '+ST_BUILDINGS[b.kind].name+' and earned '+bounty+' gold.';}
}
function stBuildApproach(unit,x,z,kind='st-farm',rotation=0){
  const fp=stFootprint(x,z,1.2,ST_BUILDINGS[kind]?.length?3:1.2,rotation),radius=stUnitRadius(unit),c=Math.cos(rotation),sn=Math.sin(rotation),candidates=[];
  for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]]){const lx=dx*(fp.localHalfX+radius+.08),lz=dz*(fp.localHalfZ+radius+.08),p=new THREE.Vector3(x+lx*c+lz*sn,0,z-lx*sn+lz*c);if(!stBlocked(p.x,p.z,radius))candidates.push(p);}candidates.sort((a,b)=>a.distanceToSquared(unit.pos)-b.distanceToSquared(unit.pos));for(const p of candidates)if(stPath(unit.pos,p,radius))return p;return null;
}
function stIssueBuild(unit,kind,x,z,rotation=0){const result=stCanBuild(kind,x,z,unit.id,rotation);if(!result.ok)return result;const approach=stBuildApproach(unit,result.x,result.z,result.kind,result.rotation);if(!approach)return stResult(false,'Your sheep cannot reach that building site.',result);unit.archiveRoute=null;stSetOrder(unit,{action:'build',kind:result.kind,siteX:result.x,siteZ:result.z,rotation:result.rotation,x:approach.x,z:approach.z});return result;}
function stUpdateSheep(unit,dt){
  const s=stSession;if(unit.captured){if(unit.spiritOrder){const p=unit.spirit.position,t=unit.spiritOrder,dx=t.x-p.x,dz=t.z-p.z,d=Math.hypot(dx,dz),step=Math.min(d,3.5*dt);if(d>.01){p.x+=dx/d*step;p.z+=dz/d*step;}else unit.spiritOrder=null;}stAnimateSpirit(unit.spirit,s.elapsed,unit.phase);return;}
  if(unit.isIllusion)return;const order=unit.order,target=stOrderTarget(unit);if(order&&target)stMoveUnit(unit,target,dt);
  if(order?.action==='build'&&target&&Math.hypot(unit.pos.x-target.x,unit.pos.z-target.z)<.42){const valid=stCanBuild(order.kind,order.siteX,order.siteZ,unit.id,order.rotation);if(valid.ok){s.resources[unit.id]-=valid.cost;stNewBuilding(valid.kind,valid.x,valid.z,unit.id,null,valid.rotation);if(unit.id===s.controlledId)s.message=unit.name+' is building a '+ST_BUILDINGS[valid.kind].name+'.';}else if(unit.id===s.controlledId)s.message=valid.reason;stSetOrder(unit,null);}else if(order?.action==='move'&&target&&!unit.archiveOnUpper&&Math.hypot(unit.pos.x-target.x,unit.pos.z-target.z)<.22)stSetOrder(unit,null);
  for(const captive of s.units)if(captive.captured&&s.elapsed>captive.captureAt+.6){const close=Math.hypot(unit.pos.x-captive.spirit.position.x,unit.pos.z-captive.spirit.position.z)<1.45&&Math.abs(stEntityHeight(unit)-captive.spirit.position.y)<1.2;captive.rescueBy=captive.rescueBy||Object.create(null);captive.rescueBy[unit.id]=close?(captive.rescueBy[unit.id]||0)+dt:0;if(captive.rescueBy[unit.id]>=(s.rules.rescueHold??.6))stRescue(captive,unit);}
}
function stUpdateWolf(unit,dt){
  const s=stSession;if(s.elapsed<s.rules.headstart)return;const order=unit.order,target=stOrderTarget(unit);if(order&&target)stMoveUnit(unit,target,dt);if(order?.action==='move'&&target&&!unit.archiveOnUpper&&Math.hypot(unit.pos.x-target.x,unit.pos.z-target.z)<.25)stSetOrder(unit,null);
  for(const sheep of s.units)if(sheep.kind==='sheep'&&!sheep.captured&&s.elapsed>=(sheep.invulnerableUntil||0)&&stPerceives(unit,sheep)&&Math.abs(stEntityHeight(unit)-stEntityHeight(sheep))<1.2&&Math.hypot(unit.pos.x-sheep.pos.x,unit.pos.z-sheep.pos.z)<stUnitRadius(unit)+stUnitRadius(sheep)+.1)stCapture(sheep,unit);
  if(order?.action==='attack'){const b=s.buildings.find(b=>b.id===order.id&&b.hp>0);if(b){if(stPerceives(unit,b)&&stBuildingDistance(unit,b)<=stUnitRadius(unit)+.36&&Math.abs(stEntityHeight(unit)-b.pos.y)<(b.kind==='st-wall'||b.kind==='st-ramp'?5:1.2))stAttackBuilding(unit,b);}else if(!s.units.some(u=>u.id===order.id&&!u.captured))stSetOrder(unit,null);else if(!target)stSetOrder(unit,null);}
}
function stBotKnownEnemies(unit){const s=stSession;for(const enemy of s.units)if(enemy.kind!==unit.kind&&!enemy.captured&&stPerceives(unit,enemy))stRemember(unit,enemy);return [...unit.memory.values()].filter(m=>s.elapsed-m.at<10);}
function stChooseBase(unit){
  const s=stSession,known=stBotKnownEnemies(unit),candidates=[unit.home.clone(),...s.buildings.filter(b=>b.hp>0&&s.units.some(u=>u.id===b.owner&&u.kind==='sheep')).slice(0,12).map(b=>b.pos.clone().add(new THREE.Vector3(4.5,0,4.5)))];let best=unit.home.clone(),score=-Infinity;
  for(const p of candidates){p.x=Math.round(p.x/.15)*.15;p.z=Math.round(p.z/.15)*.15;if(Math.abs(p.x)>s.rules.bounds-8||Math.abs(p.z)>s.rules.bounds-8||Math.abs(p.x-s.pen.x)<s.pen.reserveX+8&&Math.abs(p.z-s.pen.z)<s.pen.reserveZ+8||stBlocked(p.x,p.z,stUnitRadius(unit)))continue;const safety=known.length?Math.min(...known.map(e=>p.distanceToSquared(e.pos))):200,value=safety-unit.pos.distanceToSquared(p)*.3;if(value>score&&stPath(unit.pos,p,stUnitRadius(unit))){score=value;best=p;}}return best;
}
function stBotSheep(unit){
  const s=stSession;if(unit.captured||unit.isIllusion||unit.archiveRoute||s.elapsed<unit.botAt)return;unit.botAt=s.elapsed+1.1;const known=stBotKnownEnemies(unit),near=known.sort((a,b)=>a.pos.distanceToSquared(unit.pos)-b.pos.distanceToSquared(unit.pos))[0],danger=s.elapsed>=s.rules.headstart&&near&&near.pos.distanceToSquared(unit.pos)<121;
  if(danger){let best=null,score=-Infinity;const candidates=Array.from({length:12},(_,i)=>new THREE.Vector3(unit.pos.x+Math.cos(i*Math.PI/6)*6,0,unit.pos.z+Math.sin(i*Math.PI/6)*6));if(unit.base)candidates.unshift(unit.base.clone());for(const p of candidates){if(stBlocked(p.x,p.z,stUnitRadius(unit)))continue;const route=stPath(unit.pos,p,stUnitRadius(unit));if(!route)continue;const safety=Math.min(...known.map(w=>p.distanceToSquared(w.pos))),wolfPath=stPath(near.pos,p,stUnitRadius('wolf')),defence=wolfPath?0:180,value=safety+defence-route.length*.07;if(value>score){score=value;best=p;}}if(best){unit.aiIntent='evade through a sheep-sized exit';stSetOrder(unit,{action:'move',x:best.x,z:best.z});}return;}
  const captive=s.units.filter(u=>u.captured&&!u.isIllusion).sort((a,b)=>a.spirit.position.distanceToSquared(unit.pos)-b.spirit.position.distanceToSquared(unit.pos))[0];
  if(captive){const target=captive.spirit.position,risk=known.some(w=>w.pos.distanceToSquared(target)<100);if(!risk&&stPath(unit.pos,target,stUnitRadius(unit))){stSetOrder(unit,{action:'rescue',id:captive.id});return;}}
  if(unit.order)return;if(!unit.base)unit.base=stChooseBase(unit);
  if(s.elapsed>=unit.nextBuildAt){unit.nextBuildAt=s.elapsed+5+unit.phase*.25;const owned=s.buildings.filter(b=>b.owner===unit.id&&b.hp>0);if(owned.length<Math.min(12,s.rules.houseLimit??28)){
    const kind=!owned.some(b=>b.kind==='st-income')&&(s.resources[unit.id]||0)>=60?'st-income':(s.resources[unit.id]||0)>150&&owned.length%4===3?'st-fort':'st-farm';
    // A compact ring leaves 0.6-unit sheep lanes between 2.4-unit houses.
    // Bots check a remaining ground exit; player placement remains unrestricted.
    const offsets=[[-3,-3],[0,-3],[3,-3],[-3,0],[3,0],[-3,3],[0,3],[3,3],[-3,6],[3,6],[0,9],[-6,0]];
    for(let j=0;j<offsets.length;j++){const [dx,dz]=offsets[(j+unit.botIndex)%offsets.length],x=unit.base.x+dx,z=unit.base.z+dz,result=stCanBuild(kind,x,z,unit.id);if(!result.ok)continue;const proposed={rules:s.rules,obstacles:[...stObstacles(),stFootprint(result.x,result.z,1.2,1.2)]},nav=stBuildNavigation(proposed,stUnitRadius(unit)),exits=[new THREE.Vector3(unit.base.x,0,unit.base.z+7.5),new THREE.Vector3(unit.base.x+7.5,0,unit.base.z)];if(!exits.some(p=>stFindPath(nav,unit.pos,p)))continue;if(stIssueBuild(unit,kind,x,z).ok){unit.aiIntent='build a compact maze with a viable sheep exit';return;}}
  }}if(s.elapsed>=unit.nextWanderAt){unit.nextWanderAt=s.elapsed+7;const p=unit.base.clone();if(!stBlocked(p.x,p.z,stUnitRadius(unit)))stSetOrder(unit,{action:'move',x:p.x,z:p.z});}
}
function stBotWolf(unit){
  const s=stSession;if(s.elapsed<s.rules.headstart||unit.archiveRoute||s.elapsed<unit.botAt)return;unit.botAt=s.elapsed+1;const known=stBotKnownEnemies(unit),visible=s.units.filter(u=>u.kind==='sheep'&&!u.captured&&stPerceives(unit,u));visible.sort((a,b)=>a.pos.distanceToSquared(unit.pos)-b.pos.distanceToSquared(unit.pos));
  const current=s.buildings.find(b=>b.id===unit.order?.id&&b.hp>0);if(current&&stPerceives(unit,current)&&stBuildingDistance(unit,current)<2)return;
  const target=visible[unit.botIndex%Math.min(2,visible.length)]||visible[0];
  if(target){if(stPath(unit.pos,target.pos,stUnitRadius(unit))){unit.aiIntent='predict an observed sheep route';stSetOrder(unit,{action:'attack',id:target.id});return;}
    const buildings=s.buildings.filter(b=>b.hp>0&&stPerceives(unit,b)).sort((a,b)=>(a.pos.distanceToSquared(unit.pos)+a.pos.distanceToSquared(target.pos)*.6+(a.kind==='st-totem'?-35:0)+a.hp*.03)-(b.pos.distanceToSquared(unit.pos)+b.pos.distanceToSquared(target.pos)*.6+(b.kind==='st-totem'?-35:0)+b.hp*.03));
    for(const b of buildings)if(stAttackApproach(unit,b)){unit.aiIntent='demolish an observed blocker to open a breach';stSetOrder(unit,{action:'attack',id:b.id});return;}
  }
  // Pen guards choose a public landmark, rather than unseen rescuers' coordinates.
  if(s.units.some(u=>u.captured)&&unit.botIndex%3===2){const a=s.elapsed*.12+unit.phase,p=new THREE.Vector3(s.pen.x+Math.cos(a)*(s.pen.halfX+2),0,s.pen.z+Math.sin(a)*(s.pen.halfZ+2));if(stPath(unit.pos,p,stUnitRadius(unit))){unit.aiIntent='guard the public spirit pen';stSetOrder(unit,{action:'move',x:p.x,z:p.z});return;}}
  const clue=(s.archive?.scentClues||[]).filter(c=>c.expires>s.elapsed).sort((a,b)=>(a.x-unit.pos.x)**2+(a.z-unit.pos.z)**2-((b.x-unit.pos.x)**2+(b.z-unit.pos.z)**2))[0];
  const memory=known.sort((a,b)=>b.at-a.at)[0],search=clue?new THREE.Vector3(clue.x,0,clue.z):memory?.pos;
  if(search&&unit.pos.distanceToSquared(search)>1&&stPath(unit.pos,search,stUnitRadius(unit))){unit.aiIntent=clue?'investigate an approximate scent clue':'search a last-observed location';stSetOrder(unit,{action:'move',x:search.x,z:search.z});return;}
  const angle=s.elapsed*.045+unit.botIndex*Math.PI*2/Math.max(1,s.units.filter(u=>u.kind==='wolf').length),distance=s.rules.bounds*.58,p=new THREE.Vector3(Math.cos(angle)*distance,0,Math.sin(angle)*distance);if(stPath(unit.pos,p,stUnitRadius(unit))){unit.aiIntent='patrol for new sightings';stSetOrder(unit,{action:'move',x:p.x,z:p.z});}
}
function stCreateFog(s){
  if(s.simulate||s.rules.fogMode==='off'||typeof document==='undefined')return;const canvas=document.createElement('canvas'),width=Math.ceil(s.rules.bounds*2/2);canvas.width=canvas.height=width;const texture=new THREE.CanvasTexture(canvas);texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestFilter;const material=new THREE.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false,side:THREE.DoubleSide}),mesh=new THREE.Mesh(new THREE.PlaneGeometry(s.rules.bounds*2,s.rules.bounds*2),material);mesh.rotation.x=-Math.PI/2;mesh.position.y=.055;mesh.renderOrder=3;scene.add(mesh);s.fog={canvas,texture,material,mesh,width,cellSize:2,extent:s.rules.bounds,visible:new Uint8Array(width*width),explored:new Uint8Array(width*width),updateAt:-1};
}
function stUpdateVision(s,force=false){
  for(const unit of s.units){if(!unit.memory)unit.memory=new Map();if(!unit.isIllusion)for(const target of s.units)if(unit.kind!==target.kind&&!target.captured&&stPerceives(unit,target))stRemember(unit,target);unit.actor.visible=!unit.captured&&stSeenByRole(unit);if(unit.spirit)unit.spirit.visible=stSeenByRole(unit);}
  for(const b of s.buildings)if(b.hp>0)b.mesh.visible=stSeenByRole(b);
  const entities=[...s.units.filter(u=>!u.captured),...s.buildings.filter(b=>b.hp>0)];for(const entity of entities)if(stSeenByRole(entity))s.viewMemory.set(entity.id,{id:entity.id,kind:entity.kind,name:entity.name||ST_BUILDINGS[entity.kind]?.name,pos:entity.pos.toArray(),seenAt:s.elapsed});
  if(!s.fog||!force&&s.elapsed<s.fog.updateAt)return;const f=s.fog;f.updateAt=s.elapsed+.35;f.visible.fill(0);let viewers=s.units.filter(u=>u.kind===s.role&&!u.captured&&!u.isIllusion);if(s.rules.fogMode==='solo')viewers=viewers.filter(u=>u.id===s.controlledId);const range=(s.role==='wolf'?s.rules.wolfVision:s.rules.sheepVision)*(s.archive?.visionMultiplier??1);
  for(const unit of viewers){const minX=Math.max(0,Math.floor((unit.pos.x-range+f.extent)/f.cellSize)),maxX=Math.min(f.width-1,Math.ceil((unit.pos.x+range+f.extent)/f.cellSize)),minZ=Math.max(0,Math.floor((unit.pos.z-range+f.extent)/f.cellSize)),maxZ=Math.min(f.width-1,Math.ceil((unit.pos.z+range+f.extent)/f.cellSize));for(let z=minZ;z<=maxZ;z++)for(let x=minX;x<=maxX;x++)if(Math.hypot((x+.5)*f.cellSize-f.extent-unit.pos.x,(z+.5)*f.cellSize-f.extent-unit.pos.z)<=range){const id=z*f.width+x;f.visible[id]=f.explored[id]=1;}}
  const ctx=f.canvas.getContext('2d'),data=ctx.createImageData(f.width,f.width);for(let i=0;i<f.visible.length;i++){data.data[i*4]=10;data.data[i*4+1]=21;data.data[i*4+2]=30;data.data[i*4+3]=f.visible[i]?0:f.explored[i]?80:165;}ctx.putImageData(data,0,0);f.texture.needsUpdate=true;
}
function stStart(simulate=false){
  if(stSession)stStop();const rules={...stRules()},baseline=new Map();for(const actor of actors){const children=[];actor.traverse(node=>{if(/^stLeg|^stHead$|^stTail$/.test(node.name))children.push({node,rotation:node.rotation.clone()});});baseline.set(actor,{position:actor.position.clone(),rotation:actor.rotation.clone(),scale:actor.scale.clone(),visible:actor.visible,children});}
  const penActor=actors.find(a=>a.userData.actorType==='st-pen'&&a.userData.baked!==false&&walkingObjectVisible(a)),penPosition=penActor?stWorldPosition(penActor):new THREE.Vector3(),penScale=new THREE.Vector3(1,1,1);if(penActor)penActor.getWorldScale(penScale);const pen={x:penPosition.x,z:penPosition.z,halfX:Math.max(1,Math.abs(penScale.x)*5),halfZ:Math.max(1,Math.abs(penScale.z)*5),reserveX:Math.abs(penScale.x)*7,reserveZ:Math.abs(penScale.z)*7};
  const s={rules,baseline,pen,shops:[],simulate:!!simulate,role:rules.role==='wolf'?'wolf':'sheep',elapsed:0,winner:null,message:'Build a maze during the head start. Keep exits open, or risk trapping yourself.',selectedId:null,controlledId:null,resources:Object.create(null),units:[],buildings:[],obstacles:[],noBuildZones:[],serial:0,navVersion:0,navigation:new Map(),viewMemory:new Map(),incomeClock:0,attacks:[]};stSession=s;let sheepIndex=0,wolfIndex=0;
  for(const actor of actors){const kind=actor.userData.actorType;if(actor.userData.baked===false||!walkingObjectVisible(actor))continue;
    if(kind==='st-sheep'||kind==='st-wolf'){const pos=stWorldPosition(actor),sheep=kind==='st-sheep',index=sheep?sheepIndex++:wolfIndex++,unit={id:actor.userData.id,name:actor.name,kind:sheep?'sheep':'wolf',actor,pos,home:pos.clone(),captured:false,spirit:null,spiritOrder:null,order:null,destination:null,path:[],pathVersion:-1,pathTarget:null,repathAt:0,botAt:sheep?2:index*.4,nextBuildAt:2+index*1.1,nextWanderAt:5+index,botIndex:index,phase:index*.93,speed:sheep?rules.sheepSpeed:rules.wolfSpeed,damage:rules.wolfDamage,level:1,attackAt:0,invulnerableUntil:0,captureAt:0,walkDistance:0,walkBlend:0,pivots:baseline.get(actor).children,memory:new Map(),velocity:new THREE.Vector3()};s.units.push(unit);s.resources[unit.id]=sheep?rules.startGold:0;
    }else if(ST_BUILDINGS[kind]){const p=stWorldPosition(actor);stNewBuilding(kind,p.x,p.z,actor.userData.stOwner||null,actor);}
    else{const obstacle=stStaticObstacle(actor);if(obstacle)s.obstacles.push(obstacle);if(kind==='st-shop')s.shops.push({id:actor.userData.id,pos:stWorldPosition(actor)});if(kind==='st-zone'){s.noBuildZones.push(stActorFootprint(actor,3,3));actor.visible=false;}}
  }
  for(const building of s.buildings)if(!building.owner){const sheep=s.units.filter(u=>u.kind==='sheep').sort((a,b)=>a.pos.distanceToSquared(building.pos)-b.pos.distanceToSquared(building.pos))[0];building.owner=sheep?.id||null;}
  const controlled=s.units.find(u=>u.kind===s.role);s.controlledId=simulate?null:controlled?.id||null;s.selectedId=controlled?.id||s.units[0]?.id||null;stInvalidateNavigation();if(typeof stArchiveStart==='function')stArchiveStart(s);stCreateFog(s);stUpdateVision(s,true);return stResult(true,'',stStatus());
}
function stStop(){
  const s=stSession;if(!s)return false;if(typeof stArchiveStop==='function')stArchiveStop(s);for(const unit of s.units)if(unit.spirit)stDisposeVisual(unit.spirit);for(const b of s.buildings){if(!b.authored&&b.hp>0)stDisposeVisual(b.mesh);if(b.authored)for(const e of b.colors)e.material.color.copy(e.color);}if(s.fog){stDisposeVisual(s.fog.mesh);s.fog.texture.dispose();}
  for(const [actor,state] of s.baseline){actor.position.copy(state.position);actor.rotation.copy(state.rotation);actor.scale.copy(state.scale);actor.visible=state.visible;for(const child of state.children)child.node.rotation.copy(child.rotation);}s.navigation.clear();stSession=null;return true;
}
function stUpdate(dt,t){
  const s=stSession;if(!s||paused||s.winner)return;dt=Math.max(0,Math.min(Number(dt)||0,.05));s.elapsed=Math.min(s.rules.duration,s.elapsed+dt);s.incomeClock+=dt;if(typeof stArchiveBeforeUpdate==='function')stArchiveBeforeUpdate(s,dt,t);
  while(s.incomeClock>=1){s.incomeClock--;for(const u of s.units)if(u.kind==='sheep'&&!u.captured&&!u.isIllusion)s.resources[u.id]=(s.resources[u.id]||0)+1+s.buildings.filter(b=>b.owner===u.id&&b.hp>0&&b.progress>=1).reduce((n,b)=>n+b.income,0);}
  for(const b of s.buildings)if(b.hp>0){b.progress=Math.min(1,b.progress+dt/b.buildTime);b.attackFlash=Math.max(0,b.attackFlash-dt);if(!b.authored)b.mesh.scale.y=b.baseScale.y*(.15+.85*b.progress);for(const e of b.colors){e.material.color.copy(e.color);if(b.attackFlash>0)e.material.color.lerp(new THREE.Color('#ff6653'),b.attackFlash/.24*.8);}}
  for(const unit of [...s.units]){const before=unit.pos.clone();if(unit.id!==s.controlledId&&!unit.isIllusion){if(unit.kind==='sheep')stBotSheep(unit);else stBotWolf(unit);}if(unit.kind==='sheep')stUpdateSheep(unit,dt);else stUpdateWolf(unit,dt);if(!unit.isIllusion)unit.velocity=unit.pos.clone().sub(before).multiplyScalar(dt?1/dt:0);const distance=unit.isIllusion?Math.max(0,unit.archiveMovedDistance||0):Math.hypot(unit.pos.x-before.x,unit.pos.z-before.z);unit.archiveMovedDistance=0;unit.walkDistance=(unit.walkDistance||0)+distance;unit.walkBlend=(unit.walkBlend||0)+(Number(distance>.002)-(unit.walkBlend||0))*Math.min(1,dt*10);
    for(const pivot of unit.pivots||[]){pivot.node.rotation.copy(pivot.rotation);if(/^stLeg/.test(pivot.node.name)){const i=Number(pivot.node.name.slice(5))||0;pivot.node.rotation.x+=Math.sin(unit.walkDistance*9+(i===0||i===3?0:Math.PI))*.58*unit.walkBlend;}else if(pivot.node.name==='stTail')pivot.node.rotation.y+=Math.sin(s.elapsed*3+unit.phase)*.18;else if(pivot.node.name==='stHead'&&unit.kind==='wolf'&&unit.attackAt>s.elapsed)pivot.node.rotation.x+=Math.sin((unit.attackAt-s.elapsed)*Math.PI/(s.rules.attackInterval??.65))*.38;}}
  if(typeof stArchiveAfterUpdate==='function')stArchiveAfterUpdate(s,dt,t);stUpdateVision(s);s.attacks=s.attacks.filter(a=>s.elapsed-a.at<1.4);const flock=s.units.filter(u=>u.kind==='sheep'&&!u.isIllusion);if(flock.length&&flock.every(u=>u.captured)){s.winner='wolves';s.message='The wolves tagged the whole flock. Wolves win!';}else if(s.elapsed>=s.rules.duration){s.winner='sheep';s.message='The flock survived until the timer ended. Sheep win!';}
}
function stStatus(){
  const s=stSession;if(!s)return {active:false,units:[],buildings:[],resources:{},selectedId:null,controlledId:null};const flock=s.units.filter(u=>u.kind==='sheep'&&!u.isIllusion),controlled=s.units.find(u=>u.id===s.controlledId),magic=typeof stArchivePublicStatus==='function'?stArchivePublicStatus(s,controlled):{};
  return {active:true,role:s.role,simulate:s.simulate,elapsed:s.elapsed,remaining:Math.max(0,s.rules.duration-s.elapsed),headstartRemaining:Math.max(0,s.rules.headstart-s.elapsed),winner:s.winner,message:s.message,selectedId:s.selectedId,controlledId:s.controlledId,gold:s.resources[s.controlledId]??0,pen:{...s.pen},shops:s.shops.map(shop=>({id:shop.id,pos:shop.pos.toArray()})),resources:{...s.resources},rules:{...s.rules},counts:{sheep:flock.length,totalSheep:flock.length,livingSheep:flock.filter(u=>!u.captured).length,capturedSheep:flock.filter(u=>u.captured).length,wolves:s.units.filter(u=>u.kind==='wolf').length},attacks:s.attacks.map(a=>({...a})),...magic,
    units:s.units.map(u=>({id:u.id,kind:u.captured?'wisp':u.kind,name:u.name,pos:(u.spirit?.position||u.pos).toArray(),captured:u.captured,controlled:u.id===s.controlledId,order:u.order?{...u.order}:u.spiritOrder?{action:'move',...u.spiritOrder}:null,level:u.level,speed:u.speed,damage:u.damage,upgradeCost:u.kind==='wolf'&&u.level<3?u.level*75:null,isIllusion:!!u.isIllusion,ai:{intent:u.aiIntent||'',base:u.base?.toArray()||null,lastKnown:[...(u.memory?.values()||[])].map(m=>({id:m.id,pos:m.pos.toArray(),seenAt:m.at}))},concealment:u.concealAmount||0,onUpper:!!u.archiveOnUpper,scentUntil:u.archiveScentUntil||0,progression:typeof stArchiveStatus==='function'?stArchiveStatus(u):null})),
    buildings:s.buildings.filter(b=>b.hp>0).map(b=>({id:b.id,kind:b.kind,name:ST_BUILDINGS[b.kind].name,pos:b.pos.toArray(),halfX:b.halfX,halfZ:b.halfZ,localHalfX:b.localHalfX,localHalfZ:b.localHalfZ,rotation:b.rotation,corners:b.corners,hp:b.hp,maxHp:b.maxHp,progress:b.progress,owner:b.owner,level:b.level,income:b.income,cost:b.cost,damageAt:b.damageAt,upgradeCost:b.level<3?b.level*50:null}))};
}
function stViewStatus(){
  const s=stSession,status=stStatus();if(!s||s.simulate)return status;const visibleIds=new Set(s.units.filter(u=>stSeenByRole(u)).map(u=>u.id)),buildingIds=new Set(s.buildings.filter(b=>b.hp>0&&stSeenByRole(b)).map(b=>b.id));
  status.units=status.units.filter(u=>visibleIds.has(u.id)).map(u=>{const source=s.units.find(v=>v.id===u.id),friendly=source.kind===s.role;const safe={...u};if(!friendly){delete safe.isIllusion;delete safe.ai;delete safe.progression;delete safe.scentUntil;safe.order=null;safe.name=source.kind==='sheep'?'Sheep':safe.name;}return safe;});status.buildings=status.buildings.filter(b=>buildingIds.has(b.id));status.resources=Object.fromEntries(Object.entries(status.resources).filter(([id])=>s.units.some(u=>u.id===id&&u.kind===s.role)));
  status.lastKnown=[...s.viewMemory.values()].filter(v=>!visibleIds.has(v.id)&&!buildingIds.has(v.id)&&s.elapsed-v.seenAt<25).map(v=>({...v,name:v.kind==='sheep'?'Sheep':v.name,lastKnown:true,pos:[...v.pos]}));status.attacks=status.attacks.filter(a=>buildingIds.has(a.buildingId));
  if(!visibleIds.has(status.selectedId)&&!buildingIds.has(status.selectedId))status.selectedId=s.controlledId;const f=s.fog;status.fog={mode:s.rules.fogMode,vision:(s.role==='wolf'?s.rules.wolfVision:s.rules.sheepVision)*(s.archive?.visionMultiplier??1),cellSize:f?.cellSize||2,width:f?.width||Math.ceil(s.rules.bounds),extent:s.rules.bounds,visible:f?Array.from(f.visible.keys()).filter(i=>f.visible[i]):[],explored:f?Array.from(f.explored.keys()).filter(i=>f.explored[i]):[]};return status;
}
function stCommand(action,payload={}){
  const s=stSession;if(!s)return stResult(false,'Start Play to control the flock.');
  if(action==='select'){const unit=s.units.find(u=>u.id===payload.id),b=s.buildings.find(b=>b.id===payload.id&&b.hp>0);if(!unit&&!b||!s.simulate&&!stSeenByRole(unit||b))return stResult(false,'That unit or structure is not currently visible.');s.selectedId=payload.id;return stResult(true);}
  if(action==='restart'){const simulate=s.simulate;stStop();return stStart(simulate);}if(action==='role'){if(!['sheep','wolf'].includes(payload.role))return stResult(false,'Choose sheep or wolf.');const unit=s.units.find(u=>u.kind===payload.role&&!u.isIllusion);if(!unit)return stResult(false,'This map has no '+payload.role+' spawn.');s.role=payload.role;s.controlledId=unit.id;s.selectedId=unit.id;s.simulate=false;stSetOrder(unit,null);if(s.fog){stDisposeVisual(s.fog.mesh);s.fog.texture.dispose();s.fog=null;}s.viewMemory.clear();stCreateFog(s);stUpdateVision(s,true);return stResult(true);}
  if(s.winner)return stResult(false,'The round has ended. Use Restart for another game.');if(paused)return stResult(false,'Resume the game before giving orders.');const unit=s.units.find(u=>u.id===s.controlledId);if(!unit)return stResult(false,'Simulate runs the bots. Use Play or choose a role to take control.');if(typeof stArchiveCommand==='function'){const handled=stArchiveCommand(action,payload,unit);if(handled!==null&&handled!==undefined)return handled;}
  if(action==='build-snap'){const value=Number(payload.value);if(![.15,3].includes(value))return stResult(false,'Choose precision or 3-unit placement.');s.rules.buildSnap=value;return stResult(true,'',{value});}
  if(action==='preview')return stCanBuild(payload.kind,payload.x,payload.z,unit.id,payload.rotation);
  if(action==='move'){if(s.selectedId!==unit.id)return stResult(false,'Select your '+(unit.captured?'wisp':unit.kind)+' to give orders.');const x=Number(payload.x),z=Number(payload.z);if(!Number.isFinite(x)||!Number.isFinite(z))return stResult(false,'Choose a destination on the meadow.');if(unit.captured){unit.spiritOrder={x:THREE.MathUtils.clamp(x,s.pen.x-s.pen.halfX+.8,s.pen.x+s.pen.halfX-.8),z:THREE.MathUtils.clamp(z,s.pen.z-s.pen.halfZ+.8,s.pen.z+s.pen.halfZ-.8)};return stResult(true,'Wisps stay in the spirit pen until rescued.');}if(unit.kind==='wolf'&&s.elapsed<s.rules.headstart)return stResult(false,'The wolves are released after the head start.');const radius=stUnitRadius(unit);if(stBlocked(x,z,radius))return stResult(false,'Choose clear ground inside the meadow.');if(!stPath(unit.pos,new THREE.Vector3(x,0,z),radius))return stResult(false,'There is no open route to that destination.');unit.archiveRoute=null;stSetOrder(unit,{action:'move',x,z});return stResult(true);}
  if(action==='build'){if(s.selectedId!==unit.id)return stResult(false,'Select your sheep to build.');if(unit.kind!=='sheep'||unit.captured)return stResult(false,'Only a living sheep can build.');return stIssueBuild(unit,payload.kind,payload.x,payload.z,payload.rotation);}
  if(action==='attack'){if(unit.kind!=='wolf')return stResult(false,'Only wolves attack sheep and structures.');if(s.selectedId!==unit.id)return stResult(false,'Select your wolf to attack.');if(s.elapsed<s.rules.headstart)return stResult(false,'The wolves are released after the head start.');const b=s.buildings.find(b=>b.id===payload.id&&b.hp>0),sheep=s.units.find(u=>u.id===payload.id&&u.kind==='sheep'&&!u.captured),target=b||sheep;if(!target||!stSeenByRole(target))return stResult(false,'Choose a visible sheep or standing structure.');if(b&&!stAttackApproach(unit,b)&&stBuildingDistance(unit,b)>stUnitRadius(unit)+.36)return stResult(false,'No route reaches this structure. Break a closer obstruction first.');if(sheep)stRemember(unit,sheep);unit.archiveRoute=null;stSetOrder(unit,{action:'attack',id:payload.id});return stResult(true);}
  if(action==='rescue'){if(unit.kind!=='sheep'||unit.captured)return stResult(false,'A living sheep must reach the captured wisp.');if(s.selectedId!==unit.id)return stResult(false,'Select your sheep to rescue a teammate.');if(!s.units.some(u=>u.id===payload.id&&u.captured))return stResult(false,'Choose a captured wisp in the spirit pen.');unit.archiveRoute=null;stSetOrder(unit,{action:'rescue',id:payload.id});return stResult(true);}
  if(action==='wolf-upgrade'||action==='upgrade'&&unit.kind==='wolf'){if(unit.kind!=='wolf')return stResult(false,'The merchant sells hunting upgrades to wolves.');if(unit.level>=3)return stResult(false,'Your wolf is already level 3.');if(!s.shops.some(shop=>Math.hypot(shop.pos.x-unit.pos.x,shop.pos.z-unit.pos.z)<=4.5))return stResult(false,'Move your wolf beside a merchant to buy an upgrade.');const cost=unit.level*75;if(s.resources[unit.id]<cost)return stResult(false,'Need '+cost+' gold. Break houses or tag sheep to earn bounty.');s.resources[unit.id]-=cost;unit.level++;unit.speed+=.55;unit.damage+=25;s.message=unit.name+' upgraded to level '+unit.level+'.';return stResult(true,'',{cost,level:unit.level});}
  if(action==='sell'||action==='upgrade'){const b=s.buildings.find(b=>b.id===(payload.id||s.selectedId)&&b.hp>0);if(!b||b.owner!==unit.id||unit.kind!=='sheep'||unit.captured)return stResult(false,'Select one of your own structures while your sheep is alive.');if(action==='sell'){const refund=Math.floor(b.cost*.5);s.resources[unit.id]+=refund;stRemoveBuilding(b);s.message='Cleared '+ST_BUILDINGS[b.kind].name+'; refunded '+refund+' gold.';return stResult(true,'',{refund});}if(b.progress<1)return stResult(false,'Wait until construction is complete.');if(b.level>=3)return stResult(false,'This structure is already level 3.');const cost=b.level*50;if(s.resources[unit.id]<cost)return stResult(false,'Need '+cost+' gold to upgrade.');s.resources[unit.id]-=cost;b.cost+=cost;b.level++;b.maxHp+=180;b.hp+=180;if(b.kind==='st-income')b.income+=2;s.message=ST_BUILDINGS[b.kind].name+' upgraded to level '+b.level+'.';return stResult(true,'',{cost});}
  return stResult(false,'Unknown Sheep Tag command.');
}
