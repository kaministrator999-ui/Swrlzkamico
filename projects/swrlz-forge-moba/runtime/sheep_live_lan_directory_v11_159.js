// §E v11.159 — real live-room discovery for the public HTTPS Sheep Tag page.
// HTTPS cannot scan local subnet addresses. Instead, a temporary MQTT
// announcement directory is grouped by hashed public IPv4 egress, typically
// shared by browsers on the same Wi-Fi. This is NOT proof of LAN membership.
// MQTT only carries public lobby metadata. PeerJS/WebRTC still joins/plays.
const se159={
 scope:'',client:null,started:null,connected:false,notice:'Connecting to live directory…',
 rooms:new Map(),heartbeat:null,listed:false,library:null,lastProbe:0,
 lastAnnouncement:'',lastAdvertiseAt:0,net:'unresolved'
};
function se159Enabled(){return location.protocol==='https:';}
function se159ValidRoom(value){
 return typeof value==='string'&&/^se151-[a-z0-9]{10,80}$/i.test(value);
}
function se159ActiveRoom(){
 return !!se151.host&&!!se151.peer?.open&&
   se159ValidRoom(se151.room)&&!se150Match.active&&
   se149Peer.links.filter(p=>p.channel?.readyState==='open'&&p.name).length<7;
}
function se159Players(){
 return Math.min(8,1+se149Peer.links.filter(p=>
  p.channel?.readyState==='open'&&p.name).length);
}
async function se159NetworkScope(){
 // Public IPv4 is never sent to the broker. It is used only to derive a
 // temporary shared directory topic; this may include different LANs behind
 // one NAT, and won't match when one phone is using cellular data.
 const res=await fetch('https://api.ipify.org?format=json',{cache:'no-store'});
 if(!res.ok)throw new Error('Network matching unavailable');
 const data=await res.json();
 const ip=String(data.ip||'');
 if(!/^\d{1,3}(?:\.\d{1,3}){3}$/.test(ip)||
    ip.split('.').some(x=>Number(x)>255))
   throw new Error('A shared IPv4 connection is required for automatic listing');
 const bytes=new TextEncoder().encode('swyrlz-sheep-directory-v1|'+ip);
 const digest=await crypto.subtle.digest('SHA-256',bytes);
 return [...new Uint8Array(digest)].slice(0,12).map(v=>v.toString(16).padStart(2,'0')).join('');
}
function se159LoadMQTT(){
 if(typeof window.mqtt?.connect==='function')return Promise.resolve(window.mqtt);
 if(se159.library)return se159.library;
 se159.library=new Promise((resolve,reject)=>{
  const el=document.createElement('script');
  el.async=true;
  el.src='https://cdn.jsdelivr.net/npm/mqtt@5.10.1/dist/mqtt.min.js';
  el.onload=()=>typeof window.mqtt?.connect==='function'?
    resolve(window.mqtt):reject(new Error('MQTT library was blocked'));
  el.onerror=()=>reject(new Error('Live directory library unavailable'));
  document.head.appendChild(el);
 }).catch(err=>{se159.library=null;throw err;});
 return se159.library;
}
function se159Topic(){
 return 'swyrlz/engine/sheep-tag/live-lobbies/v1/'+se159.scope;
}
function se159Publish(type){
 const client=se159.client;
 if(!client?.connected||!se159.scope)return;
 if(type==='open'&&!se159ActiveRoom())type='closed';
 const room=se151.room;
 if(!se159ValidRoom(room))return;
 const info={v:1,type,room,name:'Sheep Tag LAN',
   players:se159Players(),capacity:8,phase:'waiting'};
 try{client.publish(se159Topic(),JSON.stringify(info),{qos:0,retain:false});}
 catch(err){se159.notice='Announcement failed: '+(err?.message||err);}
 if(type==='open'){se159.listed=true;se159.lastAdvertiseAt=Date.now();}
 else se159.listed=false;
}
function se159Probe(){
 if(!se159.client?.connected)return;
 if(Date.now()-se159.lastProbe<1000)return;
 se159.lastProbe=Date.now();
 se159.client.publish(se159Topic(),JSON.stringify({v:1,type:'probe'}),
   {qos:0,retain:false});
}
function se159Expire(){
 const now=Date.now();
 let changed=false;
 for(const [id,row] of se159.rooms){
  if(now-row.seen>18000||row.phase!=='waiting'){
   se159.rooms.delete(id);changed=true;
  }
 }
 if(changed)se159Draw();
}
function se159OnMessage(topic,payload){
 if(topic!==se159Topic())return;
 let msg;
 try{
  const str=typeof payload==='string'?payload:new TextDecoder().decode(payload);
  if(str.length>1600)return;
  msg=JSON.parse(str);
 }catch{return;}
 if(msg?.v!==1)return;
 if(msg.type==='probe'){
  if(se159ActiveRoom())se159Publish('open');
  return;
 }
 if(!se159ValidRoom(msg.room))return;
 if(msg.room===se151.room&&se151.host)return;
 if(msg.type==='closed'){se159.rooms.delete(msg.room);se159Draw();return;}
 if(msg.type!=='open'||msg.phase!=='waiting'||!Number.isInteger(msg.players)||
    msg.players<1||msg.players>8||msg.capacity!==8)return;
 se159.rooms.set(msg.room,{id:msg.room,name:'Sheep Tag LAN',
    players:msg.players,capacity:8,phase:msg.phase,seen:Date.now()});
 if(se159.rooms.size>32){
  const first=se159.rooms.keys().next().value;
  se159.rooms.delete(first);
 }
 se159Draw();
}
function se159Pulse(){
 se159Expire();
 if(se159ActiveRoom()){
  se159Publish('open');
 }else if(se159.listed){
  se159Publish('closed');
 }
}
function se159Draw(){
 if(!se159Enabled()||!se146Lan.active)return;
 const root=se146Lan.root,el=root?.querySelector('#se146LanGames');
 if(!el)return;
 se159ExpireNoRender();
 const rooms=[...se159.rooms.values()].sort((a,b)=>b.seen-a.seen);
 el.replaceChildren();
 if(!rooms.length){
  const empty=document.createElement('p');empty.className='se146-empty';
  empty.textContent=se159.connected?
   'No open games on this internet connection yet. Start a lobby on another device.':
   'Connecting to live game directory… You can still join using a host invite.';
  el.appendChild(empty);
 }else for(const room of rooms){
  const row=document.createElement('div');
  row.className='se146-game';
  const info=document.createElement('div');info.className='se146-game-info';
  const name=document.createElement('b');name.textContent=room.name;
  const details=document.createElement('small');
  details.textContent=room.players+' / '+room.capacity+' players · live waiting lobby';
  info.append(name,details);
  const join=document.createElement('button');join.type='button';
  join.textContent='Join';join.disabled=room.players>=8;
  join.onclick=()=>{
   const input=root.querySelector('#se149OfferIn');
   if(!input){se146Message('Join-by-invite is unavailable. Reload §E.');return;}
   input.value=room.id;
   // Invoke the same real PeerJS connection and player-seat handshake used
   // by manual joining. Never mark the guest joined from a directory ad.
   se151JoinGame();
  };
  row.append(info,join);el.appendChild(row);
 }
 const status=root.querySelector('#se146LanStatus');
 if(status){
  status.textContent=se159.connected?
    rooms.length+' live waiting game(s) · grouped by shared public Wi-Fi/internet exit. Not a private subnet scan.':
    se159.notice+' · manual invite joining remains available.';
 }
 const h=root.querySelector('.se146-list-head b');
 if(h)h.textContent='Available Live Games';
}
function se159ExpireNoRender(){
 const now=Date.now();
 for(const [id,room] of se159.rooms)if(now-room.seen>18000)se159.rooms.delete(id);
}
function se159Start(){
 if(!se159Enabled())return Promise.resolve(false);
 if(se159.started)return se159.started;
 se159.started=(async()=>{
  se159.net='checking';
  const scope=await se159NetworkScope();
  const mqtt=await se159LoadMQTT();
  se159.scope=scope;se159.net='shared-internet-exit';
  const id='s159'+(crypto.randomUUID?.()||Date.now().toString(36)).replace(/-/g,'').slice(0,16);
  const client=mqtt.connect('wss://broker.emqx.io:8084/mqtt',{
   clientId:id,clean:true,connectTimeout:8500,reconnectPeriod:5000,
   keepalive:30,resubscribe:true
  });
  se159.client=client;
  client.on('connect',()=>{
   se159.connected=true;se159.notice='Live game directory connected';
   client.subscribe(se159Topic(),{qos:0},err=>{
    if(err){se159.notice='Directory subscribe failed';se159Draw();return;}
    se159Probe();
    if(se159ActiveRoom())se159Publish('open');
   });
   se159Draw();
  });
  client.on('message',se159OnMessage);
  client.on('reconnect',()=>{se159.connected=false;se159.notice='Reconnecting live directory';se159Draw();});
  client.on('close',()=>{se159.connected=false;se159.notice='Live directory offline';se159Draw();});
  client.on('error',err=>{
   se159.connected=false;se159.notice='Live directory unavailable: '+(err?.message||'connection failed');
   se159Draw();
  });
  if(!se159.heartbeat)se159.heartbeat=setInterval(se159Pulse,5500);
  return true;
 })().catch(err=>{
  se159.started=null;se159.connected=false;
  se159.notice='Automatic discovery unavailable: '+(err?.message||err);
  se159Draw();return false;
 });
 return se159.started;
}
// The original LAN Bridge remains the genuine local subnet scanner on its
// own HTTP origin. Only the hosted HTTPS browser receives cloud discovery.
const se159PriorScan=se146Scan;
se146Scan=async function(force=false){
 const result=await se159PriorScan(force);
 if(!se159Enabled()||!se146Lan.active)return result;
 se159Start();
 if(force)se159Probe();
 se159Draw();
 return result;
};
const se159PriorHost=se151HostGame;
se151HostGame=async function(...args){
 if(se159Enabled())se159Start();
 const result=await se159PriorHost(...args);
 const peer=se151.peer;
 if(peer&&se159Enabled()){
  const announce=()=>se159Start().then(()=>se159Publish('open'));
  peer.on('open',announce);
  if(peer.open)announce();
 }
 return result;
};
const se159PriorDisconnect=se151Disconnect;
se151Disconnect=function(...args){
 if(se159.listed)se159Publish('closed');
 return se159PriorDisconnect(...args);
};
const se159PriorInstall=se146Install;
se146Install=function(...args){
 const result=se159PriorInstall(...args);
 if(se159Enabled()){
  const root=se146Lan.root;
  const head=root?.querySelector('.se146-list-head');
  if(head&&!root.querySelector('#se159DiscoveryHint')){
   const hint=document.createElement('p');
   hint.id='se159DiscoveryHint';hint.className='se146-status';
   hint.textContent='Automatically finds open lobbies sharing your public internet connection (for example, the same Wi-Fi). Uses a public test directory. On different networks, use the invite code.';
   head.after(hint);
  }
 }
 return result;
};
window.SWYRL_ENGINE_LAN.liveGames=()=>({
 online:se159.connected,networkGroup:se159.net,
 listed:se159.rooms.size,hostingAdvertised:se159.listed,
 rooms:[...se159.rooms.values()].map(x=>({id:x.id,players:x.players,age:Date.now()-x.seen}))
});
