/* SE513_RIG_SKIN_MATH_START
   Generic bounded 4-influence vertex weight editing. Pure math with no DOM,
   renderer, project mutation, network or Sorting Hat assumptions. */
const se513SkinMath=(()=>{
 'use strict';
 const clamp=(x,low=0,high=1)=>Math.min(high,Math.max(low,x));
 const validIndex=(x,count)=>Number.isInteger(x)&&x>=0&&x<count;
 function row(indices,weights,boneCount){
  if(!Array.isArray(indices)||!Array.isArray(weights)||
     indices.length!==4||weights.length!==4||!Number.isInteger(boneCount)||boneCount<1)return null;
  const values=new Map();
  for(let k=0;k<4;k++){
   const id=indices[k],weight=weights[k];
   if(!validIndex(id,boneCount)||!Number.isFinite(weight)||weight<0||weight>1.000001)return null;
   if(weight>1e-10)values.set(id,(values.get(id)||0)+weight);
  }
  let sorted=[...values].sort((a,b)=>b[1]-a[1]).slice(0,4);
  const total=sorted.reduce((sum,e)=>sum+e[1],0);
  if(!(total>1e-9))return {indices:[0,0,0,0],weights:[1,0,0,0]};
  sorted=sorted.map(([id,w])=>[id,w/total]);
  while(sorted.length<4)sorted.push([0,0]);
  return {indices:sorted.map(e=>e[0]),weights:sorted.map(e=>e[1])};
 }
 function edit(source,bone,change,boneCount){
  if(!validIndex(bone,boneCount)||!Number.isFinite(change)||Math.abs(change)>1)return null;
  const initial=row(source?.indices,source?.weights,boneCount);
  if(!initial)return null;
  const weights=new Map();
  for(let i=0;i<4;i++)if(initial.weights[i]>1e-10)
   weights.set(initial.indices[i],(weights.get(initial.indices[i])||0)+initial.weights[i]);
  const existing=weights.get(bone)||0;
  const desired=clamp(existing+change);
  if(Math.abs(desired-existing)<1e-9)return initial;
  weights.delete(bone);
  let other=[...weights].filter(e=>e[1]>1e-10).sort((a,b)=>b[1]-a[1]).slice(0,desired>1e-9?3:4);
  if(!other.length){
   // A vertex must always have a valid influence. Root is a safe donor for
   // new child weights; root-only vertices cannot erase their last influence.
   if(bone===0)return initial;
   other=[[0,1]];
  }
  const otherTotal=other.reduce((sum,e)=>sum+e[1],0);
  if(!(otherTotal>0))return initial;
  const target=[];
  if(desired>1e-9)target.push([bone,desired]);
  for(const [id,w] of other){
   const rem=(1-desired)*w/otherTotal;
   if(rem>1e-9)target.push([id,rem]);
  }
  target.sort((a,b)=>b[1]-a[1]);
  while(target.length<4)target.push([0,0]);
  // Normalize once to avoid tiny floating errors in WebGL skinning.
  return row(target.map(e=>e[0]),target.map(e=>e[1]),boneCount);
 }
 function region(positions,indices,weights,center,radius,bone,change,boneCount,pose=null){
  if(!Array.isArray(positions)||positions.length%3||
    !Array.isArray(indices)||indices.length!==positions.length/3*4||
    !Array.isArray(weights)||weights.length!==indices.length||
    !Array.isArray(center)||center.length!==3||!center.every(Number.isFinite)||
    !Number.isFinite(radius)||radius<=0||radius>5||
    !Number.isFinite(change)||Math.abs(change)>1)return null;
  const vertices=positions.length/3;
  if(vertices>300000)return null;
  const resultIndices=indices.slice(),resultWeights=weights.slice();
  let changed=0;
  for(let i=0;i<vertices;i++){
   const p=pose?pose(i):positions.slice(i*3,i*3+3);
   if(!Array.isArray(p)||p.length!==3||!p.every(Number.isFinite))return null;
   const d=Math.hypot(p[0]-center[0],p[1]-center[1],p[2]-center[2]);
   if(d>=radius)continue;
   const t=d/radius,falloff=1-(t*t*(3-2*t));
   const old={indices:indices.slice(i*4,i*4+4),weights:weights.slice(i*4,i*4+4)};
   const next=edit(old,bone,change*falloff,boneCount);
   if(!next)return null;
   if(next.indices.some((n,k)=>n!==old.indices[k])||
      next.weights.some((w,k)=>Math.abs(w-old.weights[k])>1e-7)){
    resultIndices.splice(i*4,4,...next.indices);
    resultWeights.splice(i*4,4,...next.weights);
    changed++;
   }
  }
  return {indices:resultIndices,weights:resultWeights,changed,vertices};
 }
 function validSkin(data,vertices,bones){
  if(data?.schema!=='swyrl-explicit-skin-v1'||!Number.isInteger(vertices)||vertices<1||
    !Array.isArray(data.indices)||!Array.isArray(data.weights)||
    data.indices.length!==vertices*4||data.weights.length!==vertices*4)return false;
  for(let i=0;i<vertices;i++){
   const ri=data.indices.slice(i*4,i*4+4),rw=data.weights.slice(i*4,i*4+4);
   if(!ri.every(n=>validIndex(n,bones))||!rw.every(n=>Number.isFinite(n)&&n>=0&&n<=1))return false;
   if(Math.abs(rw.reduce((a,b)=>a+b,0)-1)>1e-4)return false;
  }
  return true;
 }
 return Object.freeze({row,edit,region,validSkin});
})();
window.SWYRL_ENGINE_RIG_SKIN_MATH_513=se513SkinMath;
/* SE513_RIG_SKIN_MATH_END */
