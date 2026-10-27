// §E v11.149: edit-menu parity and real local-only WebRTC lobby via manual codes.
// No signaling server, fake IP scan, internet relay, or multiplayer game authority.
const se149Peer={mode:'',roomId:'',links:[],guest:null,room:null};
function se149Copy(value){if(navigator.clipboard?.writeText)return navigator.clipboard.writeText(value);
 return Promise.reject(new Error('Select and copy the code manually'));}
function se149Message(value){se148Say(value);se146Message(value);}
function se149Decode(raw){
 const code=String(raw||'').trim();
 if(code.length>35000||code.length<12)throw new Error('Invalid invite/reply code');
 let msg;
 try{msg=JSON.parse(atob(code));}catch{throw new Error('Malformed invite/reply code');}
 if(msg.protocol!=='se149-peer-lan-v1'||!['offer','answer'].includes(msg.kind)||
    typeof msg.roomId!=='string'||typeof msg.sdp!=='string'||msg.sdp.length>24000)
  throw new Error('This code is not a Sheep Tag LAN invite/reply');
 return msg;
}
function se149Encode(kind,roomId,sdp){
 return btoa(JSON.stringify({protocol:'se149-peer-lan-v1',kind,roomId,sdp}));
}
function se149Gather(pc){
 return new Promise(resolve=>{
  if(pc.iceGatheringState==='complete'){resolve();return;}
  const on=()=>{if(pc.iceGatheringState==='complete'){pc.removeEventListener('icegatheringstatechange',on);resolve();}};
  pc.addEventListener('icegatheringstatechange',on);
  setTimeout(()=>{pc.removeEventListener('icegatheringstatechange',on);resolve();},8500);
 });
}
function se149Status(){
 const peers=se149Peer.links.filter(x=>x.channel?.readyState==='open'&&x.name);
 const slots=[{seat:1,name:'Host',role:'host',occupied:true}];
 for(let n=2;n<=8;n++){
  const p=peers[n-2];
  slots.push({seat:n,name:p?.name||'',role:p?'guest':'open',occupied:!!p});
 }
 return {id:se149Peer.roomId,name:'Sheep Tag LAN',players:peers.length+1,
         capacity:8,slots,phase:'waiting',canStartMatch:false};
}
function se149PaintPeer(){
 if(se149Peer.mode!=='host')return;
 const game=se149Status();
 se148DrawRoom(game);
 for(const p of se149Peer.links){
  if(p.channel?.readyState==='open')
   try{p.channel.send(JSON.stringify({kind:'roster',game}));}catch{}
 }
}
function se149Close(){
 for(const p of se149Peer.links){try{p.channel?.close();p.pc?.close();}catch{}}
 try{se149Peer.guest?.close();}catch{}
 se149Peer.mode='';se149Peer.roomId='';se149Peer.links=[];se149Peer.guest=null;
 se149Peer.room?.remove();se149Peer.room=null;
}
function se149Form(){
 const pane=se148Room.screen;if(!pane)return null;
 se149Peer.room?.remove();
 const box=document.createElement('section');
 box.id='se149PeerControls';
 box.innerHTML='<h3>Direct Wi-Fi lobby · invitation codes</h3>'+
  '<p>Local browser-to-browser connection. Share codes directly with a guest; the public site cannot automatically scan Wi-Fi hosts.</p>'+
  '<div id="se149HostTools"><button type="button" id="se149CreateInvite">Create Guest Invite</button>'+
  '<textarea id="se149OfferOut" aria-label="Host invite code" readonly placeholder="Invite appears here"></textarea>'+
  '<button type="button" id="se149CopyOffer">Copy Invite</button>'+
  '<textarea id="se149ReplyIn" aria-label="Guest reply code" placeholder="Paste guest reply here"></textarea>'+
  '<button type="button" id="se149AcceptReply">Connect Guest</button></div>'+
  '<div id="se149GuestTools" hidden><textarea id="se149AnswerOut" aria-label="Guest answer code" readonly></textarea>'+
  '<button type="button" id="se149CopyAnswer">Copy Answer for Host</button>'+
  '<p>Send this answer to the host. Your occupied seat appears when the host connects.</p></div>';
 const start=pane.querySelector('#se148Start');start?.after(box);
 box.querySelector('#se149CreateInvite').onclick=se149CreateInvite;
 box.querySelector('#se149AcceptReply').onclick=se149AcceptReply;
 box.querySelector('#se149CopyOffer').onclick=()=>se149Copy(box.querySelector('#se149OfferOut').value).catch(e=>se149Message(e.message));
 box.querySelector('#se149CopyAnswer').onclick=()=>se149Copy(box.querySelector('#se149AnswerOut').value).catch(e=>se149Message(e.message));
 se149Peer.room=box;return box;
}
function se149EnterRoom(owner,roomId){
 se149Peer.mode=owner?'host':'guest';se149Peer.roomId=roomId;
 se148OpenRoom({owner,gameId:roomId,host:'browser-peer',port:0});
 const box=se149Form();
 box.querySelector('#se149HostTools').hidden=!owner;
 box.querySelector('#se149GuestTools').hidden=owner;
 if(owner)se149PaintPeer();
 else se148DrawRoom({id:roomId,name:'Sheep Tag LAN',players:1,capacity:8,
  slots:[{seat:1,name:'Host',role:'host',occupied:true},
   ...Array.from({length:7},(_,i)=>({seat:i+2,name:'',role:'open',occupied:false}))]});
 se149Message(owner?'Host lobby created. Generate an invite for each guest.':'Send the generated answer to the host.');
}
function se149Host(){
 if(!window.RTCPeerConnection||!window.crypto?.randomUUID){
  se146Message('This browser cannot host a peer-to-peer LAN room. Use the local LAN Bridge.');return;
 }
 se149Close();
 se149EnterRoom(true,crypto.randomUUID());
}
async function se149CreateInvite(){
 if(se149Peer.mode!=='host')return;
 if(se149Peer.links.length>=7){se149Message('All seven guest connections are allocated.');return;}
 const box=se149Peer.room;const button=box.querySelector('#se149CreateInvite');
 button.disabled=true;
 try{
  const pc=new RTCPeerConnection({iceServers:[]});
  const entry={pc,channel:pc.createDataChannel('sheep-lan-room'),name:'',answerPending:true};
  se149Peer.links.push(entry);
  const channel=entry.channel;
  channel.onmessage=ev=>{
   let data;try{data=JSON.parse(ev.data);}catch{return;}
   if(data.kind==='hello'&&typeof data.name==='string'){
    entry.name=data.name.trim().slice(0,32)||'Guest';
    se149PaintPeer();
   }
  };
  channel.onclose=()=>{se149Peer.links=se149Peer.links.filter(x=>x!==entry);se149PaintPeer();};
  pc.onconnectionstatechange=()=>{if(['failed','closed','disconnected'].includes(pc.connectionState)){
   entry.name='';se149PaintPeer();
  }};
  await pc.setLocalDescription(await pc.createOffer());
  await se149Gather(pc);
  box.querySelector('#se149OfferOut').value=se149Encode('offer',se149Peer.roomId,pc.localDescription.sdp);
  box.querySelector('#se149ReplyIn').value='';
  box.querySelector('#se149AcceptReply').dataset.slot=String(se149Peer.links.indexOf(entry));
  se149Message('Share the invite code, then paste that guest’s answer below.');
 }catch(e){se149Message('Unable to create invite: '+e.message);}
 finally{button.disabled=false;}
}
async function se149AcceptReply(){
 if(se149Peer.mode!=='host')return;
 const box=se149Peer.room;
 try{
  const response=se149Decode(box.querySelector('#se149ReplyIn').value);
  if(response.kind!=='answer'||response.roomId!==se149Peer.roomId)throw new Error('Reply belongs to a different room');
  const slot=Number(box.querySelector('#se149AcceptReply').dataset.slot);
  const entry=se149Peer.links[slot];
  if(!entry||!entry.answerPending)throw new Error('Create an invite for this guest first');
  await entry.pc.setRemoteDescription({type:'answer',sdp:response.sdp});
  entry.answerPending=false;
  se149Message('Reply accepted. Waiting for direct Wi-Fi connection.');
 }catch(e){se149Message('Cannot connect guest: '+e.message);}
}
async function se149JoinInvite(){
 const code=se146Lan.root?.querySelector('#se149OfferIn')?.value;
 let pc;
 try{
  const offer=se149Decode(code);
  if(offer.kind!=='offer')throw new Error('Paste the host invite, not a reply');
  if(!window.RTCPeerConnection)throw new Error('WebRTC unavailable in this browser');
  se149Close();
  pc=new RTCPeerConnection({iceServers:[]});
  se149Peer.guest=pc;
  pc.ondatachannel=event=>{
   const ch=event.channel;
   ch.onopen=()=>{
    const name=String(se146Lan.root?.querySelector('#se148PlayerName')?.value||'Guest').slice(0,32);
    ch.send(JSON.stringify({kind:'hello',name}));
   };
   ch.onmessage=ev=>{
    let packet;try{packet=JSON.parse(ev.data);}catch{return;}
    if(packet.kind==='roster'&&packet.game?.id===offer.roomId)se148DrawRoom(packet.game);
   };
   ch.onclose=()=>se149Message('Host disconnected. Return to the LAN browser.');
  };
  await pc.setRemoteDescription({type:'offer',sdp:offer.sdp});
  await pc.setLocalDescription(await pc.createAnswer());
  await se149Gather(pc);
  const answer=se149Encode('answer',offer.roomId,pc.localDescription.sdp);
  se149EnterRoom(false,offer.roomId);
  se149Peer.room.querySelector('#se149AnswerOut').value=answer;
 }catch(e){try{pc?.close();}catch{}se146Message('Cannot join invite: '+e.message);}
}
const se149PriorScan=se146Scan;
se146Scan=async function(force=false){
 if(location.protocol==='https:'){
  if(!se146Lan.active)return;
  se146Lan.bridge=false;se146Lan.canHost=false;se146Lan.hosting=false;
  se146Draw([]);
  const button=se146Lan.root?.querySelector('#se146LanHost');
  if(button){button.disabled=false;button.textContent='＋ Host Game';button.onclick=se149Host;}
  se146Message('Host Game uses direct Wi-Fi invite codes. Automatic LAN discovery still requires the local bridge.');
  return;
 }
 return se149PriorScan(force);
};
const se149PriorInstall=se146Install;
se146Install=function(...args){
 const result=se149PriorInstall(...args);
 const pane=se146Lan.root;
 if(pane&&!pane.querySelector('#se149OfferIn')){
  const box=document.createElement('div');box.className='se149-join';
  box.innerHTML='<label>Join by invitation code<textarea id="se149OfferIn" placeholder="Paste host invitation"></textarea></label>'+
    '<button type="button" id="se149JoinInvite">Join with Invite</button>';
  const head=pane.querySelector('.se146-list-head');head?.before(box);
  box.querySelector('#se149JoinInvite').onclick=se149JoinInvite;
 }
 return result;
};
const se149PriorRefresh=se148Refresh;
se148Refresh=async function(){
 if(se149Peer.mode)return;
 return se149PriorRefresh();
};
const se149PriorLeaveRoom=se148LeaveRoom;
se148LeaveRoom=async function(){
 if(se149Peer.mode){
  se149Close();se148ClearRoom();
  if(se146Lan.active){se146Lan.root.hidden=false;se146Scan(true);}
  return;
 }
 return se149PriorLeaveRoom();
};
const se149PriorLeave=se146Leave;
se146Leave=function(...args){se149Close();return se149PriorLeave(...args);};
// Keep the editor authoring preview equivalent to the runtime launch menu.
// Only preview DOM changes; authored level actors and editor camera stay editable.
function se149PreviewParity(){
 const preview=seLevels.preview;
 const panel=preview?.querySelector('.st141-menu-panel');
 if(!panel||panel.querySelector('#se149PreviewLan'))return;
 const button=document.createElement('button');
 button.type='button';button.id='se149PreviewLan';
 button.textContent='LOCAL LAN';button.disabled=true;button.tabIndex=-1;
 panel.appendChild(button);
}
const se149PreviousLevelsUI=seLevelsEnsureUI;
seLevelsEnsureUI=function(...args){const result=se149PreviousLevelsUI(...args);se149PreviewParity();return result;};
se149PreviewParity();
