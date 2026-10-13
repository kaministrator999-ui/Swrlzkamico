import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url)),sealedPath=process.env.SWYRL_MAUL_WARS_HTML;
const input=sealedPath?fs.readFileSync(sealedPath,'utf8'):fs.readFileSync(path.join(here,'../runtime/maul_core.js'),'utf8')+'\n'+fs.readFileSync(path.join(here,'../runtime/maul_wars_core.js'),'utf8');
function source(name){const a=input.indexOf(`const ${name} = (() => {`),b=input.indexOf(`// ${name}_END`,a);assert.ok(a>=0&&b>a,`Actual sealed ${name} must be present.`);return input.slice(a,b);}
const context=vm.createContext({});vm.runInContext(source('MAUL_CORE')+'\n'+source('MAUL_WARS_CORE')+'\nglobalThis.core = MAUL_WARS_CORE;',context,{timeout:2000});
const core=context.core;if(sealedPath)console.log(`MAUL_WARS_CPU_SOURCE_SHA256 ${crypto.createHash('sha256').update(input).digest('hex')}`);
let cases=0;const names=new Set(),pass=name=>{assert.ok(!names.has(name));names.add(name);cases++;console.log(`MAUL_WARS_CPU_CASE_PASS ${name}`);};
const plain=v=>JSON.parse(JSON.stringify(v)),rounded=v=>JSON.parse(JSON.stringify(v,(_,x)=>typeof x==='number'?Math.round(x*1e8)/1e8:x));
const fresh=(rules={},towers=[],map=core.mapDefault())=>core.createSession({rules:{preparation:0,soloSupport:false,opponentAI:false,...rules},map,towers});
const advance=(s,seconds,dt=.05)=>{for(let left=seconds;left>1e-9;left-=dt)core.tick(s,Math.min(dt,left));};
const until=(s,predicate,max=160)=>{for(let i=0;i<max*20;i++){if(predicate(s))return;core.tick(s,.05);}assert.ok(predicate(s),`Timed out in ${s.phase}; ${core.status(s).creeps} live creeps.`);};
const tower=(kind,cx,cz,level=1,owner=undefined)=>({kind,cx,cz,level,...(owner===undefined?{}:{owner})});
function shortMap(){const m=plain(core.mapDefault());for(const r of m.routes){const mirror=z=>r.team?50-z:z;r.spawn={x:3,z:mirror(3)};r.waypoints=[{x:6,z:mirror(3)},{x:6,z:mirror(4)}];r.exit={...r.waypoints.at(-1)};m.reserved.push(r.spawn,...r.waypoints);}return m;}

