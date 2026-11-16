import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../runtime/model_tool_rail_fold_v11_473.js',import.meta.url),'utf8');
new vm.Script(source);
const saved=new Map();
const elements=[];
const eventMap=new Map();
const button={
 id:'',type:'',className:'',textContent:'',title:'',attributes:{},
 setAttribute(k,v){this.attributes[k]=v;},
 addEventListener(k,cb){eventMap.set(k,cb);},
 click(){eventMap.get('click')?.();}
};
const rail={
 _button:null,
 querySelector(selector){return selector==='#se473RailFold'?this._button:null;},
 prepend(btn){this._button=btn;}
};
const panel={
 dataset:{},
 querySelector(selector){return selector==='#modelAtelierToolRail'?rail:null;}
};
const document={
 readyState:'complete',body:{},
 getElementById(id){return id==='modelAtelierPanel'?panel:id==='se473RailFold'?rail._button:null;},
 createElement(tag){assert.equal(tag,'button');return button;}
};
let resizeEvents=0;
class MutationObserver{constructor(cb){this.cb=cb;}observe(){}}
const ctx={document,localStorage:{getItem:k=>saved.get(k)||null,setItem:(k,v)=>saved.set(k,v)},
 MutationObserver,window:{dispatchEvent(e){if(e.type==='resize')resizeEvents++;}},
 Event:class{constructor(type){this.type=type;}},queueMicrotask};
const api=vm.runInNewContext(source+'\nwindow.SWYRL_ENGINE_TOOL_RAIL_473',ctx);
assert.equal(panel.dataset.se473RailCollapsed,'false');
assert.equal(button.attributes['aria-expanded'],'true');
assert.equal(rail._button,button);
button.click();
assert.equal(panel.dataset.se473RailCollapsed,'true');
assert.equal(button.attributes['aria-expanded'],'false');
assert.equal(saved.get('swyrl.engine.modeler.tool-rail-fold.v1'),'collapsed');
button.click();
assert.equal(panel.dataset.se473RailCollapsed,'false');
assert.equal(saved.get('swyrl.engine.modeler.tool-rail-fold.v1'),'expanded');
assert.equal(resizeEvents,2);
assert.equal(api.state().collapsed,false);
console.log('SE473_TOOL_RAIL_FOLD_PASS: native top handle, collapsed state, persistence, aria and layout updates');
