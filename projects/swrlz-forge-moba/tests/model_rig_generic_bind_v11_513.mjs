#!/usr/bin/env node
/* Test actual v11.220 SkinnedMesh construction, hierarchy, neutral bind, and
   three.js r169 CPU pose deformation on generic, transformed two/three-joint
   meshes, never on the Sorting Hat asset. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {pathToFileURL,fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2]||'')));
assert.equal(THREE.REVISION,'169','the deployed renderer uses Three.js r169');
if(!process.argv[3])throw Error('Expected generated §E HTML path after Three module');
const base=fs.readFileSync(path.resolve(process.argv[3]),'utf8');
assert(base.includes('SE513_RIG_SKIN_MATH_END'),'test requires v11.513 generated source');
const start=base.indexOf('function se220RigMesh(part){');
const end=base.indexOf('function se220RigRemember(){',start);
assert(start>=0&&end>start);
const source=base.slice(start,end);
const rig={schema:'swyrl-cloth-skin-v1',targetPartId:'generic-cylinder',bones:[
 {id:'root',parent:null,rest:[0,0,0]},
 {id:'mid',parent:'root',rest:[0,.5,0]},
 {id:'tip',parent:'mid',rest:[0,1,0]}
],pose:{}};
const part={id:'generic-cylinder',position:[0,.5,0],rotation:[0,0,0],scale:[1,1,1]};
const rootNode=new THREE.Group();rootNode.position.set(1,.2,-.7);rootNode.rotation.y=.17;
const context={THREE,modelRoot:rootNode,se220RigAvailable:()=>true,se220Rig:()=>rig,
 atelierSculptApply:g=>g,geometry:()=>new THREE.CylinderGeometry(.2,.2,1,12,2,false),
 material:()=>new THREE.MeshStandardMaterial(),
 se220RigWeights:([x,y,z])=>y<.25?{indices:[0,0,0,0],weights:[1,0,0,0]}:
  y>.75?{indices:[2,0,0,0],weights:[1,0,0,0]}:
  {indices:[1,0,0,0],weights:[1,0,0,0]},
 se220RigValidate:()=>true,se220BoneOverlay:null,se220Bones:null,se220Skeleton:null,
 $m:()=>({checked:true})};
vm.runInNewContext(source,vm.createContext(context));
const mesh=context.se220RigMesh(part);mesh.userData.atelierId=part.id;
mesh.position.fromArray(part.position);rootNode.add(mesh);
const plain=context.se220RigMesh({...part,id:'unrelated-part'});
assert.equal(plain.isSkinnedMesh,false,'non-target mesh must remain independent of cloth skeleton');
context.se220RigBind();
const pos=mesh.geometry.getAttribute('position');
const world=(id)=>new THREE.Vector3().fromBufferAttribute(pos,id).applyMatrix4(mesh.matrixWorld);
const skinned=(id)=>{
 const point=new THREE.Vector3().fromBufferAttribute(pos,id);
 mesh.applyBoneTransform(id,point);
 return point.applyMatrix4(mesh.matrixWorld);
};
let bottom=-1,upper=-1;
for(let i=0;i<pos.count;i++){
 if(pos.getY(i)<-.45&&bottom<0)bottom=i;
 if(pos.getY(i)>.45&&Math.abs(pos.getX(i))>.05&&upper<0)upper=i;
 const baseline=world(i),neutral=skinned(i);
 assert(baseline.distanceTo(neutral)<1e-5,'neutral binding must preserve transformed mesh vertex');
}
assert(bottom>=0&&upper>=0);
const lowerStart=skinned(bottom),upperStart=skinned(upper);
context.se220RigPose({tip:[0,0,.45]});
const lowerPose=skinned(bottom),upperPose=skinned(upper);
assert(lowerStart.distanceTo(lowerPose)<1e-5,'unrelated root vertices must remain stable');
assert(upperStart.distanceTo(upperPose)>.015,'weighted tip must visibly deform');
assert(Number.isFinite(upperPose.x)&&Number.isFinite(upperPose.y));
const maxShift=Math.max(...Array.from({length:pos.count},(_,i)=>world(i).distanceTo(skinned(i))));
assert(maxShift<.5,'small generic pose must not explode mesh');
context.se220RigPose({});
assert(upperStart.distanceTo(skinned(upper))<1e-5,'restoring pose must exactly reset skin');
console.log('SE513_GENERIC_SKIN_BIND_PASS',JSON.stringify({neutralVertices:pos.count,
 rootStable:true,tipMoved:true,poseReset:true,unrelatedUnskinned:true,maxPoseMovement:maxShift}));
