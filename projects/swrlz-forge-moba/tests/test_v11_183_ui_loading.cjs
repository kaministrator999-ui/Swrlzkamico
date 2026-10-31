const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.join(__dirname,'..');
const js=fs.readFileSync(path.join(root,'runtime/engine_project_ui_load_v11_183.js'),'utf8');
const css=fs.readFileSync(path.join(root,'runtime/engine_project_ui_load_v11_183.css'),'utf8');
for(const term of ['se183LevelsToggle','se183LevelsActions','se183LoadStatus','engine-stats-pill','st141RuntimeMenu','se183-spinner'])
 assert.ok((js+css).includes(term),term);
assert.match(css,/\.engine-stats-pill\{display:none!important\}/);
assert.match(js,/requestAnimationFrame\(\(\)=>requestAnimationFrame\(resolve\)\)/);
assert.match(js,/se183CloudCacheClear/);
assert.doesNotMatch(js,/(?:eval\(|new Function|postMessage\(|sessionStorage\.)/);
const sandbox={
 window:{},document:{},performance:{now:()=>1000},CSS:{escape:s=>s},
 console,Promise,Map,Set,Math,Number,
 requestAnimationFrame:f=>f(),setInterval:()=>1,clearInterval:()=>{},
 setTimeout:()=>1,clearTimeout:()=>{}
};
vm.createContext(sandbox);vm.runInContext(js,sandbox,{timeout:3000});
(async()=>{
 let calls=0;
 const a=sandbox.se183CloudListCached(()=>{calls++;return Promise.resolve({projects:[{id:'1'}]})});
 const b=sandbox.se183CloudListCached(()=>{calls++;return Promise.resolve({projects:[{id:'2'}]})});
 const ab=await Promise.all([a,b]);
 assert.equal(calls,1);assert.equal(ab[0].projects[0].id,'1');assert.equal(ab[1].projects[0].id,'1');
 await sandbox.se183CloudListCached(()=>{calls++;return Promise.resolve({projects:[]})});
 assert.equal(calls,1,'12s cache should reuse list');
 sandbox.se183CloudCacheClear();
 await sandbox.se183CloudListCached(()=>{calls++;return Promise.resolve({projects:[]})});
 assert.equal(calls,2,'account invalidation must refetch');
 await sandbox.se183PaintNext();
 assert.ok(sandbox.window.SWYRL_ENGINE_PROJECT_LOAD.read());
 console.log('SE183_LOAD_AND_UI_FOCUSED_TESTS_PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
