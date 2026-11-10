/* Focused contract test: left-trigger reversible sweep does not erase earlier selections. */
'use strict';
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../runtime/model_vr_phase1_v11_372.js'),'utf8');
let now=0, selections=['existing','staff-a'];
const record={targetTracked:true,hit:{id:'staff-a',ui:false},pulseAt:0};
const workspace={mode:'inspect',gesture:null,se372Sweep:null,
 inputSample:{buttons:{LT:{physical:true}}}};
const ui=[];
const ctx={
 se340XR:workspace,performance:{now:()=>now},se340VisibleSession:()=>true,
 se350Tools:()=>({selection:()=>({ids:selections.slice()}),
  select:(id,{additive}={})=>{
   if(!additive){selections=id?[id]:[];return {ok:true};}
   if(selections.includes(id))selections=selections.filter(x=>x!==id);
   else if(selections.length<32)selections.push(id);
   else return {ok:false,error:'MODEL_SELECTION_LIMIT_32'};
   return {ok:true};
  }}),
 se350Invalidate:()=>{},se340Pulse:()=>{},se340Notice:m=>ui.push(m),
 se350Result:()=>{},localStorage:{getItem:()=>null,setItem:()=>{},removeItem:()=>{}}
};
vm.createContext(ctx);vm.runInContext(source,ctx,{filename:'model_vr_phase1_v11_372.js'});
ctx.se372SweepStart(record,['existing']);
assert.deepEqual(selections,['existing','staff-a']);
for(const [mesh,expected] of [
 ['staff-b',['existing','staff-a','staff-b']],
 ['staff-c',['existing','staff-a','staff-b','staff-c']],
 ['staff-b',['existing','staff-a','staff-b']],
 ['staff-a',['existing','staff-a']],
 ['staff-b',['existing','staff-a','staff-b']],
]){
 now+=50;record.hit={id:mesh,ui:false};ctx.se372SweepFrame(workspace);
 assert.deepEqual(selections,expected,'sweep path '+mesh);
}
workspace.inputSample.buttons.LT.physical=false;
ctx.se372SweepFrame(workspace);
assert.equal(workspace.se372Sweep,null,'release ends sweep');
assert.deepEqual(selections,['existing','staff-a','staff-b']);
assert.ok(ui.some(s=>s.includes('reverse sweep')));
console.log('v11.372 reversible sweep selection PASS');
