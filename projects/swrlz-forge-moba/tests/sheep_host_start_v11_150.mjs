import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
const src=fs.readFileSync('projects/swrlz-forge-moba/runtime/sheep_lan_match_start_v11_150.js','utf8');
const css=fs.readFileSync('projects/swrlz-forge-moba/runtime/sheep_lan_match_start_v11_150.css','utf8');
new vm.Script(src);assert(css.includes('#se150MatchStatus'));
function node(){return {children:[],disabled:true,hidden:false,textContent:'',appendChild(child){this.children.push(child);child.parentElement=this},remove(){this.removed=true;},querySelector(){return null}}}
const start=node(),pane={querySelector:id=>id==='#se148Start'?start:null},canvas={parentElement:node()};
let starts=0,closes=0,packets=[],errors=[];
const ctx={console:{...console,warn:x=>errors.push(x)},Date,
 window:{crypto:{randomUUID:()=> 'match-1'},SWYRL_ENGINE_LAN:{}},
 se149Peer:{mode:'host',roomId:'room-1',links:[],guest:null},
 se148Room:{screen:pane},
 se149PaintPeer(){start.disabled=true;return 'painted'},
 se149EnterRoom(){return true},se149JoinInvite(){},
 se149Close(){closes++},se149Message(){},se146Message(){},
 seLevels:{playingMenu:true,records:new Map([['game',{}]])},
 seLevelsCurrent(){return {role:'menu'}},
 seLevelsTransition(id,autoPlay){assert.equal(id,'game');assert.equal(autoPlay,true);
  // menu teardown invokes se149Close; v150 must retain the peer.
  ctx.se149Close();ctx.seLevels.playingMenu=false;ctx.playing=true;starts++;return true;},
 playing:false,simulating:false,stSession:null,
 stopSession(){ctx.playing=false;return true;},
 document:{createElement:()=>node(),querySelector:()=>canvas,body:node()},
 $:()=>canvas};
vm.createContext(ctx);vm.runInContext(src,ctx);
const ch={readyState:'open',send:x=>packets.push(JSON.parse(x))};
ctx.se149Peer.links=[{name:'Clover',channel:ch}];
ctx.se149PaintPeer();
assert.equal(start.disabled,false,'host start enabled only for real guest');
assert.equal(start.onclick,ctx.window.SWYRL_ENGINE_LAN.startMatch);
assert.equal(start.onclick(),true);
assert.equal(starts,1,'one native Gameplay transition');
assert.equal(closes,0,'menu must not sever RTC peer');
assert.equal(ctx.window.SWYRL_ENGINE_LAN.matchStatus().nativeGameplayActive,true);
assert.equal(packets[0].kind,'match-start');
assert.equal(packets[0].roomId,'room-1');
assert.equal(packets[0].matchId,'match-1');
assert.equal(start.onclick(),false,'prevent duplicate start');
ctx.stopSession();
assert.equal(closes,1,'stop closes peer');
assert.equal(ctx.window.SWYRL_ENGINE_LAN.matchStatus().active,false);
assert.equal(packets.at(-1).kind,'match-end');
// Guest accepts only a direct channel packet for this room, not arbitrary mismatched start.
ctx.se149Peer.mode='guest';ctx.se149Peer.roomId='room-2';
ctx.seLevels.playingMenu=true;ctx.playing=false;
vm.runInContext('se150PeerPacket(JSON.stringify({kind:"match-start",roomId:"bad",matchId:"hack",level:"game"}))',ctx);
assert.equal(starts,1,'wrong-room start rejected');
vm.runInContext('se150PeerPacket(JSON.stringify({kind:"match-start",roomId:"room-2",matchId:"new-match",level:"game"}))',ctx);
assert.equal(starts,2,'correct guest start transitions native Gameplay');
assert.equal(ctx.window.SWYRL_ENGINE_LAN.matchStatus().role,'guest');
ctx.stopSession();
console.log('SE150_HOST_START_AND_GUEST_RECEIVE_NATIVE_LEVEL_TRANSITION_RTC_PRESERVE_AND_STOP_PASS');
