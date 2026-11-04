// v11.268 focused Quest LAN menu: controller options and real room routing.
// No browser/GPU automation; these mocks prove the menu dispatch and do not
// claim a successful physical Quest/WebRTC end-to-end test.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const code=fs.readFileSync(path.join(__dirname,'../runtime/sheep_vr_lan_menu_v11_268.js'),'utf8');
let joins=0,hosts=0,started=0,probes=0,refreshes=0,guests=0;
const room='se151-'+'a'.repeat(32),input={value:''};
const overlay={};
const root={parentElement:overlay,
  querySelector(selector){if(selector==='#se149OfferIn')return input;return null;},
  querySelectorAll(){return [];}};
const ctx={
  window:{},performance:{now:()=>1000},Promise,
  renderer:{xr:{isPresenting:true}},location:{protocol:'https:'},
  navigator:{clipboard:{readText:()=>Promise.resolve(room),
    writeText:()=>Promise.resolve()}},
  se195:{mode:'menu',page:'main'},
  se195Menu:()=>true,
  se195Options:(mode,page)=>[['start','PLAY'],['cinema','CINEMA'],
    ['capturePage','CAPTURE'],['help','CONTROLS'],['editor','EDIT']],
  se195HandleAction:()=>false,
  se195MakeRadial:()=>{refreshes++;},
  se195Page(page){ctx.se195.page=page;},
  se193XRFrame:()=>undefined,se193XRCleanup:()=>undefined,
  se191XRHeadPose:()=>null,
  seLevels:{playingMenu:true,overlay},
  se146Lan:{active:false,root:null},
  se146Open(){ctx.se146Lan.active=true;ctx.se146Lan.root=root;return true;},
  se146Scan:()=>undefined,
  se148LeaveRoom:()=>Promise.resolve(),
  se149Peer:{mode:'',roomId:''},se151:{room:''},se150Match:{active:false},
  se150ReadyGuests:()=>Array.from({length:guests},(_,i)=>({name:'guest'+i})),
  se150HostStart:()=>{started++;return true;},
  se151HostGame:()=>{hosts++;ctx.se149Peer.mode='host';return Promise.resolve();},
  se151JoinGame:()=>{joins++;return Promise.resolve();},
  se151CloudInvite(raw){const id=String(raw||'').trim();if(!/^se151-[a-z0-9]{10,80}$/i.test(id))throw Error('Invalid invite');return id;},
  se149Close:()=>{ctx.se149Peer.mode='';},
  se159ExpireNoRender:()=>undefined,se159Probe:()=>{probes++;},
  se159:{connected:true,rooms:new Map([[room,{id:room,name:'Nearby hosted game',
    players:1,capacity:8,seen:Date.now()}]])},
  scene:{add(){},remove(){}},
  THREE:{}
};
vm.runInNewContext(code,ctx,{filename:'sheep_vr_lan_menu_v11_268.js'});
assert.equal(ctx.se195Options().find(x=>x[0]==='lanPage')[1],'LOCAL LAN');
assert.equal(ctx.se195HandleAction('lanPage'),true);
assert.equal(ctx.se195.page,'lan');
assert.equal(ctx.se146Lan.active,true);
assert.equal(ctx.se195Options().some(x=>x[0]==='lanHost'),true);
assert.equal(ctx.se195HandleAction('lanHost'),true);
assert.equal(hosts,1);
assert.equal(ctx.se195HandleAction('lanStart'),true);assert.equal(started,0);
guests=1;
assert.equal(ctx.se195HandleAction('lanStart'),true);assert.equal(started,1);
assert.equal(ctx.se195HandleAction('lanRooms'),true);
assert.equal(ctx.se195.page,'lanRooms');
assert.equal(ctx.se195Options().some(x=>x[0]==='lanJoin0'),true);
assert.equal(ctx.se195HandleAction('lanJoin0'),true);
assert.equal(input.value,room);assert.equal(joins,1);
assert.equal(ctx.se195HandleAction('back'),true);
assert.equal(ctx.se195.page,'lan');
assert.equal(ctx.se195HandleAction('back'),true);
assert.equal(ctx.se195.page,'main');
ctx.se195.mode='game';
assert.equal(ctx.se195Options().some(x=>x[0]==='lanPage'),false);
assert.equal(ctx.window.SWYRL_ENGINE_SHEEP_VR_LAN_268.diagnose().privateSubnetScan,false);
console.log('QUEST_LAN_268_MENU_ROUTING_OK',{hosts,joins,started,probes,refreshes});
