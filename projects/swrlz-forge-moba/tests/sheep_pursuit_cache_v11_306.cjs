#!/usr/bin/env node
// Focused live-source regression: the wolf AI and target resolver share one
// cached approach without changing the historical v11.256 sheep AI budget.
'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const html=fs.readFileSync(process.argv[2]||'', 'utf8');
const begin=html.indexOf('function se306CachedApproach(wolf,sheep){');
const finish=html.indexOf('const stLanesOrderTargetBase = stOrderTarget;',begin);
assert(begin>=0&&finish>begin,'expected live v11.306 cached approach');
assert(html.includes('const point=se306CachedApproach(unit,sheep);'),'attacking wolf target uses shared cache');
assert(html.includes('const approach=se306CachedApproach(unit,sheep);'),'bot decision uses shared cache');
assert(html.includes('const se256AIBudget={frame:-1,used:0,perFrame:2'),'v11.256 frame-budgeted sheep AI preserved');
class Vec {
  constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
  clone(){return new Vec(this.x,this.y,this.z);}
  distanceToSquared(v){return (this.x-v.x)**2+(this.y-v.y)**2+(this.z-v.z)**2;}
}
const session={elapsed:1,navVersion:7},perf={reuses:0,adoptions:0};
let calls=0;
const context=vm.createContext({
  stSession:session,se306Perf:perf,
  stLanesSheepApproach:()=>{calls++;return new Vec(4,0,3);}
});
vm.runInContext(html.slice(begin,finish),context,{timeout:1000});
const wolf={botIndex:1},sheep={id:'s1',pos:new Vec(0,0,0)};
assert(context.se306CachedApproach(wolf,sheep));
assert.equal(calls,1,'initial approach planned');
session.elapsed=1.08;sheep.pos.x=.5;
assert(context.se306CachedApproach(wolf,sheep));
assert.equal(calls,1,'moving sheep reuses cached approach');
session.elapsed=1.12;sheep.pos.x=2.1;
assert(context.se306CachedApproach(wolf,sheep));
assert.equal(calls,2,'significant sheep motion invalidates approach');
session.navVersion++;
session.elapsed=1.13;
assert(context.se306CachedApproach(wolf,sheep));
assert.equal(calls,3,'building navigation change invalidates approach');
session.elapsed=4;wolf.sheepApproach=null;
context.stLanesSheepApproach=()=>{calls++;return null;};
assert.equal(context.se306CachedApproach(wolf,sheep),null);
const failedCalls=calls;
session.elapsed=4.1;
assert.equal(context.se306CachedApproach(wolf,sheep),null);
assert.equal(calls,failedCalls,'blocked approach reuses negative cache');
assert(perf.reuses>=2&&perf.adoptions>=4,'instrumentation records hits and refreshes');
console.log('SE306_CACHE_REGRESSION_PASS',JSON.stringify({calls,hits:perf.reuses,plans:perf.adoptions}));
