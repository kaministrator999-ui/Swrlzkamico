// Captured spirits crawl, may drift just outside the pen, and are returned
// home on crossing the leash. Only the existing living-sheep rescue revives.
const ST_WISP_MOTION=Object.freeze({speed:.35,outsideAllowance:2.5});
function stVastFrameMap(){
 const extent=stRules().bounds,prior=orbit.maxDistance;orbit.maxDistance=Infinity;
 setCameraView('perspective');perspectiveCamera.fov=50;perspectiveCamera.updateProjectionMatrix();
 orbit.target.set(0,0,0);const direction=new THREE.Vector3(0,82,65).normalize();
 perspectiveCamera.position.copy(direction).multiplyScalar(extent*3);perspectiveCamera.lookAt(orbit.target);perspectiveCamera.updateMatrixWorld();
 const inverse=perspectiveCamera.quaternion.clone().invert(),tanY=Math.tan(THREE.MathUtils.degToRad(25)),tanX=tanY*perspectiveCamera.aspect;let distance=0;
 for(const x of [-extent,extent])for(const z of [-extent,extent]){const p=new THREE.Vector3(x,0,z).applyQuaternion(inverse);distance=Math.max(distance,Math.abs(p.x)/tanX+p.z,Math.abs(p.y)/tanY+p.z);}
 distance*=1.12;perspectiveCamera.position.copy(direction).multiplyScalar(distance);perspectiveCamera.lookAt(orbit.target);
 orbit.maxDistance=Math.max(prior,distance*1.25);perspectiveCamera.far=Math.max(600,distance+extent*4);perspectiveCamera.updateProjectionMatrix();orbit.update();
 if(scene.fog?.isFog){scene.fog.near=distance+extent;scene.fog.far=scene.fog.near+extent*3;}
}
function stVastOpenGroundBase(base){
 // At wide overview distances a top face fractions below the textured ground
 // loses depth precision. Retain the skirt/underside, removing that hidden top.
 const g=base.geometry,top=g.groups.find(group=>group.materialIndex===2),a=Array.from(g.index.array);
 if(top){g.setIndex(a.filter((_,i)=>i<top.start||i>=top.start+top.count));g.clearGroups();}
}
function stUpdateCapturedWisp(unit,dt){
 const s=stSession,p=unit.spirit.position;
 if(!unit.spiritHome)unit.spiritHome=p.clone();
 if(unit.spiritOrder){
  const dx=unit.spiritOrder.x-p.x,dz=unit.spiritOrder.z-p.z,d=Math.hypot(dx,dz);
  if(d>.01){const distance=Math.min(d,ST_WISP_MOTION.speed*dt);p.x+=dx/d*distance;p.z+=dz/d*distance;}else unit.spiritOrder=null;
 }
 const margin=ST_WISP_MOTION.outsideAllowance;
 if(Math.abs(p.x-s.pen.x)>s.pen.halfX+margin||Math.abs(p.z-s.pen.z)>s.pen.halfZ+margin){
  p.copy(unit.spiritHome);unit.spiritOrder=null;unit.rescueBy=Object.create(null);
  unit.wispReturns=(unit.wispReturns||0)+1;
  if(unit.id===s.controlledId)s.message='Your wisp drifted too far and returned to the pen. A living sheep must revive you.';
 }
 stAnimateSpirit(unit.spirit,s.elapsed,unit.phase);
}

// Large worlds keep the native 0.15 m maze grid. Clear trips need no grid;
// obstructed trips first use bounded local grids and fall back to a full map
// only when their detour actually needs it. Every returned point is world-space.
function stVastFindPath(context,start,target,radius){
 if(stContextBlocked(context,start.x,start.z,radius)||stContextBlocked(context,target.x,target.z,radius))return null;
 if(stSegmentClear(context,start,target,radius))return [new THREE.Vector3(target.x,0,target.z)];
 const centerX=Math.round((start.x+target.x)/24)*12,centerZ=Math.round((start.z+target.z)/24)*12;
 const reach=Math.max(Math.abs(start.x-centerX),Math.abs(start.z-centerZ),Math.abs(target.x-centerX),Math.abs(target.z-centerZ));
 for(const padding of [8,24]){
  const extent=Math.ceil((reach+padding)/6)*6;
  if(extent>=context.rules.bounds)break;
  const cache=stSession?(stSession.vastNavigation??=new Map()):null;
  const key=[stSession?.navVersion,radius,centerX,centerZ,extent].join('|');let nav=cache?.get(key);
  if(!nav){
   const obstacles=context.obstacles.filter(o=>Math.abs(o.x-centerX)<extent+(o.radius??Math.hypot(o.halfX,o.halfZ))+radius&&Math.abs(o.z-centerZ)<extent+(o.radius??Math.hypot(o.halfX,o.halfZ))+radius).map(o=>({...o,x:o.x-centerX,z:o.z-centerZ,corners:o.corners?.map(([x,z])=>[x-centerX,z-centerZ])}));
   // Boundary slabs keep cropped searches from routing outside the real map.
   const bounds=context.rules.bounds,span=bounds+extent+24;
   for(const side of [-1,1]){
    obstacles.push(stFootprint(side*(bounds+span)-centerX,-centerZ,span,span*2,0,'vast-boundary-x'+side));
    obstacles.push(stFootprint(-centerX,side*(bounds+span)-centerZ,span*2,span,0,'vast-boundary-z'+side));
   }
   nav=stBuildNavigation({rules:{...context.rules,bounds:extent},obstacles},radius);
   if(cache){if(cache.size>=3)cache.delete(cache.keys().next().value);cache.set(key,nav);}
  }
  const a=new THREE.Vector3(start.x-centerX,0,start.z-centerZ),b=new THREE.Vector3(target.x-centerX,0,target.z-centerZ),path=stFindPath(nav,a,b);
  if(path)return path.map(p=>new THREE.Vector3(p.x+centerX,0,p.z+centerZ));
 }
 // The unrestricted native search preserves routes around a long obstruction
 // that cannot be contained in either bounded window.
 return stFindPath(stSession?stNavigation(radius):stBuildNavigation(context,radius),start,target);
}
