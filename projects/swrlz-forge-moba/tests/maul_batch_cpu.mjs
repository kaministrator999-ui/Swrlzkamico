import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const directory=path.dirname(fileURLToPath(import.meta.url));
const sealedPath=process.env.SWYRL_MAUL_BATCH_HTML;
const input=sealedPath?fs.readFileSync(sealedPath,'utf8'):['maul_core.js','maul_layout_core.js','maul_batch_core.js'].map(name=>fs.readFileSync(path.join(directory,'../runtime',name),'utf8')).join('\n');
const extract=name=>{const begin=input.indexOf(`const ${name} = (() => {`),end=input.indexOf(`// ${name}_END`,begin);assert.ok(begin>=0&&end>begin,`Executed source must contain ${name}.`);return input.slice(begin,end);};
const context=vm.createContext({});
vm.runInContext(['MAUL_CORE','MAUL_LAYOUT_CORE','MAUL_BATCH_CORE'].map(extract).join('\n')+'\nglobalThis.core=MAUL_CORE;globalThis.layout=MAUL_LAYOUT_CORE;globalThis.batch=MAUL_BATCH_CORE;',context,{timeout:2000});
const {core,layout,batch}=context;
if(sealedPath)console.log(`MAUL_BATCH_CPU_SOURCE_SHA256 ${crypto.createHash('sha256').update(input).digest('hex')}`);
else console.log('MAUL_BATCH_CPU_DEVELOPMENT_ONLY Unsealed modules do not establish native integration proof.');
let cases=0;const pass=name=>{cases++;console.log(`MAUL_BATCH_CPU_CASE_PASS ${name}`);};
const plain=value=>JSON.parse(JSON.stringify(value));
const rounded=value=>JSON.parse(JSON.stringify(value,(_,v)=>typeof v==='number'?Math.round(v*1e9)/1e9:v));
const key=p=>`${p.x},${p.z}`;
const fresh=(rules={},map=batch.mapDefault(),towers=[])=>batch.createSession({rules:{soloSupport:false,autoWaves:false,...rules},map,towers});
const advance=(s,seconds)=>{for(let left=seconds;left>1e-9;left-=.05)core.tick(s,Math.min(.05,left));};
const runUntil=(s,predicate,max=180)=>{for(let i=0;i<max*20;i++){if(predicate(s))return;core.tick(s,.05);}assert.ok(predicate(s),`Timed out in ${s.phase}, wave ${s.wave}, queued ${batch.queued(s)}.`);};
const spawned=s=>s.events.filter(e=>e.type==='spawned');
const groups=s=>s.events.filter(e=>e.type==='spawn-group');
const fixtureEvent=(s,type,details)=>{const e={seq:++s.eventSeq,t:s.elapsed,type,details};s.events.push(e);return e;};
const fixtureSpawn=(s,item)=>{const p=core.cellToWorld(s.map,item.spawn),u={id:`fixture-${++s.idSeq}`,sector:item.sector,x:p.x,z:p.z,boss:item.boss,alive:true};s.units.push(u);fixtureEvent(s,'spawned',{id:u.id,sector:item.sector});};

