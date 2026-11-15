#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const src=fs.readFileSync(new URL('../runtime/model_hard_surface_orbit_v11_461.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../runtime/model_touch_dock_v11_461.css',import.meta.url),'utf8');
new vm.Script(src,{filename:'model_hard_surface_orbit_v11_461.js'});
class Vector3 {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new Vector3(this.x,this.y,this.z);}
 add(b){this.x+=b.x;this.y+=b.y;this.z+=b.z;return this;}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this;}
 toArray(){return [this.x,this.y,this.z];}
 distanceTo(b){return Math.hypot(this.x-b.x,this.y-b.y,this.z-b.z);}
 length(){return Math.hypot(this.x,this.y,this.z);}
}
class Box3 {
 constructor(){this.min=new Vector3(Infinity,Infinity,Infinity);this.max=new Vector3(-Infinity,-Infinity,-Infinity);}
 expandByObject(m){
  const [x,y,z]=m.center,[a,b,c]=m.size;
  const v=[x,y,z],sz=[a,b,c],l=['x','y','z'];
  for(let k=0;k<3;k++){this.min[l[k]]=Math.min(this.min[l[k]],v[k]-sz[k]/2);
   this.max[l[k]]=Math.max(this.max[l[k]],v[k]+sz[k]/2);}
  return this;
 }
 isEmpty(){return this.min.x>this.max.x;}
 getCenter(v){return v.set((this.min.x+this.max.x)/2,(this.min.y+this.max.y)/2,(this.min.z+this.max.z)/2);}
 getSize(v){return v.set(this.max.x-this.min.x,this.max.y-this.min.y,this.max.z-this.min.z);}
}
class EdgesGeometry{constructor(geometry,angle){this.source=geometry;this.angle=angle;}}
class LineBasicMaterial{constructor(props){Object.assign(this,props);}}
class LineSegments{constructor(geom,mat){this.geometry=geom;this.material=mat;this.userData={};}}
const sourceMaterial={flatShading:false,userData:{authored:true},clone(){return {flatShading:false,userData:{authored:true},clone:this.clone};}};
const cube={isMesh:true,visible:true,userData:{atelierId:'cube'},center:[3,1,-2],size:[1,1,1],
 geometry:{getIndex:()=>({count:60}),getAttribute:()=>({count:20})},
 material:sourceMaterial,children:[],add(child){this.children.push(child);}};
const p={id:'cube',kind:'topologyMesh'};
let mode='solid',cameraUpdates=0;
const orbit={yaw:.42,pitch:.12,distance:2.75};
const ctx=vm.createContext({
 THREE:{Vector3,Box3,EdgesGeometry,LineBasicMaterial,LineSegments},
 modelRoot:{children:[cube],updateWorldMatrix(){}},selection:null,
 atelierCameraInterior:false,camera:{},orbit,window:{},
 atelierDetailTarget:null,atelierCameraPan:new Vector3(0,.66,0),
 model:()=>({assemblies:null}),
 atelierViewModeFor:()=>mode,
 atelierViewModeApply:(mesh)=>mesh,
 cameraUpdate:()=>{cameraUpdates++;},
});
vm.runInContext(src,ctx);
const bridge=ctx.window.SWYRL_ENGINE_MODEL_HARD_SURFACE_461;
assert(bridge);
assert.equal(vm.runInContext('se461LowPolyEditable',ctx)(p,cube),true,'Simple editable indexed topology is eligible');
ctx.atelierViewModeApply(cube,p);
assert.equal(cube.children.length,1,'Unselected solid topology still has visible hard-surface edge guides');
assert.equal(cube.children[0].geometry.angle,25);
assert.equal(cube.children[0].material.depthTest,true);
assert.equal(cube.children[0].userData.se455OwnedGeometry,true);
ctx.atelierViewModeApply(cube,p);
assert.equal(cube.children.length,1,'No duplicate edge overlays');
mode='overlay';
cube.material=sourceMaterial;
ctx.atelierViewModeApply(cube,p);
assert.notEqual(cube.material,sourceMaterial,'Shaded wire uses a disposable material for correct hard face normals');
assert.equal(cube.material.flatShading,true);
assert.equal(sourceMaterial.flatShading,false,'Do not mutate original authored mesh material');
assert.equal(cube.material.userData.atelierViewportClone,true,'Native view switching disposes only owned materials');
assert.equal(vm.runInContext('se461AlignOrbitPivot()',ctx),true);
assert.deepEqual(bridge.inspect().bounds,[3,1,-2]);
assert.deepEqual(bridge.inspect().cameraPivot,[3,1,-2]);
assert.deepEqual(orbit,{yaw:.42,pitch:.12,distance:2.75},'Aligning orbit does not reset zoom or angles');
assert.equal(ctx.atelierCameraPan.y,0);
assert.equal(cameraUpdates,1);
assert.equal(vm.runInContext('se461AlignOrbitPivot()',ctx),false,'Centered camera does not jump or reframe twice');
const smoothMesh={...cube,geometry:{getIndex:()=>({count:900}),getAttribute:()=>({count:450})},children:[]};
assert.equal(vm.runInContext('se461LowPolyEditable',ctx)(p,smoothMesh),false,'Dense topology keeps existing smooth shading');
assert(css.includes('right:calc(var(--se320-right) + 1px)!important;'));
assert(css.includes('width:36px!important;'));
assert(!src.includes('setInterval(')&&!src.includes('checkpoint('));
if(process.argv[2]){
 const html=fs.readFileSync(process.argv[2],'utf8');
 for(const token of ['SWYRL_ENGINE_DEPLOY_MARKER: V11_461_MODEL_EDGES_ORBIT_DOCK',
 "window.SWRLZ_FORGE_BUILD={version:'v11.461'",
 'SE461_HARD_SURFACE_ORBIT_START','SE461_TOUCH_DOCK_BOUNDS_START',
 'flatShading:mode===\'flat\'||se461LowPolyEditable(part,mesh)',
 'if(!gesture.se461PivotAligned){se461AlignOrbitPivot();',
 'if(!pressed.se461PivotAligned){se461AlignOrbitPivot();',
 'SE460_NATIVE_VIEW_COMMANDS_START']){
  assert(html.includes(token),'Full engine missing '+token);
 }
}
console.log('SE461_NATIVE_MODEL_PASS: correct hard-edge shading, no source material mutation, bounded silhouette, actual orbit center and touch grip placement');
