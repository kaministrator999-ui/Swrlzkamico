// §E v11.125: label local sheep clearance from real swept collision, not
// from a one-metre-long approach that may strike unrelated nearby houses.
// Building ejection is restored separately by the ordered patch; neither
// movement routes nor the collision/placement implementation is replaced.
const stHonestGapPrevious=stClarityGap;
function stHonestGapLocalClear(gap,a,b,buildings,rules,species){
 const radius=stUnitRadius(species);
 if(gap.width+1e-6<radius*2)return false;
 const axis=gap.axis,cross=axis==='x'?'z':'x';
 const crossHalf=cross==='x'?'halfX':'halfZ';
 const aPos=a.pos,bPos=b.pos;
 const lo=Math.max(aPos[cross]-a[crossHalf],bPos[cross]-b[crossHalf]);
 const hi=Math.min(aPos[cross]+a[crossHalf],bPos[cross]+b[crossHalf]);
 if(hi-lo<Math.max(.16,radius*.8))return false;
 const edgeA=aPos[axis]+(aPos[axis]<bPos[axis]?a[axis==='x'?'halfX':'halfZ']:-a[axis==='x'?'halfX':'halfZ']);
 const edgeB=bPos[axis]+(bPos[axis]<aPos[axis]?b[axis==='x'?'halfX':'halfZ']:-b[axis==='x'?'halfX':'halfZ']);
 const mid=(edgeA+edgeB)/2;
 const available=(gap.width-radius*2)/2;
 const shifts=[0,-Math.min(.18,available*.65),Math.min(.18,available*.65)];
 const obstacles=[...(stSession?.obstacles||[]),...buildings.filter(v=>v.hp>0).map(stBuildingObstacle)];
 const context={rules,obstacles};
 // Only claim physical clearance *inside* the two facing walls. A different
 // house beyond one endpoint must not paint this local gap red; a whole-map
 // accessible route is deliberately not asserted by this indicator.
 for(const shift of shifts){
  const p={x:0,z:0},q={x:0,z:0};
  p[axis]=q[axis]=mid+shift;
  p[cross]=lo+.025;q[cross]=hi-.025;
  if(stSegmentClear(context,p,q,radius))return true;
 }
 return false;
}
stClarityGap=function(a,b,buildings=stSession?.buildings||[],rules=stSession?.rules){
 const gap=stHonestGapPrevious(a,b,buildings,rules);
 if(!gap||!rules||gap.width<stSafeLaneWidth()-.015||gap.sheep)return gap;
 if(!stHonestGapLocalClear(gap,a,b,buildings,rules,'sheep'))return gap;
 const wolf=stHonestGapLocalClear(gap,a,b,buildings,rules,'wolf');
 gap.sheep=true;gap.wolf=wolf;
 gap.label=wolf?'BOTH CLEAR':'SHEEP CLEAR';
 gap.color=wolf?0xe5c66a:0x48e6ed;
 gap.localClearance=true;
 return gap;
};
