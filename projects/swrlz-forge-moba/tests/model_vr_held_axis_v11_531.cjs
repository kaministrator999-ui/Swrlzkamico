#!/usr/bin/env node
'use strict';
// Executes the shipped v11.531 XR wrapper with tracked controller vectors.
// Tests reversible held-axis motion and suppression of duplicate Trigger events.
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const src=fs.readFileSync(path.resolve(__dirname,'../runtime/model_vr_quest_interactions_v11_531.js'),'utf8');
class V {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;this.isVector3=true;}
 clone(){return new V(this.x,this.y,this.z);}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this;}
 addScaledVector(v,k){this.x+=v.x*k;this.y+=v.y*k;this.z+=v.z*k;return this;}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this;}
 multiplyScalar(k){this.x*=k;this.y*=k;this.z*=k;return this;}
 dot(v){return this.x*v.x+this.y*v.y+this.z*v.z;}
 lengthSq(){return this.dot(this);}
 normalize(){return this.multiplyScalar(1/Math.sqrt(this.lengthSq()));}
 applyQuaternion(){return this;}
 applyMatrix4(){return this;}
 setComponent(i,v){this[['x','y','z'][i]]=v;return this;}
 toArray(){return [this.x,this.y,this.z];}
 copy(v){this.x=v.x;this.y=v.y;this.z=v.z;return this;}
 distanceToSquared(v){return this.clone().sub(v).lengthSq();}
 lerp(v,a){this.x+=(v.x-this.x)*a;this.y+=(v.y-this.y)*a;this.z+=(v.z-this.z)*a;return this;}
}
const updates=[],dispatched=[];
const context={
 THREE:{Vector3:V,Quaternion:class{},MathUtils:{clamp:(n,a,b)=>Math.max(a,Math.min(b,n))}},
 se340XR:{snap:false,mode:'move',gesture:null,controllers:[],paletteVisible:true},
 se372MenuOrbit(){},se340CreateModelVRUI(){return {root:{getObjectByName(){return null;},
  updateWorldMatrix(){}},inspect(){return {}},update(){},tick(){},press(){}};},
 se390UpdatePose(){throw Error('Captured axis must not call the obsolete pose implementation.');},
 se350Dispatch(sample){dispatched.push(sample);return sample;},
 se512GizmoInput:{inspect:()=>({captured:[{key:'RT',mode:'move',axis:'x'}]})},
 se350Record(){return null;},
 se374GizmoContact(){return null;},
 se350Tools:()=>({updateGroup(payload){updates.push(payload);return {ok:true};}}),
 se372Constrain(){},se372GuideUpdate(){},
 se340CancelGesture(msg){throw Error('Unexpected native gesture cancellation: '+msg);},
 window:{}
};
vm.createContext(context);
vm.runInContext(src,context,{filename:'model_vr_quest_interactions_v11_531.js'});
assert(context.window.SWYRL_ENGINE_QUEST_INTERACTIONS_531,'Expected diagnostics');
const sample={events:[{action:'select',keys:['RT']},{action:'tool-wheel',keys:['RT']},
 {action:'cancel',keys:['B']}],buttons:{RT:{physical:true}}};
context.se350Dispatch(sample);
assert.deepEqual(dispatched.at(-1).events.map(e=>e.action),['cancel'],
 'Held gizmo capture must prevent repeated Trigger events while preserving B cancel');
for(const [axis,positions,expect] of [
 ['x',[[0,0,0],[.25,0,0],[.10,0,0],[.10,1,0]],[.10,0,0]],
 ['y',[[0,0,0],[0,.30,0],[0,.11,0],[2,.11,0]],[0,.11,0]],
 ['z',[[0,0,0],[0,0,.23],[0,0,-.04],[0,2,-.04]],[0,0,-.04]]
]){
 updates.length=0;
 const g={se512Trigger:true,kind:'group',mode:'move',axis,record:{gripTracked:true,targetTracked:true},
  rootInverse:{},rootQuaternion:{}};
 for(const [x,y,z] of positions)context.se390UpdatePose(g,{position:new V(x,y,z)},1);
 const result=updates.at(-1).translation;
 for(let i=0;i<3;i++)assert(Math.abs(result[i]-expect[i])<1e-8,
  axis+' axis drift: '+result+' expected '+expect);
 assert.equal(g.se531Axis.frames,positions.length,'Every held frame must update native preview.');
}
console.log('SE531_HELD_AXIS_DYNAMIC_TEST_PASS');
