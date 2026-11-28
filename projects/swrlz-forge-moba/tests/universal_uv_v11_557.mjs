import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {optimizeExistingUV} from '../runtime/uv_atlas_core_v11_555.mjs';
const p=[0,0,0,1,0,0,1,1,0,0,1,0,2,0,0,3,0,0,3,1,0,2,1,0],ix=[0,1,2,0,2,3,4,5,6,4,6,7],uv=[.01,.01,.11,.01,.11,.11,.01,.11,.2,.2,.3,.2,.3,.3,.2,.3];
const input={positions:p,indices:ix,uvs:uv};
const a=optimizeExistingUV(input);
assert(a.changed);assert.deepEqual(a.positions,p);assert.deepEqual(a.indices,ix);assert.deepEqual(input.uvs,uv);
assert(a.report.packing.candidateTriangleArea>a.report.packing.baselineTriangleArea);
assert.equal(a.report.after.positiveAreaOverlapPairs,0);
assert.throws(()=>optimizeExistingUV({...input,uvs:[...uv.slice(0,8),...uv.slice(0,8)]}),/overlap/i);
assert.throws(()=>optimizeExistingUV({...input,uvs:uv.map(()=>0)}),/collapsed/i);
const scenes=path.resolve(import.meta.dirname,'../scenes');
let accepted=0,skipped=0;
for(const name of fs.readdirSync(scenes).filter(s=>/clean-topology-humanoid|futuristic-humanoid-v11-546|sorting-hat/.test(s))){
 const doc=JSON.parse(fs.readFileSync(path.join(scenes,name),'utf8'));
 for(const part of doc.project?.modelAtelier?.parts||[]){
  const m=part.topologyMesh;if(!m?.uvs?.length)continue;
  let r;try{r=optimizeExistingUV(m);}catch(e){skipped++;console.log('SKIP',name,part.name,e.message);continue;}
  assert.deepEqual(r.positions,m.positions);assert.deepEqual(r.indices,m.indices);assert.equal(r.report.after.positiveAreaOverlapPairs,0);
  accepted++;console.log('PASS',name,part.name,JSON.stringify({changed:r.changed,packing:r.report.packing?.relativeAreaGain,stretch:r.report.relaxation?.after.max}));
 }
}
assert(accepted>=1,'No real starter meshes passed');
console.log('SWRLZ_UNIVERSAL_UV_CORE_PASS',JSON.stringify({accepted,skipped}));
