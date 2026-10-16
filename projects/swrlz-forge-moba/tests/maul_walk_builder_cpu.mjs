import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const root='projects/swrlz-forge-moba/runtime/';
const context=vm.createContext({console});
for(const name of ['maul_core.js','maul_builder_core.js'])
  vm.runInContext(readFileSync(root+name,'utf8'),context,{filename:name});
const evalIn=source=>vm.runInContext(source,context);
const map={cols:16,rows:16,cell:2,origin:{x:-16,z:-16},blocked:[],reserved:[],
  sectors:[{id:0,minX:0,maxX:15,minZ:0,maxZ:15}],
  spawns:[{x:4,z:3,sector:0}],exit:{x:8,z:15}};
const site={x:12,z:11},start={x:1,z:10};
assert.equal(evalIn('MAUL_BUILDER_CORE.protectedSpawn('+JSON.stringify(map)+',{x:5,z:4})'),true);
assert.equal(evalIn('MAUL_BUILDER_CORE.protectedSpawn('+JSON.stringify(map)+',{x:8,z:8})'),false);
const result=evalIn('MAUL_BUILDER_CORE.plan('+JSON.stringify(map)+',[],'+JSON.stringify(start)+','+JSON.stringify(site)+',0)');
assert.equal(result.ok,true,JSON.stringify(result));
assert.ok(result.path.length>1,'Non-adjacent builder must have a movement route');
assert.equal(Math.abs(result.destination.x-site.x)+Math.abs(result.destination.z-site.z),1,'Builder must stand adjacent to build');
const forbidden=evalIn('MAUL_BUILDER_CORE.plan('+JSON.stringify(map)+',[],'+JSON.stringify(start)+',{x:5,z:4},0)');
assert.equal(forbidden.ok,false);assert.match(forbidden.reason,/no-build/i);
const other=evalIn('MAUL_BUILDER_CORE.plan('+JSON.stringify(map)+',[],'+JSON.stringify(start)+',{x:16,z:6},0)');
assert.equal(other.ok,false);
const sealed=readFileSync(process.env.SWYRL_MAUL_WALK_HTML||'dist/swrlz-forge-moba/index.html','utf8');
for(const name of ['V11_12_GROUNDED_STANCE_POSES','MAUL_BUILDER_CORE','maulBuildAt=function','maulPendingBuilds','maul-build-queued','maul-build-completed','maul-build-cancelled','maulWalkBuildEnabled']){
 assert.ok(sealed.includes(name),'Missing engine integration '+name);
}
assert.ok(sealed.includes('maulSpawnProtection'),'New map must declare full spawn protection');
console.log('MAUL_WALK_BUILDER_CPU_PASS route-planning adjacent-construction protected-spawns release-integration');
