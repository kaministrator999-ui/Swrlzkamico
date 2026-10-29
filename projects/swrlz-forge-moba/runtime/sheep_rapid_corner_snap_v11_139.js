// §E v11.139 · Rapid building near a diagonal corner now considers a
// genuinely flush, SAFE neighbor snap instead of leaving the ghost red.
// All collision, unit/owner and route validation still uses native stCanBuild.
const st139NativeCanBuild=stCanBuild;
function st139RapidCornerProposal(fit,kind,x,z,ownerId,rotation){
 if(!stSession||!st132Rapid||!ST_LANE_HOUSES.has(kind)||
    !fit||fit.ok||typeof fit.reason!=='string'||
    !fit.reason.startsWith('A diagonal crack is not a sheep passage.'))return fit;
 const halfX=fit.halfX??1.2,halfZ=fit.halfZ??1.2;
 const lane=stSafeLaneWidth(),limit=Math.min(lane,1.25);
 let best=null,bestDelta=Infinity;
 for(const b of stSession.buildings){
  if(b.hp<=0||!ST_LANE_HOUSES.has(b.kind)||
     Math.abs(Math.sin(2*(b.rotation||0)))>.001)continue;
  const dx=fit.x-b.pos.x,dz=fit.z-b.pos.z;
  const a=Math.abs(dx)-(halfX+b.halfX),c=Math.abs(dz)-(halfZ+b.halfZ);
  if(a<=.022||c<=.022||Math.hypot(a,c)>=lane-.015)continue;
  // Move the minimum necessary distance to close BOTH corner slits.
  // Moving one axis alone could leave a misleading blocked diagonal.
  const targetX=b.pos.x+Math.sign(dx)*(halfX+b.halfX+.002);
  const targetZ=b.pos.z+Math.sign(dz)*(halfZ+b.halfZ+.002);
  const delta=Math.hypot(targetX-fit.x,targetZ-fit.z);
  if(delta>limit||delta>=bestDelta)continue;
  const next=st139NativeCanBuild(kind,targetX,targetZ,ownerId,rotation);
  if(!next?.ok||Math.hypot(next.x-targetX,next.z-targetZ)>.35||
     Math.hypot(next.x-fit.x,next.z-fit.z)>limit+.2)continue;
  // The candidate must also pass the existing v11.124 clearance validator,
  // so other houses/rocks/units cannot be ignored just to show a green ghost.
  best=next;bestDelta=delta;
 }
 if(best){
  best.st139CornerSnap=true;
  best.st139Requested=[x,z];
  return best;
 }
 return fit;
}
stCanBuild=function(kind,x,z,ownerId=null,rotation=0){
 const fit=st139NativeCanBuild(kind,x,z,ownerId,rotation);
 return st139RapidCornerProposal(fit,kind,x,z,ownerId,rotation);
};
