import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const THREE=require(process.env.SE_THREE_MODULE);
const {JSDOM}=require(process.env.SE_JSDOM_MODULE);
const source=fs.readFileSync('projects/swrlz-forge-moba/runtime/sheep_rapid_build_rotated_routes_wireframe_v11_132.js','utf8');
const css=fs.readFileSync('projects/swrlz-forge-moba/runtime/sheep_rapid_build_rotated_routes_wireframe_v11_132.css','utf8');
const {window}=new JSDOM('<div id="sheepTagHUD"></div>',{url:'https://example.test'});
const sceneProject={scene:{actors:[]}};
for(const id of ['pinewatch','moonflower','amberglade'])
 for(const suffix of ['south-ramp','center-deck','north-ramp'])
 sceneProject.scene.actors.push({id:'st-permanent-route-'+id+'-'+suffix,position:[0,0,0],rotation:[0,0,0]});
let created=0,buttonRotations=0,feedback=[],updated=0;
const originalActor=new THREE.Group();originalActor.name='stActualSheep';
originalActor.add(new THREE.Mesh(new THREE.SphereGeometry(.48,6,6),new THREE.MeshBasicMaterial()));
originalActor.position.set(0,0,0);
const center=new THREE.Mesh(new THREE.BoxGeometry(2.4,.3,6),new THREE.MeshBasicMaterial());
center.position.set(0,3.2,0);center.updateMatrixWorld(true);
const building={id:'deck-1',kind:'st-wall',hp:250,progress:1,mesh:center,
 pos:{x:0,y:0,z:0},localHalfX:1.2,localHalfZ:3,rotation:0};
