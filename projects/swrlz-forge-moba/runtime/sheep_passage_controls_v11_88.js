// Prefer a real, passable house lane before the nearest outside corner.
const stPassageCornerBase=stHouseSlideTarget;
stHouseSlideTarget=function(unit,direction,context,radius){
 if(unit.kind!=='sheep'||unit.captured||unit.isIllusion||unit.archiveOnUpper||unit.archiveRoute||unit.archiveFalling)return stPassageCornerBase(unit,direction,context,radius);
 const nearby=context.obstacles.filter(b=>ST_LANE_HOUSES.has(b.kind)&&Math.hypot(b.x-unit.pos.x,b.z-unit.pos.z)<7&&Math.abs(Math.sin(2*(b.rotation||0)))<.001),lanes=[];
 for(let i=0;i<nearby.length;i++)for(let j=i+1;j<nearby.length;j++)for(const cross of ['x','z']){
  const along=cross==='x'?'z':'x',half=cross==='x'?'halfX':'halfZ',longHalf=cross==='x'?'halfZ':'halfX';
  if(Math.abs(direction[along])<.65)continue;
  const pair=[nearby[i],nearby[j]].sort((a,b)=>a[cross]-b[cross]),[a,b]=pair;
  const low=a[cross]+a[half],high=b[cross]-b[half],gap=high-low;
  if(gap<radius*2+.005||gap>1.15)continue;
  const lo=Math.max(a[along]-a[longHalf],b[along]-b[longHalf]),hi=Math.min(a[along]+a[longHalf],b[along]+b[longHalf]);
  if(hi-lo<.3||unit.pos[along]<lo-.85||unit.pos[along]>hi+.85)continue;
  const center=(low+high)/2,offset=Math.abs(unit.pos[cross]-center);
  if(offset>gap/2+.42)continue;
  // Don't pull a sheep back into a lane it is leaving.
  const sign=Math.sign(direction[along]);if(sign>0&&unit.pos[along]>hi+.3||sign<0&&unit.pos[along]<lo-.3)continue;
  const target=unit.pos.clone();target[cross]=center;target[along]+=sign*.65;
  const align=unit.pos.clone();align[cross]=center;
  for(const p of [target,align])if(p.distanceToSquared(unit.pos)>.0001&&stSegmentClear(context,unit.pos,p,radius)&&!stLanesSegmentOccupant(unit,unit.pos,p)){lanes.push({p,score:offset+Math.max(0,sign>0?lo-unit.pos[along]:unit.pos[along]-hi)});break;}
 }
 if(lanes.length){lanes.sort((a,b)=>a.score-b.score);unit.path=[];unit.pathVersion=-1;unit.repathAt=0;stHouseSlideUnits.add(unit);return lanes[0].p;}
 return stPassageCornerBase(unit,direction,context,radius);
};
