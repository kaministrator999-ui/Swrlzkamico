// §E v11.111 focused unit regression for genuine circular-hole geometry.
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const base='projects/swrlz-forge-moba/runtime/';
const src=fs.readFileSync(base+'model_atelier_bowling_holes_v11_111.js','utf8');
const audit=fs.readFileSync(base+'model_atelier_topology_audit_v11_44.js','utf8');
const builder=src.split('function atelierBowlingInstall(){')[0];
const ctx={THREE,console};
vm.createContext(ctx);
vm.runInContext(audit+'\n'+builder,ctx);
ctx.atelierTopologyValid=p=>{
 const d=p.topologyMesh;
 return p.kind==='topologyMesh' && d.positions.length%3===0 &&
  d.positions.length/3<=9000&&d.indices.length%3===0&&
  d.indices.length/3<=16000&&d.uvs.length===d.positions.length/3*2 &&
  d.positions.every(Number.isFinite)&&d.uvs.every(Number.isFinite) &&
  d.indices.every(i=>Number.isInteger(i)&&i>=0&&i<d.positions.length/3);
};
function test(number){
 const result=ctx.atelierBowlingBuild(1,[0,0,0],[0,0,1],number,.15,.45);
 if(!result.ok)throw Error(number+' hole generated invalid: '+result.reason);
 const audit=ctx.atelierTopologyAudit(result.data);
 console.log(JSON.stringify({number,vertices:result.vertices,faces:result.triangles,
  boundary:audit.boundaryEdges,nonManifold:audit.nonManifoldEdges,
  winding:audit.oppositeWindingErrors,zeroArea:audit.zeroAreaFaces}));
 if(audit.boundaryEdges||audit.nonManifoldEdges||audit.oppositeWindingErrors||audit.zeroAreaFaces)
  throw Error('not watertight and consistently oriented');
 if(result.vertices>9000||result.triangles>16000)throw Error('over budget');
 if(number===3&&!result.triangles>5000)throw Error('missing bore mesh');
}
test(1);test(3);
for(const radius of [.08,.15,.18]){
 const r=ctx.atelierBowlingBuild(.9,[0,0,0],[0,1,0],3,radius,.5);
 if(!r.ok)throw Error('Unexpected geometry failure on varied radius '+radius+': '+r.reason);
}
console.log('§E v11.111 ROUND_HOLE_GEOMETRY_PASS');
