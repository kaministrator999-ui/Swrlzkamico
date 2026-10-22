import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const html=fs.readFileSync(process.env.SWYRL_TEST_HTML||'/workspace/sheep-clarity-candidate/index.html','utf8');
const game=html.slice(html.indexOf('// Match state and helpers are transient.'),html.indexOf('// Player-proposed Archive experiments'));
assert.ok(game.includes('function stUpdateCapturedWisp')&&game.includes('function stVastFindPath'));
const context=vm.createContext({THREE,console,scene:new THREE.Scene(),actors:[],paused:false,terrainHeight:()=>0,walkingObjectVisible:a=>a.visible,
 stMakeSpirit:()=>new THREE.Group(),stAnimateSpirit:()=>{},stRules:()=>({bounds:128}),currentProject:{sheepTag:{bounds:128}}});
vm.runInContext('function stHuntReleased(s=stSession){return !!s&&s.elapsed>=s.rules.headstart;}',context);vm.runInContext("const ST_LANE_HOUSES=new Set(['st-farm','st-income','st-fort','st-totem']);"+html.slice(html.indexOf('function stClarityPortalRoute('),html.indexOf('const stClarityPathBase=stPath;')),context);vm.runInContext(game,context);
vm.runInContext(`
 const victim={id:'victim',kind:'sheep',name:'Captured sheep',actor:new THREE.Group(),pos:new THREE.Vector3(),phase:0,captured:false,archiveOnUpper:true,archiveHeight:3.3};
 const ally={id:'ally',kind:'sheep',name:'Living rescuer',actor:new THREE.Group(),pos:new THREE.Vector3(30,0,30),phase:0,captured:false};
 stSession={rules:{bounds:128,fogMode:'off',rescueHold:.6,rescueProtection:3},units:[victim,ally],buildings:[],obstacles:[],resources:{},pen:{x:0,z:0,halfX:5,halfZ:5},elapsed:2,controlledId:'victim',selectedId:'victim',navigation:new Map(),navVersion:0};
 stCapture(victim);globalThis.receipt={home:victim.spirit.position.toArray(),speed:ST_WISP_MOTION.speed,formerUpperCleared:!victim.archiveOnUpper&&victim.archiveHeight===undefined};
 globalThis.result=stCommand('move',{x:100,z:0});
 stUpdateSheep(victim,.05);globalThis.firstStep=victim.spirit.position.clone().sub(victim.spiritHome).length();
`,context);
assert.equal(context.result.ok,true);assert.equal(context.receipt.formerUpperCleared,true);assert.ok(Math.abs(context.firstStep-.0175)<1e-8);
vm.runInContext(`
 // After ten seconds the wisp has actually crossed the old pen boundary.
 for(let i=1;i<200;i++){stSession.elapsed+=.05;stUpdateSheep(victim,.05);}
 globalThis.outside={x:victim.spirit.position.x,captured:victim.captured,returns:victim.wispReturns};
 for(let i=0;i<200&&victim.wispReturns===0;i++){stSession.elapsed+=.05;stUpdateSheep(victim,.05);}
 globalThis.returned={position:victim.spirit.position.toArray(),captured:victim.captured,returns:victim.wispReturns,order:victim.spiritOrder};
`,context);
assert.ok(context.outside.x>5&&context.outside.x<=7.5);assert.equal(context.outside.returns,0);assert.equal(context.outside.captured,true);
assert.equal(context.returned.captured,true);assert.equal(context.returned.returns,1);assert.equal(context.returned.order,null);assert.deepEqual(Array.from(context.returned.position),Array.from(context.receipt.home));
for(const [x,z] of [[-100,0],[0,100],[0,-100]]){
 context.target={x,z};vm.runInContext(`{stCommand('move',target);const before=victim.wispReturns;for(let i=0;i<1000&&victim.wispReturns===before;i++){stSession.elapsed+=.05;stUpdateSheep(victim,.05);}globalThis.axisReturn=victim.wispReturns>before&&victim.spirit.position.distanceTo(victim.spiritHome)<1e-8;}`,context);assert.equal(context.axisReturn,true);
}
vm.runInContext(`
 globalThis.selfRescue=stRescue(victim,victim);
 globalThis.noBuild=stCommand('build',{kind:'st-farm',x:20,z:20});
 stCommand('move',{x:100,z:0});for(let i=0;i<210;i++){stSession.elapsed+=.05;stUpdateSheep(victim,.05);}
 ally.pos.copy(victim.spirit.position); // Arrange the rescue-range CPU fixture.
 for(let i=0;i<14;i++){stSession.elapsed+=.05;stUpdateSheep(ally,.05);}
 globalThis.revived={captured:victim.captured,spirit:victim.spirit,visible:victim.actor.visible,rescuer:victim.lastRescuerId,protection:victim.invulnerableUntil>stSession.elapsed};
`,context);
assert.equal(context.selfRescue,false);assert.equal(context.noBuild.ok,false);assert.equal(context.revived.captured,false);assert.equal(context.revived.spirit,null);assert.equal(context.revived.visible,true);assert.equal(context.revived.rescuer,'ally');assert.equal(context.revived.protection,true);
// Real native pathfinding keeps 0.15 m maze precision while bounding memory
// for local searches in a 256 m world. All segments must obey world collision.
vm.runInContext(`
 stSession.rules.bounds=128;stSession.obstacles=[{x:102,z:50,radius:4}];stInvalidateNavigation();
 const ctx={rules:stSession.rules,obstacles:stSession.obstacles},start=new THREE.Vector3(92,0,50),end=new THREE.Vector3(112,0,50);
 const route=stVastFindPath(ctx,start,end,.78);let previous=start,clear=!!route;
 for(const p of route||[]){clear=clear&&stSegmentClear(ctx,previous,p,.78);previous=p;}
 globalThis.navigation={clear,points:route?.length||0,cells:[...stSession.vastNavigation.values()].map(n=>n.count),grid:ST_GRID};
 stSession.obstacles=[{x:125,z:109,radius:2}];stInvalidateNavigation();
 const edge=stVastFindPath({rules:stSession.rules,obstacles:stSession.obstacles},new THREE.Vector3(125,0,100),new THREE.Vector3(125,0,118),.78);
 globalThis.edgeSafe=!!edge&&edge.every(p=>Math.abs(p.x)<=127.22&&Math.abs(p.z)<=127.22);
`,context);
assert.equal(context.navigation.clear,true);assert.ok(context.navigation.points>1);assert.equal(context.navigation.grid,.15);assert.ok(context.navigation.cells.every(n=>n<300000));assert.equal(context.edgeSafe,true);
vm.runInContext(`{
 stSession.obstacles=[stFootprint(98.5,50,1.2,1.2,0,'house-a'),stFootprint(101.5,50,1.2,1.2,0,'house-b')];stInvalidateNavigation();
 const ctx={rules:stSession.rules,obstacles:stSession.obstacles},a=new THREE.Vector3(100,0,45),b=new THREE.Vector3(100,0,55);
 const lengths=[.27,.78].map(radius=>{const path=stVastFindPath(ctx,a,b,radius);let previous=a,length=0;for(const p of path||[]){if(!stSegmentClear(ctx,previous,p,radius))throw Error('Maze path crosses a real obstacle');length+=previous.distanceTo(p);previous=p;}return path?length:Infinity;});globalThis.gaps=lengths;
 stSession.obstacles=[stFootprint(80,-85,3,1.2,Math.PI/4,'rotated-house')];stInvalidateNavigation();
 const rotated=stVastFindPath({rules:stSession.rules,obstacles:stSession.obstacles},new THREE.Vector3(70,0,-85),new THREE.Vector3(90,0,-85),.78);let previous=new THREE.Vector3(70,0,-85);
 globalThis.rotatedSafe=!!rotated;for(const p of rotated||[]){globalThis.rotatedSafe=globalThis.rotatedSafe&&stSegmentClear({rules:stSession.rules,obstacles:stSession.obstacles},previous,p,.78);previous=p;}
 stSession.obstacles=[];stInvalidateNavigation();stSession.pen={x:18,z:-13,halfX:7,halfZ:3};stCapture(victim);stCommand('move',{x:18,z:-100});const home=victim.spiritHome.clone();for(let i=0;i<1200&&!victim.wispReturns;i++){stSession.elapsed+=.05;stUpdateSheep(victim,.05);}globalThis.movedPenReturn=victim.wispReturns===1&&victim.spirit.position.distanceTo(home)<1e-8;
}`,context);
assert.ok(Math.abs(context.gaps[0]-10)<1e-6&&context.gaps[1]>11,'Fine house-gap species behavior changed: '+JSON.stringify(context.gaps));assert.equal(context.rotatedSafe,true);assert.equal(context.movedPenReturn,true);
console.log('VAST_WISP_CRAWL_LEAVE_RETURN_ALL_AXES_REVIVE_AND_FINE_LOCAL_NAV_PASS',JSON.stringify({speed:context.receipt.speed,firstStep:context.firstStep,outside:context.outside,navigation:context.navigation}));
