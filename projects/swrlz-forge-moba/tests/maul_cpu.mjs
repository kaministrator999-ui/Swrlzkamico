import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const testDirectory=path.dirname(fileURLToPath(import.meta.url));
const sealedPath=process.env.SWYRL_MAUL_HTML;
const input=fs.readFileSync(sealedPath||path.join(testDirectory,'../runtime/maul_core.js'),'utf8');
const begin=input.indexOf('const MAUL_CORE = (() => {'),end=input.indexOf('// MAUL_CORE_END',begin);
assert.ok(begin>=0&&end>begin,'The executed source must contain the actual sealed Maul core.');
const context=vm.createContext({});
vm.runInContext(input.slice(begin,end)+'\nglobalThis.core = MAUL_CORE;',context,{timeout:2000});
const core=context.core;
if(sealedPath)console.log(`MAUL_CPU_SOURCE_SHA256 ${crypto.createHash('sha256').update(input).digest('hex')}`);
let cases=0;
const pass=name=>{cases++;console.log(`MAUL_CPU_CASE_PASS ${name}`);};
const plain=value=>JSON.parse(JSON.stringify(value));
const rounded=value=>JSON.parse(JSON.stringify(value,(_,v)=>typeof v==='number'?Math.round(v*1e9)/1e9:v));
const cellKey=p=>`${p.x},${p.z}`;
const fresh=(rules={},towers=[])=>core.createSession({rules:{soloSupport:false,autoWaves:false,...rules},towers});
const advance=(s,seconds)=>{for(let left=seconds;left>1e-9;left-=.05)core.tick(s,Math.min(.05,left));};
const runUntil=(s,predicate,max=180)=>{for(let i=0;i<max*20;i++){if(predicate(s))return;core.tick(s,.05);}assert.ok(predicate(s),`Timed out in ${s.phase}, wave ${s.wave}, creeps ${core.status(s).creeps}.`);};
const playerTower=(kind,cx,cz,level=1)=>({kind,cx,cz,level,owner:'player'});

