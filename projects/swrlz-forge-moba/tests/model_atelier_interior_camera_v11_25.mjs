import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import * as THREE from 'three';
const src=fs.readFileSync(new URL('../runtime/model_atelier_viewport_v11_21.js',import.meta.url),'utf8');
const mesh=new THREE.Mesh(new THREE.SphereGeometry(.8,12,8),new THREE.MeshBasicMaterial());
mesh.userData.atelierId='test-mesh';mesh.position.set(.25,2,0);
const camera=new THREE.PerspectiveCamera(50,1,.1,1000);
const elements=new Map();
for(const id of ['ViewportMode','ViewportScope','ViewportColors','ViewportTextures','ViewportWireContrast',
 'ViewportWireTint','ViewportClipNear','ViewportClipFar','ViewportInsideExit']){
 elements.set(id,{value:'',checked:true,disabled:false});
}
const c=vm.createContext({THREE,console,camera,orbit:{distance:8.1,yaw:0,pitch:0},
 selection:'test-mesh',atelierDetailTarget:null,
 modelRoot:{children:[mesh]},renderer:{domElement:{getBoundingClientRect:()=>({width:400,height:600})}},
 partById:id=>id==='test-mesh'?{id,name:'Test sphere'}:null,
 $m:id=>elements.get(id)||null,cameraUpdate:()=>{},renderParts:()=>{},status:()=>{}});
vm.runInContext(src,c,{filename:'model_atelier_viewport_v11_21.js'});
const go=s=>vm.runInContext(s,c);
assert.equal(go('atelierViewportClipApply(.002,100)'),false);
assert.equal(go('atelierViewportClipApply(.01,301)'),false);
assert.equal(go('atelierViewportClipApply(.03,30)'),true);
assert.equal(camera.near,.03);assert.equal(camera.far,30);
assert.equal(go('atelierViewportInsideEnter()'),true);
assert.equal(go('atelierCameraInterior'),true);
assert(Math.abs(go('orbit.distance')-.16)<1e-8);
assert.equal(go('atelierViewOverrides.get("test-mesh")'),'xray');
assert.equal(go('atelierDetailTarget.distanceTo(new THREE.Vector3(.25,2,0))<1e-5'),true);
assert.equal(go('atelierViewportInsideExit()'),undefined);
assert.equal(go('atelierCameraInterior'),false);
assert.equal(go('atelierViewOverrides.has("test-mesh")'),false);
assert.equal(go('orbit.distance'),8.1);
assert.equal(camera.near,.03,'Camera near plane must be restored');
assert.equal(camera.far,30,'Camera far plane must be restored');
assert.equal(go('atelierViewportClipApply(-.1,30)'),false);
assert.equal(go('atelierViewportClipApply(.1,10000)'),false);
console.log('V1125_INSIDE_CAMERA_CLIPPING_NONDESTRUCTIVE_ENTER_EXIT_PASS');
