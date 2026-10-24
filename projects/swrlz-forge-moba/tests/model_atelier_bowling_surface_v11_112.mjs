// Functional regression for the exact ball geometry, not merely triangle counts.
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const prefix='projects/swrlz-forge-moba/runtime/';
const before=fs.readFileSync(prefix+'model_atelier_bowling_holes_v11_111.js','utf8');
const after=fs.readFileSync('/tmp/se-v11112-optimized.js','utf8');
const audit=fs.readFileSync(prefix+'model_atelier_topology_audit_v11_44.js','utf8');
function evaluate(source,n){
 const ctx={THREE,console};
 vm.createContext(ctx);
 vm.runInContext(audit+'\n'+source.split('function atelierBowlingInstall(){')[0],ctx);
 ctx.atelierTopologyValid=p=>{
  const d=p.topologyMesh;return p.kind==='topologyMesh' &&
   d.positions.length%3===0&&d.positions.length/3<=9000&&
   d.indices.length%3===0&&d.indices.length/3<=16000&&
   d.uvs.length===d.positions.length/3*2 &&
   d.positions.every(Number.isFinite)&&d.uvs.every(Number.isFinite)&&
   d.indices.every(i=>Number.isInteger(i)&&i>=0&&i<d.positions.length/3);
 };
 const r=ctx.atelierBowlingBuild(1,[0,0,0],[0,0,1],n,.15,.45);
 if(!r.ok)throw Error('Rejected '+n+' holes: '+r.reason);
 const a=ctx.atelierTopologyAudit(r.data);
 if(!a.ok||a.boundaryEdges||a.nonManifoldEdges||a.oppositeWindingErrors||a.zeroAreaFaces)
  throw Error('Invalid '+n+' cavity mesh: '+JSON.stringify({b:a.boundaryEdges,m:a.nonManifoldEdges,w:a.oppositeWindingErrors,z:a.zeroAreaFaces}));
 const isNew=source===after;
 const segmentCount= isNew ? 288 : 144;
 const lipCount=isNew ? 160 : 80;
 const frontFaces=r.triangles-segmentCount*19-(n*lipCount*13);
 if(r.frontTriangles!==undefined && frontFaces!==r.frontTriangles)
  throw Error('Invalid front face boundary accounting');
 const errs=[], p=r.data.positions, inds=r.data.indices;
 for(let f=0;f<frontFaces;f++){
  const ids=inds.slice(f*3,f*3+3);
  const xyz=[0,1,2].map(k=>ids.map(i=>p[i*3+k]).reduce((a,b)=>a+b,0)/3);
  errs.push(Math.abs(1-Math.hypot(...xyz)));
 }
 errs.sort((a,b)=>a-b);
 const result={holes:n,vertices:r.vertices,triangles:r.triangles,frontFaces,
  max:errs.at(-1),p95:errs[Math.floor((errs.length-1)*.95)],average:errs.reduce((a,b)=>a+b,0)/errs.length};
 return result;
}
for(const n of [1,3]){
 const old=evaluate(before,n),updated=evaluate(after,n);
 console.log('BOWLING_SURFACE_BEFORE',JSON.stringify(old));
 console.log('BOWLING_SURFACE_AFTER',JSON.stringify(updated));
 if(updated.max>=old.max*.82||updated.p95>=old.p95*.82)
  throw Error('Roundness did not improve enough from baseline');
}
console.log('SE_V11112_SPHERE_CURVATURE_AND_BORE_GEOMETRY_PASS');
