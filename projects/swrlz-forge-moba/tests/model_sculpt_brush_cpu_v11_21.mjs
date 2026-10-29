import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8');
const c=vm.createContext({THREE,console});
vm.runInContext(read('runtime/model_atelier_sculpt_brush_v11_21.js')+'\n'+read('runtime/model_atelier_surface_lasso_v11_22.js')+'\n'+read('runtime/model_atelier_local_refinement_v11_23.js'),c);
const mode=(extra={})=>({
 center:[0,0,1],axis:[0,0,1],radius:.65,strength:.2,
 falloff:'smooth',half:false,yaw:0,pitch:0,snap:0,plateau:0,taper:.5,level:false,...extra
});
const sphere=()=>new THREE.SphereGeometry(1,48,32);
const baseline=sphere();
const original=baseline.attributes.position;
const raised=c.atelierSculptApply(sphere(),{sculptBrushes:[mode()]});
const lowered=c.atelierSculptApply(sphere(),{sculptBrushes:[mode({strength:-.2})]});
assert(c.atelierSculptValid({sculptBrushes:[mode()]}));
assert(!c.atelierSculptValid({sculptBrushes:[mode({radius:Infinity})]}));
assert(!c.atelierSculptValid({sculptBrushes:[mode({axis:[0,0,0]})]}));
assert(!c.atelierSculptValid({sculptBrushes:[mode({plateau:2})]}));
assert(!c.atelierSculptValid({sculptBrushes:[mode({level:'notBoolean'})]}));
assert(!c.atelierSculptValid({sculptBrushes:[mode({taper:NaN})]}));
assert(!c.atelierSculptValid({sculptBrushes:Array(33).fill(mode())}));
let moved=0,center=.0,far=0;
for(let i=0;i<original.count;i++){
 const x=original.getX(i),y=original.getY(i),z=original.getZ(i),d=Math.hypot(x,y,z-1);
 const up=raised.attributes.position.getZ(i)-z,down=lowered.attributes.position.getZ(i)-z;
 assert(Number.isFinite(up));
 if(d<.17){center=Math.max(center,up);assert(Math.abs(up+down)<1e-5);}
 if(d>.65){assert(Math.abs(up)<1e-6);far++;}
 if(up>.0001)moved++;
}
assert(center>.17&&moved>25&&far>1000,'Spherical brush must affect local vertices with bounded falloff');
const full=c.atelierSculptApply(sphere(),{sculptBrushes:[mode({plateau:1,radius:1.9,strength:.16})]});
let fullInterior=0;
for(let i=0;i<original.count;i++){
 const x=original.getX(i),y=original.getY(i),z=original.getZ(i),d=Math.hypot(x,y,z-1);
 if(d<1.4){assert(Math.abs((full.attributes.position.getZ(i)-z)-.16)<1e-5);fullInterior++;}
}
assert(fullInterior>500,'Full-radius plateau must apply full strength everywhere inside');
const level=c.atelierSculptApply(sphere(),{sculptBrushes:[mode({radius:1.4,plateau:1,strength:.12,level:true})]});
const preserve=c.atelierSculptApply(sphere(),{sculptBrushes:[mode({radius:1.4,plateau:1,strength:.12,level:false})]});
let flatten=0,uneven=0;
for(let i=0;i<original.count;i++){
 const x=original.getX(i),y=original.getY(i),z=original.getZ(i),d=Math.hypot(x,y,z-1);
 if(d<.9){
  assert(Math.abs(level.attributes.position.getZ(i)-1.12)<1e-5,'Level-to-plane should remove existing uneven height');
  flatten++;
  if(Math.abs(preserve.attributes.position.getZ(i)-1.12)>.1)uneven++;
 }
}
assert(flatten>50&&uneven>50,'Preserve mode must retain local relief vs level mode');
const half=c.atelierSculptApply(sphere(),{sculptBrushes:[mode({center:[0,0,0],half:true,radius:1.4})]});
let halfRaised=0;
for(let i=0;i<original.count;i++){
 const z=original.getZ(i),dz=half.attributes.position.getZ(i)-z;
 if(z<-.27)assert(Math.abs(dz)<1e-6);
 if(z>.32&&dz>.01)halfRaised++;
}
assert(halfRaised>150,'Rotatable hemisphere must sculpt the chosen side');
const turned=c.atelierSculptApply(sphere(),{sculptBrushes:[mode({center:[0,0,0],half:true,radius:1.4,yaw:Math.PI/2})]});
let changedAlongX=0;
for(let i=0;i<original.count;i++){
 if(original.getX(i)>.35&&Math.abs(turned.attributes.position.getX(i)-original.getX(i))>.01)changedAlongX++;
}
assert(changedAlongX>100,'Rotating the hemisphere must rotate displacement axis');
const snapped=c.atelierSculptApply(sphere(),{sculptBrushes:[mode({snap:.01})]});
for(let i=0;i<original.count;i++){
 const dz=snapped.attributes.position.getZ(i)-original.getZ(i);
 assert(Math.abs(dz/.01-Math.round(dz/.01))<.0001);
}
const resolution={u:48,v:32};
const edit={indices:[0,1],delta:[0,.1,0],resolution:[48,32]};
assert(c.atelierSculptValid({sculptVertexEdits:[edit]}));
assert(!c.atelierSculptValid({sculptVertexEdits:[{...edit,indices:[0,0]}]}));
assert(!c.atelierSculptValid({sculptVertexEdits:[{...edit,delta:[Infinity,0,0]}]}));
const manual=c.atelierSculptApply(sphere(),{meshDensity:resolution,sculptVertexEdits:[edit]});
assert(Math.abs(manual.attributes.position.getY(0)-original.getY(0)-.1)<1e-5);
assert.equal(manual.attributes.position.getY(2),original.getY(2));
const differentResolution=c.atelierSculptApply(sphere(),{meshDensity:{u:64,v:48},sculptVertexEdits:[edit]});
assert.equal(differentResolution.attributes.position.getY(0),original.getY(0));
const saved=JSON.stringify({sculptBrushes:[mode()],sculptVertexEdits:[edit]});
assert(c.atelierSculptValid(JSON.parse(saved)));
console.log('SCULPT_BRUSH_SPHERE_TAPER_LEVEL_HEMISPHERE_SNAP_VERTEX_SELECTION_REPLAY_PASS',moved,flatten);
