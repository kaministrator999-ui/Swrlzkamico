// §E v11.148: server-owned waiting lobby, not simulated multiplayer.
const se148Room={screen:null,session:null,timer:null,busy:false};
function se148Say(message){
 const el=se148Room.screen?.querySelector('#se148Notice');if(el)el.textContent=message;
}
function se148Post(path,body){
 return se146Fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
}
function se148RoomParams(session){
 const q=new URLSearchParams({host:session.host,port:String(session.port)});
 return '/api/lan/lobby?'+q.toString();
}
function se148DrawRoom(game){
 const pane=se148Room.screen,session=se148Room.session;
 if(!pane||!session)return;
 if(game.id!==session.gameId){se148Say('Lobby changed or closed. Return to Local LAN.');return;}
 pane.querySelector('#se148RoomTitle').textContent=game.name||'Sheep Tag';
 pane.querySelector('#se148RoomCount').textContent=game.players+' / '+game.capacity+' players';
 const list=pane.querySelector('#se148Slots');list.replaceChildren();
 for(const member of game.slots||[]){
  const row=document.createElement('div');row.className='se148-slot '+(member.role==='host'?'se148-host':'');
  const index=document.createElement('span');index.className='se148-number';index.textContent=String(member.seat).padStart(2,'0');
  const name=document.createElement('b');name.textContent=member.occupied?member.name:'Open slot';
  const role=document.createElement('small');role.textContent=member.role==='host'?'HOST':member.occupied?'JOINED':'WAITING';
  row.append(index,name,role);list.appendChild(row);
 }
 pane.querySelector('#se148Authority').textContent=session.owner?
  'You are the host. Only this hosting device can close the lobby or eventually start a synchronized match.':
  'Host controls the match. Waiting for the host and other players.';
 const start=pane.querySelector('#se148Start');
 start.hidden=!session.owner;
 start.disabled=true; // No playable netcode yet: never falsely launch local match.
 start.textContent='Start Match · networking pending';
 se148Say('Waiting room active on local Wi-Fi. Actual synchronized gameplay is not implemented yet.');
}
async function se148Refresh(){
 const session=se148Room.session;if(!session||se148Room.busy)return;
 se148Room.busy=true;
 try{
  if(!session.owner){
   await se148Post('/api/lan/pulse',{host:session.host,port:session.port,
      gameId:session.gameId,playerId:session.playerId});
  }
  const response=await se146Fetch(se148RoomParams(session));
  if(se148Room.session===session)se148DrawRoom(response.game);
 }catch(e){
  if(se148Room.session===session)se148Say('Unable to reach the waiting lobby: '+e.message);
 }finally{se148Room.busy=false;}
}
function se148OpenRoom(session,game){
 if(!se146Lan.active||!se146Lan.root)return;
 se148Room.session=session;
 if(se148Room.timer)clearInterval(se148Room.timer);
 se148Room.screen.hidden=false;
 se148Room.screen.classList.add('se148-room-open');
 se146Lan.root.hidden=true;
 if(game)se148DrawRoom(game);
 se148Refresh();
 se148Room.timer=setInterval(se148Refresh,4000);
}
async function se148LeaveRoom(){
 const session=se148Room.session;
 if(session){
  try{
   if(session.owner)await se146Fetch('/api/lan/host',{method:'DELETE'});
   else await se148Post('/api/lan/leave',{host:session.host,port:session.port,
      gameId:session.gameId,playerId:session.playerId});
  }catch(e){se148Say('Cannot leave lobby: '+e.message);return;}
 }
 se148ClearRoom();
 if(se146Lan.active){se146Lan.root.hidden=false;se146Scan(true);}
}
function se148ClearRoom(){
 if(se148Room.timer){clearInterval(se148Room.timer);se148Room.timer=null;}
 se148Room.session=null;se148Room.busy=false;
 if(se148Room.screen){se148Room.screen.hidden=true;se148Room.screen.classList.remove('se148-room-open');}
}
function se148InstallRoom(){
 const overlay=se146Lan.root?.parentElement;if(!overlay)return;
 let pane=overlay.querySelector('#se148WaitingRoom');
 if(pane) pane.remove();
 pane=document.createElement('section');
 pane.id='se148WaitingRoom';pane.className='se148-room';
 pane.setAttribute('aria-label','Sheep Tag local LAN waiting lobby');
 pane.hidden=true;
 pane.innerHTML='<div class="se148-kicker">SHEEP TAG · LOCAL LAN</div>'+
  '<h2 id="se148RoomTitle">Waiting lobby</h2>'+
  '<p id="se148RoomCount"></p>'+
  '<div id="se148Slots" class="se148-slots" aria-live="polite"></div>'+
  '<p id="se148Authority"></p>'+
  '<button type="button" id="se148Start" disabled>Start Match · networking pending</button>'+
  '<p id="se148Notice" role="status"></p>'+
  '<button type="button" id="se148Leave">Back to LAN browser</button>';
 pane.querySelector('#se148Leave').onclick=se148LeaveRoom;
 overlay.appendChild(pane);se148Room.screen=pane;
}
const se148PreviousInstall=se146Install;
se146Install=function(...args){
 se148ClearRoom();
 const result=se148PreviousInstall(...args);
 se148InstallRoom();
 return result;
};
const se148PreviousLeave=se146Leave;
se146Leave=function(...args){se148ClearRoom();return se148PreviousLeave(...args);};
// The original menu button now transitions directly into the waiting room.
se146Host=async function(){
 if(!se146Lan.active||!se146Lan.bridge||!se146Lan.canHost)return;
 try{
  const name=String(currentProject?.name||'Sheep Tag').slice(0,60);
  const response=await se148Post('/api/lan/host',{name});
  const game=response.game;
  se146Lan.hosting=true;
  se148OpenRoom({owner:true,host:game.host,port:game.port,gameId:game.id},game);
 }catch(e){se146Message('Cannot host: '+e.message);}
};
se146Join=async function(game){
 if(!se146Lan.active||!se146Lan.bridge)return;
 try{
  const name=String(se146Lan.root.querySelector('#se148PlayerName')?.value||'').trim().slice(0,32);
  const response=await se148Post('/api/lan/join',{host:game.host,port:game.port,gameId:game.id,name});
  if(!response.joined||!response.playerId)throw new Error('No verified player seat assigned');
  se148OpenRoom({owner:false,host:response.host,port:response.port,
    gameId:response.gameId,playerId:response.playerId});
 }catch(e){se146Message('Cannot join: '+e.message);}
};
const se148PreviousBrowserInstall=se146Install;
se146Install=function(...args){
 const result=se148PreviousBrowserInstall(...args);
 const input=document.createElement('input');
 input.id='se148PlayerName';input.type='text';input.maxLength=32;
 input.placeholder='Player name (optional)';input.autocomplete='off';
 input.setAttribute('aria-label','Name to show when joining a LAN game');
 const listHead=se146Lan.root?.querySelector('.se146-list-head');
 if(listHead)listHead.parentElement.insertBefore(input,listHead);
 return result;
};
window.SWYRL_ENGINE_LAN.room=()=>se148Room.session?
 {owner:se148Room.session.owner,gameId:se148Room.session.gameId,waiting:true}:null;
