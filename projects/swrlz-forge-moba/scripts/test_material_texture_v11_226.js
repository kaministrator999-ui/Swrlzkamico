#!/usr/bin/env node
// §E v11.226 focused Material/Texture Studio contract tests (no browser suite).
'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
let seq=0,now=0;const steps=[],alerts=[];
class MColor{
 constructor(hex='#ffffff'){this.set(hex);}
 set(hex){const n=parseInt(String(hex).replace('#',''),16);
  this.r=((n>>>16)&255)/255;this.g=((n>>>8)&255)/255;this.b=(n&255)/255;return this;}
}
class MTexture{
 constructor(canvas){this.canvas=canvas;this.repeat={set:(x,y)=>{this.rx=x;this.ry=y;}};this.disposed=false;}
 dispose(){this.disposed=true;}
}
class MMaterial{
 constructor(props={}){this.isMeshStandardMaterial=true;this.color=new MColor();this.emissive=new MColor();
  this.side=props.side??0;this.map=null;this.disposed=false;this.roughness=.7;this.metalness=0;
  this.opacity=1;this.transparent=false;}
 clone(){let next=new MMaterial({side:this.side});Object.assign(next,this);
  next.color=new MColor();next.emissive=new MColor();next.disposed=false;return next;}
 dispose(){this.disposed=true;}
}
class MSphere{dispose(){this.disposed=true;}}
class MVec{
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z});}
 copy(v){Object.assign(this,{x:v.x,y:v.y,z:v.z});return this;}
}
class MMesh{
 constructor(geometry,material){this.geometry=geometry;this.material=material;this.userData={};this.isMesh=true;this.position=new MVec();this.rotation={y:0};}
 removeFromParent(){if(this.parent)this.parent.remove(this);}
}
const mockCanvas=()=>({
 width:256,height:256,ctx:null,
 getContext(){
  if(!this.ctx)this.ctx={fillRect(){},beginPath(){},moveTo(){},lineTo(){},stroke(){},fill(){},arc(){},drawImage(){}};
  return this.ctx;
 }
});
const scene={nodes:[],add(obj){this.nodes.push(obj);obj.parent=this;},remove(obj){this.nodes=this.nodes.filter(x=>x!==obj);obj.parent=null;}};
const initial=new MMaterial(),mesh=new MMesh(null,initial);
const actor={name:'Test Actor',userData:{id:'actor_100',actorType:'hero'},traverse:fn=>fn(mesh)};
const ctx={
 window:{SWYRL_ENGINE_STUDIOS:{active:()=> 'game'}},
 document:{createElement:name=>{if(name!=='canvas')throw Error('Unexpected element '+name);return mockCanvas();}},
 Image:class{}, THREE:{CanvasTexture:MTexture,MeshStandardMaterial:MMaterial,Mesh:MMesh,
  SphereGeometry:MSphere,Vector3:MVec,SRGBColorSpace:'srgb',RepeatWrapping:1,FrontSide:0},
 actors:[actor],selected:actor,scene,camera:{updateMatrixWorld(){},localToWorld:x=>x},
 playing:false,simulating:false,currentProject:{name:'Test Map'},
 uid:()=> 'a_'+String(++seq).padStart(6,'0'),
 structuredClone,toast:msg=>alerts.push(msg),beginTransaction:()=>{},
 commitTransaction:msg=>steps.push(msg),performance:{now:()=>now},
 se225MaterialUIRefresh:()=>{}
};
vm.createContext(ctx);
const file=path.join(__dirname,'../runtime/material_texture_core_v11_226.js');
vm.runInContext(fs.readFileSync(file,'utf8'),ctx,{filename:'material_texture_core_v11_226.js'});
const api=ctx.window.SWYRL_ENGINE_MATERIALS;
assert.equal(api.schema,'swyrl-material-studio-v1');
assert.equal(api.presets().length,10);
const wood=api.create('wood');assert.equal(api.list().length,1);
assert.equal(ctx.currentProject.materialStudio.materials[0].pattern,'wood');
assert.ok(api.edit(wood.id,{roughness:.41}));
const count=steps.length;
assert.equal(api.edit(wood.id,{roughness:Infinity}),false);
assert.equal(steps.length,count,'rejected edits must not touch history');
assert.equal(api.list()[0].roughness,.41,'rejected edit leaves material unchanged');
const painted=[{color:'#7bfaff',width:.025,points:[[.1,.2],[.2,.3],[.5,.8]]}];
assert.ok(api.edit(wood.id,{strokes:painted}));
assert.equal(api.list()[0].strokes[0].points.length,3);
assert.equal(api.assign('actor_100',wood.id),true);
vm.runInContext('se225MaterialSync(true)',ctx);
assert.notEqual(mesh.material,initial,'3D actor must receive authored PBR material');
assert.ok(mesh.material.map instanceof MTexture,'3D assigned material must contain a generated texture');
assert.equal(mesh.material.roughness,.41);
assert.equal(mesh.material.map.canvas.width,256);
assert.equal(api.inspect().assignments,1);
let oldApplied=mesh.material;
assert.ok(api.unassign('actor_100'));
vm.runInContext('se225MaterialSync(true)',ctx);
assert.equal(mesh.material,initial,'Unassign restores exact authored base material');
assert.equal(oldApplied.disposed,true,'Old 3D material disposed on unassign');
const gold=api.create('gold');
assert.ok(api.duplicate(gold.id));assert.equal(api.list().length,3);
assert.ok(api.remove(gold.id));assert.equal(api.list().length,2);
const portable=JSON.parse(JSON.stringify(api.export()));
assert.equal(portable.assignments.length,0,'portable material library has no project-specific actor IDs');
assert.equal(api.import({schema:'swyrl-material-studio-v1',materials:[{name:'bad'}],assignments:[]}),false);
assert.equal(api.list().length,2,'invalid imported library must not erase authored data');
assert.equal(api.import(portable),true);
assert.equal(api.list().length,2,'valid library import round trip');
const saved=JSON.stringify(ctx.currentProject.materialStudio);
ctx.currentProject={name:'Other Scene',materialStudio:{
 schema:'swyrl-material-studio-v1',materials:[{name:'bad'}],assignments:[]}};
vm.runInContext('se225MaterialSync(true)',ctx);
assert.equal(api.list().length,0,'malformed external project materials are not trusted');
assert.equal(mesh.material,initial);
ctx.currentProject={name:'Restored',materialStudio:JSON.parse(saved)};
vm.runInContext('se225MaterialSync(true)',ctx);
assert.equal(api.list().length,2,'saved project metadata round trips');
ctx.playing=true;
assert.equal(api.create('magic'),false,'cannot mutate authoring data in gameplay');
assert.ok(steps.length>=8);
console.log(JSON.stringify({status:'PASS',tests:'presets,validate,paint,assign,restore,texture GPU,import,scene switch,history',materials:api.list().length,steps:steps.length}));
