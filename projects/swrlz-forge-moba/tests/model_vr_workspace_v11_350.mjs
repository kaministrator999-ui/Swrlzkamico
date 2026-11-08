#!/usr/bin/env node
// Exercise the actual workspace dispatcher/gesture math, independently from
// the native transaction tests and browser's XR hardware-emulation coverage.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[2])throw Error('Usage: node tests/model_vr_workspace_v11_350.mjs /path/to/three-0.169.0.mjs');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const inputSource=fs.readFileSync(root+'/runtime/model_vr_input_profile_v11_350.js','utf8');
const workspaceSource=fs.readFileSync(root+'/runtime/model_vr_workspace_v11_350.js','utf8');
const clone=value=>JSON.parse(JSON.stringify(value));
const near=(actual,expected,label='number')=>assert.ok(Math.abs(actual-expected)<1e-8,`${label}: ${actual} != ${expected}`);
function fixture(){
 const scene=new THREE.Scene(),nativeRoot=new THREE.Group(),mesh=new THREE.Mesh(new THREE.BoxGeometry(.4,.5,.3),new THREE.MeshBasicMaterial());
 mesh.userData.atelierId='part';nativeRoot.add(mesh);scene.add(nativeRoot);
 let profile=null,cancelCount=0,ends=0,extrudeDepth=null,lastGroup=null;
 const record=hand=>{const grip=new THREE.Group(),target=new THREE.Group();scene.add(grip,target);return {index:hand==='left'?0:1,grip,target,held:false,blockGrip:false,blockTrigger:false,
  input:{handedness:hand,gamepad:{buttons:Array.from({length:6},()=>({value:0,pressed:false})),axes:[0,0,0,0]}},gripTracked:true,targetTracked:true,dot:{visible:true},hit:null};};
 const left=record('left'),right=record('right');left.grip.position.set(-.2,1.2,-.8);right.grip.position.set(.2,1.2,-.8);
 const tools={cancel:()=>{cancelCount++;return {ok:true}},selection:()=>({ids:['part'],primaryId:'part',pivot:[0,0,0]}),inspect:()=>({selectedIds:['part']}),
  select:()=>({ok:true}),beginGroup:()=>({ok:true}),updateGroup:delta=>{lastGroup=clone(delta);return {ok:true,changed:true}},
  endGroup:()=>{ends++;return {ok:true,changed:true}},projection:()=>({ready:true,root:nativeRoot,meshes:[{id:'part',name:'Part',mesh}]})};
 const surface={cancel:()=>({ok:true}),inspect:()=>({}),extrudeBegin:()=>({ok:true,id:'part',normal:[0,0,1],mesh}),
  extrudeUpdate:depth=>{extrudeDepth=depth;return {ok:true,changed:Math.abs(depth)>.003}},extrudeEnd:()=>({ok:true,changed:true})};
 const bridge={inspect:()=>({open:true,documentToken:1,revision:0,partCount:1,selectedId:'part',borrowed:true}),projection:tools.projection,cancel:()=>({ok:true})};
 const context=vm.createContext({THREE,ModelAtelier:{xrBridge:bridge,vrTools:tools,vrSurface:surface},
  window:{SWYRL_VR_CONTROLS:{currentProfile:()=>profile},dispatchEvent:()=>{}},document:{getElementById:()=>null},
  CustomEvent:class{constructor(name,options){this.type=name;this.detail=options?.detail}},performance:{now:()=>1000},
  renderer:{xr:{isPresenting:true}},setTimeout,clearTimeout,console});
 vm.runInContext(inputSource+'\n'+workspaceSource+`\nthis.api={state:se340XR,input:se350Input,bindings:SE350_MODEL_VR_BINDINGS,
  begin:se340BeginGesture,beginView:se350BeginView,update:se340UpdateGesture,finish:se340FinishGesture,cancel:se340CancelGesture,
  pair:se350Pair,navigate:se350Navigate,dispatch:se350Dispatch};`,context);
 context.fakeHit=()=>({id:'part',name:'Part',mesh,point:mesh.getWorldPosition(new THREE.Vector3())});
 vm.runInContext('se340Hit=globalThis.fakeHit;',context);
 const api=context.api,s=api.state;s.session={visibilityState:'visible'};s.scene=scene;s.controllers=[left,right];s.anchor={position:new THREE.Vector3(0,1.6,0),forward:new THREE.Vector3(0,0,-1)};
 s.ui={closeWheel:()=>{},inspect:()=>({})};s.zoom=1;s.yaw=.2;s.pitch=.1;
 s.inputSample={held:{},buttons:{},axes:{},thresholds:{precisionMultiplier:.18,snapDegrees:30,turnSensitivity:1,brushSensitivity:1}};
 const thresholds=s.inputSample.thresholds;
 const sample=time=>{s.inputSample=api.input.sample({time,context:'model',sources:[{input:left.input,tracked:true,record:left},{input:right.input,tracked:true,record:right}]});return s.inputSample;};
 const hold=(hand,index,value)=>{const r=hand==='left'?left:right;r.input.gamepad.buttons[index]={value,pressed:!!value};};
 return {api,s,scene,nativeRoot,mesh,left,right,tools,surface,thresholds,sample,hold,setProfile:value=>{profile=value},
  lastGroup:()=>lastGroup,depth:()=>extrudeDepth,counts:()=>({cancelCount,ends})};
}
let groups=0;
{
 // Presentation cancellation restores the complete start pose even after a
 // zoom shortcut and physical hand movement have both changed the preview.
 const f=fixture(),{api,s,left}=f,original={anchor:s.anchor.position.clone(),zoom:s.zoom,yaw:s.yaw,pitch:s.pitch};
 api.beginView(left);left.grip.position.x+=.3;api.update();
 const held={pan:{source:{record:left}}};
 api.navigate({held,axes:{orbit:{x:0,y:-.8}},thresholds:f.thresholds},.05);
 assert.notEqual(s.zoom,original.zoom);api.cancel('B');
 assert.ok(s.anchor.position.distanceTo(original.anchor)<1e-9);near(s.zoom,original.zoom,'cancel zoom');near(s.yaw,original.yaw);near(s.pitch,original.pitch);
 assert.equal(s.gesture,null);assert.equal(f.counts().ends,0,'Presentation must never commit geometry');groups++;
}
{
 // The final two-hand presentation movement can arrive in the same frame as
 // release. Sampling may no longer report held controls, but poses are valid.
 const f=fixture(),{api,s,left,right}=f;api.beginView(left);
 s.inputSample.held={pan:{source:{record:left}},grab:{source:{record:right}}};api.update();
 const baseline=s.anchor.position.clone();left.grip.position.x-=.1;right.grip.position.x+=.1;left.grip.position.y+=.12;right.grip.position.y+=.12;
 s.inputSample.held={};assert.equal(api.finish(left),true);near(s.zoom,1.5,'final-release view scale');near(s.anchor.position.y,baseline.y+.12,'final-release view center');
 assert.equal(s.gesture,null);assert.equal(f.counts().ends,0);groups++;
}
{
 // Profiles may put the two hand roles on triggers instead of grips. Pair
 // activation follows resolved actions, never hard-coded physical LG/RG.
 const f=fixture(),bindings=clone(f.api.bindings);
 bindings.model=bindings.model.filter(row=>!['pan','grab','select','multiselect'].includes(row[0]));
 bindings.model.push(['pan','hold:LT','Left assist'],['grab','hold:RT','Right grab']);
 f.setProfile({profileId:'custom-trigger-pair',profileName:'Trigger pair',bindings,thresholds:{}});
 f.sample(0);f.hold('left',0,1);f.hold('right',0,1);const sample=f.sample(20);
 assert.ok(sample.held.pan&&sample.held.grab);assert.equal(f.left.held,false);assert.equal(f.right.held,false);
 const pair=f.api.pair();assert.ok(pair,'Resolved custom held actions must form a pair');assert.equal(pair.left,f.left);assert.equal(pair.right,f.right);
 f.s.mode='two-hand';assert.equal(f.api.begin(f.right),true);assert.equal(f.s.gesture.kind,'two-hand');groups++;
}
{
 // Inspect's workbench gesture starts on the assist hand, but after both
 // hands join it, releasing the other hand must also finish the gesture.
 const f=fixture(),{api,s,left,right}=f;s.mode='inspect';api.beginView(left);
 s.inputSample.held={pan:{source:{record:left}},grab:{source:{record:right}}};api.update();
 left.grip.position.x-=.05;right.grip.position.x+=.05;left.grip.position.y+=.1;right.grip.position.y+=.1;
 s.inputSample.held={pan:{source:{record:left}}};
 assert.equal(api.finish(right),true,'Either member of a paired presentation must finish it');
 near(s.zoom,1.25,'right-release presentation scale');assert.equal(s.gesture,null);
 const position=s.anchor.position.clone();left.grip.position.y+=.4;api.update();
 assert.ok(s.anchor.position.distanceTo(position)<1e-9,'Remaining held hand cannot keep moving a finished pair');
 assert.equal(f.counts().ends,0);groups++;
}
{
 // Grip releases belong to grip-owned transforms. They must never consume
 // an unfinished stroke/outline/lasso while its trigger is still held.
 for(const kind of ['sculpt','draw','lasso']){
  const f=fixture(),{api,s,right}=f,gesture={kind,mode:kind,record:right,id:'part',points:[]};s.mode=kind;s.gesture=gesture;
  const sample={events:[{action:'grab',phase:'end',source:{record:right}}],held:{stroke:{source:{record:right}}},axes:{},
   buttons:{RT:{down:true,physical:true},RG:{down:false,physical:false}},thresholds:f.thresholds};s.inputSample=sample;
  api.dispatch(sample);assert.equal(s.gesture,gesture,`Grip release consumed trigger-owned ${kind}`);assert.equal(f.counts().ends,0);
 }
 groups++;
}
{
 // A release must use both tracked final hand poses, rather than committing
 // the previous frame or treating a released grip as lost tracking.
 const f=fixture(),{api,s,left,right}=f;s.mode='two-hand';s.inputSample.held={pan:{source:{record:left}},grab:{source:{record:right}}};
 assert.equal(api.begin(right),true);left.grip.position.x-=.1;right.grip.position.x+=.1;left.grip.position.z-=.2;right.grip.position.z-=.2;
 s.inputSample.held={};assert.equal(api.finish(left),true);const delta=f.lastGroup();near(delta.scale,1.5);near(delta.translation[2],-.2);assert.equal(f.counts().ends,1);groups++;
}
{
 // Profile-owned precision gain must reach physical model motion.
 const f=fixture(),{api,s,right}=f;s.mode='move';s.precision=true;s.inputSample.thresholds.precisionMultiplier=.18;
 assert.equal(api.begin(right),true);right.grip.position.x+=.3;api.update();near(f.lastGroup().translation[0],.054,'profile precision movement');groups++;
}
{
 // Feed the real resolver's simultaneous B + grip-release result through
 // the actual dispatcher: cancel wins before a release can commit.
 const f=fixture(),{api,s,right}=f;s.mode='move';f.sample(0);f.hold('right',1,1);api.dispatch(f.sample(10));
 assert.equal(s.gesture.kind,'group');right.grip.position.x+=.2;api.update();
 f.hold('right',1,0);f.hold('right',5,1);const sample=f.sample(20);assert.equal(sample.cancel,true);
 api.dispatch(sample);assert.equal(s.gesture,null);assert.equal(f.counts().ends,0,'Same-frame cancel/release must never commit');groups++;
}
{
 // Snap angle is configurable. A 38-degree wrist turn snaps to 30 degrees
 // under this profile; a fixed 15-degree implementation would produce45.
 const f=fixture(),{api,s,right}=f;s.mode='rotate';s.snap=true;s.inputSample.thresholds.snapDegrees=30;
 assert.equal(api.begin(right),true);right.grip.quaternion.setFromAxisAngle(new THREE.Vector3(0,0,1),38*Math.PI/180);api.update();
 const q=new THREE.Quaternion(...f.lastGroup().rotation),angle=new THREE.Euler().setFromQuaternion(q).z;near(angle,Math.PI/6,'profile snap angle');groups++;
}
{
 // Extrusion is a signed mesh-local normal displacement, not hand travel
 // length and not root-local motion. Include unrelated tangential movement.
 const f=fixture(),{api,s,right,mesh,nativeRoot}=f;
 nativeRoot.position.set(.4,.7,-.3);nativeRoot.rotation.set(.3,-.4,.1);nativeRoot.scale.set(1.2,.7,1.4);
 mesh.rotation.set(.2,Math.PI/2,-.1);mesh.scale.set(.8,1.3,.6);f.scene.updateMatrixWorld(true);
 s.mode='extrude';const start=right.grip.position.clone();assert.equal(api.begin(right),true);
 const worldDelta=local=>new THREE.Vector3(...local).applyMatrix4(mesh.matrixWorld).sub(new THREE.Vector3().applyMatrix4(mesh.matrixWorld));
 right.grip.position.copy(start).add(worldDelta([.4,.2,.3]));api.update();near(f.depth(),.3,'normal pull');
 right.grip.position.copy(start).add(worldDelta([-.2,.3,-.2]));api.update();near(f.depth(),-.2,'signed reverse pull');
 right.grip.position.copy(start).add(worldDelta([.4,-.2,0]));api.update();near(f.depth(),0,'tangent-only movement');groups++;
}
console.log('MODEL_VR_WORKSPACE_V11_350_PASS',JSON.stringify({groups,three:THREE.REVISION,actualWorkspaceSource:true,
 presentation:'immutable cancel; same-frame release',profiles:'remapped pair; precision gain; snap angle',extrude:'signed mesh-local normal'}));
