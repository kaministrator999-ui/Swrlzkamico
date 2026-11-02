// §E v11.224 · native Sheep Tag Astra wolf animation overlay.
// Uses existing 6 pivots + the new articulated jaw. Never modifies commands,
// collision, attack timing/damage, fog, LAN state or camera transformations.
const se224WolfGameMemory=new WeakMap();
function se224WolfGameFrame(dt){
 const s=stSession;if(!s||paused)return;
 for(const u of s.units||[]){
  if(u.kind!=='wolf'||!u.actor||!u.actor.visible)continue;
  const ahead=s.elapsed<s.rules.headstart;
  const near=s.units.filter(other=>other.kind==='sheep'&&!other.captured)
   .reduce((best,other)=>{
    const dist=other.pos.distanceToSquared(u.pos);
    return !best||dist<best.dist?{dist}:best;
   },null);
  const tag=u.wolf224TaggedAt!=null&&s.elapsed-u.wolf224TaggedAt<.48;
  const attack=u.attackAt>s.elapsed&&u.attackAt-s.elapsed<=.75;
  let kind='idle';
  if(s.winner==='wolves')kind='victory';
  else if(ahead)kind='alert';
  else if(tag||attack)kind='bite';
  else if((u.walkBlend||0)>.65&&near?.dist<6)kind='pounce';
  else if((u.walkBlend||0)>.65)kind='run';
  else if((u.walkBlend||0)>.18)kind=u.order?.action==='attack'?'stalk':'walk';
  else if(u.order?.action==='attack'&&near?.dist<36)kind='alert';
  else if(Math.sin(s.elapsed*.25+(u.phase||0))>.94)kind='howl';
  else if(Math.sin(s.elapsed*.48+(u.phase||0))>.78)kind='sniff';
  let state=se224WolfGameMemory.get(u);
  if(!state){state={kind:null,from:se224WolfPose('idle',0),changed:s.elapsed,base:null};se224WolfGameMemory.set(u,state);}
  if(kind!==state.kind){state.from=state.last||se224WolfPose('idle',0);state.kind=kind;state.changed=s.elapsed;}
  const phase=(kind==='walk'||kind==='run'||kind==='stalk')?(u.walkDistance||0)*(kind==='run'?.88:.48):s.elapsed;
  const target=se224WolfPose(kind,phase,u.phase||0),fade=se224Ease((s.elapsed-state.changed)/.19);
  const lerp=(a,b)=>(Number(a)||0)*(1-fade)+(Number(b)||0)*fade;
  const pose={...target,legs:target.legs.map((v,i)=>lerp(state.from.legs[i],v)),
    knees:target.knees.map((v,i)=>lerp(state.from.knees[i],v)),
    head:lerp(state.from.head,target.head),headY:lerp(state.from.headY,target.headY),
    neck:lerp(state.from.neck,target.neck),tail:lerp(state.from.tail,target.tail),
    tailX:lerp(state.from.tailX,target.tailX),jaw:lerp(state.from.jaw,target.jaw),
    spine:lerp(state.from.spine,target.spine),bob:lerp(state.from.bob,target.bob)};
  state.last=pose;
  const g=u.actor.getObjectByName('AstraCometCourier');
  if(g){
   if(state.base===null)state.base=g.position.y;
   g.position.y=state.base+pose.bob; // cosmetic body bounce on this actor only
  }
  const jaw=u.actor.getObjectByName('stJaw');
  if(jaw)jaw.rotation.x=pose.jaw;
  for(const pivot of u.pivots||[]){
   const node=pivot.node,m=/^stLeg([0-3])$/.exec(node.name);
   if(m){
    const i=Number(m[1]);
    const legacy=Math.sin((u.walkDistance||0)*9+(i===0||i===3?0:Math.PI))*.58*(u.walkBlend||0);
    node.rotation.x+=pose.legs[i]-legacy;
   }else if(node.name==='stTail'){
    node.rotation.y+=pose.tail-Math.sin(s.elapsed*3+(u.phase||0))*.18;
    node.rotation.x+=pose.tailX;
   }else if(node.name==='stHead'){
    const legacy=u.attackAt>s.elapsed?
      Math.sin((u.attackAt-s.elapsed)*Math.PI/.75)*.2:0;
    node.rotation.x+=pose.head-legacy;
    node.rotation.y+=pose.headY;
   }
  }
 }
}
const se224WolfCaptureOriginal=stCapture;
stCapture=function(unit,wolf=null){
 const untouched=!!unit?.captured;
 const result=se224WolfCaptureOriginal(unit,wolf);
 if(wolf&&!untouched&&unit?.captured&&stSession)wolf.wolf224TaggedAt=stSession.elapsed;
 return result;
};
const se224WolfGameOriginal=stUpdate;
stUpdate=function(...args){
 const output=se224WolfGameOriginal(...args);
 se224WolfGameFrame(args[0]);
 return output;
};
const se224WolfStopOriginal=stStop;
stStop=function(...args){
 for(const u of stSession?.units||[]){
  if(u.kind!=='wolf')continue;
  const state=se224WolfGameMemory.get(u);
  const body=u.actor?.getObjectByName('AstraCometCourier');
  if(body&&state?.base!==null&&Number.isFinite(state?.base))body.position.y=state.base;
  const jaw=u.actor?.getObjectByName('stJaw');if(jaw)jaw.rotation.x=0;
  se224WolfGameMemory.delete(u);
 }
 return se224WolfStopOriginal(...args);
};
window.SWYRL_ENGINE_WOLF_224=Object.freeze({
 clips:()=>se224WolfClips(),pose:se224WolfPose,
 active:()=>({version:'v11.227',wolves:stSession?.units?.filter(u=>u.kind==='wolf').length||0,
  animations:SE224_WOLF_MOTIONS.map(x=>x[0]),cosmeticOnly:true}),
 prefab:()=>{
  // Inspect the exact game prefab without starting or mutating a match.
  const wolf=stMakeVisual('st-wolf'),model=wolf.getObjectByName('AstraCometCourier');
  const count=name=>!!wolf.getObjectByName(name);
  const result={furred:!!model,head:count('stHead'),jaw:count('stJaw'),
   face:count('Astra · enhanced head'),body:count('Astra · enhanced body'),
   paws:[0,1,2,3].filter(i=>count('stLeg'+i)).length,
   visualMeshes:0};
  wolf.traverse(n=>{if(n.isMesh)result.visualMeshes++;if(n.isMesh&&n.userData.wolf224VisualOnly){
   n.geometry?.dispose();n.material?.dispose();
  }});
  return result;
 },
 visuals:()=> (stSession?.units||[]).filter(u=>u.kind==='wolf').map(u=>({
  id:u.id,head:!!u.actor?.getObjectByName('stHead'),
  jaw:!!u.actor?.getObjectByName('stJaw'),
  face:!!u.actor?.getObjectByName('Astra · enhanced head'),
  body:!!u.actor?.getObjectByName('Astra · enhanced body'),
  paws:(u.pivots||[]).filter(p=>/^stLeg[0-3]$/.test(p.node.name)).length,
  activeMotion:se224WolfGameMemory.get(u)?.kind||'idle'
 }))
});
