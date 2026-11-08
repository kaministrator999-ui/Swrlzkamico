/* SE344_MODEL_VR_AIM_VIEWS_START */
// Per-controller WebXR target-ray calibration. Meta's OS overlay pointer is
// not exposed to WebXR; calibrate a small local aim offset only when needed.
const SE344_AIM_KEY='swrlz-model-vr-pointer-calibration-v1';
function se344ReadAim(){
 const empty=()=>({yaw:0,pitch:0});
 try{
  const value=JSON.parse(localStorage.getItem(SE344_AIM_KEY)||'null');
  if(!value||typeof value!=='object')return {left:empty(),right:empty()};
  const read=v=>({yaw:THREE.MathUtils.clamp(Number(v?.yaw)||0,-25,25),
   pitch:THREE.MathUtils.clamp(Number(v?.pitch)||0,-25,25)});
  return {left:read(value.left),right:read(value.right)};
 }catch(_){return {left:empty(),right:empty()};}
}
function se344WriteAim(){
 try{localStorage.setItem(SE344_AIM_KEY,JSON.stringify(se340XR.aim));}catch(_){}
}
function se344Hand(record){
 const h=record.input?.handedness;
 return h==='left'||h==='right'?h:record.index===0?'left':'right';
}
function se344AimQuat(record){
 const a=se340XR.aim?.[se344Hand(record)]||{yaw:0,pitch:0};
 return new THREE.Quaternion().setFromEuler(
  new THREE.Euler(THREE.MathUtils.degToRad(a.pitch),THREE.MathUtils.degToRad(a.yaw),0,'YXZ'));
}
function se344SetView(view){
 const s=se340XR;
 if(s.gesture){se340Notice('Release the active grip before changing view.');return false;}
 const yaw=Math.atan2(-s.forward.x,-s.forward.z);
 const presets={
  front:[0,0],back:[Math.PI,0],left:[-Math.PI/2,0],
  right:[Math.PI/2,0],top:[0,-Math.PI/2+.035],
  bottom:[0,Math.PI/2-.035],iso:[-Math.PI/4,-.62]
 };
 if(view==='orbit'){s.viewMode='orbit';se340Notice('Free orbit · use right joystick.');return true;}
 const pose=presets[view];if(!pose)return false;
 s.yaw=yaw+pose[0];s.pitch=pose[1];s.viewMode=view;
 se340Notice(view[0].toUpperCase()+view.slice(1)+' model view · right stick resumes free orbit.');
 return true;
}
function se344AimAction(action){
 const s=se340XR;
 if(action==='aim-hand'){s.aimHand=s.aimHand==='left'?'right':'left';}
 else if(action==='aim-reset-all'){
  s.aim={left:{yaw:0,pitch:0},right:{yaw:0,pitch:0}};
  se344WriteAim();
 }else{
  const a=s.aim[s.aimHand];
  const step=2;
  if(action==='aim-yaw-minus')a.yaw=THREE.MathUtils.clamp(a.yaw-step,-25,25);
  else if(action==='aim-yaw-plus')a.yaw=THREE.MathUtils.clamp(a.yaw+step,-25,25);
  else if(action==='aim-pitch-minus')a.pitch=THREE.MathUtils.clamp(a.pitch-step,-25,25);
  else if(action==='aim-pitch-plus')a.pitch=THREE.MathUtils.clamp(a.pitch+step,-25,25);
  else if(action==='aim-reset'){a.yaw=0;a.pitch=0;}
  else return false;
  se344WriteAim();
 }
 for(const record of s.controllers){
  if(record.ray)record.ray.quaternion.copy(se344AimQuat(record));
  record.nextHoverAt=0;record.hit=null;record.hoverKey=null;
 }
 const a=s.aim[s.aimHand];
 se340Notice(s.aimHand.toUpperCase()+' target-ray offset: yaw '+a.yaw+'°, pitch '+a.pitch+'°. Stored on this browser.');
 return true;
}
/* SE344_MODEL_VR_AIM_VIEWS_END */
