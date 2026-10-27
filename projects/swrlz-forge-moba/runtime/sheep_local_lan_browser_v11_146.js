// §E v11.146 — actual LAN game directory UI; NO fabricated hosts or browser subnet scans.
// Local HTTP companion implements discovery and lobby presence. Gameplay netcode is separate.
const se146Lan={root:null,button:null,active:false,bridge:false,hosting:false,canHost:false,poll:null,busy:false,scanSerial:0};
function se146Text(node,message){if(node)node.textContent=message;}
function se146Fetch(path,options={}){
 return fetch(path,{cache:'no-store',...options}).then(async response=>{
  if(!response.ok)throw new Error('LAN bridge returned '+response.status);
  const data=await response.json();if(data.protocol!=='swrlz-lan-v1')
   throw new Error('Not a §wyrlz LAN bridge');
  return data;
 });
}
function se146Host(){
 if(!se146Lan.active)return;
 if(!se146Lan.bridge){se146Message('Hosting needs the local LAN Bridge. Open §e using its local network address.');return;}
 const name=String(currentProject?.name||'Sheep Tag').slice(0,60);
 se146Fetch('/api/lan/host',{method:'POST',
  headers:{'Content-Type':'application/json'},body:JSON.stringify({name})})
  .then(()=>se146Scan(true)).catch(e=>se146Message(e.message));
}
function se146Message(msg){
 const target=se146Lan.root?.querySelector('#se146LanStatus');
 se146Text(target,msg);
}
function se146Draw(games){
 const list=se146Lan.root?.querySelector('#se146LanGames');
 if(!list)return;
 list.replaceChildren();
 if(!games.length){
  const empty=document.createElement('p');empty.className='se146-empty';
  empty.textContent='No LAN hosts found. Start a host on another device and refresh.';
  list.appendChild(empty);return;
 }
 for(const game of games){
  const card=document.createElement('div');card.className='se146-game';
  const info=document.createElement('div');info.className='se146-game-info';
  const title=document.createElement('b');title.textContent=game.name||'Sheep Tag lobby';
  const description=document.createElement('small');
  const owner=!!game.self&&se146Lan.canHost;
  description.textContent=game.host+':'+game.port+' · '+game.players+' player(s) · '+(owner?'This device':'LAN');
  info.append(title,description);
  const join=document.createElement('button');join.type='button';
  join.textContent=owner?'Your lobby':'Join Lobby';
  join.disabled=owner;
  join.onclick=()=>se146Join(game);
  card.append(info,join);list.append(card);
 }
}
async function se146Join(game){
 if(!se146Lan.active||!se146Lan.bridge)return;
 try{
  const result=await se146Fetch('/api/lan/join',{method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({host:game.host,port:game.port,gameId:game.id})});
  se146Message(result.message||'Connected to LAN lobby. Match synchronization is not available yet.');
 }catch(e){se146Message('Cannot join lobby: '+e.message);}
}
async function se146Scan(force=false){
 if(!se146Lan.active||se146Lan.busy)return;
 const serial=se146Lan.scanSerial;
 se146Lan.busy=true;
 const scan=se146Lan.root.querySelector('#se146LanRefresh');
 if(scan)scan.disabled=true;
 try{
  // A public HTTPS Space cannot scan private IP addresses; don't attempt
  // fetches against guessed LAN hosts, bypass browser permissions, or fake results.
  if(location.protocol!=='http:'){
   se146Lan.bridge=false;se146Lan.hosting=false;se146Draw([]);
   se146Message('LAN discovery requires the local §e LAN Bridge. Hosted HTTPS pages cannot scan or host on Wi-Fi.');
   se146Lan.root.querySelector('#se146LanHost').disabled=true;
   return;
  }
  const status=await se146Fetch('/api/lan/status');
  if(serial!==se146Lan.scanSerial||!se146Lan.active)return;
  se146Lan.bridge=true;se146Lan.canHost=!!status.canHost;
  se146Lan.hosting=!!status.game&&se146Lan.canHost;
  const button=se146Lan.root.querySelector('#se146LanHost');
  button.textContent=se146Lan.hosting?'■ Stop Hosting':se146Lan.canHost?'＋ Host Game':'Hosting requires your own device';
  button.disabled=!se146Lan.canHost;
  const directory=await se146Fetch('/api/lan/games'+(force?'?scan=1':''));
  if(serial!==se146Lan.scanSerial||!se146Lan.active)return;
  se146Draw(Array.isArray(directory.games)?directory.games:[]);
  se146Message('Scanning local Wi-Fi · '+directory.games.length+' lobby(s) found · gameplay networking not connected yet');
 }catch(error){
  if(serial!==se146Lan.scanSerial||!se146Lan.active)return;
  se146Lan.bridge=false;se146Lan.hosting=false;se146Draw([]);
  se146Message('Local Bridge unavailable. Start it and open its http://LAN-IP:8765 address.');
  const button=se146Lan.root.querySelector('#se146LanHost');
  button.disabled=true;
 }finally{se146Lan.busy=false;if(scan)scan.disabled=false;}
}
function se146Leave(){
 se146Lan.active=false;se146Lan.scanSerial++;
 if(se146Lan.poll){clearInterval(se146Lan.poll);se146Lan.poll=null;}
 se146Lan.root?.classList.remove('se146-lan-open');
 if(se146Lan.root)se146Lan.root.hidden=true;
 se146Lan.button?.classList.remove('se146-selected');
}
function se146Open(){
 const overlay=seLevels.overlay;
 if(!overlay||!seLevels.playingMenu)return false;
 if(se146Lan.root?.parentElement!==overlay)se146Install(overlay);
 se146Lan.active=true;se146Lan.scanSerial++;
 se146Lan.root.hidden=false;
 se146Lan.root.classList.add('se146-lan-open');
 se146Lan.button?.classList.add('se146-selected');
 se146Scan(true);
 if(se146Lan.poll)clearInterval(se146Lan.poll);
 se146Lan.poll=setInterval(()=>se146Scan(false),3500);
 return true;
}
function se146Install(overlay){
 se146Leave();
 const menu=overlay.querySelector('.st141-menu-panel');
 if(!menu)return;
 const lanButton=document.createElement('button');
 lanButton.type='button';lanButton.id='se146LanOpen';lanButton.textContent='LOCAL LAN';
 lanButton.onclick=se146Open;
 menu.appendChild(lanButton);
 const pane=document.createElement('section');
 pane.id='se146LanScreen';pane.className='se146-screen';
 pane.setAttribute('aria-label','Local network Sheep Tag games');
 pane.hidden=true;
 pane.innerHTML='<div class="se146-title">LOCAL LAN</div>'+
  '<button type="button" id="se146LanHost" disabled>＋ Host Game</button>'+
  '<div class="se146-list-head"><b>Available LAN Games</b>'+
  '<button type="button" id="se146LanRefresh">↻ Refresh</button></div>'+
  '<div id="se146LanGames" class="se146-list" aria-live="polite"></div>'+
  '<p id="se146LanStatus" class="se146-status" role="status"></p>'+
  '<button type="button" id="se146LanBack">← Back</button>';
 pane.querySelector('#se146LanBack').onclick=se146Leave;
 pane.querySelector('#se146LanRefresh').onclick=()=>se146Scan(true);
 pane.querySelector('#se146LanHost').onclick=async()=>{
  if(se146Lan.hosting){
   try{await se146Fetch('/api/lan/host',{method:'DELETE'});await se146Scan(true);}
   catch(e){se146Message(e.message);}
  }else se146Host();
 };
 overlay.appendChild(pane);se146Lan.root=pane;se146Lan.button=lanButton;
}
const se146PlayBase=seLevelsPlayMenu;
seLevelsPlayMenu=function(...args){
 const result=se146PlayBase(...args);
 if(result&&seLevels.overlay)se146Install(seLevels.overlay);
 return result;
};
const se146StopBase=seLevelsStopMenu;
seLevelsStopMenu=function(...args){se146Leave();return se146StopBase(...args);};
window.SWYRL_ENGINE_LAN={open:se146Open,back:se146Leave,
 status:()=>({screen:se146Lan.active,bridge:se146Lan.bridge,hosting:se146Lan.hosting})};
