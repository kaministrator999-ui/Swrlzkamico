const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.join(__dirname,'..');
const boot=fs.readFileSync(path.join(root,'runtime/user_project_default_boot_v11_184.js'),'utf8');
const cards=fs.readFileSync(path.join(root,'runtime/user_project_cards_v11_184.js'),'utf8');
const css=fs.readFileSync(path.join(root,'runtime/user_project_cards_v11_184.css'),'utf8');
for(const x of ['saved:local:','saved:cloud:','se128StartupPending','indexedDB.open','openCloud','setTimeout'])assert.ok(boot.includes(x));
for(const x of ['se184ExtractPreview','se184PreviewView','dataset.se184Default','se184RenderLocalProjects','se184RenderCloudProjects','se175Read','cloud.load'])assert.ok(cards.includes(x),x);
assert.match(css,/grid-template-columns:repeat\(auto-fill/);
assert.match(css,/se184-default-label/);
assert.doesNotMatch(boot+cards,/(?:\beval\(|new Function\(|innerHTML\s*\+\=|localStorage\.setItem\(.+projectData)/);
const store=new Map();
const sandbox={window:{},document:{body:{append(){}},createElement:()=>({setAttribute(){},append(){}}),getElementById:()=>null,querySelectorAll:()=>[]},
 localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v),removeItem:k=>store.delete(k)},
 console,queueMicrotask,clearTimeout,setTimeout,Promise,structuredClone};
vm.createContext(sandbox);vm.runInContext(boot,sandbox);
const api=sandbox.window.SWYRL_ENGINE_SAVED_DEFAULT;
assert.ok(api);assert.equal(api.read(),null);
assert.equal(api.set('local','a1'),true);
assert.equal(api.read().source,'local');assert.equal(api.read().id,'a1');
assert.equal(store.size,1);
assert.equal(api.set('cloud','c9'),true);assert.equal(api.read().source,'cloud');
assert.equal(api.set(null),true);assert.equal(api.read(),null);
assert.equal(api.set('cloud',''),false);

assert.equal(api.set('cloud','cloud-42'),true);
assert.equal(api.launch(),true);
assert.equal(api.pending().source,'cloud');
assert.equal(sandbox.window.se128StartupPending,true);
api.openCloud(async id=>{assert.equal(id,'cloud-42');return true;}).then(ok=>{
 assert.equal(ok,true);
 assert.equal(api.report().success,true);
 assert.equal(api.pending(),null);
 assert.equal(sandbox.window.se128StartupPending,false);
 console.log('SE184_DEFAULT_PREFERENCE_SINGLE_CHOICE_AND_CLOUD_BOOT_PASS');
}).catch(e=>{console.error(e);process.exitCode=1;});

