#!/usr/bin/env node
/* §E v11.516: exercise the real generated SkinnedMesh factory/bind/pose code
   with arbitrary geometries, nonuniform model + mesh transforms, hierarchy
   changes and repeated inverse bind/pose/reset. No specific starter assets. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {pathToFileURL} from 'node:url';
const threePath=process.argv[2],htmlPath=process.argv[3];
if(!threePath||!htmlPath)throw Error('Expected Three169 module and generated §E HTML');
const THREE=await import(pathToFileURL(path.resolve(threePath)));
assert.equal(THREE.REVISION,'169');
const html=fs.readFileSync(htmlPath,'utf8');
const a=html.indexOf('function se220RigMesh(part){');
const b=html.indexOf('function se220RigRemember(){',a);
assert(a>=0&&b>a);
const source=html.slice(a,b);
const fixtures=[
 ['box-seams',()=>new THREE.BoxGeometry(.45,.85,.27,4,6,3)],
 ['curved-sphere',()=>new THREE.SphereGeometry(.38,16,10)],
 ['irregular-torus',()=>new THREE.TorusKnotGeometry(.24,.066,64,12)],
 ['open-plane',()=>new THREE.PlaneGeometry(.5,.9,6,9)]
];
let total=0;
for(const [label,factory] of fixtures){
 const rig={schema:'swyrl-cloth-skin-v1',targetPartId:'generic-target',
  bones:[{id:'root',label:'Root',parent:null,rest:[0,0,0]},
   {id:'mid',label:'Mid',parent:'root',rest:[0,.48,0]},
   {id:'tip',label:'Tip',parent:'mid',rest:[0,.92,0]}],
  pose:{}};
 const modelRoot=new THREE.Group();
 modelRoot.position.set(.9,.27,-.3);
 modelRoot.rotation.set(.13,-.25,.17);
 modelRoot.scale.set(1.5,.8,1.18);
 const part={id:rig.targetPartId,position:[.1,.68,-.07],
  rotation:[.03,.12,-.09],scale:[.8,1.35,.62]};
 const ctx={THREE,modelRoot,atelierSculptApply:g=>g,geometry:()=>factory(),
  material:()=>new THREE.MeshStandardMaterial(),
  se220RigAvailable:()=>true,se220Rig:()=>rig,
  se220RigWeights:([x,y,z])=>({indices:[y>.70?2:y<.4?0:1,0,0,0],
    weights:[1,0,0,0]}),
  se489AuthoredSkinWeights:(p,index,r,point)=>ctx.se220RigWeights(point,r),
  se220RigValidate:()=>true,se220Bones:null,se220Skeleton:null,
  se220BoneOverlay:null,$m:()=>({checked:false})};
 vm.runInNewContext(source,vm.createContext(ctx));
 const mesh=ctx.se220RigMesh(part);
 assert(mesh.isSkinnedMesh,label+': target must be skinned');
 mesh.position.fromArray(part.position);
 mesh.rotation.fromArray(part.rotation);
 mesh.scale.fromArray(part.scale);
 modelRoot.add(mesh);
 const other=ctx.se220RigMesh({...part,id:'unrelated'});
 assert(other.isMesh&&!other.isSkinnedMesh,label+': unrelated should not be skinned');
 ctx.se220RigBind();
 const pos=mesh.geometry.getAttribute('position'),ids=mesh.geometry.getAttribute('skinIndex'),
  weights=mesh.geometry.getAttribute('skinWeight');
 const unskinned=i=>new THREE.Vector3().fromBufferAttribute(pos,i).applyMatrix4(mesh.matrixWorld);
 const skinned=i=>{
  const v=new THREE.Vector3().fromBufferAttribute(pos,i);
  mesh.applyBoneTransform(i,v);
  return v.applyMatrix4(mesh.matrixWorld);
 };
 const assertNeutral=tag=>{
  modelRoot.updateMatrixWorld(true);
  for(let i=0;i<pos.count;i++){
   const d=unskinned(i).distanceTo(skinned(i));
   assert(d<3e-5,label+': '+tag+' bind vertex '+i+' drift '+d);
   const sum=weights.getX(i)+weights.getY(i)+weights.getZ(i)+weights.getW(i);
   assert(Math.abs(sum-1)<1e-5,label+': normalized skin weights');
   for(let k=0;k<4;k++)assert(ids.getComponent(i,k)>=0&&ids.getComponent(i,k)<rig.bones.length);
  }
 };
 const assertMatrices=()=>{
  const identity=new THREE.Matrix4().elements;
  for(let i=0;i<mesh.skeleton.bones.length;i++){
   const got=mesh.skeleton.bones[i].matrixWorld.clone().multiply(mesh.skeleton.boneInverses[i]).elements;
   assert(got.every((x,k)=>Math.abs(x-identity[k])<2e-5),label+': inverse bind mismatch');
  }
 };
 assertNeutral('initial');assertMatrices();
 const neutral=Array.from({length:pos.count},(_,i)=>skinned(i));
 let moved=0;
 for(let k=0;k<20;k++){
  const strength=.12+(k%5)*.075;
  ctx.se220RigPose({mid:[.11,0,-.07],tip:[-.1,.08,strength]});
  for(let i=0;i<pos.count;i++){
   const p=skinned(i);
   assert(p.toArray().every(Number.isFinite),label+': finite pose');
   moved=Math.max(moved,p.distanceTo(neutral[i]));
  }
  ctx.se220RigPose({});
  assertNeutral('pose-reset-'+k);
 }
 assert(moved>.009&&moved<3,label+': bone rotation should deform without exploding');
 // Rebind after a parent-chain/rest adjustment; old skeletal roots/helpers
 // must not accumulate in the current model scene.
 const rootsBefore=modelRoot.children.filter(o=>o.isBone).length;
 rig.bones[2].parent='root';
 rig.bones[1].rest=[0,.51,0];
 rig.bones[2].rest=[0,.92,0];
 ctx.se220RigBind();
 assertNeutral('reparent-rebind');assertMatrices();
 const rootsAfter=modelRoot.children.filter(o=>o.isBone).length;
 assert(rootsBefore===1&&rootsAfter===1,label+': old rig root must be removed');
 assert.equal(modelRoot.children.filter(o=>o.type==='SkeletonHelper').length,1,
  label+': exactly one skeleton helper');
 modelRoot.position.x+=.31;
 modelRoot.scale.set(.92,1.38,.77);
 ctx.se220RigPose({});
 assertNeutral('post-parent-transform');
 total+=pos.count;
 console.log('SE516_COMPLEX_FIXTURE_PASS',label,JSON.stringify({vertices:pos.count,rebind:true,moved}));
}
console.log('SE516_GENERIC_RIG_DEFORMATION_PASS',JSON.stringify({fixtures:fixtures.length,vertices:total}));
