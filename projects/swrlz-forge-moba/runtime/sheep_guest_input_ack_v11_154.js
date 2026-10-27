// §E v11.154 — explicit peer-bound guest inputs and HOST acknowledgements.
// Shared world snapshots and game logic from v11.152 remain unchanged.
// Never label a local send attempt as proof the host received it.
const se154={
 streams:new Map(),tx:0,rx:0,accepted:0,moved:0,blocked:0,ack:0,
 hostMoved:0,lastAck:null,lastHostInputAt:0,clientSeq:0
};
function se154Packet(raw){
 if(typeof raw==='string'){
  if(raw.length>4000)return null;
  try{return JSON.parse(raw);}catch{return null;}
 }
 return raw&&typeof raw==='object'?raw:null;
}
function se154HostMessage(peer,conn,raw){
 const msg=se154Packet(raw);
 if(!msg||msg.kind!=='guest-stick-v2')return;
 se154.rx++;
 if(!se150Match.active||se150Match.role!=='host'||!stSession||
    msg.roomId!==se150Match.roomId||msg.matchId!==se150Match.matchId){
  return;
 }
 // Validate against the server-owned peer entry, not the claimed actor id.
 if(!se152.seats.has(peer))se152Roster();
 const actorId=se152.seats.get(peer),unit=stSession.units.find(u=>u.id===actorId);
 if(!actorId||!unit)return;
 const x=Number(msg.x),z=Number(msg.z),strength=Number(msg.strength);
 const seq=Number(msg.seq);
 if(![x,z,strength,seq].every(Number.isFinite)||seq<1||
    seq>1000000000||Math.abs(x)>1.001||Math.abs(z)>1.001||
    strength<0||strength>1.001)return;
 const old=se154.streams.get(peer);
 if(old&&seq<=old.seq)return;
 const length=Math.hypot(x,z);
 const now=Date.now();
 se154.streams.set(peer,{id:actorId,seq,x:length>.0001?x/length:0,
  z:length>.0001?z/length:0,strength,at:now,conn});
 se154.accepted++;
 se154.lastHostInputAt=now;
 // Round-trip acknowledgement proves the host actually received the input.
 // Periodic sends avoid flooding the WebRTC channel.
 if(!old||now-(old.ackedAt||0)>360){
  const record=se154.streams.get(peer);
  record.ackedAt=now;
  se152Send(conn,{kind:'guest-stick-ack-v2',roomId:se150Match.roomId,
   matchId:se150Match.matchId,seq,actorId,rx:se154.accepted,
   moved:se154.moved,blocked:se154.blocked});
 }
}
const se154PriorAttach=se151HostAttach;
se151HostAttach=function(conn,serial){
 const count=se149Peer.links.length;
 se154PriorAttach(conn,serial);
 const entry=se149Peer.links.length>count?se149Peer.links.at(-1):null;
 if(!entry?.cloud)return;
 // Attached to the real incoming PeerJS connection. No synthetic UI event.
 conn.on('data',raw=>se154HostMessage(entry,conn,raw));
 conn.on('close',()=>se154.streams.delete(entry));
};
function se154ReceiveAck(raw){
 const message=se154Packet(raw);
 if(!message||message.kind!=='guest-stick-ack-v2'||!se150Match.active||
    se150Match.role!=='guest'||message.roomId!==se150Match.roomId||
    message.matchId!==se150Match.matchId)return;
 se154.ack++;
 se154.lastAck=message;
 if(se150Match.badge)se154GuestLabel();
}
const se154PriorWatchGuest=se152WatchGuestConnection;
se152WatchGuestConnection=function(){
 se154PriorWatchGuest();
 const conn=se151.guestConn;
 if(!conn||conn.se154Watched)return;
 conn.se154Watched=true;
 conn.on('data',se154ReceiveAck);
};
function se154GuestLabel(){
 if(!se150Match.badge)return;
 const active=stMobile.pointer!==null&&stMobile.strength>.13;
 const base='LAN GUEST · world '+se152.received+
  ' · joystick '+(active?'ACTIVE':'idle')+
  ' · TX '+se154.tx+' · host ACK '+se154.ack;
 const tail=se154.lastAck?' · host moves '+Number(se154.lastAck.moved||0):' · awaiting host reply';
 se150Match.badge.textContent=base+tail;
}
const se154PreviousControls=se152GuestControls;
se152GuestControls=function(){
 if(!se152Guest()||!se152.assigned)return;
 const joy=stMobile;
 const down=joy.enabled&&joy.pointer!==null&&joy.session===stSession;
 const amount=down?Math.max(0,Math.min(1,Number(joy.strength)||0)):0;
 const x=down?Math.max(-1,Math.min(1,Number(joy.x)||0)):0;
 const z=down?Math.max(-1,Math.min(1,Number(joy.y)||0)):0;
 se154.clientSeq++;
 const packet={kind:'guest-stick-v2',roomId:se150Match.roomId,
  matchId:se150Match.matchId,seq:se154.clientSeq,x,z,strength:amount};
 se152Send(se151.guestConn,packet);
 se154.tx++;
 se154GuestLabel();
};
const se154PreviousUpdate=stUpdate;
stUpdate=function(dt,t){
 if(se150Match.active&&se150Match.role==='host'&&stSession&&!paused){
  const s=stSession,now=Date.now();
  const frame=Math.max(0,Math.min(.05,Number(dt)||0));
  for(const [peer,input] of se154.streams){
   if(!se152.seats.has(peer)||se152.seats.get(peer)!==input.id){
    se154.streams.delete(peer);continue;
   }
   if(now-input.at>420||input.strength<.13||frame<=0||s.winner)continue;
   const u=s.units.find(item=>item.id===input.id);
   if(!u||u.captured||(u.kind==='wolf'&&s.elapsed<s.rules.headstart))continue;
   // The guest owns this actor's immediate intent. Cancel stale bot orders.
   if(u.order)stSetOrder(u,null);
   const dx=input.x*u.speed*frame*input.strength;
   const dz=input.z*u.speed*frame*input.strength;
   const radius=u.kind==='wolf'?ST_WOLF_RADIUS:ST_SHEEP_RADIUS;
   let xx=u.pos.x,zz=u.pos.z;
   if(!stBlocked(xx+dx,zz+dz,radius)){xx+=dx;zz+=dz;}
   else if(!stBlocked(xx+dx,zz,radius)){xx+=dx;}
   else if(!stBlocked(xx,zz+dz,radius)){zz+=dz;}
   if(xx!==u.pos.x||zz!==u.pos.z){
    const distance=Math.hypot(xx-u.pos.x,zz-u.pos.z);
    u.pos.x=xx;u.pos.z=zz;
    u.actor.rotation.y=Math.atan2(input.x,input.z);
    u.walkDistance+=distance;
    stPlaceUnit(u);
    se154.moved++;
   }else se154.blocked++;
  }
 }
 const output=se154PreviousUpdate(dt,t);
 return output;
};
const se154PreviousSnapshot=se152Snapshot;
se152Snapshot=function(...args){
 const output=se154PreviousSnapshot(...args);
 if(se150Match.active&&se150Match.role==='host'&&se150Match.badge){
  se150Match.badge.textContent='LAN HOST · '+(se152.seats.size+1)+' players'+
   ' · guest RX '+se154.rx+' · moved '+se154.moved+
   (se154.blocked?' · blocked '+se154.blocked:'');
 }
 return output;
};
const se154PreviousStop=stopSession;
stopSession=function(...args){
 se154.streams.clear();
 se154.tx=0;se154.rx=0;se154.accepted=0;
 se154.moved=0;se154.blocked=0;se154.ack=0;
 se154.lastAck=null;se154.clientSeq=0;se154.lastHostInputAt=0;
 return se154PreviousStop(...args);
};
window.SWYRL_ENGINE_LAN.guestInput=()=>({
 active:se150Match.active,role:se150Match.role,
 assignedUnit:se152.assigned,snapshots:se152.received,
 joystickPointer:stMobile.pointer!==null,
 joystickStrength:Number((Number(stMobile.strength)||0).toFixed(2)),
 attemptedSends:se154.tx,hostAcknowledgements:se154.ack,
 hostPacketsReceived:se154.rx,hostPacketsAccepted:se154.accepted,
 hostMovementFrames:se154.moved,hostBlockedFrames:se154.blocked,
 lastAcknowledgement:se154.lastAck
});
