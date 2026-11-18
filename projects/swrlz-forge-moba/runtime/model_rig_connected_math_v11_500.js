/* §E v11.500 — validated connected rest-chain editing, no renderer required.
   A parented joint keeps its original segment length; descendants and their
   influence envelope centers follow one rigid transform. Root translates all. */
const se500RestMath=(()=>{
 'use strict';
 const limit=19.995,eps=1e-8;
 const valid=v=>Array.isArray(v)&&v.length===3&&v.every(n=>Number.isFinite(n)&&Math.abs(n)<limit);
 const sub=(a,b)=>a.map((n,i)=>n-b[i]);
 const add=(a,b)=>a.map((n,i)=>n+b[i]);
 const scale=(a,k)=>a.map(n=>n*k);
 const dot=(a,b)=>a.reduce((sum,n,i)=>sum+n*b[i],0);
 const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
 const len=a=>Math.hypot(...a);
 function quaternionBetween(a,b){
  const al=len(a),bl=len(b);
  if(al<eps||bl<eps)return [0,0,0,1];
  const x=scale(a,1/al),y=scale(b,1/bl),d=Math.min(1,Math.max(-1,dot(x,y)));
  if(d<-.999999){
   const candidate=Math.abs(x[0])<.75?[1,0,0]:[0,1,0];
   const axis=cross(x,candidate),length=len(axis);
   return [...scale(axis,1/length),0];
  }
  const c=cross(x,y),q=[...c,1+d],qlen=Math.hypot(...q);
  return q.map(n=>n/qlen);
 }
 function rotate(v,q){
  const u=q.slice(0,3),t=scale(cross(u,v),2);
  return add(add(v,scale(t,q[3])),cross(u,t));
 }
 function descendants(rig,id){
  const chosen=new Set([id]);
  for(const b of rig.bones)if(chosen.has(b.parent))chosen.add(b.id);
  return chosen;
 }
 function solve(rig,id,target,lockLength=true){
  if(!Array.isArray(rig?.bones)||!valid(target))return null;
  const bone=rig.bones.find(b=>b.id===id);
  if(!bone||!valid(bone.rest))return null;
  const parent=bone.parent?rig.bones.find(b=>b.id===bone.parent):null;
  if(bone.parent&&(!parent||!valid(parent.rest)))return null;
  const chosen=descendants(rig,id);
  let transform;
  if(parent&&lockLength){
   const base=sub(bone.rest,parent.rest),wanted=sub(target,parent.rest);
   const baseLength=len(base);
   if(baseLength<eps)return null; // cannot rotate a zero-length segment
   const aim=len(wanted)<eps?base:wanted;
   const rotation=quaternionBetween(base,aim);
   transform=point=>add(parent.rest,rotate(sub(point,parent.rest),rotation));
  }else{
   const delta=sub(target,bone.rest);
   transform=point=>add(point,delta);
  }
  const bones=[];
  for(const b of rig.bones){
   if(!chosen.has(b.id))continue;
   const rest=transform(b.rest);
   if(!valid(rest))return null;
   bones.push({id:b.id,rest});
  }
  const envelopes=[];
  for(let i=0;i<(rig.envelopes||[]).length;i++){
   const e=rig.envelopes[i];
   if(!chosen.has(e.bone))continue;
   const center=transform(e.center);
   if(!valid(center))return null;
   envelopes.push({index:i,center});
  }
  return {bones,envelopes,affected:chosen.size,
   locked:!!parent&&!!lockLength,selected:bones.find(b=>b.id===id)?.rest};
 }
 function weightOf(indices,weights,boneIndex){
  if(!Array.isArray(indices)||!Array.isArray(weights)||indices.length!==4||weights.length!==4)return 0;
  let sum=0;
  for(let i=0;i<4;i++)if(indices[i]===boneIndex&&Number.isFinite(weights[i])&&weights[i]>0)sum+=weights[i];
  return Math.min(1,Math.max(0,sum));
 }
 function snapshot(rig){
  return {bones:rig.bones.map(b=>({id:b.id,rest:b.rest.slice()})),
   envelopes:(rig.envelopes||[]).map((e,index)=>({index,center:e.center.slice()}))};
 }
 function apply(rig,state){
  if(!state?.bones||!Array.isArray(state.envelopes))return false;
  const bones=new Map(state.bones.map(b=>[b.id,b.rest]));
  for(const bone of rig.bones){
   const rest=bones.get(bone.id);
   if(rest){if(!valid(rest))return false;bone.rest=rest.slice();}
  }
  for(const e of state.envelopes){
   if(!valid(e.center)||!rig.envelopes?.[e.index])return false;
   rig.envelopes[e.index].center=e.center.slice();
  }
  return true;
 }
 return Object.freeze({solve,snapshot,apply,descendants,quaternionBetween,rotate,weightOf});
})();
window.SWYRL_ENGINE_RIG_CONNECTED_MATH_500=se500RestMath;
