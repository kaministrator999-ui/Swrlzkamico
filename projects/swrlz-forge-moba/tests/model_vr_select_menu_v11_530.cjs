#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2],'utf8');
function section(start,end){
 const a=html.indexOf(start),b=html.indexOf(end,a+start.length);
 assert(a>=0&&b>a,'Missing native source section '+start);
 return html.slice(a,b);
}
const stage=section('/* SE445_VR_PROGRESSIVE_TOOLS_START','/* SE445_VR_PROGRESSIVE_TOOLS_END');
const ui=section('/* SE360_MODEL_VR_UI_START','/* SE360_MODEL_VR_UI_END');
const selector=section('/* SE376_VR_SELECTOR_LASSO_START','/* SE376_VR_SELECTOR_LASSO_END');
const pairRe=/\['([^']+)','([^']+)'\]/g;
const pairs=s=>[...s.matchAll(pairRe)].map(m=>[m[1],m[2]]);
const row=stage.split('\n').find(x=>x.trim().startsWith('inspect:[['));
assert(row,'Missing native Modeling Lab Select operation rail');
assert.deepEqual(pairs(row),[
 ['selector-sweep','Sweep'],['selector-lasso','Lasso'],['selection-clear','Clear Selection']
],'Select should expose exactly three purposeful actions');
assert(stage.includes("detailsOpen=category==='inspect'?item.action==='selector-lasso':category==='create-menu'?item.action==='create-pouch':category==='draw'?false:true"),
 'Only Lasso in Select and Pouch in Create should open contextual native settings');
const objects=stage.split('\n').find(x=>x.trim().startsWith('objects:[['));
assert(objects,'Missing Objects category');
assert(!pairs(objects).some(x=>x[0]==='selection-clear'),'Clear Selection duplicated under Objects');
assert(pairs(objects).some(x=>x[0]==='focus'),'Focus Selection must remain in Objects');
const page=ui.match(/^\s*selector:\[\n([\s\S]*?)^\s*\],/m);
assert(page,'Missing native selector modifier panel');
assert.deepEqual(pairs(page[1]),[['selector-depth','Depth: Front']],
 'Third stage must be dedicated to depth settings, not duplicate Select tools');
assert(ui.includes("if(id==='selector-depth')return ['lasso-front','lasso-through'].includes(state.selectionMode)"),
 'Depth must be contextual to Lasso');
assert(ui.includes("item.id==='selector-depth')return state.selectionMode==='lasso-through'?'Depth: Through':'Depth: Front'"),
 'Current depth needs a dynamic label');
assert(ui.includes("selector:['Lasso settings','DEPTH · FRONT / THROUGH']"));
assert(selector.includes('function se376LassoCommit(')&&selector.includes('function se376SelectionBand('),
 'Real VR lasso geometry and front-depth filtering must be retained');
assert(html.includes('function se372SweepFrame('),'Reversible sweep implementation must survive');
assert(selector.includes("purpose==='pan'&&record.input?.handedness==='left'"),
 'Left Grip lasso gesture must remain');
assert(selector.includes('if(already.size>=32)'),'Selection-limit guard must survive');
assert(selector.includes("se376SelectionMode==='lasso-through'?'lasso-front':'lasso-through'"),
 'Lasso Depth must switch the existing front and through modes');
assert(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_530_QUEST_GIZMO_CONTROLLER_MENU'));
assert(stage.includes("['labs','Labs','labs']")&&stage.includes("['projects','Projects','projects']")&&stage.includes("['undo','Undo'],['redo','Redo']"),
 'Labs, Projects and durable history controls must be preserved');
// Execute the real compiled selection-mode router in isolation with mocked
// UI dependencies: prove Sculpt/Draw is disarmed and Depth cycles.
const begin=selector.indexOf('function se376PanelMode(action){');
const end=selector.indexOf('\nfunction se376ShouldLasso(',begin);
assert(begin>=0&&end>begin,'Could not isolate real selection mode handler');
const src=selector.slice(begin,end);
const s={mode:'sculpt',page:'sculpt',se376SelectionMode:'sweep',gesture:null};
const messages=[];let sync=0,publish=0,cancel=0;
const router=Function('se340XR','se340CancelGesture','se340Notice','se340SyncUI','se340Publish',
 src+'\nreturn se376PanelMode;'
)(s,()=>{cancel++;s.gesture=null},m=>messages.push(m),()=>{sync++},()=>{publish++});
assert.equal(router('selector-lasso'),true);
assert.deepEqual([s.mode,s.page,s.se376SelectionMode],['inspect','selector','lasso-front']);
assert.equal(router('selector-depth'),true);
assert.equal(s.se376SelectionMode,'lasso-through');
assert.equal(router('selector-depth'),true);
assert.equal(s.se376SelectionMode,'lasso-front');
s.mode='draw';s.gesture={kind:'draw'};
assert.equal(router('selector-sweep'),true);
assert.equal(cancel,1);
assert.deepEqual([s.mode,s.page,s.se376SelectionMode],['inspect','selector','sweep']);
assert.equal(router('selector-lasso-through'),true);
assert.equal(s.se376SelectionMode,'lasso-through','old shortcut still supported');
assert.equal(router('selector-lasso'),true);
assert.equal(s.se376SelectionMode,'lasso-through','Lasso retains chosen depth');
assert.equal(router('nonsense-action'),false);
assert(sync>=5&&publish>=5&&messages.some(x=>/Through/.test(x)));
console.log('SE524_SELECT_MENU_PASS: 3 operations, contextual native depth, real sweep/lasso handlers, clean mode switch');
