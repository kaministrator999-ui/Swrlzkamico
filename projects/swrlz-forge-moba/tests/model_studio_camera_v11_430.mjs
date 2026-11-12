// Exercise the actual camera adapter with Three r169 and native clipping /
// interior / resize functions. No renderer, DOM imitation or screenshots are
// used to claim browser usability; that is covered by the focused app harness.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import path from 'node:path';

const root=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
const modulePath=process.argv[2]||'/workspace/scratch/vr340-tools/node_modules/three/build/three.module.js';
const THREE=await import(pathToFileURL(path.resolve(modulePath)).href);
assert.equal(THREE.REVISION,'169');
const code=fs.readFileSync(path.join(root,'runtime/model_studio_camera_v11_430.js'),'utf8');
const viewport=fs.readFileSync(path.join(root,'runtime/model_atelier_viewport_v11_21.js'),'utf8');
const original=fs.readFileSync(path.join(root,'runtime/model_atelier.js'),'utf8');
function nativeFunction(source,name){
 const start=source.indexOf('function '+name+'(');assert.ok(start>=0,name);
 const open=source.indexOf('{',start);let level=0;
 for(let at=open;at<source.length;at++){
  if(source[at]==='{')level++;
  else if(source[at]==='}'&&!--level)return source.slice(start,at+1);
 }
 throw Error('Unterminated native '+name);
}
function fixture(){
 const modelRoot=new THREE.Group();
 const a=new THREE.Mesh(new THREE.BoxGeometry(1,2,1),new THREE.MeshBasicMaterial());
 a.userData.atelierId='one';a.position.set(-2,1,1);a.rotation.set(.2,.4,.1);a.scale.set(.7,1.3,.9);modelRoot.add(a);
 const b=new THREE.Mesh(new THREE.BoxGeometry(2,1,3),new THREE.MeshBasicMaterial());
 b.userData.atelierId='two';b.position.set(3,2,-3);b.rotation.set(-.3,.6,0);modelRoot.add(b);
 const c=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshBasicMaterial());
 c.userData.atelierId='unselected';c.position.set(19,5,2);modelRoot.add(c);
 const parts=modelRoot.children.map(mesh=>({id:mesh.userData.atelierId,name:mesh.userData.atelierId,kind:'box',position:mesh.position.toArray(),rotation:mesh.rotation.toArray().slice(0,3),scale:mesh.scale.toArray()}));
 const source={parts,meshGroups:[{id:'assembly',parts:['one','two']}],references:[{id:'front',angle:'front'}]};
 let borrowed=false,infoCalls=0,viewRebuilds=0,panDelegations=0,poseDelegations=0,resizeCalls=0;
 const context={
  THREE,console,Math,Number,Object,Map,Set,Array,
  camera:new THREE.PerspectiveCamera(44,4/3,.1,100),
  modelRoot,model:()=>source,selection:'one',panel:null,stage:{clientWidth:800,clientHeight:600},
  renderer:{domElement:{getBoundingClientRect:()=>({width:800,height:600})},setSize:()=>{resizeCalls++;}},
  orbit:{yaw:.3,pitch:.19,distance:8.2},atelierDetailTarget:null,atelierCameraPan:new THREE.Vector3(),
  atelierCameraInterior:false,atelierInteriorPartId:null,atelierInteriorPreviousMode:null,atelierInteriorPreviousCamera:null,
  atelierViewOverrides:new Map(),atelierComponentMode:'mesh',atelierComponentIds:[],atelierHDDirty:false,
  se340ModelBridge:{isBorrowed:()=>borrowed},$m:()=>null,status:()=>{},
  atelierMeshActiveIds:()=>['one','two'],atelierMeshSelectedMeshes:()=>[a,b],
  atelierComponentTopologyForActive:()=>({mesh:a,topology:{}}),atelierComponentIndices:()=>[0,1,2],
  atelierViewportBounds:()=>({width:800,height:600}),
  partById:id=>parts.find(p=>p.id===id),
  atelierViewRebuild:()=>{viewRebuilds++;},atelierViewportControlsRefresh:()=>{},
  atelierViewportCameraInfoUpdate:()=>{infoCalls++;},
  atelierSetPoseCamera:()=>{poseDelegations++;return 'legacy';},
  atelierMeshFrameSelected:()=>{},
  atelierCameraPanByPixels:()=>{panDelegations++;},cameraUpdate:()=>{},
 };
 vm.createContext(context);
 vm.runInContext([
  ...['atelierViewportClipApply','atelierViewportInsideEnter','atelierViewportInsideExit'].map(name=>nativeFunction(viewport,name)),
  nativeFunction(original,'resize'),code,'globalThis.cameraTools=se430ModelCamera;'
 ].join('\n'),context);
 const snapshot=JSON.stringify(source);
 return {context,api:context.cameraTools,source,snapshot,meshes:[a,b,c],setBorrowed:value=>{borrowed=value;},counts:()=>({infoCalls,viewRebuilds,panDelegations,poseDelegations,resizeCalls})};
}
function near(a,b,epsilon=1e-8){assert.ok(Math.abs(a-b)<=epsilon,`${a} != ${b}`);}
function nearVector(a,b,epsilon=1e-8){a.forEach((value,k)=>near(value,b[k],epsilon));}
function projectedBounds(meshes,camera,limit=.861){
 const box=new THREE.Box3();for(const mesh of meshes)box.expandByObject(mesh);
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
  const p=new THREE.Vector3(x,y,z).project(camera);assert.ok(Math.abs(p.x)<=limit&&Math.abs(p.y)<=limit,JSON.stringify(p));assert.ok(p.z>=-1-1e-8&&p.z<=1+1e-8,'Frame clips depth');
 }
}
let groups=0;
{
 const f=fixture(),{context:c,api}=f;
 const views={front:[0,0,-1],back:[0,0,1],left:[1,0,0],right:[-1,0,0],top:[0,-1,0],bottom:[0,1,0]};
 for(const projection of ['perspective','orthographic']){
  assert.equal(api.setProjection(projection),true);
  for(const [view,direction]of Object.entries(views)){
   assert.equal(api.setView(view),true);const detail=api.inspect();
   assert.equal(detail.projection,projection);assert.equal(detail.view,view);nearVector(detail.direction,direction);
   if(view==='top')nearVector(detail.up,[0,0,-1]);if(view==='bottom')nearVector(detail.up,[0,0,1]);
   projectedBounds(f.meshes,c.camera);
  }
 }
 assert.equal(JSON.stringify(f.source),f.snapshot);groups++;
}
{
 const {context:c,api}=fixture();api.setView('front');api.setProjection('orthographic');
 const target=new THREE.Vector3(...api.inspect().target),a=target.clone().add(new THREE.Vector3(1,0,0)),b=a.clone().add(new THREE.Vector3(0,0,3));
 near(a.clone().project(c.camera).x,b.clone().project(c.camera).x);
 assert.equal(c.camera.isOrthographicCamera,true);near(c.camera.projectionMatrix.elements[15],1);
 api.setProjection('perspective');assert.equal(c.camera.isPerspectiveCamera,true);
 assert.ok(Math.abs(a.clone().project(c.camera).x-b.clone().project(c.camera).x)>.001,'Perspective must have depth foreshortening');groups++;
}
{
 const f=fixture(),{context:c,api}=f;
 for(const projection of ['perspective','orthographic']){
  api.setProjection(projection);api.setView('right');api.frame('selected');
  const selectedCenter=new THREE.Box3().expandByObject(f.meshes[0]).expandByObject(f.meshes[1]).getCenter(new THREE.Vector3());
  nearVector(api.inspect().target,selectedCenter.toArray());projectedBounds(f.meshes.slice(0,2),c.camera);
  assert.ok(Math.abs(new THREE.Vector3(...api.inspect().target).x-f.meshes[0].position.x)>.5,'Frame selection must cover both objects');
  api.frame('all');projectedBounds(f.meshes,c.camera);
 }
 assert.equal(JSON.stringify(f.source),f.snapshot);groups++;
}
{
 const f=fixture(),{context:c,api}=f;c.atelierComponentMode='vertex';c.atelierComponentIds=[0,1,2];
 api.setProjection('orthographic');assert.equal(api.frame('selected'),true);
 const expected=new THREE.Box3();for(const i of [0,1,2])expected.expandByPoint(new THREE.Vector3().fromBufferAttribute(f.meshes[0].geometry.attributes.position,i).applyMatrix4(f.meshes[0].matrixWorld));
 nearVector(api.inspect().target,expected.getCenter(new THREE.Vector3()).toArray());groups++;
}
{
 const f=fixture(),{context:c,api}=f;api.setView('front');api.setProjection('orthographic');api.frame('selected');
 const before=api.inspect(),unit=before.span.height/600;
 c.atelierCameraPanByPixels(60,30);nearVector(api.inspect().pan,[-60*unit,30*unit,0]);
 api.setProjection('perspective');c.atelierCameraPanByPixels(1,2);assert.equal(f.counts().panDelegations,1,'Preserve native perspective pan');groups++;
}
{
 const f=fixture(),{context:c,api}=f;api.setProjection('orthographic');api.setView('front');
 c.stage.clientWidth=360;c.stage.clientHeight=720;c.resize();
 near(api.inspect().aspect,.5);near(api.inspect().span.width/api.inspect().span.height,.5);
 const before=api.inspect().span.height;c.orbit.distance*=.5;c.cameraUpdate();near(api.inspect().span.height,before*.5);
 assert.equal(f.counts().resizeCalls,1);groups++;
}
{
 const f=fixture(),{context:c,api}=f;api.setProjection('orthographic');api.setView('front');
 assert.equal(c.atelierViewportClipApply(.025,120),true);assert.equal(c.atelierViewportClipApply(.6,120),false);
 near(api.inspect().near,.025);near(api.inspect().far,120);
 const before=api.inspect();assert.equal(c.atelierViewportInsideEnter(),true);
 assert.equal(api.inspect().interior,true);assert.equal(api.inspect().projection,'perspective');
 assert.equal(api.setProjection('orthographic'),false,'Interior projection must remain perspective');
 c.atelierViewportInsideExit();assert.equal(api.inspect().interior,false);assert.equal(api.inspect().projection,'orthographic');
 near(api.inspect().distance,before.distance);near(api.inspect().near,.025);near(api.inspect().far,120);
 assert.equal(c.atelierViewOverrides.size,0,'Interior shading override restored');assert.equal(JSON.stringify(f.source),f.snapshot);groups++;
}
{
 const f=fixture(),{context:c,api}=f;api.setView('top');c.orbit.pitch-=.03;c.cameraUpdate();
 assert.equal(api.inspect().view,'orbit');nearVector(api.inspect().up,[0,1,0]);
 assert.equal(c.atelierSetPoseCamera('left'),true);nearVector(api.inspect().direction,[1,0,0]);
 assert.equal(c.atelierSetPoseCamera('hero'),'legacy');assert.equal(f.counts().poseDelegations,1,'Preserve advanced pose camera routing');
 assert.equal(api.setView('unknown'),false);assert.equal(api.setProjection('fisheye'),false);groups++;
}
{
 const f=fixture(),{api}=f;const before=JSON.stringify(api.inspect());f.setBorrowed(true);
 assert.equal(api.setView('top'),false);assert.equal(api.setProjection('orthographic'),false);assert.equal(api.frame('all'),false);
 f.setBorrowed(false);assert.equal(JSON.stringify(api.inspect()),before,'Native camera cannot alter borrowed XR presentation');groups++;
}
{
 const f=fixture(),{context:c,api}=f;api.setProjection('orthographic');api.setView('left');
 c.camera=new THREE.PerspectiveCamera(44,2,.1,100);c.orbit={yaw:0,pitch:0,distance:9};c.cameraUpdate();
 assert.equal(api.inspect().projection,'orthographic','Reopened editor restores preferred projection using the new camera');near(api.inspect().aspect,2);
 assert.equal(JSON.stringify(f.source),f.snapshot);groups++;
}
console.log('MODEL_STUDIO_CAMERA_V11_430_PASS',JSON.stringify({groups,three:THREE.REVISION,exactViews:6,projections:['perspective','orthographic'],nativeClipInteriorResize:true,modelHistoryUnchanged:true,xrCameraBorrowGuard:true}));
