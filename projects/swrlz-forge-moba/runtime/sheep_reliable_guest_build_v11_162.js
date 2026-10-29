// §E v11.162 — guest house orders are independent from joystick throttling.
// Keep v11.161 continuous guest rendering and v11.159 LAN browser unchanged.
const se162={
 sequence:0,sent:0,accepted:0,rejected:0,completed:0,
 hostAccepted:0,hostRejected:0,hostCompleted:0,
 last:'none',lastReason:'',pending:new Map(),seen:new Map()
};
function se162BuildRequest(p){
 return !!p&&typeof p==='object'&&typeof p.kind==='string'&&
  p.kind.length<=48&&Number.isFinite(Number(p.x))&&
  Number.isFinite(Number(p.z))&&
  (p.rotation===undefined||Number.isFinite(Number(p.rotation)))&&
  Math.abs(Number(p.x))<=10000&&Math.abs(Number(p.z))<=10000;
}
function se162HostResponse(peer,id,state,reason='',building=null){
 if(!peer?.channel||peer.channel.readyState!=='open')return;
 se152Send(peer.channel,{
  kind:'world-build-result-v3',roomId:se150Match.roomId,
  matchId:se150Match.matchId,requestId:id,state,
  reason:String(reason||'').slice(0,180),buildingId:building?.id||null
 });
}
const se162PriorHostCommand=se152ApplyRemoteCommand;
se152ApplyRemoteCommand=function(peer,message){
 if(message?.kind!=='world-command'||message.action!=='build')
  return se162PriorHostCommand(peer,message);
 // A build is a discrete action, NOT another joystick frame.
 // Original v11.152 throttled all traffic using peer.lastInput <36ms.
 if(!se150Match.active||se150Match.role!=='host'||!stSession||
    message.roomId!==se150Match.roomId||
    message.matchId!==se150Match.matchId||
    !se152.seats.has(peer))return;
 const id=typeof message.requestId==='string'&&
  /^[a-z0-9-]{1,48}$/i.test(message.requestId)?
  message.requestId:'legacy-'+Date.now().toString(36);
 const previously=se162.seen.get(peer);
 if(previously?.id===id){
  se162HostResponse(peer,id,previously.state,previously.reason);
  return;
 }
 const reject=reason=>{
  se162.hostRejected++;se162.last='rejected';
  se162.lastReason=String(reason||'Build rejected').slice(0,180);
  se162.seen.set(peer,{id,state:'rejected',reason:se162.lastReason});
  se162HostResponse(peer,id,'rejected',se162.lastReason);
 };
 if(!se162BuildRequest(message.payload))return reject('Invalid house placement.');
 const s=stSession,unit=s.units.find(u=>u.id===se152.seats.get(peer));
 if(!unit||unit.kind!=='sheep'||unit.captured||unit.isIllusion)
  return reject('Only your living sheep may build.');
 if(s.winner)return reject('This round has ended.');
 const payload={
  kind:message.payload.kind,
  x:Number(message.payload.x),z:Number(message.payload.z),
  rotation:Number(message.payload.rotation)||0
 };
 if(!Object.prototype.hasOwnProperty.call(ST_BUILDINGS,payload.kind))
  return reject('This structure type is not available.');
 // Invoke the same native authoritative command validation as local Play.
 // Bind the verified peer's sheep temporarily, not another player's sheep.
 const controlled=s.controlledId,selected=s.selectedId;
 let result;
 try{
  s.controlledId=unit.id;s.selectedId=unit.id;
  result=se152BaseCommand('build',payload);
 }catch(error){
  result={ok:false,reason:'Could not start the house order.'};
  console.warn('LAN guest house order',error);
 }finally{
  s.controlledId=controlled;s.selectedId=selected;
 }
 if(!result?.ok||unit.order?.action!=='build')
  return reject(result?.reason||'No building path accepted.');
 se162.hostAccepted++;se162.last='accepted';se162.lastReason='Sheep traveling to construction site';
 se162.pending.set(unit.id,{
  id,peer,kind:unit.order.kind,x:unit.order.siteX,
  z:unit.order.siteZ,at:Date.now()
 });
 se162.seen.set(peer,{id,state:'accepted',reason:se162.lastReason});
 // An old held joystick command should not cancel the newly accepted order.
 se153.inputs.delete(peer);
 const stick=se154.streams.get(peer);
 if(stick)stick.strength=0;
 se162HostResponse(peer,id,'accepted','Your sheep is going to the building site.');
};

// The guest preview is advisory: it can lag behind the host by network
// snapshots, especially while movement smoothing is active. The host must be
// the sole final judge of real placement, resources and path validation.
const se162OriginalCanBuild=stCanBuild;
stCanBuild=function(kind,x,z,...args){
 const result=se162OriginalCanBuild(kind,x,z,...args);
 if(!se150Match.active||se150Match.role!=='guest'||
    !se152Guest()||!stSession||!se152.assigned||result?.ok)return result;
 const owner=stSession.units.find(u=>u.id===se152.assigned);
 if(!owner||owner.kind!=='sheep'||owner.captured)return result;
 const bounds=Number(stSession.rules.bounds)||80;
 const px=Number(result?.x),pz=Number(result?.z);
 if(!Number.isFinite(px)||!Number.isFinite(pz)||
    Math.abs(px)>=bounds-1||Math.abs(pz)>=bounds-1||
    !Object.prototype.hasOwnProperty.call(ST_BUILDINGS,stBuildKind(kind)))
  return result;
 // Host rejects invalid spots explicitly; never create a local house.
 return {...result,ok:true,reason:'Host will verify this building site.',
  hostValidationRequired:true};
};

