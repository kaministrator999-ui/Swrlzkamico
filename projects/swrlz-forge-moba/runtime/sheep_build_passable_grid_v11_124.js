// §E v11.124 — housing choices are flush or a genuinely passable lane.
// No changes to sheep movement, collision radii, player input or game state.
stSafeLaneWidth=function(){
 const radius=Math.max(.27,Number(stSession?.rules?.sheepRadius)||.27);
 // The sheep's diameter alone is not sufficient for a navigable corridor:
 // reserve two navigation grid margins so a centerline cell stays traversable.
 return Math.round(Math.ceil(Math.max(1.2,radius*2+ST_GRID*2)/ST_GRID)*ST_GRID*100)/100;
};
const stBuildGridPreviousSnap=stLanesSnapHouse;
stLanesSnapHouse=function(kind,x,z,snap=.15){
 if(!stSession||!ST_LANE_HOUSES.has(kind)||
    !Number.isFinite(Number(x))||!Number.isFinite(Number(z)))
  return stBuildGridPreviousSnap(kind,x,z,snap);
 const step=ST_GRID,point={
  x:Math.round(Number(x)/step)*step,z:Math.round(Number(z)/step)*step
 };
 const lane=stSafeLaneWidth();
 for(const axis of ['x','z']){
  const cross=axis==='x'?'z':'x',half=axis==='x'?'halfX':'halfZ',
        otherHalf=axis==='x'?'halfZ':'halfX';
  let best=null;
  for(const building of stSession.buildings){
   if(building.hp<=0||!ST_LANE_HOUSES.has(building.kind))continue;
   const distance=point[axis]-building.pos[axis];
   const extent=1.2+building[half];
   if(Math.abs(point[cross]-building.pos[cross])>=1.2+building[otherHalf]-.02||
      Math.abs(distance)<extent-.45||
      Math.abs(distance)>extent+lane+.65)continue;
   for(const gap of [0,lane]){
    // 2 mm collision epsilon is visually flush and avoids SAT edge jitter.
    const worldGap=gap===0?.002:gap;
    const target=building.pos[axis]+Math.sign(distance||1)*(extent+worldGap);
    const delta=Math.abs(target-point[axis]);
    // Quantize the entire near-neighbor band to two actual positions.
    if(delta<=Math.max(.6,lane*.55)&&
       (!best||delta<best.delta-1e-7||
        (Math.abs(delta-best.delta)<1e-7&&gap>best.gap)))
     best={target,delta,gap};
   }
  }
  if(best)point[axis]=Math.round(best.target*10000)/10000;
 }
 return point;
};
const stBuildGridPreviousCanBuild=stCanBuild;
stCanBuild=function(kind,x,z,ownerId=null,rotation=0){
 const fit=stBuildGridPreviousCanBuild(kind,x,z,ownerId,rotation);
 if(!fit?.ok||!stSession||!ST_LANE_HOUSES.has(fit.kind))return fit;
 const lane=stSafeLaneWidth(),epsilon=.022;
 // The native footprint/collision result is already valid. Here we prevent
 // narrow false pathways between its footprint and any other existing house.
 const axisAligned=f=>Math.abs(Math.sin(2*(f.rotation||0)))<.001;
 if(!axisAligned(fit))return fit;
 const halfX=fit.halfX??1.2,halfZ=fit.halfZ??1.2;
 const checks=[];
 for(const other of stSession.buildings){
  if(other.hp<=0||!ST_LANE_HOUSES.has(other.kind)||!axisAligned(other))continue;
  const a=Math.abs(fit.x-other.pos.x)-(halfX+other.halfX);
  const b=Math.abs(fit.z-other.pos.z)-(halfZ+other.halfZ);
  // Candidate and neighbor overlap in the perpendicular coordinate, so
  // the positive separation is a visible but potentially blocked corridor.
  const alongZ=b<-.04,alongX=a<-.04;
  const width=alongZ?a:alongX?b:null;
  if(width!==null&&width>epsilon&&width<lane-.015)
   return stResult(false,
    'This opening would trap a sheep. Place houses flush or leave at least '+
      lane.toFixed(2)+' m.',{...fit,minimumSheepLane:lane});
  // Diagonal slits between near-touching corners are not walkable either.
  if(width===null&&a>epsilon&&b>epsilon&&Math.hypot(a,b)<lane-.015)
   return stResult(false,
    'A diagonal crack is not a sheep passage. Join houses or leave '+
      lane.toFixed(2)+' m.',{...fit,minimumSheepLane:lane});
  if(width!==null&&width>=lane-.015&&width<lane+1.2)
   checks.push({other,axis:alongZ?'x':'z',width});
 }
 // Actual sheep-capsule sweeps through the opening, using the same obstacles
 // the navigation system uses. This catches a third house plugging the exit.
 if(checks.length&&typeof stSegmentClear==='function'){
  const obstacles=[...stObstacles(),{
   kind:fit.kind,x:fit.x,z:fit.z,rotation:fit.rotation||0,
   halfX,halfZ,localHalfX:fit.localHalfX??halfX,
   localHalfZ:fit.localHalfZ??halfZ
  }];
  const context={rules:stSession.rules,obstacles};
  const radius=stUnitRadius('sheep');
  for(const {other,axis} of checks){
   const cross=axis==='x'?'z':'x',half=axis==='x'?'halfX':'halfZ',
    long=axis==='x'?'halfZ':'halfX';
   const lo=fit[axis]<other.pos[axis]?fit:other;
   const hi=lo===fit?other:fit;
   const left=(lo===fit?fit[axis]:other.pos[axis])+(lo===fit?halfX:other.halfX);
   const right=(hi===fit?fit[axis]:other.pos[axis])-(hi===fit?halfX:other.halfX);
   const start=Math.max(fit[cross]-(cross==='x'?halfX:halfZ),
                        other.pos[cross]-other[long]);
   const end=Math.min(fit[cross]+(cross==='x'?halfX:halfZ),
                      other.pos[cross]+other[long]);
   if(end-start<radius*2+.2)continue;
   const p={x:0,z:0},q={x:0,z:0};
   p[axis]=q[axis]=(left+right)/2;
   p[cross]=start-radius-.2;q[cross]=end+radius+.2;
   if(!stSegmentClear(context,p,q,radius))
    return stResult(false,
     'A house or obstacle blocks this sheep passage. Join houses or clear a wider route.',
      {...fit,minimumSheepLane:lane});
  }
 }
 fit.minimumSheepLane=lane;
 return fit;
};
// Never label a physically wide but grid-impractical 0.90m gap SHEEP ONLY.
// Current/old houses remain unchanged; the overlay reports their true status.
const stBuildGridPreviousClarityGap=stClarityGap;
stClarityGap=function(...args){
 const gap=stBuildGridPreviousClarityGap(...args);
 if(gap&&gap.width>=.022&&gap.width<stSafeLaneWidth()-.015){
  gap.sheep=false;gap.wolf=false;gap.label='BLOCKED';gap.color=0xf17d74;
 }
 return gap;
};
