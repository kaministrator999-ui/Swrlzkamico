#!/usr/bin/env node
/* §E v11.514 — tests against actual Three.js 169, scoped native XR hooks.
   Verifies menu ownership, skeletal pose, Trigger/Grip, cancel, undo and
   authored GPU skin weights. No standalone UI or synthetic menu dispatcher. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[3])throw Error('Expected current generated §E HTML');
const compiled=fs.readFileSync(path.resolve(process.argv[3]),'utf8');
const a=compiled.indexOf('(function se518NativeRigClosure(){'),b=compiled.indexOf('/* SE514_NATIVE_XR_RIG_END',a);
assert(a>0&&b>a,'Missing new native rig scope adapter');
assert(a>0&&b>a);
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION,'169');
const rig={schema:'swyrl-cloth-skin-v1',targetPartId:'generic',bones:[
 {id:'root',label:'Root',rest:[0,0,0],parent:null},
 {id:'mid',label:'Middle',rest:[0,1,0],parent:'root'},
 {id:'tip',label:'Tip',rest:[0,2,0],parent:'mid'}
],pose:{},timeline:[]};
const rootGroup=new THREE.Group(),boneRoot=new THREE.Bone(),boneMid=new THREE.Bone(),boneTip=new THREE.Bone();
boneRoot.name='root';boneMid.name='mid';boneTip.name='tip';
boneMid.position.y=1;boneTip.position.y=1;
rootGroup.add(boneRoot);boneRoot.add(boneMid);boneMid.add(boneTip);
rootGroup.updateWorldMatrix(true,true);
const bones={root:boneRoot,mid:boneMid,tip:boneTip},skeleton=new THREE.Skeleton([boneRoot,boneMid,boneTip]);
skeleton.calculateInverses();
const geom=new THREE.BufferGeometry();
geom.setAttribute('position',new THREE.Float32BufferAttribute([0,0,0,1,0,0,0,1,0],3));
geom.setIndex([0,1,2]);geom.computeVertexNormals();
geom.setAttribute('skinIndex',new THREE.Uint16BufferAttribute([0,0,0,0,0,0,0,0,0,0,0,0],4));
geom.setAttribute('skinWeight',new THREE.Float32BufferAttribute([1,0,0,0,1,0,0,0,1,0,0,0],4));
const mesh=new THREE.SkinnedMesh(geom,new THREE.MeshBasicMaterial());mesh.userData.atelierId='generic';
mesh.bind(skeleton,mesh.matrixWorld.clone());rootGroup.add(mesh);
rootGroup.updateWorldMatrix(true,true);
const part={id:'generic',topologyMesh:{positions:[0,0,0,1,0,0,0,1,0]}};
const project={parts:[part]};
const viewer={scene:null,session:{visibilityState:'visible'},mode:'inspect',page:'tools',frameCount:0,
 controllers:[],gesture:null};
let joint='root',remembered=0,dirty=0,feedback=[],ui=0,paintedClicks=0,stageCalls=0,originalGestureCalls=0;
const nativeUndo=[],poseHistory=[];
const record={input:{handedness:'right'},targetTracked:true,gripTracked:true,
 pose:{position:new THREE.Vector3(0,0,0),quaternion:new THREE.Quaternion()}};
viewer.controllers=[record];
record.ray=new THREE.Raycaster(new THREE.Vector3(0,1,-1),new THREE.Vector3(0,0,1));
record.ray.near=.01;record.ray.far=3;
let menuHit=false,modelHit={id:'generic',point:new THREE.Vector3(.01,.02,0)};
const sandbox={
 THREE,window:{},structuredClone,console,
 se340XR:viewer,modelRoot:rootGroup,se220Bones:bones,se220Skeleton:skeleton,
 se220Joint:joint,se220PoseHistory:poseHistory,
 se220RigAvailable:()=>true,se220RigValidate:()=>true,se220Rig:()=>rig,
 se220R:()=>null,se220RigJointUI:()=>{},se220RigRemember:()=>{remembered++;poseHistory.push(JSON.stringify(rig.pose));},
 se220RigTouched:()=>{dirty++;},
 se220RigPose:(pose)=>{
  for(const spec of rig.bones)bones[spec.id].rotation.set(...(pose?.[spec.id]||[0,0,0]));
  rootGroup.updateWorldMatrix(true,true);skeleton.update();
 },
 se220Playing:false,se340VisibleSession:()=>true,
 se340MakeStage:()=>{stageCalls++;viewer.scene=new THREE.Scene();return true;},
 se340Cast:r=>r.ray,se340Hit:()=>menuHit?{ui:true,action:'rig'}:modelHit,
 se340Notice:(text,bad)=>feedback.push([text,!!bad]),se340Publish:()=>{},
 se340SyncUI:()=>{ui++;},se340Pulse:()=>{},
 se340GripPose:r=>({position:r.pose.position.clone(),quaternion:r.pose.quaternion.clone()}),
 se340Trigger:()=>{paintedClicks++;return true;},
 se340BeginGesture:()=>{originalGestureCalls++;return true;},
 se340UpdateGesture:()=>{},
 se340FinishGesture:()=>{},
 se340CancelGesture:()=>{viewer.gesture=null;return true;},
 se340ModelXRAction:()=>false,
 se350Dispatch:s=>s,se350Record:hand=>hand==='right'?record:null,
 se340Cleanup:()=>{viewer.session=null;viewer.scene=null;viewer.gesture=null;return true;},
 partById:id=>project.parts.find(p=>p.id===id),
 checkpoint:()=>nativeUndo.push(JSON.stringify(project.parts)),
 undo:nativeUndo
};
sandbox.window.SWYRL_ENGINE_MODEL_RIG_ACCESS_518={
 available:()=>sandbox.se220RigAvailable(),rig:sandbox.se220Rig,
 get bones(){return sandbox.se220Bones;},
 get skeleton(){return sandbox.se220Skeleton;},
 get root(){return sandbox.modelRoot;},
 get joint(){return sandbox.se220Joint;},
 set joint(value){sandbox.se220Joint=value;},
 get playing(){return sandbox.se220Playing;},
 set playing(value){sandbox.se220Playing=value;},
 get poseHistory(){return sandbox.se220PoseHistory;},
 element:sandbox.se220R,jointUI:sandbox.se220RigJointUI,pose:sandbox.se220RigPose,
 remember:sandbox.se220RigRemember,touched:sandbox.se220RigTouched,
 validate:sandbox.se220RigValidate,part:sandbox.partById,checkpoint:sandbox.checkpoint
};
const ctx=vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(root,'runtime/model_rig_skin_math_v11_513.js'),'utf8'),ctx);
vm.runInContext(fs.readFileSync(path.join(root,'runtime/model_rig_precision_v11_516.js'),'utf8'),ctx);
vm.runInContext(compiled.slice(a,b+'/* SE514_NATIVE_XR_RIG_END */'.length),ctx);
const api=sandbox.window.SWYRL_ENGINE_IMMERSIVE_RIG_514;
assert(api?.action&&api?.beforeDispatch&&api?.undoRig&&api?.inspect);
sandbox.se220RigAvailable=()=>false;
assert.equal(api.valid(),false,'ordinary unrigged sphere must enter VR without missing rig globals');
assert.equal(api.uiState().rigAvailable,false,'unrigged model stays in regular Model Studio');
sandbox.se220RigAvailable=()=>true;
vm.runInContext('se340MakeStage()',ctx);
assert.equal(stageCalls,1);
assert.equal(api.action('rig'),true);
assert.equal(viewer.mode,'rig');
assert.equal(viewer.page,'rig');
api.syncHandles();
assert.equal(api.inspect().joints,3,'existing XR frame builds joint handles in scene');
const weightsOverlay=()=>viewer.scene?.getObjectByName('Selected bone weighted vertices');
let overlay=weightsOverlay();
assert(overlay?.isPoints,'current XR gizmos must include actual selected bone weights');
assert.equal(overlay.raycast.length,0,'weight dots cannot block native XR hit tests');
const first=overlay.geometry.getAttribute('position');
assert(first.count>0,'live weight dots must be populated');
assert.equal(api.action('rig-next'),true);
assert.equal(api.inspect().rigBoneId,'mid');
assert.equal(api.action('rig-pose-y-plus'),true);
assert(Math.abs(rig.pose.mid[1]-Math.PI/36)<1e-6);
assert.equal(api.undoRig(),true);
assert(Math.abs((rig.pose.mid?.[1]||0))<1e-9);
assert.equal(api.beginPose(record),true);
assert.equal(viewer.gesture?.kind,'se514-rig-pose');
record.pose.quaternion.setFromAxisAngle(new THREE.Vector3(0,0,1),.3);
vm.runInContext('se340UpdateGesture()',ctx);
assert(Math.abs(rig.pose.mid[2])>.1,'Grip wrist rotation drives actual joint pose');
assert.equal(api.finishPose(record),true);
assert.equal(viewer.gesture,null);
assert.equal(api.undoRig(),true);
assert.equal(rig.pose.mid,undefined,'Undo restores neutral pose');
record.pose.quaternion.identity();
assert.equal(api.beginPose(record),true);
record.pose.quaternion.setFromAxisAngle(new THREE.Vector3(1,0,0),.25);
vm.runInContext('se340UpdateGesture()',ctx);
vm.runInContext('se340CancelGesture("B cancel")',ctx);
assert.equal(rig.pose.mid,undefined,'B cancel restores source pose');
assert.equal(viewer.gesture,null);
record.pose.quaternion.identity();
menuHit=true;const beforeClicks=paintedClicks;
vm.runInContext('se340Trigger(se350Record("right"),false)',ctx);
assert.equal(paintedClicks,beforeClicks+1,'UI-owned Trigger remains with native menu');
menuHit=false;
assert.equal(api.action('rig-weights'),true);
assert.equal(viewer.mode,'rig-weight');assert.equal(viewer.page,'rig-weights');
assert.equal(api.action('rig-select-mode'),true);
assert.equal(api.uiState().rigTarget,'vertex');
assert.equal(api.action('rig-select-mode'),true);
assert.equal(api.uiState().rigTarget,'region');
assert.equal(api.action('rig-weight-add'),true);
modelHit={id:'generic',point:new THREE.Vector3(.01,.02,0)};
const down={buttons:{RT:{physical:true}},events:[{action:'select',keys:['RT']}],cancel:false,resetRequired:false};
const filteredDown=api.beforeDispatch(down);
assert.equal(filteredDown.events.length,0,'weight brush captures its own trigger, avoids model selection');
assert.equal(api.inspect().painting,true);
assert.equal(part.skinning,undefined,'only GPU preview exists while Trigger held');
const changed=geom.getAttribute('skinWeight');
assert(changed.getX(0)<1&&changed.getY(0)>0,'weight brush updates actual GPU skinned vertex buffer');
const released=api.beforeDispatch({buttons:{RT:{physical:false}},events:[{action:'select',keys:['RT']}]});
assert.equal(released.events.length,0,'committed stroke cannot fall through to native mesh select');
assert.equal(api.inspect().painting,false);
assert.equal(part.skinning?.schema,'swyrl-explicit-skin-v1','completed stroke persists authored weights');
assert.equal(nativeUndo.length,1,'one source checkpoint per entire stroke');
assert.equal(api.undoRig(),true);
assert.equal(part.skinning,undefined,'in-VR undo restores authored weight state without scene rebuild');
assert.equal(nativeUndo.length,0,'in-VR undo does not leave duplicate native undo');
assert(Math.abs(changed.getX(0)-1)<1e-6,'in-VR undo restores GPU skin weights');
api.beforeDispatch({...down,events:[]});
assert.equal(api.inspect().painting,true);
api.cancelPaint();
assert.equal(api.inspect().painting,false,'B/tracking cancellation removes uncommitted stroke');
assert.equal(part.skinning,undefined);
assert.equal(api.action('rig-weight-stop'),true);
assert.equal(viewer.mode,'rig');assert.equal(viewer.page,'rig');
assert.equal(api.action('rig-weights'),true);
vm.runInContext('se340ModelXRAction("studio")',ctx);
assert.equal(viewer.mode,'inspect','leaving rig menu disarms paint');
vm.runInContext('se340Cleanup()',ctx);
assert.equal(api.inspect().joints,0,'XR exit releases joint gizmo handles');
assert.equal(weightsOverlay(),undefined,'XR exit must dispose weight visualization');
console.log('SE518_NATIVE_XR_SCOPE_PASS',JSON.stringify({
 nativeMenuPriority:true,gripPose:true,boneCycle:true,poseUndo:true,BCancel:true,
 fourInfluenceGPU:true,weightSave:true,weightUndo:true,strokeCapture:true,
 headsetCleanup:true,stageCalls,remembered,dirty,ui}));
