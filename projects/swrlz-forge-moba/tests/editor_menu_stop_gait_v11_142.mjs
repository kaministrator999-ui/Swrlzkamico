import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const ROOT='projects/swrlz-forge-moba/';
const code=fs.readFileSync(ROOT+'runtime/engine_playback_menu_gait_v11_142.js','utf8');
const css=fs.readFileSync(ROOT+'runtime/engine_playback_menu_gait_v11_142.css','utf8');
const html=process.env.SE_ASSEMBLED_HTML?fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8'):'';
if(html)for(const key of [
 'V11_142_EDITOR_STOP_MENU_AND_CHARACTER_GAIT',
 'se142SyncStop','se142MoveLevelBar','se142Gait',
 'id="se142-playback-menu-gait"'])assert.ok(html.includes(key),'assembled source missing '+key);
class V3{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new V3(this.x,this.y,this.z);}
 copy(a){return this.set(a.x,a.y,a.z);}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this;}
}
const classes=()=>({
 s:new Set(['hidden']),
 add(x){this.s.add(x);},remove(x){this.s.delete(x);},contains(x){return this.s.has(x);}
});
const toolbar={name:'toolbar'};
const viewport={name:'viewport',classList:classes(),children:[],appendChild(e){this.children.push(e);e.parentElement=this;}};
const stop={id:'stopBtn',parentElement:toolbar,classList:classes(),hidden:true,disabled:true,
 attrs:{},setAttribute(k,v){this.attrs[k]=v;},onclick:null};
const play={id:'playBtn',parentElement:toolbar,after(e){e.parentElement=toolbar;}};
const pause={id:'pauseBtn',parentElement:toolbar,after(e){e.parentElement=toolbar;e.placedAfter='pause';}};
const newButton={id:'se142PlayGame',onclick:null};
const bar={parentElement:toolbar,children:[],querySelector(sel){
 if(sel==='#se142PlayGame')return this.children.find(b=>b.id==='se142PlayGame')||null;
 if(sel==='#st141NewLevel')return {id:'st141NewLevel'};return null;
},insertBefore(b){this.children.push(b);}};
const rigs=[];
function unit(type,x){
 const leg=(i)=>({name:'stLeg'+i,rotation:new V3(.04,0,0)});
 const parts=[leg(0),leg(1),leg(2),leg(3),
  {name:'stHead',rotation:new V3(.1,0,0)},{name:'stTail',rotation:new V3(0,.08,0)}];
 const actor={userData:{actorType:type},position:new V3(x,0,0),parts,
  traverse(fn){parts.forEach(fn);}};
 rigs.push(actor);return actor;
}
const sheep=unit('st-sheep',0),wolf=unit('st-wolf',4);
const level={id:'menu',name:'Main Menu',role:'menu',data:{project:{canonicalId:'sheep-tag-menu-level',
 name:'Sheep Tag · Main Menu Level',kind:'sheep-tag',sheepTagLevel:'menu',
 sheepTagMenu:{title:'SHEEP TAG'}}}};
let started=0,stopped=0,syncs=0;
const startButton={hidden:true,disabled:true,style:{},getAttribute(){},onclick:null};
const overlay={hidden:true,style:{},querySelector(sel){return sel==='#st141StartGame'?startButton:null;}};
const c={
 console,Math,Number,structuredClone,Map,Set,window:{SWYRL_ENGINE_LEVELS:{status(){return {level:'menu'};}}},
 seLevels:{root:'sheep-tag-meadow',active:'menu',records:new Map([['menu',level]]),
   playingMenu:false,bar,overlay:null},
 currentProject:{kind:'sheep-tag',name:'Sheep Tag · Main Menu Level'}, // native loader dropped custom root
 playing:false,simulating:false,stSession:null,
 seLevelsCurrent(){return level;},
 seLevelsOwns(){return this.currentProject?.levelProjectRoot==='sheep-tag-meadow';},
 seLevelsSwitch(){return true;},
 stLoadStarter(){},
 loadProject(){},
 beginPlay(){return c.seLevelsOwns()?c.seLevelsPlayMenu():false;},
 stopSession(){return c.seLevelsStopMenu();},
 seLevelsEnsureUI(){},
 seLevelsRefresh(){},
 seLevelsMenuActors(type){return rigs.filter(x=>x.userData.actorType===type);},
 seLevelsMenuTick(dt){
  if(!c.seLevels.playingMenu)return;
  for(const a of rigs)a.position.x+=Number(dt)*5;
 },
 seLevelsPlayMenu(){
  if(!c.seLevelsOwns())return false;
  c.seLevels.playingMenu=true;c.seLevels.overlay=overlay;started++;return true;
 },
 seLevelsStopMenu(){
  if(!c.seLevels.playingMenu)return false;
  c.seLevels.playingMenu=false;c.seLevels.overlay=null;stopped++;return true;
 },
 setSessionButtons(){syncs++;},
 document:{createElement(type){
   assert.equal(type,'button');return {id:'',type:'',textContent:'',title:'',handlers:{},
    addEventListener(type,handler){this.handlers[type]=handler;}};
 }},
 $:id=>({playBtn:play,pauseBtn:pause,stopBtn:stop,viewport})[id]||null,
};
vm.createContext(c);
vm.runInContext(code,c,{filename:'st142.js'});
const run=x=>vm.runInContext(x,c);
// Menu detection is recovered even when the native loader discarded an
// unknown project root metadata field.
assert.equal(run('seLevelsOwns()'),true);
assert.equal(run('se142RestoreLevelMeta()'),true);
assert.equal(c.currentProject.levelProjectRoot,'sheep-tag-meadow');
// Level controls leave playback toolbar; Stop is directly beside Pause.
run('seLevelsEnsureUI()');
assert.equal(bar.parentElement,viewport);
assert.equal(stop.placedAfter,'pause');
assert.equal(bar.children.length,1,'explicit Play Game entry command installed');
assert.equal(stop.classList.contains('hidden'),false);
assert.equal(stop.disabled,true,'Stop is visible but inert while in Edit mode');
assert.equal(css.includes('#viewport > #st141LevelBar'),true);
// Playing menu must show Start Game and enable Stop.
assert.equal(run('beginPlay()'),true);
assert.equal(started,1);
assert.equal(startButton.hidden,false);
assert.equal(startButton.disabled,false);
assert.equal(startButton.style.pointerEvents,'auto');
assert.equal(stop.disabled,false);
assert.equal(stop.attrs['aria-label'],'Stop playback');
run('seLevelsMenuTick(.20)');
const legs=[...sheep.parts,...wolf.parts].filter(p=>p.name.startsWith('stLeg'));
assert.ok(legs.some(p=>Math.abs(p.rotation.x-.04)>.01),
 'articulated legs must actually move; actor translation alone is not animation');
assert.ok([...sheep.parts,...wolf.parts].some(p=>p.name==='stTail'&&Math.abs(p.rotation.y-.08)>.001));
// Stop should restore all rig changes, the editor and its control state.
assert.equal(run('stopSession()'),true);
assert.equal(stopped,1);
assert.equal(stop.disabled,true);
assert.ok(syncs>0,'Stop uses native session button refresh');
assert.ok(legs.every(p=>Math.abs(p.rotation.x-.04)<1e-8));
assert.equal(run('se142.rigs.size'),0);
assert.equal(c.seLevels.playingMenu,false);
assert.ok(css.includes('#st141RuntimeMenu #st141StartGame'));
console.log('SE142_STOP_NEXT_TO_PAUSE_MENU_START_VISIBLE_ARTICULATED_SHEEP_WOLF_AND_RIG_RESTORE_PASS');
