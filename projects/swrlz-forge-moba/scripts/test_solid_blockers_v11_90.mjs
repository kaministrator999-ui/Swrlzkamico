import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';
const html=fs.readFileSync(process.env.SWYRL_TEST_HTML||'/workspace/passages-release/index.html','utf8'),r=new URL('../',import.meta.url);
const game=html.slice(html.indexOf('// Match state and helpers are transient.'),html.indexOf('// Player-proposed Archive experiments'));
const rules={...JSON.parse(fs.readFileSync(new URL('scenes/sheep-tag-seven-minute-v11-85.swyrl.json',r))).project.sheepTag,bounds:160,sheepRadius:.27,wolfRadius:.9,sheepSpeed:6,headstart:30,fogMode:'team'};
const c=vm.createContext({THREE,console,stUi:{shown:true},matchMedia:()=>({matches:true}),$:()=>({style:{},classList:{remove(){},add(){}}}),window:{SWYRL_ENGINE_SHEEP_TAG:{}},scene:new THREE.Scene(),actors:[],paused:false,terrainHeight:()=>0,walkingObjectVisible:a=>a.visible,currentProject:{sheepTag:rules},stRules:()=>rules,stCleanRules:v=>({...rules,...v}),stMakeVisual:()=>new THREE.Group(),stAuthoredMapPreflight:()=>({errors:[]}),stAnimateSpirit:()=>{},stMakeSpirit:()=>new THREE.Group()});
vm.runInContext(game,c);for(const name of ['sheep_lanes.js','sheep_clarity_v11_81.js'])vm.runInContext(fs.readFileSync(new URL('runtime/'+name,r),'utf8').replace('const ST_LANE_GAP = .6;','const ST_LANE_GAP = .75;'),c);
let mobile=fs.readFileSync(new URL('runtime/sheep_touch_controls_v11_82.js',r),'utf8');mobile=mobile.slice(0,mobile.indexOf('function stMobileIcon(')).replace('radius=stUnitRadius(unit);let target=null;','radius=stUnitRadius(unit);let target=stHouseSlideTarget(unit,direction,context,radius);').replace('for(const distance of [1.2,.6,.3,.12]){','if(!target)for(const distance of [1.2,.6,.3,.12]){');mobile=mobile.replace('unit.destination.copy(target);','unit.destination.copy(target);unit.path=[];unit.pathVersion=-1;unit.repathAt=0;');vm.runInContext(mobile,c);vm.runInContext(fs.readFileSync(new URL('runtime/sheep_house_slide_v11_86.js',r),'utf8'),c);
vm.runInContext(fs.readFileSync(new URL('runtime/sheep_passage_controls_v11_88.js',r),'utf8'),c);
vm.runInContext('var stRunBegin=()=>{};const stRunState={active:null};',c);vm.runInContext(fs.readFileSync(new URL('runtime/sheep_solid_blockers_v11_90.js',r),'utf8'),c);
vm.runInContext(`
const rules=stCleanRules({}),make=(id,kind,x,z)=>({id,name:id,kind,actor:new THREE.Group(),pos:new THREE.Vector3(x,0,z),home:new THREE.Vector3(x,0,z),memory:new Map(),velocity:new THREE.Vector3(),captured:false,botIndex:0,phase:0,path:[],pathVersion:-1,repathAt:0,speed:6});
const sheep=make('player','sheep',40,0);
stSession={rules,units:[sheep],buildings:[],obstacles:[],resources:{player:500},shops:[],pen:{x:0,z:0,halfX:5,halfZ:5,reserveX:7,reserveZ:7},elapsed:40,controlledId:'player',selectedId:'player',role:'sheep',navigation:new Map(),navVersion:0,viewMemory:new Map(),archive:{scentClues:[]},attacks:[],duration:420};
function house(x,z,rotation=0){return {kind:'st-farm',pos:new THREE.Vector3(x,0,z),...stFootprint(x,z,1.2,1.2,rotation,'house'+x+','+z),hp:200,progress:1};}
function reset(x,z,buildings,direction=[1,0]){stMobileReset();sheep.kind='sheep';sheep.pos.set(x,0,z);sheep.captured=false;sheep.archiveOnUpper=false;sheep.archiveRoute=null;sheep.traffic=null;stSession.units=[sheep];stSession.buildings=buildings;stSession.obstacles=[];stSession.elapsed=40;stInvalidateNavigation();stSetOrder(sheep,null);Object.assign(stMobile,{pointer:1,session:stSession,unit:sheep,captured:false,x:direction[0],y:direction[1],strength:1});}
function ticks(n){for(let i=0;i<n;i++){const before=sheep.pos.clone();stSession.elapsed+=.05;stUpdateSheep(sheep,.05);if(!stSegmentClear({rules,obstacles:stObstacles()},before,sheep.pos,.27))throw Error('Sheep crossed a house');if(stLanesOccupant(sheep,sheep.pos.x,sheep.pos.z))throw Error('Sheep crossed another unit');}return sheep.pos.toArray();}
globalThis.cases={};
for(const z of [-.65,.65,0]){reset(40,z,[house(43,0)]);ticks(16);cases['nearest'+z]={early:sheep.pos.toArray()};ticks(45);cases['nearest'+z].end=sheep.pos.toArray();}
reset(40,.65,[house(43,0)]);ticks(16);stMobileReset('release');const released=sheep.pos.clone();ticks(5);cases.releaseStops=sheep.pos.distanceTo(released)<1e-9;
reset(40,.65,[house(43,0)]);ticks(16);stMobile.x=-1;ticks(10);cases.reverse=sheep.pos.toArray();
const angle=Math.PI/4,c=Math.cos(angle),sn=Math.sin(angle);reset(43-3*c+.65*sn,3*sn+.65*c,[house(43,0,angle)],[c,-sn]);ticks(61);cases.rotated=stLocalPoint(sheep.pos.x,sheep.pos.z,stSession.buildings[0]);
reset(40,.65,[house(43,0)]);stSession.obstacles=[stFootprint(41.5,1.5,.4,.15,0,'fence')];stInvalidateNavigation();ticks(16);cases.blockedNearest=sheep.pos.toArray();
reset(40,0,[house(43,0)]);stSession.obstacles=[stFootprint(41.5,1.5,.4,.15,0,'north'),stFootprint(41.5,-1.5,.4,.15,0,'south')];stInvalidateNavigation();ticks(40);cases.bothBlocked=sheep.pos.toArray();
reset(40,.65,[house(43,0)]);stSession.units.push(make('traffic','sheep',41.1,1.25));ticks(16);cases.traffic=sheep.pos.toArray();
reset(40,0,[house(43,-1.5),house(43,1.5)]);ticks(40);cases.gap=sheep.pos.toArray();
for(const gap of [.6,.75])for(const offset of [-.28,.28])for(const sign of [-1,1]){
 const rows=[];for(const x of [43,45.4,47.8])for(const side of [-1,1])rows.push(house(x,side*(1.2+gap/2)));
 reset(sign>0?40:51,offset,rows,[sign,0]);ticks(65);cases['corridor'+gap+','+offset+','+sign]=sheep.pos.toArray();
}
for(const sign of [-1,1]){const rows=[];for(const x of [43,45.4,47.8])for(const side of [-1,1])rows.push(house(x,side*1.5));reset(45.4,.02,rows,[sign,0]);ticks(30);cases['inside'+sign]=sheep.pos.toArray();}
for(const offset of [-.28,.28]){const rows=[];for(const z of [43,45.4,47.8])for(const side of [-1,1])rows.push(house(side*1.575,z));reset(offset,40,rows,[0,1]);ticks(45);cases['vertical'+offset]=sheep.pos.toArray();}
reset(40,0,[house(43,0)]);cases.snap=stLanesSnapHouse('st-farm',46.0,0);
reset(40,.65,[house(43,0)]);sheep.kind='wolf';stSession.role='wolf';ticks(40);cases.wolf=sheep.pos.toArray();
`,c);
vm.runInContext(`reset(41.52,0,[house(43,0)]);stMobileReset();const idle=sheep.pos.clone();ticks(20);cases.idleStops=sheep.pos.distanceTo(idle)<1e-9;reset(40,0,[house(43,0)]);ticks(4);cases.approach=sheep.pos.toArray();`,c);
const t=JSON.parse(JSON.stringify(c.cases));console.log(JSON.stringify(t,null,2));assert.equal(t.idleStops,true);assert.equal(t.releaseStops,true);assert.ok(t.approach[0]>41&&Math.abs(t.approach[2])<1e-8);for(const z of [-.65,.65,0])assert.ok(t['nearest'+z].end[0]>46,'detour '+z);assert.ok(t.reverse[0]<42);assert.ok(t.rotated[0]>3);assert.ok(t.gap[0]>48&&Math.abs(t.gap[2])<1e-8);for(const [k,p] of Object.entries(t))if(k.startsWith('corridor'))assert.ok(k.endsWith(',1')?p[0]>49:p[0]<42,k+JSON.stringify(p));assert.ok(t['inside1'][0]>50&&t['inside-1'][0]<41);assert.ok(t['vertical-0.28'][2]>49&&t['vertical0.28'][2]>49);console.log('SOLID_BLOCKERS_CONTACT_THEN_ROUTE_NO_IDLE_PUSH_RELEASE_ROTATION_NARROW_LANES_PASS');
vm.runInContext(`
const perfContext={rules,obstacles:Array.from({length:300},(_,i)=>stFootprint(50+(i%20)*4,-40+Math.floor(i/20)*4,1.2,1.2,i%3*.17,'perf'+i))};
const intersectBase=stIntersectsObstacle;let calls=0;stIntersectsObstacle=(...args)=>{calls++;return intersectBase(...args);};let oldCalls=0,newCalls=0;
for(let i=0;i<100;i++){const a=new THREE.Vector3(40,0,(i%20)-10),b=a.clone().add(new THREE.Vector3(.3,0,.1));calls=0;const old=stSolidSegmentBase(perfContext,a,b,.27);oldCalls+=calls;calls=0;const current=stSegmentClear(perfContext,a,b,.27);newCalls+=calls;if(old!==current)throw Error('Broad phase changed collision');}
for(let i=0;i<200;i++){const a=new THREE.Vector3(49+(i%31)*.45,0,-42+(i%47)*.42),b=a.clone().add(new THREE.Vector3(Math.sin(i)*3,0,Math.cos(i)*3));if(stSolidSegmentBase(perfContext,a,b,.27)!==stSegmentClear(perfContext,a,b,.27))throw Error('Broad phase changed rotated collision');}
stIntersectsObstacle=intersectBase;globalThis.performanceEvidence={oldCalls,newCalls,shortSegments:100,obstacles:300,matchingRandomSegments:200};`,c);
assert.ok(c.performanceEvidence.newCalls<c.performanceEvidence.oldCalls*.1);console.log('COLLISION_BROADPHASE_EQUIVALENCE_AND_WORK_REDUCTION',JSON.stringify(c.performanceEvidence));
vm.runInContext(`terrainHeight=()=>4;reset(40,0,[house(43,0)]);sheep.pos.y=4;ticks(60);globalThis.elevatedGround=sheep.pos.toArray();`,c);assert.ok(c.elevatedGround[0]>46&&c.elevatedGround[1]===4);console.log('CONTACT_ROUTE_ON_NONZERO_GROUND_HEIGHT_PASS');
