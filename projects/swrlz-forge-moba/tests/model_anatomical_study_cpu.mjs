import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const root=new URL('../',import.meta.url),read=p=>fs.readFileSync(new URL(p,root),'utf8');
const historic=JSON.parse(read('scenes/model-atelier-festival-polish-v11-19.swyrl.json')).project.modelAtelier;
const study=JSON.parse(read('scenes/model-atelier-festival-anatomy-v11-20.swyrl.json')).project.modelAtelier;
const context=vm.createContext({THREE,console});
vm.runInContext([
 'runtime/model_atelier_density_v11_16.js',
 'runtime/model_atelier_hd_v11_17.js',
 'runtime/model_atelier_portrait_v11_19.js',
 'runtime/model_atelier_anatomical_v11_20.js'].map(read).join('\n'),context);
const by=(m,id)=>m.parts.find(p=>p.id===id);
assert.equal(study.parts.length,historic.parts.length);
for(const previous of historic.parts){
 const now=by(study,previous.id);assert(now,'Lost part '+previous.id);
 if(!['model-0001','left-ear','right-ear'].includes(previous.id))
   assert.deepEqual(now,previous,'Unrelated source part changed: '+previous.id);
}
assert.equal(study.parts.filter(p=>p.anatomyStudy).length,1);
assert.equal(study.parts.filter(p=>p.earStudy).length,2);
const head=by(study,'model-0001'),ear=by(study,'left-ear');
assert.equal(context.atelierAnatomyValid(head),true);
assert.equal(context.atelierAnatomyValid({...head,anatomyStudy:{...head.anatomyStudy,jaw:1.1}}),false);
assert.equal(context.atelierAnatomyValid({...head,anatomyStudy:{jaw:0}}),false);
assert.equal(context.atelierAnatomyValid({...ear,earStudy:{...ear.earStudy,concha:Infinity}}),false);
const geometry=part=>part.anatomyStudy?context.atelierAnatomicalHead(part):context.atelierAnatomicalEar(part);
for(const p of [head,by(study,'left-ear'),by(study,'right-ear')]){
 const g=geometry(p),pos=g.attributes.position,norm=g.attributes.normal,col=g.attributes.color;
 assert(pos.count>(p.id==='model-0001'?5000:3000)&&g.index.count>10000,p.id+' must be genuine dense editable geometry');
 assert.equal(pos.count,norm.count);assert.equal(pos.count,col.count);
 for(const attr of [pos,norm,col])for(const v of attr.array)assert(Number.isFinite(v),p.id+' invalid vertex');
 for(const index of g.index.array)assert(Number.isInteger(index)&&index>=0&&index<pos.count);
 g.computeBoundingBox();
 assert(g.boundingBox.getSize(new THREE.Vector3()).length()>0);
 g.dispose();
}
const original=context.atelierPortraitFinish(by(historic,'model-0001'));

const neutral=context.atelierAnatomicalHead({...head,anatomyStudy:{jaw:.5,malar:.5,orbit:.5,nose:.5,chin:.5,temple:.5}});
assert.deepEqual(Array.from(neutral.attributes.position.array),Array.from(original.attributes.position.array),
 'Neutral anatomy sliders MUST reproduce the complete v11.19 portrait, not replace the head topology');
assert.deepEqual(Array.from(neutral.attributes.color.array),Array.from(original.attributes.color.array),
 'Neutral anatomy sliders must preserve the original skin/cheek shading');
assert.equal(neutral.index.count,original.index.count,'The original portrait topology was replaced');
const candidate=context.atelierAnatomicalHead(head),tame=context.atelierAnatomicalHead({...head,anatomyStudy:{...head.anatomyStudy,orbit:0,nose:0}});
assert.equal(candidate.attributes.position.count,original.attributes.position.count,'Lost v11.19 sampling');
const p0=original.attributes.position,p1=candidate.attributes.position;
let maxDisplacement=0,frontNose=0;
for(let i=0;i<p0.count;i++){
 const dx=p1.getX(i)-p0.getX(i),dy=p1.getY(i)-p0.getY(i),dz=p1.getZ(i)-p0.getZ(i);
 const delta=Math.hypot(dx,dy,dz);maxDisplacement=Math.max(maxDisplacement,delta);
 if(Math.abs(p0.getX(i))<.13&&p0.getY(i)<-.20&&p0.getY(i)>-.39&&p0.getZ(i)>.65)
   frontNose=Math.max(frontNose,dz);
}
assert(maxDisplacement<.08,'Anatomy pass destroyed historical facial silhouette');
assert(frontNose>.002,'Saved sculpted bridge/tip must project beyond the approved portrait');
console.log('PRESERVED_PORTRAIT_NEUTRAL_GEOMETRY_AND_RESTRAINED_NOSE_MORPHS_PASS',frontNose,maxDisplacement);

assert.notDeepEqual(Array.from(candidate.attributes.position.array),Array.from(original.attributes.position.array),
 'The study may not render the unchanged original sphere');
assert.notDeepEqual(Array.from(candidate.attributes.position.array),Array.from(tame.attributes.position.array),
 'The saved anatomical controls must edit actual vertices');
const normals=candidate.attributes.normal,verts=candidate.attributes.position;
let litFront=0;
for(let i=0;i<verts.count;i++)if(verts.getZ(i)>.75&&Math.abs(verts.getX(i))<.30&&Math.abs(verts.getY(i))<.30){
 assert(normals.getZ(i)>.2,'Skull normals must face OUTWARD under studio light');litFront++;
}
assert(litFront>30,'Missing front facial surface samples');
candidate.computeBoundingBox();
assert(candidate.boundingBox.min.y>-.92,'Shortened chin must preserve neck clearance');
const oldLeft=context.atelierHDSphere(by(historic,'left-ear'));
const shaped=context.atelierAnatomicalEar(ear),flat=context.atelierAnatomicalEar({...ear,earStudy:{helix:0,concha:0,lobe:0}});
assert.notDeepEqual(Array.from(shaped.attributes.position.array),Array.from(flat.attributes.position.array),
 'Outer ear anatomy controls must change geometry');
assert.notDeepEqual(Array.from(shaped.attributes.position.array),Array.from(oldLeft.attributes.position.array),
 'Anatomical ear must not be a decorative oval');
console.log('ANATOMICAL_STUDY_SKULL_AURICLE_EDITABILITY_HISTORY_FINITE_GEOMETRY_PASS');
