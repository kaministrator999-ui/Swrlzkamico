// Ground joystick assistance only. Movement remains native, swept and analog.
const stHouseSlideUnits=new WeakSet();
function stHouseSlideTarget(unit,direction,context,radius){
 const wasSliding=stHouseSlideUnits.delete(unit);
 const resetPath=()=>{unit.path=[];unit.pathVersion=-1;unit.repathAt=0;};
 if(unit.kind!=='sheep'||unit.captured||unit.isIllusion||unit.archiveOnUpper||unit.archiveRoute||unit.archiveFalling){if(wasSliding)resetPath();return null;}
 const ahead=unit.pos.clone().addScaledVector(direction,.6);
 if(stSegmentClear(context,unit.pos,ahead,radius)){if(wasSliding)resetPath();return null;}
 // Find the first house hit along the intended direction, including rotations.
 let hit=null;
 for(const obstacle of context.obstacles){
  if(!ST_LANE_HOUSES.has(obstacle.kind))continue;
  const [x,z]=stLocalPoint(unit.pos.x,unit.pos.z,obstacle),c=Math.cos(obstacle.rotation||0),sn=Math.sin(obstacle.rotation||0);
  const dx=direction.x*c-direction.z*sn,dz=direction.x*sn+direction.z*c;
  const hx=(obstacle.localHalfX??obstacle.halfX)+radius,hz=(obstacle.localHalfZ??obstacle.halfZ)+radius;
  let entry=-Infinity,exit=Infinity,face=null;
  for(const [axis,p,d,h] of [['x',x,dx,hx],['z',z,dz,hz]]){
   if(Math.abs(d)<1e-8){if(Math.abs(p)>h)exit=-Infinity;continue;}
   const a=(-h-p)/d,b=(h-p)/d,near=Math.min(a,b),far=Math.max(a,b);
   if(near>entry){entry=near;face=axis;}exit=Math.min(exit,far);
  }
  if(entry<-.001||entry>.6||exit<entry||!face)continue;
  // Rounded circle/rectangle corners may fit despite the expanded box.
  if(stSegmentClear({rules:context.rules,obstacles:[obstacle]},unit.pos,ahead,radius))continue;
  if(!hit||entry<hit.entry)hit={obstacle,x,z,c,sn,hx,hz,face,entry};
 }
 if(!hit){if(wasSliding)resetPath();return null;}
 const {obstacle,x,z,c,sn,hx,hz,face}=hit;
 const world=(lx,lz)=>new THREE.Vector3(obstacle.x+lx*c+lz*sn,unit.pos.y,obstacle.z-lx*sn+lz*c);
 const candidates=[-1,1].map(sign=>world(face==='x'?x:sign*(hx+.045),face==='z'?z:sign*(hz+.045)));
 candidates.sort((a,b)=>a.distanceToSquared(unit.pos)-b.distanceToSquared(unit.pos)||b.clone().sub(unit.pos).dot(direction)-a.clone().sub(unit.pos).dot(direction));
 for(const corner of candidates){
  if(!stSegmentClear(context,unit.pos,corner,radius)||stLanesSegmentOccupant(unit,unit.pos,corner))continue;
  const delta=corner.clone().sub(unit.pos),distance=delta.length();if(distance<.02)continue;
  const target=unit.pos.clone().addScaledVector(delta,Math.min(.65,distance)/distance);
  resetPath();stHouseSlideUnits.add(unit);return target;
 }
 if(wasSliding)resetPath();return null;
}
