// §E v11.160 — LAN guest construction delivery + wolves released on time.
// Preserve the proven host-authoritative world, smoother movement, and
// one authoritative structure reconciler. No separate simulation loop.
const se160={sentBuildings:0,receivedBuildings:0,renderedBuildings:0,
 missedBuildings:0,lastBuilding:'',heldOrders:0,wolvesHidden:0,wolvesReleased:0};

function se160WolfVisibility(s){
 if(!se150Match.active||!s?.units||!s.rules)return;
 const held=Number(s.rules.headstart)||0;
 const released=Number(s.elapsed)>=held;
 let hidden=0,visible=0;
 for(const unit of s.units){
  if(unit.kind!=='wolf'||!unit.actor)continue;
  if(!released){
   unit.actor.visible=false;hidden++;
   // Pre-release wolves do not receive actionable movement targets.
   if(unit.order)stSetOrder(unit,null);
  }else{
   // Once the timer ends, honor normal team/fog visibility.
   unit.actor.visible=!unit.captured&&stSeenByRole(unit);
   if(unit.actor.visible)visible++;
  }
 }
 se160.wolvesHidden=hidden;se160.wolvesReleased=visible;
}

// The native session spawns wolf actors before the head-start timer is over.
// Keep them hidden until the actual release moment on both host and guests.
const se160StartBase=stStart;
stStart=function(...args){
 const result=se160StartBase(...args);
 if(se150Match.active)se160WolfVisibility(stSession);
 return result;
};
const se160VisionBase=stUpdateVision;
stUpdateVision=function(s,...args){
 const result=se160VisionBase(s,...args);
 if(se150Match.active)se160WolfVisibility(s);
 return result;
};
const se160FogBase=se156PaintTeamFog;
se156PaintTeamFog=function(s,...args){
 const result=se160FogBase(s,...args);
 if(se150Match.active)se160WolfVisibility(s);
 return result;
};
const se160ClientBase=se152ClientApply;
se152ClientApply=function(packet){
 const output=se160ClientBase(packet);
 if(se150Match.active&&se150Match.role==='guest'&&stSession)
  se160WolfVisibility(stSession);
 return output;
};
const se160SnapshotBase=se152Snapshot;
se152Snapshot=function(...args){
 const result=se160SnapshotBase(...args);
 if(se150Match.active&&se150Match.role==='host'&&stSession)
  se160WolfVisibility(stSession);
 return result;
};

// Guest v11.153 still has a legacy joystick stream on the host. If it stays
// pressed during a building approach, that older handler can cancel the
// sheep's actual 'build' order. Suppress those older intents during the order.
// v11.156 already suspends v2 guest joystick movement on snapshot ticks.
const se160NativeUpdateBase=stUpdate;
stUpdate=function(...args){
 if(!se150Match.active||se150Match.role!=='host'||!stSession||
    !se153?.inputs?.size)return se160NativeUpdateBase(...args);
 const saved=[];
 for(const [peer,intent] of se153.inputs){
  const unit=stSession.units.find(u=>u.id===se152.seats.get(peer));
  if(unit?.order?.action==='build'){
   saved.push([peer,intent]);se153.inputs.delete(peer);
  }
 }
 if(saved.length)se160.heldOrders+=saved.length;
 try{return se160NativeUpdateBase(...args);}
 finally{
  for(const [peer,input] of saved)if(!se153.inputs.has(peer))se153.inputs.set(peer,input);
 }
};

function se160StateFromBuilding(b){
 return {id:b.id,kind:b.kind,pos:[b.pos.x,b.pos.y,b.pos.z],
  rotation:Number(b.rotation)||0,owner:b.owner,
  hp:b.hp,maxHp:b.maxHp,progress:b.progress,level:b.level,
  income:b.income,cost:b.cost};
}
function se160AnnounceBuilt(b){
 if(!se150Match.active||se150Match.role!=='host'||!stSession||!b||
    b.hp<=0||b.authored)return;
 const units=stSession.units.map(u=>({id:u.id,kind:u.kind}));
 const packet={kind:'world-building-created-v2',
  roomId:se150Match.roomId,matchId:se150Match.matchId,
  building:se160StateFromBuilding(b),units};
 for(const peer of se149Peer.links){
  if(peer?.channel?.readyState==='open'&&peer.name)
   se152Send(peer.channel,packet);
 }
 se160.sentBuildings++;
}
const se160CreateBase=stNewBuilding;
stNewBuilding=function(...args){
 const result=se160CreateBase(...args);
 if(result&&se150Match.active&&se150Match.role==='host'&&!result.authored)
  se160AnnounceBuilt(result);
 return result;
};

