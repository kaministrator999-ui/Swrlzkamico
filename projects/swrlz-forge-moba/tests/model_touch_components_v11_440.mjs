import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const html=fs.readFileSync(process.argv[3],'utf8');
function fn(name){const start=html.indexOf('function '+name+'(');assert(start>=0,name);let i=html.indexOf('{',start),depth=0;for(;i<html.length;i++){if(html[i]==='{')depth++;else if(html[i]==='}'&&!--depth)return html.slice(start,i+1);}throw Error(name);}
const mesh=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshBasicMaterial()),camera=new THREE.OrthographicCamera(-1,1,1,-1,.01,10),rect={left:20,top:30,width:400,height:400};
camera.position.set(0,2,0);camera.up.set(0,0,-1);camera.lookAt(0,0,0);camera.updateProjectionMatrix();camera.updateMatrixWorld(true);mesh.updateMatrixWorld(true);
let rays=0;const raycaster=new THREE.Raycaster(),original=raycaster.intersectObject.bind(raycaster);raycaster.intersectObject=(...a)=>{rays++;return original(...a);};
const ctx=vm.createContext({THREE,camera,renderer:{domElement:{getBoundingClientRect:()=>rect}},mouse:new THREE.Vector2(),raycaster,atelierComponentTopologyCache:new WeakMap(),atelierMeshClamp:(n,a,b)=>Math.max(a,Math.min(b,n)),point:e=>({x:2*(e.clientX-rect.left)/rect.width-1,y:1-2*(e.clientY-rect.top)/rect.height})});
ctx.mesh=mesh;ctx.atelierComponentMode='vertex';
vm.runInContext(['atelierComponentTriangles','atelierComponentTopology','atelierComponentProject','atelierComponentScreen'].map(fn).join('\n')+'\nthis.top=atelierComponentTopology(mesh);',ctx);
ctx.atelierComponentTopologyForActive=()=>({mesh,topology:ctx.top});vm.runInContext(fn('atelierComponentHit'),ctx);
const pick=(x,y,type='touch',mode='vertex')=>{ctx.atelierComponentMode=mode;rays=0;return ctx.atelierComponentHit({clientX:x,clientY:y,pointerType:type});};
let groups=0;
for(const rep of ctx.top.vertices.filter(id=>mesh.geometry.attributes.position.getY(id)>.4)){
 const p=ctx.atelierComponentScreen(mesh,rep),x=p.x+(p.x<220?-2:2),y=p.y+(p.y<230?-2:2);
 assert.equal(pick(x,y),ctx.top.vertices.indexOf(rep),'Rounded silhouette tap must choose the native welded vertex');assert(rays>1&&rays<=9);groups++;
}
{
 const edge=ctx.top.edges.find(e=>e.every(id=>mesh.geometry.attributes.position.getY(id)>.4&&mesh.geometry.attributes.position.getZ(id)<-.4));
 const [a,b]=edge.map(i=>ctx.atelierComponentScreen(mesh,i)),x=(a.x+b.x)/2,y=(a.y+b.y)/2-2;
 assert.equal(pick(x,y,'touch','edge'),ctx.top.edges.indexOf(edge));assert(rays<=9);groups++;
 assert.equal(pick(x,y,'mouse','edge'),null);assert.equal(rays,1);assert.equal(pick(x,y,'touch','face'),null);assert.equal(rays,1);groups++;
}
assert.equal(pick(30,40),null);assert.equal(rays,9);groups++;
console.log('MODEL_TOUCH_COMPONENTS_440_PASS',JSON.stringify({groups,corners:4,maximumRays:9,nativeSeamOrdinals:true,mouseAndFaceUnchanged:true,missesStayMisses:true}));
