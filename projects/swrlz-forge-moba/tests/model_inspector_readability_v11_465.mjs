#!/usr/bin/env node
// §E v11.465 — native inspector compaction and restored full-width overlay.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const js=fs.readFileSync(new URL('../runtime/model_inspector_readability_v11_465.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../runtime/model_inspector_readability_v11_465.css',import.meta.url),'utf8');
new vm.Script(js,{filename:'model_inspector_readability_v11_465.js'});
assert(!js.includes('checkpoint(')&&!js.includes('model().parts='));
assert(!js.includes('style.width=')&&!js.includes('se251RightWidth='));
assert(css.includes('overflow-wrap:normal!important;word-break:normal!important;'));
assert(css.includes('[data-se465-inspector-narrow=true]'));
assert(css.includes(':not(.atelier-tool-handle):not(.se465-inspector-narrow-hint)'));
assert(css.includes('[data-se464-inspector-focus=true] .atelier-body'));
assert(css.includes('--se320-right:0px!important;'));
assert(css.includes('grid-template-columns:var(--se320-left) minmax(0,1fr) var(--se320-rail) 0px!important;'));
assert(css.includes('[data-se251-layout=desktop]'));
assert(css.includes('@media(min-width:921px) and (pointer:fine)'));
assert(css.includes('width:min(440px,calc(100% - 16px))!important;'));
assert(!css.includes('overflow-wrap:anywhere;'));
let width=120,installs=0,notes=[],resizes=[],removes=0,observations=[];
class ResizeObserver {
 constructor(callback){this.callback=callback;resizes.push(this);}
 observe(element){this.element=element;observations.push(element);}
 disconnect(){this.disconnected=true;}
 trigger(){this.callback([{target:this.element}]);}
}
function element(tag){
 return {tagName:tag,children:[],attrs:{},setAttribute(name,value){this.attrs[name]=value;},
  append(...children){this.children.push(...children);},
  textContent:'',after(node){notes.push(node);}};
}
const handle=element('header');
const inspector={
 isConnected:true,clientWidth:120,
 getBoundingClientRect:()=>({width}),
 querySelector:s=>s==='.atelier-tool-handle'?handle:null
};
let currentInspector=inspector;
const panel={
 hidden:false,dataset:{se464InspectorFocus:'false'},
 querySelector:s=>s==='.atelier-inspector'?currentInspector:null
};
const listeners={};
const window={
 addEventListener(name,fn){listeners[name]=fn;},
 removeEventListener(name,fn){if(listeners[name]===fn){removes++;delete listeners[name];}}
};
const document={createElement:element};
const ctx=vm.createContext({
 se430BeginnerInstall:()=>{installs++;},window,document,ResizeObserver,
 requestAnimationFrame:callback=>callback(),panel,Object
});
vm.runInContext(js,ctx);
assert(window.SWYRL_ENGINE_INSPECTOR_READABILITY_465);
assert.equal(window.SWYRL_ENGINE_INSPECTOR_READABILITY_465.thresholdPx,236);
ctx.se430BeginnerInstall(panel);
assert.equal(installs,1);
assert.equal(notes.length,1);
assert.equal(notes[0].id,'se465InspectorNarrowHint');
assert.equal(notes[0].attrs.role,'note');
assert.equal(notes[0].children[0].textContent,'Tools are compact');
assert.match(notes[0].children[1].textContent,/Tap Expand/);
assert.equal(panel.dataset.se465InspectorNarrow,'true');
assert.equal(window.SWYRL_ENGINE_INSPECTOR_READABILITY_465.inspect().compact,true);
width=235;resizes[0].trigger();
assert.equal(panel.dataset.se465InspectorNarrow,'true');
width=236;resizes[0].trigger();
assert.equal(panel.dataset.se465InspectorNarrow,'false');
width=390;panel.dataset.se464InspectorFocus='true';resizes[0].trigger();
assert.equal(panel.dataset.se465InspectorNarrow,'false');
assert.equal(window.SWYRL_ENGINE_INSPECTOR_READABILITY_465.inspect().expanded,true);
width=120;panel.dataset.se464InspectorFocus='false';resizes[0].trigger();
assert.equal(panel.dataset.se465InspectorNarrow,'true');
ctx.se430BeginnerInstall(panel);
assert.equal(installs,2,'Previous native install always called');
assert.equal(notes.length,1,'No duplicated compact prompt on native refresh');
assert.equal(resizes.length,1,'No duplicated observer on native refresh');
const handle2=element('header');
const replacement={
 isConnected:true,clientWidth:274,
 getBoundingClientRect:()=>({width:274}),
 querySelector:s=>s==='.atelier-tool-handle'?handle2:null
};
currentInspector=replacement;
ctx.se430BeginnerInstall(panel);
assert.equal(resizes[0].disconnected,true,'Old native inspector observer cleaned on remount');
assert.equal(removes,1,'Old window resize callback removed on remount');
assert.equal(notes.length,2,'New native inspector gets a single prompt');
assert.equal(panel.dataset.se465InspectorNarrow,'false','New dock width detected');
assert.equal(observations[1],replacement);
panel.hidden=true;resizes[1].trigger();
assert.equal(panel.dataset.se465InspectorNarrow,'false','Hidden modeler does not mismeasure');
if(process.argv[2]){
 const html=fs.readFileSync(process.argv[2],'utf8');
 for(const marker of [
  "window.SWRLZ_FORGE_BUILD={version:'v11.465'",
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_465_INSPECTOR_READABILITY',
  'SE465_NARROW_INSPECTOR_START',
  'SE465_NARROW_INSPECTOR_STYLES_START',
  'SE464_MODEL_VISUAL_POLISH_START',
  'SE464_INSPECTOR_VISUAL_POLISH_START',
  'SE461_TOUCH_DOCK_BOUNDS_START',
  'SE462_VIEW_AND_DOCK_STYLES_START',
  'Select mesh · Undo / Redo'
 ])assert(html.includes(marker),'Compiled §E missing '+marker);
}
console.log('SE465_INSPECTOR_READABILITY_PASS: word wrapping, compact threshold, Expand/Dock track, preserved dock resizers, remount and visibility');
