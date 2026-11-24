#!/usr/bin/env node
// v11.555: run the identical xatlas WASM conformal UV core used by §E's browser.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {unwrapMesh} from '../runtime/uv_atlas_core_v11_555.mjs';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'..');
const imported=pathToFileURL(path.join(root,'.se555_deps/node_modules/xatlas-wasm/dist/index.mjs')).href;
const createXAtlas=(await import(imported)).default;
const scenePath=path.join(root,'scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json');
const reportPath=path.join(root,'docs/qa/clean-topology-humanoid-v11-554.json');
const scene=JSON.parse(fs.readFileSync(scenePath,'utf8'));
const report=JSON.parse(fs.readFileSync(reportPath,'utf8'));
const part=scene.project.modelAtelier.parts[0];
const source=part.topologyMesh;
const boxes=report.uvBoxes;
const regions=['head','torso','leftArm','rightArm','leftLeg','rightLeg'];
const material=Array.from({length:source.indices.length/3},(_,fi)=>{
 const ids=source.indices.slice(fi*3,fi*3+3);
 const u=ids.reduce((sum,id)=>sum+source.uvs[id*2],0)/3;
 const v=ids.reduce((sum,id)=>sum+source.uvs[id*2+1],0)/3;
 const type=regions.find(n=>{const [a,b,c,d]=boxes[n];return a-.0001<=u&&u<=c+.0001&&b-.0001<=v&&v<=d+.0001;});
 if(!type)throw Error('Missing anatomical material for triangle '+fi);
 return regions.indexOf(type);
});
let accepted=null,errors=[];
for(const seamMode of ['anatomical','geometry']){
 try{
  const r=await unwrapMesh(createXAtlas,source,{
   method:'lscm',faceMaterialData:seamMode==='anatomical'?material:null,
   resolution:2048,padding:8,maxVertices:9000,maxCharts:70
  });
  if(r.distortion.p95P05>45)
   throw Error('Excess LSCM texel density ratio '+r.distortion.p95P05);
  accepted={...r,seamMode};break;
 }catch(e){errors.push(seamMode+': '+String(e?.message||e));
  console.log('SE555_LSCM_RETRY',seamMode,errors.at(-1));}
}
if(!accepted)throw Error('No qualified anatomy UV unwrap: '+JSON.stringify(errors));
part.topologyMesh={...source,positions:accepted.positions,
                   uvs:accepted.uvs,indices:accepted.indices};
part.name='Clean Topology Humanoid · xatlas relaxed UV mesh';
scene.engine='§wyrl§ Engine v11.555 · geometry-derived xatlas UV';
scene.project.modelAtelier.reference='Connected quad-loop humanoid with genuine xatlas conformal UV unwrap, anatomical face/torso/limb chart seams and checker skin. Save as account project before sculpting.';
report.revision='xatlas-anatomical-conformal-v4';
report.vertices=accepted.positions.length/3;
report.triangles=accepted.indices.length/3;
report.uvAlgorithm='seamed-LSCM+verified-single-atlas-packer';
report.uvPaintMode='xatlas-actual-geometry-masked-checker';
report.uvChartCount=accepted.charts;
report.uvTexelDensity=accepted.distortion;
report.uvAtlasSize=[accepted.width,accepted.height];
report.uvMaxCost=null;
report.uvMethod=accepted.method;
report.uvLscmIterations=accepted.lscmIterations;
report.uvSeamMode=accepted.seamMode;
report.uvPacking=accepted.packing;
report.uvChartScale=accepted.chartScale;
report.uvPaddingPixels=accepted.paddingPixels;
report.uvWeldedInputVertices=accepted.weldedInputVertices;
report.originalAnatomicalRegions=regions;
delete report.uvBoxes;delete report.uvCharts;delete report.guideAnatomyLabels;
const meta={regionPerFace:material,regionLabels:regions,charts:accepted.charts};
fs.writeFileSync(path.join(root,'docs/qa/clean-topology-humanoid-v11-555-region-meta.json'),JSON.stringify(meta));
fs.writeFileSync(scenePath,JSON.stringify(scene));
fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');
console.log('SE555_XATLAS_CONFORMAL_UNWRAP_PASS',JSON.stringify({
 vertices:report.vertices,triangles:report.triangles,charts:accepted.charts,
 density:accepted.distortion.p95P05,atlas:report.uvAtlasSize}));
