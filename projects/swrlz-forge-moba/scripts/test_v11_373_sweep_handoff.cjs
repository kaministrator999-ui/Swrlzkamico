'use strict';
// Regression for the native selection refresh clearing cached XR hover.
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const path=require('node:path');
const html=fs.readFileSync(process.argv[2],'utf8');
for(const needle of [
 'record.hit=hit;record.se372TriggerHit=hit;',
 'se372SweepStart(record,before,record.se372TriggerHit);record.se372TriggerHit=null;',
 'function se372SweepStart(record,before,hit){',
 'const s=se340XR;hit=hit||record.hit;'
])assert.ok(html.includes(needle),'Missing press-hit handoff '+needle);
const start=html.indexOf('/* SE372_MODEL_VR_PHASE1_START */'),end=html.indexOf('/* SE372_MODEL_VR_PHASE1_END */',start);
assert.ok(start>=0&&end>start);
let selections=['ear','staff-grip'];const record={targetTracked:true,hit:null};
const s={mode:'inspect',gesture:null,se372Sweep:null,inputSample:{buttons:{LT:{physical:true}}}};
const sandbox={se340XR:s,performance:{now:()=>75},se340VisibleSession:()=>true,
 se350Tools:()=>({selection:()=>({ids:selections.slice()}),select:(part,{additive})=>{
  if(!additive)selections=[part];
  else if(selections.includes(part))selections=selections.filter(v=>v!==part);
  else selections.push(part);
  return {ok:true};
 }}),se350Invalidate:()=>{},se340Pulse:()=>{},se340Notice:()=>{},
 se350Result:()=>{},localStorage:{getItem:()=>null,setItem:()=>{},removeItem:()=>{}}};
vm.createContext(sandbox);
vm.runInContext(html.slice(start,end),sandbox);
sandbox.se372SweepStart(record,['ear'],{id:'staff-grip',ui:false,name:'Grip'});
assert.ok(s.se372Sweep,'Starts from preserved hit even after hover invalidation');
record.hit={id:'staff-tip',ui:false};sandbox.se372SweepFrame(s);
assert.deepEqual(selections,['ear','staff-grip','staff-tip']);
record.hit={id:'staff-grip',ui:false};sandbox.se372SweepFrame(s);
assert.deepEqual(selections,['ear','staff-grip'],'Reverse only removes sweep-added part');
assert.ok(selections.includes('ear'),'Existing selection preserved');
console.log('v11.373 trigger-hit handoff and reverse sweep PASS');
