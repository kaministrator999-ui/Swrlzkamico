import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../runtime/',import.meta.url);
const files=['engine_account_start_v11_476.js','engine_account_bridge_v11_476.js','engine_resume_camera_v11_476.js'];
for(const file of files){
 const code=fs.readFileSync(new URL(file,root),'utf8');
 new vm.Script(code,{filename:file});
}
const js=fs.readFileSync(new URL(files[0],root),'utf8');
const css=fs.readFileSync(new URL('engine_account_start_v11_476.css',root),'utf8');
const bridge=fs.readFileSync(new URL(files[1],root),'utf8');
for(const key of ['se476StartupGate','se476SignIn','se476Projects','se476Remember','se476SignalLost',
 'se476RetryConnection','se476OfflineContinue','se476Open','se476ContinueLocal']){
 assert(css.includes(key)||js.includes(key),'Missing '+key);
}
for(const invariant of [
 'SWYRL_ENGINE_SAVED_DEFAULT?.read?.()',
 "if(!finished||!session)return;",
 "if(entry?.source==='cloud'&&account!=='connected')",
 "session?.source===entry?.source&&session?.id===entry?.id",
 "window.SWYRL_ENGINE_STARTUP_CAMERA_476?.restore?.(cam)",
 "window.SWYRL_ENGINE_STARTUP_ACCOUNT_476"
])assert(js.includes(invariant),'Missing safe startup invariant '+invariant);
assert(css.includes('position:fixed!important;inset:0!important'),'Downtime screen must be a full-page overlay');
assert(css.includes('prefers-reduced-motion:reduce'),'Reduced motion must disable animations');
assert(bridge.includes('se176RefreshProjects()'),'Reuse real account project listing');
assert(bridge.includes('se175LoadLocal()'),'Reuse real native local loader');
assert(bridge.includes('loadCloud(id)'),'Reuse real native cloud loader');
console.log('SE476_STARTUP_STATIC_PASS: scripts parse, native storage hooks, auto/default priority, full-screen offline recovery');
