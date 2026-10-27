import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const css=fs.readFileSync(root+'runtime/engine_runtime_fullscreen_v11_147.css','utf8');
const js=fs.readFileSync(root+'runtime/engine_runtime_fullscreen_v11_147.js','utf8');
for(const token of [
 'body.se145-runtime .viewport-wrap:has(> #viewport)',
 'position:fixed!important',
 'height:100dvh!important',
 'body.se145-runtime .viewport-wrap > #viewport',
 'height:100%!important',
 'body.se145-menu .viewport-wrap > #st141RuntimeMenu',
 'body.se145-menu .viewport-wrap > #st141RuntimeMenu .se146-screen',
 'body.se145-runtime .viewport-wrap > #se145ExitEditor',
 'bottom:max(9px,env(safe-area-inset-bottom))'
])assert.ok(css.includes(token),'missing runtime geometry repair '+token);
assert.ok(!css.includes('body:not(.se145-runtime) .viewport-wrap'),'must not change edit layout');
assert.ok(!js.includes('setInterval('),'no second render/resize loop');
let mode='',fit=0,resize=0,schedule=[];
const canvas={parentElement:{tagName:'MAIN'},getBoundingClientRect(){return {width:412,height:915}}};
const classes={contains:name=>name==='se145-runtime'&&!!mode};
const context={
 Event:class{constructor(type){this.type=type}},
 window:{SWYRL_ENGINE_LEVELS:{status:()=>({baseline:'okay'})},dispatchEvent(event){
  assert.equal(event.type,'resize');resize++;
 }},
 requestAnimationFrame(fn){schedule.push(fn);},
 se145:{get mode(){return mode}},
 se143ViewportHost:()=>canvas.parentElement,
 se143FitCanvasRect(){fit++;},se145SyncRuntime(){
  mode=this.nextMode||'';
 },
 document:{body:{classList:classes}},$:id=>id==='viewport'?canvas:null
};
context.se145SyncRuntime=function(){mode=context.nextMode||'';};
vm.createContext(context);vm.runInContext(js,context,{filename:'v11_147_runtime.js'});
context.nextMode='menu';context.se145SyncRuntime();
assert.equal(resize,1,'native resize immediately after entering menu');
assert.equal(fit,2,'overlay is fitted before and after native resize');
assert.equal(schedule.length,1,'one deferred post-layout refit');
schedule.shift()();assert.equal(resize,2);assert.equal(fit,4);
let receipt=context.window.SWYRL_ENGINE_LEVELS.status().runtimeViewportRepair;
assert.equal(receipt.mode,'menu');assert.equal(receipt.canvasHeight,915);assert.ok(receipt.hostMatchesCanvas);
context.se145SyncRuntime();assert.equal(resize,2,'idle menu refresh must not create a new loop');
context.nextMode='game';context.se145SyncRuntime();assert.equal(resize,3,'game transition reflows existing canvas');
schedule.shift()();
context.nextMode='';context.se145SyncRuntime();assert.equal(resize,5,'Stop reflows original editor');
schedule.shift()();
receipt=context.window.SWYRL_ENGINE_LEVELS.status().runtimeViewportRepair;
assert.equal(receipt.fullscreen,false);
assert.equal(receipt.mode,'');
console.log('SE147_FULLSCREEN_CANVAS_MENU_LAN_EXIT_EDITOR_REFIT_AND_STOP_RESTORE_PASS');
