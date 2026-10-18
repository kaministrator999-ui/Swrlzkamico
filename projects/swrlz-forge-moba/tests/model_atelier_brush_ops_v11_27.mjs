import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const read=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,console});
vm.runInContext(['model_atelier_surface_targeting_v11_22.js',
 'model_atelier_sculpt_brush_v11_21.js','model_atelier_brush_ops_v11_27.js',
 'model_atelier_surface_lasso_v11_22.js','model_atelier_local_refinement_v11_23.js']
 .map(read).join('\n'),c);
const stroke=(overrides={})=>({
 center:[0,0,0],axis:[0,0,1],radius:.32,selectionRadius:.32,
 strength:.12,half:false,level:false,falloff:'smooth',plateau:0,taper:.5,
 yaw:0,pitch:0,snap:0,surfaceMode:'front',offsetU:0,offsetV:0,
 ...overrides
});
const apply=(geom,op)=>c.atelierSculptApply(geom.clone(),{sculptBrushes:[op]});
const sample=(g,x,y,z=0)=>{
 const a=g.attributes.position;
 let best=-1,dist=Infinity;
 for(let i=0;i<a.count;i++){
   const d=Math.hypot(a.getX(i)-x,a.getY(i)-y,a.getZ(i)-z);
   if(d<dist){dist=d;best=i;}
 }
 return best;
};
const pos=(g,i)=>new THREE.Vector3().fromBufferAttribute(g.attributes.position,i);
const plane=new THREE.PlaneGeometry(1,1,20,20);
const original=Float32Array.from(plane.attributes.position.array);
assert(c.atelierSculptValid({sculptBrushes:[stroke()]}));
for(const bad of [
 {operation:'purge'}, {mirrorX:'yes'}, {falloff:'not-a-falloff'}
])assert(!c.atelierSculptValid({sculptBrushes:[stroke(bad)]}));
assert(c.atelierSculptValid({sculptBrushes:[stroke({operation:'pinch',mirrorX:true,falloff:'sharp'})]}));
const legacy=apply(plane,stroke());
const newPush=apply(plane,stroke({operation:'push',mirrorX:false}));
assert.deepEqual(Array.from(legacy.attributes.position.array),
 Array.from(newPush.attributes.position.array),'Explicit push must equal old stroke evaluation');
const mirror=apply(plane,stroke({operation:'push',center:[.2,0,0],radius:.13,
  selectionRadius:.13,mirrorX:true,strength:.12}));
const plus=sample(plane,.2,0),minus=sample(plane,-.2,0),far=sample(plane,0,.5);
assert(Math.abs(pos(mirror,plus).z-.12)<.025);
assert(Math.abs(pos(mirror,minus).z-.12)<.025);
assert(Math.abs(pos(mirror,plus).z-pos(mirror,minus).z)<1e-5,
 'Mirrored X brush footprints must have equal magnitude on symmetric geometry');
assert.equal(pos(mirror,far).z,0,'Unselected vertices may not move');
const pinch=apply(plane,stroke({operation:'pinch',strength:.14}));
const near=sample(plane,.1,0);
assert(Math.abs(pos(pinch,near).x)<Math.abs(pos(plane,near).x),
 'Pinch must bring tangential points toward the footprint center');
const inflate=apply(plane,stroke({operation:'inflate'}));
assert(pos(inflate,sample(plane,0,0)).z>.08);
const translate=apply(plane,stroke({operation:'translate'}));
assert(pos(translate,sample(plane,0,0)).z>.08);
const raised=plane.clone(),center=sample(raised,0,0);
raised.attributes.position.setZ(center,.20);
raised.computeVertexNormals();
const flatten=apply(raised,stroke({operation:'flatten',center:[0,0,0],
 radius:.3,selectionRadius:.3,strength:0}));
assert(pos(flatten,center).z<.2-1e-4&&pos(flatten,center).z>0,
 'Flatten must reduce height toward plane without ignoring radial falloff');
const smooth=apply(raised,stroke({operation:'smooth',center:[0,0,.20],
 radius:.3,selectionRadius:.3,strength:.4}));
assert(pos(smooth,center).z<.16,'Smooth must average actual connected triangle neighbors');
const snap=apply(plane,stroke({operation:'inflate',strength:.041,snap:.01}));
assert(Math.abs(pos(snap,sample(plane,0,0)).z-.04)<.001);
assert(c.atelierSculptFalloff(.5,'sharp')<c.atelierSculptFalloff(.5,'flat'));
const doubleSided=new THREE.BufferGeometry();
const geomA=new THREE.PlaneGeometry(.4,.4,8,8);
const geomB=geomA.clone();geomB.rotateY(Math.PI);geomB.translate(0,0,.03);
const aa=geomA.attributes.position,bb=geomB.attributes.position;
const na=geomA.attributes.normal,nb=geomB.attributes.normal,n=aa.count;
const points=[],normals=[];
for(const [p,nrm]of[[aa,na],[bb,nb]])for(let i=0;i<p.count;i++){
 points.push(p.getX(i),p.getY(i),p.getZ(i));
 normals.push(nrm.getX(i),nrm.getY(i),nrm.getZ(i));
}
doubleSided.setAttribute('position',new THREE.Float32BufferAttribute(points,3));
doubleSided.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
doubleSided.setIndex([...geomA.index.array,...Array.from(geomB.index.array,k=>k+n)]);
const isolated=apply(doubleSided,stroke({operation:'inflate'}));
assert(Math.abs(isolated.attributes.position.getZ(n+sample(geomB,0,0))-.03)<1e-6,
 'Front-facing inflation must NOT alter reverse-facing thin shell');
assert.deepEqual(Array.from(plane.attributes.position.array),Array.from(original),
 'Advanced operators must never mutate the source geometry');
for(const op of ['smooth','flatten','inflate','pinch','translate']){
 const record=stroke({operation:op,mirrorX:true});
 const a=apply(raised,record);
 const b=apply(raised,JSON.parse(JSON.stringify(record)));
 assert.deepEqual(Array.from(a.attributes.position.array),
   Array.from(b.attributes.position.array),
   'Native JSON stroke replay must be deterministic: '+op);
 assert.equal(a.attributes.position.count,raised.attributes.position.count);
}
console.log('V1127_ADVANCED_BRUSH_SMOOTH_FLATTEN_INFLATE_PINCH_TRANSLATE_MIRROR_LEGACY_PASS');
