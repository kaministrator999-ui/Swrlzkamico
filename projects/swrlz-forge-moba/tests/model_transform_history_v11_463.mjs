#!/usr/bin/env node
// §E v11.463 — actual native transform toolbar status contract across Undo.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
for(const phrase of [
 "window.SWRLZ_FORGE_BUILD={version:'v11.463'",
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_463_TRANSFORM_BAR_HISTORY',
 'const hasSelection=!!state?.selected;',
 "if(caption)caption.textContent=hasSelection?'Transform':'Select mesh · Undo / Redo';",
 'if(native&&bar._se463ObservedNative!==native){',
 'if(button.dataset.se320History)requestAnimationFrame(()=>se320RefreshTransformAccess(panel));',
 'SE462_MODEL_WIRE_CLARITY_START'
])assert(html.includes(phrase),'Compiled modeler missing '+phrase);
const begin=html.indexOf('function se320RefreshTransformAccess(panel){');
const next=html.indexOf('function se320ModelTransformAccess(panel,inspector){',begin);
assert(begin>=0&&next>begin);
const fn=html.slice(begin,next);
new vm.Script(fn,{filename:'se320RefreshTransformAccess.js'});
const state={open:true,selected:'cube'};
const toolbarBtns=[
 ...['move','rotate','scale','x','y','z','minus','plus'].map(x=>({
  dataset:{se320Transform:x},
  disabled:false,
  hasAttribute:n=>n==='aria-pressed',
  setAttribute(n,v){this[n]=v;}
 })),
 ...['undo','redo'].map(x=>({dataset:{se320History:x},disabled:false})),
 {dataset:{se320Uv:'toggle'},disabled:false,setAttribute(n,v){this[n]=v;}}
];
const caption={textContent:'Transform'};
const uvNudges={hidden:false};
const bar={
 hidden:true,attrs:{},parentElement:null,_se463ObservedNative:null,
 setAttribute(n,v){this.attrs[n]=v;},
 querySelector(s){return s==='.se320-transform-label'?caption:s==='.se320-uv-nudges'?uvNudges:null;},
 querySelectorAll(s){
  return s==='[data-se320-history]'?toolbarBtns.filter(x=>x.dataset.se320History):
   s==='[data-se320-uv]'?toolbarBtns.filter(x=>x.dataset.se320Uv):
   s==='[data-se320-transform]'?toolbarBtns.filter(x=>x.dataset.se320Transform):[];
 }
};
const originals={
 '#modelAtelierUndo':{disabled:true},'#modelAtelierRedo':{disabled:false}
};
const native={querySelector(){return {disabled:false,getAttribute:()=> 'false'};}};
const panel={hidden:false,nodes:{
 '#se320ModelTransform':bar,'#modelAtelierMeshQuickStrip':native,...originals
},querySelector(s){return this.nodes[s]||null;}};
const ctx=vm.createContext({ModelAtelier:{status:()=>state},window:{
 SWYRLZ_E_MODEL_UV_SLIDE:{state:()=>({enabled:false,available:true})}
},q:(s,root)=>root.querySelector(s),document:{}});
vm.runInContext(fn,ctx);
const refresh=ctx.se320RefreshTransformAccess;
refresh(panel);
assert.equal(bar.hidden,false,'Selected mesh displays toolbar');
assert.equal(caption.textContent,'Transform');
assert.equal(toolbarBtns.find(x=>x.dataset.se320Transform==='move').disabled,false);
state.selected=null;refresh(panel); // Undo restores state with no selection
assert.equal(bar.hidden,false,'Undo deselection MUST NOT hide Undo/Redo');
assert.equal(bar.attrs['aria-hidden'],'false');
assert.match(caption.textContent,/Select mesh/);
assert.equal(toolbarBtns.find(x=>x.dataset.se320Transform==='move').disabled,true);
assert.equal(toolbarBtns.find(x=>x.dataset.se320Uv==='toggle').disabled,true);
assert.equal(toolbarBtns.find(x=>x.dataset.se320History==='redo').disabled,false,
 'Redo must remain accessible with no selected mesh');
assert.equal(toolbarBtns.find(x=>x.dataset.se320History==='undo').disabled,true,
 'History disabled state remains native');
state.selected='cube';originals['#modelAtelierUndo'].disabled=false;refresh(panel);
assert.equal(bar.hidden,false);assert.equal(caption.textContent,'Transform');
assert.equal(toolbarBtns.find(x=>x.dataset.se320Transform==='move').disabled,false);
assert.equal(toolbarBtns.find(x=>x.dataset.se320History==='undo').disabled,false);
state.open=false;refresh(panel);
assert.equal(bar.hidden,true,'Close modeler still hides toolbar');
state.open=true;panel.hidden=true;refresh(panel);
assert.equal(bar.hidden,true,'Hidden modeler still hides toolbar');
state.selected=null;panel.hidden=false;refresh(panel);
panel.nodes['#modelAtelierMeshQuickStrip']=null;
refresh(panel);
assert.equal(bar.hidden,false,'Transient native strip replacement does not remove history');
assert.equal(toolbarBtns.find(x=>x.dataset.se320History==='redo').disabled,false);
assert.equal(toolbarBtns.find(x=>x.dataset.se320Transform==='move').disabled,true);
console.log('SE463_TRANSFORM_HISTORY_PASS: selected, Undo deselection, Redo and remount fallback with native status/disabled gating');
