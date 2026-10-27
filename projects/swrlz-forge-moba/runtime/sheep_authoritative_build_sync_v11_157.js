// §E v11.157 — ONE canonical guest-side host-building reconciler.
// v11.152 (3 types) + v11.156 (all types) previously both mutated structures
// on every world packet. Never replay house creation/removal in both passes.
const se157={byHostId:new Map(),remoteCount:0,shownCount:0,created:0,
  updates:0,destroyed:0,failed:0,lastError:'',buildRequests:0,buildAccepted:0,
  lastHostSeq:0,world:null};

function se157ValidStructure(v){
 return !!v&&typeof v.id==='string'&&v.id.length>0&&v.id.length<=130&&
  Object.prototype.hasOwnProperty.call(ST_BUILDINGS,v.kind)&&
  Array.isArray(v.pos)&&v.pos.length===3&&v.pos.every(Number.isFinite)&&
  Number.isFinite(v.hp)&&v.hp>0&&v.hp<=100000;
}
function se157OwnerId(hostOwner,units,s){
 const at=units.findIndex(u=>u.id===hostOwner);
 if(at<0)return null;
 return (s.units.find(u=>u.id===hostOwner)||s.units[at])?.id||null;
}
function se157SyncStructure(s,item,units){
 let b=se157.byHostId.get(item.id);
 if(b&&!s.buildings.includes(b))b=null;
 if(b&&b.kind!==item.kind)b=null;
 if(!b){
  b=s.buildings.find(x=>x.hp>0&&x.id===item.id&&x.kind===item.kind)||
   s.buildings.find(x=>x.hp>0&&x.authored&&x.kind===item.kind&&
    ![...se157.byHostId.values()].includes(x)&&
    Math.hypot(x.pos.x-item.pos[0],x.pos.z-item.pos[2])<.4);
 }
 const owner=se157OwnerId(item.owner,units,s);
 if(!b){
  // Render only actual host-created structures — never speculative previews.
  b=stNewBuilding(item.kind,item.pos[0],item.pos[2],owner,null,Number(item.rotation)||0);
  if(!b)throw new Error('Unable to create the replica');
  // Keep IDs consistent for minimap selection, upgrade/sell and navigation.
  b.id=item.id;
  se157.created++;
 }else se157.updates++;
 se157.byHostId.set(item.id,b);
 b.owner=owner||b.owner;
 b.hp=item.hp;
 b.maxHp=Math.max(1,Number(item.maxHp)||b.maxHp);
 b.progress=Math.max(0,Math.min(1,Number(item.progress)||0));
 b.level=Math.max(1,Math.min(3,Number(item.level)||1));
 b.income=Math.max(0,Number(item.income)||0);
 b.cost=Math.max(0,Number(item.cost)||0);
 const rot=Number(item.rotation)||0;
 if(Number.isFinite(rot)&&Math.abs(rot-(b.rotation||0))>.00001){
  Object.assign(b,stFootprint(item.pos[0],item.pos[2],1.2,
   ST_BUILDINGS[item.kind]?.length?3:1.2,rot,item.id));
  if(b.mesh)b.mesh.rotation.y=rot;
 }
 if(b.pos?.set)b.pos.set(item.pos[0],item.pos[1],item.pos[2]);
 if(!b.authored&&b.mesh?.scale&&b.baseScale)
  b.mesh.scale.y=b.baseScale.y*(.15+.85*b.progress);
 // This is a game structure, not a UI ghost. Native fog owns enemy
 // visibility; allied houses must not be hidden by stale guest fog.
 if(b.mesh&&s.role==='sheep'&&owner&&s.units.some(u=>u.id===owner&&u.kind==='sheep'))
  b.mesh.visible=true;
 return b;
}
function se157Reconcile(s,remote){
 const alive=new Map();
 let failed=0;
 for(const item of remote.buildings){
  if(!se157ValidStructure(item))continue;
  try{alive.set(item.id,se157SyncStructure(s,item,remote.units));}
  catch(error){failed++;se157.lastError=String(error?.message||error).slice(0,160);}
 }
 // Remove only host-absent structures. Do not delete UI ghost meshes.
 // Preserve authored objects' lifetime and owner baselines.
 for(const [hostId,b] of se157.byHostId){
  if(alive.has(hostId))continue;
  if(b?.hp>0){stRemoveBuilding(b);se157.destroyed++;}
 }
 // Catch host-deleted prefabs that existed in the guest's initial scene,
 // without removing scenery/preview meshes or newly created host structures.
 for(const b of s.buildings){
  if(b.hp<=0||alive.has(b.id)||[...alive.values()].includes(b))continue;
  if(b.authored||b.id?.startsWith('st-runtime-building-')){
   stRemoveBuilding(b);se157.destroyed++;
  }
 }
 se157.byHostId=alive;
 se157.remoteCount=remote.buildings.length;
 se157.shownCount=alive.size;
 se157.lastHostSeq=remote.seq;
 se157.failed+=failed;
 // Refresh actual team fog/house visibility after building creation.
 if(typeof se156PaintTeamFog==='function')se156PaintTeamFog(s,true);
}
const se157LegacyApply=se152ClientApply;
se152ClientApply=function(packet){
 if(!packet||!stSession||!se152Guest()||
  packet.roomId!==se150Match.roomId||
  packet.matchId!==se150Match.matchId||
  !Number.isInteger(packet.seq)||packet.seq<=se152.received||
  !Array.isArray(packet.buildings)||packet.buildings.length>160||
  !Array.isArray(packet.units)||packet.units.length>128)
  return se157LegacyApply(packet);
 const s=stSession;
 if(se157.world!==s){se157.world=s;se157.byHostId.clear();}
 const oldRemove=stRemoveBuilding;
 // Let earlier versions apply authoritative animals, timers and resources,
 // but never create/remove structures. A single pass below owns those.
 stRemoveBuilding=function(){};
 let okay=false;
 try{
  se157LegacyApply({...packet,buildings:[]});
  okay=se152.received===packet.seq;
 }finally{stRemoveBuilding=oldRemove;}
 if(!okay)return;
 se157Reconcile(s,packet);
};

