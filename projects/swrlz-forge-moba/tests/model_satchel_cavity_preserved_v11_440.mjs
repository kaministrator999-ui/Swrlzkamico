import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
assert.ok(process.argv[2],'Pass local Three r169 ESM');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION,'169');
const opsctx=vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(ROOT,'runtime/model_mesh_operations_v11_430.js'),'utf8')+'\nthis.ops=se430MeshOps;',opsctx);
const ops=opsctx.ops;
const helperctx=vm.createContext({window:{},THREE,se430MeshOps:ops});
vm.runInContext(fs.readFileSync(path.join(ROOT,'runtime/se436_satchel_cavity.js'),'utf8'),helperctx);
const helper=helperctx.window.SWYRL_E_SATCHEL_CAVITY_436;
const cubeGeometry=new THREE.BoxGeometry(1,1,1);
const converted=ops.convert(cubeGeometry);cubeGeometry.dispose();assert.equal(converted.ok,true,converted.reason);
const cube=converted.data;
const normalY=f=>{
 const [a,b,c]=cube.indices.slice(f*3,f*3+3).map(i=>cube.positions.slice(i*3,i*3+3));
 return (b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]);
};
const top=Array.from({length:cube.indices.length/3},(_,i)=>i).find(i=>normalY(i)>.5);
const region=ops.region(cube,[top],{expand:true});assert.equal(region.ok,true,region.reason);
const inset=ops.inset(cube,region.triangleIds,{fraction:.2});assert.equal(inset.ok,true,inset.reason);
const inward=ops.extrude(inset.data,inset.selectedFaces,{depth:-.35});assert.equal(inward.ok,true,inward.reason);
const outward=ops.extrude(inset.data,inset.selectedFaces,{depth:.2});assert.equal(outward.ok,true,outward.reason);
const part=(d)=>({id:'model-seed',name:'Practice cube · shape into body',kind:'topologyMesh',scale:[1.4,1,.65],position:[0,1.5,0],topologyMesh:d});
let groups=0;
assert.equal(helper.inspect([part(cube)]).ok,false);assert.equal(helper.inspect([part(inset.data)]).ok,false);
assert.equal(helper.inspect([part(outward.data)]).ok,false);
assert.equal(helper.inspect([part(inward.data)]).ok,true);
const detail=helper.inspect([part(inward.data)]);assert.ok(detail.walls>=4);assert.ok(detail.capTriangles>=2);groups++;
const group=new THREE.Group();assert.equal(helper.makeGhost(group),true);assert.equal(group.children.length,1);
assert.equal(group.children[0].geometry.index.count/3,28);assert.equal(group.children[0].userData.editorOnly,true);
assert.equal(group.children[0].raycast(),undefined); // noninteractive tutorial helper
group.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose();}});groups++;
function xrFixture(kind='box'){
 const s={se430Manual:false,session:true,scene:true,mode:'grab',se430Operation:null};
 const part={id:'model-seed',kind},history=[],notices=[];
 const api={inspect:()=>({selection:{partId:part.id},convert:{available:kind==='box'}}),convert:()=>{part.kind='topologyMesh';return {ok:true};}};
 const ctx=vm.createContext({window:{},se340XR:s,se340VisibleSession:()=>true,
  se340ModelXRAction:action=>{history.push(action);if(action==='manual-mesh')s.se430Manual=true;
    if(action==='manual-extrude')s.se430Operation='extrude';return true;},
  ModelAtelier:{workshop:api},currentProject:{modelAtelier:{parts:[part]}},
  se340Notice:message=>notices.push(message),se340SyncUI:()=>{},se340Publish:()=>{},se350Invalidate:()=>{}});
 vm.runInContext(fs.readFileSync(path.join(ROOT,'runtime/se436_vr_cube_extrude.js'),'utf8'),ctx);
 return {s,part,history,notices,run:action=>vm.runInContext('se340ModelXRAction('+JSON.stringify(action)+')',ctx)};
}
let f=xrFixture();assert.equal(f.run('extrude'),true);assert.equal(f.part.kind,'topologyMesh');
assert.deepEqual(f.history,['manual-mesh','manual-extrude']);assert.equal(f.s.se430Manual,true);groups++;
f=xrFixture('topologyMesh');f.run('extrude');assert.deepEqual(f.history,['manual-mesh','manual-extrude']);groups++;
f=xrFixture('poly');f.run('extrude');assert.deepEqual(f.history,['extrude']);groups++;
const html=fs.readFileSync(process.argv[3],'utf8');
for(const text of ['V11_440_MODEL_TOOLS_VALIDATION','SE436_SATCHEL_CAVITY_START','SE436_VR_CUBE_EXTRUDE_START',
 'Inset and extrude one hollow body','Make editable','window.SWYRL_E_SATCHEL_CAVITY_436?.makeGhost(group)',
 "action==='manual-mesh'?'mesh'","['scale'],['convert','inset','extrude']"]){
 assert.ok(html.includes(text),'Missing assembled tutorial or Extrude route: '+text);
}
assert.ok(!html.includes("Detected '+s.walls.length+'/4 surrounding thin walls."));
groups++;
console.log('MODEL_SATCHEL_CAVITY_PRESERVED_440_PASS',JSON.stringify({groups,three:THREE.REVISION,cavity:'connected topology',ghostMeshes:1,vrCubeExtrude:true,outlineRoutingVerifiedSeparately:true}));