{
  const m=core.mapDefault(),check=core.preflight(m);assert.equal(check.ok,true);assert.equal(m.cols,49);assert.equal(m.rows,51);assert.equal(m.cell,2);assert.equal(m.sectors.length,6);assert.equal(m.routes.length,2);
  for(const p of m.blocked)assert.ok(m.blocked.some(q=>q.x===p.x&&q.z===50-p.z));
  assert.equal(m.blocked.filter(p=>p.z===25).length,49);assert.equal(m.routes[0].waypoints.length,6);
  assert.deepEqual(plain(m.routes[1].waypoints),plain(m.routes[0].waypoints.map(p=>({x:p.x,z:50-p.z}))));
  for(const r of m.routes){let last=-1;for(const p of r.waypoints){const at=check.paths[r.team].findIndex((q,i)=>i>last&&q.x===p.x&&q.z===p.z);assert.ok(at>last);last=at;}assert.deepEqual(plain(check.paths[r.team].at(-1)),{...plain(r.exit),stage:6});}
  assert.deepEqual(plain(core.cellToWorld(m,24,25)),{x:0,z:0});assert.deepEqual(plain(core.worldToCell(m,-42,-44)),{x:3,z:3});
  pass('mirrored_six_sector_horseshoe_routes_cliff_islands_and_two_ships');
}
{
  const m=core.mapDefault();assert.equal(core.slotAt(m,3,3),0);assert.equal(core.slotAt(m,45,3),1);assert.equal(core.slotAt(m,24,20),2);assert.equal(core.slotAt(m,3,47),3);assert.equal(core.slotAt(m,45,47),4);assert.equal(core.slotAt(m,24,30),5);assert.equal(core.slotAt(m,24,25),null);assert.equal(core.slotAt(m,-1,3),null);
  const air=core.route(m,[tower('maze-wall',4,3)],m.routes[0].spawn,0,true);assert.equal(air.length,7);assert.deepEqual(plain(air[1]),{x:45,z:3,stage:1});
  const ground=core.route(m,[tower('maze-wall',4,3)],m.routes[0].spawn,0);assert.ok(ground);assert.equal(ground.some(p=>p.x===4&&p.z===3),false);
  for(let i=1;i<ground.length;i++)assert.equal(Math.abs(ground[i].x-ground[i-1].x)+Math.abs(ground[i].z-ground[i-1].z),1);
  const partial=core.route(m,[],{x:45,z:12},0,false,1);assert.equal(partial.some(p=>p.x===45&&p.z===3),false);assert.equal(partial.at(-1).stage,6);
  pass('sector_ownership_cardinal_ground_routes_and_ordered_air_turns');
}
{
  const m=core.mapDefault();assert.equal(core.preflight(m,[tower('arrow',3,3)]).ok,false);assert.equal(core.preflight(m,[tower('arrow',12,10)]).ok,false);assert.equal(core.preflight(m,[tower('unknown',4,4)]).ok,false);assert.equal(core.preflight(m,[tower('arrow',4,4,4)]).ok,false);assert.equal(core.preflight(m,[tower('arrow',4,4,1,1)]).ok,false);assert.equal(core.preflight(m,[tower('arrow',4,4),tower('frost',4,4)]).ok,false);
  assert.equal(core.preflight({...plain(m),blocked:{}}).ok,false);assert.equal(core.preflight({...plain(m),reserved:null}).ok,false);
  const broken=plain(m);broken.routes[0].waypoints[0]={x:45,z:47};broken.reserved.push({x:45,z:47});assert.equal(core.preflight(broken).ok,false);
  assert.throws(()=>fresh({},[{...tower('arrow',4,4),id:'same'},{...tower('arrow',5,4),id:'same'}]),/unique IDs/);
  assert.equal(core.preflight(shortMap()).ok,true,'Stopped editor fixtures may shorten ordered routes while keeping team ownership.');
  pass('authored_preflight_rejects_protected_cliffs_overlap_ownership_and_invalid_routes');
}
{
  for(const value of [{lives:0},{startIncome:-1},{preparation:181},{difficulty:5},{incomeInterval:4},{selectedSector:3},{seed:-1},{opponentAI:'yes'},{soloSupport:1}])assert.equal(core.validateRules(value).ok,false);
  assert.equal(core.validateRules(null).ok,false);assert.equal(core.validateRules({lives:1,preparation:0,startGold:0,incomeInterval:5,soloSupport:false,opponentAI:false}).ok,true);
  const clean=core.cleanRules({lives:0,opponentAI:'yes',startIncome:60});assert.equal(clean.lives,25);assert.equal(clean.opponentAI,true);assert.equal(clean.startIncome,60);assert.throws(()=>fresh({selectedSector:3}),/selectedSector/);
  pass('bounded_rules_and_strict_ai_toggles_are_validated_before_match_creation');
}
{
  const s=fresh({startGold:20}),original=JSON.stringify(s);for(const [x,z,code] of [[0,4,'wall'],[3,3,'reserved'],[45,4,'territory'],[-1,3,'outside']]){assert.equal(core.build(s,'arrow',x,z).code,code);assert.equal(JSON.stringify(s),original);}
  const made=core.build(s,'arrow',4,4);assert.equal(made.ok,true);assert.equal(made.tower.owner,0);assert.equal(made.tower.team,0);assert.equal(s.players[0].gold,0);assert.equal(s.players[1].gold,20);assert.equal(core.build(s,'maze-wall',4,4).code,'occupied');assert.equal(core.build(s,'maze-wall',5,4).code,'gold');
  const other=core.build(s,'arrow',44,4,1);assert.equal(other.ok,true);assert.equal(s.players[1].gold,0);assert.equal(other.tower.owner,1);assert.equal(core.canBuild(s,'arrow',44,46,1).code,'territory');
  pass('construction_is_transactional_and_charges_only_the_territory_owner');
}
{
  const s=fresh({startGold:10000});for(let x=1;x<48;x++){if(x===24)continue;assert.equal(core.build(s,'maze-wall',x,4,core.slotAt(s.map,x,4)).ok,true);}
  const before=JSON.stringify(s),closed=core.build(s,'maze-wall',24,4,1);assert.equal(closed.code,'blocked');assert.equal(JSON.stringify(s),before);assert.equal(core.preflight(s.map,s.towers).ok,true);
  pass('last_maze_gap_cannot_block_either_ordered_team_route');
}
{
  const s=fresh({startGold:200}),made=core.build(s,'arrow',4,4).tower;assert.equal(core.upgrade(s,made.id,1).code,'owner');assert.equal(core.sell(s,made.id,1).code,'owner');assert.equal(core.setPriority(s,made.id,'strong',1).code,'owner');assert.equal(core.upgrade(s,made.id).ok,true);assert.equal(core.upgrade(s,made.id).ok,true);assert.equal(made.level,3);assert.equal(made.spent,120);assert.equal(s.players[0].gold,80);assert.equal(core.upgrade(s,made.id).code,'maximum');assert.equal(core.setPriority(s,made.id,'strong').ok,true);assert.equal(core.setPriority(s,made.id,'bad').code,'priority');assert.equal(core.sell(s,made.id).refund,84);assert.equal(s.players[0].gold,164);assert.equal(s.players[1].gold,200);
  const ids=fresh({},[{...tower('arrow',4,4),id:'wars-tower-8'}]);assert.equal(core.build(ids,'arrow',5,4).tower.id,'wars-tower-9');
  pass('private_upgrade_budgets_target_priorities_refunds_and_authored_id_safety');
}
{
  const waiting=fresh({preparation:2,startGold:100}),before=JSON.stringify(waiting);assert.equal(core.send(waiting,'wisp').code,'preparation');assert.equal(JSON.stringify(waiting),before);advance(waiting,2);assert.equal(waiting.phase,'battle');
  for(const [kind,id,count,code] of [['none',0,1,'kind'],['wisp',6,1,'player'],['wisp',0,0,'count'],['wisp',0,9,'count'],['siege',0,1,'gold']]){const snapshot=JSON.stringify(waiting);assert.equal(core.send(waiting,kind,id,count).code,code);assert.equal(JSON.stringify(waiting),snapshot);}
  assert.equal(core.send(waiting,'brute',0,2).ok,true);assert.equal(waiting.players[0].gold,20);assert.equal(waiting.players[0].income,31);assert.equal(waiting.spawnQueue.length,2);assert.equal(waiting.spawnQueue[0].defendTeam,1);assert.equal(waiting.spawnQueue[0].sourcePlayer,0);assert.ok(Math.abs(waiting.spawnQueue[1].at-waiting.spawnQueue[0].at-.55)<1e-9);assert.equal(waiting.units.length,0);
  const e=waiting.events.at(-1);assert.equal(e.type,'sent');assert.equal(e.details.incomeGain,6);assert.equal(e.details.cost,80);
  pass('sending_opens_after_preparation_charges_gold_and_permanently_raises_income');
}
{
  const s=fresh({startGold:100,startIncome:10,incomeInterval:5});assert.equal(core.send(s,'wisp',0,2).ok,true);advance(s,4.95);assert.equal(s.players[0].gold,70);advance(s,.05);assert.equal(s.players[0].gold,82);assert.equal(s.players[1].gold,110);advance(s,5);assert.equal(s.players[0].gold,94);assert.equal(s.players[1].gold,120);
  const payments=s.events.filter(e=>e.type==='income-paid');assert.equal(payments.length,12);assert.deepEqual(plain(payments.filter(e=>e.details.player===0).map(e=>e.details.amount)),[12,12]);assert.ok(Math.abs(s.incomeTimer-5)<1e-7);
  pass('recurring_income_pays_all_six_wallets_exactly_on_the_shared_timer');
}
{
  const s=fresh();core.send(s,'wisp',3);advance(s,.25);const u=s.units.find(u=>u.alive);assert.equal(u.defendTeam,0);assert.equal(u.sourcePlayer,3);assert.equal(u.stage,0);
  const before=JSON.stringify(s);assert.equal(core.build(s,'maze-wall',4,3).code,'creep');assert.equal(JSON.stringify(s),before);assert.equal(core.build(s,'maze-wall',5,3).ok,true);
  const trapped=fresh({startGold:10000});core.send(trapped,'wisp',3);advance(trapped,1.4);const live=trapped.units[0];assert.equal(live.cx,5);assert.equal(live.cz,3);
  for(const [x,z] of [[5,2],[5,4],[4,3]])assert.equal(core.build(trapped,'maze-wall',x,z).ok,true);const snap=JSON.stringify(trapped);assert.equal(core.build(trapped,'maze-wall',6,3).code,'trapped');assert.equal(JSON.stringify(trapped),snap);assert.equal(core.preflight(trapped.map,[...trapped.towers,tower('maze-wall',6,3)]).ok,true);
  pass('physical_creep_footprints_and_active_creep_enclosures_reject_without_charge');
}
{
  const s=fresh();core.send(s,'wisp',3);advance(s,34);const u=s.units.find(u=>u.alive);assert.equal(u.stage,1);assert.equal(u.cx,45);assert.ok(u.cz>3&&u.cz<20);const position={x:u.x,z:u.z};
  assert.equal(core.build(s,'maze-wall',45,15,1).ok,true);assert.equal(u.stage,1);assert.equal(u.x,position.x);assert.equal(u.z,position.z);assert.equal(u.path.some(p=>p.x===45&&p.z===3),false);assert.equal(u.path.some(p=>p.x===45&&p.z===15),false);
  let stage=u.stage;for(let i=0;i<20*30&&u.alive;i++){core.tick(s,.05);assert.ok(u.stage>=stage);stage=u.stage;const clearance=.95+.45;for(const t of s.towers){const p=core.cellToWorld(s.map,t.cx,t.cz);assert.ok(Math.abs(u.x-p.x)>clearance||Math.abs(u.z-p.z)>clearance);}}
  assert.equal(core.sell(s,s.towers[0].id,1).ok,true);assert.ok(u.stage>=1);assert.equal(u.path.some(p=>p.x===45&&p.z===3),false);
  pass('live_rerouting_preserves_continuous_pose_and_completed_turns_without_tunneling');
}
{
  const s=fresh({},[tower('cannon',4,4,3,0)],shortMap());core.send(s,'flyer',3);advance(s,.2);const u=s.units[0];assert.equal(u.air,true);const hp=u.hp;advance(s,.5);assert.equal(u.hp,hp);assert.equal(s.shots.length,0);
  const airPath=plain(u.path);assert.equal(core.build(s,'maze-wall',4,3).ok,true);assert.deepEqual(plain(u.path),airPath);until(s,x=>x.teams[0].leaks===1,8);assert.equal(u.stage,2);
  pass('air_creeps_ignore_ground_maze_walls_and_ground_only_cannons');
}
{
  const m=shortMap(),s=fresh({},[tower('arrow',4,4,3,0),tower('arrow',4,46,3,3)],m);const g0=s.players[0].gold,g3=s.players[3].gold;core.send(s,'wisp',3);core.send(s,'wisp',0);advance(s,.1);
  assert.equal(s.teams[0].kills,1);assert.equal(s.teams[1].kills,1);assert.equal(s.players[0].gold,g0-15+3);assert.equal(s.players[3].gold,g3-15+3);assert.equal(s.teams[0].lives,25);assert.equal(s.teams[1].lives,25);
  for(const e of s.events.filter(e=>e.type==='killed'))assert.equal(s.towers.find(t=>t.id===e.details.towerId).team,e.details.defendTeam);
  assert.ok(s.shots.length>=2);for(const shot of s.shots)assert.equal(s.units.find(u=>u.id===shot.targetId).defendTeam,shot.team);
  pass('tower_damage_and_kill_bounties_are_restricted_to_each_defending_team');
}
{
  // Two native authored routes alongside the divider deliberately overlap
  // attack radii. Real spawned creeps must still remain on separate teams.
  for(const kind of ['storm','cannon']){
    const m=plain(core.mapDefault());for(const r of m.routes){const z=r.team?26:24;r.spawn={x:4,z};r.waypoints=[{x:6,z},{x:8,z}];r.exit={...r.waypoints.at(-1)};m.reserved.push(r.spawn,...r.waypoints);}
    const s=fresh({},[tower(kind,4,23,3,2)],m);core.send(s,'brute',0);core.send(s,'brute',3);advance(s,.1);const own=s.units.find(u=>u.defendTeam===0),opponent=s.units.find(u=>u.defendTeam===1);
    assert.ok(own.hp<own.maxHp);assert.equal(opponent.hp,opponent.maxHp);assert.equal(s.shots.some(v=>v.targetId===opponent.id),false);
  }
  pass('chain_and_splash_candidate_filters_do_not_attack_the_other_team');
}
{
  const s=fresh();core.send(s,'siege',3);advance(s,.2);const u=s.units[0];assert.equal(u.armor,25);assert.equal(u.boss,true);assert.equal(u.maxHp,450);assert.equal(u.bounty,18);
  assert.equal(core.build(s,'frost',4,4).ok,true);advance(s,.1);assert.ok(u.hp<u.maxHp);assert.ok(u.slowUntil>s.elapsed);assert.equal(u.slowFactor,.55);const expected=450-7*100/125;assert.ok(Math.abs(u.hp-expected)<1e-8);
  core.sell(s,s.towers[0].id);advance(s,2.2);assert.equal(u.slowFactor,1);assert.equal(u.slowUntil,0);
  pass('armored_siege_damage_frost_slow_and_expiry_use_real_combat_rules');
}
{
  const win=fresh({lives:1},[],shortMap());core.send(win,'wisp',0);until(win,s=>s.phase==='won',8);assert.equal(win.winner,0);assert.equal(win.teams[1].lives,0);assert.equal(win.teams[0].lives,1);assert.equal(win.events.filter(e=>e.type==='won').length,1);
  const seal=JSON.stringify(win);advance(win,3);assert.equal(JSON.stringify(win),seal);assert.equal(core.build(win,'arrow',4,4).code,'finished');assert.equal(core.send(win,'wisp').code,'finished');
  const loss=fresh({lives:1},[],shortMap());core.send(loss,'wisp',3);until(loss,s=>s.phase==='lost',8);assert.equal(loss.winner,1);assert.equal(loss.teams[0].lives,0);assert.equal(loss.events.filter(e=>e.type==='lost').length,1);const sealed=JSON.stringify(loss);advance(loss,2);assert.equal(JSON.stringify(loss),sealed);
  pass('shared_team_lives_winners_and_terminal_clocks_freeze_exactly_once');
}
{
  const s=fresh({startGold:100000,startIncome:0});for(let i=0;i<7;i++)assert.equal(core.send(s,'wisp',0,8).ok,true);assert.equal(core.send(s,'wisp',0,4).ok,true);const before=JSON.stringify(s);assert.equal(core.send(s,'wisp',0).code,'capacity');assert.equal(JSON.stringify(s),before);assert.equal(s.players[0].income,60);
  for(let id=1;id<4;id++){for(let i=0;i<7;i++)assert.equal(core.send(s,'wisp',id,8).ok,true);assert.equal(core.send(s,'wisp',id,4).ok,true);}assert.equal(s.spawnQueue.length,240);const full=JSON.stringify(s);assert.equal(core.send(s,'flyer',4).code,'capacity');assert.equal(JSON.stringify(s),full);
  pass('send_capacity_limits_are_bounded_and_failed_sends_do_not_grant_income');
}
{
  const off=fresh({preparation:1});advance(off,35);assert.equal(off.towers.length,0);assert.equal(off.spawnQueue.length+off.units.length,0);assert.equal(off.events.filter(e=>e.type==='sent').length,0);
  const on=fresh({preparation:1,soloSupport:true,opponentAI:true});advance(on,35);assert.equal(on.players.filter(p=>p.ai).length,5);assert.equal(on.players[0].gold,475);assert.equal(on.towers.some(t=>t.owner===0),false);
  for(let id=1;id<6;id++){assert.ok(on.towers.some(t=>t.owner===id));assert.ok(on.events.some(e=>e.type==='sent'&&e.details.sourcePlayer===id));assert.ok(on.players[id].income>25);}
  for(const t of on.towers){assert.equal(t.owner,core.slotAt(on.map,t.cx,t.cz));assert.equal(t.team,Math.floor(t.owner/3));}assert.equal(core.preflight(on.map,on.towers).ok,true);
  assert.ok(on.units.some(u=>u.defendTeam===0));assert.ok(on.units.some(u=>u.defendTeam===1));assert.ok(on.towers.some(t=>t.level>1));assert.ok(on.events.some(e=>e.type==='upgraded'));
  pass('optional_ai_builds_upgrades_and_sends_with_five_private_wallets');
}
{
  const a=fresh({preparation:2,soloSupport:true,opponentAI:true,seed:913}),b=fresh({preparation:2,soloSupport:true,opponentAI:true,seed:913});core.build(a,'arrow',4,4);core.build(b,'arrow',4,4);advance(a,40,.05);advance(b,40,.1);assert.deepEqual(rounded(a),rounded(b));
  const before=JSON.stringify(a);for(const dt of [0,-1,NaN,Infinity])core.tick(a,dt);assert.equal(JSON.stringify(a),before);const limited=fresh();core.tick(limited,20);assert.ok(Math.abs(limited.elapsed-1)<1e-8);
  const seq=a.events.map(e=>e.seq);assert.equal(new Set(seq).size,seq.length);for(let i=1;i<a.events.length;i++)assert.ok(a.events[i].t>=a.events[i-1].t);assert.equal(new Set([...a.towers,...a.units,...a.shots].map(v=>v.id)).size,a.towers.length+a.units.length+a.shots.length);
  pass('deterministic_fixed_steps_monotonic_event_times_and_unique_runtime_ids');
}
console.log(`MAUL_WARS_CPU_ALL_CASES_PASS ${cases}`);
