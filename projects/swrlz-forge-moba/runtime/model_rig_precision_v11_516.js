/* SE516_RIG_PRECISION_START
   Generic, topology-preserving nearest-vertex/seam or smooth region editing.
   No starter-specific assumptions. This helper shares the v11.513 normalization
   contract and only changes four skin influences on existing vertices. */
const se516SkinPrecision=(()=>{
 'use strict';
 function region(positions,indices,weights,center,radius,bone,delta,bones,pose=null,target='region'){
  if(target==='region')
   return se513SkinMath.region(positions,indices,weights,center,radius,bone,delta,bones,pose);
  if(target!=='vertex'||!Array.isArray(positions)||positions.length%3||
     !Array.isArray(indices)||!Array.isArray(weights)||
     positions.length/3*4!==indices.length||indices.length!==weights.length||
     !Array.isArray(center)||center.length!==3||!center.every(Number.isFinite)||
     !Number.isFinite(radius)||radius<=0||radius>5||
     !Number.isFinite(delta)||Math.abs(delta)>1||
     !Number.isInteger(bones)||bones<1||!Number.isInteger(bone)||bone<0||bone>=bones)
   return null;
  const vertices=positions.length/3;
  if(!vertices||vertices>120000||
     !se513SkinMath.validSkin({schema:'swyrl-explicit-skin-v1',indices,weights},vertices,bones))
   return null;
  const at=i=>pose?pose(i):positions.slice(3*i,3*i+3);
  const dist=(p,q)=>Math.hypot(p[0]-q[0],p[1]-q[1],p[2]-q[2]);
  let closest=null,min=Infinity;
  for(let i=0;i<vertices;i++){
   const p=at(i);
   if(!Array.isArray(p)||p.length!==3||!p.every(Number.isFinite))return null;
   const d=dist(p,center);
   if(d<min){min=d;closest=p;}
  }
  const result={indices:indices.slice(),weights:weights.slice(),changed:0,vertices};
  if(min>radius||!closest)return result;
  // Shared-position vertices are often distinct topology indices on UV seams.
  // Include these, but never another nearby vertex in the brush region.
  const epsilon=Math.max(1e-6,Math.min(radius*.01,1e-4));
  for(let i=0;i<vertices;i++){
   const p=at(i);
   if(!Array.isArray(p)||p.length!==3||!p.every(Number.isFinite))return null;
   if(dist(p,closest)>epsilon)continue;
   const start=4*i,original={
    indices:indices.slice(start,start+4),weights:weights.slice(start,start+4)
   };
   const next=se513SkinMath.edit(original,bone,delta,bones);
   if(!next)return null;
   if(next.indices.some((v,k)=>v!==original.indices[k])||
      next.weights.some((v,k)=>Math.abs(v-original.weights[k])>1e-7)){
    for(let k=0;k<4;k++){
     result.indices[start+k]=next.indices[k];
     result.weights[start+k]=next.weights[k];
    }
    result.changed++;
   }
  }
  return result;
 }
 return Object.freeze({region});
})();
window.SWYRL_ENGINE_RIG_PRECISION_516=se516SkinPrecision;
/* SE516_RIG_PRECISION_END */
