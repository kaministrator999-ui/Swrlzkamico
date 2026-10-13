import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const testDirectory=path.dirname(fileURLToPath(import.meta.url));
const sealedPath=process.env.SWYRL_MAUL_LAYOUT_HTML;
const input=sealedPath?fs.readFileSync(sealedPath,'utf8'):[fs.readFileSync(path.join(testDirectory,'../runtime/maul_core.js'),'utf8'),fs.readFileSync(path.join(testDirectory,'../runtime/maul_layout_core.js'),'utf8')].join('\n');
const extract=name=>{const begin=input.indexOf(`const ${name} = (() => {`),end=input.indexOf(`// ${name}_END`,begin);assert.ok(begin>=0&&end>begin,`Executed source must contain ${name}.`);return input.slice(begin,end);};
const context=vm.createContext({});
vm.runInContext(extract('MAUL_CORE')+'\n'+extract('MAUL_LAYOUT_CORE')+'\nglobalThis.core=MAUL_LAYOUT_CORE;globalThis.original=MAUL_CORE;',context,{timeout:2000});
const core=context.core,original=context.original;
if(sealedPath)console.log(`MAUL_LAYOUT_CPU_SOURCE_SHA256 ${crypto.createHash('sha256').update(input).digest('hex')}`);
let cases=0;const pass=name=>{cases++;console.log(`MAUL_LAYOUT_CPU_CASE_PASS ${name}`);};
const plain=value=>JSON.parse(JSON.stringify(value));
const rounded=value=>JSON.parse(JSON.stringify(value,(_,v)=>typeof v==='number'?Math.round(v*1e9)/1e9:v));
const key=p=>`${p.x},${p.z}`;
const fresh=(rules={},towers=[])=>core.createSession({rules:{soloSupport:false,autoWaves:false,...rules},towers});
const advance=(s,seconds)=>{for(let left=seconds;left>1e-9;left-=.05)core.tick(s,Math.min(.05,left));};
const runUntil=(s,predicate,max=180)=>{for(let i=0;i<max*20;i++){if(predicate(s))return;core.tick(s,.05);}assert.ok(predicate(s),`Timed out in ${s.phase}, wave ${s.wave}, creeps ${core.status(s).creeps}.`);};
const tower=(kind,cx,cz,level=1)=>({kind,cx,cz,level,owner:'player'});

