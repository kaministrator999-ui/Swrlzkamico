#!/usr/bin/env node
// §E v11.446: a cube square face is TWO triangles, selected as ONE region.
// Verify real native region geometry and the shipped touch pick adapter.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const html=fs.readFileSync(process.argv[2],'utf8');

const start='/* SE430_MODEL_MESH_OPERATIONS_START */';
const end='/* SE430_MODEL_MESH_OPERATIONS_END */';
const a=html.indexOf(start),b=html.indexOf(end,a);
assert(a>=0&&b>a,'Native mesh operations missing');
const ctx=vm.createContext({});
vm.runInContext(html.slice(a,b+end.length)+'\nthis.meshOps=se430MeshOps;',ctx);
const ops=ctx.meshOps;
const vertices=[
 [-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],
 [-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]
];
const quads=[
 [4,5,6,7], // front (+Z)
 [1,0,3,2], // back (-Z)
 [5,1,2,6], // right (+X)
 [0,4,7,3], // left (-X)
 [7,6,2,3], // top (+Y)
 [0,1,5,4]  // bottom (-Y)
];
const cube={
 positions:vertices.flat(),
 uvs:vertices.flatMap(p=>[(p[0]+1)/2,(p[1]+1)/2]),
 indices:quads.flatMap(([a,b,c,d])=>[a,b,c,a,c,d])
};
assert.equal(ops.audit(cube).ok,true,'Welded cube must be valid closed topology');
for(let side=0;side<6;side++){
 const first=side*2,second=first+1;
 const a=ops.region(cube,[first],{expand:true}),b=ops.region(cube,[second],{expand:true});
 assert.equal(a.ok,true,'First triangle should expand to quad region '+side);
 assert.equal(b.ok,true,'Second triangle should expand to quad region '+side);
 assert.deepEqual(Array.from(a.triangleIds),[first,second], 'First seed expands to its full square');
 assert.deepEqual(Array.from(b.triangleIds),[first,second], 'Second seed expands to the same square');
 assert.equal(a.boundary.length,4,'Square must have four outer edges');
 assert.equal(b.boundary.length,4,'Square must have four outer edges');
 const selected=ops.region(cube,[first]);assert.equal(selected.ok,true);
 assert.equal(selected.triangleIds.length,1,'Native explicit triangle edit is preserved');
}
const normal=ops.region(cube,[0],{expand:true});
const inset=ops.inset(cube,normal.triangleIds,{fraction:.2});
assert.equal(inset.ok,true,'Inset should accept the full square region: '+inset.reason);
assert.equal(inset.selectedFaces.length,2,'The new inset cap remains two triangles that form a square');

const beginning='/* SE446_PLANAR_FACE_TAP_START */',ending='/* SE446_PLANAR_FACE_TAP_END */';
const c=html.indexOf(beginning),d=html.indexOf(ending,c);
assert(c>=0&&d>c,'Face tap integration missing');
const source=html.slice(c,d+ending.length);
const context=vm.createContext({
 atelierComponentMode:'face',atelierComponentMulti:false,selection:'cube',
 se430ModelWorkshop:{selectRegion:(id,part)=>({ok:true,partId:part,faceIds:ops.region(cube,[id],{expand:true}).triangleIds})},
 status:()=>{}
});
vm.runInContext(source+'\nthis.pick=se446SelectPlanarFace;',context);
assert.equal(context.pick(0),true);assert.equal(context.pick(1),true);
assert.equal(context.pick(null),false);
context.atelierComponentMulti=true;assert.equal(context.pick(0),false,'Multi preserves triangle precision');
context.atelierComponentMulti=false;context.atelierComponentMode='edge';assert.equal(context.pick(0),false,'Edge selection is unchanged');
context.atelierComponentMode='face';
let warning='';
context.se430ModelWorkshop={selectRegion:()=>({ok:false,reason:'Convert this plain primitive to editable topology before selecting a region.'})};
context.status=(message)=>{warning=message;};
assert.equal(context.pick(0),true);
assert.match(warning,/Make mesh editable first/i,'Plain primitive gives conversion guidance');
assert(html.includes("if(!d.moved){const hitId=atelierComponentHit(e);if(!se446SelectPlanarFace(hitId))atelierComponentChoose(hitId);}"));
assert(html.includes('1 flat face selected ('));
assert(html.includes('1 FLAT FACE · '));
console.log('SE446_PLANAR_FACE_PICK_PASS: six cube faces, either seed selects whole quad, native Inset, touch face/Multi/Edge guards');
