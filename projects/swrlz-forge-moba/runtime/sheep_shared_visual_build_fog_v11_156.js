// §E v11.156 — one shared host simulation, smooth guest display,
// all structure kinds replicated, and sheep-team sight from sheep + houses.
const se156={tracks:new Map(),raf:0,alive:false,fogAt:0,fogSession:null,
  mirrored:0,buildAcks:0,clock:0};

// Native Sheep Tag accepts farms, fortified houses, walls, ramps and totems.
// v11.152's initial three-kind filter silently skipped the latter types.
const se156PriorClientApply=se152ClientApply;
se152ClientApply=function(packet){
 const s=stSession,valid=!!s&&!!packet&&se152Guest()&&
  packet.roomId===se150Match.roomId&&packet.matchId===se150Match.matchId&&
  Number.isInteger(packet.seq)&&packet.seq>se152.received&&
  Array.isArray(packet.units)&&packet.units.length<=128&&
  Array.isArray(packet.buildings)&&packet.buildings.length<=160;
 if(!valid)return se156PriorClientApply(packet);
 const items=packet.buildings.filter(item=>
  item&&typeof item.id==='string'&&item.id.length<=130&&
  Object.prototype.hasOwnProperty.call(ST_BUILDINGS,item.kind)&&
  Array.isArray(item.pos)&&item.pos.length===3&&item.pos.every(Number.isFinite));
 const keep=new Set(items.map(item=>item.id));
 // While the old three-kind mirror runs, retain the extra real house types.
 const oldRemove=stRemoveBuilding;
 stRemoveBuilding=function(b){
  if(se152Guest()&&keep.has(b.id))return;
  return oldRemove(b);
 };
 try{se156PriorClientApply(packet);}
 finally{stRemoveBuilding=oldRemove;}
 if(se152.received!==packet.seq)return;
 // Clone only authoritative buildings; never create from a guest preview.
 for(const item of items){
  const ownerIndex=packet.units.findIndex(u=>u.id===item.owner);
  const owner=ownerIndex>=0?
   (s.units.find(u=>u.id===item.owner)||s.units[ownerIndex])?.id:null;
  let b=s.buildings.find(v=>v.id===item.id&&v.hp>0);
  if(!b){
   b=s.buildings.find(v=>v.authored&&v.kind===item.kind&&v.hp>0&&
      Math.hypot(v.pos.x-item.pos[0],v.pos.z-item.pos[2])<.3);
  }
  if(!b){
   try{
    b=stNewBuilding(item.kind,item.pos[0],item.pos[2],owner,null,Number(item.rotation)||0);
    b.id=item.id;se156.mirrored++;
   }catch(e){console.warn('LAN building mirror',item.kind,e);continue;}
  }
  if(b.kind!==item.kind)continue;
  b.owner=owner||b.owner;
  b.hp=Math.max(0,Math.min(100000,Number(item.hp)||0));
  b.maxHp=Math.max(1,Number(item.maxHp)||b.maxHp);
  b.progress=Math.max(0,Math.min(1,Number(item.progress)||0));
  b.level=Math.max(1,Math.min(3,Number(item.level)||1));
  b.cost=Math.max(0,Number(item.cost)||0);
  b.income=Math.max(0,Number(item.income)||0);
  if(Number.isFinite(item.rotation)&&b.mesh){
   b.rotation=item.rotation;b.mesh.rotation.y=item.rotation;
  }
  if(!b.authored&&b.mesh&&b.baseScale)b.mesh.scale.y=
    b.baseScale.y*(.15+.85*b.progress);
 }
 // Original mirror already removes destroyed old farm types; also remove
 // extended kinds when the host no longer lists them.
 for(const b of s.buildings)
  if(b.hp>0&&!keep.has(b.id))oldRemove(b);
 // Keep logical owner-resource values bound to this client's local actors.
 for(const [i,remote] of packet.units.entries()){
  const local=s.units.find(u=>u.id===remote.id)||s.units[i];
  if(local&&local.id!==remote.id&&Number.isFinite(packet.resources?.[remote.id]))
   s.resources[local.id]=Math.max(0,packet.resources[remote.id]);
 }
 // Set new visual trajectories using the host's latest source positions.
 const now=performance.now();
 for(const unit of s.units){
  const target=se152.target.get(unit.id);
  if(!target)continue;
  const last=se156.tracks.get(unit.id);
  const interval=last?Math.max(85,Math.min(210,now-last.received)):130;
  const prev=last?.goal||{x:unit.pos.x,z:unit.pos.z,rot:unit.actor.rotation.y};
  const velocityX=(target.pos[0]-prev.x)/(interval/1000);
  const velocityZ=(target.pos[2]-prev.z)/(interval/1000);
  const lookahead=last?Math.min(.075,interval/2000):0;
  const predictX=Math.max(-.35,Math.min(.35,velocityX*lookahead));
  const predictZ=Math.max(-.35,Math.min(.35,velocityZ*lookahead));
  se156.tracks.set(unit.id,{from:{x:unit.pos.x,z:unit.pos.z,
    rot:unit.actor.rotation.y},
    goal:{x:target.pos[0],z:target.pos[2],rot:target.rot},
    draw:{x:target.pos[0]+predictX,z:target.pos[2]+predictZ,rot:target.rot},
    received:now,duration:Math.max(100,Math.min(180,interval))});
 }
 se156PaintTeamFog(s,true);
};

