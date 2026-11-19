#!/usr/bin/env node
// Compiled v11.520 WebXR source; Three.js r169 real vector/quaternion/menu math.
import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import path from 'node:path';
import {pathToFileURL} from 'node:url';
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION,'169');
const html=fs.readFileSync(path.resolve(process.argv[3]),'utf8');
const snippet=(a,b)=>{
 const i=html.indexOf(a),j=html.indexOf(b,i);
 assert(i>0&&j>i,'Compiled source section missing: '+a);
 return html.slice(i,j+b.length);
};
const trigger=snippet('/* SE512_MODEL_VR_TRIGGER_GIZMO_START','/* SE512_MODEL_VR_TRIGGER_GIZMO_END */');
const runtime=snippet('/* SE520_VR_INTERACTION_REPAIR_START','/* SE520_VR_INTERACTION_REPAIR_END */');
const record={input:{handedness:'right'},targetTracked:true,gripTracked:true};
const pose={position:new THREE.Vector3(.2,1.3,-.6),quaternion:new THREE.Quaternion()};
const root=new THREE.Group(),scene=new THREE.Scene(),menu=new THREE.Group();
scene.add(root,menu);menu.position.set(-.6,1.35,-1);
let uiPicks=0,updates=0,finishes=0,cancels=0,dispatches=[];
const state={mode:'move',gesture:null,controllers:[record],session:{},scene,
 ui:{root:menu},lastViewer:{position:new THREE.Vector3(0,1.5,0)},
 se372MenuBase:{position:menu.position.clone(),quaternion:menu.quaternion.clone()},
 se390Creation:null,se372Sweep:null,paletteVisible:true};
let gizmo=null,hit={id:'sphere',name:'Sphere'};
const tools={selection:()=>({ids:['sphere'],primaryId:'sphere'}),
 beginGroup:(id,mode)=>({ok:true,mode}),cancel:()=>{cancels++;return {ok:true};},
 updateGroup:()=>{updates++;return {ok:true,changed:true};}};
const ctx=vm.createContext({THREE,window:{},se340XR:state,se340VisibleSession:()=>true,
 se374GizmoContact:()=>gizmo,se340Hit:()=>{uiPicks++;return hit;},
 se350Tools:()=>tools,se340GripPose:()=>({position:pose.position.clone(),quaternion:pose.quaternion.clone()}),
 se350Root:()=>root,se390BeginPose:(g,p)=>{g.se390Pose={position:p.position.clone(),positionActive:false};},
 se372GuideStart:()=>{},se340Notice:()=>{},se340Pulse:()=>{},
 se390NoticeError:()=>{},se340FinishGesture:()=>{finishes++;state.gesture=null;return true;},
 se340CancelGesture:()=>{cancels++;state.gesture=null;return true;},
 se350Dispatch:s=>{dispatches.push(s.events.map(e=>e.action));},
 se340UpdateGesture:()=>{updates++;},se372Frame:()=>{},
 se372MenuOrbit:()=>{},se340Cleanup:()=>{},se340XRSource:true});
vm.runInContext(trigger,ctx);vm.runInContext(runtime,ctx);
const frame=(down,events=[],extra={})=>ctx.se350Dispatch({
 buttons:{RT:{physical:down},LT:{physical:false}},events,...extra});
frame(true,[{action:'select',keys:['RT']}]);
assert.equal(state.gesture?.se520DirectTrigger,true,'selected mesh starts Trigger-held direct drag');
assert.equal(state.gesture?.se520Activated,false);
assert.deepEqual(dispatches.at(-1),[],'initial select tap is consumed by active mesh drag');
vm.runInContext('se340UpdateGesture()',ctx);
pose.position.x+=.005;vm.runInContext('se340UpdateGesture()',ctx);
assert.equal(updates,0,'tiny tracking jitter makes no native translation preview');
frame(false,[{action:'select',keys:['RT']}]);
assert.equal(finishes,0,'short tap never commits transform');
assert.equal(cancels,1,'short tap cancels pending native transaction');
pose.position.set(.2,1.3,-.6);
frame(true,[{action:'select',keys:['RT']}]);
pose.position.x+=.032;vm.runInContext('se340UpdateGesture()',ctx);
assert.equal(state.gesture.se520Activated,true,'held physical movement activates transform');
assert.equal(updates,0,'activation rebases without sudden model jump');
pose.position.x+=.025;vm.runInContext('se340UpdateGesture()',ctx);
assert.equal(updates,1,'subsequent held frame streams model preview');
frame(false,[{action:'select',keys:['RT']}]);
assert.equal(finishes,1,'release applies one native group gesture');
gizmo={gizmo:true,axis:'y'};
frame(true);assert.equal(state.gesture.axis,'y');assert.equal(state.gesture.se520DirectTrigger,false,
 'native handle still beats direct-mesh selection');
frame(false);
hit={ui:true,action:'projects'};gizmo=null;
frame(true,[{action:'select',keys:['RT']}]);
assert.equal(state.gesture,null,'native VR menu ray is never claimed as model drag');
frame(false);
hit={id:'other',name:'Other'};
frame(true);assert.equal(state.gesture,null,'unselected mesh tap is not a drag');frame(false);
hit={id:'sphere',name:'Sphere'};
for(let i=0;i<8;i++){
 state.lastViewer.position.set(i*.14,1.4+(i%2)*.12,i*.09);
 state.gesture={kind:'menu'};
 vm.runInContext('se372Frame(se340XR)',ctx);
 const toViewer=state.lastViewer.position.clone().sub(menu.position).normalize();
 const front=menu.getWorldDirection(new THREE.Vector3());
 assert(front.dot(toViewer)>.995,'world menu must face headset even during Grip-based placement');
 assert(menu.position.distanceToSquared(new THREE.Vector3(-.6,1.35,-1))<1e-12,
  'menu remains anchored at its original world location');
}
console.log('SE520_XR_TRIGGER_MENU_PASS',JSON.stringify({
 tapNoMotion:true,heldContinuousPreview:true,releaseCommitsOnce:true,
 gizmoPriority:true,menuRayPriority:true,unselectedTapRetained:true,
 headsetFacingPerFrame:true,menuAnchorPreserved:true}));
