import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const source=fs.readFileSync(root+'runtime/sheep_centered_placement_world_routes_magic_v11_126.js','utf8');
const project=JSON.parse(fs.readFileSync(root+'scenes/sheep-tag-seven-minute-v11-85.swyrl.json','utf8'));
let made=0,attacks=0,removed=0,orders=0,previews=0,seeded=null;
const point={x:9,y:0,z:12,clone(){return {...this,clone:this.clone}}};
const c={
 ST_CANONICAL_PROJECT:project,structuredClone:globalThis.structuredClone,
 stNewBuilding:(kind,x,z,owner,authored)=>({id:authored?.userData?.id||'player-'+(++made),kind,owner,progress:authored?1:0,hp:300}),
 stAttackBuilding:()=>attacks++,stRemoveBuilding:()=>removed++,
 stCommand:()=>{orders++;return {ok:true};},stResult:(ok,reason)=>({ok,reason}),
 stArchiveStart:s=>{for(const u of s.units){u.archiveLevel=1;u.archiveSplitAt=-Infinity;u.archiveTotemAt=-Infinity;}},
 stArchiveTotemReady:()=>false,stUiStatus:()=>({}),stLoadStarter:()=>true,
 stPlacementGridSeed:()=>{},stUi:{preview:{},build:'st-farm',placementPoint:null},
 stTouchPlacementEnabled:()=>true,stUiPlacePreview:p=>{seeded=p;previews++;},
 stSession:{controlledId:'sheep',units:[{id:'sheep',pos:point}],buildings:[]},
 terrainHeight:()=>0,
 ST_ARCHIVE_HOUSES:new Set(['st-farm','st-income','st-fort','st-totem'])
};
vm.createContext(c);
vm.runInContext(source,c,{filename:'v11_126.js'});
const routes=project.scene.actors.filter(a=>a.id?.startsWith('st-permanent-route-'));
assert.equal(routes.length,9,'three crossing groups × ramp,deck,ramp');
assert.equal(new Set(routes.map(x=>x.id)).size,9,'unique world actor IDs');
assert.equal(routes.filter(x=>x.type==='st-ramp').length,6);
assert.equal(routes.filter(x=>x.type==='st-wall').length,3);
assert.ok(routes.every(x=>x.baked&&x.visible&&x.tags.includes('indestructible')));
for(const id of ['pinewatch','moonflower','amberglade']){
 const r=routes.filter(x=>x.id.startsWith('st-permanent-route-'+id+'-'));
 assert.equal(r.length,3);
 const ramp1=r.find(x=>x.id.endsWith('south-ramp'));
 const deck=r.find(x=>x.id.endsWith('center-deck'));
 const ramp2=r.find(x=>x.id.endsWith('north-ramp'));
 assert.equal(ramp1.position[2]-deck.position[2],6);
 assert.equal(ramp2.position[2]-deck.position[2],-6);
 assert.ok(Math.abs(ramp2.rotation[1]-Math.PI)<.00001);
 // Rising ends touch deck at its 2 opposite six-metre endpoints.
 assert.equal(ramp1.position[2]-3,deck.position[2]+3);
 assert.equal(ramp2.position[2]+3,deck.position[2]-3);
}
// Ensure we did not place permanent world pieces on obstacles or spawn pads.
const other=project.scene.actors.filter(a=>!a.id?.startsWith('st-permanent-route-')
 && ['st-sheep','st-wolf','st-rock','st-tree','st-pond','st-shop','st-zone','st-pen'].includes(a.type));
for(const piece of routes){
 for(const a of other){
  const r=a.type==='st-pen'?30:a.type==='st-zone'?12:
   (a.colliderRadius||1.5)*Math.max(Math.abs(a.scale[0]),Math.abs(a.scale[2]));
  const dx=Math.max(0,Math.abs(piece.position[0]-a.position[0])-1.2);
  const dz=Math.max(0,Math.abs(piece.position[2]-a.position[2])-3);
  assert.ok(Math.hypot(dx,dz)>r+.35,'raised route intersects authored obstacle '+a.id);
 }
}
assert.equal(c.st126InstallStarterRoutes(),0,'starter injection idempotent');
const authored={userData:{id:routes[0].id}};
const fixed=c.stNewBuilding('st-ramp',0,0,null,authored);
const regular=c.stNewBuilding('st-ramp',5,5,'sheep');
assert.equal(fixed.permanentRoute,true);assert.equal(fixed.owner,'world');assert.equal(fixed.progress,1);
c.stSession.buildings=[fixed,regular];
c.stAttackBuilding(null,fixed);c.stRemoveBuilding(fixed);
assert.equal(attacks,0);assert.equal(removed,0);
c.stAttackBuilding(null,regular);c.stRemoveBuilding(regular);
assert.equal(attacks,1);assert.equal(removed,1);
assert.equal(c.stCommand('sell',{id:fixed.id}).ok,false);
assert.equal(orders,0);
const s={role:'sheep',rules:{split:true,splitUnlock:2,splitCooldown:30,totems:true,totemLimit:'once',totemCooldown:120},units:[{kind:'sheep'}]};
c.stArchiveStart(s);
assert.equal(s.rules.splitUnlock,1);assert.equal(s.rules.splitCooldown,12);
assert.equal(s.rules.totemLimit,'cooldown');assert.equal(s.rules.totemCooldown,25);
const sheep={kind:'sheep',id:'sheep',captured:false,isIllusion:false,archiveTotemAt:-Infinity};
const home={kind:'st-farm',owner:'sheep',hp:180,progress:1};
assert.equal(c.stArchiveTotemReady({rules:s.rules,elapsed:0},sheep,home),true);
assert.equal(c.stArchiveTotemReady({rules:s.rules,elapsed:0},sheep,{...home,progress:0}),false);
assert.equal(c.st126SeedAtSheep(),true);
assert.equal(previews,1);assert.equal(seeded.x,9);assert.equal(seeded.z,12);
assert.equal(orders,0,'preview must never auto-build');
if(process.env.SE_ASSEMBLED_HTML){
 const h=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 for(const t of [
  "else st126SeedAtSheep();",
  "stBuildInputFinish('Tool selected',true);st126SeedAtSheep();",
  "stPlacementGridSeed=st126SeedAtSheep",
  "Preview starts at your sheep",
  "st126InstallStarterRoutes",
  "densityRequired:1",
  "if(count<1)return stResult",
  "stLanesEjection",
  "stHonestGapLocalClear",
  "SWYRL_ENGINE_DEPLOY_MARKER: V11_126_SHEEP_CENTERED_BUILD_PERMANENT_ROUTES_READY_SKILLS",
 ]) assert.ok(h.includes(t),'missing assembled contract '+t);
}
console.log('SE_V11126_SHEEP_CENTERED_PREVIEW_9_PERMANENT_ROUTE_PIECES_AND_FASTER_MAGIC_PASS');
