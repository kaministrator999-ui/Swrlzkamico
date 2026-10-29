import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';import {gzipSync,gunzipSync} from 'node:zlib';
const root=new URL('../',import.meta.url),project=JSON.parse(gunzipSync(fs.readFileSync(new URL('payload/organic-animals/sheep.swyrl.json.gz',root)))),ctx=vm.createContext({THREE,MODEL_ATELIER_KINDS:[]});
vm.runInContext(fs.readFileSync(new URL('runtime/model_atelier_topology_lod_v11_38.js',root),'utf8').split('function atelierLODRefresh(')[0],ctx);
const model=project.project.modelAtelier;let before=0,after=0;
for(const part of model.parts){const high=part.topologyMesh;before+=high.indices.length/3;ctx.part=part;const low=vm.runInContext('(()=>{const g=atelierTopologyGeometry(part),plan=atelierLODPlan(g,.12);g.dispose();if(!plan.ok)throw Error(plan.reason);return plan.data;})()',ctx);part.topologyMesh={positions:low.positions.map(v=>+v.toFixed(6)),uvs:low.uvs.map(v=>+v.toFixed(6)),indices:low.indices};after+=low.indices.length/3;}
model.name='Clover · Meadow Sheep · Game';model.sourceModel='scenes/model-atelier-organic-sheep-v11-87.swyrl.json';model.sourceTriangles=before;project.engine='§wyrl§ Engine · Maker v11.89';project.project.name=model.name;
fs.writeFileSync(new URL('payload/clover-game-v11-89.swyrl.json.gz',root),gzipSync(JSON.stringify(project),{level:9,mtime:0}));console.log({parts:model.parts.length,before,after,ratio:after/before});