{
  const map=core.mapDefault(),check=core.preflight(map);
  assert.equal(map.cols,41);assert.equal(map.rows,45);assert.equal(map.cell,2);assert.deepEqual(plain(map.origin),{x:-40,z:-44});assert.equal(check.ok,true,check.errors.join(' '));
  assert.equal(map.layout,'classic-v2');assert.equal(map.sectors.length,9);assert.equal(map.spawns.length,9);assert.equal(new Set(map.spawns.map(p=>p.sector)).size,9);
  assert.deepEqual(plain(core.cellToWorld(map,map.exit)),{x:0,z:42});assert.deepEqual(plain(core.worldToCell(map,-26,-38)),{x:7,z:3});
  assert.equal(core.definitions,original.definitions);assert.equal(core.defaults,original.defaults);assert.equal(core.build,original.build);assert.equal(core.tick,original.tick);
  pass('classic_terrain_uses_existing_cooperative_rules_and_world_grid');
}
{
  const map=core.mapDefault(),blocked=new Set(map.blocked.map(key)),raster=new Set();
  for(const p of core.geometry())for(let z=p.cz-(p.depth-1)/2;z<=p.cz+(p.depth-1)/2;z++)for(let x=p.cx-(p.width-1)/2;x<=p.cx+(p.width-1)/2;x++){assert.ok(Number.isInteger(x)&&Number.isInteger(z));raster.add(`${x},${z}`);}
  assert.deepEqual([...raster].sort(),[...blocked].sort());assert.equal(blocked.size,map.blocked.length);
  for(let z=2;z<=19;z++)for(const x of [12,13,14,26,27,28])assert.ok(blocked.has(`${x},${z}`));
  for(const s of map.sectors.slice(0,3)){assert.ok(s.maxZ-s.minZ>s.maxX-s.minX,'North maze bays must be taller than wide.');for(let z=s.minZ;z<=s.maxZ;z++)for(let x=s.minX;x<=s.maxX;x++)assert.equal(blocked.has(`${x},${z}`),false);}
  const altered=core.geometry();altered[0].cx=999;assert.notEqual(core.geometry()[0].cx,999,'Authored callers receive their own geometry values.');
  pass('native_cliff_rectangles_match_three_long_northern_maze_bays');
}
{
  const map=core.mapDefault(),blocked=new Set(map.blocked.map(key));
  for(let z=21;z<=26;z++)for(let x=2;x<=38;x++)assert.equal(blocked.has(`${x},${z}`),false,'The middle is one broad connected crossbar.');
  assert.ok(map.sectors[6].maxX-map.sectors[6].minX>=14);assert.ok(map.sectors[8].maxX-map.sectors[8].minX>=14);
  for(const [x,z] of [[5,27],[15,27],[25,27],[35,27],[15,30],[25,30],[16,31],[24,31]])assert.ok(blocked.has(`${x},${z}`),'Stepped lower ridges remain maze boundaries.');
  for(let z=42;z<=44;z++)for(let x=2;x<=38;x++)assert.equal(blocked.has(`${x},${z}`),x<18||x>22,'Only the five-cell shared harbor aisle is open.');
  for(const p of map.reserved)assert.equal(blocked.has(key(p)),false);
  pass('broad_crossbar_lower_wings_and_shared_harbor_replace_square_compartments');
}
{
  const map=core.mapDefault();
  for(const spawn of map.spawns){const route=core.route(map,[],spawn,spawn.sector),sector=map.sectors[spawn.sector];assert.ok(route);
    let previous=-1;for(const [objective,gate] of sector.gates.entries()){const i=route.findIndex(p=>p.x===gate.x&&p.z===gate.z&&p.stage===objective+1);assert.ok(i>previous,`Sector ${sector.id} follows its downstream gates.`);previous=i;}
    assert.deepEqual(plain({x:route.at(-1).x,z:route.at(-1).z}),plain(map.exit));assert.ok(route.some(p=>p.x===20&&p.z===41),'Every stream reaches the rear catcher.');
    for(let i=1;i<route.length;i++)assert.equal(Math.abs(route[i].x-route[i-1].x)+Math.abs(route[i].z-route[i-1].z),1);
  }
  const west=core.route(map,[],map.spawns[0],0),center=core.route(map,[],map.spawns[1],1),east=core.route(map,[],map.spawns[2],2);
  assert.ok(west.length>=70);assert.ok(center.length>=75);assert.equal(west.length,east.length);
  assert.ok(west.some(p=>p.x===10&&p.z===39));assert.ok(east.some(p=>p.x===30&&p.z===39));
  pass('nine_cardinal_streams_visit_frontline_wings_rear_catcher_and_one_exit');
}
{
  const map=core.mapDefault();map.sectors[3].gate={x:9,z:26};core.withGates(map);assert.deepEqual(plain(map.sectors[0].gates[1]),{x:9,z:26});assert.ok(map.reserved.some(p=>p.x===9&&p.z===26));assert.equal(core.preflight(map).ok,true);
  const stale=core.mapDefault();stale.sectors[0].gates.pop();assert.equal(core.preflight(stale).ok,false);
  const outside=core.mapDefault();outside.sectors[6].gate.z=45;core.withGates(outside);assert.equal(core.preflight(outside).ok,false);
  const missing=core.mapDefault();missing.sectors.splice(4,1);assert.equal(core.preflight(missing).ok,false);
  pass('editable_waypoints_rebuild_chains_and_reject_missing_or_outside_defenders');
}
{
  const map=core.mapDefault(),route=core.route(map,[],map.spawns[0],0);
  const south=route.findIndex(p=>p.x===10&&p.z===39&&p.stage===5),north=route.findIndex(p=>p.x===15&&p.z===33&&p.stage===6),rear=route.findIndex(p=>p.x===20&&p.z===41&&p.stage===7);
  assert.ok(south>=0&&north>south&&rear>north,'The lower wing travels south, returns north, then joins the shared rear catcher.');
  for(let i=1;i<route.length;i++)assert.ok(route[i].stage>=route[i-1].stage&&route[i].stage-route[i-1].stage<=1);
  const resumed=core.route(map,[],{x:15,z:33},0,false,6);
  assert.equal(resumed[0].stage,6);assert.ok(resumed.every(p=>p.stage>=6));assert.equal(resumed.some(p=>p.x===10&&p.z===39),false,'Rerouting after the northward return never repeats the completed outer wing.');
  const detour=core.route(map,[tower('maze-wall',19,38)],{x:15,z:33},0,false,6);assert.ok(detour);assert.equal(detour.some(p=>p.x===19&&p.z===38),false);assert.equal(detour.at(-1).stage,8);
  const air=core.route(map,[],{x:15,z:33},0,true,6);assert.deepEqual(plain(air),[{x:15,z:33,stage:6},{x:20,z:41,stage:7},{x:20,z:43,stage:8}]);
  if(sealedPath){
    const s=fresh({waves:1,lives:200,spawnInterval:2});core.startWave(s);advance(s,.05);
    const first=s.units.find(u=>u.sector===0);assert.equal(first.stage,0,'Sealed native spawning initializes completed objectives.');assert.ok(first.path.every(p=>Number.isInteger(p.stage)),'Sealed spawning uses the stage-bearing layout route.');
    runUntil(s,()=>first.alive&&first.stage===6,160);const position={x:first.x,z:first.z};
    const built=core.build(s,'maze-wall',15,37);assert.equal(built.ok,true,built.reason);assert.equal(first.x,position.x);assert.equal(first.z,position.z);assert.equal(first.stage,6);assert.ok(first.path.every(p=>p.stage>=6));assert.equal(first.path.some(p=>p.x===10&&p.z===39),false,'Live construction does not send a returned creep through the completed wing again.');
    assert.equal(core.sell(s,built.tower.id).ok,true);assert.equal(first.stage,6);assert.ok(first.path.every(p=>p.stage>=6),'Selling preserves the same completed objectives.');
    runUntil(s,()=>!first.alive,80);assert.equal(first.stage,8);assert.ok(s.events.some(e=>e.type==='leaked'&&e.details.id===first.id));
  }
  pass('nonmonotonic_lower_wing_returns_keep_completed_stage_during_reroutes');
}
{
  const s=fresh({startGold:1000}),before=JSON.stringify(s);
  for(const p of [{x:12,z:10},{x:6,z:29},{x:15,z:43}]){assert.equal(core.build(s,'arrow',p.x,p.z).code,'wall');assert.equal(JSON.stringify(s),before);}
  for(const p of s.map.reserved){assert.equal(core.build(s,'arrow',p.x,p.z).code,'reserved');assert.equal(JSON.stringify(s),before);}
  const route=core.route(s.map,[],s.map.spawns[0],0);assert.ok(route.some(p=>p.x===7&&p.z===8));
  const built=core.build(s,'maze-wall',7,8);assert.equal(built.ok,true);assert.equal(s.gold,995);const detour=core.route(s.map,s.towers,s.map.spawns[0],0);assert.ok(detour.length>route.length);assert.equal(detour.some(p=>p.x===7&&p.z===8),false);
  const crossing=core.build(s,'arrow',20,25);assert.equal(crossing.ok,true,'Crossbar terrain supports towers.');
  pass('placement_protects_cliffs_coast_markers_and_can_maze_the_new_terrain');
}
{
  const s=fresh({startGold:1000});for(let x=2;x<=11;x++){if(x===7)continue;assert.equal(core.build(s,'maze-wall',x,8).ok,true);}
  const gold=s.gold,count=s.towers.length;assert.equal(core.build(s,'maze-wall',7,8).code,'blocked');assert.equal(s.gold,gold);assert.equal(s.towers.length,count);assert.equal(core.preflight(s.map,s.towers).ok,true);
  const harbor=fresh({startGold:1000});for(const x of [18,19,21,22])assert.equal(core.build(harbor,'maze-wall',x,42).ok,true);const before=JSON.stringify(harbor);assert.equal(core.build(harbor,'maze-wall',20,42).code,'blocked');assert.equal(JSON.stringify(harbor),before);
  pass('last_frontline_and_harbor_gaps_cannot_close_any_creep_route');
}
{
  const s=fresh({spawnInterval:2});core.startWave(s);advance(s,1.4);const creep=s.units.find(u=>u.sector===0);assert.equal(creep.cz,5);
  const before=JSON.stringify(s);assert.equal(core.build(s,'maze-wall',7,5).code,'creep');assert.equal(JSON.stringify(s),before);
  for(const [x,z] of [[6,5],[8,5],[7,4]])assert.equal(core.build(s,'maze-wall',x,z).ok,true);
  const gold=s.gold;assert.equal(core.build(s,'maze-wall',7,6).code,'trapped');assert.equal(s.gold,gold);assert.equal(core.preflight(s.map,[...s.towers,tower('maze-wall',7,6)]).ok,true);
  pass('active_creep_clearance_and_trapping_guards_work_inside_long_bays');
}
{
  const a=fresh({seed:31,spawnInterval:.1}),b=fresh({seed:31,spawnInterval:.1});core.startWave(a);core.startWave(b);advance(a,1);for(let i=0;i<4;i++)core.tick(b,.25);
  assert.deepEqual(rounded(a),rounded(b));assert.equal(new Set(a.events.filter(e=>e.type==='spawned').map(e=>e.details.sector)).size,9);
  const restored=plain(a);advance(a,2);advance(restored,2);assert.deepEqual(plain(a),plain(restored));
  const map=core.mapDefault();for(const spawn of map.spawns){const route=core.route(map,[tower('maze-wall',7,8)],spawn,spawn.sector,true);assert.equal(route.length,map.sectors[spawn.sector].gates.length+2);assert.deepEqual(plain({x:route.at(-1).x,z:route.at(-1).z}),plain(map.exit));}
  pass('all_nine_seeded_streams_and_json_restoration_keep_ground_air_paths_deterministic');
}
{
  const s=fresh({waves:1,lives:1,preparation:0,autoWaves:true});runUntil(s,q=>q.phase==='lost',120);assert.equal(s.lives,0);assert.equal(s.leaks,1);assert.equal(s.events.filter(e=>e.type==='lost').length,1);
  const leaked=s.events.find(e=>e.type==='leaked');assert.equal(leaked.details.sector,7,'The rear catcher is the shortest stream to the shared exit.');
  const final=JSON.stringify(s);core.tick(s,1);assert.equal(JSON.stringify(s),final);assert.equal(core.build(s,'arrow',6,8).code,'finished');
  pass('shared_south_harbor_leak_ends_the_cooperative_round_once');
}
{
  const s=core.createSession({rules:{preparation:0,intermission:0}});
  for(const [kind,cx,cz] of [['arrow',6,17],['storm',8,17],['arrow',19,40],['arrow',21,40],['frost',20,39]]){
    const built=core.build(s,kind,cx,cz);assert.equal(built.ok,true,`${kind} at ${cx},${cz}: ${built.reason}`);while(built.tower.level<3)assert.equal(core.upgrade(s,built.tower.id).ok,true);
  }
  runUntil(s,q=>q.phase==='won'||q.phase==='lost',3600);assert.equal(s.phase,'won');assert.equal(s.wave,30);assert.ok(s.lives>0);assert.ok(s.kills>1000);assert.equal(s.events.filter(e=>e.type==='wave-cleared').length,30);assert.equal(s.events.filter(e=>e.type==='won').length,1);
  assert.ok(s.events.some(e=>e.type==='spawned'&&e.details.air));assert.ok(s.events.some(e=>e.type==='spawned'&&e.details.boss));assert.ok(s.events.some(e=>e.type==='ally-upgraded'&&e.details.level===3));
  const final=JSON.stringify(s);core.tick(s,1);assert.equal(JSON.stringify(s),final);
  pass('classic_layout_can_win_all_thirty_ground_air_and_boss_waves_with_solo_support');
}
console.log(`MAUL_LAYOUT_CPU_ALL_CASES_PASS ${cases}`);
