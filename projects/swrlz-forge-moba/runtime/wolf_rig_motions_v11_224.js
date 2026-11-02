// §E v11.224 · Astra wolf bone hierarchy and reusable Wolf/Sheep Tag animations.
// Bone poses are visual only. No gameplay, navigation, collision or LAN mutations.
const SE224_WOLF_MOTIONS=Object.freeze([
 ['idle',2.8,'Breathing, ears and tail awareness'],
 ['sniff',2.4,'Muzzle down and curious head turns'],
 ['stalk',1.75,'Low deliberate stalking steps'],
 ['walk',1.22,'Opposed quadruped walking gait'],
 ['run',.68,'Fast bounding chase'],
 ['pounce',.78,'Anticipation, forward lunge and recovery'],
 ['bite',.58,'Jaw snap and head recoil'],
 ['howl',2.3,'Raised muzzle and expressive long howl'],
 ['alert',1.65,'Ears forward and scanning'],
 ['victory',1.5,'Proud posture and tail flourish']
]);
const se224Saturate=n=>Math.max(0,Math.min(1,n));
const se224Ease=n=>{n=se224Saturate(n);return n*n*(3-2*n);};
function se224WolfPose(name,time,phase=0){
 const duration=SE224_WOLF_MOTIONS.find(c=>c[0]===name)?.[1]||2.8;
 const t=((time%duration)+duration)%duration,u=t/duration;
 const w=Math.sin(u*2*Math.PI+phase),w2=Math.sin(u*4*Math.PI+phase);
 const diagonal=[0,Math.PI,Math.PI,0],result={
  legs:[0,0,0,0],knees:[0,0,0,0],head:0,headY:0,
  neck:0,tail:0,tailX:0,jaw:0,spine:0,bob:0
 };
 const gait=(amp,knee,bob)=>{
  result.legs=diagonal.map(a=>Math.sin(u*2*Math.PI+a+phase)*amp);
  result.knees=diagonal.map(a=>Math.max(0,Math.sin(u*2*Math.PI+a+phase))*(-knee));
  result.bob=bob*Math.max(0,w2);result.tail=.13*w;
  result.head=.07*w2;result.spine=.027*Math.sin(u*4*Math.PI+phase);
 };
 switch(name){
  case 'walk':gait(.29,.22,.016);break;
  case 'run':gait(.57,.40,.08);result.head=.12*w2;result.spine=.09*w2;result.tail=.20*w;break;
  case 'stalk':gait(.19,.16,.008);result.spine=-.10;result.head=.17+.045*w;result.neck=.10;result.tail=.10*w;break;
  case 'pounce':{
   const crouch=1-se224Ease(u/.21),leap=se224Ease((u-.18)/.17)*(1-se224Ease((u-.55)/.23));
   result.legs=[-.24,.24,.38,.38].map((n,i)=>n*crouch+(i<2?-.46:.34)*leap);
   result.knees=[-.19,-.19,-.31,-.31].map(n=>n*crouch-.17*leap);
   result.spine=-.2*crouch+.3*leap;result.neck=-.18*leap;result.head=-.20*leap;
   result.bob=.16*leap-.06*crouch;result.tailX=-.25*leap;result.jaw=.26*leap;break;
  }
  case 'bite':{
   const strike=se224Ease((u-.18)/.17)*(1-se224Ease((u-.55)/.24));
   result.head=-.24*strike;result.neck=-.16*strike;
   result.jaw=.52*Math.sin(Math.PI*se224Saturate((u-.08)/.60))**2;
   result.spine=.06*strike;result.tail=.10*w;break;
  }
  case 'howl':{
   const lift=se224Ease((u-.10)/.26)*(1-se224Ease((u-.78)/.17));
   result.head=-.43*lift;result.neck=-.22*lift;result.jaw=.32*lift;
   result.spine=.06*lift;result.tail=.16*Math.sin(u*Math.PI*2);break;
  }
  case 'alert':
   result.head=-.12+.045*Math.sin(u*2*Math.PI);
   result.headY=.29*Math.sin(u*2*Math.PI);result.tail=.08*w;break;
  case 'sniff':
   result.head=.25+.09*w;result.neck=.09;result.headY=.14*Math.sin(u*2*Math.PI*.7);
   result.jaw=.025;result.tail=.08*w;break;
  case 'victory':
   result.head=-.12+.08*w;result.neck=-.06;
   result.tail=.48*Math.sin(u*4*Math.PI);result.tailX=-.13;
   result.legs=[-.10,-.10,.16,.16].map(n=>n+.10*w);result.bob=.025*Math.max(0,w);break;
  default:
   result.head=.035*Math.sin(u*2*Math.PI*.66+phase);
   result.headY=.12*Math.sin(u*2*Math.PI*.42+phase);
   result.tail=.13*Math.sin(u*2*Math.PI*.87+phase);
   result.spine=.015*w;result.jaw=.012*Math.max(0,w);result.bob=.007*w;
 }
 return result;
}
function se224WolfRigSpec(){
 const bones=[
  {id:'wolf_root',parent:null,rest:[0,0,0]},
  {id:'wolf_spine',parent:'wolf_root',rest:[0,1.34,-.18]},
  {id:'wolf_neck',parent:'wolf_spine',rest:[0,1.83,.30]},
  {id:'wolf_head',parent:'wolf_neck',rest:[0,2.12,.43]},
  {id:'wolf_jaw',parent:'wolf_head',rest:[0,2.26,.83]},
  {id:'wolf_tail',parent:'wolf_spine',rest:[0,1.13,-.73]}
 ];
 for(const [side,label] of [[-1,'l'],[1,'r']]){
  for(const [kind,x,y,z,lowerY] of [['hind',side*.35,1.04,-.61,.55],
                                    ['fore',side*.36,1.72,.42,.70]]){
   const joint='wolf_'+kind+'_'+label;
   bones.push({id:joint,parent:'wolf_spine',rest:[x,y,z]});
   bones.push({id:joint+'_knee',parent:joint,rest:[x,lowerY,z]});
  }
 }
 const rig={schema:'swyrl-wolf-armature-v1',bones,pose:{},editedAt:'local'};
 for(const b of bones)rig.pose[b.id]=[0,0,0];
 return rig;
}
function se224WolfRigValid(v){
 if(!v||v.schema!=='swyrl-wolf-armature-v1'||!Array.isArray(v.bones)||v.bones.length!==14||!v.pose)return false;
 const ids=new Set();
 for(const b of v.bones){
  if(!b||!/^wolf_[a-z_]+$/.test(b.id)||ids.has(b.id)||b.parent!==null&&!ids.has(b.parent)||!Array.isArray(b.rest)||
   b.rest.length!==3||!b.rest.every(x=>Number.isFinite(x)&&Math.abs(x)<10))return false;
  ids.add(b.id);
 }
 return Object.entries(v.pose).length<=v.bones.length&&Object.entries(v.pose).every(([id,r])=>
  ids.has(id)&&Array.isArray(r)&&r.length===3&&r.every(n=>Number.isFinite(n)&&Math.abs(n)<=3.14));
}
function se224WolfBonePose(v){
 const p=Object.fromEntries(se224WolfRigSpec().bones.map(b=>[b.id,[0,0,0]]));
 const legs=['wolf_hind_l','wolf_hind_r','wolf_fore_l','wolf_fore_r'];
 for(let i=0;i<4;i++){
  p[legs[i]]=[v.legs[i],0,0];
  p[legs[i]+'_knee']=[v.knees[i],0,0];
 }
 p.wolf_head=[v.head,v.headY,0];p.wolf_neck=[v.neck,0,0];
 p.wolf_tail=[v.tailX,v.tail,0];p.wolf_jaw=[v.jaw,0,0];
 p.wolf_spine=[v.spine,0,0];
 return p;
}
function se224WolfClips(){
 const bones=se224WolfRigSpec().bones.map(x=>x.id);
 return {schema:'swyrl-wolf-joint-clips-v1',rig:'AstraWildwoodWolf',clips:SE224_WOLF_MOTIONS.map(([name,duration,description])=>{
  const keys=Array.from({length:13},(_,i)=>{
   const time=duration*i/12,pose=se224WolfPose(name,time);
   return {time:+time.toFixed(4),rotations:se224WolfBonePose(pose),bodyBob:pose.bob};
  });
  return {name,duration,description,joints:bones,keys};
 })};
}
function se224WolfClipsValid(v){
 if(!v||v.schema!=='swyrl-wolf-joint-clips-v1'||v.rig!=='AstraWildwoodWolf'||!Array.isArray(v.clips)||
  v.clips.length>16)return false;
 const rig=se224WolfRigSpec(),ids=rig.bones.map(b=>b.id);
 return v.clips.every(c=>typeof c.name==='string'&&c.name.length<32&&Number.isFinite(c.duration)&&
  c.duration>.1&&c.duration<=30&&Array.isArray(c.keys)&&c.keys.length<=64&&c.keys.every(k=>
  Number.isFinite(k.time)&&k.time>=0&&k.time<=c.duration+.001&&Number.isFinite(k.bodyBob)&&
  Math.abs(k.bodyBob)<=1&&ids.every(id=>Array.isArray(k.rotations?.[id])&&
  k.rotations[id].length===3&&k.rotations[id].every(n=>Number.isFinite(n)&&Math.abs(n)<=Math.PI))));
}
function se224WolfSampleClip(clip,time){
 const keys=clip?.keys||[];
 if(!keys.length)return null;
 const t=Math.max(0,Math.min(clip.duration,time));
 if(t<=keys[0].time)return keys[0];
 if(t>=keys.at(-1).time)return keys.at(-1);
 let i=1;while(i<keys.length-1&&keys[i].time<t)i++;
 const a=keys[i-1],b=keys[i],s=se224Ease((t-a.time)/(b.time-a.time));
 const rotations={};for(const id of Object.keys(a.rotations))rotations[id]=[0,1,2].map(j=>
  a.rotations[id][j]+(b.rotations[id][j]-a.rotations[id][j])*s);
 return {time:t,rotations,bodyBob:a.bodyBob+(b.bodyBob-a.bodyBob)*s};
}
function se224WolfVertexWeights(pos,rig,part,indexById=null){
 const [x,y,z]=pos,entries=new Map([['wolf_spine',1]]);
 const add=(id,w)=>{if(w>0)entries.set(id,(entries.get(id)||0)+w);};
 const replace=(influences,amount)=>{
  amount=se224Saturate(amount);
  for(const [id,w] of entries)entries.set(id,w*(1-amount));
  for(const [id,w] of influences)add(id,w*amount);
 };
 const lean=se224Ease((z-.05)/.52),high=se224Ease((y-1.60)/.57);
 const neck=se224Ease((y-1.65)/.45)*se224Ease((z-.12)/.42);
 const head=se224Ease((y-2.05)/.37)*se224Ease((z-.20)/.42);
 replace([['wolf_neck',1]],lean*neck*.75);
 replace([['wolf_head',1]],head);
 if(part?.name?.toLowerCase().includes('jaw')||part?.id?.includes('wolf224-jaw')){
  replace([['wolf_jaw',1]],.98);
 }
 const tail=se224Ease((-.70-z)/.44)*(1-se224Ease((y-1.10)/.65));
 replace([['wolf_tail',1]],tail);
 if(y<1.55){
  const front=z>.12,kind=front?'fore':'hind',side=x<0?'l':'r';
  const cx=front?.36:.35,cz=front?.42:-.61,upper=front?1.72:1.04,lower=front?.70:.55;
  const dist=Math.hypot((Math.abs(x)-cx),z-cz);
  const amount=(1-se224Ease((dist-.08)/.34))*se224Ease((upper+.14-y)/.37);
  if(amount>0){
   const knee=se224Ease((lower+.10-y)/.31);
   replace([['wolf_'+kind+'_'+side,1-knee],['wolf_'+kind+'_'+side+'_knee',knee]],amount);
  }
 }
 const top=[...entries].filter(([,w])=>w>1e-5).sort((a,b)=>b[1]-a[1]).slice(0,4);
 const ids=indexById||Object.fromEntries(rig.bones.map((b,i)=>[b.id,i]));
 const sum=top.reduce((s,p)=>s+p[1],0)||1;
 const indexes=top.map(([id])=>ids[id]),weights=top.map(([,w])=>w/sum);
 while(indexes.length<4){indexes.push(0);weights.push(0);}
 return {indexes,weights};
}