{
  const s=fresh();
  for(const wave of [1,3,5,10,25,27,30]){
    s.wave=wave;const boss=wave%10===0,air=wave%5===0&&!boss,count=boss?5:air?6+Math.floor(wave/6):Math.min(16,6+Math.floor(wave/3));
    const queue=batch.schedule(s,count,air,boss);
    assert.deepEqual(plain(queue.map(g=>g.at)),[0,2.5,5]);assert.deepEqual(plain(queue.map(g=>g.group)),[1,2,3]);
    assert.equal(batch.queued({spawnQueue:queue}),count*9);
    for(let sector=0;sector<9;sector++){
      const members=queue.flatMap(g=>g.members).filter(m=>m.sector===sector);
      assert.deepEqual(plain(members.map(m=>m.index)),Array.from({length:count},(_,i)=>i));
      assert.equal(members.filter(m=>m.boss).length,boss?1:0);assert.ok(members.every(m=>m.air===air));
      assert.ok(queue.every(g=>g.members.filter(m=>m.sector===sector).length>=1));
      if(boss)assert.equal(members.at(-1).boss,true);
    }
  }
  pass('three_group_schedule_preserves_every_sector_count_and_ground_air_boss_round');
}
{
  const map=batch.mapDefault(),walls=new Set(map.blocked.map(key)),reserved=new Set(map.reserved.map(key));
  assert.equal(map.layout,'classic-v2');assert.equal(map.spawnStyle,'grouped-v1');assert.equal(map.spawnAreas.length,9);
  assert.equal(batch.preflight(map).ok,true);
  for(const spawn of map.spawns){
    const cells=batch.spawnCells(map,spawn),sector=map.sectors[spawn.sector];assert.ok(cells.length>=6&&cells.length<=25);
    assert.equal(new Set(cells.map(key)).size,cells.length);
    for(const cell of cells){assert.ok(Math.abs(cell.x-spawn.x)<=2&&Math.abs(cell.z-spawn.z)<=2);assert.ok(cell.x>=sector.minX&&cell.x<=sector.maxX&&cell.z>=sector.minZ&&cell.z<=sector.maxZ);assert.equal(walls.has(key(cell)),false);assert.equal(reserved.has(key(cell)),true);assert.ok(layout.route(map,[],cell,spawn.sector));}
  }
  const s=fresh();for(const p of batch.spawnCells(s.map,s.map.spawns[0]))assert.equal(core.build(s,'arrow',p.x,p.z).code,'reserved');
  const legacy=layout.mapDefault(),before=JSON.stringify(legacy);batch.reserveAreas(legacy);assert.equal(JSON.stringify(legacy),before);
  pass('scatter_areas_are_open_routable_clipped_and_reserved_only_on_grouped_maps');
}
{
  const map=batch.mapDefault(),spawn=map.spawns[0],cells=batch.spawnCells(map,spawn),keep=new Set([key(spawn),...cells.filter(p=>key(p)!==key(spawn)).slice(0,4).map(key)]);
  for(const p of cells)if(!keep.has(key(p)))map.blocked.push({...p});
  const check=batch.preflight(map);assert.equal(check.ok,false);assert.ok(check.errors.some(e=>e.includes('at least six')));
  assert.throws(()=>fresh({},map),/six clear, routable cells/);
  const edited=batch.mapDefault();edited.spawns[0]={x:7,z:2,sector:0};edited.sectors[0].spawn={x:7,z:2};layout.withGates(edited);batch.reserveAreas(edited);
  assert.equal(batch.preflight(edited).ok,true);assert.ok(edited.spawnAreas[0].cells.every(p=>p.z<=4));
  pass('authored_spawn_edits_recompute_scatter_and_reject_insufficient_clear_space');
}
{
  const a=fresh({seed:31}),b=fresh({seed:31}),c=fresh({seed:32});
  for(const s of [a,b,c]){s.wave=1;s.spawnQueue=batch.schedule(s,6,false,false);s.waveElapsed=.05;assert.equal(batch.spawnDue(s,fixtureSpawn,fixtureEvent),1);}
  assert.deepEqual(plain(a),plain(b));assert.notDeepEqual(plain(a.units.map(u=>u.spawnOrigin)),plain(c.units.map(u=>u.spawnOrigin)));
  const coords=a.units.map(u=>u.spawnOrigin);assert.equal(new Set(coords.map(key)).size,coords.length);
  for(let sector=0;sector<9;sector++){const units=a.units.filter(u=>u.sector===sector);assert.equal(units.length,2);assert.ok(Math.hypot(units[0].x-units[1].x,units[0].z-units[1].z)>=4,'Small groups spread visibly across the entrance.');}
  assert.equal(groups(a)[0].details.count,18);assert.equal(new Set(spawned(a).map(e=>e.t)).size,1);
  pass('seeded_atomic_scatter_spreads_units_without_sharing_spawn_cells');
}
{
  const s=fresh();s.wave=1;s.spawnQueue=batch.schedule(s,6,false,false);s.waveElapsed=.05;
  const spawn=s.map.spawns[7];for(const p of batch.spawnCells(s.map,spawn)){const world=core.cellToWorld(s.map,p);s.units.push({id:`blocking-${key(p)}`,x:world.x,z:world.z,alive:true});}
  const before=JSON.stringify(s);assert.equal(batch.spawnDue(s,fixtureSpawn,fixtureEvent),0);assert.equal(JSON.stringify(s),before,'A congested sector causes no partial arrivals or queue loss.');assert.equal(batch.queued(s),54);
  for(const u of s.units)u.alive=false;assert.equal(batch.spawnDue(s,fixtureSpawn,fixtureEvent),1);assert.equal(spawned(s).length,18);assert.equal(batch.queued(s),36);
  assert.equal(groups(s)[0].details.group,1);assert.equal(groups(s)[0].details.at,0);
  pass('congestion_defers_a_whole_group_without_partial_spawn_or_count_loss');
}
{
  assert.equal(batch.groups,3);assert.equal(batch.groupInterval,2.5);assert.equal(core.defaults.waves,30);assert.equal(core.defaults.startGold,900);
  assert.equal(layout.definitions,core.definitions);assert.equal(layout.defaults,core.defaults);assert.equal(core.definitions.arrow.cost,20);assert.equal(core.definitions['maze-wall'].cost,5);
  const s=fresh();assert.equal(s.towers.length,0);assert.equal(s.gold,900);assert.equal(s.units.length,0);
  const built=core.build(s,'arrow',7,11);assert.equal(built.ok,true);assert.equal(s.gold,880);assert.equal(built.tower.owner,'player');
  pass('grouped_arrivals_keep_existing_prices_combat_rules_and_empty_player_start');
}
if(sealedPath){
  {
    const s=fresh({lives:200});assert.equal(core.startWave(s).ok,true);assert.equal(core.status(s).queued,54);assert.equal(s.spawnQueue.length,3);assert.equal(s.units.length,0);
    assert.equal(s.events.find(e=>e.type==='wave-started').details.count,54,'Wave logs count minions rather than queue records.');
    advance(s,.05);assert.equal(spawned(s).length,18);assert.equal(groups(s).length,1);assert.equal(core.status(s).queued,36);
    assert.equal(new Set(spawned(s).map(e=>e.t)).size,1);assert.ok(spawned(s).every(e=>e.details.group===1));
    for(let sector=0;sector<9;sector++)assert.equal(s.units.filter(u=>u.sector===sector).length,2);
    for(const u of s.units){assert.equal(u.stage,0);assert.equal(u.spawnGroup,1);assert.equal(u.spawnIndex===0||u.spawnIndex===1,true);assert.ok(u.path.every(p=>Number.isInteger(p.stage)));assert.deepEqual(plain({x:u.path[0].x,z:u.path[0].z}),plain(u.spawnOrigin));assert.equal(u.hp,Math.round(24*Math.pow(1.12,1.4)));}
    pass('sealed_first_group_spawns_all_nine_sectors_in_one_native_simulation_tick');
  }
  {
    const s=fresh({lives:200});core.startWave(s);advance(s,2.45);assert.equal(spawned(s).length,18);assert.equal(groups(s).length,1);
    advance(s,.05);assert.equal(spawned(s).length,36);assert.equal(groups(s).length,2);assert.equal(core.status(s).queued,18);
    advance(s,2.45);assert.equal(spawned(s).length,36);advance(s,.05);assert.equal(spawned(s).length,54);assert.equal(groups(s).length,3);assert.equal(core.status(s).queued,0);
    const times=groups(s).map(e=>e.t);assert.ok(times[1]-times[0]>=2.4&&times[2]-times[1]>=2.4);
    for(let g=1;g<=3;g++){const events=spawned(s).filter(e=>e.details.group===g);assert.equal(events.length,18);assert.equal(new Set(events.map(e=>e.t)).size,1);assert.equal(new Set(events.map(e=>`${e.details.cx},${e.details.cz}`)).size,18);}
    pass('sealed_round_uses_three_shortly_separated_batches_with_no_individual_drip');
  }
  {
    const a=fresh({seed:77,lives:200}),b=fresh({seed:77,lives:200});core.startWave(a);core.startWave(b);
    advance(a,5.2);for(let i=0;i<20;i++)core.tick(b,.25);core.tick(b,.2);assert.deepEqual(rounded(a),rounded(b));
    const restored=plain(a);advance(a,2);advance(restored,2);assert.deepEqual(plain(a),plain(restored));
    for(const e of spawned(a))assert.ok(Number.isInteger(e.details.group)&&Number.isInteger(e.details.cx)&&Number.isInteger(e.details.cz));
    pass('sealed_grouped_schedule_and_scatter_survive_json_restore_and_clock_partition');
  }
  {
    for(const wave of [5,10,25,27,30]){
      const s=fresh({lives:200});s.wave=wave-1;assert.equal(core.startWave(s).ok,true);advance(s,5.05);
      const events=spawned(s),boss=wave%10===0,air=wave%5===0&&!boss,count=boss?5:air?6+Math.floor(wave/6):Math.min(16,6+Math.floor(wave/3));
      assert.equal(events.length,count*9);assert.equal(groups(s).length,3);assert.equal(events.filter(e=>e.details.boss).length,boss?9:0);assert.ok(events.every(e=>e.details.air===air));
      if(boss)assert.ok(events.filter(e=>e.details.boss).every(e=>e.details.group===3&&e.details.index===4));
      for(const u of s.units)assert.equal(u.maxHp,Math.round(24*Math.pow(1+.12*wave,1.4)*(u.boss?6:1)*(u.air?.9:1)));
    }
    pass('sealed_ground_air_and_boss_batches_preserve_original_counts_health_and_final_boss');
  }
  {
    const s=fresh({lives:200});core.startWave(s);advance(s,.05);const u=s.units.find(u=>u.sector===0),position={x:u.x,z:u.z},origin=plain(u.spawnOrigin);
    const wall=core.build(s,'maze-wall',7,11);assert.equal(wall.ok,true);assert.equal(u.x,position.x);assert.equal(u.z,position.z);assert.equal(u.stage,0);assert.deepEqual(plain(u.spawnOrigin),origin);assert.ok(u.path.every(p=>p.stage>=0));assert.equal(u.path.some(p=>p.x===7&&p.z===11),false);
    assert.equal(core.sell(s,wall.tower.id).ok,true);runUntil(s,()=>u.alive&&u.stage===6,180);const returned={x:u.x,z:u.z};
    const second=core.build(s,'maze-wall',15,37);assert.equal(second.ok,true);assert.equal(u.x,returned.x);assert.equal(u.z,returned.z);assert.equal(u.stage,6);assert.ok(u.path.every(p=>p.stage>=6));assert.equal(u.path.some(p=>p.x===10&&p.z===39),false);
    pass('scattered_creeps_begin_at_stage_zero_and_keep_completed_turns_during_construction');
  }
  {
    for(const map of [core.mapDefault(),layout.mapDefault()]){
      const s=core.createSession({rules:{soloSupport:false,autoWaves:false,lives:200},map});core.startWave(s);assert.equal(s.spawnQueue.length,54);assert.ok(s.spawnQueue.every(item=>!item.members));
      advance(s,.05);assert.equal(spawned(s).length,6);assert.equal(groups(s).length,0);assert.ok(spawned(s).every(e=>e.details.group===undefined));
      advance(s,.45);assert.equal(spawned(s).length,12);assert.equal(core.status(s).queued,42);assert.ok(s.units.every(u=>u.spawnGroup===undefined));
    }
    pass('published_unflagged_maul_projects_keep_their_original_single_creep_schedule');
  }
  {
    const s=batch.createSession({rules:{autoWaves:false}});
    assert.equal(s.towers.filter(t=>t.owner==='player').length,0);
    assert.deepEqual(plain([...new Set(s.towers.map(t=>t.owner))].sort()),Array.from({length:8},(_,i)=>'ally-'+(i+1)));
    assert.equal(s.towers.length,16);assert.equal(batch.preflight(s.map,s.towers).ok,true);
    for(const t of s.towers)assert.equal(s.map.spawnAreas.some(area=>area.cells.some(c=>c.x===t.cx&&c.z===t.cz)),false);
    pass('grouped_spawn_reservations_preserve_all_eight_auto_defenders_and_empty_selected_player');
  }
  {
    const map=batch.mapDefault();for(const x of [4,6,8,9])for(let z=2;z<=5;z++)map.blocked.push({x,z});batch.reserveAreas(map);
    assert.equal(batch.preflight(map).ok,true);const s=fresh({},map),before=JSON.stringify(s),fit=core.canBuild(s,'maze-wall',5,6);
    assert.equal(fit.ok,false);assert.ok(fit.errors.some(error=>/six clear/.test(error)));assert.equal(JSON.stringify(s),before);
    assert.equal(core.build(s,'maze-wall',5,6).ok,false);assert.equal(s.gold,900);assert.equal(s.towers.length,0);
    pass('construction_cannot_reduce_routable_scatter_capacity_below_a_full_later_group');
  }
  {
    const s=batch.createSession({rules:{preparation:0,intermission:0}});
    for(const [kind,cx,cz] of [['arrow',6,17],['storm',8,17],['arrow',19,40],['arrow',21,40],['frost',20,39]]){
      const built=core.build(s,kind,cx,cz);assert.equal(built.ok,true,built.reason);while(built.tower.level<3)assert.equal(core.upgrade(s,built.tower.id).ok,true);
    }
    runUntil(s,q=>q.phase==='won'||q.phase==='lost',3600);assert.equal(s.phase,'won');assert.equal(s.wave,30);assert.ok(s.lives>0);assert.ok(s.kills>1000);assert.equal(groups(s).length,90);assert.equal(s.events.filter(e=>e.type==='wave-cleared').length,30);assert.equal(s.events.filter(e=>e.type==='won').length,1);
    assert.ok(spawned(s).some(e=>e.details.air));assert.ok(spawned(s).some(e=>e.details.boss));const final=JSON.stringify(s);core.tick(s,1);assert.equal(JSON.stringify(s),final);
    pass('grouped_cooperative_campaign_can_win_all_thirty_rounds_without_losing_any_batches');
  }
}
console.log(`MAUL_BATCH_CPU_ALL_CASES_PASS ${cases}`);
