/* Quest VR selector contract: legacy sweep, opt-in Left Grip lasso and overlap depth modes. */
'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../runtime/model_vr_selector_lasso_v11_376.js'),'utf8');
const html=process.argv[2]?fs.readFileSync(process.argv[2],'utf8'):null;
if(html)for(const needle of [
 '/* SE376_VR_SELECTOR_LASSO_START */',
 "if(se376ShouldLasso(record,purpose))return se376LassoBegin(record,purpose);",
 "if(g.kind==='selection-lasso')return se376LassoCommit(g);",
 "if(g.kind==='selection-lasso'){se376LassoUpdate(g);return;}",
 "se376LassoDispose(g);se372GuideStop(g);",
 "function se372SweepFrame(s){", // original left trigger reversible swipe remains
 "['selector-lasso-front','Lasso · front']",
 "['selector-lasso-through','Lasso · through']",
 "['selector-sweep','Swipe · trigger']",
 "['selector','Select']",
 "['projects','Projects']",
 "if(action==='pan'&&s.page==='selector'"
])assert.ok(html.includes(needle),'Missing integrated selector behavior: '+needle);
const s={page:'tools',mode:'inspect',se376SelectionMode:'sweep',gesture:null};
const messages=[],modeStubs={
 se340XR:s,THREE:{MathUtils:{clamp:(x,a,b)=>Math.max(a,Math.min(b,x))}},
 se340Notice:m=>messages.push(m),se340SyncUI:()=>{},se340Publish:()=>{},
 se340CancelGesture:()=>{s.gesture=null}
};
vm.createContext(modeStubs);vm.runInContext(source,modeStubs);
const left={input:{handedness:'left'}},right={input:{handedness:'right'}};
const square=[{x:-.2,y:-.2},{x:.2,y:-.2},{x:.2,y:.2},{x:-.2,y:.2}];
assert.equal(modeStubs.se376Inside({x:0,y:0},square),true);
assert.equal(modeStubs.se376Inside({x:.4,y:0},square),false);
assert.equal(modeStubs.se376RectOverlap(square,-.1,-.1,.1,.1),true);
assert.equal(modeStubs.se376RectOverlap(square,.4,.4,.8,.8),false);
assert.equal(modeStubs.se376RectOverlap(square,-.3,-.01,.3,.01),true);
assert.ok(modeStubs.se376PolygonArea(square)>.10);
const parts=[{id:'staff-shaft',depth:1.12},{id:'staff-cap',depth:1.16},{id:'mage-robe',depth:1.45}];
assert.deepEqual([...modeStubs.se376SelectionBand(parts,.65,false)].map(x=>x.id),['staff-shaft','staff-cap']);
assert.deepEqual([...modeStubs.se376SelectionBand(parts,.65,true)].map(x=>x.id),parts.map(x=>x.id));
assert.equal(modeStubs.se376ShouldLasso(left,'pan'),false,'default Left Grip is workspace pan');
assert.equal(modeStubs.se376PanelMode('selector-lasso-front'),true);
assert.equal(modeStubs.se376ShouldLasso(left,'pan'),true,'selector front mode takes Left Grip');
assert.equal(modeStubs.se376ShouldLasso(right,'grab'),false,'right Grip stays a model transform');
assert.equal(modeStubs.se376ShouldLasso(left,'grab'),false,'only Left Grip workspace binding');
assert.equal(modeStubs.se376PanelMode('selector-lasso-through'),true);
assert.equal(s.se376SelectionMode,'lasso-through');
assert.equal(modeStubs.se376PanelMode('selector-sweep'),true);
assert.equal(modeStubs.se376ShouldLasso(left,'pan'),false,'Swipe mode restores regular Left Grip');
assert.equal(modeStubs.se376PanelMode('open-file'),false);
s.page='projects';s.se376SelectionMode='lasso-front';
assert.equal(modeStubs.se376ShouldLasso(left,'pan'),false,'leaving Selector restores workspace Grip');
console.log('v11.376 selector modes, overlap geometry, depth filtering and control isolation PASS');
