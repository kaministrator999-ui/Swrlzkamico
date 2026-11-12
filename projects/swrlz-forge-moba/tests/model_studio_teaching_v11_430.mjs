import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../',import.meta.url),window={};
const source=fs.readFileSync(new URL('runtime/model_studio_teaching_v11_430.js',root),'utf8');
vm.runInNewContext(source,{window,Math,Number,Object,Array,Path2D:class{constructor(d){this.d=d;}}});
const api=window.SWYRL_MODEL_TEACHING;assert.ok(Object.isFrozen(api));
const entries=api.list(),ids=entries.map(e=>e.id);assert.equal(new Set(ids).size,entries.length);assert.ok(entries.length>=20);
for(const entry of entries){for(const key of ['name','summary','selection','requires','use','status'])assert.ok(typeof entry[key]==='string'&&entry[key].length>0,entry.id+':'+key);assert.ok(Object.isFrozen(entry));}
for(const id of ['inset','extrude','solidify','splitEdge','subdivide','fillHole','repairNormals'])assert.ok(ids.includes(id));
for(const id of ['bevel','merge','bridge','loopCut','mirror']){assert.equal(api.get(id).status,'incomplete');assert.ok(api.get(id).limitation.length>25);}
assert.match(api.get('solidify').requires,/entire convex planar/);assert.match(api.get('extrude').use,/inner faces selected/);assert.match(api.get('repairNormals').summary,/not guessed/);
const required=['extrude','inset','bevel','subdivide','merge','sculpt','solidify','mirror'];
const icons=required.map(id=>api.iconSVG(id));assert.equal(new Set(icons).size,required.length,'semantic operation icons differ');
for(const svg of icons){assert.match(svg,/viewBox="0 0 32 32"/);assert.match(svg,/aria-hidden="true"/);assert.doesNotMatch(svg,/<(?:script|image|foreignObject)/);}
let commands=0;const events=[];
const context=new Proxy({},{get:(_,key)=>key==='canvas'?{width:540,height:190}:(...args)=>{commands++;events.push([key,...args]);},set:()=>true});
for(const entry of entries){const start=commands;api.drawIcon(context,entry.id,16,16,24,'#b5ffe1');api.drawDemo(context,entry.id,1,540,190);assert.ok(commands-start<350,'bounded diagram cost '+entry.id);assert.ok(commands-start>10);}
assert.ok(events.some(([key,...args])=>key==='fillText'&&args[0]==='Before'));
assert.ok(events.some(([key,...args])=>key==='fillText'&&args[0]==='During'));
assert.ok(events.some(([key,...args])=>key==='fillText'&&args[0]==='After'));
assert.doesNotMatch(source,/requestAnimationFrame|setInterval|WebGLRenderer|fetch\(/,'catalog has no renderer, loop or external assets');
console.log('MODEL_STUDIO_TEACHING_V11_430_PASS',JSON.stringify({groups:6,tools:entries.length,sharedSemanticIcons:required.length,diagrams:'controlled before/during/after',unimplemented:'explicitly incomplete'}));
