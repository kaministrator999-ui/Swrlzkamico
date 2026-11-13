// Regression: phone orbit follows touch drag; mouse orbit, tap selection and limits remain unchanged.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';

assert.ok(process.argv[2],'Pass the generated §E index.html to test the SHIPPED implementation');
const full=fs.readFileSync(path.resolve(process.argv[2]),'utf8');
const atelierStart=full.indexOf('const ModelAtelier=(()=>{');
assert.ok(atelierStart>=0,'Missing assembled Model Atelier');
const runtime=full.slice(atelierStart);
function nativeFunction(name){
  const start=runtime.indexOf('function '+name+'(');
  assert.ok(start>=0,'Missing native '+name);
  const open=runtime.indexOf('{',start);
  let depth=0;
  for(let i=open;i<runtime.length;i++){
    if(runtime[i]==='{')depth++;
    if(runtime[i]==='}'&&!--depth)return runtime.slice(start,i+1);
  }
  throw Error('Unterminated '+name);
}
const source=Object.freeze({parts:[{id:'part-1'}]});
const initial=JSON.stringify(source);
const calls={camera:0,select:[],capture:[]};
const context={
  THREE:{MathUtils:{clamp:(v,lo,hi)=>Math.max(lo,Math.min(hi,v))}},
  pressed:null,orbit:{yaw:.3,pitch:.19,distance:9},
  renderer:{domElement:{setPointerCapture:id=>calls.capture.push(id),getBoundingClientRect:()=>({left:0,top:0,width:400,height:300})}},
  camera:{},modelRoot:{children:[{isMesh:true,userData:{atelierId:'part-1'}}]},
  raycaster:{setFromCamera:()=>{},intersectObjects:()=>[{object:{userData:{atelierId:'part-1'}}}]},
  mouse:{set:()=>{}},select:id=>calls.select.push(id),
  cameraUpdate:()=>{calls.camera++;},
};
vm.createContext(context);
vm.runInContext(['point','pointerDown','pointerMove','pointerUp'].map(nativeFunction).join('\n'),context);
function e(pointerType,x,y,id=7){return {pointerType,pointerId:id,button:0,clientX:x,clientY:y};}
function reset(){context.orbit.yaw=.3;context.orbit.pitch=.19;context.pressed=null;}
const near=(actual,expected)=>assert.ok(Math.abs(actual-expected)<1e-9,String(actual)+' != '+expected);

// A swipe right moves the camera to the right; a swipe up raises it.
reset();
vm.runInContext('pointerDown(event)',Object.assign(context,{event:e('touch',100,100)}));
vm.runInContext('pointerMove(event)',Object.assign(context,{event:e('touch',140,60)}));
near(context.orbit.yaw,.3+40*.008);
near(context.orbit.pitch,.19+40*.006);
assert.equal(context.pressed.moved,true);
vm.runInContext('pointerUp(event)',Object.assign(context,{event:e('touch',140,60)}));
assert.equal(calls.select.length,0,'Dragging must not tap/select a mesh');

// The mouse retains its existing orbit convention; VR controller paths aren't modified.
reset();
vm.runInContext('pointerDown(event)',Object.assign(context,{event:e('mouse',100,100)}));
vm.runInContext('pointerMove(event)',Object.assign(context,{event:e('mouse',140,60)}));
near(context.orbit.yaw,.3-40*.008);
near(context.orbit.pitch,.19-40*.006);
vm.runInContext('pointerUp(event)',Object.assign(context,{event:e('mouse',140,60)}));

// A stationary finger remains a tap instead of a camera movement.
reset();
const previous=calls.camera;
vm.runInContext('pointerDown(event)',Object.assign(context,{event:e('touch',100,100)}));
vm.runInContext('pointerMove(event)',Object.assign(context,{event:e('touch',102,102)}));
assert.equal(calls.camera,previous);
vm.runInContext('pointerUp(event)',Object.assign(context,{event:e('touch',102,102)}));
assert.deepEqual(calls.select,['part-1']);

// Guard the existing pitch clamp in either direction.
reset();
vm.runInContext('pointerDown(event)',Object.assign(context,{event:e('touch',100,100)}));
vm.runInContext('pointerMove(event)',Object.assign(context,{event:e('touch',100,-1000)}));
near(context.orbit.pitch,Math.PI/2-.001);
vm.runInContext('pointerMove(event)',Object.assign(context,{event:e('touch',100,1000)}));
near(context.orbit.pitch,-Math.PI/2+.001);
assert.equal(JSON.stringify(source),initial,'Orbit cannot edit saved geometry');
console.log('MODEL_ATELIER_MOBILE_ORBIT_V11_432_PASS');
