import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
import * as THREE from 'three';
const read=x=>fs.readFileSync(new URL('../'+x,import.meta.url),'utf8');
const c=vm.createContext({THREE,console});
vm.runInContext(
 read('runtime/model_atelier_surface_targeting_v11_22.js')+'\n'+
 read('runtime/model_atelier_sculpt_brush_v11_21.js')+'\n'+
 read('runtime/model_atelier_surface_lasso_v11_22.js')+'\n'+read('runtime/model_atelier_local_refinement_v11_23.js'),c);
const pt=(x,y)=>({point:[x,y,0],tri:0,bary:[1,0,0]});
const region=(other={})=>({
 id:'lasso-test',name:'Nose target',pins:[pt(-.12,-.12),pt(.12,-.12),pt(.12,.12),pt(-.12,.12)],
 axis:[0,0,1],feather:.035,morph:.1,enabled:true,resolution:[0,0],...other
});
const good=region(),g=new THREE.PlaneGeometry(.5,.5,12,12);
assert(c.atelierLassoValid({sculptLassos:[good]}));
assert(c.atelierLassoPolygonValid(good));
const changed=c.atelierSculptApply(g.clone(),{sculptLassos:[good]});
const a=g.attributes.position,b=changed.attributes.position;
let inside=0,outside=0;
for(let i=0;i<a.count;i++){
 const x=a.getX(i),y=a.getY(i),dz=b.getZ(i)-a.getZ(i);
 if(Math.abs(x)<.09&&Math.abs(y)<.09){assert(dz>.02,'Interior vertices should be extruded with edge feathering');inside++;}
 if(Math.abs(x)>.2||Math.abs(y)>.2){assert(Math.abs(dz)<1e-6,'Unselected vertices must not move');outside++;}
}
assert(inside>3&&outside>30);
assert(c.atelierLassoValid({sculptLassos:[region({morph:-.1})]}));
const inward=c.atelierSculptApply(g.clone(),{sculptLassos:[region({morph:-.1})]});
assert(inward.attributes.position.getZ(84)<-.075,'Intrusion should move selected surface inward');
const disabled=c.atelierSculptApply(g.clone(),{sculptLassos:[region({enabled:false})]});
assert.deepEqual(Array.from(disabled.attributes.position.array),Array.from(a.array));
const crossing=region({pins:[pt(-.12,-.12),pt(.12,.12),pt(.12,-.12),pt(-.12,.12)]});
assert(!c.atelierLassoPolygonValid(crossing),'Pin crossings must be rejected');
assert(!c.atelierLassoValid({sculptLassos:[region({feather:-1})]}));
assert(!c.atelierLassoValid({sculptLassos:[region({morph:Infinity})]}));
assert(!c.atelierLassoValid({sculptLassos:[region({pins:[pt(0,0)]})]}));
assert(!c.atelierLassoValid({sculptLassos:[region({axis:[0,0,0]})]}));
const moved=region({pins:[pt(-.15,-.12),pt(.12,-.12),pt(.12,.12),pt(-.12,.12)]});
assert(c.atelierLassoValid({sculptLassos:[moved]}));
const before=JSON.stringify(good),after=JSON.stringify(JSON.parse(before));
assert.equal(after,before,'Native reference regions must survive JSON serialization');
console.log('V1122_BOUNDARY_PINS_REGION_MORPH_FEATHER_UNDO_SCHEMA_PASS',inside,outside);
