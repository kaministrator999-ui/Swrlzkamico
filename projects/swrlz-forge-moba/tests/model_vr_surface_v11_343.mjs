#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[2])throw Error('Pass path to real Three r169 module');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION,'169');
const source=fs.readFileSync(root+'/runtime/model_vr_surface_pick_v11_343.js','utf8');
const state={hoverSurfaceCache:new WeakMap(),hoverGeometries:new Set(),hoverSurfaceMaterial:null,owned:new Set()};
const context={THREE,se340XR:state,se340Own:resource=>{state.owned.add(resource);return resource;}};
vm.createContext(context);
vm.runInContext(source+'\nglobalThis.test={make:se343HoverGeometry,surface:se343HoverContact,drop:se343DropHoverSurfaces};',context);
const api=context.test;
const material=new THREE.MeshStandardMaterial({color:0xffffff});
const sphere=new THREE.Mesh(new THREE.SphereGeometry(.5,96,64),material);
sphere.updateMatrixWorld(true);
sphere.raycast=()=>{throw Error('Hover must not cast native high-poly mesh');};
const ray=new THREE.Raycaster(new THREE.Vector3(0,0,3),new THREE.Vector3(0,0,-1),.01,5);
const hit=api.surface({id:'sphere',name:'Sphere',mesh:sphere},ray);
assert(hit?.hoverSurface,'high-resolution spherical model surface should hit');
assert(Math.abs(hit.point.z-.5)<.08,'reticle should be on surface, not AABB face');
const cached=state.hoverSurfaceCache.get(sphere);
assert(cached.proxy.geometry.index.count/3<=3600,'simplification should be bounded');
assert.equal(api.surface({id:'sphere',name:'Sphere',mesh:sphere},ray).point.z,hit.point.z);
assert.equal(state.hoverGeometries.size,1,'surface must be cached, not recreated');
const ring=new THREE.Mesh(new THREE.TorusGeometry(1,.25,30,100),material);
ring.updateMatrixWorld(true);
assert.equal(api.surface({id:'ring',name:'Ring',mesh:ring},ray),null,
 'bounding box intersects empty hole: reticle must NOT float in hole');
let ringSuccess=0,ringNative=0;
for(const [x,y] of [[1,.08],[.95,.2],[.86,.45],[.5,.84],[.3,.96]]){
 const line=new THREE.Raycaster(new THREE.Vector3(x,y,3),new THREE.Vector3(0,0,-1),.01,5);
 const baseline=[];ring.raycast(line,baseline);baseline.sort((a,b)=>a.distance-b.distance);
 const contact=api.surface({id:'ring',name:'Ring',mesh:ring},line);
 if(baseline.length)ringNative++;
 const delta=baseline.length&&contact?Math.abs(contact.distance-baseline[0].distance):null;
 if(delta!==null&&delta<.15)ringSuccess++;
 console.log('RING_SURFACE_SAMPLE',JSON.stringify({x,y,original:baseline[0]?.point.toArray(),proxy:contact?.point.toArray(),delta,faces:state.hoverSurfaceCache.get(ring)?.proxy?.geometry?.index?.count/3}));
}
assert(ringNative>=3,'original torus must have valid ring surface positions');
assert(ringSuccess>=2,'simplified surface must agree with original curved contact in multiple positions');
// The simplified hand proxy is still skinned by the original live skeleton.
const geo=new THREE.SphereGeometry(.5,80,60),n=geo.getAttribute('position').count;
const joints=new Uint16Array(n*4),weights=new Float32Array(n*4);
for(let i=0;i<n;i++)weights[i*4]=1;
geo.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(joints,4));
geo.setAttribute('skinWeight',new THREE.Float32BufferAttribute(weights,4));
const hand=new THREE.SkinnedMesh(geo,material),bone=new THREE.Bone();
hand.add(bone);hand.bind(new THREE.Skeleton([bone]));
hand.updateMatrixWorld(true);hand.skeleton.update();
hand.raycast=()=>{throw Error('Hover cannot raycast original dense skinned geometry');};
const h1=api.surface({id:'hand',name:'Hand',mesh:hand},ray);
assert(h1?.point.z>.40&&h1.point.z<.56,'skinned hover should reach surface');
bone.position.x=.2;hand.updateMatrixWorld(true);hand.skeleton.update();
const moved=api.surface({id:'hand',name:'Hand',mesh:hand},
 new THREE.Raycaster(new THREE.Vector3(.2,0,3),new THREE.Vector3(0,0,-1),.01,5));
assert(moved?.point.z>.40&&moved.point.z<.56,'hover follows live bone translation');
assert(state.hoverGeometries.size>=2);
api.drop();assert.equal(state.hoverGeometries.size,0);
assert.equal(state.hoverSurfaceCache.get(hand),undefined);
const patch=fs.readFileSync(root+'/patches/v11_343_model_vr_surface_camera.py','utf8');
for(const orientation of ['se340XR.pan.x-dx*dt*.42*gain','se340XR.pan.y+dy*dt*.42*gain',
 'se340XR.yaw+=dx*dt*1.35*gain','se340XR.pitch-dy*dt*1.05*gain'])
 assert(patch.includes(orientation),'camera control not remapped: '+orientation);
console.log('MODEL_VR_343_SURFACE_AND_CONTROLS_PASS',{faceCount:cached.proxy.geometry.index.count/3});
