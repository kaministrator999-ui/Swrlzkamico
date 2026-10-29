import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';

// Exercise the actual sealed gameplay source with Three.js, native actor
// fixtures and continuous movement. This checks geometry at every simulation
// step, including before/after path replanning and construction displacement.
const html=fs.readFileSync(process.env.SWYRL_LANES_HTML||'dist/swrlz-forge-moba/index.html','utf8');
const three=process.env.SWYRL_LANES_THREE||'/workspace/scratch/three-v95-unit.mjs';
const THREE=await import(pathToFileURL(three).href);
const runtime=new URL('../runtime/',import.meta.url),scene=new THREE.Scene(),actors=[];
const currentProject={sheepTag:{duration:1200,headstart:120,bounds:40,startGold:500,role:'sheep',fogMode:'off',elevated:false,thorns:false,totems:false,split:false,events:false,seed:71}};
const context=vm.createContext({THREE,scene,actors,currentProject,ASSET_LIBRARY:[],paused:false,terrainHeight:()=>0,
  walkingObjectVisible:a=>a.visible,stMakeSpirit:()=>new THREE.Group(),stAnimateSpirit(){}});
const game=html.slice(html.indexOf('// Match state and helpers'),html.indexOf('// Player-proposed Archive experiments'));
const integration=html.slice(html.indexOf('// Native project data is the starter'),html.indexOf('const stNativeApplyProjectMeta='));
assert.ok(game.includes('aligned=stLanesSnapHouse')&&integration.includes('wolfRadius:.78'),'CPU test needs the actual v10.4 package');
vm.runInContext(fs.readFileSync(new URL('archive_sheep_visuals.js',runtime),'utf8')+'\n'+game+'\n'+
  fs.readFileSync(new URL('archive_sheep_magic.js',runtime),'utf8')+'\n'+integration+'\n'+
  fs.readFileSync(new URL('sheep_lanes.js',runtime),'utf8')+`\n globalThis.api={start:()=>stStart(),stop:()=>stStop(),status:()=>stStatus(),
  command:(...a)=>stCommand(...a),canBuild:(...a)=>stCanBuild(...a),path:(...a)=>stPath(...a),blocked:(...a)=>stBlocked(...a),
  order:(...a)=>stSetOrder(...a),move:(...a)=>stMoveUnit(...a),bot:(...a)=>stBotWolf(...a),update:(...a)=>stUpdate(...a),
  session:()=>stSession,preflight:(...a)=>stAuthoredMapPreflight(...a),radius:(...a)=>stUnitRadius(...a),rescue:(...a)=>stRescue(...a)};`,context);
const api=context.api,cases=[];
function pass(name){cases.push(name);console.log('SHEEP_LANES_CPU_CASE_PASS',name);}
function actor(id,type,x,z,scale=[1,1,1]){const a=context.stMakeVisual(type);a.name=id;a.position.set(x,0,z);a.scale.fromArray(scale);a.userData={id,actorType:type,baked:true};scene.add(a);actors.push(a);return a;}
function reset(sheep=[[-18,0,-18]],wolves=[[30,0,30]]){api.stop();for(const a of actors)a.removeFromParent();actors.length=0;currentProject.sheepTag.headstart=120;
  sheep.forEach((p,i)=>actor('s'+i,'st-sheep',p[0],p[2]));wolves.forEach((p,i)=>actor('w'+i,'st-wolf',p[0],p[2]));actor('pen','st-pen',0,0);}
function close(a,b,label){assert.ok(Math.abs(a-b)<1e-5,label+': '+a+' vs '+b);}
function separated(){const s=api.session();for(let i=0;i<s.units.length;i++)for(let j=i+1;j<s.units.length;j++){
  const a=s.units[i],b=s.units[j];if(a.captured||b.captured||a.isIllusion||b.isIllusion||Math.abs(a.pos.y-b.pos.y)>=1.2)continue;
  assert.ok(Math.hypot(a.pos.x-b.pos.x,a.pos.z-b.pos.z)>=api.radius(a)+api.radius(b)+.0149,'Bodies overlap: '+a.id+' '+b.id+' '+a.pos.toArray()+' '+b.pos.toArray());}}
function movement(seconds){const s=api.session();for(let i=0;i<seconds/.05;i++){s.elapsed+=.05;for(const u of s.units){const target=u.order&&new THREE.Vector3(u.order.x,0,u.order.z);if(target)api.move(u,target,.05);}separated();}}

