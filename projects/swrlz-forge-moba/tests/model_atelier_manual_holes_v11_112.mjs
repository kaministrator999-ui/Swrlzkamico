import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const root='projects/swrlz-forge-moba/runtime/';
const audit=fs.readFileSync(root+'model_atelier_topology_audit_v11_44.js','utf8');
const old=fs.readFileSync(root+'model_atelier_bowling_holes_v11_111.js','utf8');
const manual=fs.readFileSync(root+'model_atelier_manual_round_holes_v11_112.js','utf8');
function init(js) {
 const ctx={THREE,console,checkPart:()=>true};
 vm.createContext(ctx);
 vm.runInContext(audit+'\n'+js.split('function atelierBowlingInstall(){')[0],ctx);
 ctx.atelierTopologyValid=p=>{
  const d=p?.topologyMesh;
  return p.kind==='topologyMesh'&&!!d&&
   d.positions.length%3===0&&d.positions.length/3<=9000&&
   d.uvs.length===2*d.positions.length/3&&
   d.indices.length%3===0&&d.indices.length/3<=16000&&
   d.positions.every(Number.isFinite)&&d.uvs.every(Number.isFinite)&&
   d.indices.every(i=>Number.isInteger(i)&&i>=0&&i<d.positions.length/3);
 };
 return ctx;
}
const baseline=init(old),editor=init(manual);
const preset=[
 {x:-.255,y:.23,r:.15,depth:.45,cap:.8},
 {x:.255,y:.23,r:.15,depth:.45,cap:.8},
 {x:0,y:-.36,r:.18,depth:.45,cap:.8}
];
const results=[];
for(let n=1;n<=3;n++){
 const holes=preset.slice(0,n);
 const r=editor.atelierBowlingBuild(1,[0,0,0],[0,0,1],holes);
 if(!r.ok)throw Error('Manual '+n+' holes failed '+r.reason);
 const a=editor.atelierTopologyAudit(r.data);
 if(!a.ok||a.boundaryEdges||a.nonManifoldEdges||a.oppositeWindingErrors||a.zeroAreaFaces)
  throw Error('Damaged mesh for '+n+' holes '+JSON.stringify({b:a.boundaryEdges,m:a.nonManifoldEdges,w:a.oppositeWindingErrors,z:a.zeroAreaFaces}));
 const plan={radius:1,center:[0,0,0],axis:[0,0,1],holes:JSON.parse(JSON.stringify(holes))};
 if(!editor.atelierBorePlanValid({kind:'topologyMesh',roundHolePlan:plan}))
  throw Error('Lost saved manual hole recipe for '+n+' holes');
 if(!editor.atelierBorePlanValid(JSON.parse(JSON.stringify({kind:'topologyMesh',roundHolePlan:plan}))))
  throw Error('Round-trip lost manual precision holes');
 results.push({holes:n,vertices:r.vertices,triangles:r.triangles,boundaries:a.boundaryEdges,nonManifold:a.nonManifoldEdges});
}
if(editor.atelierBorePlanValid({kind:'topologyMesh',roundHolePlan:{radius:1,center:[0,0,0],axis:[0,0,1],holes:[{x:1,y:0,r:.1,depth:.4,cap:.8}]}})===false)
 console.log('Malformed external recipe rejected by builder instead of schema');
const overlapping=editor.atelierBowlingBuild(1,[0,0,0],[0,0,1],[preset[0],preset[0]]);
if(overlapping.ok)throw Error('Overlapping holes incorrectly allowed');
const old3=baseline.atelierBowlingBuild(1,[0,0,0],[0,0,1],3,.15,.45);
const new3=editor.atelierBowlingBuild(1,[0,0,0],[0,0,1],preset);
function deviation(result,frontFaces){
 const pos=result.data.positions,indices=result.data.indices,errors=[];
 for(let face=0;face<frontFaces;face++){
  const ids=indices.slice(face*3,face*3+3);
  const c=[0,1,2].map(k=>ids.reduce((acc,i)=>acc+pos[i*3+k],0)/3);
  errors.push(1-Math.hypot(...c));
 }
 errors.sort((a,b)=>a-b);
 return {max:errors.at(-1),p95:errors[Math.floor(errors.length*.95)]};
}
const before=deviation(old3,784),after=deviation(new3,3136);
if(after.max>=before.max*.65||after.p95>=before.p95*.5)
 throw Error('Hand-cut ball surface not sufficiently smoother: '+JSON.stringify({before,after}));
console.log('MANUAL_BORE_TOPOLOGY',JSON.stringify(results));
console.log('BOWLING_CURVATURE',JSON.stringify({before,after}));
console.log('SE_V11112_MANUAL_ONE_AT_A_TIME_AND_ROUNDNESS_PASS');