// Attach stable request IDs at the common one-way send boundary so the
// existing client UI/build buttons and network paths continue to work.
const se162PriorSend=se152Send;
se152Send=function(channel,packet){
 if(se150Match.active&&se150Match.role==='guest'&&
    packet?.kind==='world-command'&&packet.action==='build'){
  const id='house-'+(++se162.sequence).toString(36);
  packet={...packet,requestId:id};
  se162.sent++;se162.last='sent';se162.lastReason='Awaiting host validation';
 }
 return se162PriorSend(channel,packet);
};
function se162GuestResult(raw){
 if(!se150Match.active||se150Match.role!=='guest')return;
 let msg;
 try{
  msg=typeof raw==='string'?JSON.parse(raw):raw;
 }catch{return;}
 if(msg?.kind!=='world-build-result-v3'||
  msg.roomId!==se150Match.roomId||msg.matchId!==se150Match.matchId||
  !/^[a-z0-9-]{1,48}$/i.test(msg.requestId||''))return;
 if(msg.state==='accepted'){
  se162.accepted++;se162.last='accepted';
  se162.lastReason='Host accepted; sheep traveling';
  stUiFeedback('Host accepted your house. Sheep approaching the site.');
 }else if(msg.state==='rejected'){
  se162.rejected++;se162.last='rejected';
  se162.lastReason=String(msg.reason||'Site rejected').slice(0,180);
  stUiFeedback('Host rejected build: '+se162.lastReason,true);
 }else if(msg.state==='completed'){
  se162.completed++;se162.last='completed';
  se162.lastReason='House built and being synchronized';
  stUi.build=null;stUiClearPreview();
  stUiFeedback('Your house was built in the shared world.');
 }
}
const se162PriorWatch=se152WatchGuestConnection;
se152WatchGuestConnection=function(...args){
 const result=se162PriorWatch(...args);
 const conn=se151.guestConn;
 if(conn&&!conn.se162Watched){
  conn.se162Watched=true;conn.on('data',se162GuestResult);
 }
 return result;
};

// Completion is based on an actual authoritative structure, not a preview
// or an accepted-but-unfinished order. v11.160 still sends its real model.
const se162PriorNewBuilding=stNewBuilding;
stNewBuilding=function(...args){
 const b=se162PriorNewBuilding(...args);
 if(!b||!se150Match.active||se150Match.role!=='host'||!stSession||
    b.authored||!b.owner)return b;
 const pending=se162.pending.get(b.owner);
 if(pending&&pending.kind===b.kind&&
    Math.hypot(b.pos.x-pending.x,b.pos.z-pending.z)<1.1){
  se162.pending.delete(b.owner);
  se162.hostCompleted++;se162.last='completed';se162.lastReason='Guest house created';
  se162.seen.set(pending.peer,{id:pending.id,state:'completed',reason:'House built'});
  se162HostResponse(pending.peer,pending.id,'completed','House built',b);
 }
 return b;
};
// Clear a pending order if the host game cancels the build before arrival.
// Do not report "built" unless an actual building was created.
const se162SnapshotBase=se152Snapshot;
se152Snapshot=function(...args){
 const out=se162SnapshotBase(...args);
 if(se150Match.active&&se150Match.role==='host'&&stSession){
  for(const [owner,p] of se162.pending){
   const u=stSession.units.find(unit=>unit.id===owner);
   if(!u||u.captured||stSession.winner||
      (u.order?.action!=='build'&&Date.now()-p.at>500)){
    se162.pending.delete(owner);
    se162HostResponse(p.peer,p.id,'rejected','Construction order was interrupted.');
    se162.hostRejected++;
   }
  }
 }
 return out;
};
const se162PreviousStop=se152StopWorld;
se152StopWorld=function(...args){
 se162.pending.clear();se162.seen.clear();
 se162.sequence=0;se162.sent=0;se162.accepted=0;
 se162.rejected=0;se162.completed=0;
 se162.hostAccepted=0;se162.hostRejected=0;se162.hostCompleted=0;
 se162.last='none';se162.lastReason='';
 return se162PreviousStop(...args);
};
window.SWYRL_ENGINE_LAN.houseOrders=()=>({
 active:se150Match.active,role:se150Match.role,
 guestSent:se162.sent,guestAccepted:se162.accepted,
 guestRejected:se162.rejected,guestCompleted:se162.completed,
 hostAccepted:se162.hostAccepted,hostRejected:se162.hostRejected,
 hostCompleted:se162.hostCompleted,hostPending:se162.pending.size,
 lastState:se162.last,lastReason:se162.lastReason,
 guestMirroredHouses:se157.shownCount,
 guestReportedHouses:se157.remoteCount
});
