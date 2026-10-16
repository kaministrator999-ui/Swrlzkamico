import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const root=new URL('../',import.meta.url);
const scene=JSON.parse(readFileSync(new URL('scenes/model-atelier-prism-jester-festival-v11-9.swyrl.json',root),'utf8'));
let current=structuredClone(scene.project.modelAtelier);
const original=structuredClone(current.parts);
const model=()=>current;
const partById=id=>current.parts.find(p=>p.id===id);
let undo=[],edits=0;
const checkpoint=()=>undo.push(JSON.stringify(current.parts));
const historyStep=()=>{current.parts=JSON.parse(undo.pop())};
let orbit={yaw:0,pitch:0,distance:9},view='';
const ctx={model,partById,checkpoint,historyStep,structuredClone,
    atelierBuiltInPoses:['neutral','idle','victory','victory-b'],
    atelierTransformSnapshot:()=>current.parts.map(p=>({id:p.id,position:p.position.slice(),rotation:p.rotation.slice(),
      scale:p.scale.slice(),...(p.kind==='loft'?{path:p.path.map(q=>q.slice())}:{})})),
    atelierValidPoseFrame:()=>true,
    atelierPoseCamera:()=>({yaw:orbit.yaw,pitch:orbit.pitch,distance:orbit.distance}),
    atelierApplyStoredTransforms:f=>{const m=new Map(f.poses.map(x=>[x.id,x]));for(const p of current.parts){const s=m.get(p.id);if(!s)continue;p.position=s.position.slice();p.rotation=s.rotation.slice();p.scale=s.scale.slice();if(p.kind==='loft'&&s.path)p.path=s.path.map(x=>x.slice())}},
    signalEdited:()=>edits++,atelierSetPoseCamera:x=>view=x,status:()=>{},selection:null};
vm.createContext(ctx);
vm.runInContext(readFileSync(new URL('runtime/model_atelier_grounded_poses_v11_12.js',root),'utf8'),ctx);
const apply=vm.runInContext('atelierApplyBuiltInPose',ctx);
const by=arr=>Object.fromEntries(arr.map(p=>[p.id,p]));
const base=by(original);
const assertNear=(got,want,label,tol=.001)=>assert(Math.abs(got-want)<tol,label+': '+got+' vs '+want);
function assertLeg(side,config){
  const id='atelier-v118-'+side+'-leg',old=base[id].path,leg=partById(id).path;
  const ankle=leg[5],kneeY=(old[2][1]+old[3][1])/2;
  assert.deepEqual(leg.map(x=>x[1]),old.map(x=>x[1]),'Native segment heights changed');
  assertNear(leg[0][0],old[0][0],'Hip X');assertNear(leg[0][2],old[0][2],'Hip Z');
  assertNear(ankle[0],old[5][0]+config.footX,'Ankle X');
  assertNear(ankle[2],old[5][2]+config.footZ,'Ankle Z');
  const knee=[0,kneeY,0],crossed=(k,key)=>leg[k][key];
  // All four interior knots must lie within 1mm of the two straight axis segments.
  const kneeBase=old[2].map((v,axis)=>(v+old[3][axis])/2);
  knee[0]=kneeBase[0]+config.kneeX;knee[2]=kneeBase[2]+config.kneeZ;
  for(let i=1;i<5;i++){
    const upper=leg[i][1]>=kneeY,from=upper?leg[0]:knee,to=upper?knee:ankle;
    const t=upper?(from[1]-leg[i][1])/(from[1]-to[1]):(from[1]-leg[i][1])/(from[1]-to[1]);
    assertNear(crossed(i,0),from[0]+t*(to[0]-from[0]),side+' straight-section X',.001);
    assertNear(crossed(i,2),from[2]+t*(to[2]-from[2]),side+' straight-section Z',.001);
  }
  const angle=Math.acos(Math.max(-1,Math.min(1,
      ((leg[0][0]-knee[0])*(ankle[0]-knee[0])+(leg[0][1]-knee[1])*(ankle[1]-knee[1])+(leg[0][2]-knee[2])*(ankle[2]-knee[2]))/
      (Math.hypot(...leg[0].map((v,i)=>v-knee[i]))*Math.hypot(...ankle.map((v,i)=>v-knee[i]))))))*180/Math.PI;
  const bend=180-angle;
  assert(bend<25,'Knee snapped into unnatural bend: '+bend);
  for(const footid of ['left','right'].includes(side)?vm.runInContext('atelierFootParts',ctx)[side]:[]){
    const oldP=base[footid],part=partById(footid);
    assertNear(part.position[0],oldP.position[0]+config.footX,'shoe/sock X');
    assertNear(part.position[2],oldP.position[2]+config.footZ,'shoe/sock Z');
    assertNear(part.position[1],oldP.position[1],'shoe/sock grounded height');
  }
}
for(const pose of ['idle','victory','victory-b']){
  assert(apply(pose),'Failed '+pose+' application');
  assert.equal(current.parts.length,811,'Historical native meshes lost');
  const stance=vm.runInContext('atelierGroundedStances',ctx)[pose];
  for(const side of ['left','right'])assertLeg(side,stance[side]);
  for(const id of ['model-0001','model-0003','atelier-fidelity-401','atelier-fidelity-507']){
    if(!base[id])continue;
    assert.deepEqual(partById(id).position,base[id].position,'Face/torso/ferret detached from stable scene');
  }
  const snapshot=JSON.stringify(current.parts);
  assert(apply(pose));assert.equal(JSON.stringify(current.parts),snapshot,'Preset compounds repeated deformation');
}
assert(apply('neutral'));
for(const id of ['atelier-v118-left-leg','atelier-v118-right-leg','v119-left-sole','v119-right-sole']){
  assert.deepEqual(partById(id).path||partById(id).position,base[id].path||base[id].position,'Neutral failed to restore '+id);
}
assert(edits>=7,'No editable project mutations');
console.log('GROUNDED_STANCE_811_PARTS_KNEE_FOOT_ANCHOR_PASS');
