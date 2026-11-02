// §E v11.220 — real hand armature, procedural four-influence skin binding,
// editable joint pose and keyframe interpolation. All authored in native JSON.
// Pure data/math helpers: UI and GPU SkinnedMesh integration live separately.
const se220Clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const se220Smooth=t=>{t=se220Clamp(t);return t*t*(3-2*t);};
function se220RigPreset(rig,kind){
 const pose=Object.fromEntries(rig.bones.map(b=>[b.id,[0,0,0]]));
 if(kind==='open')return pose;
 const curled=kind==='fist'||kind==='pinch',point=kind==='point';
 for(const f of rig.digits){
  const active=curled||point&&f.name!=='index';
  if(!active)continue;
  pose[f.name+'_mcp']=[kind==='pinch'&&f.name==='index'?.43:.73,0,0];
  pose[f.name+'_pip']=[kind==='pinch'&&f.name==='index'?.60:1.04,0,0];
  pose[f.name+'_dip']=[kind==='pinch'&&f.name==='index'?.20:.58,0,0];
 }
 if(kind==='fist'||kind==='pinch'){
  pose.thumb_cmc=[.16,.22,.27];pose.thumb_mcp=[.31,0,.26];pose.thumb_ip=[.22,0,.20];
 }
 return pose;
}
function se220CreateHandRig(digits){
 const bones=[
  {id:'wrist',label:'Wrist',parent:null,rest:[0,.76,0]},
  {id:'palm',label:'Palm',parent:'wrist',rest:[0,1.53,0]}
 ];
 const fcopy=digits.map(f=>({name:f.name,x:f.x,from:f.from,to:f.to,r:f.r,splay:f.splay,z:f.z}));
 for(const f of fcopy){
  const h=f.to-f.from;
  bones.push({id:f.name+'_mcp',label:f.name+' · MCP',parent:'palm',rest:[f.x,f.from,f.z]});
  bones.push({id:f.name+'_pip',label:f.name+' · PIP',parent:f.name+'_mcp',
    rest:[f.x+f.splay*.47,f.from+h*.45,f.z+.01]});
  bones.push({id:f.name+'_dip',label:f.name+' · DIP',parent:f.name+'_pip',
    rest:[f.x+f.splay*.78,f.from+h*.77,f.z+.015]});
 }
 bones.push({id:'thumb_cmc',label:'Thumb · CMC',parent:'palm',rest:[-.515,1.53,.11]},
  {id:'thumb_mcp',label:'Thumb · MCP',parent:'thumb_cmc',rest:[-.818,1.785,.19]},
  {id:'thumb_ip',label:'Thumb · IP',parent:'thumb_mcp',rest:[-1.005,1.94,.22]});
 const rig={schema:'swyrl-hand-skin-v1',algorithm:'linear-blend-4',bones,
  digits:fcopy,duration:1.5,loop:true,pose:{},timeline:[]};
 rig.pose=se220RigPreset(rig,'open');
 rig.timeline=[
  {time:0,pose:se220RigPreset(rig,'open')},
  {time:.75,pose:se220RigPreset(rig,'fist')},
  {time:1.5,pose:se220RigPreset(rig,'open')}
 ];
 return rig;
}
function se220RigValidate(rig){
 if(!rig||rig.schema!=='swyrl-hand-skin-v1'||rig.algorithm!=='linear-blend-4')return false;
 if(!Array.isArray(rig.bones)||rig.bones.length<3||rig.bones.length>32||
    !Array.isArray(rig.digits)||rig.digits.length!==4)return false;
 const ids=new Set();
 for(const b of rig.bones){
  if(!b||typeof b.id!=='string'||!/^[a-z_]{2,32}$/.test(b.id)||ids.has(b.id))return false;
  if(typeof b.label!=='string'||b.label.length>55||!Array.isArray(b.rest)||
     b.rest.length!==3||!b.rest.every(x=>Number.isFinite(x)&&Math.abs(x)<20))return false;
  if(b.parent!==null&&!ids.has(b.parent))return false; // parent-first + acyclic
  ids.add(b.id);
 }
 for(const f of rig.digits)if(!f||!['index','middle','ring','pinky'].includes(f.name)||
     ![f.x,f.from,f.to,f.r,f.splay,f.z].every(x=>Number.isFinite(x)&&Math.abs(x)<10)||
     f.to<=f.from||f.r<=0)return false;
 if(!Number.isFinite(rig.duration)||rig.duration<.2||rig.duration>30||typeof rig.loop!=='boolean')return false;
 const goodPose=pose=>{
  if(!pose||typeof pose!=='object'||Array.isArray(pose))return false;
  if(Object.keys(pose).length>rig.bones.length)return false;
  return Object.entries(pose).every(([id,v])=>ids.has(id)&&Array.isArray(v)&&v.length===3&&
    v.every(x=>Number.isFinite(x)&&Math.abs(x)<=2.8));
 };
 if(!goodPose(rig.pose)||!Array.isArray(rig.timeline)||rig.timeline.length>32)return false;
 let last=-1;
 for(const frame of rig.timeline){
  if(!frame||!Number.isFinite(frame.time)||frame.time<0||frame.time>rig.duration||
     frame.time<=last||!goodPose(frame.pose))return false;
  last=frame.time;
 }
 return true;
}
function se220RigInterpolate(rig,time){
 const keys=rig.timeline;
 if(!keys.length)return structuredClone(rig.pose);
 const t=se220Clamp(time,0,rig.duration);
 if(t<=keys[0].time)return structuredClone(keys[0].pose);
 if(t>=keys.at(-1).time)return structuredClone(keys.at(-1).pose);
 let hi=1;while(hi<keys.length-1&&keys[hi].time<t)hi++;
 const left=keys[hi-1],right=keys[hi],s=(t-left.time)/(right.time-left.time);
 const pose={};
 for(const b of rig.bones){
  const a=left.pose[b.id]||[0,0,0],c=right.pose[b.id]||[0,0,0];
  pose[b.id]=[0,1,2].map(i=>a[i]+(c[i]-a[i])*s);
 }
 return pose;
}
function se220RigWeights(pt,rig){
 const bones=rig.bones,idx=Object.fromEntries(bones.map((b,i)=>[b.id,i]));
 const [x,y,z]=pt;
 const result=new Map();
 const add=(id,w)=>{if(w>0)result.set(id,(result.get(id)||0)+w);};
 const wrist=1-se220Smooth((y-1.02)/.47);
 add('wrist',wrist);add('palm',1-wrist);
 let owner=null,closest=Infinity;
 for(const f of rig.digits){
  const h=f.to-f.from,t=se220Clamp((y-f.from)/h);
  const cx=f.x+f.splay*t;
  const dx=Math.abs(x-cx),dz=Math.abs(z-f.z);
  const distance=Math.hypot(dx,dz*.17);
  if(distance<closest&&y>=f.from-.145&&y<=f.to+.12){
   closest=distance;owner=f;
  }
 }
 if(owner){
  const f=owner,h=f.to-f.from;
  const lateral=1-se220Smooth((closest-f.r*.50)/(f.r*1.70));
  const rise=se220Smooth((y-(f.from-.13))/.235);
  const mix=lateral*rise;
  if(mix>0){
   for(const [id,w] of [...result])result.set(id,w*(1-mix));
   const pip=f.from+h*.45,dip=f.from+h*.77,blend=.072;
   const atPip=se220Smooth((y-(pip-blend))/(2*blend));
   const atDip=se220Smooth((y-(dip-blend))/(2*blend));
   add(f.name+'_mcp',mix*(1-atPip));
   add(f.name+'_pip',mix*atPip*(1-atDip));
   add(f.name+'_dip',mix*atDip);
  }
 }
 // Thumb roots follow an angled two-section skeleton, unlike upright fingers.
 const segments=[[[-.515,1.53,.11],[-.818,1.785,.19]],[[ -.818,1.785,.19],[-1.005,1.94,.22]],[[ -1.005,1.94,.22],[-1.117,2.014,.235]]];
 let bestDist=Infinity,bestT=0;
 for(let i=0;i<segments.length;i++){
  const [a,b]=segments[i],d=b.map((v,j)=>v-a[j]);
  const den=d.reduce((s,v)=>s+v*v,0),t=se220Clamp((x-a[0])*d[0]+(y-a[1])*d[1]+(z-a[2])*d[2]===0?0:
    ((x-a[0])*d[0]+(y-a[1])*d[1]+(z-a[2])*d[2])/den);
  const distance=Math.hypot(...a.map((v,j)=>pt[j]-v-t*d[j]));
  if(distance<bestDist){bestDist=distance;bestT=(i+t)/3;}
 }
 if(x<-.48&&y>1.47){
  const radial=1-se220Smooth((bestDist-.095)/.165);
  const out=radial*se220Smooth((-.48-x)/.19);
  if(out>0){
   for(const [id,w] of [...result])result.set(id,w*(1-out));
   const one=se220Smooth((bestT-.28)/.17),two=se220Smooth((bestT-.63)/.16);
   add('thumb_cmc',out*(1-one));
   add('thumb_mcp',out*one*(1-two));
   add('thumb_ip',out*two);
  }
 }
 const entries=[...result].filter(([,w])=>w>1e-6).sort((a,b)=>b[1]-a[1]).slice(0,4);
 const sum=entries.reduce((s,[,w])=>s+w,0)||1;
 const indices=entries.map(([id])=>idx[id]),weights=entries.map(([,w])=>w/sum);
 while(indices.length<4){indices.push(0);weights.push(0);}
 return {indices,weights};
}
