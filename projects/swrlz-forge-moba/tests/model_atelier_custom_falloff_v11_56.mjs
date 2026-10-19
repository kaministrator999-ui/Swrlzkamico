import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const read=p=>fs.readFileSync(new URL('../runtime/'+p,import.meta.url),'utf8');
const c=vm.createContext({THREE,console});
vm.runInContext([
 'model_atelier_custom_falloff_v11_56.js',
 'model_atelier_surface_targeting_v11_22.js',
 'model_atelier_sculpt_brush_v11_21.js',
 'model_atelier_brush_ops_v11_27.js',
 'model_atelier_surface_lasso_v11_22.js',
 'model_atelier_local_refinement_v11_23.js'
].map(read).join('\n'),c);
const knots=[1,.98,.47,.07,0];
assert(c.atelierSculptCurveValid(knots));
assert(c.atelierSculptCurveValid(undefined),'legacy strokes remain supported');
for(const wrong of [[1,.8,.9,.2,0],[1,.5,.1,0],[0,.5,.3,.2,0],
 [1,.8,.6,.3,.01],[1,NaN,.3,.2,0],[1,.9,-.1,0,0],null]){
 assert(!c.atelierSculptCurveValid(wrong));
}
const stroke={falloff:'smooth',plateau:.25,taper:.5,falloffCurve:knots};
for(const [distance,expected]of [[0,1],[.25,.98],[.5,.47],[.75,.07],[1,0]]){
 assert(Math.abs(c.atelierSculptCurveWeight(distance,stroke)-expected)<1e-12);
}
let prev=1;for(let i=1;i<=100;i++){
 const next=c.atelierSculptCurveWeight(i/100,stroke);
 assert(next<=prev+1e-12&&next>=0&&next<=1,'monotone bounded falloff');
 prev=next;
}
assert.equal(c.atelierSculptCurveWeight(.4,{...stroke,falloffCurve:undefined}),
 c.atelierSculptFalloff(.4,'smooth',.25,.5),'prior presets bit-for-bit identical');
const s={center:[0,0,0],axis:[0,0,1],radius:.4,strength:.12,half:false,
 level:false,pitch:0,yaw:0,snap:0,falloff:'smooth',plateau:.25,taper:.5,
 falloffCurve:knots,surfaceMode:'through',selectionRadius:.4,operation:'push',
 offsetU:0,offsetV:0};
assert(c.atelierSculptValid({sculptBrushes:[s]}));
assert(!c.atelierSculptValid({sculptBrushes:[{...s,falloffCurve:[1,.2,.9,.1,0]}]}));
const g=new THREE.PlaneGeometry(.8,.8,16,16);
const out=c.atelierSculptApply(g.clone(),{sculptBrushes:[s]});
const mid=(g.attributes.position.count-1)>>1;
assert(out.attributes.position.getZ(mid)>g.attributes.position.getZ(mid));
const coords=Array.from(g.attributes.position.array);
const after=Array.from(out.attributes.position.array);
assert.notDeepEqual(after,coords,'curve influences actual saved native geometry');
const legacy={...s};delete legacy.falloffCurve;
assert(c.atelierSculptValid({sculptBrushes:[legacy]}));
assert.notDeepEqual(
 Array.from(c.atelierSculptApply(g.clone(),{sculptBrushes:[legacy]}).attributes.position.array),
 after,'custom envelope materially changes falloff');
console.log('V1156_NATIVE_FIVE_KNOT_CURVE_SCHEMA_MONOTONE_GEOMETRY_LEGACY_PASS');
