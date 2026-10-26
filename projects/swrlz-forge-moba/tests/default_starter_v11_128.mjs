import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {JSDOM}=require(process.env.SE_JSDOM_MODULE);
const js=fs.readFileSync('projects/swrlz-forge-moba/runtime/engine_default_starter_v11_128.js','utf8');
const css=fs.readFileSync('projects/swrlz-forge-moba/runtime/engine_default_starter_v11_128.css','utf8');
const values=['glitch-dragons-den','starforge-observatory','anime-ghosts-ep01','sheep-tag-meadow','maul-frostveil','festival-girl-saved','model-atelier','wolf-model','sheep-model','blank-model'];
const html='<div id="projectHub"><div class="project-grid">'+values.map(x=>'<button class="project-card" data-project-template="'+x+'"><strong>'+x+'</strong></button>').join('')+'</div></div>';
function fixture(url='https://example.test/'){
 const dom=new JSDOM(html,{url});
 const opened=[],toast=[],record={startup:[]};
 const ctx={document:dom.window.document,window:dom.window,location:dom.window.location,
  localStorage:dom.window.localStorage,URLSearchParams:dom.window.URLSearchParams,queueMicrotask,console,
  toast:message=>toast.push(message),
  loadCanonicalGlitchDen:()=>record.startup.push('dragon'),
  loadCanonicalStarforge:()=>record.startup.push('starforge'),
  loadCanonicalAnimeEpisode:()=>record.startup.push('anime'),
  stLoadStarter:()=>record.startup.push('sheep-tag'),
  maulLoadStarter:()=>record.startup.push('maul'),
  createProjectFromTemplate:id=>{record.startup.push(id);return true;}};
 for(const c of [...dom.window.document.querySelectorAll('.project-card')])
  c.onclick=()=>opened.push(c.dataset.projectTemplate);
 vm.createContext(ctx);vm.runInContext(js,ctx);
 return {dom,ctx,record,opened,toast,get boxes(){return [...dom.window.document.querySelectorAll('input[data-se128-default]')]}};
}
const f=fixture();
assert.equal(f.boxes.length,values.length,'every starter gets a checkbox');
assert.equal(f.dom.window.document.querySelectorAll('.se128-starter-choice>.project-card').length,values.length);
assert.ok(f.boxes.every(box=>box.parentElement.tagName==='LABEL'),'controls are adjacent to native buttons');
assert.ok(f.boxes.every(box=>!box.closest('button')),'do not nest checkbox in clickable template button');
assert.equal(f.dom.window.document.querySelectorAll('input:checked').length,0,'no unexpected default');
f.dom.window.localStorage.setItem('swrlz-forge-v5-autosave','{ "myUserProject": true }');
f.boxes[3].click();
assert.equal(f.dom.window.localStorage.getItem('swyrl.engine.defaultStarter.v1'),'sheep-tag-meadow');
assert.equal(f.dom.window.document.querySelectorAll('input:checked').length,1);
assert.equal(f.opened.length,0,'tapping default checkbox does not open starter');
f.boxes[7].click();
assert.equal(f.dom.window.localStorage.getItem('swyrl.engine.defaultStarter.v1'),'wolf-model');
assert.equal(f.dom.window.document.querySelectorAll('input:checked').length,1);
f.boxes[7].click();
assert.equal(f.dom.window.localStorage.getItem('swyrl.engine.defaultStarter.v1'),null,'uncheck clears choice');
assert.equal(f.dom.window.document.querySelectorAll('input:checked').length,0);
f.boxes[3].click();
f.ctx.se128LaunchStartupProject();
assert.deepEqual(f.record.startup,['sheep-tag'],'selected default boots correct starter');
assert.equal(f.dom.window.localStorage.getItem('swrlz-forge-v5-autosave'),'{ "myUserProject": true }','do not touch authored autosave');
assert.equal(f.dom.window.document.querySelectorAll('input:checked').length,1);
f.dom.window.document.querySelector('[data-project-template="maul-frostveil"]').click();
assert.deepEqual(f.opened,['maul-frostveil'],'starter card action still works');
const g=fixture('https://example.test/?project=starforge-observatory');
g.dom.window.localStorage.setItem('swyrl.engine.defaultStarter.v1','sheep-tag-meadow');
g.ctx.se128SyncChoices();g.ctx.se128LaunchStartupProject();
assert.deepEqual(g.record.startup,['starforge'],'explicit query overrides remembered default');
assert.equal(g.dom.window.localStorage.getItem('swyrl.engine.defaultStarter.v1'),'sheep-tag-meadow','deep link does not overwrite preference');
const h=fixture('https://example.test/?project=sheep-model');
h.dom.window.localStorage.setItem('swyrl.engine.defaultStarter.v1','maul-frostveil');
h.ctx.se128LaunchStartupProject();
assert.deepEqual(h.record.startup,['dragon'],'preexisting specialist URL project loader owns model query');
const d=fixture();d.ctx.se128LaunchStartupProject();assert.deepEqual(d.record.startup,['dragon'],'unset preference preserves original startup');
const invalid=fixture();invalid.dom.window.localStorage.setItem('swyrl.engine.defaultStarter.v1','unknown-id');
invalid.ctx.se128LaunchStartupProject();assert.deepEqual(invalid.record.startup,['dragon'],'stale ID cannot load arbitrary project');
assert.ok(css.includes('min-height:44px')&&css.includes('.se128-default-checkbox'),'touch label visible');
if(process.env.SE_ASSEMBLED_HTML){
 const s=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 assert.ok(s.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_128_SINGLE_DEFAULT_STARTER_AND_STABLE_BOOT'));
 assert.ok(s.includes('se128LaunchStartupProject();installAnimeStarterUI();'),'real native boot path uses selected starter');
 assert.ok(s.includes('se128InstallStarterChoices();'));
 assert.ok(s.includes('!window.se128StartupPending&&loaded&&now-first>=2600'),'boot waits on selected async starter');
 assert.ok(s.includes('st127BuildOrganicPrototype'),'Clover §E v11.127 retained');
 assert.ok(s.includes('st126InstallStarterRoutes'),'Sheep Tag §E v11.126 retained');
}
console.log('SE128_DEFAULT_STARTER_CHECKBOX_PERSISTENCE_DEEPLINK_AUTOSAVE_AND_BOOT_PASS',values.length);
