import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {JSDOM}=require(process.env.SE_JSDOM_MODULE);
const js=fs.readFileSync('projects/swrlz-forge-moba/runtime/project_hub_my_projects_v11_170.js','utf8');
const html='<div id="projectHub" class="project-hub"><div class="project-window"><div class="project-head">Projects</div><div class="project-grid"><button data-project-template="a">Starter A</button></div><div class="project-actions"><button id="hubSaveBtn">Local Save</button></div><label><input type="checkbox" data-se128-default="a">Default</label></div></div>';
const dom=new JSDOM(html,{url:'https://kamiloki-swrlz-forge-moba.static.hf.space/'});
const originalCard=dom.window.document.querySelector('[data-project-template=a]');
const originalSave=dom.window.document.getElementById('hubSaveBtn');
let listCalls=0,loads=[],dirtyPrompts=0;
const context={document:dom.window.document,location:dom.window.location,window:dom.window,console,
 ALLOWED_PARENTS:new Set([dom.window.location.origin]),ready:true,frame:{src:'ready'},
 CHAT_ORIGIN:'https://kamiloki-swyrlz.hf.space',summaryName:s=>String(s||'').slice(0,100),
 bounded:(s,max=160)=>typeof s==='string'&&s.length>0&&s.length<=max,
 rpc:async type=>{assert.equal(type,'cloud.list');listCalls++;return{projects:[{id:'my1',name:'<b>Literal §§</b>',revision:4}]};},
 loadCloud:async id=>{loads.push(id);return true;},cloudBusy:false,openPanel(){},setStatus(){}};
vm.createContext(context);vm.runInContext(js,context);vm.runInContext('se170Install()',context);
const d=dom.window.document;
assert.equal(d.querySelectorAll('[role=tab]').length,2);
assert.equal(d.querySelector('[data-project-template=a]'),originalCard);
assert.equal(d.getElementById('hubSaveBtn'),originalSave);
assert.equal(d.querySelectorAll('[data-se128-default]').length,1);
d.getElementById('se170-tab-mine').click();
for(let n=0;n<5;n++)await Promise.resolve();
assert.equal(listCalls,1);
assert.equal(d.querySelector('.se170-project-card strong').textContent,'<b>Literal §§</b>');
assert.equal(d.querySelector('.se170-project-card strong').querySelector('b'),null);
d.querySelector('.se170-project-card button').click();for(let n=0;n<5;n++)await Promise.resolve();
assert.deepEqual(loads,['my1']);assert(!d.getElementById('projectHub').classList.contains('show'));
d.getElementById('se170-tab-starter').click();assert.equal(d.getElementById('se170-pane-mine').hidden,true);
assert.equal(d.getElementById('se170-pane-starter').hidden,false);
d.getElementById('se170-tab-mine').click();for(let n=0;n<5;n++)await Promise.resolve();
vm.runInContext("se170AccountStatus({authenticated:false})",context);
assert.equal(d.querySelectorAll('.se170-project-card').length,0,'account change clears prior names');
assert(d.getElementById('se170-library-status').textContent.includes('Connect'));
console.log('SE170_PROJECT_HUB_TABS_PASS');
