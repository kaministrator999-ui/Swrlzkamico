const vm=require('node:vm'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../runtime/chat_outside_dismiss_v11_180.js'),'utf8');
const listeners={},buttons={},panel={hidden:true,inert:true,src:'',
 classList:{states:new Set(),add(v){this.states.add(v)},remove(v){this.states.delete(v)},contains(v){return this.states.has(v)}},
 contains(t){return t===this||t===buttons.inside},
 setAttribute(k,v){this[k]=v},removeAttribute(k){delete this[k]}};
const toggle={focusCount:0,
 setAttribute(k,v){this[k]=v},focus(){this.focusCount++},
 contains(t){return t===this}},closeButton={focusCount:0,focus(){this.focusCount++}};
const frame={src:''},timers=new Map(),frames=new Map();let next=1,revokes=0,sendCount=0;
const context={window:{matchMedia:()=>({matches:false})},
 document:{getElementById:id=>id==='seChatToggle'?toggle:id==='seChatClose'?closeButton:null,
 addEventListener:(key,handler,capture)=>{listeners[key]={handler,capture}}},
 panel,open:false,frame,CHAT_ORIGIN:'https://chat.example.test',port:null,
 revoke:()=>{revokes++},send:()=>{sendCount++},
 requestAnimationFrame:cb=>{const id=next++;frames.set(id,cb);return id},
 cancelAnimationFrame:id=>frames.delete(id),
 setTimeout:(cb,ms)=>{const id=next++;timers.set(id,{cb,ms});return id},
 clearTimeout:id=>timers.delete(id),
};
vm.createContext(context);vm.runInContext(source,context);
function frameNext(){const all=[...frames.entries()];frames.clear();for(const [,f] of all)f()}
function settle(){const all=[...timers.entries()];timers.clear();for(const [,t] of all)t.cb()}
function down(target,type='pointerdown',mouse='touch',button=0){
 const e={type,pointerType:mouse,button,isPrimary:true,target,composedPath:()=>[target]};listeners[type].handler(e);
}
vm.runInContext('se180InstallDismiss()',context);
assert.equal(listeners.pointerdown.capture,true);
assert.equal(listeners.click.capture,true);
vm.runInContext('openPanel()',context);frameNext();
assert.equal(context.open,true);assert.equal(panel.hidden,false);
assert.equal(panel.classList.contains('se180-chat-visible'),true);
assert.equal(toggle['aria-expanded'],'true');assert.equal(frame.src,'https://chat.example.test/?forgeEmbed=1');
down(buttons.inside={});assert.equal(context.open,true,'inside Chat does not close it');
down(toggle);assert.equal(context.open,true,'Chat toggle is not treated as outside');
down({id:'canvas'},'pointerdown','mouse',2);assert.equal(context.open,true,'right click stays available');
const focusBefore=toggle.focusCount;
down({id:'editor-handle'});assert.equal(context.open,false);
assert.equal(toggle.focusCount,focusBefore,'outside tap does not steal editor focus');
assert.equal(revokes,1);assert.equal(panel.inert,true);
assert.equal(panel.classList.contains('se180-chat-visible'),false);
assert.equal(panel.hidden,false,'panel stays mounted during exit transition');
settle();assert.equal(panel.hidden,true);
assert.equal(frame.src,'https://chat.example.test/?forgeEmbed=1','same iframe retained');
vm.runInContext('openPanel()',context);frameNext();
assert.equal(panel.hidden,false);assert.equal(toggle['aria-expanded'],'true');
down({id:'workspace'});vm.runInContext('openPanel()',context);frameNext();settle();
assert.equal(panel.hidden,false,'stale close timer cannot hide a reopened Chat');
vm.runInContext('closePanel()',context);settle();
assert.equal(toggle.focusCount,focusBefore+1,'explicit close restores focus');
assert.equal(frame.src,'https://chat.example.test/?forgeEmbed=1');
console.log('SE_CHAT_OUTSIDE_DISMISS_PASS');
