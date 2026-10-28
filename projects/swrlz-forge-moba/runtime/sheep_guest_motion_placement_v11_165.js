// §E v11.165 — responsive LAN guest movement + truthful build previews.
// Host owns physics; guest sends intent, never a client-authored position.
// This patch intentionally preserves v11.161 guest renderer and v11.164
// host background simulation. No new timer, renderer, server or CI workflow.
const se165={
 tx:0,rx:0,hostMoveFrames:0,hostBlocked:0,hostStale:0,hostIdle:0,
 lastSendAt:0,lastActive:false,lastStrength:0,lastInputAt:0,
 reason:'waiting for guest',hostInputAge:0,clientHost:null,
 rejectedPreview:0,previewReason:''
};
// v11.162 was overly permissive: a stale guest preview could override ANY
// invalid native placement, including the Spirit Pen and NO-BUILD ZONES.
// Keep native local feedback red and let the same host rules reject illegal
// requests. Never display an invalid placement as buildable.
const se165PriorCanBuild=stCanBuild;
stCanBuild=function(kind,x,z,...args){
 if(se150Match.active&&se150Match.role==='guest'&&stSession){
  const check=se162OriginalCanBuild(kind,x,z,...args);
  if(!check?.ok){se165.rejectedPreview++;se165.previewReason=check?.reason||'Blocked site';}
  return check;
 }
 return se165PriorCanBuild(kind,x,z,...args);
};

function se165GuestSend(force=false){
 if(!se152Guest()||!se152.assigned||!stSession||!se151.guestConn?.open)return;
 const unit=stSession.units.find(u=>u.id===se152.assigned);
 const joy=stMobile,down=!!unit&&!unit.captured&&joy.enabled&&
  joy.pointer!==null&&joy.session===stSession&&stMobileCanMove();
 const strength=down?Math.max(0,Math.min(1,Number(joy.strength)||0)):0;
 const x=down?Math.max(-1,Math.min(1,Number(joy.x)||0)):0;
 const z=down?Math.max(-1,Math.min(1,Number(joy.y)||0)):0;
 const now=Date.now(),active=strength>.13;
 const interval=active?65:250;
 // Immediate input-start / release, while pointermove packets are bounded.
 if(!force&&active===se165.lastActive&&now-se165.lastSendAt<interval)return;
 if(force&&active===se165.lastActive&&now-se165.lastSendAt<55)return;
 se165.lastSendAt=now;se165.lastActive=active;se165.lastStrength=strength;
 se154.clientSeq++;
 se152Send(se151.guestConn,{
  kind:'guest-stick-v2',roomId:se150Match.roomId,
  matchId:se150Match.matchId,seq:se154.clientSeq,
  x,z,strength
 });
 se154.tx++;se165.tx++;
 se154GuestLabel();
}
// The v11.152 LAN interval is retained and points to this function when
// the match starts. Additional pointer updates remove up-to-115ms delay.
se152GuestControls=function(){se165GuestSend();};
const se165NativeMobileInstall=stMobileInstall;
stMobileInstall=function(...args){
 const out=se165NativeMobileInstall(...args);
 const stick=typeof $==='function'?$('stMoveStick'):null;
 if(stick&&!stick.se165Bound){
  stick.se165Bound=true;
  for(const name of ['pointerdown','pointermove','pointerup',
                     'pointercancel','lostpointercapture']){
   stick.addEventListener(name,()=>se165GuestSend(name!=='pointermove'));
  }
 }
 return out;
};

