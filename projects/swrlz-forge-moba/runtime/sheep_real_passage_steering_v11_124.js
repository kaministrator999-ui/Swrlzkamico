// §E v11.124 — A clearance label is a promise that the original physical
// sheep can *actually steer through* the passage. This feeds safe waypoints to
// the existing joystick mover; it does not alter collisions, positions, or speed.
function stPassageAssistWaypoint(unit,direction,context,radius){
 if(!stSession||unit?.kind!=='sheep'||unit.captured||unit.isIllusion||
    unit.archiveOnUpper||unit.archiveRoute||unit.archiveFalling)return null;
 const norm=Math.hypot(direction.x,direction.z);
 if(norm<.3)return null;
 const houses=context.obstacles.filter(o=>ST_LANE_HOUSES.has(o.kind)&&
   Math.hypot(o.x-unit.pos.x,o.z-unit.pos.z)<10&&
   Math.abs(Math.sin(2*(o.rotation||0)))<.001);
 let choice=null;
 for(let i=0;i<houses.length;i++)for(let j=i+1;j<houses.length;j++){
  const a=houses[i],b=houses[j];
  for(const cross of ['x','z']){
   const along=cross==='x'?'z':'x';
   const half=cross==='x'?'halfX':'halfZ';
   const longHalf=cross==='x'?'halfZ':'halfX';
   const component=direction[along]/norm;
   if(Math.abs(component)<.62)continue; // joystick points along lane
   const [left,right]=a[cross]<b[cross]?[a,b]:[b,a];
   const near=left[cross]+left[half],far=right[cross]-right[half],gap=far-near;
   if(gap<radius*2+.07||gap>1.65)continue;
   const lo=Math.max(a[along]-a[longHalf],b[along]-b[longHalf]);
   const hi=Math.min(a[along]+a[longHalf],b[along]+b[longHalf]);
   if(hi-lo<radius*2+.3)continue;
   const middle=(near+far)/2,sign=Math.sign(component),p=unit.pos;
   if(Math.abs(p[cross]-middle)>gap/2+1.15)continue;
   if(sign>0&&p[along]>hi+radius+.35||sign<0&&p[along]<lo-radius-.35)continue;
   const nearEntry=sign>0?lo-(radius+.25):hi+(radius+.25);
   const farExit=sign>0?hi+(radius+.25):lo-(radius+.25);
   // Only acquire a lane when near its mouth or inside it.
   const advance=(nearEntry-p[along])*sign;
   if(advance>2.6)continue;
   let goal=advance>.12?nearEntry:farExit;
   // Do not set a target at our current point, which would stall the stick.
   if(Math.abs(goal-p[along])<.08)goal=farExit;
   const target=p.clone();
   target[cross]=middle;target[along]=goal;
   if(target.distanceToSquared(p)<.004||
      !stSegmentClear(context,p,target,radius)||
      stLanesSegmentOccupant(unit,p,target))continue;
   // Equal-sized gaps prefer nearest reachable entrance, not faraway lanes.
   const score=Math.abs(p[cross]-middle)*1.4+
     Math.abs(p[along]-nearEntry)*.32+
     Math.abs(1-Math.abs(component))*.8+
     Math.max(0,gap-.9)*.1;
   if(!choice||score<choice.score)
    choice={target,score,gap,axis:cross,center:middle};
  }
 }
 return choice;
}
const stPassageAssistOriginalRoute=stSolidRoute;
let stPassageAssistLast=null;
stSolidRoute=function(unit,direction,context,radius){
 const option=stPassageAssistWaypoint(unit,direction,context,radius);
 if(option){
  // Drop stale corner-detour cache when acquiring a verified sheep passage.
  stSolidRoutes.delete(unit);
  stPassageAssistLast={
   gap:option.gap,axis:option.axis,center:option.center,
   target:[option.target.x,option.target.z],
   navVersion:stSession.navVersion
  };
  return option.target;
 }
 stPassageAssistLast=null;
 return stPassageAssistOriginalRoute(unit,direction,context,radius);
};
if(window.SWYRL_ENGINE_SHEEP_TAG){
 window.SWYRL_ENGINE_SHEEP_TAG.passageAssistStatus=
  ()=>stPassageAssistLast?{...stPassageAssistLast}:null;
}
