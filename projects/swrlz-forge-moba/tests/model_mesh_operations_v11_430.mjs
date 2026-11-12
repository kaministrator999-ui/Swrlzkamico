import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
const threePath=process.argv[2]||process.env.SWYRLZ_THREE_MODULE;
assert.ok(threePath,'Pass a local Three r169 ES module as the first argument');
const THREE=await import(pathToFileURL(path.resolve(threePath)).href);
assert.equal(THREE.REVISION,'169');
const context=vm.createContext({console});
vm.runInContext(fs.readFileSync(path.join(root,'runtime/model_mesh_operations_v11_430.js'),'utf8')+'\nglobalThis.ops=se430MeshOps;',context);
const ops=context.ops;
const topology=fs.readFileSync(path.join(root,'runtime/model_atelier_topology_lod_v11_38.js'),'utf8');
const validStart=topology.indexOf('function atelierTopologyValid('),validEnd=topology.indexOf('function atelierTopologyGeometry(',validStart);
vm.runInContext('const atelierLODSavedVertices=9000,atelierLODSavedTriangles=16000;\n'+topology.slice(validStart,validEnd)+'\nglobalThis.nativeValid=atelierTopologyValid;',context);
vm.runInContext(fs.readFileSync(path.join(root,'runtime/model_atelier_topology_audit_v11_44.js'),'utf8')+'\nglobalThis.nativeAudit=atelierTopologyAudit;',context);
const clone=x=>JSON.parse(JSON.stringify(x));
const volume=data=>{
 let value=0;for(let f=0;f<data.indices.length;f+=3){const [a,b,c]=data.indices.slice(f,f+3).map(id=>data.positions.slice(id*3,id*3+3));
  value+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;}
 return value;
};
function checked(result,closed=true){
 assert.equal(result.ok,true,result.reason);assert.equal(context.nativeValid({kind:'topologyMesh',topologyMesh:result.data}),true);
 const audit=context.nativeAudit(result.data);assert.equal(audit.ok,true);assert.equal(audit.zeroAreaFaces,0);assert.equal(audit.nonManifoldEdges,0);assert.equal(audit.oppositeWindingErrors,0);
 if(closed)assert.equal(audit.boundaryEdges,0);return result;
}
const normalY=(data,f)=>{
 const p=data.indices.slice(f*3,f*3+3).map(id=>new THREE.Vector3(...data.positions.slice(id*3,id*3+3)));
 return p[1].sub(p[0]).cross(p[2].sub(p[0])).normalize().y;
};
const groups=[];function test(name,fn){fn();groups.push(name);}
const cubeGeometry=new THREE.BoxGeometry(1,1,1);
const cube=checked(ops.convert(cubeGeometry)).data;
const topSeed=Array.from({length:cube.indices.length/3},(_,f)=>f).find(f=>normalY(cube,f)>.999);
const top=ops.region(cube,[topSeed],{expand:true});
let inset,container;

