// Focused v11.466 ring kernel checks against the actual native se430 mesh audit.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=name=>fs.readFileSync(path.join(root,'runtime',name),'utf8');
const context=vm.createContext({console});
vm.runInContext(source('model_mesh_operations_v11_430.js')+'\n'+source('model_ring_kernel_v11_466.js')+
 '\nthis.nativeOps=se430MeshOps;this.ring=se466RingKernel;',context);
const {nativeOps,ring}=context;
const mesh=()=>({
 positions:[-1,0,-1,1,0,-1,1,0,1,-1,0,1,0,0,0],
 uvs:[0,0,1,0,1,1,0,1,.5,.5],
 indices:[0,1,4,1,2,4,2,3,4,3,0,4]
});
const plain=value=>JSON.parse(JSON.stringify(value));
const valid=d=>{const a=nativeOps.audit(d);assert.equal(a.ok,true,a.reason);return a;};
const original=mesh();valid(original);
const outline=ring.ringSelect(original,4,{steps:1,mode:'outline'});
assert.equal(outline.ok,true,outline.reason);
assert.deepEqual(plain(outline.vertexIds),[0,1,2,3]);
const fill=ring.ringSelect(original,4,{steps:1,mode:'fill'});
assert.equal(fill.ok,true);assert.equal(fill.vertexIds.length,5);
const arc=ring.ringSelect(original,4,{steps:1,mode:'outline',plane:'xz',arcStart:0,arcSweep:180});
assert.equal(arc.ok,true);assert.ok(arc.vertexIds.length<outline.vertexIds.length);
const before=JSON.stringify(original),cap=ring.capPoint([1,0,0],[0,0,0],{scale:2,offset:[1,2,3],tilt:[0,0,0]});
assert.deepEqual(plain(cap),[3,2,3]);
const moved=ring.transform(original,[0,1,2,3],{offset:[0,.4,0]});
assert.equal(moved.ok,true,moved.reason);valid(moved.data);
assert.deepEqual(plain(moved.data.uvs),original.uvs,'position-only edits must preserve UVs');
assert.equal(moved.data.positions[1],.4);
const half=ring.transform(original,arc.vertexIds,{offset:[.2,0,0],falloff:2});
assert.equal(half.ok,true,half.reason);valid(half.data);
const subdivided=ring.refine(original,[0,1,2,3]);
assert.equal(subdivided.ok,true,subdivided.reason);valid(subdivided.data);
assert.equal(subdivided.stats.addedVertices,4);
assert.equal(subdivided.data.indices.length/3,8);
assert.equal(ring.refine(original,[0]).ok,false,'single point has no selected edges');
const extruded=ring.extrudeBoundary(original,[0,1,2,3],{axis:'y',depth:1,scale:.85,offset:[.1,0,0]});
assert.equal(extruded.ok,true,extruded.reason);valid(extruded.data);
assert.equal(extruded.data.indices.length/3,12);
assert.equal(extruded.selectedVertices.length,4);
const second=ring.extrudeBoundary(extruded.data,plain(extruded.selectedVertices),{axis:'y',depth:.35,scale:.7});
assert.equal(second.ok,true,second.reason);valid(second.data);
assert.equal(ring.extrudeBoundary(original,[0,1],{depth:.2}).ok,false,'a partial arc cannot be blindly extruded');
assert.equal(ring.transform(original,[0],{scale:300}).ok,false,'unsafe scale rejected');
assert.equal(ring.ringSelect(original,4,{steps:90}).ok,false,'unbounded radius rejected');
assert.equal(JSON.stringify(original),before,'candidate operations must never mutate source');
console.log('v11.466 ring topology: selection, arc, transforms, falloff, subdivision, boundary extrusion, UVs, validation, immutability OK');
