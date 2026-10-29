import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {JSDOM}=require(process.env.SE_JSDOM_MODULE);
const src=fs.readFileSync('projects/swrlz-forge-moba/runtime/engine_project_zoom_guard_v11_129.js','utf8');
const css=fs.readFileSync('projects/swrlz-forge-moba/runtime/engine_project_zoom_guard_v11_129.css','utf8');
const dom=new JSDOM('<div id="projectHub"><button data-project-template="sheep-tag-meadow">Sheep Tag</button><div class="se128-starter-choice"><label class="se128-default-checkbox"><input type="checkbox" data-se128-default="sheep-tag-meadow">Default</label></div></div><div id="viewport"></div>',{url:'https://example.test/'});
const {document}=dom.window;
const opened=[],deferred=[],timers=new Map();let serial=0,now=1000;
const ctx={window:dom.window,document,performance:{now:()=>now},queueMicrotask:fn=>deferred.push(fn),setTimeout:(fn,ms)=>{const id=++serial;timers.set(id,{fn,ms});return id;},clearTimeout:id=>timers.delete(id)};
vm.createContext(ctx);
vm.runInContext(src,ctx);
const button=document.querySelector('button[data-project-template]');
button.onclick=()=>opened.push('sheep-tag-meadow');
const choice=document.querySelector('input[data-se128-default]');
function touch(node,type='touch'){
 const event=new dom.window.Event('pointerup',{bubbles:true});
 Object.defineProperty(event,'pointerType',{value:type});
 node.dispatchEvent(event);
 node.click();
 while(deferred.length)deferred.shift()();
}
touch(choice);
assert.equal(document.querySelector('#se129-project-tap-guard'),null,'checkbox does not install shield');
assert.deepEqual(opened,[]);
touch(button,'mouse');
assert.equal(document.querySelector('#se129-project-tap-guard'),null,'mouse remains unchanged');
assert.equal(opened.length,1);
now+=15;
touch(button);
assert.equal(opened.length,2,'the first touch click still opens the starter');
const shield=document.querySelector('#se129-project-tap-guard');
assert.ok(shield,'touch selection protects transition');
assert.equal(shield.getAttribute('aria-hidden'),'true','shield does not trap accessibility focus');
assert.equal(timers.size,1);
const timer=[...timers.values()][0];
assert.equal(timer.ms,420,'only brief handoff protection');
let cancelled=false;
const doubleTap=new dom.window.Event('dblclick',{bubbles:true,cancelable:true});
shield.dispatchEvent(doubleTap);cancelled=doubleTap.defaultPrevented;
assert.equal(cancelled,true,'native zoom-capable double click is cancelled on shield');
timer.fn();
assert.equal(document.querySelector('#se129-project-tap-guard'),null,'shield self-cleans');
assert.equal(timers.size,0);
assert.ok(css.includes('touch-action:manipulation!important'));
assert.ok(css.includes('#projectHub .project-card'));
assert.ok(css.includes('.se128-default-checkbox'));
assert.ok(css.includes('#se129-project-tap-guard'));
assert.ok(!css.includes('#viewport {'),'camera gesture policy remains authored by viewport');
assert.ok(!/user-scalable\s*=\s*no|maximum-scale\s*=\s*1/i.test(css+src),'do not prevent pinch zoom accessibility');
assert.ok(!src.includes("preventDefault();\n // A user"),'no global pointer suppression');
if(process.env.SE_ASSEMBLED_HTML){
 const html=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 for(const token of [
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_129_PROJECT_HANDOFF_PAGE_ZOOM_GUARD',
  'se129InstallProjectTapGuard','se129-project-zoom-guard',
  'se128InstallStarterChoices','st127BuildOrganicPrototype','st126InstallStarterRoutes',
  'se127-editor-boot','se129-project-tap-guard'
 ]) assert.ok(html.includes(token),'missing integrated behavior '+token);
}
console.log('SE129_PROJECT_DOUBLE_TAP_PAGE_ZOOM_TRANSITION_PASS');
