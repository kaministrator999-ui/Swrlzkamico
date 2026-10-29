// §E v11.151 — one-code join for public HTTPS via PeerJS Cloud signaling.
// The cloud introduces peers; WebRTC carries data directly when supported.
// No automatic private-subnet discovery; no synchronized gameplay replication.
const se151={peer:null,room:'',host:false,guestConn:null,serial:0};
function se151Notice(msg){
 const el=se148Room.screen?.querySelector('#se148Notice');
 if(el)el.textContent=msg;
 else se146Message(msg);
}
function se151Library(){
 if(typeof window.Peer==='function')return Promise.resolve(window.Peer);
 if(se151.library)return se151.library;
 se151.library=new Promise((resolve,reject)=>{
  const script=document.createElement('script');
  script.src='https://cdn.jsdelivr.net/npm/peerjs@1.5.5/dist/peerjs.min.js';
  script.async=true;
  script.onload=()=>typeof window.Peer==='function'?resolve(window.Peer):reject(new Error('Peer library was blocked'));
  script.onerror=()=>reject(new Error('Peer library could not load; check internet access'));
  document.head.appendChild(script);
 }).catch(error=>{se151.library=null;throw error;});
 return se151.library;
}
function se151Disconnect(){
 const peer=se151.peer;
 se151.peer=null;se151.room='';se151.host=false;se151.serial++;
 try{se151.guestConn?.close();}catch{}
 se151.guestConn=null;
 try{peer?.destroy();}catch{}
}
function se151Wrap(connection){
 return {
  get readyState(){return connection.open?'open':'closed';},
  send(data){connection.send(data);},
  close(){connection.close();}
 };
}
function se151AddRoomUI(isHost,room){
 const panel=se148Room.screen;if(!panel)return;
 const previous=panel.querySelector('#se151OneCode');
 previous?.remove();
 const legacy=panel.querySelector('#se149PeerControls');
 if(legacy)legacy.hidden=true;
 const section=document.createElement('section');
 section.id='se151OneCode';
 const heading=document.createElement('h3');
 heading.textContent=isHost?'One-code guest invitation':'Connecting to host';
 section.appendChild(heading);
 const summary=document.createElement('p');
 summary.textContent=isHost?
  'Copy this invitation. A guest enters it once to join automatically—no answer code.' :
  'The host controls Start Match. Your seat appears after the peer connection opens.';
 section.appendChild(summary);
 if(isHost){
  const invite=document.createElement('textarea');
  invite.id='se151InviteOut';invite.readOnly=true;invite.value=room;invite.rows=2;
  invite.setAttribute('aria-label','Host invitation code');
  section.appendChild(invite);
  const copy=document.createElement('button');
  copy.type='button';copy.textContent='Copy Invite';
  copy.onclick=()=>se149Copy(room).then(()=>se151Notice('Invite copied. Guest only needs this code.')).catch(e=>se151Notice(e.message));
  section.appendChild(copy);
 }
 const disclosure=document.createElement('p');
 disclosure.className='se151-disclosure';
 disclosure.textContent='PeerJS Cloud introduces devices over the internet. Game data uses a direct WebRTC connection when the network permits. Match positions/buildings are not synchronized yet.';
 section.appendChild(disclosure);
 if(legacy)legacy.before(section);else panel.appendChild(section);
}
function se151HostAttach(conn,serial){
 if(serial!==se151.serial||!se151.host){conn.close();return;}
 if(se149Peer.links.length>=7){conn.close();se151Notice('Lobby full (8/8).');return;}
 const entry={pc:null,channel:se151Wrap(conn),name:'',cloud:true};
 se149Peer.links.push(entry);
 conn.on('data',message=>{
  if(serial!==se151.serial)return;
  let payload;
  try{payload=typeof message==='string'?JSON.parse(message):message;}catch{return;}
  if(payload?.kind==='hello'&&typeof payload.name==='string'){
   entry.name=payload.name.trim().slice(0,32)||'Guest';
   se149PaintPeer();
  }
 });
 conn.on('close',()=>{
  se149Peer.links=se149Peer.links.filter(x=>x!==entry);
  if(!se150Match.active)se149PaintPeer();
 });
 conn.on('error',()=>{entry.name='';if(!se150Match.active)se149PaintPeer();});
}
async function se151HostGame(){
 if(se150Match.active)return;
 const prior=se151.serial+1;
 se151Disconnect();
 se149Peer.links.length=0;
 try{
  const Peer=await se151Library();
  if(prior!==se151.serial)return;
  const id='se151-'+(window.crypto?.randomUUID?.()||String(Date.now())).replace(/-/g,'');
  const peer=new Peer(id,{host:'0.peerjs.com',port:443,path:'/',secure:true});
  se151.peer=peer;se151.room=id;se151.host=true;
  peer.on('open',opened=>{
   if(se151.peer!==peer)return;
   se149Peer.mode='host';se149Peer.roomId=opened;
   se149EnterRoom(true,opened);
   se151AddRoomUI(true,opened);
   se151Notice('Hosting. Share the one invitation code with a guest.');
   se150StartControls();
  });
  peer.on('connection',conn=>se151HostAttach(conn,se151.serial));
  peer.on('error',err=>se151Notice('Signaling failed: '+(err?.message||err)));
  peer.on('disconnected',()=>se151Notice('Signaling server disconnected. Connected guests can remain, but new joins may fail.'));
 }catch(err){se151Notice('Cannot start one-code host: '+err.message);}
}
function se151CloudInvite(raw){
 const id=String(raw||'').trim();
 if(!/^se151-[a-z0-9]{10,80}$/i.test(id))throw Error('Invalid host invitation. Copy the full one-code invite.');
 return id;
}
async function se151JoinGame(){
 const pane=se146Lan.root;
 const input=pane?.querySelector('#se149OfferIn');
 const button=pane?.querySelector('#se149JoinInvite');
 let room;
 try{room=se151CloudInvite(input?.value);}catch(err){se146Message(err.message);return;}
 if(button)button.disabled=true;
 se151Disconnect();
 try{
  const Peer=await se151Library();
  const peer=new Peer(undefined,{host:'0.peerjs.com',port:443,path:'/',secure:true});
  se151.peer=peer;se151.room=room;se151.host=false;
  peer.on('open',()=>{
   if(se151.peer!==peer)return;
   const connection=peer.connect(room,{reliable:true,serialization:'json'});
   se151.guestConn=connection;
   connection.on('open',()=>{
    if(se151.peer!==peer)return;
    se149Peer.mode='guest';se149Peer.roomId=room;se149Peer.guest=null;
    se149EnterRoom(false,room);
    se151AddRoomUI(false,room);
    const name=String(pane?.querySelector('#se148PlayerName')?.value||'Guest').trim().slice(0,32)||'Guest';
    connection.send(JSON.stringify({kind:'hello',name}));
    se151Notice('Connected to host. Waiting for match start.');
   });
   connection.on('data',packet=>{
    const event=typeof packet==='string'?(()=>{try{return JSON.parse(packet);}catch{return null;}})():packet;
    if(!event||se151.peer!==peer)return;
    if(event.kind==='roster'&&event.game?.id===room)se148DrawRoom(event.game);
    if(event.kind==='match-start'||event.kind==='match-end')se150PeerPacket(JSON.stringify(event));
   });
   connection.on('close',()=>{
    if(se151.peer===peer)se151Notice('Host connection closed. Return to the LAN browser.');
   });
   connection.on('error',err=>se151Notice('Connection failed: '+(err?.message||err)));
  });
  peer.on('error',err=>se151Notice('Unable to join: '+(err?.message||err)));
 }catch(err){se146Message('Cannot join: '+err.message);}
 finally{if(button)button.disabled=false;}
}
// Keep original HTTP LAN Bridge lobby behavior available.
const se151OldHost=se149Host;
se149Host=function(...args){
 if(location.protocol==='https:')return se151HostGame(...args);
 return se151OldHost(...args);
};
window.SWYRL_ENGINE_LAN.hostPeer=se149Host;
const se151OldScan=se146Scan;
se146Scan=async function(force=false){
 const response=await se151OldScan(force);
 if(location.protocol==='https:'&&se146Lan.root){
  const button=se146Lan.root.querySelector('#se146LanHost');
  if(button){button.disabled=false;button.onclick=se149Host;button.textContent='＋ Host Game';}
  const field=se146Lan.root.querySelector('#se149OfferIn');
  if(field){field.placeholder='Paste host invitation code once';field.setAttribute('aria-label','Single host invite code');}
  se146Message('One-code joining available through PeerJS Cloud signaling; no reply code is required.');
 }
 return response;
};
const se151OldInstall=se146Install;
se146Install=function(...args){
 const result=se151OldInstall(...args);
 const root=se146Lan.root;
 const join=root?.querySelector('#se149JoinInvite');
 if(join){join.onclick=se151JoinGame;join.textContent='Join with Invite';}
 return result;
};
const se151OldClose=se149Close;
se149Close=function(...args){
 if(se150Match.active)return;
 se151Disconnect();
 return se151OldClose(...args);
};
const se151OldStop=stopSession;
stopSession=function(...args){
 const running=se150Match.active;
 const output=se151OldStop(...args);
 if(running&&!se150Match.active)se151Disconnect();
 return output;
};
window.SWYRL_ENGINE_LAN.oneCode=true;