// Visual interpolation ONLY — host remains the sole gameplay simulation.
// Smooth target arrival and bounded prediction remove 130ms step/stop motion.
const se156PriorGuestFrame=se152GuestFrame;
se152GuestFrame=function(dt){
 if(!se152Guest()||!stSession)return;
 const now=performance.now();
 for(const u of stSession.units){
  const track=se156.tracks.get(u.id);
  if(!track||u.captured)continue;
  const t=Math.max(0,Math.min(1,(now-track.received)/track.duration));
  const eased=t*t*(3-2*t),x=u.pos.x,z=u.pos.z;
  u.pos.x=track.from.x+(track.draw.x-track.from.x)*eased;
  u.pos.z=track.from.z+(track.draw.z-track.from.z)*eased;
  const r=track.from.rot,delta=Math.atan2(Math.sin(track.draw.rot-r),Math.cos(track.draw.rot-r));
  u.actor.rotation.y=r+delta*eased;
  const traveled=Math.hypot(u.pos.x-x,u.pos.z-z);
  u.walkDistance+=traveled;
  u.walkBlend+=(Number(traveled>.001)-u.walkBlend)*Math.min(1,.16);
  stPlaceUnit(u);
  for(const pivot of u.pivots||[]){
   pivot.node.rotation.copy(pivot.rotation);
   if(/^stLeg/.test(pivot.node.name)){
    const index=Number(pivot.node.name.slice(5))||0;
    pivot.node.rotation.x+=Math.sin(u.walkDistance*9+(index===0||index===3?0:Math.PI))*.58*u.walkBlend;
   }
  }
 }
};
function se156VisualLoop(){
 if(!se156.alive||!se152Guest()){se156.raf=0;return;}
 se156GuestFrameOnce();
 se156.raf=requestAnimationFrame(se156VisualLoop);
}
function se156GuestFrameOnce(){se152GuestFrame(.016);}
const se156PriorStartWorld=se152StartWorld;
se152StartWorld=function(...args){
 const out=se156PriorStartWorld(...args);
 if(se150Match.role==='guest'&&typeof requestAnimationFrame==='function'&&!se156.alive){
  se156.alive=true;se156.raf=requestAnimationFrame(se156VisualLoop);
 }
 return out;
};
const se156PriorStopWorld=se152StopWorld;
se152StopWorld=function(...args){
 se156.alive=false;
 if(se156.raf&&typeof cancelAnimationFrame==='function')cancelAnimationFrame(se156.raf);
 se156.raf=0;se156.tracks.clear();se156.fogSession=null;
 return se156PriorStopWorld(...args);
};

