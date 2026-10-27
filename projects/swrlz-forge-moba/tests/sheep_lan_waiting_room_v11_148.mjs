import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const js=fs.readFileSync(root+'runtime/sheep_lan_waiting_room_v11_148.js','utf8');
const css=fs.readFileSync(root+'runtime/sheep_lan_waiting_room_v11_148.css','utf8');
new vm.Script(js);
for(const key of ['se148OpenRoom','se148DrawRoom','se148LeaveRoom','se148Refresh',
 'se148RoomTitle','se148Slots','se148RoomCount','se148Start','se148PlayerName',
 '/api/lan/host','/api/lan/join','/api/lan/leave','/api/lan/pulse','/api/lan/lobby'])
 assert(js.includes(key),key);
assert(js.includes('start.disabled=true'), 'no premature networked game launch');
assert(js.includes("session.owner"),'host role must be explicit');
assert(css.includes('.se148-host'),'host seat must have visual distinction');
const rows=[];
function node(tag){
 const n={tag,children:[],textContent:'',className:'',append(...children){this.children.push(...children)},
  replaceChildren(){this.children=[]}};
 rows.push(n);return n;
}
const pane={refs:{},querySelector(selector){return this.refs[selector]}};
for(const id of ['#se148RoomTitle','#se148RoomCount','#se148Slots','#se148Authority',
 '#se148Start','#se148Notice'])pane.refs[id]=node('div');
const ctx={se146Fetch:async()=>{},se146Install(){},se146Leave(){},se146Host(){},
 se146Join(){},se146Lan:{active:true,root:{parentElement:{}}},document:{createElement:node},
 window:{SWYRL_ENGINE_LAN:{}},setInterval(){return 1},clearInterval(){},
 se146Scan(){},currentProject:{name:'Sheep Tag'},console,URLSearchParams};
vm.createContext(ctx);vm.runInContext(js,ctx);
const room=vm.runInContext('se148Room',ctx);room.screen=pane;room.session={owner:true,host:'192.168.1.2',port:8765,gameId:'g'};
ctx.se148DrawRoom({id:'g',name:'Moonbell',players:2,capacity:8,
 slots:[{seat:1,name:'Host',role:'host',occupied:true},
        {seat:2,name:'Clover',role:'guest',occupied:true},
        ...Array.from({length:6},(_,i)=>({seat:i+3,name:'',role:'open',occupied:false}))]});
assert.equal(pane.refs['#se148Slots'].children.length,8);
assert.equal(pane.refs['#se148RoomCount'].textContent,'2 / 8 players');
assert.equal(pane.refs['#se148Start'].disabled,true);
assert.equal(pane.refs['#se148Slots'].children[0].children[2].textContent,'HOST');
assert.equal(pane.refs['#se148Slots'].children[1].children[1].textContent,'Clover');
console.log('SE148_REAL_LOBBY_EIGHT_SLOTS_HOST_AUTHORITY_AND_NO_FAKE_MATCH_PASS');
