import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const js=fs.readFileSync(new URL('../runtime/model_progressive_tools_v11_474.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../runtime/model_progressive_tools_v11_474.css',import.meta.url),'utf8');
new vm.Script(js);
for(const token of ['SE474_PROGRESSIVE_MODEL_TOOLS_STYLES_START',
 'data-se474-settings-open=false','data-se474-settings-open=true',
 'se474ToolFlyout','se474SpecificModes','touch-action:pan-x',
 'data-se474-specific-type=vertex','data-se474-specific-type=inset',
 'data-se251-layout=compact'])assert(css.includes(token),'Missing mobile layout '+token);

class El{
 constructor(tag='div'){this.tagName=tag.toUpperCase();this.children=[];this.dataset={};
  this.listeners={};this.hidden=false;this.attrs={};this.textContent='';this.value='';
  this.parent=null;this.options=[];}
 append(...nodes){for(const node of nodes){this.children.push(node);node.parent=this;}}
 replaceChildren(...nodes){this.children=[];this.append(...nodes);}
 querySelector(selector){return this.select?.[selector]||null;}
 setAttribute(k,v){this.attrs[k]=String(v);}
 getAttribute(k){return this.attrs[k]||null;}
 addEventListener(k,fn){this.listeners[k]=fn;}
 dispatchEvent(event){this.listeners[event.type]?.(event);}
 closest(){return null;}
}
const p=new El(),rail=new El(),body=new El(),inspector=new El();
const workshopOp=new El('select');workshopOp.value='inset';
workshopOp.options=['inset','extrude','splitEdge','subdivide','fillHole','deleteFaces','solidify','repairNormals']
 .map(value=>({value}));
const ringMode=new El('select');ringMode.value='outline';
const steps=new El('input');steps.value='3';
const start=new El('input');start.value='0';
const sweep=new El('input');sweep.value='360';
const plane=new El('select');plane.value='xz';
const attrs={
 '#modelAtelierToolRail':rail,'.atelier-body':body,'.atelier-inspector':inspector,
 '#modelAtelierWorkshopOperation':workshopOp,'#se466RingMode':ringMode,
 '#se466RingSteps':steps,'#se466ArcStart':start,
 '#se466ArcSweep':sweep,'#se466RingPlane':plane
};
p.select=attrs;
const doc={readyState:'complete',body:new El(),
 querySelector(selector){return selector==='#modelAtelierPanel'?p:null;},
 createElement(tag){return new El(tag);}
};
const calls=[],mesh={preview:{active:false},selection:{ids:[6],faceIds:[0],partId:'mesh-1'},ring:{centered:false}};
const bridge={inspect:()=>mesh,setComponentMode:mode=>{calls.push(['component',mode]);return {ok:true};},
 setRingAnchor:()=>{mesh.ring.centered=true;calls.push(['anchor']);return {ok:true};},
 selectRing:opts=>{calls.push(['ring',opts]);return {ok:true,message:'selected '+opts.mode};},
 selectRegion:(face,part)=>{calls.push(['region',face,part]);return {ok:true};}};
const context={groups:()=>({Sculpt:['Brush shape'],Topology:['Manual mesh modeling'],
 Meshes:['Select & organize']}),current:()=>({})};
const unified={select:(category,name)=>{calls.push(['context',category,name]);}};
const win={SWYRL_ENGINE_MODEL_WORKSHOP:bridge,SWYRL_E_CONTEXT:context,
 SWYRL_E_UNIFIED_TOOLS:unified,addEventListener(){}};
class MutationObserver{observe(){}}
const ctx={document:doc,window:win,MutationObserver,queueMicrotask,Event:class{constructor(type){this.type=type;}}};
vm.runInNewContext(js,ctx);
const api=win.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474;
assert(api,'Progressive API was not mounted');
assert.equal(p.dataset.se474SettingsOpen,'false');
api.chooseFamily('Sculpt');
assert.equal(api.inspect().flyout,true);
assert.equal(api.inspect().settings,false,'Category must not open inspector');
api.chooseTool('Vertex','vertex');
assert.equal(api.inspect().settings,false,'Tool must not open inspector');
api.chooseMode('single');
assert.equal(api.inspect().settings,false,'Single selection has no settings');
api.chooseMode('fill');
assert.equal(api.inspect().settings,true,'Ring Fill must show settings');
assert.equal(ringMode.value,'fill');
assert(calls.some(x=>x[0]==='ring'&&x[1].mode==='fill'&&x[1].steps===3));
api.chooseMode('ring');
assert(calls.some(x=>x[0]==='ring'&&x[1].mode==='outline'));
api.chooseTool('Inset','inset');
assert.equal(api.inspect().settings,false,'New tool hides old settings');
assert(calls.some(x=>x[0]==='context'&&x[1]==='Topology'&&x[2]==='Manual mesh modeling'));
api.chooseMode('region');
assert.equal(workshopOp.value,'inset');
assert(calls.some(x=>x[0]==='region'&&x[1]===0&&x[2]==='mesh-1'));
assert.equal(api.inspect().settings,true);
mesh.preview.active=true;
const before=api.inspect();
api.chooseFamily('Meshes');
assert.equal(api.inspect().family,before.family,'Active preview guards family switches');
mesh.preview.active=false;
api.chooseFamily('Meshes');
assert.equal(api.inspect().family,'Meshes');
assert.equal(api.inspect().settings,false);
assert.equal(p.querySelector('.atelier-inspector'),inspector);
console.log('SE474_PROGRESSIVE_MODEL_TOOLS_PASS: family, flyout, specific mode, Ring Fill, native inset, preview and inspector gates');
