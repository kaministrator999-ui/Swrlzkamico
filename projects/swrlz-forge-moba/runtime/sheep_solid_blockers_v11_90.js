// Contact never relocates a creature. Joystick routes exist only while held.
// Reject construction over its builder; retired nearest-side ejection is inert.
stLanesEjection=()=>null;
const stSolidCanBuildBase=stCanBuild;
stCanBuild=function(...args){const fit=stSolidCanBuildBase(...args);if(!fit.ok&&fit.reason?.startsWith('No clear side'))return {...fit,reason:'Move your sheep outside the building footprint before placing it.'};return fit;};
const stSolidRoutes=new WeakMap();
function stSolidRoute(unit,direction,context,radius){
 let state=stSolidRoutes.get(unit);
 if(state&&(state.version!==stSession.navVersion||state.direction.dot(direction)<.94)){stSolidRoutes.delete(unit);state=null;}
 if(state){while(state.points.length&&Math.hypot(state.points[0].x-unit.pos.x,state.points[0].z-unit.pos.z)<.01501)state.points.shift();if(state.points.length)return state.points[0];if(stSession.elapsed<state.retry)return null;stSolidRoutes.delete(unit);}
 // Approach the wall before planning. No proactive lane-centering or side shove.
 const step=Math.max(.035,unit.speed*.05),ahead=unit.pos.clone().addScaledVector(direction,step);
 if(stSegmentClear(context,unit.pos,ahead,radius))return ahead;
 // Bounded visibility graph: offset corners and side midpoints naturally expose
 // narrow real lanes. Never allocate a whole-map grid for a held stick.
 const obstacles=context.obstacles.filter(o=>Math.hypot(o.x-unit.pos.x,o.z-unit.pos.z)<12+(o.radius??Math.hypot(o.halfX,o.halfZ)));
 const local={rules:context.rules,obstacles},nodes=[unit.pos.clone()];
 const add=p=>{if(!stContextBlocked(local,p.x,p.z,radius)&&!nodes.some(n=>n.distanceToSquared(p)<.0004))nodes.push(p);};
 for(const o of obstacles.slice(0,32)){
  if(o.radius!==undefined){for(let i=0;i<12;i++){const a=i*Math.PI/6;add(new THREE.Vector3(o.x+Math.cos(a)*(o.radius+radius+.04),0,o.z+Math.sin(a)*(o.radius+radius+.04)));}continue;}
  const hx=(o.localHalfX??o.halfX)+radius+.018,hz=(o.localHalfZ??o.halfZ)+radius+.018,c=Math.cos(o.rotation||0),s=Math.sin(o.rotation||0);
  for(const [x,z] of [[-hx,-hz],[-hx,hz],[hx,-hz],[hx,hz],[0,-hz],[0,hz],[-hx,0],[hx,0]])add(new THREE.Vector3(o.x+x*c+z*s,0,o.z-x*s+z*c));
 }
 const lanes=[];
 for(let i=0;i<obstacles.length;i++)for(let j=i+1;j<obstacles.length;j++){const a=obstacles[i],b=obstacles[j];if(!ST_LANE_HOUSES.has(a.kind)||!ST_LANE_HOUSES.has(b.kind)||Math.abs(Math.sin(2*(a.rotation||0)))>.001||Math.abs(Math.sin(2*(b.rotation||0)))>.001)continue;for(const cross of ['x','z']){const along=cross==='x'?'z':'x',half=cross==='x'?'halfX':'halfZ',long=cross==='x'?'halfZ':'halfX',[lo,hi]=[a,b].sort((a,b)=>a[cross]-b[cross]),start=lo[cross]+lo[half],end=hi[cross]-hi[half],low=Math.max(a[along]-a[long],b[along]-b[long]),high=Math.min(a[along]+a[long],b[along]+b[long]);if(end-start<radius*2+.005||end-start>1.2||high<=low)continue;const center=(start+end)/2;lanes.push({cross,along,center});for(const v of [low-radius-.03,(low+high)/2,high+radius+.03]){const p=new THREE.Vector3();p[cross]=center;p[along]=v;add(p);}}}
 const goals=[];for(const length of [4,6,9])for(const offset of [0,.7,-.7,1.5,-1.5]){const p=unit.pos.clone().addScaledVector(direction,length);p.x+=-direction.z*offset;p.z+=direction.x*offset;const n=nodes.length;add(p);if(nodes.length>n)goals.push(n);}
 for(const lane of lanes)if(Math.abs(direction[lane.along])>.65)for(const length of [4,6,9]){const p=unit.pos.clone().addScaledVector(direction,length);p[lane.cross]=lane.center;const n=nodes.length;add(p);if(nodes.length>n)goals.push(n);}
 const scores=nodes.map(()=>Infinity),parents=nodes.map(()=>-1),done=new Set();scores[0]=0;let goal=-1;
 for(let k=0;k<nodes.length;k++){let a=-1;for(let i=0;i<nodes.length;i++)if(!done.has(i)&&(a<0||scores[i]<scores[a]))a=i;if(a<0||!Number.isFinite(scores[a]))break;if(goals.includes(a)){goal=a;break;}done.add(a);for(let b=1;b<nodes.length;b++){if(done.has(b))continue;const cost=scores[a]+nodes[a].distanceTo(nodes[b]);if(cost>=scores[b]||!stSegmentClear(local,nodes[a],nodes[b],radius))continue;scores[b]=cost;parents[b]=a;}}
 const points=[];for(let i=goal;i>0;i=parents[i])points.unshift(nodes[i]);
 stSolidRoutes.set(unit,{version:stSession.navVersion,direction:direction.clone(),points,retry:stSession.elapsed+.5});return points[0]||null;
}
const stSolidResetBase=stMobileReset;
stMobileReset=function(reason){if(stMobile.unit)stSolidRoutes.delete(stMobile.unit);return stSolidResetBase(reason);};
stMobileDrive=function(unit,dt,update){
 if(stMobile.unit!==unit||stMobile.pointer===null)return update(unit,dt);
 if(!stMobileCanMove()||stMobile.session!==stSession||unit.captured!==stMobile.captured){stMobileReset('session, capture or pause changed');return update(unit,dt);}
 const amount=stMobile.strength;if(!amount){stSolidRoutes.delete(unit);if(unit.order?.joystick)stSetOrder(unit,null);unit.spiritOrder=null;return update(unit,dt);}
 const direction=new THREE.Vector3(stMobile.x,0,stMobile.y).normalize();
 if(unit.captured){unit.spiritOrder={x:unit.spirit.position.x+direction.x,z:unit.spirit.position.z+direction.z};return update(unit,dt*amount);}
 if(typeof stWalkStick==='function'&&stWalkStick(unit,dt))return update(unit,dt);
 const context={rules:stSession.rules,obstacles:stObstacles()},target=stSolidRoute(unit,direction,context,stUnitRadius(unit));
 if(target){if(!unit.order?.joystick)stSetOrder(unit,{action:'move',x:target.x,z:target.z,joystick:true});else{unit.order.x=target.x;unit.order.z=target.z;unit.destination.copy(target);}
  // The route already passed swept collision. Native movement consumes it at
  // normal analog speed and still checks buildings/traffic every 9 cm.
  unit.path=[target.clone()];unit.pathTarget=target.clone();unit.pathVersion=stSession.navVersion;unit.repathAt=stSession.elapsed+1;
 }else if(unit.order?.joystick)stSetOrder(unit,null);
 const speed=unit.speed;unit.speed=speed*amount;try{return update(unit,dt);}finally{unit.speed=speed;}
};
// Stable obstacles for one navigation revision instead of repeated footprint
// allocation during every visibility, bot and swept movement query.
const stSolidObstaclesBase=stObstacles;let stSolidObstacleCache=null;
stObstacles=function(){const s=stSession;if(!s)return [];if(!stSolidObstacleCache||stSolidObstacleCache.session!==s||stSolidObstacleCache.version!==s.navVersion){stSolidObstacleCache={session:s,version:s.navVersion,items:stSolidObstaclesBase()};}return stSolidObstacleCache.items;};
// Same authoritative sample positions, with a conservative swept AABB before
// the narrow phase. Distant houses cannot affect this segment.
const stSolidSegmentBase=stSegmentClear;
stSegmentClear=function(context,a,b,radius){const minX=Math.min(a.x,b.x)-radius,maxX=Math.max(a.x,b.x)+radius,minZ=Math.min(a.z,b.z)-radius,maxZ=Math.max(a.z,b.z)+radius,near=context.obstacles.filter(o=>o.x+(o.radius??o.halfX)>=minX&&o.x-(o.radius??o.halfX)<=maxX&&o.z+(o.radius??o.halfZ)>=minZ&&o.z-(o.radius??o.halfZ)<=maxZ);return stSolidSegmentBase({rules:context.rules,obstacles:near},a,b,radius);};
// A phone recording no longer serializes the growing world every render frame.
// Preserve every command/event and explicit user-selected slower cadences.
const stSolidRunBeginBase=stRunBegin;
stRunBegin=function(...args){const result=stSolidRunBeginBase(...args),run=stRunState.active;if(run?.mode==='sheep-tag'&&run.capture.cadence==='full'&&stMobileMedia.matches){run.capture.cadence=.1;run.capture.mobileSampling='10 Hz world snapshots; command and event captures retained';}return result;};
