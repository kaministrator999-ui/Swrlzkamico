/* SE518_RIG_SCOPE_ACCESS_START
   Restrict the immersive rig hooks to the native Model Atelier closure.
   GPU bones, selected joint, and the pose history remain owned by Modeler.
   Never expose project documents or account credentials. */
window.SWYRL_ENGINE_MODEL_RIG_ACCESS_518=Object.freeze({
 available:()=>se220RigAvailable(),
 rig:()=>se220Rig(),
 get bones(){return se220Bones;},
 get skeleton(){return se220Skeleton;},
 get root(){return modelRoot;},
 get joint(){return se220Joint;},
 set joint(value){se220Joint=value;},
 get playing(){return se220Playing;},
 set playing(value){se220Playing=!!value;},
 get poseHistory(){return se220PoseHistory;},
 element:id=>se220R(id),
 jointUI:()=>se220RigJointUI(),
 pose:pose=>se220RigPose(pose),
 remember:()=>se220RigRemember(),
 touched:message=>se220RigTouched(message),
 validate:rig=>se220RigValidate(rig),
 part:id=>partById(id),
 checkpoint:()=>checkpoint(),
 inspect:()=>({ready:!!modelRoot,available:se220RigAvailable(),
  bones:se220Rig()?.bones?.length||0})
});
 /* SE518_RIG_SCOPE_ACCESS_END */
