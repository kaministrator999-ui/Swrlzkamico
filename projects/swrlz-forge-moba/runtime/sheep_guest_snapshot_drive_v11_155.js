// §E v11.155 — apply host-ACKed guest joystick on the confirmed running
// host world-snapshot clock. No extra timer, backend, or second game simulation.
// Physical test v11.154: guest TX 68, host ACK 34, but host moves 0.
const se155={lastTick:0,ticks:0,moves:0,blocked:0,rejected:0,lastReason:'waiting',lastStrength:0};
function se155MoveGuestOnWorldTick(){
 if(!se150Match.active||se150Match.role!=='host'||!stSession)return;
 const now=Date.now();
 const dt=se155.lastTick?Math.min(.19,Math.max(.005,(now-se155.lastTick)/1000)):.13;
 se155.lastTick=now;se155.ticks++;
 const s=stSession;
 se152Roster(); // Stable host-owned player-seat allocation.
 let reason='no guest input';
 for(const [peer,intent] of se154.streams){
  const seat=se152.seats.get(peer);
  if(!seat||seat!==intent.id){se154.streams.delete(peer);reason='seat mismatch';se155.rejected++;continue;}
  if(now-intent.at>550){reason='stale joystick input';continue;}
  const strength=Number(intent.strength);
  se155.lastStrength=strength;
  if(!Number.isFinite(strength)||strength<.13){reason='joystick idle';continue;}
  const u=s.units.find(actor=>actor.id===seat);
  if(!u){reason='assigned sheep missing';se155.rejected++;continue;}
  if(u.captured){reason='sheep captured';continue;}
  if(s.winner){reason='match finished';continue;}
  if(u.kind==='wolf'&&s.elapsed<s.rules.headstart){reason='wolf head start';continue;}
  const x=Number(intent.x),z=Number(intent.z),speed=Number(u.speed);
  if(![x,z,speed].every(Number.isFinite)||speed<=0){reason='invalid direction or speed';se155.rejected++;continue;}
  const magnitude=Math.hypot(x,z);
  if(magnitude<.02){reason='zero stick direction';continue;}
  // Native collision geometry stays authoritative on the host.
  const distance=Math.min(1,speed*dt*Math.min(1,strength));
  const dx=x/magnitude*distance,dz=z/magnitude*distance;
  const radius=u.kind==='wolf'?ST_WOLF_RADIUS:ST_SHEEP_RADIUS;
  const atX=u.pos.x,atZ=u.pos.z;
  let nextX=atX,nextZ=atZ;
  if(!stBlocked(atX+dx,atZ+dz,radius)){nextX+=dx;nextZ+=dz;}
  else if(!stBlocked(atX+dx,atZ,radius)){nextX+=dx;}
  else if(!stBlocked(atX,atZ+dz,radius)){nextZ+=dz;}
  if(nextX===atX&&nextZ===atZ){
   reason='collision blocked';se155.blocked++;continue;
  }
  if(u.order)stSetOrder(u,null); // No residual bot/path order for a human guest.
  u.pos.x=nextX;u.pos.z=nextZ;
  u.actor.rotation.y=Math.atan2(dx,dz);
  u.walkDistance+=Math.hypot(nextX-atX,nextZ-atZ);
  stPlaceUnit(u);
  se155.moves++;
  se154.moved++; // Existing guest ACK protocol uses this number.
  reason='guest sheep moving';
 }
 se155.lastReason=reason;
}
const se155PreviousWorldSnapshot=se152Snapshot;
se152Snapshot=function(...args){
 if(se150Match.active&&se150Match.role==='host'){
  se155MoveGuestOnWorldTick();
 }
 const result=se155PreviousWorldSnapshot(...args);
 if(se150Match.active&&se150Match.role==='host'&&se150Match.badge){
  se150Match.badge.textContent='LAN HOST · shared world · guests '+se152.seats.size+
   ' · RX '+se154.rx+' · moved '+se155.moves+
   ' · ticks '+se155.ticks+' · '+se155.lastReason;
 }
 return result;
};
// The previous host-frame joystick implementation is bypassed for v2 packets
// to prevent doubled movement if a browser does invoke that legacy hook.
const se155OldNativeTick=stUpdate;
stUpdate=function(...args){
 if(se150Match.active&&se150Match.role==='host'&&se154.streams.size){
  const original=se154.streams;
  se154.streams=new Map();
  try{return se155OldNativeTick(...args);}
  finally{se154.streams=original;}
 }
 return se155OldNativeTick(...args);
};
// Acknowledge application results, not only network receipt.
const se155OldAck=se154GuestLabel;
se154GuestLabel=function(){
 se155OldAck();
 if(se150Match.active&&se150Match.role==='guest'&&se150Match.badge){
  const ack=se154.lastAck;
  const suffix=ack?
   ' · host blocked '+Number(ack.blocked||0):
   ' · waiting for host';
  se150Match.badge.textContent+=suffix;
 }
};
const se155OldStop=stopSession;
stopSession=function(...args){
 se155.lastTick=0;se155.ticks=0;se155.moves=0;
 se155.blocked=0;se155.rejected=0;se155.lastReason='stopped';
 se155.lastStrength=0;
 return se155OldStop(...args);
};
window.SWYRL_ENGINE_LAN.guestMovement=()=>({
 active:se150Match.active,role:se150Match.role,
 hostSnapshotTicks:se155.ticks,
 hostAppliedMovementFrames:se155.moves,
 hostBlockedFrames:se155.blocked,
 hostRejectedCommands:se155.rejected,
 hostLastReason:se155.lastReason,
 hostLastStrength:se155.lastStrength,
 guestInputTX:se154.tx,
 guestInputACK:se154.ack,
 lastHostACK:se154.lastAck
});
