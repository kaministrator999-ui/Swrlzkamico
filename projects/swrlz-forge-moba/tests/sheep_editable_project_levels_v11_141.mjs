import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const js=fs.readFileSync(root+'runtime/sheep_editable_levels_v11_141.js','utf8');
const menu=JSON.parse(fs.readFileSync(root+'scenes/sheep-tag-main-menu-v11-141.swyrl.json','utf8'));
const gameplay=JSON.parse(fs.readFileSync(root+'scenes/sheep-tag-seven-minute-v11-85.swyrl.json','utf8'));
const html=process.env.SE_ASSEMBLED_HTML?fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8'):'';
if(html)for(const term of ['V11_142_EDITOR_STOP_MENU_AND_CHARACTER_GAIT','const ST141_CANONICAL_MENU=',
 'st140MenuTick=function(dt){seLevelsMenuTick(dt);}','project.levelPack'])
 assert.ok(html.includes(term),'assembled integration missing '+term);
assert.equal(menu.project.sheepTagLevel,'menu');
assert.equal(menu.scene.actors.filter(a=>a.type==='st-sheep').length,3);
assert.equal(menu.scene.actors.filter(a=>a.type==='st-wolf').length,1);
assert.equal(menu.scene.actors.filter(a=>a.type==='st-farm').length,4);
class V{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new V(this.x,this.y,this.z);}
 copy(a){this.x=a.x;this.y=a.y;this.z=a.z;return this;}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this;}
}
class A{
 constructor(data){this.userData={id:data.id,actorType:data.type,baked:true};this.position=new V(...data.position);
 this.rotation=new V(...data.rotation);this.scale=new V(...data.scale);this.visible=true;}
}
let sceneData=null,loadCalls=0,gameStarts=0,stops=0,menuStages=0;
const context={
 console,structuredClone,Math,Number,Map,Set,Blob,URL:{createObjectURL(){return 'blob:mock'},revokeObjectURL(){}},
 window:{},currentProject:null,playing:false,simulating:false,stSession:null,actors:[],
 st140MenuOpen(){throw Error('editor-time cinematic must never run');},
 st140MenuTick(){},
 stLoadStarter(){throw Error('old starter should be overridden');},
 ST141_CANONICAL_MENU:menu,ST_CANONICAL_PROJECT:gameplay,
 terrainHeight(){return 0;},stFrameMap(){},
 scene:{},camera:{},
 perspectiveCamera:{position:new V(0,32,24),up:new V(0,1,0),fov:50,
 quaternion:{clone(){return {copy(){}}},copy(){}},lookAt(){},updateMatrixWorld(){},updateProjectionMatrix(){}},
 orbit:{target:new V(),enabled:true,update(){}},
 setCameraView(){},initializeHistory(){},toast(){},editorLog(){},
 markSaved(){},
 projectData(){
  const data=structuredClone({...sceneData,project:{...context.currentProject}});
  data.scene.actors=data.scene.actors.map((a,i)=>{
   const live=context.actors.find(x=>x.userData.id===a.id);
   if(live){a.position=[live.position.x,live.position.y,live.position.z];
    a.rotation=[live.rotation.x,live.rotation.y,live.rotation.z];
    a.scale=[live.scale.x,live.scale.y,live.scale.z];}
   return a;
  });
  return data;
 },
 loadProject(d){loadCalls++;sceneData=structuredClone(d);context.currentProject=structuredClone(d.project);
 context.actors=d.scene.actors.map(x=>new A(x));return true;},
 beginPlay(){gameStarts++;context.playing=true;context.stSession={role:'sheep'};return true;},
 beginSimulate(){gameStarts++;context.simulating=true;return true;},
 stopSession(){stops++;context.playing=false;context.simulating=false;context.stSession=null;return true;},
 $(){return null;},document:{}
};
vm.createContext(context);vm.runInContext(js,context,{filename:'se-levels-141.js'});
const run=expr=>vm.runInContext(expr,context);
// Important: editor loads menu scene but must not start Play or animation.
context.stLoadStarter();
assert.equal(run('seLevels.active'),'menu');
assert.equal(context.playing,false);
assert.equal(gameStarts,0);
assert.equal(run('seLevels.playingMenu'),false);
assert.equal(context.currentProject.sheepTagLevel,'menu');
assert.equal(context.actors.length,13);
assert.equal(context.actors.filter(a=>a.userData.actorType==='st-farm').length,4);
// Save edits in the menu; next switching to gameplay must retain those edits.
context.actors[0].position.x=24;
context.currentProject.sheepTagMenu.title='The Sheep Will Rise';
assert.equal(run("seLevelsSwitch('game')"),true);
assert.equal(context.currentProject.sheepTagLevel,'game');
assert.equal(context.actors.length,196);
assert.equal(run("seLevelsSwitch('menu')"),true);
assert.equal(context.actors[0].position.x,24);
assert.equal(context.currentProject.sheepTagMenu.title,'The Sheep Will Rise');
// Add a separate editable map within the same project.
const id=run("seLevelsCreate('Bonus Meadow')");
assert.equal(id,'level-3');
assert.equal(context.currentProject.name,'Bonus Meadow');
assert.equal(context.actors.filter(a=>a.userData.actorType==='st-sheep').length,0);
assert.equal(context.actors.filter(a=>a.userData.actorType==='st-wolf').length,0);
assert.equal(context.actors.filter(a=>a.userData.actorType==='st-meadow').length,1);
assert.equal(run("seLevelsLink('game','level-3')"),true);
assert.equal(run("seLevelsLink('level-3','game')"),true);
assert.equal(run("seLevelsRename('level-3','Wolf Arena')"),true);
const exported=context.projectData();
assert.equal(exported.project.levelPack.schema,'se-levels-v1');
assert.equal(exported.project.levelPack.levels.length,3);
assert.equal(exported.project.levelPack.levels.find(l=>l.id==='menu').data.scene.actors[0].position[0],24);
assert.equal(exported.project.levelPack.levels.find(l=>l.id==='game').next,'level-3');
assert.ok(exported.project.levelPack.levels.every(l=>!l.data.project.levelPack),'no recursive serialization');
// A fresh load of the saved project must recover all three levels.
const copy=structuredClone(exported);
context.loadProject(copy);
assert.equal(run('seLevels.records.size'),3);
assert.equal(run('seLevels.active'),'level-3');
assert.equal(context.actors.filter(a=>a.userData.actorType==='st-wolf').length,0);
assert.equal(run("seLevelsSwitch('menu')"),true);
assert.equal(context.currentProject.sheepTagMenu.title,'The Sheep Will Rise');
// Another generic project can also create multiple separate maps.
const generic=structuredClone(menu);
generic.project={name:'Generic Animation Project',canonicalId:'general-editor-project',kind:'animation'};
generic.scene.actors=[generic.scene.actors[0]];
context.loadProject(generic);
assert.equal(run('seLevels.records.size'),1);
assert.equal(run("seLevelsCreate('Second Scene')"),'level-2');
assert.equal(run('seLevels.records.size'),2);
assert.equal(run("seLevelsLink('level-1','level-2')"),true);
assert.equal(context.projectData().project.levelPack.levels.length,2);
console.log('SE141_PROJECT_WIDE_LEVEL_BROWSER_SEPARATE_SCENES_NEW_MAP_LINK_BUNDLE_ROUNDTRIP_PASS');
