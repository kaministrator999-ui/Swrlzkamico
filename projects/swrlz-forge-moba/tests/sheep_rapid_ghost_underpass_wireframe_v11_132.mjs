import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {JSDOM}=require(process.env.SE_JSDOM_MODULE);
const THREE=require(process.env.SE_THREE_MODULE);
const root='projects/swrlz-forge-moba/';
const rapid=fs.readFileSync(root+'runtime/sheep_rapid_build_meadow_drag_v11_132.js','utf8');
const world=fs.readFileSync(root+'runtime/sheep_world_underpass_wireframe_v11_132.js','utf8');
const css=fs.readFileSync(root+'runtime/sheep_rapid_build_meadow_drag_v11_132.css','utf8');
const dom=new JSDOM('<div id="viewport"><canvas id="engine-canvas"></canvas></div><section id="sheepTagHUD"></section>',{url:'https://example.test/'});
const doc=dom.window.document,$=id=>doc.getElementById(id);
const me={id:'controlled',kind:'sheep',pos:new THREE.Vector3(0,0,-3),
 actor:new THREE.Group(),order:null,captured:false,walkBlend:0,archiveSplitAt:-Infinity};
me.actor.position.copy(me.pos);
me.actor.add(new THREE.Mesh(new THREE.BoxGeometry(1.2,1.2,1.2),new THREE.MeshStandardMaterial()));
const scene=new THREE.Scene();scene.add(me.actor);
const camera=new THREE.PerspectiveCamera(65,1,.1,100);camera.position.set(0,5,10);camera.lookAt(0,0,-3);camera.updateMatrixWorld(true);
const worldRoutes=[
 ['pinewatch',-52.5,-45],['moonflower',60,-52.5],['amberglade',-52.5,60]
].flatMap(([name,x,z])=>[['south-ramp',6],['center-deck',0],['north-ramp',-6]].map(([piece,dz])=>({
 id:'st-permanent-route-'+name+'-'+piece,position:[x,0,z+dz],rotation:[0,0,0],type:piece==='center-deck'?'st-wall':'st-ramp'
})));
const makeBuilding=(id,kind,center)=>({
 id,kind,pos:center,hp:100,progress:1,mesh:new THREE.Mesh(new THREE.BoxGeometry(3,3.3,2.4),new THREE.MeshBasicMaterial())
});
const deck=makeBuilding('st-permanent-route-pinewatch-center-deck','st-wall',new THREE.Vector3(-52.5,0,-45));
const ramp=makeBuilding('st-permanent-route-pinewatch-south-ramp','st-ramp',new THREE.Vector3(-52.5,0,-39));
const house=makeBuilding('house-player','st-farm',new THREE.Vector3(0,1,0));house.mesh.position.copy(house.pos);scene.add(house.mesh);
const house2=makeBuilding('house-normal','st-farm',new THREE.Vector3(8,1,-2));
const stSession={role:'sheep',controlledId:'controlled',elapsed:8,units:[me],buildings:[deck,ramp,house,house2],simulate:false,winner:null};
const views=[], commands=[],issued=[],stMobile={pointer:null,unit:null,strength:0};
const ctx={THREE,document:doc,window:dom.window,$,scene,perspectiveCamera:camera,stSession,stMobile,paused:false,
 ST_CANONICAL_PROJECT:{project:{kind:'sheep-tag'},scene:{actors:worldRoutes}},
 ST126_ROUTES:[['pinewatch','Pinewatch',-52.5,-45],['moonflower','Moonflower',60,-52.5],['amberglade','Amberglade',-52.5,60]],
 ST_ARCHIVE_HOUSES:new Set(['st-farm','st-income','st-fort']),ST_ARCHIVE_DECKS:new Set(['st-wall','st-ramp']),
 st126PermanentRoute:b=>b.id.startsWith('st-permanent-route-'),
 st126InstallStarterRoutes:()=>0,
 stObstacles:()=>stSession.buildings.map(b=>({id:b.id,x:b.pos.x,z:b.pos.z})),
 stArchiveAfterUpdate:()=>{},stSeenByRole:()=>true,stStop:()=>{},
 stInstallUI:()=>{},stRefreshHUD:()=>{},
 stUi:{shown:true,build:'st-farm'},stUiFeedback:(m)=>views.push(m),
 stBuildInput:{outcome:null},st126SeedAtSheep:()=>true,
 stUiOrderAt:()=>{ctx.stBuildInput.outcome={ok:true};ctx.stUi.build=null;},
 stIssueBuild:(u,kind,x,z)=>{issued.push([kind,x,z]);u.order={action:'build',kind};return {ok:true};},
 stNewBuilding:(kind,x,z,owner)=>({id:'new',kind,owner}),
 stCanBuild:()=>({ok:true,kind:'st-farm',x:6,z:8,rotation:0}),
 stBuildApproach:()=>({x:5,z:8}),
 stResult:(ok,reason,extra={})=>({ok,reason,...extra}),
 stCommand:(action)=>{commands.push(action);return {ok:true}},
 stMobileStickPoint:()=>{stMobile.strength=.75;},
 stUpdateSheep:()=>{me.order=null;},stPlaceUnit:()=>{},
 stUiStatus:()=>({active:true}),stTouchPlacementEnabled:()=>true
};
vm.createContext(ctx);vm.runInContext(rapid,ctx);vm.runInContext(world,ctx);
const inner=$('engine-canvas'),viewport=$('viewport');
assert.equal(ctx.st132MeadowTarget(inner),true,'renderer canvas is a meadow target');
assert.equal(ctx.st132MeadowTarget(viewport),true);
assert.equal(ctx.st132MeadowTarget($('sheepTagHUD')),false,'HUD is not ground');
ctx.stInstallUI();
const toggle=$('stRapidBuild');
assert.ok(toggle,'rapid toggle appended to Sheep Tag HUD');
assert.equal(toggle.getAttribute('aria-pressed'),'false');
toggle.click();
assert.equal(toggle.getAttribute('aria-pressed'),'true');
assert.equal(toggle.querySelector('small').textContent,'ON');
assert.equal(ctx.stUiStatus().rapidBuild.enabled,true);
ctx.stUiOrderAt(11,14);
assert.equal(ctx.stUi.build,'st-farm','successful native order retains chosen house only in Rapid Build');
const first=ctx.stIssueBuild(me,'st-farm',6,8);
assert.equal(first.ok,true);assert.equal(issued.length,1);
const queue=ctx.stIssueBuild(me,'st-farm',9,8);
assert.equal(queue.ok,true);assert.equal(queue.rapid,true);
assert.equal(me.st132BuildQueue.length,1);
ctx.stUpdateSheep(me,.016);
assert.equal(issued.length,2,'second house issues after completing first');
const built=ctx.stNewBuilding('st-farm',2,3,me.id);
assert.equal(built.owner,me.id);
assert.ok(me.st132BuildHoldUntil>stSession.elapsed);
let updated=0;
ctx.stUpdateSheepBase=ctx.stUpdateSheep;
ctx.stUpdateSheep(me,.016);
assert.equal(me.st132BuildHoldUntil,8.18);
ctx.stMobile.unit=me;ctx.stMobile.pointer=7;
ctx.stMobileStickPoint({pointerId:7});
assert.equal(me.st132BuildHoldUntil,-Infinity,'movement overrides construction beat');
assert.equal(me.st132BuildQueue.length,0,'movement cancels queued orders');
toggle.click();assert.equal(toggle.getAttribute('aria-pressed'),'false');
assert.equal(vm.runInContext('st132Rapid.on',ctx),false);
assert.ok(css.includes('border-radius:50%')&&css.includes('right:clamp(145px'),'circular inner toggle');
for(const [name,cx,cz] of [['pinewatch',-52.5,-45],['moonflower',60,-52.5],['amberglade',-52.5,60]]){
 const route=worldRoutes.filter(a=>a.id.includes('route-'+name+'-'));
 assert.equal(route.length,3);
 const ramp1=route.find(a=>a.id.endsWith('south-ramp')),
   middle=route.find(a=>a.id.endsWith('center-deck')),
   ramp2=route.find(a=>a.id.endsWith('north-ramp'));
 const point=(actor,z)=>new THREE.Vector3(0,0,z).applyAxisAngle(new THREE.Vector3(0,1,0),actor.rotation[1]).add(new THREE.Vector3(...actor.position));
 assert.ok(point(ramp1,-3).distanceTo(point(middle,3))<.000001,'south ramp flush at deck');
 assert.ok(point(ramp2,-3).distanceTo(point(middle,-3))<.000001,'north ramp flush at deck');
 assert.equal(middle.position[0],cx);
 assert.equal(middle.position[2],cz);
}
assert.notEqual(worldRoutes.find(a=>a.id.includes('moonflower-center')).rotation[1],0);
assert.notEqual(worldRoutes.find(a=>a.id.includes('amberglade-center')).rotation[1],0);
const blocked=ctx.stObstacles();
assert.equal(blocked.some(b=>b.id===deck.id),false,'ground sheep can pass under permanent raised deck');
assert.equal(blocked.some(b=>b.id===ramp.id),true,'sloped ramp still collides');
assert.equal(blocked.some(b=>b.id===house.id),true,'house still blocks');
assert.equal(ctx.st132OccludedByStructure(me),true,'camera ray through house hides sheep');
ctx.stArchiveAfterUpdate(stSession,.016,0);
const wire=scene.getObjectByName('st132-wireframe-sheep-controlled');
assert.ok(wire?.visible,'occluded sheep draws wireframe');
const mesh=wire.children.find(child=>child.isMesh);
assert.ok(mesh.material.wireframe&&!mesh.material.depthTest,'outline remains visible through house');
house.mesh.position.set(20,1,20);house.pos.copy(house.mesh.position);
stSession.elapsed+=.23;
ctx.stArchiveAfterUpdate(stSession,.016,0);
assert.equal(wire.visible,false,'outline hides when camera can see sheep');
house.mesh.position.set(0,1,0);house.pos.copy(house.mesh.position);
stSession.elapsed+=.23;
ctx.stArchiveAfterUpdate(stSession,.016,0);
assert.equal(wire.visible,true,'outline returns when house obscures again');
ctx.stStop();
assert.equal(scene.getObjectByName('st132-wireframe-sheep-controlled'),undefined,'clean wireframes on stopping');
if(process.env.SE_ASSEMBLED_HTML){
 const html=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 for(const fragment of [
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_132_MEADOW_GHOST_DRAG_RAPID_BUILDER_ROTATED_UNDERPASS_WIREFRAME',
  "world=st132MeadowTarget(event.target)",'st132MeadowTarget(document.elementFromPoint(x,y));',
  "!st132MeadowTarget(event.target)","if(!st132Rapid.on){stUi.build = null; stUiClearPreview();}",
  "stBuildInputFinish('Building accepted',st132Rapid.on)",'st132GroundUnderpass','st132OrientWorldRoutes',
  'st132OccludedByStructure','st132RapidInstall'
 ])assert.ok(html.includes(fragment),'assembled source missing '+fragment);
}
console.log('SE132_GHOST_DRAG_RAPID_BUILD_018S_MOVE_ROTATED_CROSSINGS_UNDERPASS_OCCLUSION_PASS');
