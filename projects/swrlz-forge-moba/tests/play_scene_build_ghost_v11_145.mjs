import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const js=fs.readFileSync(root+'runtime/engine_play_scene_build_ghost_v11_145.js','utf8');
const css=fs.readFileSync(root+'runtime/engine_play_scene_build_ghost_v11_145.css','utf8');
for(const text of ['body.se145-runtime .topbar','#se145ExitEditor','viewport-wrap'])assert.ok(css.includes(text));
let active=false,round=null,stop=0;
const classes=new Set(),children=[];
const host={appendChild(x){children.push(x);}};
const el={classList:{add(){}}};
const element=()=>({type:'',id:'',textContent:'',hidden:false,handlers:{},
 setAttribute(){},addEventListener(name,fn){this.handlers[name]=fn;}});
const originalCan=(kind,x,z)=>{
 let reason=null;
 for(const b of round?.buildings||[]){
  const a=Math.abs(x-b.pos.x)-2.4,c=Math.abs(z-b.pos.z)-2.4;
  if(a<-.03&&c<-.03)reason='A structure already occupies that space.';
  else if(a>.022&&c>.022&&Math.hypot(a,c)<1.185)reason='A diagonal crack is not a sheep passage. Join houses or leave 1.20 m.';
 }
 return {ok:!reason,reason,kind,x,z,halfX:1.2,halfZ:1.2,rotation:0};
};
const c={Math,Number,document:{body:{classList:{toggle(k,v){if(v)classes.add(k);else classes.delete(k);}}},createElement:element},
 se143ViewportHost:()=>host,
 seLevels:{playingMenu:false},stSession:null,stUi:{shown:true,build:'st-farm',preview:null},
 stBuildInput:{pointer:null,session:null,source:null},
 stTouchPlacement:{valid:false,reason:null},stPlacementGridState:{guide:null},
 st132Rapid:true,ST_LANE_HOUSES:new Set(['st-farm']),st139NativeCanBuild:originalCan,
 stUiText(){},$(id){return id==='stPlacement'?el:null;},
 seLevelsPlayMenu(){c.seLevels.playingMenu=true;return true;},
 seLevelsStopMenu(){c.seLevels.playingMenu=false;return true;},
 beginPlay(){round={simulate:false,buildings:[{kind:'st-farm',hp:100,pos:{x:0,z:0},halfX:1.2,halfZ:1.2,rotation:0}]};c.stSession=round;return true;},
 stopSession(){stop++;c.stSession=null;return true;},
 stRefreshHUD(){return true;},stTouchPlacementHide(reason){if(c.stUi.preview)c.stUi.preview.visible=false;c.stUi.placement=null;},
 stCanBuild:originalCan,stStop(){c.stSession=null;},stUiStatus(){return {base:true};},window:{},console};
vm.createContext(c);vm.runInContext(js,c);
assert.equal(c.seLevelsPlayMenu(),true);assert.ok(classes.has('se145-runtime'));assert.ok(classes.has('se145-menu'));
assert.equal(children.length,1);assert.equal(children[0].hidden,false);
c.seLevelsStopMenu();assert.ok(!classes.has('se145-runtime'));assert.equal(children[0].hidden,true);
c.beginPlay();assert.ok(classes.has('se145-game'));assert.equal(children[0].hidden,false);
children[0].handlers.click({preventDefault(){},stopPropagation(){}});
assert.equal(stop,1);assert.equal(children[0].hidden,true);
c.beginPlay();
c.stUi.preview={visible:true,traverse(fn){fn({material:{color:{set(v){c.tint=v;}},emissive:{set(){}}}});}};
c.stBuildInput={pointer:22,session:c.stSession,source:'meadow'};
c.stTouchPlacementHide('Aim on clear ground');
assert.equal(c.stUi.preview.visible,true,'invalid ray must not hide ghost while dragging');
assert.equal(c.stTouchPlacement.valid,false,'invalid drag cannot build');
assert.equal(c.tint,0xff7777,'invalid ghost must be visibly red');
c.stBuildInput.pointer=null;c.stTouchPlacementHide('stop');assert.equal(c.stUi.preview.visible,false);
c.stBuildInput.session=null;
const fit=c.stCanBuild('st-farm',3,3);
assert.equal(fit.ok,true,'nearby diagonal with legal flush alternative should snap');
assert.ok(fit.se145SafeSnap,'new magnet sourced from complete validator');
assert.ok(Math.hypot(fit.x-3,fit.z-3)<1.65,'not a distant ghost teleport');
assert.equal(c.stCanBuild('st-farm',2,2).ok,false,'occupied sites remain invalid');
c.st132Rapid=false;assert.equal(c.stCanBuild('st-farm',3,3).ok,false,'Rapid OFF must preserve original rejection');
const source=fs.readFileSync(root+'patches/v11_145_play_scene_build_ghost.py','utf8');
assert.ok(source.includes('stBuildInput.pointer===null'),'active drag HUD refresh must not stomp ghost');
console.log('SE145_EDITOR_PLAY_STATE_SAFE_SNAP_RED_PERSISTENT_GHOST_AND_RAPID_OFF_PASS');