// Provide real host world counts in the guest HUD. This identifies whether
// houses were absent from the packet or failed to render.
const se157BeforeGuestLabel=se154GuestLabel;
se154GuestLabel=function(...args){
 const result=se157BeforeGuestLabel(...args);
 if(se150Match.active&&se150Match.role==='guest'&&se150Match.badge)
  se150Match.badge.textContent+=' · houses '+se157.shownCount+'/'+se157.remoteCount+
   (se157.failed?' · replica errors '+se157.failed:'');
 return result;
};
const se157BeforeHostSnapshot=se152Snapshot;
se152Snapshot=function(...args){
 const result=se157BeforeHostSnapshot(...args);
 if(se150Match.active&&se150Match.role==='host'&&se150Match.badge&&stSession)
  se150Match.badge.textContent+=' · houses '+stSession.buildings.filter(b=>b.hp>0).length;
 return result;
};
// Count actual client build requests separately from host-confirmed build
// orders, without turning an optimistic local click into proof of success.
const se157OriginalSend=se152Send;
se152Send=function(channel,packet){
 if(se150Match.active&&se150Match.role==='guest'&&packet?.kind==='world-command'&&packet.action==='build')
  se157.buildRequests++;
 return se157OriginalSend(channel,packet);
};
const se157BeforeGuestListen=se152WatchGuestConnection;
se152WatchGuestConnection=function(...args){
 const result=se157BeforeGuestListen(...args);
 const conn=se151.guestConn;
 if(conn&&!conn.se157Watched){
  conn.se157Watched=true;
  conn.on('data',raw=>{
   let message=raw;
   if(typeof raw==='string'){
    if(raw.length>4000)return;
    try{message=JSON.parse(raw);}catch{return;}
   }
   if(message?.kind==='world-build-accepted'&&message.roomId===se150Match.roomId&&
      message.matchId===se150Match.matchId)se157.buildAccepted++;
  });
 }
 return result;
};
const se157BeforeStop=se152StopWorld;
se152StopWorld=function(...args){
 se157.byHostId.clear();se157.world=null;se157.remoteCount=0;
 se157.shownCount=0;se157.created=0;se157.updates=0;
 se157.destroyed=0;se157.failed=0;se157.lastError='';
 se157.buildRequests=0;se157.buildAccepted=0;se157.lastHostSeq=0;
 return se157BeforeStop(...args);
};
window.SWYRL_ENGINE_LAN.buildSync=()=>({
 active:se150Match.active,role:se150Match.role,
 hostWorldStructures:se157.remoteCount,
 guestReplicas:se157.shownCount,
 guestCreated:se157.created,
 guestUpdated:se157.updates,
 guestDestroyed:se157.destroyed,
 guestReplicaErrors:se157.failed,
 lastReplicaError:se157.lastError,
 guestBuildRequests:se157.buildRequests,
 confirmedBuildOrders:se157.buildAccepted,
 lastWorldSeq:se157.lastHostSeq
});
