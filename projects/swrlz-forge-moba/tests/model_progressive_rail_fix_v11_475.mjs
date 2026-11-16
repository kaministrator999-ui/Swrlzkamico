import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../runtime/model_progressive_rail_fix_v11_475.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../runtime/model_progressive_rail_fix_v11_475.css',import.meta.url),'utf8');
new vm.Script(source);
for(const required of ['.atelier-body>#se474ToolFlyout','data-se475-family-state=selected',
 'data-se475-family-state=idle','--se475-flyout-x','--se475-modes-y',
 'data-se475-mounted=true','[hidden]'])assert(css.includes(required),required);
class Element{
 constructor(name,bounds={left:0,top:0,width:0,height:0}){
  this.name=name;this._rect={...bounds,right:bounds.left+bounds.width,bottom:bounds.top+bounds.height};
  this.children=[];this.parentElement=null;this.isConnected=true;this.attrs={};
  this.textContent=name;this.dataset={};this.hidden=false;this.listeners={};
  this.style={vars:{},setProperty:(k,v)=>{this.style.vars[k]=v;}};
 }
 append(child){
  if(child.parentElement)child.parentElement.children=child.parentElement.children.filter(x=>x!==child);
  this.children.push(child);child.parentElement=this;
 }
 querySelector(sel){return this.map?.[sel]||null;}
 querySelectorAll(sel){
  if(sel!==':scope > button'&&sel!==':scope > button[aria-pressed="true"]')return [];
  const buttons=this.children.filter(x=>x.name!=='flyout');
  return sel.includes('aria-pressed')?buttons.filter(b=>b.getAttribute('aria-pressed')==='true'):buttons;
 }
 getBoundingClientRect(){return this._rect;}
 setAttribute(key,val){this.attrs[key]=String(val);}
 getAttribute(key){return this.attrs[key]??null;}
 addEventListener(name,callback){this.listeners[name]=callback;}
}
const body=new Element('body',{left:0,top:0,width:800,height:600});
const rail=new Element('rail',{left:724,top:50,width:76,height:550});
const flyout=new Element('flyout',{left:0,top:0,width:212,height:330});
const top=new Element('top',{left:0,top:0,width:520,height:47});
const scene=new Element('scene',{left:180,top:0,width:544,height:600});
const transform=new Element('transform',{left:185,top:20,width:375,height:42});
const meshes=new Element('Meshes',{left:730,top:110,width:64,height:43});
const sculpt=new Element('Sculpt',{left:730,top:170,width:64,height:43});
meshes.setAttribute('aria-pressed','true');sculpt.setAttribute('aria-pressed','false');
rail.append(meshes);rail.append(sculpt);rail.append(flyout);
const panel=new Element('panel');panel.dataset.se251Layout='desktop';
panel.map={
 '.atelier-body':body,'#modelAtelierToolRail':rail,'#se474ToolFlyout':flyout,
 '#se474SpecificModes':top,'.atelier-scene':scene,'#se320ModelTransform':transform
};
const doc={readyState:'complete',body,
 getElementById:id=>id==='modelAtelierPanel'?panel:null};
let progress={family:'Sculpt'};
const win={SWYRL_ENGINE_PROGRESSIVE_TOOLS_474:{inspect:()=>progress},addEventListener(){}};
class MutationObserver{observe(){}}
const ctx={document:doc,window:win,MutationObserver,queueMicrotask};
vm.runInNewContext(source,ctx);
await Promise.resolve();await Promise.resolve();
const api=win.SWYRL_ENGINE_PROGRESSIVE_RAIL_475;
assert.equal(api.inspect().mounted,true);
assert.equal(api.inspect().flyoutInBody,true,'Flyout must leave clipped rail without cloning its controls');
assert.equal(flyout.parentElement,body);
assert.equal(sculpt.getAttribute('aria-pressed'),'true');
assert.equal(meshes.getAttribute('aria-pressed'),'false','Previous active category must release');
assert.deepEqual(Array.from(api.inspect().activeRailButtons),['Sculpt']);
assert.equal(flyout.style.vars['--se475-flyout-x'],'506px','Flyout must appear LEFT of vertical rail');
assert.equal(flyout.style.vars['--se475-flyout-y'],'166px','Flyout should align to Sculpt button');
assert.equal(top.style.vars['--se475-modes-x'],'186px');
assert.equal(top.style.vars['--se475-modes-y'],'69px','Mode strip should start BELOW native transform bar');
progress.family='Meshes';api.refresh();await Promise.resolve();await Promise.resolve();
assert.equal(meshes.getAttribute('aria-pressed'),'true');
assert.equal(sculpt.getAttribute('aria-pressed'),'false');
panel.dataset.se251Layout='compact';
rail._rect={left:0,top:550,width:800,height:50,right:800,bottom:600};
meshes._rect={left:110,top:555,width:80,height:42,right:190,bottom:597};
api.refresh();await Promise.resolve();await Promise.resolve();
assert.equal(flyout.dataset.se475Placement,'compact');
assert(Number.parseInt(flyout.style.vars['--se475-flyout-y'])<550,'Compact flyout must remain ABOVE horizontal rail');
console.log('SE475_PROGRESSIVE_VISIBILITY_PASS: relocated live flyout, exclusive family highlight, vertical and compact placement, top strip beneath transforms');
