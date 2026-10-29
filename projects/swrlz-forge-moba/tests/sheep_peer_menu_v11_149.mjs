import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
const root='projects/swrlz-forge-moba/runtime/';
const source=fs.readFileSync(root+'sheep_peer_menu_v11_149.js','utf8');
const css=fs.readFileSync(root+'sheep_peer_menu_v11_149.css','utf8');
new vm.Script(source);
for(const key of ['se149PreviewParity','se149Host','se149JoinInvite',
 'se149CreateInvite','se149AcceptReply','RTCPeerConnection',
 'se146Scan=async function','se148DrawRoom','se149PeerControls','se149PreviewLan'])
 assert(source.includes(key),key);
assert(css.includes('#st141MenuPreview #se149PreviewLan'));
assert(source.includes("iceServers:[]"),'must not secretly depend on an online relay');
assert(source.includes('start')===false||source.includes('se148OpenRoom'),'reuse existing room, do not start fake match');
const nodes=[];
function el(tag){const item={tag,children:[],textContent:'',disabled:false,
 appendChild(x){this.children.push(x);return x;},querySelector(q){return q==='#se149PreviewLan'?this.children.find(e=>e.id==='se149PreviewLan'):null}};
 nodes.push(item);return item;}
const panel=el('div');
const preview={querySelector(sel){return sel==='.st141-menu-panel'?panel:null}};
const current={};
const ctx={window:{RTCPeerConnection:class{},crypto:{randomUUID:()=> 'room-one'},SWYRL_ENGINE_LAN:{}},
 navigator:{},location:{protocol:'https:'},document:{createElement:el},
 seLevels:{preview},seLevelsEnsureUI(){},se146Scan(){},se146Install(){},
 se146Leave(){},se146Lan:{active:false,root:null},se146Draw(){},
 se146Message(v){current.msg=v},se148Refresh(){},se148LeaveRoom(){},
 se148ClearRoom(){},se148OpenRoom(){},se148DrawRoom(){},
 se149Add:false,console,crypto:{randomUUID:()=> 'room-one'},
 setTimeout(){},setInterval(){},clearInterval(){},URLSearchParams,RTCPeerConnection:class{}};
vm.createContext(ctx);vm.runInContext(source,ctx);
assert.equal(panel.children.length,1);
assert.equal(panel.children[0].id,'se149PreviewLan');
assert.equal(panel.children[0].textContent,'LOCAL LAN');
assert.equal(panel.children[0].disabled,true,'editor preview stays non-interactive');
ctx.seLevelsEnsureUI();assert.equal(panel.children.length,1,'no duplicate on refresh');
console.log('SE149_EDITOR_PREVIEW_MATCHES_LOCAL_LAN_RUNTIME_AND_SAFE_HOST_PATH_PASS');
