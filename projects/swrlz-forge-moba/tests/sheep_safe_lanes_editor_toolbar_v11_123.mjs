import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const snapJS=fs.readFileSync('projects/swrlz-forge-moba/runtime/sheep_safe_snap_v11_123.js','utf8');
const barJS=fs.readFileSync('projects/swrlz-forge-moba/runtime/engine_main_toolbar_v11_123.js','utf8');
const css=fs.readFileSync('projects/swrlz-forge-moba/runtime/engine_main_toolbar_sheep_hud_v11_123.css','utf8');
function house(x,z=0){return {kind:'st-farm',hp:180,pos:{x,z},halfX:1.2,halfZ:1.2};}
const state={rules:{sheepRadius:.27},buildings:[house(40)]};
const ctx={console,ST_GRID:.3,ST_LANE_HOUSES:new Set(['st-farm','st-income','st-fort','st-totem']),
stSession:state,stLanesSnapHouse:(_,x,z)=>({x,z}),
stCanBuild:(kind,x,z)=>{
 const pt=state.raw?{x,z}:ctx.stLanesSnapHouse(kind,x,z);
 return {kind,x:pt.x,z:pt.z,ok:true,cost:0};
},stResult:(ok,reason,fit)=>({...fit,ok,reason})};
vm.createContext(ctx);vm.runInContext(snapJS,ctx);
const snap=(x,z=0)=>ctx.stLanesSnapHouse('st-farm',x,z);
const build=(x,z=0)=>ctx.stCanBuild('st-farm',x,z);
assert.equal(ctx.stSafeLaneWidth(),.9);
assert.ok(Math.abs(snap(42.5).x-42.415)<1e-7,'adjacent contact failed');
assert.ok(Math.abs(snap(43.0).x-43.3)<1e-7,'sheep gap must be at least 0.9');
assert.ok(Math.abs(snap(46.16).x-46.2)<1e-7,'free grid step is 0.3');
assert.equal(build(43.0).ok,true,'0.9 m sheep lane erroneously blocked');
assert.equal(build(42.5).ok,true,'flush contact erroneously blocked');
state.raw=true;
assert.equal(build(42.9).ok,false,'off-grid 0.5m slit unexpectedly allowed');
assert.equal(build(43.3).ok,true,'safe 0.9m lane rejected');
state.raw=false;
// Explicit predicate catches narrow spaces even when later callers hand in
// coordinates that bypass the usual snap helper.
assert.ok(snapJS.includes('gapX>.025&&gapX<minLane-.025'));
assert.ok(snapJS.includes('gapZ>.025&&gapZ<minLane-.025'));
state.rules.sheepRadius=.5;
assert.equal(ctx.stSafeLaneWidth(),1.5);
state.rules.sheepRadius=.27;
const events={};
const children=[];
const parent={
 dataset:{},scrollLeft:77,
 prepend(b){const i=children.indexOf(b);if(i>=0)children.splice(i,1);children.unshift(b);}
};
const mk=(id,label)=>{
 const b={id,textContent:label,innerText:label,parentElement:parent,
 classList:{classes:new Set(),add(s){this.classes.add(s);}}};
 children.push(b);return b;
};
mk('worldModeBtn','World');mk('buildModeBtn','Build');
const projects=mk('projectHubBtn','▥ Projects'),play=mk('playBtn','▶ Play');
const pause=mk('pauseBtn','Ⅱ Pause'),simulate=mk('simulateBtn','● Simulate');
const stop=mk('stopBtn','■ Stop');
mk('saveBtn','Save');
const rootNode={querySelectorAll:()=>children};
const barCtx={document:{querySelector:selector=>selector==='.topbar'?rootNode:null,readyState:'loading',addEventListener:(type,fn)=>{events[type]=fn;}},requestAnimationFrame:()=>{}};
vm.createContext(barCtx);vm.runInContext(barJS,barCtx);
assert.equal(barCtx.seMainToolbarOrganize(),true);
assert.deepEqual(children.slice(0,5).map(b=>b.id),['projectHubBtn','playBtn','pauseBtn','simulateBtn','stopBtn']);
assert.equal(parent.scrollLeft,0);
assert.ok(projects.classList.classes.has('se-main-project-button'));
assert.equal(barCtx.seMainToolbarOrganize(),true,'idempotent organizer failed');
assert.deepEqual(children.slice(0,5).map(b=>b.id),['projectHubBtn','playBtn','pauseBtn','simulateBtn','stopBtn']);
assert.ok(css.includes('translate:calc(-1 * clamp(18px,4vw,28px)) 0!important'));
assert.ok(css.includes('left:max(38px,calc(env(safe-area-inset-left) + 30px))!important'));
assert.ok(css.includes('min-height:40px!important'));
if(process.env.SE_ASSEMBLED_HTML){
 const html=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 for(const text of ['V11_123_SHEEP_LANE_GRID_AND_WORKFLOW_TOOLBAR',
 'stSafeLaneWidth()', 'seMainToolbarOrganize()', 'se-v11123-workflow-safe-lanes',
 'const stSafeCanBuildBase=stCanBuild;']){
  assert.ok(html.includes(text),'missing assembled '+text);
 }
}
console.log('SE_V11123_SHEEP_SAFE_GRID_FLUSH_OR_PASSAGE_MAIN_HEADER_INSET_HUD_PASS');
