// §E v11.222: shared Clover motion library and cosmetic Sheep Tag particle layer.
// Render-only state. Never writes sheep orders, gold, physics, construction, saves or LAN packets.
const SE222_SHEEP_MOTIONS=Object.freeze([
 ['idle',2.8,'Breathing, head tilts and soft tail wag'],
 ['graze',3.2,'Curious head dip and tiny hoof steps'],
 ['walk',1.25,'Four-leg alternating walk'],
 ['trot',.75,'Lively diagonal trot and bouncing fleece'],
 ['build',1.15,'House-building hoof taps and head nod'],
 ['celebrate',1.45,'Happy hop and tail flourish']
]);
const se222Clamp=(n,a=0,b=1)=>Math.max(a,Math.min(b,n));
function se222SheepPose(kind,time,seed=0){
 const p=time*2*Math.PI/(SE222_SHEEP_MOTIONS.find(x=>x[0]===kind)?.[1]||2.8)+seed;
 const wave=Math.sin(p),double=Math.sin(p*2),opposite=[0,Math.PI,Math.PI,0];
 let legs=[0,0,0,0],head=0,headY=0,tail=0,bob=0;
 if(kind==='walk'||kind==='trot'){
  const amp=kind==='trot'?.52:.34;
  legs=opposite.map(offset=>Math.sin(p+offset)*amp);
  head=-.045+.055*Math.sin(p*2);tail=.19*Math.sin(p*.7);
  bob=(kind==='trot'?.052:.018)*Math.max(0,double);
 }else if(kind==='build'){
  legs=[-.13,.13,.23,-.23].map((v,i)=>v+.085*Math.sin(p+(i%2)*Math.PI));
  head=.17+.14*Math.sin(p);headY=.055*Math.sin(p*.5);tail=.2*Math.sin(p*1.4);
  bob=.014*Math.max(0,Math.sin(p*2));
 }else if(kind==='graze'){
  legs=[.06,-.08,.03,-.05];head=.4+.14*Math.sin(p);headY=.12*Math.sin(p*.5);
  tail=.10*Math.sin(p*.8);bob=.008*Math.sin(p*2);
 }else if(kind==='celebrate'){
  legs=[-.24,-.24,.35,.35].map((v,i)=>v+.09*Math.sin(p+(i%2)*Math.PI));
  head=-.2+.13*Math.sin(p);headY=.18*Math.sin(p*1.2);tail=.42*Math.sin(p*2);
  bob=.09*Math.pow(Math.max(0,Math.sin(p)),2);
 }else{
  legs=opposite.map((v,i)=>.027*Math.sin(p*.58+v+i*.4));
  head=.045*Math.sin(p*.53);headY=.12*Math.sin(p*.33);
  tail=.12*Math.sin(p*.87);bob=.009*Math.sin(p*.8);
 }
 return {legs,head,headY,tail,bob};
}
function se222SheepClips(){
 const joints=['stLeg0','stLeg1','stLeg2','stLeg3','stHead','stTail'];
 return {schema:'swyrl-sheep-joint-clips-v1',rig:'CloverMeadowSheep',
  clips:SE222_SHEEP_MOTIONS.map(([name,duration,description])=>{
   const keys=Array.from({length:9},(_,i)=>{
    const t=duration*i/8,p=se222SheepPose(name,t);
    return {time:+t.toFixed(4),rotations:{
     stLeg0:[p.legs[0],0,0],stLeg1:[p.legs[1],0,0],
     stLeg2:[p.legs[2],0,0],stLeg3:[p.legs[3],0,0],
     stHead:[p.head,p.headY,0],stTail:[0,p.tail,0]
    },bodyBob:p.bob};
   });
   return {name,duration,description,joints,keys};
  })};
}
function se222SheepClipsValid(value){
 return value?.schema==='swyrl-sheep-joint-clips-v1'&&value.rig==='CloverMeadowSheep'&&
  Array.isArray(value.clips)&&value.clips.length<=16&&value.clips.every(c=>
   typeof c.name==='string'&&c.name.length<=32&&Number.isFinite(c.duration)&&c.duration>0&&c.duration<=30&&
   Array.isArray(c.keys)&&c.keys.length<=64&&c.keys.every(k=>Number.isFinite(k.time)&&
   k.time>=0&&k.time<=c.duration+1e-3&&
   ['stLeg0','stLeg1','stLeg2','stLeg3','stHead','stTail'].every(j=>
    Array.isArray(k.rotations?.[j])&&k.rotations[j].length===3&&
    k.rotations[j].every(n=>Number.isFinite(n)&&Math.abs(n)<=Math.PI))));
}
// One Points draw call, at most 96 cosmetic motes; no per-particle WebGL mesh.
const se222FX={session:null,cloud:null,geometry:null,material:null,particles:[],builds:new Map(),cheers:new Map(),lastEmit:new Map(),time:0};
function se222FXDispose(){
 if(se222FX.cloud)se222FX.cloud.removeFromParent();
 se222FX.geometry?.dispose();se222FX.material?.dispose();
 Object.assign(se222FX,{session:null,cloud:null,geometry:null,material:null,
  particles:[],builds:new Map(),cheers:new Map(),lastEmit:new Map(),time:0});
}
function se222FXBegin(session){
 se222FXDispose();
 if(!session||!scene||typeof THREE==='undefined')return;
 se222FX.session=session;
 const g=new THREE.BufferGeometry();
 g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(96*3),3));
 g.setAttribute('color',new THREE.BufferAttribute(new Float32Array(96*3),3));
 g.setDrawRange(0,0);
 const material=new THREE.PointsMaterial({vertexColors:true,size:.16,transparent:true,
  opacity:.94,depthWrite:false,blending:THREE.AdditiveBlending,sizeAttenuation:true});
 const cloud=new THREE.Points(g,material);cloud.name='Sheep Tag cosmetic VFX';
 cloud.frustumCulled=false;cloud.userData.se222VisualOnly=true;
 scene.add(cloud);Object.assign(se222FX,{cloud,geometry:g,material});
 for(const unit of session.units||[])if(unit.kind==='sheep'&&!unit.captured)
  se222Emit(unit.pos,12,'start',unit.phase||0);
}
function se222Emit(position,count,kind,seed=0){
 if(!se222FX.cloud||!position)return;
 const palette=kind==='build'?[.85,.63,.18]:
  kind==='complete'?[.25,.95,.75]:[.54,.8,1];
 for(let i=0;i<count&&se222FX.particles.length<96;i++){
  const a=i*2.39996+seed,rad=.12+(i%5)*.075,up=kind==='complete'?.85:.35;
  se222FX.particles.push({
   x:position.x+Math.cos(a)*rad,y:(position.y||0)+.18+(i%3)*.1,
   z:position.z+Math.sin(a)*rad,
   vx:Math.cos(a)*(.38+(i%4)*.07),vy:up+(i%5)*.08,
   vz:Math.sin(a)*(.38+(i%4)*.07),
   life:kind==='build'?.56:.95,age:0,
   color:palette.map((c,n)=>se222Clamp(c+(i%3===n?.08:0)))
  });
 }
}
function se222FXFrame(dt){
 if(!se222FX.geometry)return;
 const ps=se222FX.particles,positions=se222FX.geometry.getAttribute('position'),
  colors=se222FX.geometry.getAttribute('color'),d=se222Clamp(dt,0,.05);
 for(let i=ps.length-1;i>=0;i--){
  const p=ps[i];p.age+=d;
  if(p.age>=p.life){ps.splice(i,1);continue;}
  p.x+=p.vx*d;p.y+=p.vy*d;p.z+=p.vz*d;p.vy-=.48*d;
 }
 for(let i=0;i<ps.length;i++){
  const p=ps[i],fade=1-p.age/p.life;
  positions.setXYZ(i,p.x,p.y,p.z);
  colors.setXYZ(i,p.color[0]*fade,p.color[1]*fade,p.color[2]*fade);
 }
 se222FX.geometry.setDrawRange(0,ps.length);
 positions.needsUpdate=true;colors.needsUpdate=true;
}
const se222GamePoseState=new WeakMap();
function se222GameFrame(dt){
 const s=stSession;if(!s){if(se222FX.session)se222FXDispose();return;}
 if(!se222FX.session)se222FXBegin(s);
 if(se222FX.session!==s)se222FXBegin(s);
 if(paused||s.winner)return;
 for(const building of s.buildings||[]){
  if(building.hp<=0||building.authored)continue;
  const prev=se222FX.builds.get(building.id);
  if(prev!==undefined&&prev<1&&building.progress>=1){
   se222Emit(building.pos,17,'complete');
   if(building.owner)se222FX.cheers.set(building.owner,s.elapsed+1.25);
  }
  se222FX.builds.set(building.id,building.progress);
  if(building.progress<1&&s.elapsed-(se222FX.lastEmit.get(building.id)||-1)>.32){
   se222Emit({...building.pos,y:building.pos.y+.4+building.progress*1.1},3,'build',s.elapsed);
   se222FX.lastEmit.set(building.id,s.elapsed);
  }
 }
 for(const u of s.units||[]){
  if(u.kind!=='sheep'||u.captured||u.isIllusion)continue;
  let kind='idle';
  const making=(s.buildings||[]).some(b=>b.hp>0&&b.progress<1&&b.owner===u.id&&
   Math.hypot(b.pos.x-u.pos.x,b.pos.z-u.pos.z)<4);
  if((se222FX.cheers.get(u.id)||0)>s.elapsed)kind='celebrate';
  else if(making||u.order?.action==='build'&&(u.walkBlend||0)<.15)kind='build';
  else if((u.walkBlend||0)>.58)kind='trot';
  else if((u.walkBlend||0)>.1)kind='walk';
  else if(Math.sin(s.elapsed*.37+(u.phase||0))>.85)kind='graze';
  const anim=se222GamePoseState.get(u)||{kind:null,from:null,changed:s.elapsed};
  if(anim.kind!==kind){anim.from=anim.last||se222SheepPose('idle',0);anim.changed=s.elapsed;anim.kind=kind;}
  const phase=(kind==='walk'||kind==='trot')?(u.walkDistance||0)*.9:s.elapsed;
  const target=se222SheepPose(kind,phase,u.phase||0);
  const mix=se222Clamp((s.elapsed-anim.changed)*5);
  const pose={legs:target.legs.map((v,i)=>v*mix+(anim.from.legs[i]||0)*(1-mix)),
   head:target.head*mix+anim.from.head*(1-mix),
   headY:target.headY*mix+anim.from.headY*(1-mix),
   tail:target.tail*mix+anim.from.tail*(1-mix)};
  for(const pivot of u.pivots||[]){
   const node=pivot.node,match=/^stLeg([0-3])$/.exec(node.name);
   if(match){
    const i=+match[1];
    const legacy=Math.sin((u.walkDistance||0)*9+(i===0||i===3?0:Math.PI))*.58*(u.walkBlend||0);
    node.rotation.x+=pose.legs[i]-legacy;
   }else if(node.name==='stHead'){
    node.rotation.x+=pose.head;node.rotation.y+=pose.headY;
   }else if(node.name==='stTail'){
    node.rotation.y+=pose.tail-Math.sin(s.elapsed*3+(u.phase||0))*.18;
   }
  }
  anim.last=pose;se222GamePoseState.set(u,anim);
 }
 se222FXFrame(dt);
}
const se222PreviousStart=stStart;
stStart=function(...args){const result=se222PreviousStart(...args);
 if(stSession)se222FXBegin(stSession);return result;};
const se222PreviousStop=stStop;
stStop=function(...args){se222FXDispose();return se222PreviousStop(...args);};
const se222PreviousUpdate=stUpdate;
stUpdate=function(...args){const result=se222PreviousUpdate(...args);
 se222GameFrame(args[0]);return result;};
window.SWYRL_ENGINE_SHEEP_ANIMATION_222=Object.freeze({
 clips:()=>se222SheepClips(),effects:()=>({active:se222FX.particles.length,
  limitedTo:96,builds:se222FX.builds.size,session:!!se222FX.session}),
 motion:se222SheepPose
});
