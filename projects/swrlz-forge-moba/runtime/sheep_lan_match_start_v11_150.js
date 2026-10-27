// §E v11.150 — host-authorized lobby -> native Sheep Tag Gameplay transition.
// Direct WebRTC peers see the same start event; no claims of state replication.
// Keep existing RTC connections alive across the v11.141 menu teardown.
const se150Match={active:false,roomId:'',matchId:'',role:'',started:0,guestChannel:null,badge:null};
function se150ReadyGuests(){
 return se149Peer.links.filter(p=>p.name&&p.channel?.readyState==='open');
}
function se150StartControls(){
 const room=se148Room.screen,button=room?.querySelector('#se148Start');
 if(!button||se149Peer.mode!=='host'||se150Match.active)return;
 const count=se150ReadyGuests().length;
 button.hidden=false;button.disabled=count===0;
 button.textContent=count?'Start Match · '+(count+1)+' players':'Start Match · waiting for guest';
 button.onclick=se150HostStart;
}
const se150BasePaint=se149PaintPeer;
se149PaintPeer=function(...args){
 const value=se150BasePaint(...args);
 se150StartControls();
 return value;
};
const se150BaseEnterRoom=se149EnterRoom;
se149EnterRoom=function(...args){
 const value=se150BaseEnterRoom(...args);
 se150StartControls();
 return value;
};
function se150Badge(){
 se150Match.badge?.remove();
 const canvas=typeof $==='function'?$('viewport'):document.querySelector('#viewport');
 const parent=canvas?.parentElement||document.body;
 const tag=document.createElement('div');
 tag.id='se150MatchStatus';tag.className='se150-match-status';
 tag.textContent='LAN '+se150Match.role.toUpperCase()+' · match launched · entity sync pending';
 parent.appendChild(tag);se150Match.badge=tag;
}
function se150BeginNative(role,roomId,matchId){
 if(se150Match.active||!roomId||!matchId||!seLevels.playingMenu)return false;
 const current=seLevelsCurrent();
 if(!current||current.role!=='menu'||!seLevels.records.has('game'))return false;
 se150Match.active=true;
 se150Match.roomId=roomId;
 se150Match.matchId=matchId;
 se150Match.role=role;
 se150Match.started=Date.now();
 // Native editor/Sheep Tag transition owns native Play, game rules and HUD.
 // Menu stop runs through previous LAN wrappers: guard se149Close while active.
 let ok=false;
 try{ok=!!seLevelsTransition('game',true);}catch(error){console.error('LAN native game start failed',error);}
 if(!ok){
  se150Match.active=false;se150Match.roomId='';se150Match.matchId='';
  se150Match.role='';se150Match.started=0;
  return false;
 }
 se150Badge();
 return true;
}
function se150HostStart(){
 if(se149Peer.mode!=='host'||se150Match.active)return false;
 const peers=se150ReadyGuests(),roomId=se149Peer.roomId;
 if(!peers.length){se149Message('A guest must connect before the host can start.');return false;}
 if(!seLevels.playingMenu){se149Message('Open Sheep Tag Main Menu Play before starting.');return false;}
 const matchId=window.crypto?.randomUUID?.()||String(Date.now());
 if(!se150BeginNative('host',roomId,matchId)){
  se149Message('The Gameplay level could not start. Guests remain in the lobby.');
  return false;
 }
 const message=JSON.stringify({kind:'match-start',roomId,matchId,level:'game'});
 let notified=0;
 for(const peer of peers){
  try{peer.channel.send(message);notified++;}catch(error){
   console.warn('Guest start notification failed',error);
  }
 }
 if(se150Match.badge)se150Match.badge.textContent=
  'LAN HOST · match started · '+notified+'/'+peers.length+' guests notified · gameplay sync pending';
 return true;
}
function se150PeerPacket(raw){
 let packet;
 try{packet=JSON.parse(raw);}catch{return;}
 if(!packet||typeof packet!=='object')return;
 if(packet.kind==='match-start'){
  if(se149Peer.mode!=='guest'||se150Match.active)return;
  if(packet.roomId!==se149Peer.roomId||packet.level!=='game'||
    typeof packet.matchId!=='string'||packet.matchId.length<1||packet.matchId.length>100)return;
  if(!se150BeginNative('guest',packet.roomId,packet.matchId))
   se149Message('Host launched, but local Gameplay could not open. Return to the Main Menu.');
 }else if(packet.kind==='match-end'){
  if(se150Match.active&&se150Match.role==='guest'&&packet.matchId===se150Match.matchId){
   if(typeof stopSession==='function')stopSession();
  }
 }
}
// Extend the existing guest channel's verified host connection, not a page-level message.
const se150OriginalJoinInvite=se149JoinInvite;
se149JoinInvite=function(...args){
 const pending=se150OriginalJoinInvite(...args);
 const pc=se149Peer.guest;
 if(pc){
  const prior=pc.ondatachannel;
  pc.ondatachannel=function(event){
   prior?.call(pc,event);
   se150Match.guestChannel=event.channel;
   const existing=event.channel.onmessage;
   event.channel.onmessage=function(dataEvent){
    existing?.call(event.channel,dataEvent);
    se150PeerPacket(dataEvent.data);
   };
  };
 }
 return pending;
};
// The installed Join by Invite click handler references se149JoinInvite at click time.
const se150OriginalClose=se149Close;
se149Close=function(...args){
 if(se150Match.active)return; // menu teardown must not kill an in-flight match
 return se150OriginalClose(...args);
};
function se150Finish(){
 if(!se150Match.active)return;
 const role=se150Match.role,matchId=se150Match.matchId;
 se150Match.active=false;se150Match.roomId='';se150Match.matchId='';
 se150Match.role='';se150Match.started=0;se150Match.guestChannel=null;
 se150Match.badge?.remove();se150Match.badge=null;
 if(role==='host'){
  for(const peer of se150ReadyGuests()){
   try{peer.channel.send(JSON.stringify({kind:'match-end',matchId}));}catch{}
  }
 }
 se150OriginalClose();
}
const se150PreviousStopSession=stopSession;
stopSession=function(...args){
 const wasMatch=se150Match.active;
 const result=se150PreviousStopSession(...args);
 if(wasMatch&&!playing&&!simulating&&!stSession)se150Finish();
 return result;
};
window.SWYRL_ENGINE_LAN.startMatch=se150HostStart;
window.SWYRL_ENGINE_LAN.matchStatus=()=>({
 active:se150Match.active,role:se150Match.role,matchId:se150Match.matchId,
 connectedGuests:se150ReadyGuests().length,
 nativeGameplayActive:se150Match.active&&!!(playing||stSession),
 gameplaySynchronized:false
});
