// Emberfall native §E starter source and game-rule mock checks. No Chromium.
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const src=fs.readFileSync(path.join(__dirname,'../runtime/emberfall_arpg_v11_194.js'),'utf8');
const patch=fs.readFileSync(path.join(__dirname,'../patches/v11_194_emberfall_arpg_starter.py'),'utf8');
new vm.Script(src,{filename:'emberfall_arpg_v11_194.js'});
class V {
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z});}
 clone(){return new V(this.x,this.y,this.z);}
 set(x,y,z){Object.assign(this,{x,y,z});return this;}
 copy(v){return this.set(v.x,v.y,v.z);}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this;}
 setY(v){this.y=v;return this;}
 normalize(){const n=Math.hypot(this.x,this.y,this.z)||1;this.x/=n;this.y/=n;this.z/=n;return this;}
 distanceTo(v){return Math.hypot(this.x-v.x,this.y-v.y,this.z-v.z);}
 lerp(v,t){this.x+=(v.x-this.x)*t;this.y+=(v.y-this.y)*t;this.z+=(v.z-this.z)*t;return this;}
}
const events=[],actors=[],ctx={
 window:{addEventListener:()=>{}},document:{readyState:'loading',getElementById:()=>null},
 THREE:{Vector3:V,Plane:class{},Raycaster:class{}},
 actors,Math,Number,Array,Object,Set,Map,performance:{now:()=>0},
 currentProject:null,dirty:false,
 clearAll:()=>{actors.length=0;events.push('clear')},
 applyProjectMeta:meta=>{ctx.currentProject=meta},
 setProjectBackground:()=>{},rebuildTerrain:()=>{},makeGroundActor:()=>{},buildSceneryExtras:()=>{},
 makeHero:(team,p,baked,name)=>make('hero',p,name,team),
 makeRock:(p,scale,baked,name)=>make('rock',p,name),
 makeTree:(p,scale,baked,name)=>make('tree',p,name),
 makeWall:(p,scale,baked,name)=>make('wall',p,name),
 makeCrystal:(p,c,baked,name)=>make('crystal',p,name),
 makePortal:(p,c,baked,name)=>make('portal',p,name),
 finishTemplate:()=>events.push('finish'),
 initializeHistory:()=>events.push('history'),
 markSaved:()=>events.push('markSaved'),
 toast:t=>events.push(t),
 setCameraView:()=>{},
 perspectiveCamera:{position:new V(),lookAt:()=>{},updateProjectionMatrix:()=>{}},
 orbit:{target:new V(),enabled:true,update:()=>{}},
 terrainHeight:()=>0
};
function make(type,pos,name,team='blue'){
 const a={name,position:new V(pos[0],0,pos[2]),rotation:{y:0},userData:{actorType:type,id:'a'+actors.length},
 scale:{setScalar:()=>{}},visible:true,getWorldPosition:function(v){return v.copy(this.position)}};
 a.userData.team=team;actors.push(a);return a;
}
const sandbox=vm.createContext(ctx);
vm.runInContext(src,sandbox);
function evalIn(x){return vm.runInContext(x,sandbox);}
assert.equal(evalIn('ef194MakeStarter()'),true);
assert.equal(ctx.currentProject.kind,'emberfall-arpg');
assert.equal(ctx.currentProject.template,'emberfall-arpg');
assert.equal(actors.filter(a=>a.userData.role==='emberfall-player').length,1);
assert.equal(actors.filter(a=>a.userData.role==='emberfall-enemy').length,11);
assert.equal(actors.filter(a=>a.userData.role==='emberfall-boss').length,1);
assert(events.includes('markSaved'),'new starter should initialize native save history');
assert.equal(evalIn('ef194.session'),null,'starter creation does not start gameplay');
evalIn('ef194Vfx=function(){};ef194SpawnLoot=function(){};ef194RefreshHud=function(){}');
evalIn('ef194.session={hero:ef194Actor("emberfall-player"),monsters:[{actor:ef194Actor("emberfall-enemy"),id:"test",hp:40,maxHp:40,alive:true,boss:false}],dead:false,inventory:[],loot:[],level:1,xp:0,xpNeeded:30,skillPoints:0,skills:{slash:1,bolt:1,nova:1},hp:65,maxHp:100,mana:50,maxMana:50,potions:2,attackBonus:0,armor:0,gold:0,kills:0,cooldowns:{slash:0,bolt:0,nova:0,pet:0},look:new THREE.Vector3(),quest:"Test",time:0};ef194.session.monsters[0].actor.position.set(1,0,10);');
ctx.paused=false;
assert.equal(evalIn("ef194Cast('slash')"),true,'slash hits nearby enemies');
assert.equal(evalIn('ef194.session.monsters[0].hp'),22);
assert.equal(evalIn("ef194Cast('slash')"),false,'slash cooldown enforced');
evalIn('ef194.session.cooldowns.slash=0');
assert.equal(evalIn("ef194Cast('slash')"),true);
assert.equal(evalIn('ef194.session.monsters[0].hp'),4);
evalIn('ef194.session.cooldowns.slash=0');
assert.equal(evalIn("ef194Cast('slash')"),true);
assert.equal(evalIn('ef194.session.monsters[0].alive'),false);
assert.equal(evalIn('ef194.session.kills'),1);
assert.equal(evalIn('ef194.session.level'),1);
assert.equal(evalIn('ef194.session.xp'),18);
assert.equal(evalIn("ef194Potion()"),true);
assert.equal(evalIn('ef194.session.potions'),1);
assert(evalIn('ef194.session.hp')>65);
evalIn('ef194.session.xp=29;ef194.session.monsters=[{actor:ef194Actor("emberfall-boss"),hp:2,maxHp:2,alive:true,boss:true}]');
evalIn('ef194.session.monsters[0].actor.position.set(0,0,10)');
assert.equal(evalIn('ef194Damage(ef194.session.monsters[0],5)'),true);
assert.equal(evalIn('ef194.session.complete'),true);
assert(evalIn('ef194.session.level')>1);
assert(evalIn('ef194.session.skillPoints')>0);
assert.equal(evalIn("ef194SkillUp('nova')"),true);
assert.equal(evalIn('ef194.session.skills.nova'),2);
assert(!src.includes('setAnimationLoop('),'no second frame loop');
assert(!src.includes('requestAnimationFrame('),'no independent frame scheduler');
assert(!src.includes('fetch('),'no remote assets');
assert(patch.includes("if(currentProject.kind==='emberfall-arpg')ef194Update(dt);"));
console.log('PASS EMBERFALL V11.194 · starter actors, combat, skills, cooldowns, potions and boss');
