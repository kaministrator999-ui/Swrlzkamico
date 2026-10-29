import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const css=fs.readFileSync('projects/swrlz-forge-moba/runtime/engine_site_touch_guard_v11_122.css','utf8');
const js=fs.readFileSync('projects/swrlz-forge-moba/runtime/engine_site_touch_guard_v11_122.js','utf8');
const listeners={};
const document={addEventListener:(name,fn,capture)=>{
 assert.equal(capture,true,'native menu must be intercepted in capture phase');
 (listeners[name]||=[]).push(fn);
}};
const window={};
vm.runInNewContext(js,{document,window});
vm.runInNewContext(js,{document,window});
assert.equal(listeners.contextmenu.length,1,'guard duplicated');
assert.equal(listeners.selectstart.length,1,'guard duplicated');
const ordinary={closest:()=>null};
const textbox={closest:selector=>selector.includes('input')?{tagName:'INPUT'}:null};
const nested={closest:selector=>selector.includes('[contenteditable]')?{tagName:'DIV'}:null};
const select={closest:()=>null};
function fire(type,target,path=[target]){
 let cancelled=0;
 const event={target,preventDefault(){cancelled++},composedPath:()=>path};
 for(const fn of listeners[type])fn(event);
 return cancelled;
}
for(const type of ['contextmenu','selectstart']){
 assert.equal(fire(type,ordinary),1,'normal engine surface '+type+' not cancelled');
 assert.equal(fire(type,textbox),0,'input field '+type+' unexpectedly cancelled');
 assert.equal(fire(type,nested),0,'contenteditable field '+type+' unexpectedly cancelled');
 assert.equal(fire(type,select,[select,textbox]),0,'composed shadow input '+type+' unexpectedly cancelled');
}
assert.ok(css.includes('html,body{touch-action:manipulation!important}'));
assert.ok(css.includes('-webkit-touch-callout:none!important'));
assert.ok(css.includes('-webkit-touch-callout:default!important'));
assert.ok(css.includes('-webkit-user-select:text!important'));
assert.ok(css.includes('body :where('),'non-editable text rule specificity too high');
assert.ok(!/maximum-scale\s*=/.test(css));
assert.ok(!css.includes('user-scalable=no'));
assert.ok(!css.includes('touch-action:none!important'));
assert.ok(!js.includes("addEventListener('pointerdown'"));
assert.ok(!js.includes("addEventListener('touchstart'"));
assert.ok(!js.includes('setTimeout('));
assert.ok(!js.includes('preventDefault();\n },false'));
const assembled=process.env.SE_ASSEMBLED_HTML;
if(assembled){
 const html=fs.readFileSync(assembled,'utf8');
 for(const x of ['V11_122_SITEWIDE_EDITOR_TOUCH_BOUNDARIES',
 'se-v11122-site-touch-guard','se-v11122-site-touch-script',
 'if(activeScope(event.target)&&!window.seEngineIsEditable(event.target))event.preventDefault();'])
  assert.ok(html.includes(x),'built HTML missing '+x);
}
console.log('SE_V11122_SITEWIDE_DOUBLE_TAP_AND_EDITABLE_CONTEXT_GUARDS_PASS');
