// §E v11.165 — lightweight guest networking and fog under heavy buildings.
// Keep v11.161 movement, v11.162/163 house orders/growth, and v11.164 host
// simulation unchanged. Only eliminate redundant guest rendering work.
const se165={
 world:null,byId:new Map(),fogPending:null,fogAt:-1,fogState:'',
 fogRequests:0,fogPaints:0,fogCoalesced:0,unchangedHouses:0,
 changedHouses:0,snapshots:0,lastSyncMs:0,averageSyncMs:0,maxSyncMs:0,
 overBudgetSnapshots:0,lastFrameAt:0,frameSamples:0,frameFPS:0,
 lastFogMs:0,errors:0,lastError:''
};
function se165Reset(s=null){
 se165.world=s;se165.byId.clear();se165.fogPending=null;
 se165.fogAt=-1;se165.fogState='';se165.lastFrameAt=0;
}
function se165Signature(item){
 // All properties that affect a house's authoritative appearance and
 // gameplay are accounted for. Unchanged state must not reset the visual
 // construction animation already running in v11.163.
 return [item.kind,item.owner,item.pos?.[0],item.pos?.[1],item.pos?.[2],
  item.rotation,item.hp,item.maxHp,item.progress,item.level,item.income,
  item.cost].join('|');
}
const se165PriorBuilding=se157SyncStructure;
se157SyncStructure=function(s,item,units){
 if(se150Match.active&&se150Match.role==='guest'&&s&&item?.id){
  if(se165.world!==s)se165Reset(s);
  const previous=se165.byId.get(item.id);
  const mesh=se157.byHostId.get(item.id);
  const signature=se165Signature(item);
  if(previous&&previous.signature===signature&&mesh===previous.building&&
     mesh?.hp>0&&mesh.kind===item.kind&&mesh.mesh?.parent&&
     s.buildings.includes(mesh)){
   se165.unchangedHouses++;
   return mesh;
  }
  const built=se165PriorBuilding(s,item,units);
  if(built){se165.byId.set(item.id,{signature,building:built});
    se165.changedHouses++;}
  return built;
 }
 return se165PriorBuilding(s,item,units);
};
// The old guest mirror rebuilds the logical state of ALL houses on every
// 130ms world snapshot. Keep the correct reconciler, prune only its cache.
const se165PriorReconcile=se157Reconcile;
se157Reconcile=function(s,packet){
 const result=se165PriorReconcile(s,packet);
 if(se150Match.active&&se150Match.role==='guest'&&
    Array.isArray(packet?.buildings)){
  const live=new Set(packet.buildings.map(b=>b?.id));
  for(const id of se165.byId.keys())if(!live.has(id))se165.byId.delete(id);
 }
 return result;
};
// v11.156/v11.157/v11.160 all independently request full fog paints from
// the same snapshot. 36 houses => repeated canvas masks, gradients, loops,
// visibility tests, texture uploads on the main thread. Defer and coalesce
// those requests into the SINGLE existing v11.156 requestAnimationFrame.
const se165PriorFog=se156PaintTeamFog;
se156PaintTeamFog=function(s,force=false){
 if(se150Match.active&&se150Match.role==='guest'&&s?.fog&&
    s.rules?.fogMode!=='off'){
  if(se165.world!==s)se165Reset(s);
  se165.fogRequests++;
  if(se165.fogPending===s)se165.fogCoalesced++;
  se165.fogPending=s;
  return;
 }
 return se165PriorFog(s,force);
};
function se165FogKey(s){
 // Force an immediate repaint after captures, allied building changes, or
 // team-role changes. Routine movement only needs ~4 fog paints per second.
 const sheep=s.units.filter(u=>u.kind==='sheep'&&!u.captured).length;
 const wolf=s.units.filter(u=>u.kind==='wolf'&&!u.captured).length;
 const houses=s.buildings.filter(b=>b.hp>0).length;
 return [s.role,s.rules?.fogMode,sheep,wolf,houses].join(':');
}
function se165FlushFog(now){
 const s=se165.fogPending;
 if(!s||s!==stSession||!se150Match.active||
    se150Match.role!=='guest')return;
 const key=se165FogKey(s),changed=se165.fogState!==key;
 if(!changed&&se165.fogAt>=0&&now-se165.fogAt<235)return;
 se165.fogPending=null;se165.fogAt=now;se165.fogState=key;
 const started=performance.now();
 try{se165PriorFog(s,true);se165.fogPaints++;}
 catch(error){
  se165.errors++;se165.lastError=String(error?.message||error).slice(0,160);
  console.warn('§E guest fog batch',error);
 }
 se165.lastFogMs=performance.now()-started;
}
const se165PriorGuestFrame=se152GuestFrame;
se152GuestFrame=function(...args){
 const now=performance.now();
 const prior=se165.lastFrameAt;
 if(prior&&now>prior){
  const fps=1000/(now-prior);
  if(Number.isFinite(fps)&&fps<250){
   se165.frameFPS=se165.frameSamples?
    se165.frameFPS*.92+fps*.08:fps;se165.frameSamples++;
  }
 }
 se165.lastFrameAt=now;
 const result=se165PriorGuestFrame(...args);
 if(se150Match.active&&se150Match.role==='guest')se165FlushFog(now);
 return result;
};
// Instrument the real guest receive path without touching 130ms host
// networking. A single stalled expensive packet can now be identified.
const se165PriorApply=se152ClientApply;
se152ClientApply=function(packet){
 const before=se152.received,started=performance.now();
 const result=se165PriorApply(packet);
 if(se150Match.active&&se150Match.role==='guest'&&
    packet?.seq>before&&packet.seq===se152.received){
  const spent=performance.now()-started;
  se165.snapshots++;
  se165.lastSyncMs=spent;
  se165.averageSyncMs=se165.snapshots===1?
   spent:se165.averageSyncMs*.9+spent*.1;
  se165.maxSyncMs=Math.max(se165.maxSyncMs,spent);
  if(spent>16.7)se165.overBudgetSnapshots++;
 }
 return result;
};
const se165PriorGuestLabel=se154GuestLabel;
se154GuestLabel=function(...args){
 const out=se165PriorGuestLabel(...args);
 if(se150Match.active&&se150Match.role==='guest'&&se150Match.badge&&
    se165.frameSamples>3)
  se150Match.badge.textContent+=' · '+Math.round(se165.frameFPS)+
   ' fps · sync '+Math.round(se165.averageSyncMs)+'ms';
 return out;
};
const se165PriorStop=se152StopWorld;
se152StopWorld=function(...args){
 se165Reset();
 se165.fogRequests=0;se165.fogPaints=0;se165.fogCoalesced=0;
 se165.unchangedHouses=0;se165.changedHouses=0;se165.snapshots=0;
 se165.lastSyncMs=0;se165.averageSyncMs=0;se165.maxSyncMs=0;
 se165.overBudgetSnapshots=0;se165.frameSamples=0;se165.frameFPS=0;
 se165.lastFogMs=0;se165.errors=0;se165.lastError='';
 return se165PriorStop(...args);
};
window.SWYRL_ENGINE_LAN.performance=()=>({
 active:se150Match.active,role:se150Match.role,
 framesPerSecond:Math.round(se165.frameFPS),
 worldPackets:se165.snapshots,
 lastPacketWorkMs:Number(se165.lastSyncMs.toFixed(2)),
 averagePacketWorkMs:Number(se165.averageSyncMs.toFixed(2)),
 worstPacketWorkMs:Number(se165.maxSyncMs.toFixed(2)),
 packetsOver16ms:se165.overBudgetSnapshots,
 fogRequests:se165.fogRequests,fogPaints:se165.fogPaints,
 fogPaintsCoalesced:se165.fogCoalesced,
 lastFogWorkMs:Number(se165.lastFogMs.toFixed(2)),
 cachedUnchangedHouses:se165.unchangedHouses,
 changedHouses:se165.changedHouses,
 errors:se165.errors,lastError:se165.lastError
});
