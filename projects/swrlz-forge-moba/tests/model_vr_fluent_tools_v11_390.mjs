#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[2])throw Error('Pass Three.js r169 module path.');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const source=fs.readFileSync(path.join(ROOT,'runtime/model_vr_fluent_tools_v11_390.js'),'utf8');
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-10,`${a} != ${b}`);
let profile={dominantHand:'right',bindings:{model:[['select','tap:RT','']]}};
const left={input:{handedness:'left'}},right={input:{handedness:'right'}};
const s={gesture:null,inputSample:{buttons:{},events:[]},mode:'inspect',page:'tools'};
let cancelled=0,baseTrigger=0,disposed=0,baseActions=0;const depths=[];
const ctx=vm.createContext({THREE,ModelAtelier:{vrCreate:{cancel(){cancelled++;}}},se340XR:s,
 window:{SWYRL_VR_CONTROLS:{currentProfile:()=>profile}},
 se340ModelXRAction(){baseActions++;},se340Trigger(){baseTrigger++;},se340CancelGesture(){const had=!!s.gesture;s.gesture=null;return had;},
 se350Dispatch(){},se350Navigate(){},se340FinishGesture(){},se340ModelXRInspect:()=>({}),
 se350Record:side=>side==='left'?left:right,se350Surface:()=>({extrudeUpdate(depth){depths.push(depth);return {ok:true};}}),
 se340Hit:()=>({ui:true}),se340VisibleSession:()=>true,se340SyncUI(){},se340Publish(){},se340Notice(){}});
vm.runInContext(source+`\nthis.api={pair:se390PairCandidate,extrude:se390UpdateExtrude,record:se390SelectRecord,cancel:se390CancelCreation};`,ctx);
let groups=0;
{
 const g={pair:{mid:new THREE.Vector3(0,1,0),span:new THREE.Vector3(1,0,0)},rootInverse:new THREE.Matrix4().makeScale(.5,2,3),rootQuaternion:new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),.3)};
 const mid=new THREE.Vector3(.2,1.1,0),span=new THREE.Vector3(1.1,.2,0);
 const coarse=ctx.api.pair(g,mid,span,1),fine=ctx.api.pair(g,mid,span,.12);
 assert.deepEqual(JSON.parse(JSON.stringify(fine)),JSON.parse(JSON.stringify(coarse)));
 const next=ctx.api.pair(g,mid.clone().add(new THREE.Vector3(.2,0,0)),span.clone().multiplyScalar(1.1),.12);
 close(next.translation[0]-fine.translation[0],.2*.5*.12);close(next.scale/fine.scale,Math.pow(1.1,.12));
 const normal=ctx.api.pair(g,mid.clone().add(new THREE.Vector3(.2,0,0)),span.clone().multiplyScalar(1.1),1);
 assert.deepEqual(JSON.parse(JSON.stringify(normal)),JSON.parse(JSON.stringify(next)));groups++;
}
{
 const g={hand:{position:new THREE.Vector3()},rootInverse:new THREE.Matrix4().makeScale(.5,2,3),normal:new THREE.Vector3(0,0,1)};
 const pose={position:new THREE.Vector3(.4,.2,.3)};ctx.api.extrude(g,pose,1);close(depths.at(-1),.9);
 ctx.api.extrude(g,pose,.12);close(depths.at(-1),.9);
 pose.position.z+=.1;ctx.api.extrude(g,pose,.12);close(depths.at(-1),.936);
 ctx.api.extrude(g,pose,1);close(depths.at(-1),.936);groups++;
}
{
 assert.equal(ctx.api.record(),right);
 profile={dominantHand:'right',bindings:{model:[['select','tap:LT','']]}};assert.equal(ctx.api.record(),left);
 profile={dominantHand:'left',bindings:{model:[['select','tap:RT','']]}};assert.equal(ctx.api.record(),right);groups++;
}
{
 const resource=()=>({dispose(){disposed++;}});
 s.se390Creation={ghost:{removeFromParent(){disposed++;}},geometry:resource(),edges:resource(),material:resource(),edgeMaterial:resource(),draft:{}};
 assert.equal(ctx.api.cancel(),true);assert.equal(s.mode,'inspect');assert.equal(s.page,'create');assert.equal(disposed,5);assert.equal(cancelled,1);
 assert.equal(ctx.api.cancel(),false);assert.equal(disposed,5);assert.equal(cancelled,1);groups++;
}
{
 s.se372Sweep={record:left};ctx.se340CancelGesture('Canceled');assert.equal(s.se372Sweep,null);
 const inactive=ctx.se340ModelXRInspect();assert.equal(inactive.creation.active,false);assert.equal(inactive.creation.position,null);groups++;
}
{
 s.inputSample={buttons:{RT:{source:{record:right}}},events:[]};
 ctx.se350Dispatch({cancel:false,events:[{action:'duplicate',phase:'tap',keys:['X','RT'],source:{record:left}}],buttons:s.inputSample.buttons});
 assert.equal(baseTrigger,1,'duplicate chord over a menu must operate the actual pointer UI');groups++;
}
{
 s.session={};s.scene={};s.mode='create';s.se390Creation={draft:{}};
 assert.equal(ctx.se340ModelXRAction('undo'),true);assert.equal(s.se390Creation,null);
 assert.equal(baseActions,0,'Undo must cancel an uncommitted placement before native history');groups++;
}
console.log('MODEL_VR_FLUENT_TOOLS_V11_390_PASS',JSON.stringify({groups,three:THREE.REVISION,pairPrecision:'jump-free',extrudePrecision:'jump-free',placement:'mapped primary controller',disposal:'exactly once'}));
