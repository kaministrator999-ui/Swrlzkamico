import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const script=fs.readFileSync('projects/swrlz-forge-moba/runtime/sheep_local_lan_browser_v11_146.js','utf8');
const css=fs.readFileSync('projects/swrlz-forge-moba/runtime/sheep_local_lan_browser_v11_146.css','utf8');
for(const required of ['se146LanOpen','se146LanHost','se146LanGames','se146LanBack','se146LanRefresh'])
 assert.ok(script.includes(required),required);
assert.ok(css.includes('.se146-lan-open'));

// Lightweight DOM contract for the dynamically authored Main Menu LAN view.
function node(tag='div'){
 const self={tag,hidden:false,disabled:false,children:[],parentElement:null,style:{},dataset:{},
  classList:{add(){},remove(){}},setAttribute(){},addEventListener(){},textContent:'',innerHTML:'',
  appendChild(child){child.parentElement=this;this.children.push(child);return child;},
  append(...a){a.forEach(x=>this.appendChild(x));},
  replaceChildren(...a){this.children=[];this.append(...a);},
  querySelector(sel){if(sel[0]==='#')return self.refs?.[sel.slice(1)]||null;
   if(sel==='.st141-menu-panel')return self.menu||null;return null;}
 };
 return self;
}
const menu=node(),overlay=node();overlay.menu=menu;
let requests=[],stops=0,hosting=false;
const doc={createElement:(tag)=>{
 const n=node(tag);
 if(tag==='section'){n.refs={};
  for(const id of ['se146LanBack','se146LanRefresh','se146LanHost','se146LanStatus','se146LanGames'])
   n.refs[id]=node('button');}
 return n;
}};
const status=()=>({protocol:'swrlz-lan-v1',available:true,canHost:true,
 game:hosting?{id:'host-1',name:'Sheep Tag QA'}:null});
const games=()=>({protocol:'swrlz-lan-v1',games:hosting?[{
 name:'Sheep Tag QA',host:'192.168.1.9',port:8765,id:'host-1',players:1,self:true}]:[]});
const ctx={document:doc,location:{protocol:'https:'},setInterval:()=>1,clearInterval(){},
 currentProject:{name:'Sheep Tag'},seLevels:{playingMenu:false,overlay:null},
 seLevelsPlayMenu(){ctx.seLevels.playingMenu=true;ctx.seLevels.overlay=overlay;return true;},
 seLevelsStopMenu(){ctx.seLevels.playingMenu=false;ctx.seLevels.overlay=null;return true;},
 fetch:async(path,options)=>{requests.push(path);
  const json=path.includes('status')?status():path.includes('/games')?games():
    options?.method==='POST'?(hosting=true,{protocol:'swrlz-lan-v1',game:{id:'host-1'}}):
    {protocol:'swrlz-lan-v1'};
  return {ok:true,json:async()=>json};},
 console,window:{}};
vm.createContext(ctx);vm.runInContext(script,ctx,{filename:'local-lan-menu.js'});
assert.equal(ctx.seLevelsPlayMenu(),true,'menu must still run normally');
const button=menu.children.find(x=>x.id==='se146LanOpen');
assert.ok(button,'visible Local LAN control must be installed');
const panel=overlay.children.find(x=>x.id==='se146LanScreen');
assert.ok(panel,'LAN browser must be a separate screen inside menu overlay');
assert.ok(panel.innerHTML.indexOf('Host Game')<panel.innerHTML.indexOf('Available LAN Games'));
assert.ok(panel.innerHTML.indexOf('Available LAN Games')<panel.innerHTML.indexOf('Back'));
// Emulate controls parsed from the browser DOM.
ctx.window.SWYRL_ENGINE_LAN.open();
await Promise.resolve();await Promise.resolve();
assert.ok(ctx.window.SWYRL_ENGINE_LAN.status().screen);
assert.ok(panel.refs.se146LanStatus.textContent.includes('HTTPS'));
assert.equal(panel.refs.se146LanHost.disabled,true,'host must not pretend to run on public HTTPS');
assert.equal(requests.length,0,'never probe LAN from HTTPS public site');
panel.refs.se146LanBack.onclick();
assert.equal(ctx.window.SWYRL_ENGINE_LAN.status().screen,false);
assert.equal(ctx.seLevels.playingMenu,true,'Back returns to original animated menu');
ctx.seLevelsStopMenu();
assert.equal(ctx.window.SWYRL_ENGINE_LAN.status().screen,false);
console.log('SE146_LAN_BUTTON_BROWSER_HOST_ABOVE_LIST_BACK_HTTPS_BOUNDARY_PASS');
