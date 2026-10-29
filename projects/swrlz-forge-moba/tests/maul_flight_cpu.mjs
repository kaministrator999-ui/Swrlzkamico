import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const dir='projects/swrlz-forge-moba/runtime/';
const context=vm.createContext({console});
for(const name of ['maul_core.js','maul_builder_core.js','maul_flight_core.js'])
  vm.runInContext(readFileSync(dir+name,'utf8'),context,{filename:name});
const evalIn=source=>vm.runInContext(source,context);
const map={cols:16,rows:16,cell:2,origin:{x:-16,z:-16},blocked:[{x:5,z:5},{x:5,z:6}],
  reserved:[],spawns:[{x:3,z:2,sector:0}],exit:{x:8,z:15},
  sectors:[{id:0,minX:0,maxX:7,minZ:0,maxZ:15},{id:1,minX:8,maxX:15,minZ:0,maxZ:15}]};
const plan=(start,site,sector=0)=>evalIn('MAUL_FLIGHT_CORE.plan('+JSON.stringify(map)+','+
  JSON.stringify(start)+','+JSON.stringify(site)+','+sector+')');
const start={x:1,z:8},site={x:6,z:8},p=plan(start,site);
assert.equal(p.ok,true);
assert.deepEqual(JSON.parse(JSON.stringify(p.destination)),site,'Flight destination must be tower site, not adjacent cell');
assert.equal(p.path.length,2,'Flight moves directly over ground obstruction');
assert.equal(plan(start,{x:5,z:5}).ok,true,'Builder may fly over and arrive on blocked ground (build validation remains separate)');
assert.equal(plan(start,{x:3,z:3}).ok,false,'Protected entrance stays unbuildable');
assert.equal(plan(start,{x:9,z:8}).ok,false,'Builder may not issue cross-territory construction');
assert.equal(plan(start,{x:-1,z:5}).ok,false);
const from={x:0,z:0},to={x:20,z:0};
const halfway=evalIn('MAUL_FLIGHT_CORE.travel('+JSON.stringify(from)+','+JSON.stringify(to)+',.5)');
assert.equal(halfway.x,7.5,'Flight speed must be 15 world units/s');assert.equal(halfway.arrived,false);
const arrived=evalIn('MAUL_FLIGHT_CORE.travel('+JSON.stringify(halfway)+','+JSON.stringify(to)+',10)');
assert.equal(arrived.x,20);assert.equal(arrived.arrived,true,'Flight should never overshoot the tile');
const blockedGround=evalIn('MAUL_CORE.path('+JSON.stringify(map)+',[],'+JSON.stringify(start)+', {x:5,z:5})');
assert.equal(blockedGround,null,'Flight must not accidentally replace ground pathfinding');
const html=process.env.SWYRL_MAUL_FLIGHT_HTML;
if(html){
  const source=readFileSync(html,'utf8');
  for(const name of ['V11_12_GROUNDED_STANCE_POSES','MAUL_FLIGHT_CORE_END','maulFlightEnabled','MaulBuilderWing',
    'maulArtOldTexture','SWYRL_ENGINE_MAUL.flightStatus','SWYRL_ENGINE_MAUL.artStatus']){
    assert.ok(source.includes(name),'Missing sealed v11.2 integration '+name);
  }
}
console.log('MAUL_FLIGHT_V11_2_CPU_PASS direct-hover-build sector-bound no-build protection free-flight speed legacy-route-integrity');