// Host-accepted build order and subsequent structure creation are two events.
// Guard the active build path from being overwritten by joystick snapshots.
const se156PreviousMove=se155MoveGuestOnWorldTick;
se155MoveGuestOnWorldTick=function(...args){
 const suspended=[];
 if(stSession){
  for(const [peer,input] of se154.streams){
   const unit=stSession.units.find(u=>u.id===se152.seats.get(peer));
   if(unit?.order?.action==='build'){
    suspended.push([input,input.strength]);input.strength=0;
   }
  }
 }
 try{return se156PreviousMove(...args);}
 finally{for(const [input,strength] of suspended)input.strength=strength;}
};
const se156PreviousRemote=se152ApplyRemoteCommand;
se152ApplyRemoteCommand=function(peer,msg){
 const actor=stSession?.units.find(u=>u.id===se152.seats.get(peer));
 const before=actor?.order;
 const result=se156PreviousRemote(peer,msg);
 if(msg?.kind==='world-command'&&msg.action==='build'&&actor?.order?.action==='build'&&
  actor.order!==before){
  se152Send(peer.channel,{kind:'world-build-accepted',roomId:se150Match.roomId,
   matchId:se150Match.matchId,kind:actor.order.kind,
   site:[actor.order.siteX,actor.order.siteZ]});
 }
 return result;
};
const se156PrevGuestListen=se152WatchGuestConnection;
se152WatchGuestConnection=function(){
 se156PrevGuestListen();
 const conn=se151.guestConn;
 if(!conn||conn.se156Watched)return;
 conn.se156Watched=true;
 conn.on('data',raw=>{
  let msg;try{msg=typeof raw==='string'?JSON.parse(raw):raw;}catch{return;}
  if(msg?.kind==='world-build-accepted'&&msg.roomId===se150Match.roomId&&
    msg.matchId===se150Match.matchId){
   se156.buildAcks++;
   stUiFeedback('Host accepted house order; your sheep is approaching the site.');
   stUi.build=null;stUiClearPreview();
  }
 });
};

