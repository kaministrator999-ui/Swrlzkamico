import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';
const src=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,console});
vm.runInContext([
 'model_atelier_surface_targeting_v11_22.js',
 'model_atelier_surface_lasso_v11_22.js'
].map(src).join('\n'),c);
const pin=(x,y)=>({point:[x,y,0],tri:0,bary:[1,0,0]});
const region={id:'edge',name:'Local jaw edge',axis:[0,0,1],
 pins:[pin(-.2,-.2),pin(.2,-.2),pin(.2,.2),pin(-.2,.2)],
 feather:0,morph:0,enabled:true,resolution:[0,0]};
const mesh={geometry:new THREE.PlaneGeometry(1,1,16,16)};
assert(c.atelierLassoValid({sculptLassos:[region]}));
const original=JSON.stringify(region);
const area=p=>{
 const xy=c.atelierLassoProjection({...region,pins:p,boundaryCurve:0}).poly;
 let sum=0;for(let i=0;i<xy.length;i++){
  const v=xy[i],w=xy[(i+1)%xy.length];sum+=v[0]*w[1]-w[0]*v[1];
 }return Math.abs(sum)/2;
};
const before=area(region.pins);
const grown=c.atelierLassoSegmentCandidate(region,mesh,0,.05);
const shrunk=c.atelierLassoSegmentCandidate(region,mesh,0,-.05);
assert(grown.ok);assert(shrunk.ok);
assert(area(grown.pins)>before);
assert(area(shrunk.pins)<before);
assert.equal(grown.pins.length,4);
assert.deepEqual(JSON.parse(JSON.stringify(grown.pins.slice(2))),
 JSON.parse(JSON.stringify(region.pins.slice(2))),
 'Only chosen segment endpoints may move');
assert(Math.abs(grown.pins[0].point[1]+.25)<1e-6);
assert(Math.abs(grown.pins[1].point[1]+.25)<1e-6);
assert(Math.abs(shrunk.pins[0].point[1]+.15)<1e-6);
assert(Math.abs(shrunk.pins[1].point[1]+.15)<1e-6);
assert.equal(JSON.stringify(region),original,'Preview must not mutate native lasso region');
for(const [index,amount] of [[-1,.05],[4,.05],[0,0],[0,.151],[0,-.151],[0,Infinity],[NaN,.05]])
 assert(!c.atelierLassoSegmentCandidate(region,mesh,index,amount).ok);
assert(!c.atelierLassoSegmentCandidate(region,null,0,.05).ok);
const smooth={...region,boundaryCurve:.8};
const smoothGrow=c.atelierLassoSegmentCandidate(smooth,mesh,0,.04);
assert(smoothGrow.ok);
assert(c.atelierLassoPolygonValid({...smooth,pins:smoothGrow.pins}));
const copied=JSON.parse(JSON.stringify({...region,pins:grown.pins}));
assert(c.atelierLassoValid({sculptLassos:[copied]}));
console.log('V1136_SELECTED_SEGMENT_GROW_SHRINK_SNAP_ATOMIC_PIN_COUNT_PASS',before,area(grown.pins),area(shrunk.pins));
