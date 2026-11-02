#!/usr/bin/env node
/* §E v11.224 narrow Particle Studio contracts; no browser, build runner or network required. */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path');
let uid=0;
class Color {
 constructor(hex='#ffffff'){this.set(hex);}
 set(hex){const v=parseInt(String(hex).slice(1),16);
  this.r=((v>>16)&255)/255;this.g=((v>>8)&255)/255;this.b=(v&255)/255;return this;}
 copy(o){this.r=o.r;this.g=o.g;this.b=o.b;return this;}
 lerp(o,t){this.r+=(o.r-this.r)*t;this.g+=(o.g-this.g)*t;this.b+=(o.b-this.b)*t;return this;}
 multiplyScalar(x){this.r*=x;this.g*=x;this.b*=x;return this;}
}
class Vec{
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z});}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z;}
 set(x,y,z){Object.assign(this,{x,y,z});return this;}
 normalize(){const n=Math.sqrt(this.lengthSq())||1;return this.multiplyScalar(1/n);}
 multiplyScalar(n){this.x*=n;this.y*=n;this.z*=n;return this;}
 toArray(){return [this.x,this.y,this.z];}
}
class BufferAttribute{
 constructor(array,size){this.array=array;this.itemSize=size;}
 setXYZ(i,x,y,z){this.array[i*3]=x;this.array[i*3+1]=y;this.array[i*3+2]=z;}
}
class BufferGeometry{
 constructor(){this.attributes={};}
 setAttribute(name,value){this.attributes[name]=value;return this;}
 getAttribute(name){return this.attributes[name];}
 setDrawRange(start,count){this.drawRange={start,count};}
 dispose(){this.disposed=true;}
}
class PointsMaterial{constructor(p){Object.assign(this,p);}dispose(){this.disposed=true;}}
class Points{
 constructor(g,m){this.geometry=g;this.material=m;this.userData={};this.parent=null;}
 removeFromParent(){this.parent?.remove(this);}
}
const scene={nodes:[],
 add(object){if(!this.nodes.includes(object))this.nodes.push(object);object.parent=this;},
 remove(object){this.nodes=this.nodes.filter(x=>x!==object);object.parent=null;}
};
const history=[],notices=[];
const context={
 window:{},scene,renderer:{},camera:null,actors:[],selected:null,
 currentProject:{name:'Mock map',kind:'world'},
 playing:false,simulating:false,paused:false,
 document:{visibilityState:'visible'},
 THREE:{Color,Vector3:Vec,BufferGeometry,BufferAttribute,Points,PointsMaterial,AdditiveBlending:1,NormalBlending:2},
 uid:()=> 'a_'+String(++uid).padStart(6,'0'),
 structuredClone,toast:m=>notices.push(String(m)),
 beginTransaction:()=>{},commitTransaction:label=>history.push(label)
};
vm.createContext(context);
const core=fs.readFileSync(path.join(__dirname,'../runtime/particle_studio_core_v11_224.js'),'utf8');
vm.runInContext(core,context,{filename:'particle_studio_core_v11_224.js'});
const studio=context.window.SWYRL_ENGINE_PARTICLES;
const first=studio.create('fire');
assert.equal(studio.list().length,1);
assert.equal(context.currentProject.particleStudio.schema,'swyrl-particle-studio-v1');
assert.equal(first.preset,'fire');
assert.equal(studio.update(first.id,{rate:70}).rate,70);
const transactions=history.length;
assert.equal(studio.update(first.id,{rate:900}),false);
assert.equal(history.length,transactions,'invalid values must not create Undo steps');
assert.equal(studio.list()[0].rate,70);
const sparks=studio.create('sparks');
assert.equal(sparks.mode,'burst');
assert.equal(studio.duplicate(first.id).name,'Flame copy');
assert.equal(studio.list().length,3);
assert.ok(studio.remove(sparks.id));
const canonical=JSON.parse(JSON.stringify(context.currentProject.particleStudio));
context.playing=true;
assert.equal(studio.create('magic'),false,'no edit during Play');
for(let i=0;i<40;i++)vm.runInContext('se223Frame(.05,0)',context);
const stats=studio.inspect();
assert.ok(stats.particles>0,'active emitter produces particles on native tick');
assert.ok(stats.particles<=576,'global cap');
assert.equal(scene.nodes.length,2,'one point cloud per enabled emitter');
context.playing=false;
vm.runInContext('se223State.preview=false;se223Frame(.05,0)',context);
assert.equal(studio.inspect().particles,0,'stopping clears live VFX');
assert.equal(studio.import({schema:'swyrl-particle-studio-v1',emitters:[{id:'x',name:'invalid'}]}),false);
assert.deepEqual(JSON.parse(JSON.stringify(context.currentProject.particleStudio)),canonical,'rejected import preserves VFX');
assert.equal(studio.import(canonical),true,'validated library round trips');
assert.equal(studio.list().length,2);
const firstCopy=studio.list()[0];
assert.equal(studio.trigger(firstCopy.id,20),20,'manual burst fires');
vm.runInContext('se223State.preview=true;se223Frame(.016,0)',context);
assert.ok(studio.inspect().particles>0,'manual burst survives first preview frame');
const previous=scene.nodes.slice();
context.currentProject={name:'Malformed imported project',kind:'world',particleStudio:{schema:'swyrl-particle-studio-v1',emitters:[{id:'x',name:'bad'}]}};
vm.runInContext('se223Frame(.016,0)',context);
assert.equal(studio.inspect().particles,0,'malformed project VFX must not break rendering');
context.currentProject={name:'Another project',kind:'world'};
vm.runInContext('se223Frame(.016,0)',context);
assert.equal(studio.list().length,0,'new project has no inherited emitters');
assert.equal(scene.nodes.length,0,'GPU points disposed');
assert.ok(previous.every(o=>o.geometry.disposed&&o.material.disposed),'resources released');
console.log(JSON.stringify({status:'PASS',smoke:'create/edit/validation/render/preview/import/project switch',
 presetCount:studio.presets().length,limits:stats.cap,transactions:history.length}));
