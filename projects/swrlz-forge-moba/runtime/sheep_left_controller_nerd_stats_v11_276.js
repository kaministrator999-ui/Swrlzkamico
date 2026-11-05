// §E v11.276 — Quest Sheep Tag VR Nerd Stats follow the LEFT controller.
// In a Quest browser's 2D window, HTML cannot access tracked controller poses;
// native WebXR uses the existing world-space metrics surface and L3 toggle.
const se276StatsWrist={
  mountedFrames:0,headFallbacks:0,faceCorrections:0,missingHead:0,
  lastMode:'idle',lastError:'',lastSide:'left',
  offset:new THREE.Vector3(.13,.24,-.18),
  aim:new THREE.Vector3()
};
function se276StatsWristFrame(){
  if(!se210Active())return;
  const panel=se210UI.panels.get('metrics');
  if(!panel?.root?.visible||panel.grabbing)return;
  const pose=se191XRHeadPose();
  if(!pose?.eye){se276StatsWrist.missingHead++;return;}
  const record=se192InputRecord('left');
  const hand=record?.input?.handedness==='left'&&record.controller;
  if(hand){
    // Controller local pose -> game world; no separate WebXR frame, renderer,
    // input action, or scripted camera follow.
    hand.updateMatrixWorld(true);
    panel.root.position.copy(hand.localToWorld(se276StatsWrist.offset.clone()));
    se276StatsWrist.lastMode='left-controller';
    se276StatsWrist.mountedFrames++;
  }else{
    // Tracked hand temporarily absent: keep readable near the headset
    // instead of freezing in an old world position or jumping to right hand.
    const forward=pose.forward.clone();
    forward.y=0;
    if(forward.lengthSq()<.001)forward.set(0,0,-1);
    forward.normalize();
    const right=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
    panel.root.position.copy(pose.eye)
      .addScaledVector(forward,.91)
      .addScaledVector(right,-.26)
      .addScaledVector(new THREE.Vector3(0,1,0),-.11);
    se276StatsWrist.lastMode='head-fallback';
    se276StatsWrist.headFallbacks++;
  }
  // Three.Object3D.lookAt points its +Z face AT the viewer. The older
  // matrix lookAt(panel -> eye) pointed +Z away: DoubleSide then showed
  // the reverse of the texture. Reorient the actual text/front side.
  panel.root.lookAt(pose.eye);
  panel.root.updateMatrixWorld(true);
  panel.placed=true;
  panel.follow=false;
  se276StatsWrist.faceCorrections++;
}
const se276OldXRFrame=se193XRFrame;
se193XRFrame=function(...args){
  const result=se276OldXRFrame(...args);
  se276StatsWristFrame();
  return result;
};
const se276OldXRCleanup=se193XRCleanup;
se193XRCleanup=function(...args){
  se276StatsWrist.lastMode='idle';
  return se276OldXRCleanup(...args);
};
window.SWYRL_ENGINE_QUEST_LEFT_WRIST_STATS_276=Object.freeze({
  diagnose:()=>({
    active:se210Active(),
    mode:se276StatsWrist.lastMode,
    metricsVisible:!!se210UI.panels.get('metrics')?.root?.visible,
    leftStickToggleRetained:typeof se272NerdToggle==='function',
    trackedFollowFrames:se276StatsWrist.mountedFrames,
    headFallbackFrames:se276StatsWrist.headFallbacks,
    frontFaceCorrections:se276StatsWrist.faceCorrections,
    headUnavailable:se276StatsWrist.missingHead,
    lastError:se276StatsWrist.lastError
  })
});
