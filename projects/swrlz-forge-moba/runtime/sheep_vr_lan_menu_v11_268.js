// §E v11.268 — existing Sheep Tag LAN/WebRTC lobby from the Quest VR main menu.
// The renderer, XR input, room discovery, authoritative simulation and game
// transitions remain owned by the prior runtime. No private subnet scans.
const se268VRLan={
  board:null,lastBoard:'',lastPaint:0,lastList:'',status:'Choose HOST or FIND ROOMS.',
  lastError:'',attempts:0,joins:0,hosts:0,starts:0,disposed:0
};
function se268MenuActive(){
  return renderer.xr.isPresenting&&se195Menu()&&se195.mode==='menu';
}
function se268OnLanPage(){
  return se268MenuActive()&&(se195.page==='lan'||se195.page==='lanRooms');
}
function se268Rooms(){
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
function se268Status(msg,failed=false){
  se268VRLan.status=String(msg||'');
  if(failed)se268VRLan.lastError=se268VRLan.status;
  se268VRLan.lastBoard='';se268VRLan.lastPaint=0;
}
function se268EnsureBrowser(){
  if(!se268MenuActive()||!seLevels?.playingMenu){
    se268Status('Start the Sheep Tag Main Menu first.',true);return false;
  }
  // The existing UI remains the owner of the room, invite input, discovery
  // and cleanup; the 2D DOM is hidden by WebXR, never rendered as a VR panel.
  if(!se146Lan.active||!se146Lan.root||se146Lan.root.parentElement!==seLevels.overlay){
    if(se146Open()!==true){se268Status('The Local LAN screen is unavailable.',true);return false;}
  }
  return true;
}
function se268BoardLines(){
  const mode=location.protocol==='https:'?'DIRECT WEBRTC · cloud signaling':'LOCAL LAN BRIDGE';
  const host=se149Peer.mode==='host',guest=se149Peer.mode==='guest';
  const code=se151.room||se149Peer.roomId||'';
  const peers=se150ReadyGuests();
  const rooms=se268Rooms();
  const first=['SHEEP TAG / LOCAL LAN',mode,
    host?'ROLE HOST · '+(peers.length+1)+'/8 PLAYERS':
      guest?'ROLE GUEST · WAITING FOR HOST':'NO ACTIVE LOBBY',
    se150Match.active?'MATCH IN PROGRESS':se268VRLan.status];
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
function se268BoardCreate(){
  if(se268VRLan.board)return se268VRLan.board;
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
  se268VRLan.board={root,face,canvas,texture};
  return se268VRLan.board;
}
function se268BoardDispose(){
  const board=se268VRLan.board;if(!board)return;
  scene.remove(board.root);board.face.geometry.dispose();
  board.face.material.dispose();board.texture.dispose();
  se268VRLan.board=null;se268VRLan.lastBoard='';
  se268VRLan.lastPaint=0;se268VRLan.disposed++;
}
function se268BoardPaint(now){
  if(!se268OnLanPage()){se268BoardDispose();return;}
  const board=se268BoardCreate();if(!board)return;
  if(now-se268VRLan.lastPaint<850)return;
  se268VRLan.lastPaint=now;
  const lines=se268BoardLines(),key=lines.join('\n');
  if(key===se268VRLan.lastBoard)return;
  se268VRLan.lastBoard=key;
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
const se268OriginalOptions=se195Options;
se195Options=function(mode=se195.mode,page=se195.page){
  if(mode==='menu'&&page==='lan')return [
    ['lanHost','HOST'],['lanRooms','FIND ROOMS'],['lanPaste','JOIN CODE'],
    ['lanCopy','COPY INVITE'],['lanStart','START MATCH'],['lanLeave','LEAVE'],['back','BACK']
  ];
  if(mode==='menu'&&page==='lanRooms'){
    const available=se268Rooms();
    const options=available.map((_,i)=>['lanJoin'+i,'JOIN '+(i+1)]);
    return [...options,['lanRefresh','REFRESH'],['back','BACK']];
  }
  const options=se268OriginalOptions(mode,page);
  if(mode==='menu'&&page==='main'&&!options.some(item=>item[0]==='lanPage'))
    return [...options.filter(item=>item[0]!=='editor'),
      ['lanPage','LOCAL LAN'],...options.filter(item=>item[0]==='editor')];
  return options;
};
function se268RefreshRoomChoices(){
  if(!se268OnLanPage()||se195.page!=='lanRooms')return;
  const signature=se268Rooms().map(r=>r.id||r.name+':'+r.label).join('|');
  if(signature===se268VRLan.lastList)return;
  se268VRLan.lastList=signature;
  se195MakeRadial(false);
}
function se268OpenLan(){
  se268EnsureBrowser();
  se268VRLan.lastList='';
  se195Page('lan');
  se268BoardPaint(performance.now()+900);
}
function se268Host(){
  if(!se268EnsureBrowser())return true;
  if(se149Peer.mode==='host'){se268Status('Already hosting. Copy invite or START.');return true;}
  se268VRLan.attempts++;
  se268Status('Starting host lobby…');
  const job=location.protocol==='https:'?se151HostGame():se146Host();
  Promise.resolve(job).then(()=>{
    se268VRLan.hosts++;se268Status('Host request sent. Waiting for lobby confirmation.');
  }).catch(error=>se268Status('Unable to host: '+(error?.message||error),true));
  return true;
}
function se268JoinCode(code){
  if(!se268EnsureBrowser())return;
  if(location.protocol!=='https:'){
    se268Status('Bridge-only joins: use FIND ROOMS.',true);return;
  }
  const input=se146Lan.root?.querySelector('#se149OfferIn');
  if(!input){se268Status('Invite field unavailable. Reopen Local LAN.',true);return;}
  let id;
  try{id=se151CloudInvite(code);}catch(error){
    se268Status('Invite unavailable. Copy host code or use FIND ROOMS.',true);return;
  }
  input.value=id;se268VRLan.attempts++;se268Status('Connecting to host…');
  Promise.resolve(se151JoinGame()).then(()=>{
    se268VRLan.joins++;se268Status('Join requested. Waiting for verified peer connection.');
  }).catch(error=>se268Status('Unable to join: '+(error?.message||error),true));
}
function se268PasteJoin(){
  if(!se268EnsureBrowser())return true;
  const fallback=se146Lan.root?.querySelector('#se149OfferIn')?.value||'';
  // readText is requested only from a real trigger click (not an XR frame).
  if(location.protocol==='https:'&&navigator.clipboard?.readText){
    navigator.clipboard.readText().then(text=>se268JoinCode(text))
      .catch(()=>se268JoinCode(fallback));
  }else se268JoinCode(fallback);
  return true;
}
function se268JoinRoom(index){
  if(!se268EnsureBrowser())return true;
  const room=se268Rooms()[index];
  if(!room){se268Status('Lobby no longer visible; refresh rooms.',true);return true;}
  if(location.protocol==='https:')se268JoinCode(room.id);
  else if(!room.button?.disabled){room.button.click();se268Status('Joining selected LAN Bridge lobby…');}
  else se268Status('Selected LAN Bridge lobby cannot be joined.',true);
  return true;
}
function se268Copy(){
  const id=se151.room||se149Peer.roomId;
  if(!id){se268Status('Host a lobby first.',true);return true;}
  if(!navigator.clipboard?.writeText){
    se268Status('Clipboard unavailable. Read the code on the LAN board.',true);
    return true;
  }
  navigator.clipboard.writeText(id).then(()=>se268Status('Exact host invite copied.'))
    .catch(()=>se268Status('Quest clipboard denied; invite displayed above.',true));
  return true;
}
function se268StartMatch(){
  if(se149Peer.mode!=='host'){se268Status('Only the lobby host can START MATCH.',true);return true;}
  if(!se150ReadyGuests().length){
    se268Status('Waiting for a connected guest before START.',true);return true;
  }
  if(se150HostStart()===false){
    se268Status('Match did not start. Check connected seats.',true);
  }else{se268VRLan.starts++;se268Status('Host launched multiplayer match.');}
  return true;
}
function se268Leave(){
  se268Status('Leaving multiplayer lobby…');
  Promise.resolve(se148LeaveRoom()).then(()=>{
    if(se149Peer.mode==='host'||se149Peer.mode==='guest')se149Close();
    se268Status('Left lobby. Single-player still available.');
  }).catch(err=>se268Status('Cannot leave: '+(err?.message||err),true));
  return true;
}
const se268PreviousAction=se195HandleAction;
se195HandleAction=function(action,record){
  if(se268MenuActive()){
    if(action==='lanPage'){se268OpenLan();return true;}
    if(action==='back'&&se195.page==='lanRooms'){se195Page('lan');return true;}
    if(action==='back'&&se195.page==='lan'){se268BoardDispose();se195Page('main');return true;}
    if(action==='lanHost')return se268Host();
    if(action==='lanRooms'){
      se268EnsureBrowser();se268VRLan.lastList='';
      if(location.protocol==='https:')se159Probe();
      else se146Scan(true);
      se195Page('lanRooms');return true;
    }
    if(action==='lanPaste')return se268PasteJoin();
    if(action==='lanCopy')return se268Copy();
    if(action==='lanStart')return se268StartMatch();
    if(action==='lanLeave')return se268Leave();
    if(action==='lanRefresh'){
      if(se268EnsureBrowser()){
        if(location.protocol==='https:')se159Probe();
        se146Scan(true);
      }
      se268Status('Refreshing active lobby directory…');return true;
    }
    if(action.startsWith('lanJoin')&&/^lanJoin[0-3]$/.test(action))
      return se268JoinRoom(Number(action.slice(-1)));
  }
  return se268PreviousAction(action,record);
};
const se268PriorXRFrame=se193XRFrame;
se193XRFrame=function(){
  const result=se268PriorXRFrame();
  if(!se268OnLanPage()){se268BoardDispose();return result;}
  se268RefreshRoomChoices();
  se268BoardPaint(performance.now());
  return result;
};
const se268PriorCleanup=se193XRCleanup;
se193XRCleanup=function(){
  se268BoardDispose();
  // Preserve the host/guest network session; it belongs to existing LAN code.
  return se268PriorCleanup();
};
window.SWYRL_ENGINE_SHEEP_VR_LAN_268=Object.freeze({
  diagnose:()=>({
    xr:se268MenuActive(),lanPage:se195.page,active:!!se146Lan.active,
    role:se149Peer.mode||'none',hostRoom:se151.room||'',
    connectedGuests:se150ReadyGuests().length,liveRooms:se268Rooms().length,
    boardVisible:!!se268VRLan.board,attempts:se268VRLan.attempts,
    hostAttempts:se268VRLan.hosts,joinAttempts:se268VRLan.joins,
    starts:se268VRLan.starts,boardDisposals:se268VRLan.disposed,
    lastStatus:se268VRLan.status,lastError:se268VRLan.lastError,
    privateSubnetScan:false,
    connection:'existing PeerJS/WebRTC or local HTTP Bridge'
  }),
  open:se268OpenLan
});