const sheep={id:'u',kind:'sheep',pos:new THREE.Vector3(0,0,0),actor:originalActor,captured:false,order:null};
const s={units:[sheep],buildings:[building],controlledId:'u',simulate:false,winner:null,elapsed:2};
const cam=new THREE.PerspectiveCamera(50,1,.1,100);
cam.position.set(0,10,8);cam.lookAt(0,0,0);cam.updateMatrixWorld(true);
const ctx={
 THREE,window,document:window.document,console,
 stSession:s,stUi:{shown:true,build:'st-farm'},stMobile:{pointer:null,unit:null,strength:0},paused:false,
 '$':id=>window.document.getElementById(id),
 stInstallUI:()=>{},stRefreshHUD:()=>{},
 stNewBuilding:(kind,x,z,owner,authored)=>{created++;return {id:'player-'+created,kind,owner};},
 stUpdateSheep:(unit,dt)=>{updated++;if(unit.order?.action==='build')unit.pos.x+=dt*2;return 'updated';},
 stSetOrder:(unit,order)=>{unit.order=order;return order;},
 stObstacles:()=>[{id:'deck-1',kind:'st-wall'},{id:'ramp-1',kind:'st-ramp'}],
 stLoadStarter:()=>true,ST_CANONICAL_PROJECT:sceneProject,
 stUiFeedback:msg=>feedback.push(msg),stUiRotatePlacement:()=>{buttonRotations++;},
 stArchiveAfterUpdate:()=>{},stDisposeUI:()=>{},stUiStatus:()=>({}),
 stIntersectsObstacle:(x,z,r,b)=>Math.abs(x-b.x)<=b.localHalfX&&Math.abs(z-b.z)<=b.localHalfZ,
 stBuildingObstacle:b=>({...b,pos:undefined,x:b.pos.x,z:b.pos.z}),
 terrainHeight:()=>0,perspectiveCamera:cam,camera:cam,
 stUiChooseBuild:k=>ctx.stUi.build=k,st126SeedAtSheep:()=>{}
};
vm.createContext(ctx);vm.runInContext(source,ctx,{filename:'se132.js'});
ctx.stInstallUI();
const button=window.document.getElementById('st132RapidBuild');
assert.ok(button,'circular build-mode control exists');
assert.equal(button.getAttribute('aria-pressed'),'false');
button.click();assert.equal(button.getAttribute('aria-pressed'),'true');
assert.equal(vm.runInContext('st132Rapid',ctx),true);button.click();assert.equal(vm.runInContext('st132Rapid',ctx),false);
ctx.stUi.build='st-ramp';ctx.stRefreshHUD();
const rotate=window.document.getElementById('st132Rotate');
assert.equal(rotate.hidden,false);rotate.click();assert.equal(buttonRotations,1);
ctx.stUi.build='st-farm';ctx.stRefreshHUD();assert.equal(rotate.hidden,true);
const roots=sceneProject.scene.actors;
assert.equal(ctx.st132RotateCanonicalCrossings(),9);
const axis={pinewatch:0,moonflower:Math.PI/2,amberglade:-Math.PI/2};
for(const [id,angle] of Object.entries(axis)){
 const parts=roots.filter(a=>a.id.includes('-'+id+'-'));
 assert.equal(parts.length,3);
 const deck=parts.find(a=>a.id.endsWith('center-deck'));
 const south=parts.find(a=>a.id.endsWith('south-ramp'));
 const north=parts.find(a=>a.id.endsWith('north-ramp'));
 assert.ok(Math.abs(south.rotation[1]-angle)<1e-8);
 assert.ok(Math.abs(deck.rotation[1]-angle)<1e-8);
 assert.ok(Math.abs(north.rotation[1]-(angle+Math.PI))<1e-8);
 assert.ok(Math.abs(south.position[0]-deck.position[0]-6*Math.sin(angle))<1e-8);
 assert.ok(Math.abs(south.position[2]-deck.position[2]-6*Math.cos(angle))<1e-8);
 assert.ok(Math.abs(north.position[0]-deck.position[0]+6*Math.sin(angle))<1e-8);
 assert.ok(Math.abs(north.position[2]-deck.position[2]+6*Math.cos(angle))<1e-8);
}
assert.deepEqual(ctx.stObstacles().map(b=>b.kind),['st-ramp'],'completed 3.3 m deck lets sheep pass underneath');
building.progress=.5;
assert.deepEqual(ctx.stObstacles().map(b=>b.kind),['st-wall','st-ramp'],'under-construction deck is still solid');
building.progress=1;
s.elapsed=10;ctx.stNewBuilding('st-farm',3,3,'u');
assert.equal(sheep.st132RecoveryUntil,10.28);
sheep.order={action:'build',x:9,z:2};
ctx.stUpdateSheep(sheep,.1);assert.equal(sheep.pos.x,0,'sheep pauses briefly after construction');
assert.equal(sheep.order.action,'build','paused order is preserved');
ctx.stSetOrder(sheep,{action:'move',x:10,z:1});
assert.equal(sheep.st132RecoveryUntil,0,'movement immediately bypasses recovery');
ctx.stUpdateSheep(sheep,.1);
ctx.st132SetRapid(true);ctx.stRefreshHUD();
assert.equal(vm.runInContext('st132Rapid',ctx),true);
assert.equal(ctx.st132GroundUnderDeck(sheep,s),true);
ctx.stArchiveAfterUpdate(s,.016,0);
const wire=originalActor.getObjectByName('st132OccludedSheepWireframe');
assert.ok(wire&&wire.visible,'sheep occluded under raised platform gets its own wireframe');
let wireMeshes=0;wire.traverse(obj=>{if(obj.isMesh){wireMeshes++;assert.equal(obj.material.wireframe,true);assert.equal(obj.material.depthTest,false);}});
assert.ok(wireMeshes>0,'real sheep mesh cloned for x-ray outline');
building.mesh.position.set(40,3,40);building.pos={x:40,y:0,z:40};building.mesh.updateMatrixWorld(true);
s.elapsed+=.3;ctx.stArchiveAfterUpdate(s,.016,0);
assert.equal(wire.visible,false,'outline disappears when camera view is clear');
ctx.stDisposeUI();assert.equal(vm.runInContext('st132Rapid',ctx),false);
assert.equal(originalActor.getObjectByName('st132OccludedSheepWireframe'),undefined);
assert.ok(css.includes('border-radius:50%')&&css.includes('#st132Rotate'));
if(process.env.SE_ASSEMBLED_HTML){
 const h=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 for(const expected of [
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_132_RAPID_BUILD_UNDERPASS_AND_SHEEP_WIREFRAME',
  'st132InstallRapid','st132CameraBlocked','st132GroundUnderDeck','st132RotateCanonicalCrossings',
  'const kind=button?.dataset.stSkill||stUi.build,meadow=!button;',
  'stBuildInputFinish(\'New placement\',meadow);',
  'if(!meadow)stUiChooseBuild(kind);',
  'if(repeat&&stSession&&!stSession.winner){stUiChooseBuild(kind);st126SeedAtSheep();}',
  'st131InstallMirrorControl','se130InstallSecondTapProtection'
 ])assert.ok(h.includes(expected),'integrated contract missing '+expected);
}
console.log('SE132_MEADOW_DRAG_RAPID_BUILD_INTERRUPTIBLE_RECOVERY_ROTATED_CROSSINGS_UNDERPASS_WIREFRAME_PASS');
