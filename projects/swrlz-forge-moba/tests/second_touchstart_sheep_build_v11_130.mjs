import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{JSDOM}=require(process.env.SE_JSDOM_MODULE);
const root='projects/swrlz-forge-moba/';
const code=fs.readFileSync(root+'runtime/engine_second_touchstart_zoom_guard_v11_130.js','utf8');
const dom=new JSDOM('<div id="projectHub"><button data-project-template="sheep-tag-meadow">Sheep Tag</button></div><div id="viewport"></div><input id="field">',{url:'https://example.test/'});
let now=0;const c={window:dom.window,document:dom.window.document,performance:{now:()=>now},console};
vm.createContext(c);vm.runInContext(code,c);
const button=c.document.querySelector('button'),viewport=c.document.getElementById('viewport'),input=c.document.getElementById('field');
const point=(id,x,y)=>({identifier:id,clientX:x,clientY:y});
function dispatch(type,target,changed,touches){
 const e=new dom.window.Event(type,{bubbles:true,cancelable:true});
 Object.defineProperty(e,'changedTouches',{value:changed});
 Object.defineProperty(e,'touches',{value:touches});
 target.dispatchEvent(e);return e;
}
let p=point(1,10,12);
assert.equal(dispatch('touchstart',button,[p],[p]).defaultPrevented,false);
now=90;
assert.equal(dispatch('touchend',button,[p],[]).defaultPrevented,false);
now=170;
const second=point(2,30,40);
const secondStart=dispatch('touchstart',viewport,[second],[second]);
assert.equal(secondStart.defaultPrevented,true,'second touchstart intercepted before browser page zoom');
assert.equal(dispatch('touchend',viewport,[second],[]).defaultPrevented,true,'cancel second touchend too');
now=900;const distant=point(3,4,6);
assert.equal(dispatch('touchstart',viewport,[distant],[distant]).defaultPrevented,false,'guard expires');
dispatch('touchend',viewport,[distant],[]);
// Checkbox/field usage is not affected by stale transition guard.
now=1100;p=point(4,8,9);dispatch('touchstart',button,[p],[p]);now=1150;dispatch('touchend',button,[p],[]);
now=1230;p=point(5,1,1);
assert.equal(dispatch('touchstart',input,[p],[p]).defaultPrevented,false,'editable inputs preserved');
dispatch('touchend',input,[p],[]);
now=2000;p=point(6,15,15);
dispatch('touchstart',button,[p],[p]);now=2050;dispatch('touchend',button,[point(6,40,40)],[]);
now=2090;p=point(7,20,20);
assert.equal(dispatch('touchstart',viewport,[p],[p]).defaultPrevented,false,'swipe does not arm double-tap');
dispatch('touchend',viewport,[p],[]);
now=3000;p=point(8,10,10);
dispatch('touchstart',button,[p],[p]);now=3040;dispatch('touchend',button,[p],[]);
now=3070;
const two=[point(9,20,20),point(10,35,35)];
assert.equal(dispatch('touchstart',viewport,[two[1]],two).defaultPrevented,false,'true two-finger pinch not cancelled');
dispatch('touchend',viewport,[two[0]], [two[1]]);
dispatch('touchend',viewport,[two[1]],[]);
const assembled=process.env.SE_ASSEMBLED_HTML&&fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
if(assembled){
 for(const key of [
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_130_SECOND_TOUCH_BROWSER_ZOOM_AND_SHEEP_BUILD_SEED',
  'se130InstallSecondTapProtection','st126SeedAtSheep','se129InstallProjectTapGuard',
  "if(stBuildInput.source==='skill')return; // do not aim at the skill icon or finger",
  "if(source==='skill'){",
  "stBuildInputFinish('Tool selected',true);",
  "stUiFeedback('Preview begins at your sheep. Touch the meadow to aim, then release to build.')"
 ])assert.ok(assembled.includes(key),'missing integrated behavior '+key);
 const start=assembled.indexOf("window.addEventListener('pointerup',event=>{",assembled.indexOf('const stBuildInput='));
 assert.ok(start>0,'native build pointer handler exists');
 const part=assembled.slice(start,start+2100);
 assert.ok(part.indexOf("if(source==='skill'){")<part.indexOf("stBuildInputAim(event);"),'skill cannot aim from pressed icon on release');
 const mStart=assembled.indexOf("window.addEventListener('pointermove',event=>{",assembled.indexOf('const stBuildInput='));
 const mPart=assembled.slice(mStart,mStart+850);
 assert.ok(mPart.indexOf("if(stBuildInput.source==='skill')return;")<mPart.indexOf("stBuildInputAim(event);"),'skill cannot aim from finger drag');
 // The original meadow aiming and safe native build path must remain.
 assert.ok(part.includes("stUiOrderAt(event.clientX,event.clientY)"),'meadow release still commits');
 // Extract and execute the native pointerup callback from the assembled HTML.
 const snippet=assembled.slice(start,assembled.indexOf('},true);',start)+8);
 const handlers={};let aims=0,seeds=0,finish=0;
 const fake={window:{addEventListener:(type,cb)=>handlers[type]=cb},
  stBuildInput:{pointer:2,source:'skill',session:{},moved:false},
  stTouchPlacementEnabled:()=>true,stSession:{},st126SeedAtSheep:()=>{seeds++;return true},
  stBuildInputFinish:()=>{finish++},stBuildInputAim:()=>{aims++},stUiFeedback:()=>{},
  stTouchPlacement:{valid:true},stUi:{placement:{ok:true}},stUiOrderAt:()=>{},stBuildInputReject:()=>{}};
 fake.stBuildInput.session=fake.stSession;
 vm.createContext(fake);vm.runInContext(snippet,fake);
 assert.equal(typeof handlers.pointerup,'function');
 handlers.pointerup({pointerId:2,preventDefault(){},stopImmediatePropagation(){},clientX:600,clientY:12});
 assert.equal(seeds,1,'native skill release reseeds at the sheep');
 assert.equal(aims,0,'skill release never aims using button coordinates');
 assert.equal(finish,1,'tool gesture ends without placing building');
}
console.log('SE130_SECOND_TOUCHSTART_AND_SHEEP_CENTERED_BUTTON_ORIGIN_PASS');
