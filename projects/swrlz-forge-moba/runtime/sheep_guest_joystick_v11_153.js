// §E v11.153 — mobile guest joystick -> real host-controlled animal.
// Keep one host simulation. Guest sends intent; host moves the assigned unit
// on native game frames with the existing collision rules, not a second AI.
const se153={inputs:new Map(),tx:0,rx:0,moves:0,lastActive:0};
const se153OriginalCanMove=stMobileCanMove;
stMobileCanMove=function(){
 if(se150Match.active&&se150Match.role==='guest'){
  const s=stSession;
  return !!s&&!s.simulate&&stUi.shown&&!paused&&!s.winner&&
   !!se152.assigned&&!!se151.guestConn?.open&&
   (s.role!=='wolf'||stHuntReleased(s));
 }
 return se153OriginalCanMove();
};
const se153OriginalGuestControls=se152GuestControls;
se152GuestControls=function(){
 if(!se152Guest()||!se152.assigned)return;
 const m=stMobile;
 // The guest has no local stUpdate() simulation. Do not require its local
 // movement pipeline to have run before forwarding pointer intent.
 const down=m.pointer!==null&&m.session===stSession&&m.enabled;
 const amount=down?Math.max(0,Math.min(1,Number(m.strength)||0)):0;
 const direction={
  x:amount?Math.max(-1,Math.min(1,Number(m.x)||0)):0,
  z:amount?Math.max(-1,Math.min(1,Number(m.y)||0)):0,
  strength:amount
 };
 const packet={kind:'world-stick',roomId:se150Match.roomId,matchId:se150Match.matchId,...direction};
 se152Send(se151.guestConn,packet);
 se153.tx++;
 if(amount>.13)se153.lastActive=Date.now();
 if(se150Match.badge&&se152.received>0){
  se150Match.badge.textContent='LAN GUEST · shared world · '+se152.received+
   ' frames · joystick '+(amount>.13?'ACTIVE':'idle')+' · '+se153.tx+' sent';
 }
};
const se153OriginalHostCommand=se152ApplyRemoteCommand;
se152ApplyRemoteCommand=function(peer,message){
 if(message?.kind!=='world-stick')return se153OriginalHostCommand(peer,message);
 if(!se150Match.active||se150Match.role!=='host'||!stSession||
    message.roomId!==se150Match.roomId||message.matchId!==se150Match.matchId||
    !se152.seats.has(peer))return;
 const x=Number(message.x),z=Number(message.z),strength=Number(message.strength);
 if(![x,z,strength].every(Number.isFinite))return;
 const now=Date.now();
 if(now-(peer.se153RxAt||0)<28)return;
 peer.se153RxAt=now;se153.rx++;
 const magnitude=Math.hypot(x,z);
 const amount=Math.max(0,Math.min(1,strength));
 const intent={id:se152.seats.get(peer),
   x:magnitude>.00001?x/magnitude:0,
   z:magnitude>.00001?z/magnitude:0,
   strength:amount,last:now};
 se153.inputs.set(peer,intent);
};
const se153BaseUpdate=stUpdate;
stUpdate=function(dt,t){
 if(se150Match.active&&se150Match.role==='host'&&stSession&&!paused){
  const s=stSession,step=Math.min(.05,Math.max(0,Number(dt)||0)),now=Date.now();
  for(const [peer,intent] of se153.inputs){
   if(!se152.seats.has(peer)||se152.seats.get(peer)!==intent.id){
    se153.inputs.delete(peer);continue;
   }
   if(now-intent.last>360||intent.strength<.13)continue;
   const unit=s.units.find(u=>u.id===intent.id);
   if(!unit||unit.captured||s.winner||
     (unit.kind==='wolf'&&s.elapsed<s.rules.headstart))continue;
   if(unit.order&&!unit.order.remoteStick)stSetOrder(unit,null);
   const radius=unit.kind==='wolf'?ST_WOLF_RADIUS:ST_SHEEP_RADIUS;
   const distance=unit.speed*step*intent.strength;
   if(distance<=0)continue;
   const dx=intent.x*distance,dz=intent.z*distance;
   let x=unit.pos.x,z=unit.pos.z;
   if(!stBlocked(x+dx,z+dz,radius)){x+=dx;z+=dz;}
   else if(!stBlocked(x+dx,z,radius))x+=dx;
   else if(!stBlocked(x,z+dz,radius))z+=dz;
   if(x!==unit.pos.x||z!==unit.pos.z){
    unit.pos.x=x;unit.pos.z=z;unit.actor.rotation.y=Math.atan2(intent.x,intent.z);
    unit.walkDistance+=Math.hypot(x-unit.pos.x,z-unit.pos.z);
    stPlaceUnit(unit);se153.moves++;
   }
  }
 }
 return se153BaseUpdate(dt,t);
};
const se153PreviousStop=stopSession;
stopSession=function(...args){
 se153.inputs.clear();se153.tx=0;se153.rx=0;se153.moves=0;
 return se153PreviousStop(...args);
};
window.SWYRL_ENGINE_LAN.guestInput=()=>({
 active:se150Match.active,role:se150Match.role,
 assignedUnit:se152.assigned,
 joystickPointer:stMobile.pointer!==null,
 joystickStrength:Math.round((Number(stMobile.strength)||0)*100)/100,
 packetsSent:se153.tx,packetsReceived:se153.rx,movementFrames:se153.moves
});
