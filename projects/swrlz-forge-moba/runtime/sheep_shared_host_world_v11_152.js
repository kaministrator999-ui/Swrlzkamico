// §E v11.152 — one host-authoritative Sheep Tag world over existing WebRTC DataChannels.
// Host runs the native simulation; guests send bounded orders and render snapshots.
// No duplicate renderer, scene or simulation clock.
const se152={
 seats:new Map(),seq:0,received:0,timer:null,target:new Map(),assigned:'',
 lastJoystick:0,startedAt:0
};
function se152Connected(){
 return !!se150Match.active&&!!stSession;
}
function se152Guest(){
 return se152Connected()&&se150Match.role==='guest'&&se151.guestConn?.open;
}
function se152Packet(raw){
 if(typeof raw==='string'){
  if(raw.length>90000)return null;
  try{return JSON.parse(raw);}catch{return null;}
 }
 return raw&&typeof raw==='object'?raw:null;
}
function se152Send(connection,packet){
 try{
  if(connection?.open)connection.send(JSON.stringify(packet));
  else if(connection?.readyState==='open')connection.send(JSON.stringify(packet));
 }catch(error){console.warn('Sheep Tag LAN data send failed',error);}
}
function se152Roster(){
 const s=stSession;
 if(!s)return;
 // The host owns the first sheep. Other real peers get different controllable
 // actors (remaining sheep, then wolves); no guest may control the host's sheep.
 const all=s.units.filter(u=>!u.captured);
 const reserved=new Set([s.controlledId]);
 const peers=se149Peer.links.filter(p=>p.cloud&&p.name&&p.channel?.readyState==='open');
 for(const peer of peers){
  let id=se152.seats.get(peer);
  if(!all.some(u=>u.id===id)||reserved.has(id))id='';
  if(!id){
   const candidate=all.find(u=>u.kind==='sheep'&&!reserved.has(u.id))||
      all.find(u=>!reserved.has(u.id));
   id=candidate?.id||'';
  }
  if(id){reserved.add(id);se152.seats.set(peer,id);}
 }
 for(const peer of [...se152.seats.keys()])if(!peers.includes(peer))se152.seats.delete(peer);
}
function se152Snapshot(){
 if(!se152Connected()||se150Match.role!=='host')return;
 const s=stSession;se152Roster();
 const game={
  kind:'world',roomId:se150Match.roomId,matchId:se150Match.matchId,
  seq:++se152.seq,elapsed:s.elapsed,winner:s.winner,message:s.message,
  resources:{...s.resources},
  units:s.units.map(u=>({
   id:u.id,kind:u.kind,pos:[u.pos.x,u.pos.y,u.pos.z],
   rot:u.actor.rotation.y,walk:u.walkDistance,
   captured:!!u.captured,spirit:u.spirit?
    [u.spirit.position.x,u.spirit.position.y,u.spirit.position.z]:null,
   level:u.level,speed:u.speed,damage:u.damage
  })),
  buildings:s.buildings.filter(b=>b.hp>0).map(b=>({
   id:b.id,kind:b.kind,pos:[b.pos.x,b.pos.y,b.pos.z],
   owner:b.owner,hp:b.hp,progress:b.progress,level:b.level,
   maxHp:b.maxHp,income:b.income,cost:b.cost
  }))
 };
 for(const [peer,id] of se152.seats){
  se152Send(peer.channel,{...game,you:id});
 }
 if(se150Match.badge)se150Match.badge.textContent=
   'LAN HOST · world authority · '+(se152.seats.size+1)+' players · live sync';
}
function se152StartWorld(){
 if(se152.timer)clearInterval(se152.timer);
 se152.startedAt=Date.now();se152.seq=0;se152.received=0;
 se152.target.clear();se152.seats.clear();se152.assigned='';
 if(se150Match.role==='host'){
  se152Roster();se152Snapshot();
  se152.timer=setInterval(se152Snapshot,130);
 }else if(se150Match.role==='guest'){
  se152.timer=setInterval(se152GuestControls,115);
  if(se150Match.badge)se150Match.badge.textContent='LAN GUEST · waiting for host world';
 }
}
function se152StopWorld(){
 if(se152.timer)clearInterval(se152.timer);
 se152.timer=null;se152.target.clear();se152.seats.clear();
 se152.assigned='';se152.seq=0;se152.received=0;
}
function se152ClientApply(data){
 if(!se152Guest()||!data||data.matchId!==se150Match.matchId||
    data.roomId!==se150Match.roomId||data.seq<=se152.received)return;
 if(!Array.isArray(data.units)||data.units.length>128||
    !Array.isArray(data.buildings)||data.buildings.length>160)return;
 const s=stSession;se152.received=data.seq;
 if(Number.isFinite(data.elapsed))s.elapsed=Math.max(0,Math.min(s.rules.duration,data.elapsed));
 s.winner=data.winner==='sheep'||data.winner==='wolves'?data.winner:null;
 s.message=String(data.message||'').slice(0,250);
 if(data.resources&&typeof data.resources==='object'){
  for(const u of s.units)if(Number.isFinite(Number(data.resources[u.id])))
   s.resources[u.id]=Math.max(0,Number(data.resources[u.id]));
 }
 const controlled=s.units.find(u=>u.id===data.you)||
  s.units[data.units.findIndex(u=>u.id===data.you)]; // same authored order if local scene IDs differ
 if(controlled){
  if(se152.assigned!==controlled.id){
   se152.assigned=controlled.id;
   s.controlledId=controlled.id;s.selectedId=controlled.id;
   s.role=controlled.kind;
   s.simulate=false;
   stUi.build=null;stUiClearPreview();
   stUi.follow=true;
   stUiFeedback('Playing as '+controlled.name+' in the host world.');
  }
 }
 for(const [index,state] of data.units.entries()){
  const u=s.units.find(x=>x.id===state.id)||
   (s.units[index]?.kind===state.kind?s.units[index]:null);
  if(!u||!Array.isArray(state.pos)||state.pos.length!==3||
      !state.pos.every(Number.isFinite))continue;
  const captured=!!state.captured;
  if(captured&&!u.captured){
   u.captured=true;u.actor.visible=false;
   if(!u.spirit){u.spirit=stMakeSpirit();scene.add(u.spirit);}
  }else if(!captured&&u.captured){
   u.captured=false;u.actor.visible=true;
   if(u.spirit)stDisposeVisual(u.spirit);
   u.spirit=null;
  }
  if(captured&&u.spirit&&Array.isArray(state.spirit)&&state.spirit.length===3&&state.spirit.every(Number.isFinite))
   u.spirit.position.set(...state.spirit);
  se152.target.set(u.id,{pos:state.pos,rot:Number(state.rot)||0});
  u.level=Number(state.level)||u.level;
  if(Number.isFinite(state.speed))u.speed=state.speed;
  if(Number.isFinite(state.damage))u.damage=state.damage;
 }
 const ids=new Set();
 for(const item of data.buildings){
  if(typeof item.id!=='string'||item.id.length>130||
     !['st-farm','st-income','st-fort'].includes(item.kind)||
     !Array.isArray(item.pos)||item.pos.length!==3||!item.pos.every(Number.isFinite))continue;
  ids.add(item.id);
  let b=s.buildings.find(x=>x.id===item.id);
  if(!b){
   b=stNewBuilding(item.kind,item.pos[0],item.pos[2],item.owner||null);
   b.id=item.id; // Replica identity comes from the authoritative host.
  }
  if(b.kind!==item.kind)continue;
  b.hp=Math.max(0,Math.min(10000,Number(item.hp)||0));
  b.maxHp=Math.max(1,Number(item.maxHp)||b.maxHp);
  b.progress=Math.max(0,Math.min(1,Number(item.progress)||0));
  b.level=Math.max(1,Math.min(3,Number(item.level)||1));
  b.income=Math.max(0,Number(item.income)||0);
  b.cost=Math.max(0,Number(item.cost)||0);
  b.owner=item.owner||b.owner;
  if(!b.authored)b.mesh.scale.y=.15+.85*b.progress;
  else b.mesh.visible=true;
 }
 for(const b of s.buildings)if(b.hp>0&&!ids.has(b.id))stRemoveBuilding(b);
 if(se150Match.badge)se150Match.badge.textContent=
  'LAN GUEST · host world synchronized · frame '+se152.received;
}
function se152GuestFrame(dt){
 if(!stSession)return;
 const s=stSession,alpha=Math.min(1,Math.max(.05,(Number(dt)||.016)*13));
 for(const u of s.units){
  const state=se152.target.get(u.id);
  if(!state||u.captured)continue;
  const beforeX=u.pos.x,beforeZ=u.pos.z;
  u.pos.x+=(state.pos[0]-u.pos.x)*alpha;
  u.pos.z+=(state.pos[2]-u.pos.z)*alpha;
  u.actor.rotation.y+=Math.atan2(Math.sin(state.rot-u.actor.rotation.y),Math.cos(state.rot-u.actor.rotation.y))*alpha;
  stPlaceUnit(u);
  const distance=Math.hypot(u.pos.x-beforeX,u.pos.z-beforeZ);
  u.walkDistance+=distance;
  u.walkBlend+=(Number(distance>.002)-u.walkBlend)*Math.min(1,alpha);
  for(const pivot of u.pivots){
   pivot.node.rotation.copy(pivot.rotation);
   if(/^stLeg/.test(pivot.node.name)){
    const index=Number(pivot.node.name.slice(5))||0;
    pivot.node.rotation.x+=Math.sin(u.walkDistance*9+(index===0||index===3?0:Math.PI))*.58*u.walkBlend;
   }
  }
 }
}
function se152GuestControls(){
 if(!se152Guest()||!se152.assigned)return;
 const m=stMobile;
 const valid=m.pointer!==null&&m.session===stSession&&stMobileCanMove();
 const direction=valid?
   {x:Math.max(-1,Math.min(1,m.x)),z:Math.max(-1,Math.min(1,m.y)),
    strength:Math.max(0,Math.min(1,m.strength))}:
   {x:0,z:0,strength:0};
 se152Send(se151.guestConn,{kind:'world-stick',matchId:se150Match.matchId,roomId:se150Match.roomId,...direction});
}
function se152ApplyRemoteCommand(peer,message){
 if(!se152Connected()||se150Match.role!=='host'||
   message.matchId!==se150Match.matchId||message.roomId!==se150Match.roomId)return;
 const id=se152.seats.get(peer),s=stSession;
 if(!id)return;
 const actor=s.units.find(x=>x.id===id);
 if(!actor)return;
 const now=Date.now();if(now-(peer.lastInput||0)<36)return;
 peer.lastInput=now;
 if(message.kind==='world-stick'){
  const x=Number(message.x),z=Number(message.z),strength=Number(message.strength);
  if(![x,z,strength].every(Number.isFinite))return;
  const amount=Math.max(0,Math.min(1,strength)),unit=s.units.find(x=>x.id===id);
  if(!unit)return;
  if(amount<.13){
   if(unit.order?.remoteStick)stSetOrder(unit,null);
   return;
  }
  const radius=unit.kind==='wolf'?ST_WOLF_RADIUS:ST_SHEEP_RADIUS;
  const length=Math.hypot(x,z)||1;
  const nx=Math.max(-1,Math.min(1,x))/length,nz=Math.max(-1,Math.min(1,z))/length;
  const target={x:unit.pos.x+nx*1.7*amount,z:unit.pos.z+nz*1.7*amount};
  if(!stBlocked(target.x,target.z,radius)){
   stSetOrder(unit,{action:'move',x:target.x,z:target.z,remoteStick:true});
  }
  return;
 }
 if(message.kind!=='world-command'||typeof message.action!=='string')return;
 const allowed=['move','build','attack','rescue','sell','upgrade','wolf-upgrade'];
 if(!allowed.includes(message.action))return;
 const payload=message.payload&&typeof message.payload==='object'?message.payload:{};
 if(JSON.stringify(payload).length>700)return;
 const priorControlled=s.controlledId,priorSelected=s.selectedId;
 try{
  s.controlledId=id;s.selectedId=id;
  const result=se152BaseCommand(message.action,payload);
  if(!result.ok)se152Send(peer.channel,{kind:'world-feedback',matchId:se150Match.matchId,text:result.reason});
 }finally{s.controlledId=priorControlled;s.selectedId=priorSelected;}
}
// Host peer listener attaches to the same verified room connection already
// used for the lobby. Never accept game input from arbitrary browser messages.
const se152BaseAttach=se151HostAttach;
se151HostAttach=function(conn,serial){
 const count=se149Peer.links.length;
 se152BaseAttach(conn,serial);
 // This connection is added synchronously, even before the channel opens.
 const peer=se149Peer.links.length>count?se149Peer.links.at(-1):null;
 if(!peer||!peer.cloud)return;
 conn.on('data',value=>{
  const msg=se152Packet(value);
  if(msg&&['world-stick','world-command'].includes(msg.kind))se152ApplyRemoteCommand(peer,msg);
 });
};
function se152WatchGuestConnection(){
 const conn=se151.guestConn;
 if(!conn||conn.se152Watched)return;
 conn.se152Watched=true;
 conn.on('data',value=>{
  const msg=se152Packet(value);
  if(!msg)return;
  if(msg.kind==='world')se152ClientApply(msg);
  else if(msg.kind==='world-feedback'&&msg.matchId===se150Match.matchId)
   stUiFeedback(String(msg.text||'').slice(0,180),true);
 });
}
const se152BaseJoin=se151JoinGame;
se151JoinGame=async function(...args){
 await se152BaseJoin(...args);
 // PeerJS 'open' fires after the async join function returns. Attach after
 // its original listener constructs se151.guestConn, not before.
 se152WatchGuestConnection();
 se151.peer?.on('open',()=>se152WatchGuestConnection());
};
const se152BaseStart=se150HostStart;
se150HostStart=function(...args){
 const ok=se152BaseStart(...args);
 if(ok)se152StartWorld();
 return ok;
};
const se152BasePeerPacket=se150PeerPacket;
se150PeerPacket=function(raw){
 const wasActive=se150Match.active;
 se152BasePeerPacket(raw);
 if(!wasActive&&se150Match.active&&se150Match.role==='guest')se152StartWorld();
};
const se152BaseBotSheep=stBotSheep,se152BaseBotWolf=stBotWolf;
stBotSheep=function(unit){
 if(se150Match.active&&se150Match.role==='host'&&[...se152.seats.values()].includes(unit.id))return;
 return se152BaseBotSheep(unit);
};
stBotWolf=function(unit){
 if(se150Match.active&&se150Match.role==='host'&&[...se152.seats.values()].includes(unit.id))return;
 return se152BaseBotWolf(unit);
};
const se152BaseUpdate=stUpdate;
stUpdate=function(dt,t){
 if(se150Match.active&&se150Match.role==='guest'){
  se152GuestFrame(dt);return;
 }
 return se152BaseUpdate(dt,t);
};
const se152BaseCommand=stCommand;
stCommand=function(action,payload={}){
 if(!se150Match.active||se150Match.role!=='guest')return se152BaseCommand(action,payload);
 if(action==='preview'||action==='select')return se152BaseCommand(action,payload);
 if(action==='restart'||action==='role')return stResult(false,'Only the host changes the match or player roles.');
 if(!se152Guest()||!se152.assigned)return stResult(false,'Waiting for the host world.');
 if(!['move','build','attack','rescue','sell','upgrade','wolf-upgrade'].includes(action))
  return stResult(false,'Unsupported remote order.');
 se152Send(se151.guestConn,{kind:'world-command',roomId:se150Match.roomId,
  matchId:se150Match.matchId,action,payload});
 return stResult(true,'Order sent to host.');
};
const se152BaseStop=stopSession;
stopSession=function(...args){
 se152StopWorld();
 return se152BaseStop(...args);
};
window.SWYRL_ENGINE_LAN.worldSync=()=>({
 active:se150Match.active,hostAuthoritative:se150Match.active,
 role:se150Match.role,assignedUnit:se152.assigned,
 snapshotsReceived:se152.received,guests:se152.seats.size,
 synchronizedState:se152.received>0||se150Match.role==='host'
});
