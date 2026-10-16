// V11_11_FACE_POSE_FRAMES — editable native spline poses, frame snapshots and camera views.
// No fake skeleton: knee profiles deform actual anatomical loft control knots.
const atelierBuiltInPoses=['neutral','idle','victory','victory-b'];
function atelierTransformSnapshot(){
  return model().parts.map(p=>({id:p.id,position:p.position.slice(),rotation:p.rotation.slice(),
    scale:p.scale.slice(),...(p.kind==='loft'?{path:p.path.map(q=>q.slice())}:{})}));
}
function atelierValidPoseFrame(frame){
  if(!frame||typeof frame!=='object'||!Array.isArray(frame.poses)||frame.poses.length>MODEL_ATELIER_LIMIT)return false;
  if(frame.name!==undefined&&(typeof frame.name!=='string'||frame.name.length>36))return false;
  if(frame.camera!==undefined&&(!frame.camera||!['yaw','pitch','distance'].every(k=>Number.isFinite(frame.camera[k])&&Math.abs(frame.camera[k])<100)))return false;
  const ids=new Set();
  for(const v of frame.poses){
    if(!v||typeof v.id!=='string'||v.id.length>90||ids.has(v.id))return false;
    ids.add(v.id);
    for(const key of ['position','rotation','scale']){
      if(!Array.isArray(v[key])||v[key].length!==3||!v[key].every(n=>Number.isFinite(n)&&Math.abs(n)<=100))return false;
    }
    if(v.scale.some(n=>n<=.005||n>20))return false;
    if(v.path!==undefined&&(!Array.isArray(v.path)||v.path.length<2||v.path.length>40
      ||!v.path.every(q=>Array.isArray(q)&&q.length===3&&q.every(n=>Number.isFinite(n)&&Math.abs(n)<=100))))return false;
  }
  return true;
}
function atelierValidatedFrameStore(source){
  const list=source?.poseFrames===undefined?[]:source.poseFrames;
  if(!Array.isArray(list)||list.length>8||!list.every(f=>typeof f.name==='string'&&f.name.trim().length>0&&atelierValidPoseFrame(f))
    ||new Set(list.map(f=>f.name.toLowerCase())).size!==list.length)throw Error('Invalid saved pose frames.');
  const neutral=source?.poseNeutral;
  if(neutral!==undefined&&!atelierValidPoseFrame(neutral))throw Error('Invalid neutral pose.');
  return {poseFrames:structuredClone(list),poseNeutral:neutral?structuredClone(neutral):null};
}
function atelierPoseCamera(){return {yaw:orbit.yaw,pitch:orbit.pitch,distance:orbit.distance};}
function atelierSetPoseCamera(view){
  const views={front:[0,.1,8.1],back:[Math.PI,.1,8.1],left:[-Math.PI/2,.1,8.1],
    right:[Math.PI/2,.1,8.1],three:[.42,.17,8.6],hero:[.34,.11,7.9]};
  if(view in views){const [yaw,pitch,distance]=views[view];orbit={yaw,pitch,distance};cameraUpdate();return true;}
  return false;
}
function atelierApplyStoredTransforms(frame){
  if(!atelierValidPoseFrame(frame))throw Error('Invalid pose snapshot.');
  const map=new Map(frame.poses.map(p=>[p.id,p]));
  for(const p of model().parts){
    const saved=map.get(p.id);if(!saved)continue;
    p.position=saved.position.slice();p.rotation=saved.rotation.slice();p.scale=saved.scale.slice();
    if(p.kind==='loft'&&saved.path)p.path=saved.path.map(q=>q.slice());
  }
}
function atelierBendNativeLeg(part,amount,lean){
  if(part.kind!=='loft'||part.surfaceStyle!=='anatomy-smooth'||part.path?.length!==6)return;
  const weights=[0,.2,.65,1,.68,0];
  part.path=part.path.map((point,i)=>[
    +(point[0]+weights[i]*lean).toFixed(4),
    point[1],
    +(point[2]+weights[i]*amount).toFixed(4)]);
}
function atelierApplyBuiltInPose(name){
  if(!atelierBuiltInPoses.includes(name)||!model())return false;
  if(!model().poseNeutral)model().poseNeutral={poses:atelierTransformSnapshot(),camera:atelierPoseCamera()};
  if(!atelierValidPoseFrame(model().poseNeutral)){status('Neutral reference is invalid.',true);return false;}
  checkpoint();atelierApplyStoredTransforms(model().poseNeutral);
  if(name!=='neutral'){
    const left=partById('atelier-v118-left-leg'),right=partById('atelier-v118-right-leg');
    if(!left||!right||left.kind!=='loft'||right.kind!=='loft'){status('This preset needs both original anatomical leg lofts.',true);historyStep(true);return false;}
    const params={
      idle:{left:[.19,-.018],right:[.10,.008]},
      victory:{left:[.08,-.034],right:[.31,.047]},
      'victory-b':{left:[.31,-.05],right:[.09,.024]}
    }[name];
    atelierBendNativeLeg(left,...params.left);atelierBendNativeLeg(right,...params.right);
    const sway=name==='idle'?.021:name==='victory'?.052:-.052;
    for(const p of model().parts){
      // Move upper figure detail coherently, avoiding feet and standalone ferrets.
      if(p.group!=='Character'||p.id==='atelier-v118-left-leg'||p.id==='atelier-v118-right-leg')continue;
      const anchor=p.kind==='loft'&&p.path?.length?p.path[0][1]:p.position[1];
      if(anchor>=3.5){
        if(p.kind==='loft')p.path=p.path.map(q=>[+(q[0]+sway*.5).toFixed(4),q[1],q[2]]);
        else p.position[0]=+(p.position[0]+sway*.5).toFixed(4);
      }
    }
  }
  model().poseActive=name;selection=null;signalEdited();
  atelierSetPoseCamera(name==='neutral'?'three':name==='idle'?'three':'hero');
  status('Applied editable '+name+' pose · knee bends are actual loft spline deformations. Undo is available.');
  return true;
}
function atelierApplySavedPose(name){
  const frame=model()?.poseFrames?.find(f=>f.name===name);
  if(!frame||!atelierValidPoseFrame(frame)){status('Saved frame unavailable or invalid.',true);return false;}
  checkpoint();atelierApplyStoredTransforms(frame);
  model().poseActive=name;selection=null;signalEdited();
  if(frame.camera){orbit={...frame.camera};cameraUpdate();}
  status('Loaded saved '+name+' frame · native part transforms restored. Undo is available.');
  return true;
}
function atelierRefreshPoseChoices(){
  const sel=$m('PoseSelect');if(!sel||!model())return;
  const chosen=sel.value,fragment=document.createDocumentFragment();
  for(const [value,label] of [['neutral','Neutral'],['idle','Relaxed idle · bent knees'],['victory','Victory · right knee'],['victory-b','Victory B · left knee']]){
    const option=document.createElement('option');option.value=value;option.textContent=label;fragment.append(option);
  }
  for(const frame of model().poseFrames||[]){
    const option=document.createElement('option');option.value='saved:'+frame.name;option.textContent='Saved · '+frame.name;fragment.append(option);
  }
  sel.replaceChildren(fragment);sel.value=[...sel.options].some(o=>o.value===chosen)?chosen:'idle';
}
function atelierSavePoseFrame(){
  if(!model())return;
  const textValue=$m('PoseName').value.trim();
  if(!textValue||textValue.length>36||!(/[\p{L}\p{N}]/u).test(textValue)){status('Frame name must contain letters/numbers and fit 36 characters.',true);return;}
  if(atelierBuiltInPoses.includes(textValue.toLowerCase())){status('Use a different name from the built-in presets.',true);return;}
  const frames=model().poseFrames||(model().poseFrames=[]);
  const existing=frames.findIndex(f=>f.name.toLowerCase()===textValue.toLowerCase());
  if(existing<0&&frames.length>=8){status('Save a maximum of eight custom frames.',true);return;}
  const frame={name:textValue,poses:atelierTransformSnapshot(),camera:atelierPoseCamera()};
  if(!atelierValidPoseFrame(frame)){status('Frame transforms invalid.',true);return;}
  if(existing>=0)frames[existing]=frame;else frames.push(frame);
  if(typeof markDirty==='function')markDirty();
  atelierRefreshPoseChoices();$m('PoseSelect').value='saved:'+textValue;
  status('Saved pose and camera as '+textValue+'. Save Project or export model JSON to retain it.');
}
function atelierRemovePoseFrame(){
  if(!model())return;
  const value=$m('PoseSelect').value;if(!value.startsWith('saved:')){status('Choose a saved custom frame to delete.',true);return;}
  const name=value.slice(6),frames=model().poseFrames||[],index=frames.findIndex(f=>f.name===name);
  if(index<0)return;
  frames.splice(index,1);if(typeof markDirty==='function')markDirty();
  atelierRefreshPoseChoices();status('Deleted saved frame '+name+'.');
}
function atelierPoseDeckInstall(){
  const picker=$m('PoseSelect');if(!picker)return;
  atelierRefreshPoseChoices();
  $m('PoseApply').addEventListener('click',()=>{
    const choice=picker.value;
    if(choice.startsWith('saved:'))atelierApplySavedPose(choice.slice(6));
    else atelierApplyBuiltInPose(choice);
  });
  $m('PoseSave').addEventListener('click',atelierSavePoseFrame);
  $m('PoseDelete').addEventListener('click',atelierRemovePoseFrame);
  $m('PoseViewApply').addEventListener('click',()=>{
    const value=$m('PoseView').value;
    if(atelierSetPoseCamera(value))status('Camera set to '+value+'; save a custom frame to retain this view.');
  });
}