function se165HostMove(dt){
 if(!se150Match.active||se150Match.role!=='host'||!stSession||
    paused||stSession.winner||!playing)return;
 const s=stSession,stepDt=Math.max(0,Math.min(.05,Number(dt)||0));
 if(!stepDt)return;
 const now=Date.now();
 for(const [peer,intent] of se154.streams){
  const assigned=se152.seats.get(peer);
  if(!assigned||intent.id!==assigned){se165.reason='peer seat mismatch';continue;}
  const age=now-intent.at;
  se165.hostInputAge=age;
  se165.lastStrength=Number(intent.strength)||0;
  if(age>650){se165.hostStale++;se165.reason='stale joystick packet';continue;}
  if(se165.lastStrength<.13){se165.hostIdle++;se165.reason='joystick idle';continue;}
  const unit=s.units.find(u=>u.id===assigned);
  if(!unit){se165.reason='assigned sheep missing';continue;}
  if(unit.captured){se165.reason='sheep captured';continue;}
  if(unit.kind==='wolf'&&s.elapsed<s.rules.headstart){
   se165.reason='waiting for wolf release';continue;
  }
  // Accepted guest building orders must finish instead of a stale held stick
  // accidentally replacing the native sheep construction approach.
  if(unit.order?.action==='build'){se165.reason='building in progress';continue;}
  let dx=Number(intent.x),dz=Number(intent.z);
  const mag=Math.hypot(dx,dz);
  if(!Number.isFinite(mag)||mag<.02){se165.reason='zero direction';continue;}
  dx/=mag;dz/=mag;
  const speed=Number(unit.speed)||0,travel=speed*stepDt*Math.min(1,se165.lastStrength);
  if(!Number.isFinite(travel)||travel<=0){se165.reason='no movement speed';continue;}
  // A human's active joystick replaces a prior move command, never a build.
  if(unit.order)stSetOrder(unit,null);
  const radius=unit.kind==='wolf'?ST_WOLF_RADIUS:ST_SHEEP_RADIUS;
  const x=unit.pos.x,z=unit.pos.z;
  // Try the requested direction first, then sliding, then small tangent
  // adjustments around nearby solid geometry. Never ignore stBlocked.
  const options=[
   [dx,dz],[dx,0],[0,dz],
   [dx*.866-dz*.5,dx*.5+dz*.866],
   [dx*.866+dz*.5,-dx*.5+dz*.866],
   [dx*.707-dz*.707,dx*.707+dz*.707],
   [dx*.707+dz*.707,-dx*.707+dz*.707]
  ];
  let nextX=x,nextZ=z;
  for(const [vx,vz] of options){
   const size=Math.hypot(vx,vz);
   if(size<.08)continue;
   const nx=x+vx/size*travel,nz=z+vz/size*travel;
   if(!stBlocked(nx,nz,radius)){nextX=nx;nextZ=nz;break;}
  }
  if(nextX===x&&nextZ===z){
   se165.hostBlocked++;se155.blocked++;
   se165.reason='blocked by map/building';continue;
  }
  unit.pos.x=nextX;unit.pos.z=nextZ;
  unit.actor.rotation.y=Math.atan2(nextX-x,nextZ-z);
  unit.walkDistance+=Math.hypot(nextX-x,nextZ-z);
  stPlaceUnit(unit);
  se165.hostMoveFrames++;se155.moves++;se154.moved++;
  se165.reason='moving';
 }
}
// Native host updates are the real gameplay clock, including the v11.164
// background catch-up steps. Move guests along with these steps, rather
// than once per 130ms network snapshot causing visible step/stop.
const se165PriorUpdate=stUpdate;
stUpdate=function(dt,t){
 se165HostMove(dt);
 return se165PriorUpdate(dt,t);
};
// Prevent the prior v11.155 snapshot driver from moving the same guest AGAIN.
// Its tick/diagnostic counters remain for the existing LAN host status.
se155MoveGuestOnWorldTick=function(){
 se155.ticks++;se155.lastReason=se165.reason;
};

const se165PriorSend=se152Send;
se152Send=function(conn,pkt){
 if(pkt?.kind==='world'&&se150Match.active&&se150Match.role==='host'){
  pkt={...pkt,hostGuestControl:{
   reason:se165.reason,moveFrames:se165.hostMoveFrames,
   blocked:se165.hostBlocked,ageMs:se165.hostInputAge,
   strength:Math.round(se165.lastStrength*100)
  }};
 }
 return se165PriorSend(conn,pkt);
};
const se165PriorApply=se152ClientApply;
se152ClientApply=function(pkt){
 const was=se152.received;
 const out=se165PriorApply(pkt);
 if(pkt?.seq>was&&pkt.seq===se152.received&&
    se150Match.active&&se150Match.role==='guest'&&pkt.hostGuestControl)
  se165.clientHost=pkt.hostGuestControl;
 return out;
};
const se165PreviousLabel=se154GuestLabel;
se154GuestLabel=function(...args){
 const result=se165PreviousLabel(...args);
 if(se150Match.active&&se150Match.role==='guest'&&se150Match.badge){
  const state=se165.clientHost;
  if(state){
   se150Match.badge.textContent+=' · host ctrl '+state.reason+
    ' '+state.strength+'% · moved '+state.moveFrames+
    (state.blocked?' · collisions '+state.blocked:'');
  }
 }
 return result;
};
const se165PreviousStop=se152StopWorld;
se152StopWorld=function(...args){
 se165.tx=0;se165.rx=0;se165.hostMoveFrames=0;se165.hostBlocked=0;
 se165.hostStale=0;se165.hostIdle=0;se165.lastSendAt=0;
 se165.lastActive=false;se165.lastStrength=0;se165.lastInputAt=0;
 se165.hostInputAge=0;se165.reason='stopped';se165.clientHost=null;
 se165.rejectedPreview=0;se165.previewReason='';
 return se165PreviousStop(...args);
};
window.SWYRL_ENGINE_LAN.guestControlV165=()=>({
 active:se150Match.active,role:se150Match.role,
 attemptedJoystickSends:se165.tx,guestJoystick:stMobile.pointer!==null,
 guestStrength:Math.round((Number(stMobile.strength)||0)*100),
 hostMovementFrames:se165.hostMoveFrames,hostBlockedFrames:se165.hostBlocked,
 hostStaleFrames:se165.hostStale,hostIdleFrames:se165.hostIdle,
 lastHostReason:se165.reason,lastReceivedHostState:se165.clientHost,
 locallyRejectedPlacementPreviews:se165.rejectedPreview,
 lastPlacementRejection:se165.previewReason
});
