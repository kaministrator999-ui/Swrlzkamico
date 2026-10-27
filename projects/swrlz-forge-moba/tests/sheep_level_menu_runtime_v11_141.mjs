import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const js=fs.readFileSync(root+'runtime/sheep_editable_levels_v11_141.js','utf8');
const menu=JSON.parse(fs.readFileSync(root+'scenes/sheep-tag-main-menu-v11-141.swyrl.json','utf8'));
const game=JSON.parse(fs.readFileSync(root+'scenes/sheep-tag-seven-minute-v11-85.swyrl.json','utf8'));
class V{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this;}
 copy(v){return this.set(v.x,v.y,v.z);}
 clone(){return new V(this.x,this.y,this.z);}
}
let data=null,realPlay=0,realStop=0;
const viewport={children:[],classList:{add(){},remove(){}},
 appendChild(x){x.parent=this;this.children.push(x);}};
const make=()=>{
 const button={onclick:null,click(){this.onclick?.();}};
 return {id:'',className:'',parent:null,style:{setProperty(){}},
 innerHTML:'',setAttribute(){},addEventListener(){},children:[],
 querySelector(s){return s==='#st141StartGame'?button:null;},
 querySelectorAll(){return [];},
 remove(){if(this.parent){this.parent.children=this.parent.children.filter(x=>x!==this);this.parent=null;}},
 button};
};
const ctx={console,window:{},structuredClone,Math,Number,Map,Set,Blob,
 ST141_CANONICAL_MENU:menu,ST_CANONICAL_PROJECT:game,
 currentProject:null,stSession:null,playing:false,simulating:false,actors:[],
 perspectiveCamera:{position:new V(0,15,10),up:new V(0,1,0),quaternion:{clone(){return {copy(){}}},copy(){}},fov:50,
 lookAt(){},updateMatrixWorld(){},updateProjectionMatrix(){}},
 orbit:{target:new V(),enabled:true,update(){}},
 setCameraView(){},initializeHistory(){},toast(){},editorLog(){},stFrameMap(){},
 st140MenuOpen(){throw Error('legacy autorun is forbidden')},st140MenuTick(){},
 stLoadStarter(){},projectData(){return structuredClone({...data,project:{...ctx.currentProject}});},
 loadProject(p){
  data=structuredClone(p);ctx.currentProject=structuredClone(p.project);
  ctx.actors=p.scene.actors.map(a=>({userData:{id:a.id,actorType:a.type},
   position:new V(...a.position),rotation:new V(...a.rotation),scale:new V(...a.scale),visible:true}));
 },
 beginPlay(){realPlay++;ctx.playing=true;ctx.stSession={started:true};return true;},
 beginSimulate(){return true;},
 stopSession(){realStop++;ctx.playing=false;ctx.stSession=null;return true;},
 document:{createElement:make},
 $(id){return id==='viewport'?viewport:null;}
};
vm.createContext(ctx);vm.runInContext(js,ctx);
const value=q=>vm.runInContext(q,ctx);
ctx.stLoadStarter();
const sheep=ctx.actors.find(x=>x.userData.actorType==='st-sheep');
const original=sheep.position.clone();
assert.equal(realPlay,0);
ctx.st140MenuTick(.2);
assert.deepEqual(sheep.position,original,'menu editor does not animate');
assert.equal(value('seLevelsPlayMenu()'),true);
assert.equal(realPlay,0,'menu Play is not a gameplay session');
assert.equal(viewport.children.length,1,'menu overlay created');
ctx.st140MenuTick(7);
assert.notEqual(sheep.position.x,original.x,'authored sheep animates only in menu Play');
assert.equal(ctx.stSession,null);
assert.equal(value('seLevels.playingMenu'),true);
viewport.children[0].button.click();
assert.equal(value('seLevels.playingMenu'),false);
assert.equal(viewport.children.length,0,'overlay removed on transition');
assert.equal(sheep.position.x,original.x,'authored scene transform restored');
assert.equal(value('seLevels.active'),'game');
assert.equal(realPlay,1,'real gameplay starts once through native Play');
assert.equal(ctx.stSession.started,true);
assert.equal(ctx.actors.length,196,'actual gameplay map was loaded');
assert.equal(value('seLevels.playCount'),1);
assert.equal(value('seLevels.stopCount'),1);
assert.equal(value('seLevelsTransition("menu",false)'),true);
assert.equal(value('seLevels.active'),'menu');
assert.equal(realStop,1,'real play stopped before a level transition');
assert.equal(ctx.stSession,null);
console.log('SE141_MENU_STATIC_IN_EDITOR_ANIMATES_ONLY_PLAY_START_GAME_TRANSITIONS_NATIVE_MATCH_PASS');
