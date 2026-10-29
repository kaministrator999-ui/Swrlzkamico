// §E v11.117 native callout: test the exact runtime installed with fake DOM.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const code=fs.readFileSync('projects/swrlz-forge-moba/runtime/model_atelier_callout_guard_v11_117.js','utf8');
function node(parent=null){return {parent,closest(selector){
  if(this.editable && selector.includes('input'))return this;
  return null;
}}}
function contains(parent,target){
 for(let t=target;t;t=t.parent)if(t===parent)return true;
 return false;
}
const editor=node(),body=node(),pad=node(),view=node(editor),button=node(editor),
 label=node(editor),field=node(editor),outside=node(body),padButton=node(pad);
field.editable=true;
editor.contains=t=>contains(editor,t);
pad.contains=t=>contains(pad,t);
editor.hidden=false;pad.hidden=true;
const calls={};let registered=0;
const document={
 getElementById:id=>id==='modelAtelierPanel'?editor:id==='seMobileNumberPad'?pad:null,
 addEventListener:(name,listener,capture)=>{
  assert.equal(capture,true,'only capture-phase should guard long press');
  (calls[name]??=[]).push(listener);registered++;
 }
};
const context={document};vm.createContext(context);
vm.runInContext(code+';seAtelierCalloutInstall();seAtelierCalloutInstall();',context);
assert.equal(registered,2,'listeners registered more than once');
assert.deepEqual(Object.keys(calls).sort(),['contextmenu','selectstart']);
const trigger=(type,target)=>{
 let stopped=false;
 const event={target,preventDefault(){stopped=true}};
 for(const listener of calls[type])listener(event);
 return stopped;
};
assert.ok(trigger('contextmenu',view),'viewport browser menu permitted');
assert.ok(trigger('contextmenu',button),'tool button browser menu permitted');
assert.ok(trigger('contextmenu',field),'editable fields must also suppress browser contextmenu');
assert.ok(trigger('contextmenu',label),'label browser menu permitted');
assert.ok(!trigger('contextmenu',outside),'suppressed unrelated webpage menu');
assert.ok(trigger('selectstart',view),'non-editable viewport text selection permitted');
assert.ok(trigger('selectstart',button),'button text selection permitted');
assert.ok(!trigger('selectstart',field),'editable field caret/selection blocked');
assert.ok(!trigger('selectstart',outside),'outside selection blocked');
pad.hidden=false;
assert.ok(trigger('contextmenu',padButton),'editor numeric keypad missed');
assert.ok(trigger('selectstart',padButton),'numeric keypad selected');
pad.hidden=true;
assert.ok(!trigger('contextmenu',padButton),'hidden numeric keypad should not claim contextmenu');
editor.hidden=true;
assert.ok(!trigger('contextmenu',view),'closed editor still blocks browser');
assert.ok(!trigger('selectstart',button),'closed editor still blocks text selection');
assert.ok(!trigger('contextmenu',padButton),'closed editor affects unrelated dialogs');
console.log('SE_V11117_SCOPED_CONTEXTMENU_SELECTION_AND_EDITOR_GESTURES_PASS');
