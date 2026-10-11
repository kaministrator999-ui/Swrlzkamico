// Sheep Tag gameplay state is temporary. The editor's authored actors remain
// the source of spawn locations and the native Save Project export.
let stSession = null;
const ST_BUILDINGS = Object.freeze({
  'st-farm': {name:'Farm',cost:0,hp:180,time:1.4,income:0,size:2.4},
  'st-income': {name:'Income Farm',cost:60,hp:240,time:3,income:3,size:2.4},
  'st-fort': {name:'Strong Farm',cost:100,hp:650,time:4,income:0,size:2.4}
});
const ST_GRID = .3;
const ST_SHEEP_RADIUS = .27;
const ST_WOLF_RADIUS = .68;
const stBuildKind = value => ({farm:'st-farm',income:'st-income',fort:'st-fort',strong:'st-fort'}[value] || value);
const stResult = (ok,reason='',extra={}) => ({...extra,ok,reason});
function stWorldPosition(actor){actor.updateWorldMatrix(true,false);return actor.getWorldPosition(new THREE.Vector3());}
function stPlaceUnit(unit){
  const p=unit.pos.clone();p.y=terrainHeight(p.x,p.z);
  unit.pos.y=p.y;
  if(unit.actor.parent&&unit.actor.parent!==scene)unit.actor.parent.worldToLocal(p);
  unit.actor.position.copy(p);
}
function stStaticObstacle(actor){
  const kind=actor.userData.actorType;
  if(actor.userData.baked===false||!['st-tree','st-rock','st-pond','st-shop'].includes(kind)||!walkingObjectVisible(actor))return null;
  const pos=stWorldPosition(actor),scale=new THREE.Vector3();actor.getWorldScale(scale);
  if(kind==='st-tree'||kind==='st-rock')return {id:actor.userData.id,x:pos.x,z:pos.z,radius:(kind==='st-tree'?1.7:1.8)*Math.max(Math.abs(scale.x),Math.abs(scale.z))};
  const half=kind==='st-pond'?3:1.5,matrix=actor.matrixWorld.elements;
  return {id:actor.userData.id,x:pos.x,z:pos.z,halfX:half*(Math.abs(matrix[0])+Math.abs(matrix[8])),halfZ:half*(Math.abs(matrix[2])+Math.abs(matrix[10]))};
}
function stIntersectsObstacle(x,z,radius,obstacle){
  if(obstacle.radius!==undefined)return Math.hypot(x-obstacle.x,z-obstacle.z)<radius+obstacle.radius-.00001;
  const dx=Math.max(0,Math.abs(x-obstacle.x)-obstacle.halfX),dz=Math.max(0,Math.abs(z-obstacle.z)-obstacle.halfZ);
  return dx*dx+dz*dz<radius*radius-.000001;
}
function stObstacles(){
  const s=stSession;if(!s)return [];
  return [...s.obstacles,...s.buildings.filter(b=>b.hp>0).map(b=>({id:b.id,x:b.pos.x,z:b.pos.z,halfX:b.halfX,halfZ:b.halfZ}))];
}
function stBlocked(x,z,radius,ignore=null){
  const s=stSession;if(!s)return true;
  if(Math.abs(x)>s.rules.bounds-radius||Math.abs(z)>s.rules.bounds-radius)return true;
  for(const obstacle of stObstacles())if(obstacle.id!==ignore&&stIntersectsObstacle(x,z,radius,obstacle))return true;
  return false;
}
function stInvalidateNavigation(){if(stSession){stSession.navVersion++;stSession.navigation.clear();}}
function stNavigation(radius){
  const s=stSession,key=String(radius);if(s.navigation.has(key))return s.navigation.get(key);
  // A lattice anchored at zero preserves the narrow sheep-only passages
  // between 2.4-unit farms on the editor's 3-unit building grid.
  const extent=Math.floor((s.rules.bounds-radius)/ST_GRID),width=extent*2+1,count=width*width;
  const nav={extent,width,count,radius,blocked:new Uint8Array(count),scores:new Float64Array(count),parents:new Int32Array(count),closed:new Uint8Array(count)};
  for(const o of stObstacles()){
    const hx=(o.radius??o.halfX)+radius,hz=(o.radius??o.halfZ)+radius;
    const minX=Math.max(-extent,Math.floor((o.x-hx)/ST_GRID)),maxX=Math.min(extent,Math.ceil((o.x+hx)/ST_GRID));
    const minZ=Math.max(-extent,Math.floor((o.z-hz)/ST_GRID)),maxZ=Math.min(extent,Math.ceil((o.z+hz)/ST_GRID));
    for(let z=minZ;z<=maxZ;z++)for(let x=minX;x<=maxX;x++)if(stIntersectsObstacle(x*ST_GRID,z*ST_GRID,radius,o))nav.blocked[(z+extent)*width+x+extent]=1;
  }
  s.navigation.set(key,nav);return nav;
}
function stGridCell(nav,x,z,nearby=true){
  const gx=THREE.MathUtils.clamp(Math.round(x/ST_GRID),-nav.extent,nav.extent),gz=THREE.MathUtils.clamp(Math.round(z/ST_GRID),-nav.extent,nav.extent);
  const index=(gz+nav.extent)*nav.width+gx+nav.extent;if(!nav.blocked[index])return index;if(!nearby)return -1;
  let best=-1,distance=Infinity;
  // Native map pieces may be scaled in the Inspector. Searching beyond a
  // default farm's footprint still finds the edge of an enlarged structure.
  for(let ring=1;ring<=Math.min(64,nav.width);ring++){
    for(let dz=-ring;dz<=ring;dz++)for(let dx=-ring;dx<=ring;dx++){
      if(Math.abs(dx)!==ring&&Math.abs(dz)!==ring)continue;
      const cx=gx+dx,cz=gz+dz;if(Math.abs(cx)>nav.extent||Math.abs(cz)>nav.extent)continue;
      const cell=(cz+nav.extent)*nav.width+cx+nav.extent;if(nav.blocked[cell])continue;
      const d=(cx*ST_GRID-x)**2+(cz*ST_GRID-z)**2;if(d<distance){distance=d;best=cell;}
    }
    if(best!==-1)return best;
  }
  return -1;
}
function stCellPoint(nav,index){return new THREE.Vector3((index%nav.width-nav.extent)*ST_GRID,0,(Math.floor(index/nav.width)-nav.extent)*ST_GRID);}
function stPath(start,target,radius){
  const nav=stNavigation(radius),first=stGridCell(nav,start.x,start.z),last=stGridCell(nav,target.x,target.z);
  if(first<0||last<0)return null;if(first===last)return [stCellPoint(nav,last)];
  nav.scores.fill(Infinity);nav.parents.fill(-1);nav.closed.fill(0);
  const heap=[];
  const push=(id,f)=>{let i=heap.length;heap.push({id,f});while(i){const p=(i-1)>>1;if(heap[p].f<=f)break;heap[i]=heap[p];i=p;}heap[i]={id,f};};
  const pop=()=>{const top=heap[0],tail=heap.pop();if(heap.length){let i=0;while(i*2+1<heap.length){let c=i*2+1;if(c+1<heap.length&&heap[c+1].f<heap[c].f)c++;if(heap[c].f>=tail.f)break;heap[i]=heap[c];i=c;}heap[i]=tail;}return top.id;};
  const goalX=last%nav.width,goalZ=Math.floor(last/nav.width);
  const heuristic=id=>{const dx=Math.abs(id%nav.width-goalX),dz=Math.abs(Math.floor(id/nav.width)-goalZ);return Math.max(dx,dz)+(Math.SQRT2-1)*Math.min(dx,dz);};
  nav.scores[first]=0;push(first,heuristic(first));let expanded=0,found=false;
  while(heap.length&&expanded<18000){
    const id=pop();if(nav.closed[id])continue;if(id===last){found=true;break;}nav.closed[id]=1;expanded++;
    const x=id%nav.width,z=Math.floor(id/nav.width);
    for(let dz=-1;dz<=1;dz++)for(let dx=-1;dx<=1;dx++){
      if(!dx&&!dz)continue;const nx=x+dx,nz=z+dz;if(nx<0||nz<0||nx>=nav.width||nz>=nav.width)continue;
      const next=nz*nav.width+nx;if(nav.blocked[next]||nav.closed[next])continue;
      if(dx&&dz&&(nav.blocked[z*nav.width+nx]||nav.blocked[nz*nav.width+x]))continue;
      const score=nav.scores[id]+(dx&&dz?Math.SQRT2:1);if(score>=nav.scores[next])continue;
      nav.scores[next]=score;nav.parents[next]=id;push(next,score+heuristic(next));
    }
  }
  if(!found)return null;const path=[];let id=last;
  while(id!==first&&id>=0){path.push(stCellPoint(nav,id));id=nav.parents[id];}path.reverse();
  return path;
}
function stSetOrder(unit,order){
  unit.order=order;unit.path=[];unit.pathVersion=-1;unit.repathAt=0;
  if(order&&order.x!==undefined)unit.destination=new THREE.Vector3(order.x,0,order.z);else unit.destination=null;
}
function stOrderTarget(unit){
  const s=stSession,o=unit.order;if(!o)return null;
  if(o.action==='attack'){const target=s.buildings.find(b=>b.id===o.id&&b.hp>0)||s.units.find(u=>u.id===o.id&&!u.captured);return target?.pos||null;}
  if(o.action==='rescue'){const target=s.units.find(u=>u.id===o.id&&u.captured);return target?.spirit?.position||null;}
  return unit.destination;
}
function stMoveUnit(unit,target,dt){
  const s=stSession;if(!target)return false;const radius=unit.kind==='wolf'?ST_WOLF_RADIUS:ST_SHEEP_RADIUS;
  const movedTarget=!unit.pathTarget||unit.pathTarget.distanceToSquared(target)>1;
  if(unit.pathVersion!==s.navVersion||movedTarget||s.elapsed>=unit.repathAt){
    unit.path=stPath(unit.pos,target,radius)||[];unit.pathVersion=s.navVersion;unit.pathTarget=target.clone();unit.repathAt=s.elapsed+.8;
  }
  let budget=unit.speed*dt,moved=false;
  while(unit.path.length&&budget>0){
    const next=unit.path[0],dx=next.x-unit.pos.x,dz=next.z-unit.pos.z,distance=Math.hypot(dx,dz);
    if(distance<.025){unit.path.shift();continue;}
    const step=Math.min(budget,distance),x=unit.pos.x+dx/distance*step,z=unit.pos.z+dz/distance*step;
    if(stBlocked(x,z,radius)){unit.path=[];unit.repathAt=0;break;}
    unit.pos.x=x;unit.pos.z=z;unit.actor.rotation.y=Math.atan2(dx,dz);budget-=step;moved=true;
    if(step>=distance-.00001)unit.path.shift();
  }
  stPlaceUnit(unit);return moved;
}
function stCanBuild(kind,x,z,ownerId=null){
  kind=stBuildKind(kind);const config=ST_BUILDINGS[kind],s=stSession;
  const snappedX=Math.round(Number(x)/3)*3,snappedZ=Math.round(Number(z)/3)*3;
  const extra={kind,x:snappedX,z:snappedZ,cost:config?.cost??0};
  if(!s)return stResult(false,'Start Play before building.',extra);
  if(!config)return stResult(false,'Choose Farm, Income Farm or Strong Farm.',extra);
  if(!Number.isFinite(snappedX)||!Number.isFinite(snappedZ))return stResult(false,'Choose a place on the meadow.',extra);
  const owner=s.units.find(u=>u.id===(ownerId||s.controlledId));
  if(!owner||owner.kind!=='sheep'||owner.captured)return stResult(false,'Only a living sheep can build.',extra);
  if(s.winner)return stResult(false,'Restart the round to build again.',extra);
  if(Math.abs(snappedX)>s.rules.bounds-1.2||Math.abs(snappedZ)>s.rules.bounds-1.2)return stResult(false,'The building must fit inside the meadow.',extra);
  if(Math.abs(snappedX-s.pen.x)<s.pen.reserveX+1.2&&Math.abs(snappedZ-s.pen.z)<s.pen.reserveZ+1.2)return stResult(false,'Keep the central spirit pen and its entrances clear.',extra);
  if(s.buildings.filter(b=>b.owner===owner.id&&b.hp>0).length>=14)return stResult(false,'Each sheep can have up to 14 buildings.',extra);
  if(s.buildings.filter(b=>b.hp>0).length>=84)return stResult(false,'The meadow has reached its building limit.',extra);
  if((s.resources[owner.id]||0)<config.cost)return stResult(false,'Need '+config.cost+' gold for '+config.name+'.',extra);
  for(const obstacle of s.obstacles){
    if(obstacle.radius!==undefined){
      const dx=Math.max(0,Math.abs(snappedX-obstacle.x)-1.2),dz=Math.max(0,Math.abs(snappedZ-obstacle.z)-1.2);
      if(Math.hypot(dx,dz)<obstacle.radius+.08)return stResult(false,'Choose clear ground away from trees, rocks and water.',extra);
    }else if(Math.abs(snappedX-obstacle.x)<1.2+obstacle.halfX+.08&&Math.abs(snappedZ-obstacle.z)<1.2+obstacle.halfZ+.08)return stResult(false,'Choose clear ground away from trees, rocks and water.',extra);
  }
  for(const building of s.buildings)if(building.hp>0&&Math.abs(snappedX-building.pos.x)<1.2+building.halfX+.02&&Math.abs(snappedZ-building.pos.z)<1.2+building.halfZ+.02)return stResult(false,'A building already occupies that space.',extra);
  for(const unit of s.units)if(!unit.captured&&Math.abs(snappedX-unit.pos.x)<1.2+(unit.kind==='wolf'?ST_WOLF_RADIUS:ST_SHEEP_RADIUS)&&Math.abs(snappedZ-unit.pos.z)<1.2+(unit.kind==='wolf'?ST_WOLF_RADIUS:ST_SHEEP_RADIUS))return stResult(false,'Leave room for the units standing here.',extra);
  // Orders reserve gold only when construction actually starts. A second
  // builder reaching the same location must revalidate against the new farm.
  return stResult(true,'',extra);
}
function stNewBuilding(kind,x,z,owner,authored=null){
  const config=ST_BUILDINGS[kind],mesh=authored||stMakeVisual(kind),s=stSession;
  const pos=new THREE.Vector3(x,terrainHeight(x,z),z);
  if(!authored){mesh.position.copy(pos);scene.add(mesh);}
  let halfX=1.2,halfZ=1.2;
  if(authored){authored.updateWorldMatrix(true,true);const matrix=authored.matrixWorld.elements,bounds=new THREE.Box3().setFromObject(authored);halfX=Math.max(1.2*(Math.abs(matrix[0])+Math.abs(matrix[8])),Math.abs(bounds.min.x-x),Math.abs(bounds.max.x-x));halfZ=Math.max(1.2*(Math.abs(matrix[2])+Math.abs(matrix[10])),Math.abs(bounds.min.z-z),Math.abs(bounds.max.z-z));}
  const building={id:authored?.userData.id||'st-runtime-building-'+(++s.serial),kind,pos,halfX,halfZ,owner,hp:config.hp,maxHp:config.hp,progress:authored?1:0,level:1,mesh,authored:!!authored,income:config.income,cost:config.cost,buildTime:config.time,attackFlash:0};
  const materials=new Set();mesh.traverse(node=>{for(const material of Array.isArray(node.material)?node.material:[node.material])if(material?.color)materials.add(material);});
  building.colors=[...materials].map(material=>({material,color:material.color.clone()}));
  s.buildings.push(building);stInvalidateNavigation();return building;
}
function stDisposeVisual(object){
  if(!object)return;scene.remove(object);object.removeFromParent();
  const geometries=new Set(),materials=new Set();object.traverse(node=>{if(node.geometry)geometries.add(node.geometry);for(const material of Array.isArray(node.material)?node.material:[node.material])if(material)materials.add(material);});
  geometries.forEach(geometry=>geometry.dispose());materials.forEach(material=>material.dispose());
  // Den wisp canvas glow maps are a shared cache; disposing a spirit never
  // disposes those textures or another unit's artwork.
}
function stRemoveBuilding(building){
  if(building.hp<=0)return;building.hp=0;if(building.authored)building.mesh.visible=false;else stDisposeVisual(building.mesh);stInvalidateNavigation();
}
function stCapture(unit,wolf=null){
  const s=stSession;if(unit.captured||unit.kind!=='sheep')return;
  unit.captured=true;unit.actor.visible=false;stSetOrder(unit,null);
  for(const building of s.buildings)if(building.owner===unit.id&&building.hp>0)stRemoveBuilding(building);
  unit.spirit=stMakeSpirit();const index=s.units.filter(u=>u.kind==='sheep').indexOf(unit),angle=index*Math.PI*2/Math.max(1,s.units.filter(u=>u.kind==='sheep').length);
  unit.spirit.position.set(s.pen.x+Math.cos(angle)*Math.min(2.3,s.pen.halfX-.8),terrainHeight(s.pen.x,s.pen.z),s.pen.z+Math.sin(angle)*Math.min(2.3,s.pen.halfZ-.8));scene.add(unit.spirit);unit.spiritOrder=null;unit.captureAt=s.elapsed;
  if(wolf)s.resources[wolf.id]=(s.resources[wolf.id]||0)+60;
  s.message=unit.name+' was tagged. Reach the glowing spirit in the centre to rescue them.';
}
function stRescue(unit,rescuer){
  const s=stSession;if(!unit.captured||!rescuer||rescuer.captured||rescuer.kind!=='sheep')return false;
  const origin=unit.spirit.position.clone();stDisposeVisual(unit.spirit);unit.spirit=null;unit.spiritOrder=null;unit.captured=false;unit.actor.visible=true;unit.invulnerableUntil=s.elapsed+3;
  const nav=stNavigation(ST_SHEEP_RADIUS),cell=stGridCell(nav,origin.x+.75,origin.z+.75),position=cell>=0?stCellPoint(nav,cell):origin;
  unit.pos.copy(position);stPlaceUnit(unit);stSetOrder(unit,null);unit.botAt=s.elapsed+.6;
  s.resources[unit.id]=Math.max(s.resources[unit.id]||0,30);s.message=rescuer.name+' rescued '+unit.name+'! Three seconds of protection.';return true;
}
function stAttackBuilding(wolf,building){
  const s=stSession;if(s.elapsed<wolf.attackAt||building.hp<=0)return;wolf.attackAt=s.elapsed+.75;
  const damage=wolf.damage;building.hp=Math.max(0,building.hp-damage);building.attackFlash=.12;
  if(building.hp<=0){const bounty=building.kind==='st-farm'?10:building.kind==='st-income'?20:35;s.resources[wolf.id]=(s.resources[wolf.id]||0)+bounty;building.hp=1;stRemoveBuilding(building);s.message=wolf.name+' broke a '+ST_BUILDINGS[building.kind].name+' and earned '+bounty+' gold.';}
}
function stBuildApproach(unit,x,z){
  const candidates=[];
  for(const [dx,dz] of [[1.65,0],[-1.65,0],[0,1.65],[0,-1.65],[1.65,1.65],[-1.65,-1.65],[1.65,-1.65],[-1.65,1.65]])if(!stBlocked(x+dx,z+dz,ST_SHEEP_RADIUS))candidates.push(new THREE.Vector3(x+dx,0,z+dz));
  candidates.sort((a,b)=>a.distanceToSquared(unit.pos)-b.distanceToSquared(unit.pos));
  for(const candidate of candidates)if(stPath(unit.pos,candidate,ST_SHEEP_RADIUS))return candidate;return null;
}
function stIssueBuild(unit,kind,x,z){
  const result=stCanBuild(kind,x,z,unit.id);if(!result.ok)return result;
  const approach=stBuildApproach(unit,result.x,result.z);if(!approach)return stResult(false,'Your sheep cannot reach that building site.',result);
  stSetOrder(unit,{action:'build',kind:result.kind,siteX:result.x,siteZ:result.z,x:approach.x,z:approach.z});return result;
}
function stUpdateSheep(unit,dt){
  const s=stSession;
  if(unit.captured){
    if(unit.spiritOrder){const p=unit.spirit.position,target=unit.spiritOrder,dx=target.x-p.x,dz=target.z-p.z,d=Math.hypot(dx,dz),step=Math.min(d,3.5*dt);if(d>.01){p.x+=dx/d*step;p.z+=dz/d*step;}else unit.spiritOrder=null;}
    stAnimateSpirit(unit.spirit,s.elapsed,unit.phase);
    return;
  }
  const order=unit.order,target=stOrderTarget(unit);if(order&&target)stMoveUnit(unit,target,dt);
  if(order?.action==='build'&&target&&Math.hypot(unit.pos.x-target.x,unit.pos.z-target.z)<.55){
    const valid=stCanBuild(order.kind,order.siteX,order.siteZ,unit.id);
    if(valid.ok){s.resources[unit.id]-=valid.cost;stNewBuilding(valid.kind,valid.x,valid.z,unit.id);s.message=unit.name+' is building a '+ST_BUILDINGS[valid.kind].name+'.';}
    else if(unit.id===s.controlledId)s.message=valid.reason;
    stSetOrder(unit,null);
  }else if(order?.action==='move'&&target&&Math.hypot(unit.pos.x-target.x,unit.pos.z-target.z)<.35)stSetOrder(unit,null);
  for(const captive of s.units)if(captive.captured&&s.elapsed>captive.captureAt+.6&&Math.hypot(unit.pos.x-captive.spirit.position.x,unit.pos.z-captive.spirit.position.z)<1.45)stRescue(captive,unit);
}
function stUpdateWolf(unit,dt){
  const s=stSession;if(s.elapsed<s.rules.headstart)return;
  const order=unit.order,target=stOrderTarget(unit);if(order&&target)stMoveUnit(unit,target,dt);
  if(order?.action==='move'&&target&&Math.hypot(unit.pos.x-target.x,unit.pos.z-target.z)<.4)stSetOrder(unit,null);
  for(const sheep of s.units)if(sheep.kind==='sheep'&&!sheep.captured&&s.elapsed>=sheep.invulnerableUntil&&Math.hypot(unit.pos.x-sheep.pos.x,unit.pos.z-sheep.pos.z)<1.05)stCapture(sheep,unit);
  if(order?.action==='attack'){
    const building=s.buildings.find(b=>b.id===order.id&&b.hp>0);
    if(building){const dx=Math.max(0,Math.abs(unit.pos.x-building.pos.x)-building.halfX),dz=Math.max(0,Math.abs(unit.pos.z-building.pos.z)-building.halfZ);if(Math.hypot(dx,dz)<1.05)stAttackBuilding(unit,building);}
    else if(!s.units.some(u=>u.id===order.id&&!u.captured))stSetOrder(unit,null);
  }
}
function stBotSheep(unit){
  const s=stSession;if(unit.captured||s.elapsed<unit.botAt)return;unit.botAt=s.elapsed+.8;
  const wolves=s.units.filter(u=>u.kind==='wolf'),nearest=wolves.reduce((best,w)=>!best||w.pos.distanceToSquared(unit.pos)<best.pos.distanceToSquared(unit.pos)?w:best,null);
  const danger=s.elapsed>=s.rules.headstart&&nearest&&nearest.pos.distanceToSquared(unit.pos)<100;
  if(danger){
    let best=null,score=-Infinity;
    for(let i=0;i<12;i++){
      const angle=i*Math.PI/6,x=unit.pos.x+Math.cos(angle)*7.5,z=unit.pos.z+Math.sin(angle)*7.5;
      if(stBlocked(x,z,ST_SHEEP_RADIUS))continue;
      const safety=Math.min(...wolves.map(w=>(x-w.pos.x)**2+(z-w.pos.z)**2));
      if(safety>score&&stPath(unit.pos,new THREE.Vector3(x,0,z),ST_SHEEP_RADIUS)){score=safety;best={x,z};}
    }
    if(best)stSetOrder(unit,{action:'move',...best});return;
  }
  const captive=s.units.filter(u=>u.captured).sort((a,b)=>a.spirit.position.distanceToSquared(unit.pos)-b.spirit.position.distanceToSquared(unit.pos))[0];
  if(captive){stSetOrder(unit,{action:'rescue',id:captive.id});return;}
  if(unit.order)return;
  if(s.elapsed>=unit.nextBuildAt){
    unit.nextBuildAt=s.elapsed+8+unit.phase*1.4;
    const owned=s.buildings.filter(b=>b.owner===unit.id&&b.hp>0);
    if(owned.length<10){
      const kind=!owned.some(b=>b.kind==='st-income')&&s.resources[unit.id]>=60?'st-income':s.resources[unit.id]>150&&owned.length%3===2?'st-fort':'st-farm';
      const baseX=Math.round(unit.pos.x/3)*3,baseZ=Math.round(unit.pos.z/3)*3;
      const offsets=[[3,0],[-3,0],[0,3],[0,-3],[3,3],[-3,-3],[-3,3],[3,-3],[6,0],[0,6]];
      for(let j=0;j<offsets.length;j++){const [dx,dz]=offsets[(j+unit.botIndex)%offsets.length];if(stIssueBuild(unit,kind,baseX+dx,baseZ+dz).ok)return;}
    }
  }
  if(s.elapsed>=unit.nextWanderAt){
    unit.nextWanderAt=s.elapsed+6;
    const angle=unit.phase+s.elapsed*.17,x=THREE.MathUtils.clamp(unit.home.x+Math.cos(angle)*7,-s.rules.bounds+3,s.rules.bounds-3),z=THREE.MathUtils.clamp(unit.home.z+Math.sin(angle)*7,-s.rules.bounds+3,s.rules.bounds-3);
    if(!stBlocked(x,z,ST_SHEEP_RADIUS))stSetOrder(unit,{action:'move',x,z});
  }
}
function stBotWolf(unit){
  const s=stSession;if(s.elapsed<s.rules.headstart||s.elapsed<unit.botAt)return;unit.botAt=s.elapsed+1.2;
  const living=s.units.filter(u=>u.kind==='sheep'&&!u.captured);
  if(!living.length){stSetOrder(unit,null);return;}
  living.sort((a,b)=>a.pos.distanceToSquared(unit.pos)-b.pos.distanceToSquared(unit.pos));
  let target=living[unit.botIndex%Math.min(2,living.length)]||living[0];
  const current=s.buildings.find(b=>b.id===unit.order?.id&&b.hp>0);
  if(current&&current.pos.distanceToSquared(unit.pos)<49)return;
  if(stPath(unit.pos,target.pos,ST_WOLF_RADIUS)){stSetOrder(unit,{action:'attack',id:target.id});return;}
  const blockers=s.buildings.filter(b=>b.hp>0).sort((a,b)=>(a.pos.distanceToSquared(unit.pos)+a.pos.distanceToSquared(target.pos)*.22)-(b.pos.distanceToSquared(unit.pos)+b.pos.distanceToSquared(target.pos)*.22));
  for(const building of blockers){
    const nav=stNavigation(ST_WOLF_RADIUS),cell=stGridCell(nav,building.pos.x,building.pos.z);
    if(cell>=0&&stPath(unit.pos,stCellPoint(nav,cell),ST_WOLF_RADIUS)){stSetOrder(unit,{action:'attack',id:building.id});return;}
  }
  target=living[0];stSetOrder(unit,{action:'attack',id:target.id});
}
function stStart(simulate=false){
  if(stSession)stStop();const rules={...stRules()},baseline=new Map();
  for(const actor of actors){const children=[];actor.traverse(node=>{if(/^stLeg|^stHead$|^stTail$/.test(node.name))children.push({node,rotation:node.rotation.clone()});});baseline.set(actor,{position:actor.position.clone(),rotation:actor.rotation.clone(),scale:actor.scale.clone(),visible:actor.visible,children});}
  const penActor=actors.find(a=>a.userData.actorType==='st-pen'&&a.userData.baked!==false&&walkingObjectVisible(a)),penPosition=penActor?stWorldPosition(penActor):new THREE.Vector3(),penScale=new THREE.Vector3(1,1,1);if(penActor)penActor.getWorldScale(penScale);
  const pen={x:penPosition.x,z:penPosition.z,halfX:Math.max(1,Math.abs(penScale.x)*5),halfZ:Math.max(1,Math.abs(penScale.z)*5),reserveX:Math.abs(penScale.x)*7,reserveZ:Math.abs(penScale.z)*7};
  const s={rules,baseline,pen,shops:[],simulate:!!simulate,role:rules.role==='wolf'?'wolf':'sheep',elapsed:0,winner:null,message:'Build farms during the head start, then keep your flock alive.',selectedId:null,controlledId:null,resources:Object.create(null),units:[],buildings:[],obstacles:[],serial:0,navVersion:0,navigation:new Map(),incomeClock:0};
  stSession=s;let sheepIndex=0,wolfIndex=0;
  for(const actor of actors){
    const kind=actor.userData.actorType;
    if(actor.userData.baked===false||!walkingObjectVisible(actor))continue;
    if(kind==='st-sheep'||kind==='st-wolf'){
      const pos=stWorldPosition(actor),isSheep=kind==='st-sheep',index=isSheep?sheepIndex++:wolfIndex++;
      const unit={id:actor.userData.id,name:actor.name,kind:isSheep?'sheep':'wolf',actor,pos,home:pos.clone(),captured:false,spirit:null,spiritOrder:null,order:null,destination:null,path:[],pathVersion:-1,pathTarget:null,repathAt:0,botAt:isSheep?2:index*.4,nextBuildAt:2+index*1.1,nextWanderAt:5+index,botIndex:index,phase:index*.93,speed:isSheep?5.4:6.2,damage:65,level:1,attackAt:0,invulnerableUntil:0,captureAt:0,walkDistance:0,walkBlend:0,pivots:baseline.get(actor).children};
      s.units.push(unit);s.resources[unit.id]=isSheep?rules.startGold:0;
    }else if(ST_BUILDINGS[kind]){
      const position=stWorldPosition(actor);stNewBuilding(kind,position.x,position.z,actor.userData.stOwner||null,actor);
    }else{const obstacle=stStaticObstacle(actor);if(obstacle)s.obstacles.push(obstacle);if(kind==='st-shop')s.shops.push({id:actor.userData.id,pos:stWorldPosition(actor)});}
  }
  // Authored starting buildings without an explicit owner belong to the
  // nearest sheep. Their ownership is session data and never mutates the map.
  for(const building of s.buildings)if(!building.owner){const sheep=s.units.filter(u=>u.kind==='sheep').sort((a,b)=>a.pos.distanceToSquared(building.pos)-b.pos.distanceToSquared(building.pos))[0];building.owner=sheep?.id||null;}
  const controlled=s.units.find(u=>u.kind===s.role);s.controlledId=simulate?null:controlled?.id||null;s.selectedId=controlled?.id||s.units[0]?.id||null;
  stInvalidateNavigation();return stResult(true,'',stStatus());
}
function stStop(){
  const s=stSession;if(!s)return false;
  for(const unit of s.units)if(unit.spirit)stDisposeVisual(unit.spirit);
  for(const building of s.buildings){if(!building.authored&&building.hp>0)stDisposeVisual(building.mesh);if(building.authored)for(const entry of building.colors)entry.material.color.copy(entry.color);}
  for(const [actor,state] of s.baseline){actor.position.copy(state.position);actor.rotation.copy(state.rotation);actor.scale.copy(state.scale);actor.visible=state.visible;for(const child of state.children)child.node.rotation.copy(child.rotation);}
  s.navigation.clear();stSession=null;return true;
}
function stUpdate(dt,t){
  const s=stSession;if(!s||paused||s.winner)return;
  dt=Math.max(0,Math.min(Number(dt)||0,.05));s.elapsed=Math.min(s.rules.duration,s.elapsed+dt);s.incomeClock+=dt;
  while(s.incomeClock>=1){
    s.incomeClock--;
    for(const unit of s.units)if(unit.kind==='sheep'&&!unit.captured)s.resources[unit.id]+=(1+s.buildings.filter(b=>b.owner===unit.id&&b.hp>0&&b.progress>=1).reduce((n,b)=>n+b.income,0));
  }
  for(const building of s.buildings)if(building.hp>0){
    building.progress=Math.min(1,building.progress+dt/building.buildTime);building.attackFlash=Math.max(0,building.attackFlash-dt);
    if(!building.authored)building.mesh.scale.y=.15+.85*building.progress;
    for(const entry of building.colors){entry.material.color.copy(entry.color);if(building.attackFlash>0)entry.material.color.lerp(new THREE.Color('#ff7758'),building.attackFlash/.12*.7);}
  }
  for(const unit of s.units){
    const before=unit.pos.clone();
    if(unit.id!==s.controlledId){if(unit.kind==='sheep')stBotSheep(unit);else stBotWolf(unit);}
    if(unit.kind==='sheep')stUpdateSheep(unit,dt);else stUpdateWolf(unit,dt);
    const distance=Math.hypot(unit.pos.x-before.x,unit.pos.z-before.z);unit.walkDistance+=distance;unit.walkBlend+=(Number(distance>.002)-unit.walkBlend)*Math.min(1,dt*10);
    for(const pivot of unit.pivots){
      pivot.node.rotation.copy(pivot.rotation);
      if(/^stLeg/.test(pivot.node.name)){const index=Number(pivot.node.name.slice(5))||0;pivot.node.rotation.x+=Math.sin(unit.walkDistance*9+(index===0||index===3?0:Math.PI))*.58*unit.walkBlend;}
      else if(pivot.node.name==='stTail')pivot.node.rotation.y+=Math.sin(s.elapsed*3+unit.phase)*.18;
      else if(pivot.node.name==='stHead'&&unit.kind==='wolf'&&unit.attackAt>s.elapsed)pivot.node.rotation.x+=Math.sin((unit.attackAt-s.elapsed)*Math.PI/.75)*.2;
    }
  }
  const sheep=s.units.filter(u=>u.kind==='sheep');
  if(sheep.length&&sheep.every(u=>u.captured)){s.winner='wolves';s.message='The wolves tagged the whole flock. Wolves win!';}
  else if(s.elapsed>=s.rules.duration){s.winner='sheep';s.message='The flock survived until the timer ended. Sheep win!';}
}
function stStatus(){
  const s=stSession;if(!s)return {active:false,units:[],buildings:[],resources:{},selectedId:null,controlledId:null};
  return {active:true,role:s.role,simulate:s.simulate,elapsed:s.elapsed,remaining:Math.max(0,s.rules.duration-s.elapsed),headstartRemaining:Math.max(0,s.rules.headstart-s.elapsed),winner:s.winner,message:s.message,selectedId:s.selectedId,controlledId:s.controlledId,gold:s.resources[s.controlledId]??0,pen:{...s.pen},shops:s.shops.map(shop=>({id:shop.id,pos:shop.pos.toArray()})),
    resources:{...s.resources},units:s.units.map(u=>({id:u.id,kind:u.captured?'wisp':u.kind,name:u.name,pos:(u.spirit?.position||u.pos).toArray(),captured:u.captured,controlled:u.id===s.controlledId,order:u.order?{...u.order}:u.spiritOrder?{action:'move',...u.spiritOrder}:null,level:u.level,speed:u.speed,damage:u.damage,upgradeCost:u.kind==='wolf'&&u.level<3?u.level*75:null})),
    buildings:s.buildings.filter(b=>b.hp>0).map(b=>({id:b.id,kind:b.kind,name:ST_BUILDINGS[b.kind].name,pos:b.pos.toArray(),halfX:b.halfX,halfZ:b.halfZ,hp:b.hp,maxHp:b.maxHp,progress:b.progress,owner:b.owner,level:b.level,income:b.income,upgradeCost:b.level<3?b.level*50:null}))};
}
function stCommand(action,payload={}){
  const s=stSession;if(!s)return stResult(false,'Start Play to control the flock.');
  if(action==='select'){
    if(!s.units.some(u=>u.id===payload.id)&&!s.buildings.some(b=>b.id===payload.id&&b.hp>0))return stResult(false,'That unit or building is no longer available.');
    s.selectedId=payload.id;return stResult(true);
  }
  if(action==='restart'){const simulate=s.simulate;stStop();return stStart(simulate);}
  if(action==='role'){
    if(!['sheep','wolf'].includes(payload.role))return stResult(false,'Choose sheep or wolf.');
    const unit=s.units.find(u=>u.kind===payload.role);if(!unit)return stResult(false,'This map has no '+payload.role+' spawn.');
    s.role=payload.role;s.controlledId=unit.id;s.selectedId=unit.id;s.simulate=false;stSetOrder(unit,null);return stResult(true);
  }
  if(s.winner)return stResult(false,'The round has ended. Use Restart for another game.');
  if(paused)return stResult(false,'Resume the game before giving orders.');
  const unit=s.units.find(u=>u.id===s.controlledId);
  if(!unit)return stResult(false,'Simulate runs the bots. Use Play or choose a role to take control.');
  if(action==='preview')return stCanBuild(payload.kind,payload.x,payload.z);
  if(action==='move'){
    if(s.selectedId!==unit.id)return stResult(false,'Select your '+(unit.captured?'wisp':unit.kind)+' to give orders.');
    const x=Number(payload.x),z=Number(payload.z);if(!Number.isFinite(x)||!Number.isFinite(z))return stResult(false,'Choose a destination on the meadow.');
    if(unit.captured){unit.spiritOrder={x:THREE.MathUtils.clamp(x,s.pen.x-s.pen.halfX+.8,s.pen.x+s.pen.halfX-.8),z:THREE.MathUtils.clamp(z,s.pen.z-s.pen.halfZ+.8,s.pen.z+s.pen.halfZ-.8)};return stResult(true,'Wisps stay in the spirit pen until rescued.');}
    if(unit.kind==='wolf'&&s.elapsed<s.rules.headstart)return stResult(false,'The wolves are released after the head start.');
    const radius=unit.kind==='wolf'?ST_WOLF_RADIUS:ST_SHEEP_RADIUS;
    if(stBlocked(x,z,radius))return stResult(false,'Choose clear ground inside the meadow.');
    if(!stPath(unit.pos,new THREE.Vector3(x,0,z),radius))return stResult(false,'There is no open route to that destination.');
    stSetOrder(unit,{action:'move',x,z});return stResult(true);
  }
  if(action==='build'){
    if(s.selectedId!==unit.id)return stResult(false,'Select your sheep to build.');
    if(unit.kind!=='sheep'||unit.captured)return stResult(false,'Only a living sheep can build.');return stIssueBuild(unit,payload.kind,payload.x,payload.z);
  }
  if(action==='attack'){
    if(unit.kind!=='wolf')return stResult(false,'Only wolves attack sheep and farms.');
    if(s.selectedId!==unit.id)return stResult(false,'Select your wolf to attack.');
    if(s.elapsed<s.rules.headstart)return stResult(false,'The wolves are released after the head start.');
    const building=s.buildings.find(b=>b.id===payload.id&&b.hp>0),sheep=s.units.find(u=>u.id===payload.id&&u.kind==='sheep'&&!u.captured);
    if(!building&&!sheep)return stResult(false,'Choose a living sheep or standing farm.');
    stSetOrder(unit,{action:'attack',id:payload.id});return stResult(true);
  }
  if(action==='rescue'){
    if(unit.kind!=='sheep'||unit.captured)return stResult(false,'A living sheep must reach the captured wisp.');
    if(s.selectedId!==unit.id)return stResult(false,'Select your sheep to rescue a teammate.');
    if(!s.units.some(u=>u.id===payload.id&&u.captured))return stResult(false,'Choose a captured wisp in the central pen.');
    stSetOrder(unit,{action:'rescue',id:payload.id});return stResult(true);
  }
  if(action==='wolf-upgrade'||action==='upgrade'&&unit.kind==='wolf'){
    if(unit.kind!=='wolf')return stResult(false,'The merchant sells hunting upgrades to wolves.');
    if(unit.level>=3)return stResult(false,'Your wolf is already level 3.');
    if(!s.shops.some(shop=>Math.hypot(shop.pos.x-unit.pos.x,shop.pos.z-unit.pos.z)<=4.5))return stResult(false,'Move your wolf beside a corner merchant to buy an upgrade.');
    const cost=unit.level*75;if(s.resources[unit.id]<cost)return stResult(false,'Need '+cost+' gold. Break farms or tag sheep to earn bounty.');
    s.resources[unit.id]-=cost;unit.level++;unit.speed+=.55;unit.damage+=25;s.message=unit.name+' upgraded to level '+unit.level+'.';return stResult(true,'',{cost,level:unit.level});
  }
  if(action==='sell'||action==='upgrade'){
    const id=payload.id||s.selectedId,building=s.buildings.find(b=>b.id===id&&b.hp>0);
    if(!building||building.owner!==unit.id||unit.kind!=='sheep'||unit.captured)return stResult(false,'Select one of your own farms while your sheep is alive.');
    if(action==='sell'){const refund=Math.floor(building.cost*.5);s.resources[unit.id]+=refund;stRemoveBuilding(building);s.message='Sold '+ST_BUILDINGS[building.kind].name+' for '+refund+' gold.';return stResult(true,'',{refund});}
    if(building.progress<1)return stResult(false,'Wait until construction is complete.');
    if(building.level>=3)return stResult(false,'This farm is already level 3.');
    const cost=building.level*50;if(s.resources[unit.id]<cost)return stResult(false,'Need '+cost+' gold to upgrade.');
    s.resources[unit.id]-=cost;building.cost+=cost;building.level++;building.maxHp+=180;building.hp+=180;if(building.kind==='st-income')building.income+=2;
    s.message=ST_BUILDINGS[building.kind].name+' upgraded to level '+building.level+'.';return stResult(true,'',{cost});
  }
  return stResult(false,'Unknown Sheep Tag command.');
}