test('Exact plain primitive conversion welds seams into closed editable native topology',()=>{
 assert.equal(cube.positions.length/3,8);assert.equal(cube.indices.length/3,12);assert.ok(Math.abs(volume(cube)-1)<1e-10);
 const stats=ops.convert(cubeGeometry).stats;assert.equal(stats.uvReprojected,true);assert.equal(cubeGeometry.attributes.position.count,24);
 const round=clone(cube);checked({ok:true,data:round});assert.deepEqual(round,clone(cube));
});
test('Viewport triangle resolves to a connected coplanar polygon face',()=>{
 assert.equal(top.ok,true,top.reason);assert.equal(top.triangleIds.length,2);assert.equal(top.boundary.length,4);assert.equal(top.convex,true);assert.ok(top.normal[1]>.999);
 assert.equal(ops.region(cube,[topSeed]).triangleIds.length,1);
 assert.equal(ops.region(cube,[0,topSeed]).ok,false);
});
test('Inset creates a real border, preserves cube volume and selects the smaller cap',()=>{
 const baseline=JSON.stringify(cube);inset=checked(ops.inset(cube,top.triangleIds,{fraction:.2}));assert.equal(JSON.stringify(cube),baseline);
 assert.equal(inset.data.indices.length/3,20);assert.equal(inset.selectedFaces.length,2);assert.equal(inset.data.positions.length/3,12);
 assert.ok(Math.abs(volume(inset.data)-1)<1e-10);
 const region=ops.region(inset.data,inset.selectedFaces);assert.equal(region.ok,true);assert.ok(Math.abs(region.stats.area-.64)<1e-9);
});
test('Inward connected-face extrusion forms a hollow container with a retained floor',()=>{
 const baseline=JSON.stringify(inset.data);container=checked(ops.extrude(inset.data,inset.selectedFaces,{depth:-.35}));assert.equal(JSON.stringify(inset.data),baseline);
 assert.equal(container.data.indices.length/3,28);assert.equal(container.data.positions.length/3,16);assert.equal(container.selectedFaces.length,2);
 assert.ok(Math.abs(volume(container.data)-(.776))<1e-9);
 const floor=ops.region(container.data,container.selectedFaces);assert.ok(Math.abs(floor.origin[1]-.15)<1e-9);assert.ok(floor.normal[1]>.999);
});
test('Outward extrusion adds attached walls without an internal source cap',()=>{
 const result=checked(ops.extrude(inset.data,inset.selectedFaces,{depth:.2}));assert.equal(result.data.indices.length/3,28);
 assert.ok(Math.abs(volume(result.data)-1.128)<1e-9);
 const cap=ops.region(result.data,result.selectedFaces);assert.ok(Math.abs(cap.origin[1]-.7)<1e-9);
});
test('Inward depth refuses to punch through existing surfaces',()=>{
 const before=JSON.stringify(inset.data);const bad=ops.extrude(inset.data,inset.selectedFaces,{depth:-1});assert.equal(bad.ok,false);assert.match(bad.reason,/surface|floor/);
 assert.equal(JSON.stringify(inset.data),before);assert.equal(ops.extrude(container.data,container.selectedFaces,{depth:-.65}).ok,false);
});
test('Inward whole-face extrusion rejects coincident walls and explains the required rim',()=>{
 const before=JSON.stringify(cube),bad=ops.extrude(cube,top.triangleIds,{depth:-.2});
 assert.equal(bad.ok,false);assert.match(bad.reason,/overlap.*wall.*Inset first/);assert.equal(JSON.stringify(cube),before);
 const out=checked(ops.extrude(cube,top.triangleIds,{depth:.2}));assert.ok(Math.abs(volume(out.data)-1.2)<1e-9);
});
test('Convex swept clearance detects small obstacles between rays and interior vertical surfaces',()=>{
 const append=(base,other)=>{const result=clone(base),offset=result.positions.length/3;result.positions.push(...other.positions);result.uvs.push(...other.uvs);result.indices.push(...other.indices.map(id=>id+offset));return result;};
 const geometry=new THREE.BoxGeometry(.03,.03,.03);geometry.translate(.21,.32,-.07);
 const obstacle=checked(ops.convert(geometry)).data,combined=append(inset.data,obstacle);checked({ok:true,data:combined});
 const before=JSON.stringify(combined),result=ops.extrude(combined,inset.selectedFaces,{depth:-.35});
 assert.equal(result.ok,false);assert.match(result.reason,/reach or pass another surface/);assert.equal(JSON.stringify(combined),before);geometry.dispose();
 const vertical={positions:[.17,.42,-.08,.17,.21,-.08,.17,.21,.08,.17,.42,.08],uvs:[0,0,0,1,1,1,1,0],indices:[0,1,2,0,2,3]};
 const withWall=append(inset.data,vertical);checked({ok:true,data:withWall},false);
 assert.equal(ops.extrude(withWall,inset.selectedFaces,{depth:-.35}).ok,false);
});
test('Dense but valid face regions reject before expensive interactive collision work',()=>{
 const geometry=new THREE.BoxGeometry(1,1,1,20,20,20),data=checked(ops.convert(geometry)).data;
 const seed=Array.from({length:data.indices.length/3},(_,f)=>f).find(f=>normalY(data,f)>.999);
 const region=ops.region(data,[seed],{expand:true});assert.equal(region.ok,true,region.reason);assert.equal(region.triangleIds.length,800);
 const baseline=JSON.stringify(data),result=ops.extrude(data,region.triangleIds,{depth:.1});
 assert.equal(result.ok,false);assert.match(result.reason,/interactive collision-check budget/);assert.equal(JSON.stringify(data),baseline);
 geometry.dispose();
});
test('Selected-face deletion creates an honest open boundary and never deletes the entire object',()=>{
 const result=checked(ops.deleteFaces(cube,top.triangleIds),false);assert.equal(result.data.indices.length/3,10);
 assert.equal(context.nativeAudit(result.data).boundaryEdges,4);assert.equal(result.selectedFaces.length,0);
 assert.equal(ops.deleteFaces(cube,Array.from({length:12},(_,i)=>i)).ok,false);
});
test('Solidify turns a complete planar open patch into a closed editable shell',()=>{
 const plane=new THREE.PlaneGeometry(1,.8,1,1);const surface=checked(ops.convert(plane),false);const ids=Array.from({length:surface.data.indices.length/3},(_,i)=>i);
 const result=checked(ops.solidify(surface.data,ids,{thickness:.12}));assert.equal(result.data.indices.length/3,12);assert.equal(result.data.positions.length/3,8);
 assert.ok(Math.abs(volume(result.data)-.096)<1e-8);assert.equal(ops.extrude(surface.data,ids,{depth:.1}).ok,false);
 assert.equal(ops.solidify(cube,top.triangleIds,{thickness:.1}).ok,false);plane.dispose();
});
test('Invalid, nonplanar, concave, branched and malformed regions reject without source writes',()=>{
 assert.equal(ops.inset(cube,top.triangleIds,{fraction:0}).ok,false);assert.equal(ops.extrude(cube,top.triangleIds,{depth:NaN}).ok,false);
 assert.equal(ops.solidify(cube,top.triangleIds,{thickness:-.1}).ok,false);assert.equal(ops.region(cube,[999]).ok,false);
 const malformed=clone(cube);malformed.indices[0]=999;assert.equal(ops.audit(malformed).ok,false);
 const duplicate=clone(cube);duplicate.indices.push(...duplicate.indices.slice(0,3));assert.equal(ops.audit(duplicate).ok,false);
 const concave={positions:[0,0,0,2,0,0,2,1,0,1,1,0,1,2,0,0,2,0],uvs:[0,0,1,0,1,.5,.5,.5,.5,1,0,1],indices:[0,1,3,1,2,3,0,3,5,3,4,5]};
 const r=ops.region(concave,[0,1,2,3]);assert.equal(r.ok,true,r.reason);assert.equal(r.convex,false);assert.equal(ops.inset(concave,[0,1,2,3],{fraction:.2}).ok,false);
});
test('Native UV limits and geometry budgets are enforced; rigged and painted conversion rejects',()=>{
 const painted=new THREE.BoxGeometry();painted.setAttribute('color',new THREE.Float32BufferAttribute(new Array(24*3).fill(1),3));assert.equal(ops.convert(painted).ok,false);painted.dispose();
 const skin=new THREE.BoxGeometry();skin.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(new Array(24*4).fill(0),4));assert.equal(ops.convert(skin).ok,false);skin.dispose();
 const bad=clone(cube);bad.uvs[0]=21;assert.equal(ops.audit(bad).ok,false);assert.equal(ops.limits.vertices,9000);assert.equal(ops.limits.faces,16000);
});
test('Repeated manual edits remain native, closed and source-independent',()=>{
 let current=clone(cube),selection=[...top.triangleIds];
 for(let i=0;i<5;i++){
  const r=checked(ops.inset(current,selection,{fraction:.1}));const e=checked(ops.extrude(r.data,r.selectedFaces,{depth:-.05}));current=e.data;selection=[...e.selectedFaces];
 }
 assert.ok(current.positions.length/3<100);assert.equal(context.nativeValid({kind:'topologyMesh',topologyMesh:clone(current)}),true);assert.ok(volume(current)>.5);
});
cubeGeometry.dispose();
console.log('MODEL_MESH_OPERATIONS_V11_430_PASS',JSON.stringify({groups:groups.length,three:THREE.REVISION,nativeValidator:true,nativeTopologyAudit:true,containerVolume:volume(container.data),operations:['convert','region','inset','extrude','deleteFaces','solidify']}));
