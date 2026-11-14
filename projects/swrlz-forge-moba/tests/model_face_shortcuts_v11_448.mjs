#!/usr/bin/env node
// Focused §E v11.448 shortcut routing and discoverability without geometry mutation.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(process.argv[2],'utf8');
for(const needle of [
 'SE445_SCULPT_FACE_SHORTCUTS_START',
 'SE445_VR_PROGRESSIVE_TOOLS_START',
 'SWYRL_ENGINE_MODEL_VR_PROGRESSIVE_445',
 'SE445_SHAPE_DISCOVERY_START',
 "['manual-inset','Inset face'],['manual-extrude','Extrude face']",
 "['manual-mesh','Face tools','manual-mesh']",
 "faceQuick.id='se445ShapeQuick'",
 'data-se445-op="inset"',
 'data-se445-op="extrude"',
 'data-se445-op="solidify"',
 'data-se445-op="more"',
 "if(operation==='more'){",
 "se448ShapeQuickActivate(faceQuick,operation)"
]){
 assert.ok(html.includes(needle),'Missing visible native shortcut: '+needle);
}
const start='/* SE445_SCULPT_FACE_SHORTCUTS_START */',end='/* SE445_SCULPT_FACE_SHORTCUTS_END */';
const a=html.indexOf(start),b=html.indexOf(end,a);
assert.ok(a>=0&&b>a,'Missing scoped VR shortcut adapter');
const script=html.slice(a,b+end.length);

function scenario({mode='mesh',partId='part-1',count=1,manual=false,success=true}={}){
 let selectionMode=mode,edits=0,switches=0;
 const xr={se430Manual:manual};
 const actions=[];
 const native=(action)=>{
  actions.push(action);
  if(action==='manual-mesh'&&success)xr.se430Manual=true;
  return success;
 };
 const api={
  inspect:()=>({selection:{partId,mode:selectionMode,objectCount:count}}),
  setComponentMode:(value)=>{switches++;selectionMode=value;return {ok:true};}
 };
 const context=vm.createContext({
  se340ModelXRAction:native,se340XR:xr,se430VRWorkshop:()=>api,
  se340Notice:()=>{},window:{}
 });
 vm.runInContext(script,context);
 assert.equal(context.window.SWYRL_ENGINE_FACE_TOOLS_445.modelEditsOnShortcut,false);
 context.se340ModelXRAction('manual-inset');
 return {actions,switches,selectionMode,edits,context};
}
let run=scenario();
assert.deepEqual(run.actions,['manual-mesh','manual-inset']);
assert.equal(run.selectionMode,'face');
assert.equal(run.switches,1);
run=scenario({mode:'face'});
assert.deepEqual(run.actions,['manual-mesh','manual-inset']);
assert.equal(run.switches,0);
run=scenario({partId:null});
assert.deepEqual(run.actions,['manual-mesh','manual-inset']);
assert.equal(run.switches,0);
run=scenario({count:2});
assert.deepEqual(run.actions,['manual-mesh','manual-inset']);
assert.equal(run.switches,0);
run=scenario({manual:true});
assert.deepEqual(run.actions,['manual-inset']);
run=scenario({success:false});
assert.deepEqual(run.actions,['manual-mesh']);
assert.equal(run.switches,0);
console.log('§E v11.448 Sculpt → native face workshop shortcuts: passed');
