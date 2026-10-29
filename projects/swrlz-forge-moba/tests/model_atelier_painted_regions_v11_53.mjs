import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8');
const c=vm.createContext({THREE,console});
vm.runInContext([
 'runtime/model_atelier_painted_regions_v11_53.js',
 'runtime/model_atelier_occluded_brush_v11_51.js',
 'runtime/model_atelier_surface_targeting_v11_22.js',
 'runtime/model_atelier_sculpt_brush_v11_21.js',
 'runtime/model_atelier_surface_lasso_v11_22.js',
 'runtime/model_atelier_local_refinement_v11_23.js'
].map(read).join('\n'),c);
const pin=(x,y)=>({point:[x,y,0],tri:0,bary:[1,0,0]});
const region=(paintDabs=[])=>({
 id:'lasso-paint',name:'Painted region',axis:[0,0,1],
 pins:[pin(-.1,-.1),pin(.1,-.1),pin(.1,.1),pin(-.1,.1)],
 feather:0,morph:.1,resolution:[0,0],enabled:true,paintDabs
});
const add={center:[.2,.15,0],axis:[0,0,1],radius:.09,op:'add'};
const erase={center:[0,0,0],axis:[0,0,1],radius:.09,op:'subtract'};
assert(c.atelierPaintDabsValid([add,erase]));
assert(!c.atelierPaintDabsValid([{...add,radius:Infinity}]));
assert(!c.atelierPaintDabsValid([{...add,axis:[0,0,0]}]));
assert(!c.atelierPaintDabsValid([{...add,op:'magic'}]));
assert(!c.atelierPaintDabsValid(Array(65).fill(add)));
assert(c.atelierLassoValid({sculptLassos:[region([add,erase])]}));
const base=region(),modified=region([add,erase]);
assert(c.atelierPaintCandidate(base,add).ok);
assert(!c.atelierPaintCandidate(modified,{...add,center:[NaN,0,0]}).ok);
const geometry=new THREE.PlaneGeometry(.6,.6,12,12);
const baseG=c.atelierSculptApply(geometry.clone(),{sculptLassos:[base]});
const painted=c.atelierSculptApply(geometry.clone(),{sculptLassos:[modified]});
const xyz=geometry.attributes.position;
let added=0,erased=0;
for(let i=0;i<xyz.count;i++){
 const x=xyz.getX(i),y=xyz.getY(i);
 if(Math.abs(x-.2)<1e-5&&Math.abs(y-.15)<1e-5){
  assert(baseG.attributes.position.getZ(i)<1e-6,'outside original polygon');
  assert(painted.attributes.position.getZ(i)>.09,'added selection should deform');
  added++;
 }
 if(Math.abs(x)<1e-5&&Math.abs(y)<1e-5){
  assert(baseG.attributes.position.getZ(i)>.09,'center belongs to original polygon');
  assert(Math.abs(painted.attributes.position.getZ(i))<1e-6,'erasure should exclude center');
  erased++;
 }
}
assert(added&&erased);
assert.equal(c.atelierPaintMaskContains([0,0,.3],false,[add]),false,'exclude opposite shell');
assert.equal(c.atelierPaintMaskContains([.2,.15,0],false,[add]),true);
assert.equal(c.atelierPaintMaskContains([.2,.15,0],false,[add,{...erase,center:[.2,.15,0]}]),false);
assert.deepEqual(JSON.parse(JSON.stringify(modified)),modified,'roundtrip exact native mask data');
console.log('V1153_PAINTED_LASSO_MASK_ADD_ERASE_SHELL_SCHEMA_GEOMETRY_PASS');
