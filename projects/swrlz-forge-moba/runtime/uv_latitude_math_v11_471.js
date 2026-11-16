/* SE471_UV_LATITUDE_MATH_START */
// Latitude-aware UV spacing for a sphere flattened along its local Y axis.
// A blend of 0 preserves the artist's original sphere UVs; 1 distributes
// texture latitude according to the deformed spheroid's meridian arc length.
const se471Latitude=Math.freeze((()=>{
 const N=256;
 function lookup(scale){
  const a=Math.hypot(scale[0],scale[2])/Math.SQRT2;
  const b=Math.abs(scale[1]);
  if(!Number.isFinite(a)||!Number.isFinite(b)||a<.0001||b<.0001)throw Error('Invalid spherical scale');
  const c=new Float64Array(N+1);let sum=0;
  const velocity=t=>Math.hypot(a*Math.cos(t),b*Math.sin(t));
  for(let i=1;i<=N;i++){
   const theta0=(i-1)*Math.PI/N,theta1=i*Math.PI/N;
   sum+=(velocity(theta0)+velocity(theta1))*(theta1-theta0)/2;
   c[i]=sum;
  }
  for(let i=1;i<=N;i++)c[i]/=sum;
  return c;
 }
 function remap(v,curve,blend=1){
  if(!Number.isFinite(v)||!Number.isFinite(blend))return v;
  // UV islands outside [0,1] belong to authored repeating atlases, not spheres.
  if(v<0||v>1)return v;
  const t=(1-v)*N,i=Math.min(N-1,Math.floor(t));
  const warped=1-(curve[i]*(1-(t-i))+curve[i+1]*(t-i));
  return v+(warped-v)*Math.min(1,Math.max(0,blend));
 }
 return {lookup,remap};
})());
/* SE471_UV_LATITUDE_MATH_END */
