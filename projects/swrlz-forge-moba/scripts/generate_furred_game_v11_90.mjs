import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';import {gzipSync,gunzipSync} from 'node:zlib';
const root=new URL('../',import.meta.url),project=JSON.parse(gunzipSync(fs.readFileSync(new URL('payload/furred-astra-v11-90.swyrl.json.gz',root)))),ctx=vm.createContext({THREE,MODEL_ATELIER_KINDS:[]});vm.runInContext(fs.readFileSync(new URL('runtime/model_atelier_topology_lod_v11_38.js',root),'utf8').split('function atelierLODRefresh(')[0],ctx);
const model=project.project.modelAtelier;let before=0,after=0;
for(const part of model.parts){
 if(part.kind==='loft'){part.meshDensity={u:20,v:12};continue;}if(part.kind==='sphere'){part.meshDensity={u:20,v:12};continue;}if(!part.topologyMesh)continue;
 const high=part.topologyMesh;before+=high.indices.length/3;
 if(part.organicSurface?.region==='fur3d'){const positions=[],uvs=[],indices=[],vertices=38,faces=72;for(let tuft=0;tuft<high.positions.length/(vertices*3);tuft+=4){const base=positions.length/3;positions.push(...high.positions.slice(tuft*vertices*3,(tuft+1)*vertices*3));uvs.push(...high.uvs.slice(tuft*vertices*2,(tuft+1)*vertices*2));indices.push(...high.indices.slice(tuft*faces*3,(tuft+1)*faces*3).map(i=>i-tuft*vertices+base));}part.topologyMesh={positions,uvs,indices};}
 else{ctx.part=part;const low=vm.runInContext('(()=>{const g=atelierTopologyGeometry(part),plan=atelierLODPlan(g,.07);g.dispose();if(!plan.ok)throw Error(plan.reason);return plan.data;})()',ctx);part.topologyMesh={positions:low.positions.map(v=>+v.toFixed(6)),uvs:low.uvs.map(v=>+v.toFixed(6)),indices:low.indices};}
 after+=part.topologyMesh.indices.length/3;
}
model.name='Astra · Furred Courier · Game';model.sourceModel='scenes/model-atelier-furred-astra-v11-90.swyrl.json';model.sourceTriangles=before;project.project.name=model.name;fs.writeFileSync(new URL('payload/furred-game-v11-90.swyrl.json.gz',root),gzipSync(JSON.stringify(project),{level:9,mtime:0}));console.log({parts:model.parts.length,topologyBefore:before,topologyAfter:after});
