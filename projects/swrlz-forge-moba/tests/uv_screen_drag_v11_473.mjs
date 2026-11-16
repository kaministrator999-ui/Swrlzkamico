import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../runtime/model_uv_screen_drag_v11_473.js',import.meta.url),'utf8');
new vm.Script(source);
const saved=new Map();
const popup={
 hidden:false,style:{width:'',height:'',left:'',top:'',right:'',bottom:''},
 getBoundingClientRect(){
  return {width:parseFloat(this.style.width)||480,height:parseFloat(this.style.height)||620,
   left:parseFloat(this.style.left)||0,top:parseFloat(this.style.top)||0};
 }
};
const context={popup,innerWidth:868,innerHeight:860,
 window:{visualViewport:{offsetLeft:0,offsetTop:0,width:868,height:860}},
 localStorage:{getItem:k=>saved.get(k)||null,setItem:(k,v)=>saved.set(k,v)},
 JSON,Math,Number};
const api=vm.runInNewContext(source+'\n({safeBounds,fitWindow,se473RememberWindow,se473SavedWindow})',context);
api.fitWindow(true);
const first=popup.getBoundingClientRect();
assert(first.left>=400,'Default UV window should be off to the right, allowing model inspection');
assert(first.top>=6&&first.top+first.height<=854);
assert(first.width<=856);
popup.style.left='15px';popup.style.top='20px';
api.se473RememberWindow();
popup.style.left='600px';popup.style.top='370px';
api.fitWindow(true);
assert.equal(popup.getBoundingClientRect().left,15);
assert.equal(popup.getBoundingClientRect().top,20);
assert.equal(api.se473SavedWindow().width,first.width);
popup.style.left='-900px';popup.style.top='-700px';
api.fitWindow(false);
assert(popup.getBoundingClientRect().left>=6);
assert(popup.getBoundingClientRect().top>=6);
popup.style.left='9999px';popup.style.top='9999px';
api.fitWindow(false);
assert(popup.getBoundingClientRect().left+popup.getBoundingClientRect().width<=862.0001);
assert(popup.getBoundingClientRect().top+popup.getBoundingClientRect().height<=854.0001);
context.window.visualViewport={offsetLeft:0,offsetTop:0,width:393,height:700};
api.fitWindow(false);
assert(popup.getBoundingClientRect().width<=381);
assert(popup.getBoundingClientRect().left>=6);
assert(popup.getBoundingClientRect().top+popup.getBoundingClientRect().height<=694.0001);
popup.hidden=true;const before={...popup.style};
api.fitWindow(true);
assert.deepEqual(popup.style,before,'Hidden UV dialog should not jump or mutate');
console.log('SE473_UV_SCREEN_DRAG_PASS: free browser bounds, saved x/y/size, resize/clamp, no hidden changes');