{
  const map=core.mapDefault(),check=core.preflight(map);
  assert.equal(map.sectors.length,9);assert.equal(map.spawns.length,9);assert.equal(map.cols,31);assert.equal(map.rows,38);assert.equal(map.cell,2);assert.equal(check.ok,true);
  assert.equal(new Set(map.spawns.map(p=>p.sector)).size,9);
  for(const sector of map.sectors){assert.ok(map.reserved.some(p=>p.x===sector.spawn.x&&p.z===sector.spawn.z));assert.ok(map.reserved.some(p=>p.x===sector.gate.x&&p.z===sector.gate.z));}
  assert.deepEqual(plain(core.cellToWorld(map,15,36)),{x:0,z:35});assert.deepEqual(plain(core.worldToCell(map,-20,-35)),{x:5,z:1});
  pass('nine_sector_authored_grid_routes_protected_gates_and_world_coordinates');
}
{
  const map={cols:5,rows:5,cell:2,origin:{x:0,z:0},blocked:[{x:1,z:0},{x:0,z:1}]};
  assert.equal(core.path(map,[],{x:0,z:0},{x:1,z:1}),null,'Blocked cardinal neighbors cannot be crossed diagonally.');
  const route=core.path(map,[],{x:2,z:0},{x:0,z:2});assert.ok(route.length>1);
  for(let i=1;i<route.length;i++)assert.equal(Math.abs(route[i].x-route[i-1].x)+Math.abs(route[i].z-route[i-1].z),1);
  assert.equal(core.path(map,[],{x:-1,z:0},{x:2,z:2}),null);
  pass('cardinal_bfs_rejects_corner_cutting_and_outside_cells');
}
{
  const map=core.mapDefault();
  for(const spawn of map.spawns){const p=core.route(map,[],spawn,spawn.sector),sector=map.sectors[spawn.sector];assert.ok(p);
    let last=-1;for(const gate of sector.gates){const index=p.findIndex(q=>q.x===gate.x&&q.z===gate.z);assert.ok(index>last);last=index;}
    assert.deepEqual(plain(p.at(-1)),plain(map.exit));
  }
  const air=core.route(map,[{cx:5,cz:2}],map.spawns[0],0,true);assert.equal(air.length,5);assert.deepEqual(plain(air[1]),{x:5,z:11});
  pass('each_stream_visits_downstream_sector_gates_then_shared_exit');
}
{
  const map=core.mapDefault();
  assert.equal(core.preflight(map,[playerTower('arrow',5,1)]).ok,false);
  assert.equal(core.preflight(map,[playerTower('arrow',4,4),playerTower('frost',4,4)]).ok,false);
  assert.equal(core.preflight(map,[playerTower('unknown',4,4)]).ok,false);
  assert.equal(core.preflight(map,[playerTower('arrow',4,4,4)]).ok,false);
  const walls=Array.from({length:9},(_,i)=>playerTower('maze-wall',i+1,4));assert.equal(core.preflight(map,walls).ok,false);
  assert.throws(()=>fresh({},[playerTower('arrow',5,1)]),/protected/);
  pass('editor_preflight_rejects_overlaps_invalid_levels_and_authored_dead_ends');
}
{
  const s=fresh({startGold:20}),before=JSON.stringify(s);
  for(const [x,z,code] of [[0,4,'wall'],[5,1,'reserved'],[15,36,'reserved'],[-1,3,'outside']]){assert.equal(core.build(s,'arrow',x,z).code,code);assert.equal(JSON.stringify(s),before);}
  const built=core.build(s,'arrow',4,4);assert.equal(built.ok,true);assert.equal(s.gold,0);assert.equal(core.build(s,'maze-wall',4,4).code,'occupied');assert.equal(core.build(s,'maze-wall',3,4).code,'gold');assert.equal(s.towers.length,1);
  const imported=fresh({},[{...playerTower('arrow',4,4),id:'maul-tower-2'}]);assert.equal(core.build(imported,'arrow',3,4).tower.id,'maul-tower-3');assert.equal(new Set(imported.towers.map(t=>t.id)).size,2);
  pass('construction_validation_is_transactional_and_charges_only_valid_cells');
}
{
  const s=fresh();for(let x=1;x<=9;x++){if(x===5)continue;assert.equal(core.build(s,'maze-wall',x,4).ok,true);}
  const gold=s.gold,count=s.towers.length,fit=core.build(s,'maze-wall',5,4);assert.equal(fit.ok,false);assert.equal(fit.code,'blocked');assert.equal(s.gold,gold);assert.equal(s.towers.length,count);assert.equal(core.preflight(s.map,s.towers).ok,true);
  pass('last_maze_gap_cannot_close_any_sector_route');
}
{
  const near=fresh({spawnInterval:2});core.startWave(near);advance(near,.3);const nearCreep=near.units.find(u=>u.sector===0);assert.equal(nearCreep.cz,1);
  const beforeNearBuild=JSON.stringify(near);assert.equal(core.build(near,'maze-wall',5,2).code,'creep');assert.equal(JSON.stringify(near),beforeNearBuild,'A neighboring cell placement cannot overlap a moving creep body or charge gold.');assert.equal(core.canBuild(near,'maze-wall',5,3).ok,true);
  const s=fresh({spawnInterval:2});core.startWave(s);advance(s,1.4);
  const creep=s.units.find(u=>u.sector===0);assert.equal(creep.cz,3);
  assert.equal(core.build(s,'maze-wall',creep.cx,creep.cz).code,'creep');
  for(const [x,z] of [[4,3],[6,3],[5,2]])assert.equal(core.build(s,'maze-wall',x,z).ok,true);
  const gold=s.gold,fit=core.build(s,'maze-wall',5,4);assert.equal(fit.code,'trapped');assert.equal(s.gold,gold);assert.equal(core.preflight(s.map,[...s.towers,playerTower('maze-wall',5,4)]).ok,true,'Spawn routes alone remain open; the active creep check prevents this trap.');
  pass('active_ground_creeps_cannot_be_overbuilt_or_enclosed');
}
{
  const s=fresh({spawnInterval:2});core.startWave(s);advance(s,.8);const u=s.units.find(u=>u.sector===0),position={x:u.x,z:u.z};
  assert.equal(core.build(s,'maze-wall',5,4).ok,true);assert.equal(u.x,position.x);assert.equal(u.z,position.z);assert.equal(u.path.some(p=>p.x===5&&p.z===4),false);
  for(let i=0;i<160;i++){core.tick(s,.05);if(!u.alive)break;assert.equal(s.towers.some(t=>t.cx===u.cx&&t.cz===u.cz),false);}
  const sold=core.sell(s,s.towers[0].id);assert.equal(sold.ok,true);assert.ok(u.path.length);
  pass('live_builds_reroute_from_current_cells_without_teleporting_or_tunneling');
}
{
  const s=fresh({startGold:200}),t=core.build(s,'arrow',4,4).tower;assert.equal(s.gold,180);
  assert.equal(core.upgrade(s,t.id).ok,true);assert.equal(t.level,2);assert.equal(t.spent,55);assert.equal(s.gold,145);
  assert.equal(core.upgrade(s,t.id).ok,true);assert.equal(t.level,3);assert.equal(t.spent,120);assert.equal(s.gold,80);
  assert.equal(core.upgrade(s,t.id).code,'maximum');assert.equal(core.setPriority(s,t.id,'strong').ok,true);assert.equal(t.priority,'strong');assert.equal(core.setPriority(s,t.id,'invalid').ok,false);
  assert.equal(core.sell(s,t.id).refund,84);assert.equal(s.gold,164);assert.equal(s.towers.length,0);
  pass('tower_upgrade_costs_target_priorities_and_seventy_percent_sell_refunds');
}
{
  const waiting=fresh({preparation:.1});advance(waiting,1);assert.equal(waiting.wave,0);assert.equal(waiting.timer,0);assert.equal(core.startWave(waiting).ok,true);assert.equal(core.startWave(waiting).code,'active');
  const automatic=fresh({preparation:.1,autoWaves:true});advance(automatic,.15);assert.equal(automatic.wave,1);assert.equal(automatic.phase,'wave');
  const paused=JSON.stringify(automatic);assert.equal(core.tick(automatic,0).phase,'wave');assert.equal(JSON.stringify(automatic),paused);core.tick(automatic,NaN);assert.equal(JSON.stringify(automatic),paused);
  pass('manual_and_automatic_wave_clocks_advance_only_from_native_elapsed_time');
}
{
  const s=core.createSession({rules:{soloSupport:true,autoWaves:false,waves:2,difficulty:.25}});assert.equal(s.gold,900);assert.equal(s.towers.length,16);assert.equal(s.towers.some(t=>t.owner==='ally-0'),false);
  const ally=s.towers[0];assert.equal(core.upgrade(s,ally.id).code,'ally');assert.equal(core.sell(s,ally.id).code,'ally');assert.equal(core.setPriority(s,ally.id,'last').code,'ally');
  core.startWave(s);runUntil(s,q=>q.phase==='intermission');assert.ok(s.towers.some(t=>t.owner!=='player'&&t.level===2));assert.ok(s.events.some(e=>e.type==='ally-upgraded'));assert.equal(s.gold,944,'Allied kill bounties belong to their builders; only the wave bonus reaches the player.');
  pass('solo_support_builders_use_separate_budgets_and_upgrade_between_waves');
}
{
  const s=fresh({waves:1,difficulty:.25,spawnInterval:.1},[playerTower('cannon',4,2,3)]);core.startWave(s);advance(s,1.3);
  const group=s.events.filter(e=>e.type==='killed'&&e.details.towerId===s.towers[0].id);assert.ok(group.length>=3);assert.ok(group.some((e,i)=>i&&Math.abs(e.t-group[i-1].t)<1e-8),'One siege splash must kill multiple nearby creeps.');
  const frost=fresh({spawnInterval:2},[playerTower('frost',4,2)]);core.startWave(frost);advance(frost,.5);const chilled=frost.units.find(u=>u.sector===0);assert.ok(chilled.slowUntil>frost.elapsed);assert.equal(chilled.slowFactor,.55);assert.ok(chilled.hp<chilled.maxHp);
  assert.equal(core.sell(frost,frost.towers[0].id).ok,true);advance(frost,2.1);assert.equal(chilled.slowFactor,1);assert.equal(chilled.slowUntil,0);
  const storm=fresh({difficulty:.25,spawnInterval:.1},[playerTower('storm',4,2,3)]);core.startWave(storm);advance(storm,.8);assert.ok(storm.events.filter(e=>e.type==='killed').length>=3);
  pass('native_combat_applies_siege_splash_frost_slow_and_storm_chain_hits');
}
{
  const defense=[playerTower('arrow',4,8,3),playerTower('storm',6,8,3),playerTower('arrow',14,35,3),playerTower('arrow',16,35,3)];
  const s=core.createSession({rules:{waves:10,preparation:0,intermission:0,difficulty:.25},towers:defense});
  runUntil(s,q=>q.wave===5&&q.units.some(u=>u.alive&&u.air),600);const flier=s.units.find(u=>u.alive&&u.air);assert.ok(flier.path.length<=5);assert.ok(flier.path.every(p=>p.x===s.map.spawns[flier.sector].x||p.x===s.map.exit.x));
  assert.ok(s.events.some(e=>e.type==='spawned'&&e.details.armor>0));
  runUntil(s,q=>q.wave===10&&q.units.some(u=>u.alive&&u.boss),600);const boss=s.units.find(u=>u.alive&&u.boss);assert.equal(boss.air,false);assert.ok(boss.maxHp>100);const escort=s.events.find(e=>e.type==='spawned'&&!e.details.boss&&e.details.armor===0);assert.ok(boss.maxHp>escort.details.hp*5);assert.ok(s.events.some(e=>e.type==='wave-started'&&e.details.wave===5&&e.details.air));assert.ok(s.events.some(e=>e.type==='wave-started'&&e.details.wave===10&&e.details.boss));
  pass('scheduled_air_armored_and_boss_waves_keep_distinct_routes_and_stats');
}
{
  const a=fresh({seed:17,spawnInterval:.1}),b=fresh({seed:17,spawnInterval:.1});core.startWave(a);core.startWave(b);advance(a,1);for(let i=0;i<4;i++)core.tick(b,.25);
  assert.deepEqual(rounded(a),rounded(b));const resumed=JSON.parse(JSON.stringify(a));advance(a,.5);advance(resumed,.5);assert.deepEqual(plain(a),plain(resumed));
  assert.equal(JSON.stringify(a).includes('null'),false,'Finite JSON state is retained.');
  pass('seeded_simulation_and_json_restoration_are_deterministic_across_tick_sizes');
}
{
  const s=fresh({waves:1,lives:1,preparation:0,autoWaves:true});runUntil(s,q=>q.phase==='lost',120);assert.equal(s.lives,0);assert.equal(s.leaks,1);assert.equal(s.events.filter(e=>e.type==='lost').length,1);
  const final=JSON.stringify(s);core.tick(s,1);assert.equal(JSON.stringify(s),final);assert.equal(core.build(s,'arrow',4,4).code,'finished');assert.equal(core.startWave(s).code,'finished');
  pass('shared_exit_leaks_end_the_match_once_and_freeze_terminal_game_state');
}
{
  assert.equal(core.validateRules({waves:31,lives:0,preparation:1000,difficulty:NaN}).ok,false);assert.throws(()=>fresh({waves:31}),/waves/);
  const cleaned=core.cleanRules({waves:31,lives:-4,preparation:NaN,autoWaves:'false'});assert.equal(cleaned.waves,30);assert.equal(cleaned.lives,30);assert.equal(cleaned.preparation,40);assert.equal(cleaned.autoWaves,true);
  const small=fresh({waves:1,lives:1,preparation:0,intermission:0,startGold:0});assert.equal(small.rules.waves,1);assert.equal(small.rules.startGold,0);
  pass('authoring_rules_reject_unrealistic_values_and_preserve_short_test_rounds');
}
{
  const s=core.createSession({rules:{preparation:0,intermission:0}});
  for(const [kind,cx,cz] of [['arrow',4,8],['storm',6,8],['arrow',14,35],['arrow',16,35],['frost',5,7]]){
    const built=core.build(s,kind,cx,cz);assert.equal(built.ok,true);while(built.tower.level<3)assert.equal(core.upgrade(s,built.tower.id).ok,true);
  }
  runUntil(s,q=>q.phase==='won'||q.phase==='lost',2400);assert.equal(s.phase,'won');assert.equal(s.wave,30);assert.ok(s.lives>0);assert.ok(s.kills>1000);assert.equal(s.events.filter(e=>e.type==='wave-cleared').length,30);assert.equal(s.events.filter(e=>e.type==='won').length,1);
  const final=JSON.stringify(s);core.tick(s,1);assert.equal(JSON.stringify(s),final);assert.ok(s.events.some(e=>e.type==='ally-upgraded'&&e.details.level===3));
  pass('balanced_full_thirty_wave_campaign_can_win_with_player_and_solo_builders');
}
console.log(`MAUL_CPU_ALL_CASES_PASS ${cases}`);
