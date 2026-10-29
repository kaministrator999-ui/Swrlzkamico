// V11_12_GROUNDED_STANCE_POSES — screenshot corrective pass, native geometry not faux joints.
// Model's two six-knot anatomy-smooth leg lofts form two nearly straight sections
// (hip -> knee -> ankle); feet translate as a complete side-specific assembly.
const atelierGroundedStances=Object.freeze({
  idle:{
    left:{kneeX:-.014,kneeZ:.055,footX:-.04,footZ:.015},
    right:{kneeX:0,kneeZ:.005,footX:0,footZ:0}},
  victory:{
    left:{kneeX:0,kneeZ:.006,footX:0,footZ:0},
    right:{kneeX:.037,kneeZ:.105,footX:.11,footZ:.04}},
  'victory-b':{
    left:{kneeX:-.037,kneeZ:.105,footX:-.11,footZ:.04},
    right:{kneeX:0,kneeZ:.006,footX:0,footZ:0}}
});
const atelierFootParts=Object.freeze({
  left:['model-0020','model-0021','model-0022','atelier-v117-0423','v119-left-toe','v119-left-sole','v119-left-sock'],
  right:['model-0037','model-0038','model-0039','atelier-v117-0440','v119-right-toe','v119-right-sole','v119-right-sock']
});
function atelierGroundedLeg(part,config){
  if(part?.kind!=='loft'||part.surfaceStyle!=='anatomy-smooth'||part.path?.length!==6)return false;
  const original=part.path.map(p=>p.slice());
  const hip=original[0],ankle=original[5];
  const kneeY=(original[2][1]+original[3][1])/2;
  const kneeBase=original[2].map((v,axis)=>(v+original[3][axis])/2);
  const knee=[kneeBase[0]+config.kneeX,kneeY,kneeBase[2]+config.kneeZ];
  const foot=[ankle[0]+config.footX,ankle[1],ankle[2]+config.footZ];
  // At every point, interpolate along one anatomical segment, not a bell-curve
  // which made the whole thigh and shin appear rubbery in v11.11.
  part.path=original.map((p,i)=>{
    if(i===0)return hip.slice();
    if(i===5)return foot.map(n=>+n.toFixed(4));
    const upper=p[1]>=kneeY;
    const from=upper?hip:knee,to=upper?knee:foot;
    const factor=upper?(hip[1]-p[1])/(hip[1]-kneeY):(kneeY-p[1])/(kneeY-foot[1]);
    return [
      +(from[0]+(to[0]-from[0])*factor).toFixed(4),
      p[1],
      +(from[2]+(to[2]-from[2])*factor).toFixed(4)
    ];
  });
  return true;
}
function atelierGroundedFoot(side,config){
  for(const id of atelierFootParts[side]){
    const p=partById(id);if(!p)continue;
    p.position[0]=+(p.position[0]+config.footX).toFixed(4);
    p.position[2]=+(p.position[2]+config.footZ).toFixed(4);
    // Shoe and sock heights remain anchored on stage, including their soles.
  }
}
function atelierApplyBuiltInPose(name){
  if(!atelierBuiltInPoses.includes(name)||!model())return false;
  if(!model().poseNeutral)model().poseNeutral={poses:atelierTransformSnapshot(),camera:atelierPoseCamera()};
  if(!atelierValidPoseFrame(model().poseNeutral)){status('Neutral reference invalid.',true);return false;}
  if(name!=='neutral'&&(!partById('atelier-v118-left-leg')||!partById('atelier-v118-right-leg'))){
    status('Original continuous anatomical legs needed for this preset.',true);return false;
  }
  checkpoint();atelierApplyStoredTransforms(model().poseNeutral);
  if(name!=='neutral'){
    const stance=atelierGroundedStances[name];
    if(!stance){status('Unknown grounded stance.',true);return false;}
    for(const side of ['left','right']){
      if(!atelierGroundedLeg(partById('atelier-v118-'+side+'-leg'),stance[side])){
        historyStep(true);status('Anatomical leg is invalid.',true);return false;
      }
      atelierGroundedFoot(side,stance[side]);
    }
  }
  // Do not shift the face independently from the neck/torso or leave companion
  // hair sockets hanging in space. Upper figure stays an attached silhouette.
  model().poseActive=name;selection=null;signalEdited();
  atelierSetPoseCamera(name==='neutral'?'three':name==='idle'?'three':'hero');
  status(name==='neutral'?'Restored native neutral model.':'Applied grounded '+name+' stance · planted soles and segmented knees. Undo available.');
  return true;
}
