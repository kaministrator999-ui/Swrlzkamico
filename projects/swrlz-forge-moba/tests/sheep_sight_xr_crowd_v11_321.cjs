#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2]||'', 'utf8');
const start=html.indexOf('// SE321_LOS_CORE_START');
const end=html.indexOf('// SE321_LOS_CORE_END',start);
assert(start>=0&&end>start,'active sight extension exists');
assert(html.includes('se321BudgetFor(!!renderer?.xr?.isPresenting'),'VR-specific crowded budget');
assert(html.includes("const kind=Math.abs(args[2]-stUnitRadius('wolf'))<.001?'wolf':'sheep';"),
  'correct actual wolf radius statistics');
assert(html.includes('const se256AIBudget={frame:-1,used:0,perFrame:2'),
  'existing sheep AI preserved');
const sheep=(x,z,id='sheep')=>({id,kind:'sheep',pos:{x,z},captured:false});
const wolf=(x,z,id='wolf')=>({id,kind:'wolf',pos:{x,z},captured:false});
const building={hp:250,progress:1,pos:{x:4,z:0},halfX:1.2,halfZ:1.2,
  localHalfX:1.2,localHalfZ:1.2,rotation:0};
const session={elapsed:1,navVersion:3,rules:{fogMode:'team'},buildings:[building]};
const context=vm.createContext({stSession:session,
 stPerceivesDirect:(a,b)=>Math.hypot(a.pos.x-b.pos.x,a.pos.z-b.pos.z)<20});
vm.runInContext(html.slice(start,end),context,{timeout:1000});
const w=wolf(0,0),s=sheep(8,0);
assert.equal(context.stPerceivesDirect(w,s),false,'house blocks wolf spotting sheep');
assert.equal(context.stPerceivesDirect(s,w),false,'house blocks sheep spotting wolf');
assert.equal(context.stPerceivesDirect(w,s),false,'same update is cached');
assert(context.se321Sight.reused>=1,'cache hits counted');
s.pos.z=5;session.elapsed+=.01;
assert.equal(context.stPerceivesDirect(w,s),true,'clear side route restores sight');
s.pos.z=0;session.navVersion++;
assert.equal(context.stPerceivesDirect(w,s),false,'navigation change refreshes blocked sight');
session.rules.fogMode='off';
assert.equal(context.stPerceivesDirect(w,s),true,'no fog keeps legacy full vision');
session.rules.fogMode='team';
building.rotation=Math.PI/4;
session.navVersion++;
assert.equal(context.stPerceivesDirect(w,s),false,'rotated house blocks diagonal vision');
building.hp=0;session.navVersion++;
assert.equal(context.stPerceivesDirect(w,s),true,'destroyed house does not occlude');
assert.equal(context.stPerceivesDirect(w,wolf(8,0)),true,'teammates unaffected');
const budgetStart=html.indexOf('function se321BudgetFor(xr,sheep,houses){');
const budgetEnd=html.indexOf('const se321PriorUpdate=stUpdate;',budgetStart);
assert(budgetStart>=0&&budgetEnd>budgetStart,'budget helper');
vm.runInContext(html.slice(budgetStart,budgetEnd),context,{timeout:1000});
assert.equal(context.se321BudgetFor(true,3,10),1,'crowded XR reduced');
assert.equal(context.se321BudgetFor(true,1,10),2,'lone sheep unchanged');
assert.equal(context.se321BudgetFor(false,3,10),2,'non XR unchanged');
assert.equal(context.se321BudgetFor(true,3,3),2,'few houses unchanged');
assert(html.includes('const se321PreviousSample=se286Sample;'),'existing HMD sample reused');
console.log('SE321_SIGHT_HEAD_DIAGNOSTIC_PASS');
