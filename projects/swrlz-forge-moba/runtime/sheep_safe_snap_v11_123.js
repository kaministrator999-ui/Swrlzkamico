// §E v11.123. Sheep Tag's placement footprint and the actual sheep path must agree.
// The collision and pathfinding engines remain the source of truth.
function stSafeLaneWidth() {
 const radius=Math.max(.27,Number(stSession?.rules?.sheepRadius)||.27);
 return Math.round(Math.max(.9,Math.ceil((radius*2+.3)/ST_GRID)*ST_GRID)*100)/100;
}
const stSafeSnapBase=stLanesSnapHouse;
stLanesSnapHouse=function(kind,x,z,snap=.15) {
 if(!ST_LANE_HOUSES.has(kind)||!stSession||
    !Number.isFinite(Number(x))||!Number.isFinite(Number(z)))
  return stSafeSnapBase(kind,x,z,snap);
 // A single stable world lattice for every build intent, not arbitrary 0.15m
 // increments between buildings. Existing authored buildings keep their origin.
 const step=ST_GRID;
 const point={x:Math.round(Number(x)/step)*step,
              z:Math.round(Number(z)/step)*step};
 const width=stSafeLaneWidth();
 for(const axis of ['x','z']){
  const cross=axis==='x'?'z':'x';
  const half=axis==='x'?'halfX':'halfZ';
  const otherHalf=axis==='x'?'halfZ':'halfX';
  let choice=null;
  for(const house of stSession.buildings){
   if(house.hp<=0||!ST_LANE_HOUSES.has(house.kind))continue;
   if(Math.abs(point[cross]-house.pos[cross])>=1.2+house[otherHalf]-.04)continue;
   const delta=point[axis]-house.pos[axis];
   const extent=1.2+house[half];
   if(Math.abs(delta)<extent-.32||Math.abs(delta)>extent+width+.55)continue;
   const sign=Math.sign(delta)||1;
   for(const lane of [0,width]){
    const target=house.pos[axis]+sign*(extent+lane);
    const distance=Math.abs(target-point[axis]);
    if(distance<=Math.max(.52,width*.65)&&
       (!choice||distance<choice.distance-1e-8||
        (Math.abs(distance-choice.distance)<1e-8&&lane>choice.lane)))
     choice={value:target,distance,lane};
   }
  }
  if(choice)point[axis]=Math.round(choice.value*10000)/10000;
 }
 return point;
};
const stSafeCanBuildBase=stCanBuild;
stCanBuild=function(kind,x,z,ownerId=null,rotation=0){
 const fit=stSafeCanBuildBase(kind,x,z,ownerId,rotation);
 if(!fit?.ok||!ST_LANE_HOUSES.has(fit.kind)||!stSession)return fit;
 const minLane=stSafeLaneWidth();
 // Reject a narrow *walkway-looking* slit on either axis. Contact is legal;
 // lanes must admit a sheep plus a navigation-grid safety band. Footprint and
 // physical collisions continue to be enforced by the pre-existing engine.
 for(const house of stSession.buildings){
  if(house.hp<=0||!ST_LANE_HOUSES.has(house.kind))continue;
  const dx=Math.abs(fit.x-house.pos.x),dz=Math.abs(fit.z-house.pos.z);
  const hx=1.2+house.halfX,hz=1.2+house.halfZ;
  const gapX=dx-hx,gapZ=dz-hz;
  const overlapsZ=dz<hz-.04,overlapsX=dx<hx-.04;
  if((overlapsZ&&gapX>.025&&gapX<minLane-.025)||
     (overlapsX&&gapZ>.025&&gapZ<minLane-.025))
   return stResult(false,
     'That slit would block sheep. Snap flush against the house or leave a '+minLane.toFixed(2)+' m sheep lane.',
     {...fit,minimumSheepLane:minLane});
 }
 fit.minimumSheepLane=minLane;
 return fit;
};
