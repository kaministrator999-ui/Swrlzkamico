/* SE510_CONE_AWARE_UV_START
   Cone-sector (developed surface) UVs, with safe non-cone fallback.
   Physical surface stretch is measured on 3D-to-UV triangle derivatives.
   No mesh edits, texture mutations, files, or browser dependencies. */
const se510ConeUV=(()=>{
 'use strict';
 const median=values=>{
  if(!values.length)return NaN;
  values.sort((a,b)=>a-b);
  return values[Math.floor(values.length/2)];
 };
 function profile(topology,cut,maxY){
  const p=topology.positions,H=maxY-cut;
  if(!(H>1e-6))return {tapered:false,reason:'No vertical crown'};
  let low=[],high=[],centerX=0,centerZ=0,centerN=0;
  for(let i=0;i<p.length;i+=3){
   const y=p[i+1];
   if(y>cut+.03*H&&y<cut+.14*H){
    centerX+=p[i];centerZ+=p[i+2];centerN++;
   }
  }
  centerX=centerN?centerX/centerN:0;
  centerZ=centerN?centerZ/centerN:0;
  for(let i=0;i<p.length;i+=3){
   const y=p[i+1],r=Math.hypot(p[i]-centerX,p[i+2]-centerZ);
   if(y>cut+.03*H&&y<cut+.14*H)low.push(r);
   if(y>maxY-.14*H&&y<maxY-.03*H)high.push(r);
  }
  const lowSamples=low.length,highSamples=high.length;
  const baseRadius=median(low),tipRadius=median(high);
  const radiusRatio=tipRadius/Math.max(baseRadius,1e-9);
  const alpha=baseRadius/Math.hypot(H,baseRadius);
  const tapered=lowSamples>=24&&highSamples>=12&&baseRadius>.015*H&&
   baseRadius<1.4*H&&radiusRatio<.62&&alpha>=.02&&alpha<=.82;
  return {tapered,centerX,centerZ,maxY,cut,H,alpha,baseRadius,tipRadius,
   radiusRatio,lowSamples,highSamples,
   reason:tapered?'Tapered upright crown detected':
    'Mesh does not have a reliably tapered upright crown'};
 }
 function project(position,group,p){
  const x=position[0]-p.centerX,z=position[2]-p.centerZ;
  const angle=group===0?Math.atan2(x,Math.abs(z)+1e-10):
   Math.atan2(-x,Math.abs(z)+1e-10);
  const slant=Math.hypot(Math.max(0,p.maxY-position[1]),Math.hypot(x,z));
  const phi=angle*p.alpha;
  return [slant*Math.sin(phi),-slant*Math.cos(phi)];
 }
 function legacy(position,group){
  const x=position[0],z=position[2];
  return [Math.atan2(group===0?x:-x,Math.abs(z)+1e-10),position[1]];
 }
 function stretch(points,uv){
  const a=points[1].map((v,k)=>v-points[0][k]),
        b=points[2].map((v,k)=>v-points[0][k]);
  const du1=uv[1][0]-uv[0][0],dv1=uv[1][1]-uv[0][1],
        du2=uv[2][0]-uv[0][0],dv2=uv[2][1]-uv[0][1];
  const determinant=du1*dv2-du2*dv1;
  const cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],
    a[0]*b[1]-a[1]*b[0]];
  const weight=Math.hypot(...cross)/2;
  if(!(weight>1e-13)||Math.abs(determinant)<1e-12)
   return null;
  const xu=a.map((v,k)=>(v*dv2-b[k]*dv1)/determinant),
        xv=a.map((v,k)=>(b[k]*du1-v*du2)/determinant);
  const A=xu.reduce((n,v)=>n+v*v,0),
        C=xv.reduce((n,v)=>n+v*v,0),
        B=xu.reduce((n,v,k)=>n+v*xv[k],0);
  const disc=Math.hypot(A-C,2*B);
  const high=Math.sqrt(Math.max(0,(A+C+disc)/2)),
        low=Math.sqrt(Math.max(0,(A+C-disc)/2));
  const ratio=high/low;
  return Number.isFinite(ratio)&&ratio>=1&&ratio<=1e6?
   {ratio,weight}:null;
 }
 function compare(topology,tris,pro,usingCone){
  let qualityWeight=0,qualitySum=0,legacyWeight=0,legacySum=0,measured=0;
  for(const tri of tris){
   if(tri.group>1)continue;
   const pts=tri.ids.map(i=>topology.positions.slice(i*3,i*3+3));
   const current=stretch(pts,tri.coords);
   const baseline=usingCone?stretch(pts,pts.map(v=>legacy(v,tri.group))):current;
   if(current){
    qualityWeight+=current.weight;
    qualitySum+=Math.log(current.ratio)*current.weight;measured++;
   }
   if(baseline){
    legacyWeight+=baseline.weight;legacySum+=Math.log(baseline.ratio)*baseline.weight;
   }
  }
  const round=n=>Math.round(n*100)/100;
  return {measuredFaces:measured,
   current:qualityWeight?round(Math.exp(qualitySum/qualityWeight)):null,
   projected:legacyWeight?round(Math.exp(legacySum/legacyWeight)):null,
   method:usingCone?'cone-surface':'flat-panel',
   alpha:pro?.alpha||null,coneDetected:!!pro?.tapered};
 }
 return Object.freeze({profile,project,legacy,stretch,compare});
})();
/* SE510_CONE_AWARE_UV_END */