for(const [start,expected]of [[[[-18.85,0,-18]],[-19.495,-18]],[[[-17.15,0,-18]],[-16.505,-18]],[[[-18,0,-18.85]],[-18,-19.495]],[[[-18,0,-17.15]],[-18,-16.505]]]){
  reset(start);api.start();const fit=api.canBuild('farm',-18,-18);assert.equal(fit.ok,true);assert.ok(fit.builderExit);
  const before=api.status().gold;assert.equal(api.command('build',{kind:'farm',x:-18,z:-18}).ok,true);
  const s=api.session(),u=s.units[0];close(u.pos.x,expected[0],'Nearest side x');close(u.pos.z,expected[1],'Nearest side z');
  assert.equal(s.buildings.length,1);assert.equal(api.status().gold,before);assert.equal(api.blocked(u.pos.x,u.pos.z,api.radius(u)),false);separated();
}pass('self_construction_uses_all_four_nearest_clear_sides');

for(const kind of ['income','fort','wall','ramp']) {
  reset([[-18.85,0,-18]]);currentProject.sheepTag.elevated=true;api.start();
  const site=api.canBuild(kind,-18,-18),before=api.status().gold;assert.equal(site.ok,true,kind+' rejects its own builder');
  assert.equal(api.command('build',{kind,x:-18,z:-18}).ok,true);const u=api.session().units[0];
  close(u.pos.x,-19.495,kind+' nearest safe side');assert.equal(api.status().gold,before-site.cost);
  assert.equal(api.blocked(u.pos.x,u.pos.z,api.radius(u)),false,kind+' trapped its builder inside its footprint');
}
currentProject.sheepTag.elevated=false;pass('income_fort_wall_and_ramp_also_eject_their_own_builder_and_charge_once');

reset([[-18.85,0,-18]]);actor('neighbour','st-farm',-20.4,-18);api.start();
const fit=api.canBuild('farm',-18,-18);assert.equal(fit.ok,true);assert.ok(fit.builderExit);
assert.ok(Math.abs(fit.builderExit[0]+19.495)>.1,'Builder was pushed inside the flush neighbour');
assert.equal(api.command('build',{kind:'farm',x:-18,z:-18}).ok,true);assert.equal(api.blocked(api.session().units[0].pos.x,api.session().units[0].pos.z,.27),false);
pass('blocked_nearest_side_uses_next_feasible_side');

reset();for(const [x,z]of [[-20.4,-18],[-15.6,-18],[-18,-20.4],[-18,-15.6]])actor('box'+x+z,'st-farm',x,z);api.start();
const gold=api.status().gold,position=api.session().units[0].pos.toArray();assert.equal(api.canBuild('income',-18,-18).ok,false);
assert.equal(api.command('build',{kind:'income',x:-18,z:-18}).ok,false);assert.equal(api.status().gold,gold);assert.deepEqual(api.session().units[0].pos.toArray(),position);assert.equal(api.status().buildings.length,4);
pass('no_safe_ejection_rejects_without_gold_position_or_building_mutation');

reset([[-24,0,-24]]);actor('house','st-farm',-18,-18);api.start();
for(const kind of ['farm','income','fort']){
  const flush=api.canBuild(kind,-15.75,-18),lane=api.canBuild(kind,-14.85,-18);assert.equal(flush.ok,true);assert.equal(lane.ok,true);
  close(flush.x,-15.6,'Flush centre');close(lane.x,-15,'Lane centre');
}
actor('lane','st-farm',-15,-18);api.stop();api.start();assert.ok(api.path(new THREE.Vector3(-16.5,0,-21),new THREE.Vector3(-16.5,0,-15),.27));
assert.equal(api.blocked(-16.5,-18,.78),true);pass('house_edge_snap_seals_or_leaves_actual_sheep_only_lane');

reset([[-16.5,0,-22],[-16.5,0,-20.8]]);actor('left','st-farm',-18,-18,[1,1,5]);actor('right','st-farm',-15,-18,[1,1,5]);api.start();
let s=api.session();api.order(s.units[0],{action:'move',x:-16.5,z:-14});const start=s.units[0].pos.clone();movement(14);
assert.ok(s.units[0].traffic,'No actual traffic decision');assert.ok(s.units[0].pos.distanceTo(start)>.5,'Follower never backed out or selected an alternate lane');
assert.ok(s.units[0].pos.z>-15,'Follower failed to route around a stationary sheep in a one-sheep-wide lane');
pass('following_sheep_does_not_phase_through_blocker_and_takes_another_lane');

