// §E v11.163 — render actual host-owned construction growth on guests.
// Do not simulate construction on clients: only the authoritative host
// decides which buildings exist and how far construction has progressed.
const se163={
 builds:new Map(),world:null,frames:0,packets:0,finished:0,
 stalled:0,errors:0,lastError:'',awaitingKind:null,rejections:0
};
function se163Clamp(n){return Number.isFinite(n)?Math.min(1,Math.max(0,n)):0;}
function se163Scale(b,p){
 if(!b||b.hp<=0||b.authored||!b.mesh?.scale)return false;
 const base=Number(b.baseScale?.y);
 const fullHeight=Number.isFinite(base)&&base>0?base:1;
 const y=fullHeight*(.15+.85*se163Clamp(p));
 if(!Number.isFinite(y))return false;
 b.mesh.scale.y=y;
 if(!b.mesh.parent&&typeof scene!=='undefined')scene.add(b.mesh);
 if(stSession?.role==='sheep'&&stSession.units.some(u=>u.id===b.owner&&u.kind==='sheep'))
  b.mesh.visible=true;
 return true;
}
function se163SyncHostProgress(packet){
 if(!se150Match.active||se150Match.role!=='guest'||!stSession||
    !packet||packet.seq!==se152.received||!Array.isArray(packet.buildings))return;
 const s=stSession,now=performance.now();
 if(se163.world!==s){se163.world=s;se163.builds.clear();}
 const live=new Set();
 for(const remote of packet.buildings){
  if(!remote||typeof remote.id!=='string'||!Number.isFinite(remote.progress)||
     !Number.isFinite(remote.hp)||remote.hp<=0)continue;
  const b=se157.byHostId.get(remote.id)||
    s.buildings.find(x=>x.id===remote.id&&x.hp>0);
  if(!b)continue;
  live.add(remote.id);
  const host=se163Clamp(remote.progress);
  const old=se163.builds.get(remote.id);
  const changed=!old||host>old.host+.0001||host<old.host-.001;
  const visual=old?Math.max(host,Math.min(1,old.visual)):host;
  se163.builds.set(remote.id,{
   host,visual,receivedAt:now,
   progressedAt:changed?now:old.progressedAt,
   buildTime:Math.max(.25,Number(b.buildTime)||Number(ST_BUILDINGS[b.kind]?.time)||1.4),
   model:b,kind:b.kind
  });
  if(host>=1){se163Scale(b,1);se163.finished++;}
  else se163Scale(b,visual);
 }
 for(const id of se163.builds.keys())if(!live.has(id))se163.builds.delete(id);
 se163.packets++;
}
const se163PriorApply=se152ClientApply;
se152ClientApply=function(packet){
 const before=se152.received;
 const result=se163PriorApply(packet);
 if(packet?.seq>before&&packet.seq===se152.received)
  se163SyncHostProgress(packet);
 return result;
};
// v11.161 already supplies a single guest requestAnimationFrame animation
// path. Animate only construction mesh SCALE on that same render frame.
const se163PriorGuestFrame=se152GuestFrame;
se152GuestFrame=function(...args){
 const result=se163PriorGuestFrame(...args);
 if(!se152Guest()||!stSession||!se163.builds.size)return result;
 se163.frames++;
 const now=performance.now();
 for(const [id,track] of se163.builds){
  const b=track.model;
  if(!b||b.hp<=0||!stSession.buildings.includes(b))continue;
  // Bounded extrapolation bridges a 130ms network gap, but never turns a
  // stalled host-side build into a falsely completed structure.
  const age=Math.max(0,(now-track.receivedAt)/1000);
  const recent=now-track.progressedAt<1150;
  const lead=recent&&track.host>0&&track.host<1?
    Math.min(.14,age)/track.buildTime:0;
  const next=se163Clamp(track.host+lead);
  track.visual=Math.max(track.host,next);
  if(!se163Scale(b,track.visual)){
   se163.errors++;se163.lastError='Cannot set building scale '+id;
  }
 }
 return result;
};
// Preserve selected placement type if the host rejects a submitted site,
// so a phone user can choose another location without reselecting House.
const se163PriorCommand=stCommand;
stCommand=function(action,payload={}){
 if(action==='build'&&se150Match.active&&se150Match.role==='guest')
  se163.awaitingKind=typeof payload?.kind==='string'?payload.kind:null;
 return se163PriorCommand(action,payload);
};
function se163BuildFeedback(raw){
 if(!se150Match.active||se150Match.role!=='guest'||!stSession)return;
 let msg;
 try{
  if(typeof raw==='string'&&raw.length>4096)return;
  msg=typeof raw==='string'?JSON.parse(raw):raw;
 }catch{return;}
 if(msg?.kind!=='world-build-result-v3'||
   msg.roomId!==se150Match.roomId||msg.matchId!==se150Match.matchId)return;
 if(msg.state==='rejected'){
  se163.rejections++;
  const kind=se163.awaitingKind;
  if(kind&&ST_BUILDINGS[kind]&&!stUi.build){
   try{stUiChooseBuild(kind);}
   catch(error){se163.errors++;se163.lastError=String(error).slice(0,120);}
  }
  if(msg.reason)stUiFeedback('Build rejected: '+String(msg.reason).slice(0,120),true);
 }else if(msg.state==='accepted'||msg.state==='completed'){
  se163.awaitingKind=null;
 }
}
const se163PriorWatch=se152WatchGuestConnection;
se152WatchGuestConnection=function(...args){
 const result=se163PriorWatch(...args);
 const conn=se151.guestConn;
 if(conn&&!conn.se163Watched){
  conn.se163Watched=true;conn.on('data',se163BuildFeedback);
 }
 return result;
};
const se163PriorLabel=se154GuestLabel;
se154GuestLabel=function(...args){
 const result=se163PriorLabel(...args);
 if(se150Match.active&&se150Match.role==='guest'&&se150Match.badge){
  const growing=[...se163.builds.values()].filter(t=>t.host<1);
  const stalled=growing.filter(t=>performance.now()-t.progressedAt>2200);
  se163.stalled=stalled.length;
  const last=growing.at(-1);
  if(last)se150Match.badge.textContent+=
    ' · building '+Math.round(last.host*100)+'% host / '+
     Math.round(last.visual*100)+'% shown'+(stalled.length?' · progress stalled':'');
 }
 return result;
};
const se163PriorStop=se152StopWorld;
se152StopWorld=function(...args){
 se163.builds.clear();se163.world=null;se163.frames=0;
 se163.packets=0;se163.finished=0;se163.stalled=0;
 se163.errors=0;se163.lastError='';se163.awaitingKind=null;se163.rejections=0;
 return se163PriorStop(...args);
};
window.SWYRL_ENGINE_LAN.constructionProgress=()=>({
 active:se150Match.active,role:se150Match.role,
 receivedSnapshots:se163.packets,renderFrames:se163.frames,
 houses:[...se163.builds].map(([id,x])=>({
  id,kind:x.kind,hostPercent:Math.round(x.host*100),
  visualPercent:Math.round(x.visual*100),
  meshHeight:x.model?.mesh?.scale?.y,
  staleMs:Math.round(performance.now()-x.progressedAt)
 })).slice(-20),
 stalled:se163.stalled,renderErrors:se163.errors,
 lastError:se163.lastError,rejectedSites:se163.rejections
});
