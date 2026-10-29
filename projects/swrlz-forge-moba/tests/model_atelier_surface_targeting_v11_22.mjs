import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8');
const c=vm.createContext({THREE,console});
vm.runInContext(read('runtime/model_atelier_surface_targeting_v11_22.js')+'\n'+
 read('runtime/model_atelier_sculpt_brush_v11_21.js')+'\n'+read('runtime/model_atelier_surface_lasso_v11_22.js')+'\n'+read('runtime/model_atelier_local_refinement_v11_23.js'),c);
assert.equal(vm.runInContext('typeof atelierSculptSurfaceInstall',c),'function');
assert.doesNotMatch(read('runtime/model_atelier_surface_targeting_v11_22.js'),/function\s+atelierSurfaceInstall\s*\(/);
const stroke=(overrides={})=>({
 center:[0,0,0],axis:[0,0,1],radius:.28,selectionRadius:.28,strength:.15,
 surfaceMode:'front',falloff:'smooth',half:false,level:false,
 snap:0,plateau:.3,taper:.4,yaw:0,pitch:0,offsetU:0,offsetV:0,...overrides
});
const piece=(z,reversed=false)=>{
 const g=new THREE.PlaneGeometry(.25,.25,4,4);
 if(reversed)g.rotateY(Math.PI);
 g.translate(0,0,z);
 return g;
};
function shells(secondReversed){
 const a=piece(0),b=piece(.05,secondReversed);
 const pa=a.attributes.position,pb=b.attributes.position,na=a.attributes.normal,nb=b.attributes.normal;
 const n=pa.count,m=pb.count;
 const xyz=new Float32Array((n+m)*3),normal=new Float32Array((n+m)*3);
 for(let i=0;i<n+m;i++){
   const src=i<n?pa:pb,k=i<n?i:i-n;
   const nr=i<n?na:nb;
   xyz.set([src.getX(k),src.getY(k),src.getZ(k)],i*3);
   normal.set([nr.getX(k),nr.getY(k),nr.getZ(k)],i*3);
 }
 const ind=[...Array.from(a.index.array),...Array.from(b.index.array,x=>x+n)];
 const g=new THREE.BufferGeometry();
 g.setAttribute('position',new THREE.BufferAttribute(xyz,3));
 g.setAttribute('normal',new THREE.BufferAttribute(normal,3));
 g.setIndex(ind);
 return {g,n,m};
}
const positive=shells(false),facing=shells(true);
const centerPositive=12,centerRear=positive.n+12;
assert(c.atelierSculptValid({sculptBrushes:[stroke()]}));
for(const invalid of [
 {selectionRadius:Infinity},{surfaceMode:'magic'},{offsetU:3},{offsetV:NaN},
 {selectionRadius:0.005}
])assert(!c.atelierSculptValid({sculptBrushes:[stroke(invalid)]}));
const front=c.atelierSculptApply(facing.g.clone(),{sculptBrushes:[stroke()]});
const through=c.atelierSculptApply(facing.g.clone(),{sculptBrushes:[stroke({surfaceMode:'through'})]});
const backBefore=facing.g.attributes.position.getZ(centerRear);
assert(Math.abs(front.attributes.position.getZ(centerRear)-backBefore)<1e-6,
 'Front surface mode must NOT move a rear-facing nearby layer');
assert(through.attributes.position.getZ(centerRear)>backBefore+.04,
 'Through-volume mode intentionally reaches a nearby back surface');
const nearFront=c.atelierSculptApply(positive.g.clone(),{sculptBrushes:[stroke({surfaceMode:'front'})]});
const connected=c.atelierSculptApply(positive.g.clone(),{sculptBrushes:[stroke({surfaceMode:'connected'})]});
assert(nearFront.attributes.position.getZ(centerRear)>positive.g.attributes.position.getZ(centerRear)+.03,
 'Front direction without connected targeting includes a nearby parallel layer');
assert(Math.abs(connected.attributes.position.getZ(centerRear)-positive.g.attributes.position.getZ(centerRear))<1e-6,
 'Connected geodesic mode must not cross disconnected parallel shells');
assert(connected.attributes.position.getZ(centerPositive)>positive.g.attributes.position.getZ(centerPositive)+.09,
 'Connected mode must still move the picked surface itself');
const narrow=c.atelierSculptApply(positive.g.clone(),{sculptBrushes:[stroke({selectionRadius:.065})]});
assert(Math.abs(narrow.attributes.position.getZ(4)-positive.g.attributes.position.getZ(4))<1e-6);
const offset=c.atelierSculptApply(positive.g.clone(),{sculptBrushes:[stroke({offsetU:.08})]});
let delta=0;
for(let i=0;i<positive.g.attributes.position.count;i++)
 delta+=Math.abs(offset.attributes.position.getZ(i)-nearFront.attributes.position.getZ(i));
assert(delta>.01,'Offset falloff center must move the editable footprint');
const modeList=vm.runInContext('atelierSurfaceModes.join(",")',c);
assert.equal(modeList,'front,connected,inside,through,nearest,occluded,visible-geodesic');
const nearShell=c.atelierSculptApply(positive.g.clone(),{sculptBrushes:[
 stroke({surfaceMode:'nearest',center:[0,0,.05]})]});
assert(Math.abs(nearShell.attributes.position.getZ(centerPositive)-
 positive.g.attributes.position.getZ(centerPositive))<1e-6,
 'Nearest projected shell must reject deeper parallel front-facing layer');
assert(nearShell.attributes.position.getZ(centerRear)>
 positive.g.attributes.position.getZ(centerRear)+.08,
 'Nearest projected shell must preserve picked outer surface');
const inside=stroke({surfaceMode:'inside'});
assert(c.atelierSculptValid({sculptBrushes:[inside]}));
const insideResult=c.atelierSculptApply(facing.g.clone(),{sculptBrushes:[inside]});
assert(insideResult.attributes.position.getZ(centerRear)>backBefore+.04,
 'Inside mode must sculpt the opposite-normal shell');
assert(Math.abs(insideResult.attributes.position.getZ(centerPositive)-
 facing.g.attributes.position.getZ(centerPositive))<1e-6,
 'Inside mode must leave the exterior/front shell unchanged');
console.log('V1122_SURFACE_BRUSH_FRONT_CONNECTED_THROUGH_RADIUS_OFFSET_SAVE_VALIDATION_PASS');