// Multiplayer sheep teammates share sight. Buildings reveal nearby ground
// for their owning sheep team; wolves do not inherit sheep-house vision.
// This uses actual game fog mesh + exploration memory, never an opaque overlay.
function se156TeamViewers(s){
 const role=s.role,range=(role==='wolf'?s.rules.wolfVision:s.rules.sheepVision)*
   (s.archive?.visionMultiplier??1);
 const viewers=s.units.filter(u=>u.kind===role&&!u.captured&&!u.isIllusion)
  .map(u=>({x:u.pos.x,z:u.pos.z,range}));
 if(role==='sheep'){
  const ownIds=new Set(s.units.filter(u=>u.kind==='sheep'&&!u.captured).map(u=>u.id));
  for(const b of s.buildings)if(b.hp>0&&ownIds.has(b.owner))
   viewers.push({x:b.pos.x,z:b.pos.z,range:Math.max(4,range*.64)});
 }
 return viewers;
}
const se156OriginalSeen=stSeenByRole;
stSeenByRole=function(entity,role=stSession?.role){
 const s=stSession;
 if(!s||!se150Match.active||s.rules.fogMode==='off')
  return se156OriginalSeen(entity,role);
 if(entity.kind===role||entity.captured&&role==='sheep')return true;
 if(entity.owner&&s.units.some(u=>u.id===entity.owner&&u.kind===role))return true;
 const p=entity.spirit?.position||entity.pos;
 if(!p)return false;
 const original=s.role;
 if(role!==original)return se156OriginalSeen(entity,role);
 return se156TeamViewers(s).some(v=>Math.hypot(v.x-p.x,v.z-p.z)<=v.range);
};
function se156PaintTeamFog(s,force=false){
 const f=s?.fog;
 if(!f||!se150Match.active||s.rules.fogMode==='off')return;
 const now=performance.now();
 if(!force&&se156.fogSession===s&&now-se156.fogAt<170)return;
 se156.fogAt=now;se156.fogSession=s;
 const viewers=se156TeamViewers(s),size=f.canvas.width;
 const scale=size/(f.extent*2),ctx=f.canvas.getContext('2d');
 if(!ctx)return;
 const memory=f.softMemory||(f.softMemory=document.createElement('canvas'));
 if(memory.width!==size||memory.height!==size){memory.width=memory.height=size;}
 const mem=memory.getContext('2d');if(!mem)return;
 const circle=(target,v)=>{
  const x=(v.x+f.extent)*scale,y=(v.z+f.extent)*scale;
  const r=v.range*scale;
  const gradient=target.createRadialGradient(x,y,r*.83,x,y,r);
  gradient.addColorStop(0,'rgba(255,255,255,1)');
  gradient.addColorStop(1,'rgba(255,255,255,0)');
  target.fillStyle=gradient;target.beginPath();target.arc(x,y,r,0,Math.PI*2);target.fill();
 };
 f.visible.fill(0);
 for(const v of viewers){
  const minX=Math.max(0,Math.floor((v.x-v.range+f.extent)/f.cellSize));
  const maxX=Math.min(f.width-1,Math.ceil((v.x+v.range+f.extent)/f.cellSize));
  const minZ=Math.max(0,Math.floor((v.z-v.range+f.extent)/f.cellSize));
  const maxZ=Math.min(f.width-1,Math.ceil((v.z+v.range+f.extent)/f.cellSize));
  for(let z=minZ;z<=maxZ;z++)for(let x=minX;x<=maxX;x++)
   if(Math.hypot((x+.5)*f.cellSize-f.extent-v.x,(z+.5)*f.cellSize-f.extent-v.z)<=v.range){
    const id=z*f.width+x;f.visible[id]=1;f.explored[id]=1;
   }
  mem.globalCompositeOperation='source-over';circle(mem,v);
 }
 ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;
 ctx.clearRect(0,0,size,size);
 ctx.fillStyle='rgba(10,21,30,.76)';ctx.fillRect(0,0,size,size);
 ctx.globalCompositeOperation='destination-out';
 ctx.globalAlpha=.65;ctx.drawImage(memory,0,0);
 ctx.globalAlpha=1;
 for(const v of viewers)circle(ctx,v);
 ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;
 f.texture.needsUpdate=true;
 // The guest has no native simulation tick, so refresh actual enemy and
 // building visibility from the replicated positions and shared team sight.
 for(const u of s.units){
  u.actor.visible=!u.captured&&stSeenByRole(u);
  if(u.spirit)u.spirit.visible=stSeenByRole(u);
 }
 for(const b of s.buildings)if(b.hp>0)b.mesh.visible=stSeenByRole(b);
}
const se156PriorSnapshot=se152Snapshot;
se152Snapshot=function(...args){
 const value=se156PriorSnapshot(...args);
 if(se150Match.active&&se150Match.role==='host')se156PaintTeamFog(stSession);
 return value;
};
const se156PriorStop=stopSession;
stopSession=function(...args){
 se156.alive=false;
 if(se156.raf&&typeof cancelAnimationFrame==='function')cancelAnimationFrame(se156.raf);
 se156.raf=0;se156.tracks.clear();se156.fogSession=null;se156.mirrored=0;se156.buildAcks=0;
 return se156PriorStop(...args);
};
window.SWYRL_ENGINE_LAN.visualSync=()=>({
 role:se150Match.role,smoothGuestFrames:se156.tracks.size,
 mirroredBuildings:se156.mirrored,hostBuildAcknowledgements:se156.buildAcks,
 teamSightViewers:stSession?se156TeamViewers(stSession).length:0,
 fogActive:!!stSession?.fog
});
