// §E v11.161 — continuous guest rendering between authoritative snapshots.
// Keep the proven host's game logic, 130-ms world clock, build sync and LAN
// discovery unchanged. Render exactly once per requestAnimationFrame on guest.
const se161={tracks:new Map(),frames:0,packets:0,lastFrame:0,
  lastSeq:0,staleFrames:0,teleports:0,lastAge:0,world:null};
const se161OriginalApply=se152ClientApply;
se152ClientApply=function(packet){
 const receivedBefore=se152.received;
 const result=se161OriginalApply(packet);
 if(!se152Guest()||!stSession||!packet||
    !Array.isArray(packet.units)||packet.seq!==se152.received||
    packet.seq<=receivedBefore)return result;
 const s=stSession,at=performance.now();
 if(se161.world!==s){se161.world=s;se161.tracks.clear();se161.lastFrame=0;}
 for(let index=0;index<packet.units.length;index++){
  const remote=packet.units[index];
  if(!Array.isArray(remote?.pos)||remote.pos.length!==3||
      !remote.pos.every(Number.isFinite))continue;
  const u=s.units.find(x=>x.id===remote.id)||
   (s.units[index]?.kind===remote.kind?s.units[index]:null);
  if(!u)continue;
  const x=remote.pos[0],z=remote.pos[2],prev=se161.tracks.get(u.id);
  const gap=prev?Math.max(.03,Math.min(.5,(at-prev.at)/1000)):.13;
  const dx=prev?x-prev.x:0,dz=prev?z-prev.z:0;
  const jump=Math.hypot(dx,dz);
  const teleport=prev&&jump>Math.max(3.2,(Number(u.speed)||5.4)*gap*3);
  const allowedSpeed=Math.max(1,Math.min(22,(Number(u.speed)||5.4)*1.6));
  let vx=jump>.006?dx/gap:0,vz=jump>.006?dz/gap:0;
  const speed=Math.hypot(vx,vz);
  if(speed>allowedSpeed){vx*=allowedSpeed/speed;vz*=allowedSpeed/speed;}
  if(prev&&!teleport&&jump>.006){
   vx=prev.vx*.22+vx*.78;
   vz=prev.vz*.22+vz*.78;
  }
  if(teleport){
   u.pos.x=x;u.pos.z=z;stPlaceUnit(u);se161.teleports++;
   vx=0;vz=0;
  }
  se161.tracks.set(u.id,{
   x,z,vx,vz,rot:Number(remote.rot)||0,at,
   captured:!!remote.captured
  });
 }
 se161.packets++;
 se161.lastSeq=packet.seq;
 return result;
};

// The original v11.156 smoothstep restarted from zero velocity at EVERY
// network packet. At 130-ms packet cadence this looked like step/stop/step.
// Instead, predict a bounded distance from latest host position and approach
// it with continuous exponential correction; no per-packet easing restart.
se152GuestFrame=function(){
 if(!se152Guest()||!stSession)return;
 const now=performance.now(),prevFrame=se161.lastFrame;
 const delta=prevFrame?Math.max(.008,Math.min(.05,(now-prevFrame)/1000)):.016;
 se161.lastFrame=now;se161.frames++;
 const alpha=1-Math.exp(-delta/.055);
 for(const u of stSession.units){
  const track=se161.tracks.get(u.id);
  if(!track||u.captured)continue;
  const age=Math.max(0,(now-track.at)/1000);
  se161.lastAge=age;
  if(age>.32)se161.staleFrames++;
  // Predict through ordinary packet jitter without allowing unlimited drift
  // during connection loss. Positions still converge to host authority.
  const lead=Math.min(.24,age);
  const goalX=track.x+track.vx*lead;
  const goalZ=track.z+track.vz*lead;
  const oldX=u.pos.x,oldZ=u.pos.z;
  const error=Math.hypot(goalX-oldX,goalZ-oldZ);
  if(error>4){
   u.pos.x=track.x;u.pos.z=track.z;
  }else{
   u.pos.x+=(goalX-u.pos.x)*alpha;
   u.pos.z+=(goalZ-u.pos.z)*alpha;
  }
  const turn=Math.atan2(
   Math.sin(track.rot-u.actor.rotation.y),
   Math.cos(track.rot-u.actor.rotation.y));
  u.actor.rotation.y+=turn*alpha;
  const traveled=Math.hypot(u.pos.x-oldX,u.pos.z-oldZ);
  u.walkDistance+=traveled;
  u.walkBlend+=(Number(traveled>.0008)-u.walkBlend)*Math.min(1,delta*12);
  stPlaceUnit(u);
  for(const pivot of u.pivots||[]){
   pivot.node.rotation.copy(pivot.rotation);
   if(/^stLeg/.test(pivot.node.name)){
    const index=Number(pivot.node.name.slice(5))||0;
    pivot.node.rotation.x+=Math.sin(u.walkDistance*9+
      (index===0||index===3?0:Math.PI))*.58*u.walkBlend;
   }
  }
 }
};

// v11.156 already owns one guest requestAnimationFrame loop. The native
// stUpdate wrapper also invoked se152GuestFrame and doubled render updates.
// Do not run a second guest animation from the native simulation hook.
const se161OriginalUpdate=stUpdate;
stUpdate=function(...args){
 if(se150Match.active&&se150Match.role==='guest')return;
 return se161OriginalUpdate(...args);
};
const se161OriginalStop=se152StopWorld;
se152StopWorld=function(...args){
 se161.tracks.clear();se161.frames=0;se161.packets=0;
 se161.lastFrame=0;se161.lastSeq=0;se161.staleFrames=0;
 se161.teleports=0;se161.lastAge=0;se161.world=null;
 return se161OriginalStop(...args);
};
window.SWYRL_ENGINE_LAN.motion=()=>({
 active:se150Match.active,role:se150Match.role,
 rendering:se156.alive,
 frames:se161.frames,hostPackets:se161.packets,
 lastHostSeq:se161.lastSeq,
 lastPacketAgeMs:Math.round(se161.lastAge*1000),
 staleFrames:se161.staleFrames,
 teleports:se161.teleports,
 trackedUnits:se161.tracks.size
});
