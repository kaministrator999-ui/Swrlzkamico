// §E v11.267 — existing Sheep Tag LAN/WebRTC lobby from the Quest VR main menu.
// The renderer, XR input, room discovery, authoritative simulation and game
// transitions remain owned by the prior runtime. No private subnet scans.
const se267VRLan={
  board:null,lastBoard:'',lastPaint:0,lastList:'',status:'Choose HOST or FIND ROOMS.',
  lastError:'',attempts:0,joins:0,hosts:0,starts:0,disposed:0
};
function se267MenuActive(){
  return renderer.xr.isPresenting&&se195Menu()&&se195.mode==='menu';
}
function se267OnLanPage(){
  return se267MenuActive()&&(se195.page==='lan'||se195.page==='lanRooms');
}
function se267Rooms(){
  if(location.protocol==='https:'){
    if(typeof se159ExpireNoRender==='function')se159ExpireNoRender();
    return [...se159.rooms.values()].filter(room=>room.players<room.capacity)
      .sort((a,b)=>b.seen-a.seen).slice(0,4).map(room=>({
        id:room.id,players:room.players,capacity:room.capacity,name:room.name||'Sheep Tag LAN'
      }));
  }
  return [...(se146Lan.root?.querySelectorAll('.se146-game')||[])].slice(0,4)
    .map((el,i)=>({index:i,name:el.querySelector('b')?.textContent||'Local lobby',
      label:el.querySelector('small')?.textContent||'',button:el.querySelector('button')}));
}
function se267Status(msg,failed=false){
  se267VRLan.status=String(msg||'');
  if(failed)se267VRLan.lastError=se267VRLan.status;
  se267VRLan.lastBoard='';se267VRLan.lastPaint=0;
}
function se267EnsureBrowser(){
  if(!se267MenuActive()||!seLevels?.playingMenu){
    se267Status('Start the Sheep Tag Main Menu first.',true);return false;
  }
  // The existing UI remains the owner of the room, invite input, discovery
  // and cleanup; the 2D DOM is hidden by WebXR, never rendered as a VR panel.
  if(!se146Lan.active||!se146Lan.root||se146Lan.root.parentElement!==seLevels.overlay){
    if(se146Open()!==true){se267Status('The Local LAN screen is unavailable.',true);return false;}
  }
  return true;
}
function se267BoardLines(){
  const mode=location.protocol==='https:'?'DIRECT WEBRTC · cloud signaling':'LOCAL LAN BRIDGE';
  const host=se149Peer.mode==='host',guest=se149Peer.mode==='guest';
  const code=se151.room||se149Peer.roomId||'';
  const peers=se150ReadyGuests();
  const rooms=se267Rooms();
  const first=['SHEEP TAG / LOCAL LAN',mode,
    host?'ROLE HOST · '+(peers.length+1)+'/8 PLAYERS':
      guest?'ROLE GUEST · WAITING FOR HOST':'NO ACTIVE LOBBY',
    se150Match.active?'MATCH IN PROGRESS':se267VRLan.status];
  if(host&&code){
    first.push('INVITE (COPY sends exact code):');
    // Present the same exact code in two lines, without inserting spaces.
    first.push(code.slice(0,23));
    if(code.length>23)first.push(code.slice(23));
  }
  if(se195.page==='lanRooms'){
    first.push('OPEN ROOMS (SAME INTERNET EXIT):');
    if(!rooms.length)first.push(se159.connected?'No available rooms':'Directory unavailable / loading');
    rooms.forEach((room,i)=>first.push(
      (i+1)+'. '+room.name.slice(0,18)+' · '+
      (room.players===undefined?room.label:room.players+'/'+room.capacity+' players')));
  }else{
    first.push('Use radial: HOST / ROOMS / JOIN / START');
    if(!host&&!guest)first.push('JOIN reads invite from Quest clipboard');
    if(host)first.push('START requires a connected guest');
  }
  first.push('HTTPS: not a private Wi-Fi subnet scan');
  first.push('Actual host-authoritative WebRTC match');
  return first;
}
function se267BoardCreate(){
  if(se267VRLan.board)return se267VRLan.board;
  const pose=se191XRHeadPose();
  if(!pose)return null;
  const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=768;
  const texture=new THREE.CanvasTexture(canvas);
  texture.colorSpace=THREE.SRGBColorSpace;
  texture.minFilter=THREE.LinearFilter;texture.magFilter=THREE.LinearFilter;
  texture.generateMipmaps=false;
  const root=new THREE.Group();root.name='§E · Sheep Tag LAN world-pinned lobby board';
  const face=new THREE.Mesh(new THREE.PlaneGeometry(1.22,.92),
    new THREE.MeshBasicMaterial({map:texture,transparent:true,depthTest:false,
      depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
  face.renderOrder=10820;face.frustumCulled=false;
  face.raycast=function(){return null;}; // decorative: no ray passthrough or collision
  root.add(face);
  const horizontal=pose.forward.clone();horizontal.y=0;
  if(horizontal.lengthSq()<.01)horizontal.set(0,0,-1);
  horizontal.normalize();
  const right=new THREE.Vector3().crossVectors(horizontal,new THREE.Vector3(0,1,0)).normalize();
  root.position.copy(pose.eye).addScaledVector(horizontal,1.55)
    .addScaledVector(right,-.36).add(new THREE.Vector3(0,.16,0));
  // Orient ONCE at creation. The board never chases headset gaze.
  root.lookAt(pose.eye);
  scene.add(root);
  se267VRLan.board={root,face,canvas,texture};
  return se267VRLan.board;
}
function se267BoardDispose(){
  const board=se267VRLan.board;if(!board)return;
  scene.remove(board.root);board.face.geometry.dispose();
  board.face.material.dispose();board.texture.dispose();
  se267VRLan.board=null;se267VRLan.lastBoard='';
  se267VRLan.lastPaint=0;se267VRLan.disposed++;
}
function se267BoardPaint(now){
  if(!se267OnLanPage()){se267BoardDispose();return;}
  const board=se267BoardCreate();if(!board)return;
  if(now-se267VRLan.lastPaint<850)return;
  se267VRLan.lastPaint=now;
  const lines=se267BoardLines(),key=lines.join('\n');
  if(key===se267VRLan.lastBoard)return;
  se267VRLan.lastBoard=key;
  const ctx=board.canvas.getContext('2d');if(!ctx)return;
  const grad=ctx.createLinearGradient(0,0,0,768);
  grad.addColorStop(0,'#123f53');grad.addColorStop(1,'#06151f');
  ctx.fillStyle=grad;ctx.fillRect(0,0,1024,768);
  ctx.strokeStyle='#65e9df';ctx.lineWidth=9;ctx.strokeRect(12,12,1000,744);
  ctx.font='bold 37px sans-serif';ctx.textBaseline='middle';
  lines.forEach((line,i)=>{
    if(i>13)return;
    ctx.fillStyle=i===0?'#8fffe9':i===1?'#a0bdc3':'#effcfb';
    const str=String(line);
    ctx.fillText(str.length>53?str.slice(0,53):str,36,58+i*51,950);
  });
  board.texture.needsUpdate=true;
}
const se267OriginalOptions=se195Options;
se195Options=function(mode=se195.mode,page=se195.page){
  if(mode==='menu'&&page==='lan')return [
    ['lanHost','HOST'],['lanRooms','FIND ROOMS'],['lanPaste','JOIN CODE'],
    ['lanCopy','COPY INVITE'],['lanStart','START MATCH'],['lanLeave','LEAVE'],['back','BACK']
  ];
  if(mode==='menu'&&page==='lanRooms'){
    const available=se267Rooms();
    const options=available.map((_,i)=>['lanJoin'+i,'JOIN '+(i+1)]);
    return [...options,['lanRefresh','REFRESH'],['back','BACK']];
  }
  const options=se267OriginalOptions(mode,page);
  if(mode==='menu'&&page==='main'&&!options.some(item=>item[0]==='lanPage'))
    return [...options.filter(item=>item[0]!=='editor'),
      ['lanPage','LOCAL LAN'],...options.filter(item=>item[0]==='editor')];
  return options;
};
function se267RefreshRoomChoices(){
  if(!se267OnLanPage()||se195.page!=='lanRooms')return;
  const signature=se267Rooms().map(r=>r.id||r.name+':'+r.label).join('|');
  if(signature===se267VRLan.lastList)return;
  se267VRLan.lastList=signature;
  se195MakeRadial(false);
}
function se267OpenLan(){
  se267EnsureBrowser();
  se267VRLan.lastList='';
  se195Page('lan');
  se267BoardPaint(performance.now()+900);
}
function se267Host(){
  if(!se267EnsureBrowser())return true;
  if(se149Peer.mode==='host'){se267Status('Already hosting. Copy invite or START.');return true;}
  se267VRLan.attempts++;
  se267Status('Starting host lobby…');
  const job=location.protocol==='https:'?se151HostGame():se146Host();
  Promise.resolve(job).then(()=>{
    se267VRLan.hosts++;se267Status('Host request sent. Waiting for lobby confirmation.');
  }).catch(error=>se267Status('Unable to host: '+(error?.message||error),true));
  return true;
}
function se267JoinCode(code){
  if(!se267EnsureBrowser())return;
  if(location.protocol!=='https:'){
    se267Status('Bridge-only joins: use FIND ROOMS.',true);return;
  }
  const input=se146Lan.root?.querySelector('#se149OfferIn');
  if(!input){se267Status('Invite field unavailable. Reopen Local LAN.',true);return;}
  let id;
  try{id=se151CloudInvite(code);}catch(error){
    se267Status('Invite unavailable. Copy host code or use FIND ROOMS.',true);return;
  }
  input.value=id;se267VRLan.attempts++;se267Status('Connecting to host…');
  Promise.resolve(se151JoinGame()).then(()=>{
    se267VRLan.joins++;se267Status('Join requested. Waiting for verified peer connection.');
  }).catch(error=>se267Status('Unable to join: '+(error?.message||error),true));
}
function se267PasteJoin(){
  if(!se267EnsureBrowser())return true;
  const fallback=se146Lan.root?.querySelector('#se149OfferIn')?.value||'';
  // readText is requested only from a real trigger click (not an XR frame).
  if(location.protocol==='https:'&&navigator.clipboard?.readText){
    navigator.clipboard.readText().then(text=>se267JoinCode(text))
      .catch(()=>se267JoinCode(fallback));
  }else se267JoinCode(fallback);
  return true;
}
function se267JoinRoom(index){
  if(!se267EnsureBrowser())return true;
  const room=se267Rooms()[index];
  if(!room){se267Status('Lobby no longer visible; refresh rooms.',true);return true;}
  if(location.protocol==='https:')se267JoinCode(room.id);
  else if(!room.button?.disabled){room.button.click();se267Status('Joining selected LAN Bridge lobby…');}
  else se267Status('Selected LAN Bridge lobby cannot be joined.',true);
  return true;
}
function se267Copy(){
  const id=se151.room||se149Peer.roomId;
  if(!id){se267Status('Host a lobby first.',true);return true;}
  if(!navigator.clipboard?.writeText){
    se267Status('Clipboard unavailable. Read the code on the LAN board.',true);
    return true;
  }
  navigator.clipboard.writeText(id).then(()=>se267Status('Exact host invite copied.'))
    .catch(()=>se267Status('Quest clipboard denied; invite displayed above.',true));
  return true;
}
function se267StartMatch(){
  if(se149Peer.mode!=='host'){se267Status('Only the lobby host can START MATCH.',true);return true;}
  if(!se150ReadyGuests().length){
    se267Status('Waiting for a connected guest before START.',true);return true;
  }
  if(se150HostStart()===false){
    se267Status('Match did not start. Check connected seats.',true);
  }else{se267VRLan.starts++;se267Status('Host launched multiplayer match.');}
  return true;
}
function se267Leave(){
  se267Status('Leaving multiplayer lobby…');
  Promise.resolve(se148LeaveRoom()).then(()=>{
    if(se149Peer.mode==='host'||se149Peer.mode==='guest')se149Close();
    se267Status('Left lobby. Single-player still available.');
  }).catch(err=>se267Status('Cannot leave: '+(err?.message||err),true));
  return true;
}
const se267PreviousAction=se195HandleAction;
se195HandleAction=function(action,record){
  if(se267MenuActive()){
    if(action==='lanPage'){se267OpenLan();return true;}
    if(action==='back'&&se195.page==='lanRooms'){se195Page('lan');return true;}
    if(action==='back'&&se195.page==='lan'){se267BoardDispose();se195Page('main');return true;}
    if(action==='lanHost')return se267Host();
    if(action==='lanRooms'){
      se267EnsureBrowser();se267VRLan.lastList='';
      if(location.protocol==='https:')se159Probe();
      else se146Scan(true);
      se195Page('lanRooms');return true;
    }
    if(action==='lanPaste')return se267PasteJoin();
    if(action==='lanCopy')return se267Copy();
    if(action==='lanStart')return se267StartMatch();
    if(action==='lanLeave')return se267Leave();
    if(action==='lanRefresh'){
      if(se267EnsureBrowser()){
        if(location.protocol==='https:')se159Probe();
        se146Scan(true);
      }
      se267Status('Refreshing active lobby directory…');return true;
    }
    if(action.startsWith('lanJoin')&&/^lanJoin[0-3]$/.test(action))
      return se267JoinRoom(Number(action.slice(-1)));
  }
  return se267PreviousAction(action,record);
};
const se267PriorXRFrame=se193XRFrame;
se193XRFrame=function(){
  const result=se267PriorXRFrame();
  if(!se267OnLanPage()){se267BoardDispose();return result;}
  se267RefreshRoomChoices();
  se267BoardPaint(performance.now());
  return result;
};
const se267PriorCleanup=se193XRCleanup;
se193XRCleanup=function(){
  se267BoardDispose();
  // Preserve the host/guest network session; it belongs to existing LAN code.
  return se267PriorCleanup();
};
window.SWYRL_ENGINE_SHEEP_VR_LAN_267=Object.freeze({
  diagnose:()=>({
    xr:se267MenuActive(),lanPage:se195.page,active:!!se146Lan.active,
    role:se149Peer.mode||'none',hostRoom:se151.room||'',
    connectedGuests:se150ReadyGuests().length,liveRooms:se267Rooms().length,
    boardVisible:!!se267VRLan.board,attempts:se267VRLan.attempts,
    hostAttempts:se267VRLan.hosts,joinAttempts:se267VRLan.joins,
    starts:se267VRLan.starts,boardDisposals:se267VRLan.disposed,
    lastStatus:se267VRLan.status,lastError:se267VRLan.lastError,
    privateSubnetScan:false,
    connection:'existing PeerJS/WebRTC or local HTTP Bridge'
  }),
  open:se267OpenLan
});