// An actual host building-created message takes the same native visual path
// as the reconciled snapshots. It cannot be confused with a ghost preview.
function se160GuestBuilt(raw){
 if(!se150Match.active||se150Match.role!=='guest'||!stSession||
    !se151.guestConn?.open)return;
 let msg;
 try{
  msg=typeof raw==='string'?JSON.parse(raw):raw;
 }catch{return;}
 if(msg?.kind!=='world-building-created-v2'||
    msg.roomId!==se150Match.roomId||msg.matchId!==se150Match.matchId||
    !Array.isArray(msg.units)||msg.units.length>128||
    !se157ValidStructure(msg.building))return;
 se160.receivedBuildings++;
 const s=stSession;
 try{
  if(se157.world!==s){se157.world=s;se157.byHostId.clear();}
  const b=se157SyncStructure(s,msg.building,msg.units);
  // If an old client-side fog pass detached or hid this native mesh, restore
  // a friendly house. Reconciliation continues from the same host ID.
  if(b?.mesh&&!b.authored){
   if(!b.mesh.parent)scene.add(b.mesh);
   const owner=s.units.find(u=>u.id===b.owner);
   if(owner?.kind==='sheep'&&s.role==='sheep')b.mesh.visible=true;
  }
  if(b){
   se160.renderedBuildings++;
   se160.lastBuilding=msg.building.id;
   if(msg.building.owner&&msg.units.some(u=>u.id===msg.building.owner&&u.id===se152.assigned)){
    stUi.build=null;stUiClearPreview();
    stUiFeedback('Your building is now in the shared game.');
   }
  }
  se156PaintTeamFog(s,true);
 }catch(err){
  se160.missedBuildings++;
  console.warn('LAN host building renderer',err);
 }
}
const se160GuestWatchBase=se152WatchGuestConnection;
se152WatchGuestConnection=function(...args){
 const result=se160GuestWatchBase(...args);
 const conn=se151.guestConn;
 if(conn&&!conn.se160BuildingListener){
  conn.se160BuildingListener=true;
  conn.on('data',se160GuestBuilt);
 }
 return result;
};

// The authoritative snapshot reconciler remains the source of truth, even
// after an announcement is missed during a temporary peer disconnection.
const se160ReconcileBase=se157Reconcile;
se157Reconcile=function(s,packet){
 const result=se160ReconcileBase(s,packet);
 if(se150Match.active&&se150Match.role==='guest'){
  for(const b of se157.byHostId.values()){
   if(!b||b.hp<=0||!b.mesh)continue;
   if(!b.authored&&!b.mesh.parent)scene.add(b.mesh);
   const owner=s.units.find(u=>u.id===b.owner);
   if(owner?.kind==='sheep'&&s.role==='sheep')b.mesh.visible=true;
  }
  se160WolfVisibility(s);
 }
 return result;
};
const se160StopBase=se152StopWorld;
se152StopWorld=function(...args){
 se160.sentBuildings=0;se160.receivedBuildings=0;
 se160.renderedBuildings=0;se160.missedBuildings=0;
 se160.lastBuilding='';se160.heldOrders=0;
 se160.wolvesHidden=0;se160.wolvesReleased=0;
 return se160StopBase(...args);
};
window.SWYRL_ENGINE_LAN.constructionRelease=()=>({
 role:se150Match.role,active:se150Match.active,
 hostCreatedAnnouncements:se160.sentBuildings,
 guestReceivedCreates:se160.receivedBuildings,
 guestRenderedCreates:se160.renderedBuildings,
 guestRenderErrors:se160.missedBuildings,
 guestHostSnapshotHouses:se157.remoteCount,
 guestVisibleReplicaCount:se157.shownCount,
 lastBuiltID:se160.lastBuilding,
 buildOrdersProtected:se160.heldOrders,
 wolvesHeldBeforeCountdown:se160.wolvesHidden,
 wolvesReleasedVisible:se160.wolvesReleased,
 headstartRemaining:stSession?Math.max(0,stSession.rules.headstart-stSession.elapsed):null
});
