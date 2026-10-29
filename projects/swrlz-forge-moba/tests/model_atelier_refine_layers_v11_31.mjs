import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';
const read=n=>fs.readFileSync(new URL('../runtime/'+n,import.meta.url),'utf8');
const c=vm.createContext({THREE,console});
vm.runInContext(['model_atelier_surface_targeting_v11_22.js',
 'model_atelier_sculpt_brush_v11_21.js',
 'model_atelier_surface_lasso_v11_22.js',
 'model_atelier_local_refinement_v11_23.js'].map(read).join('\n'),c);
const pin=(x,y)=>({point:[x,y,0],tri:0,bary:[1,0,0]});
const region={id:'region-1',name:'Cheek detail',pins:[
 pin(-.18,-.18),pin(.18,-.18),pin(.18,.18),pin(-.18,.18)],
 axis:[0,0,1],feather:.02,morph:0,enabled:true,resolution:[0,0]};
const old={id:'detail-one',regionId:'region-1',level:1,enabled:true};
const locked={...old,locked:true};
const p={sculptLassos:[region],refinementLayers:[old]};
assert(c.atelierRefineValid(p),'Legacy layers without locked property must import');
assert(c.atelierRefineValid({...p,refinementLayers:[locked]}));
assert(!c.atelierRefineValid({...p,refinementLayers:[{...locked,locked:'yes'}]}));
assert(!c.atelierRefineValid({...p,refinementLayers:[{...locked,inject:true}]}));
assert(!c.atelierRefineValid({...p,refinementLayers:[{...locked,locked:1}]}));
const original=JSON.stringify(p);
const result=c.atelierRefineDuplicateCandidate(p,0,'detail-copy-two');
assert(result.ok);assert.equal(result.index,1);
assert.equal(result.layers.length,2);
assert.equal(result.layers[0].id,'detail-one');
assert.equal(result.layers[1].enabled,false,'Clone must be disabled by default');
assert.equal(result.layers[1].locked,false,'Clone must be unlocked independently');
assert.equal(result.layers[1].regionId,'region-1');
assert.equal(result.layers[1].level,1);
assert.equal(JSON.stringify(p),original,'Planning a copy must not mutate original native part');
assert(c.atelierRefineValid({...p,refinementLayers:result.layers}));
assert(!c.atelierRefineDuplicateCandidate(p,0,'detail-one').ok,'Duplicate IDs rejected');
assert(!c.atelierRefineDuplicateCandidate(p,4,'unique').ok);
assert(!c.atelierRefineDuplicateCandidate(p,0,'').ok);
const cap={...p,refinementLayers:[
 old,{...old,id:'two',enabled:false},{...old,id:'three',enabled:false}]};
assert(!c.atelierRefineDuplicateCandidate(cap,0,'four').ok,'Mobile 3-layer cap preserved');
assert.equal(c.atelierRefineLayerLocked(old),false);
assert.equal(c.atelierRefineLayerLocked(locked),true);
assert.equal(c.atelierRefineCanMove(result.layers,1,0),true);
assert.equal(c.atelierRefineCanMove([{...locked},result.layers[1]],1,0),false,
 'Locked neighbor cannot move indirectly');
assert.equal(c.atelierRefineCanMove([{...old},{...locked,id:'other'}],0,1),false);
assert.equal(c.atelierRefineCanMove(result.layers,0,2),false);
const g=new THREE.PlaneGeometry(1,1,16,16);
const baseTriangles=c.atelierRefineCount(g);
const once=c.atelierRefineApply(g.clone(),p);
const withDisabled=c.atelierRefineApply(g.clone(),{
 ...p,refinementLayers:result.layers});
assert.equal(c.atelierRefineCount(once),c.atelierRefineCount(withDisabled),
 'Duplicating disabled must not change generated mesh triangle count');
assert.deepEqual(Array.from(once.attributes.position.array),
 Array.from(withDisabled.attributes.position.array),
 'Disabled copy must not alter generated topology');
const replay=JSON.parse(JSON.stringify({...p,refinementLayers:result.layers}));
assert(c.atelierRefineValid(replay));
assert.equal(replay.refinementLayers[1].locked,false);
console.log('V1131_DETAIL_LOCK_DISABLED_DUPLICATE_REORDER_LEGACY_GEOMETRY_PASS');
