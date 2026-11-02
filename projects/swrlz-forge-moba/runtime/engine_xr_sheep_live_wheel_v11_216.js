// §E v11.216 — Sheep Tag Quest Play: move AND select simultaneously.
// v11.214 rightly made the A/X wheel upright, head-following, and the sole
// modal pointer. It wrongly silenced the left movement stick and world follow.
// Restore both original authoritatively collision-checked paths while keeping
// the right stick dedicated to house/ability selection (v11.204's own gate).
// Never change the HMD's native orientation, tracking space, or VR OS state.
const se216={
  movingWithWheelFrames:0,followingWithWheelFrames:0,
  wheelOpensWithoutCancelingMovement:0,lastIntent:null
};

// The v11.214 show wrapper invokes this before presenting a new wheel.
// An already-held VR stick is normal gameplay, NOT a stale command to cancel.
se214StopStickOrder=function(){
  se216.wheelOpensWithoutCancelingMovement++;
};

// Restore the native stick intent for the left controller throughout the
// modal. se200MoveUnit handles terrain collision, speed and host authority.
const se216NativeStickIntent=se214PriorStickIntent;
se199StickIntent=function(...args){
  const intent=se216NativeStickIntent(...args);
  if(se214WheelOpen()){
    se216.movingWithWheelFrames++;
    se216.lastIntent={
      x:Number(intent?.x)||0,z:Number(intent?.z)||0,
      strength:Number(intent?.strength)||0
    };
  }
  return intent;
};

// Keep the camera smoothly centered on the moving sheep. v11.214's wheel
// already follows tracked HMD eye every frame and remains yaw-upright.
// In v11.204, se192Stick('right') is *already neutralized* while the quick
// wheel is open; right thumbstick still selects sectors via raw gamepad axes.
// Therefore camera follow moves with the sheep but never orbits/zooms from
// the selection stick. Other OS-overlay guards (v11.211) are unchanged.
const se216NativeFollow=se214PriorFollow;
se195FollowCamera=function(dt){
  if(se214WheelOpen())se216.followingWithWheelFrames++;
  return se216NativeFollow(dt);
};

window.SWYRL_ENGINE_SHEEP_LIVE_WHEEL_216=Object.freeze({
  diagnose:()=>({
    wheelOpen:se214WheelOpen(),sheepMovementAllowed:true,
    leftStickOwnsSheep:true,rightStickSelectsWheel:true,
    cameraTracksMovingSheep:true,headsetPoseUnchanged:true,
    currentInput:se216.lastIntent,
    wheelMovementFrames:se216.movingWithWheelFrames,
    wheelCameraFollowFrames:se216.followingWithWheelFrames,
    wheelOpensWithoutMovementCancellation:se216.wheelOpensWithoutCancelingMovement
  })
});
