import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';import {gzipSync} from 'node:zlib';
const root=new URL('../',import.meta.url),original=JSON.parse(fs.readFileSync(new URL('scenes/model-atelier-comet-courier-v11-77.swyrl.json',root))),ctx=vm.createContext({THREE,structuredClone,COMET_COURIER_PROJECT:original});
vm.runInContext(fs.readFileSync(new URL('runtime/model_atelier_animals_v11_87.js',root),'utf8'),ctx);
vm.runInContext(fs.readFileSync(new URL('runtime/model_atelier_courier_organic_v11_88.js',root),'utf8').split('const atelierOriginalWolfLoader=')[0],ctx);
const data=vm.runInContext('atelierRefineCourierProject()',ctx);fs.writeFileSync(new URL('payload/courier-organic-v11-88.swyrl.json.gz',root),gzipSync(JSON.stringify(data),{level:9,mtime:0}));
console.log({parts:data.project.modelAtelier.parts.length,organicMeshes:data.project.modelAtelier.parts.filter(p=>p.topologyMesh).map(p=>({name:p.name,vertices:p.topologyMesh.positions.length/3,triangles:p.topologyMesh.indices.length/3}))});