reset([[-16.5,0,-22],[-16.5,0,-14]]);actor('left','st-farm',-18,-18,[1,1,5]);actor('right','st-farm',-15,-18,[1,1,5]);api.start();s=api.session();
api.order(s.units[0],{action:'move',x:-16.5,z:-10});api.order(s.units[1],{action:'move',x:-16.5,z:-26});movement(18);
assert.ok(s.units[0].pos.z>-11&&s.units[1].pos.z<-25,'Head-on sheep failed to clear each other by yielding or rerouting');
pass('head_on_sheep_clear_the_lane_without_overlap_at_any_step');

reset([[-30,0,-30]],[[18,0,18],[18,0,21]]);api.start();s=api.session();
api.order(s.units[1],{action:'move',x:18,z:25});api.order(s.units[2],{action:'move',x:18,z:15});movement(8);
assert.ok(s.units[1].pos.z>24&&s.units[2].pos.z<16,'Wolves failed to pass around each other');
close(api.status().houseLanes.wolfRadius,.78,'Larger wolf collision radius');
pass('wolves_use_larger_bodies_and_never_overlap_during_crossing');

reset([[-18,0,-18],[-9,0,-18]],[[-13,0,-18]]);actor('block','st-farm',-15.6,-18);api.start();s=api.session();s.rules.headstart=0;
const wolf=s.units.find(u=>u.kind==='wolf');wolf.botAt=0;api.order(wolf,{action:'attack',id:'block'});api.bot(wolf);
assert.equal(wolf.order.action,'attack');assert.ok(['s0','s1'].includes(wolf.order.id),'Wolf stayed on a building while a sheep was reachable');
assert.match(wolf.aiIntent,/reachable sheep/);pass('wolf_switches_from_building_to_reachable_sheep');

reset([[-18,0,-18],[-4,0,-18]],[[-10,0,-18]]);
for(const dx of [-2.4,0,2.4])for(const dz of [-2.4,0,2.4])if(dx||dz)actor('ring'+dx+dz,'st-farm',-18+dx,-18+dz);
api.start();s=api.session();s.rules.headstart=0;const chooser=s.units.find(u=>u.kind==='wolf');chooser.botAt=0;api.bot(chooser);
assert.equal(chooser.order.id,'s1','An unreachable nearby sheep caused demolition while another sheep was reachable');
pass('wolf_checks_all_visible_sheep_before_demolishing_an_unreachable_targets_maze');

reset([[-18,0,-6]],[[-22,0,-6]]);currentProject.sheepTag.elevated=true;currentProject.sheepTag.wolvesUseRamps=true;
actor('ramp','st-ramp',-18,-12);actor('deck','st-wall',-18,-18);api.start();
assert.equal(api.command('move',{x:-18,z:-18,layer:'upper'}).ok,true);
for(let i=0;i<140;i++){api.update(.05,i*.05);separated();}
s=api.session();assert.equal(s.units[0].archiveOnUpper,true,'Raised fixture never reached the deck on foot');
s.rules.headstart=0;const climber=s.units.find(u=>u.kind==='wolf');climber.botAt=0;api.bot(climber);
assert.equal(climber.order.id,'s0','Wolf demolished a connected ramp rather than chasing its reachable raised sheep');
for(let i=0;i<240&&!s.units[0].captured;i++){api.update(.05,i*.05);separated();}
assert.equal(s.units[0].captured,true,'Wolf failed to climb the connected ramp and tag the prioritized sheep');
currentProject.sheepTag.elevated=false;pass('wolf_prioritizes_reachable_raised_sheep_and_uses_connected_ramp');

reset([[-18,0,-18],[-23,0,-23]]);api.start();s=api.session();const captive=s.units[1],rescuer=s.units[0];captive.captured=true;captive.spirit=new THREE.Group();captive.spirit.position.copy(rescuer.pos);scene.add(captive.spirit);
assert.equal(api.rescue(captive,rescuer),true);separated();pass('rescue_chooses_free_landing_instead_of_overlapping_rescuer');

const pre=api.preflight({pieces:[{id:'a',type:'st-sheep',position:[-18,0,-18]},{id:'b',type:'st-sheep',position:[-18.1,0,-18]},{id:'w',type:'st-wolf',position:[20,0,20]},{id:'pen',type:'st-pen',position:[0,0,0]}]});
assert.equal(pre.ok,false);assert.match(pre.reason,/overlapping sheep/);pass('native_map_preflight_rejects_overlapping_same_species_spawns');
api.stop();console.log('SHEEP_LANES_CPU_ALL_CASES_PASS',cases.length);
