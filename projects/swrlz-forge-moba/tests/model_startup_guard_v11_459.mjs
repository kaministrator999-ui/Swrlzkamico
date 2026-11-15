#!/usr/bin/env node
// §E v11.459: viewport visual helpers cannot prevent editor boot.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

assert(process.argv[2], 'built engine HTML path required');
const html=fs.readFileSync(process.argv[2],'utf8');
const viewStart=html.indexOf('/* SE455_VIEW_READABILITY_START */');
const viewEnd=html.indexOf('/* SE455_VIEW_READABILITY_END */',viewStart);
assert(viewStart>=0&&viewEnd>viewStart);
const display=html.slice(viewStart,viewEnd);
assert(!display.includes('const mode=()=>atelierViewGlobal;'),
 'Viewport display boot must not access the private atelierViewGlobal');
assert(!display.includes('mode:atelierViewGlobal'),
 'Viewport inspection must not access the private atelierViewGlobal');
assert(display.includes("panel?.querySelector('#ViewportMode')?.value"),
 'Viewport quick switch should read the existing native input');
assert(display.includes("native.dispatchEvent(new Event('change',{bubbles:true}))"),
 'Quick view selection must delegate to original native renderer event');
const begin='/* SE458_MODEL_VIEWPORT_STABILITY_START */';
const end='/* SE459_STARTUP_SAFETY_COMPLETE */';
const start=html.indexOf(begin),stop=html.indexOf(end,start);
assert(start>=0&&stop>start,'Exact optional viewport module must be installed');
const moduleText=html.slice(start,stop+end.length);
new vm.Script(moduleText);
const events={};
const window={addEventListener:(name,callback)=>{events[name]=callback;}};
let environment=vm.createContext({window,queueMicrotask:fn=>fn(),requestAnimationFrame:fn=>fn()});
assert.doesNotThrow(()=>vm.runInContext(moduleText,environment),
 'Optional module must not crash if internal renderer is unavailable at startup');
assert.equal(window.SWYRL_ENGINE_MODEL_VIEW_STABILITY_458.inspect().hasModel,false);
assert.equal(typeof events['swrlz:model-workshop-change'],'function');

assert.doesNotThrow(()=>events['swrlz:model-workshop-change']({detail:{
  message:'Applied inset to native geometry.',selection:{partId:'cube',mode:'face'},preview:{active:false}
}}), 'Early native-change events before model initialization must be safe');
const cameraCalled=[];
const runtime={
 window:{addEventListener:(n,cb)=>cameraCalled.push(n)},modelRoot:null,
 atelierViewModeApply:()=>({ok:true}),
 selection:null
};
assert.doesNotThrow(()=>vm.runInNewContext(moduleText,runtime),
 'Optional viewport module may integrate when native renderer is available');
assert(cameraCalled.includes('swrlz:model-workshop-change'));

for(const token of [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_459_VIEWPORT_BOOT_GUARD',
 "window.SWRLZ_FORGE_BUILD={version:'v11.459'",
 '/* SE458_DOCK_AND_MODEL_CONTRAST_START */',
 'V11_457_CONVERSION_NO_FACE_GATE',
 'SE454_INSET_TOP_STEPS_START'
]){
 assert(html.includes(token),'Built HTML missing '+token);
}
console.log('SE459_STARTUP_GUARD_PASS: no renderer at startup, native renderer available, scene events safe before initialization, history intact');
