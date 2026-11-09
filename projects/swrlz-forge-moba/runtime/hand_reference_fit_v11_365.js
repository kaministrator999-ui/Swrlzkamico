// §E v11.365 · anatomy-led refinement for the two existing stone-hand starters.
// Source measurements: MIT WebXR Input Profiles generic-hand/right.glb, 25 joint
// landmarks in assets/models/webxr-hands/right.json. Ratios use (tip - proximal)
// along the long axis, normalized against the middle finger:
// index .943, middle 1, ring .920, pinky .746. Reuse these calibrated ratios
// instead of introducing a new displayed hand, renderer, mesh or rig.
const se365WebXRAnatomy=Object.freeze({
 source:'assets/models/webxr-hands/right.json',
 tipToProximal: Object.freeze({index:.943,middle:1,ring:.920,pinky:.746}),
 cliffFingerRise:Object.freeze({index:.048,middle:0,ring:0,pinky:.042}),
 rockFingerRise:Object.freeze({index:.050,middle:0,ring:.004,pinky:.041})
});
const se365Smooth=(a,b,n)=>{
 const t=Math.max(0,Math.min(1,(n-a)/(b-a)));
 return t*t*(3-2*t);
};
const se365OriginalStoneScene=se281RockScene;
const se365RockMeasurements={originalParts:0,retainedParts:0,removedByCategory:{},runs:0};
function se365RefinedRockScene(){
 const scene=se365OriginalStoneScene();
 const m=scene.project?.modelAtelier;
 if(!m||!Array.isArray(m.parts)||!se220RigValidate(m.rigging))
  throw Error('Reference-aligned Rock Hand requires the existing native rock anatomy and rig.');
 const initial=m.parts;
 // These are ONLY decorative rocks. Keep all true 360-degree palm, finger,
 // thumb and wrist anatomy, every major joint and every existing crack.
 const removed={palm:0,side:0,fingerChips:0,wrist:0};
 const kept=initial.filter(part=>{
  let match;
  if((match=part.name.match(/^(?:Back|Palm) · cliff stratum (\d+)$/))&&+match[1]>5){
   removed.palm++;return false;
  }
  if((match=part.name.match(/side · overhanging cliff block (\d+)$/))&&+match[1]!==3){
   removed.side++;return false;
  }
  if((match=part.name.match(/^Finger (?:index|middle|ring|pinky) · jutting outer rock (\d+)$/))&&+match[1]!==2){
   removed.fingerChips++;return false;
  }
  if((match=part.name.match(/^Wrist root · (?:back|front) broken basalt (\d+)$/))&&+match[1]===2){
   removed.wrist++;return false;
  }
  return true;
 });
 if(initial.length<100||kept.length>=initial.length||removed.fingerChips!==8||
    removed.side!==8||removed.palm!==10||removed.wrist!==2)
  throw Error('Rock Hand reference filter encountered unexpected original model topology.');
 const digits=new Map(m.rigging.digits.map(f=>[f.name,f]));
 if(digits.size!==4)throw Error('Native rock hand finger hierarchy has changed.');
 for(const part of kept){
  const mesh=part.topologyMesh,positions=mesh?.positions;
  if(!Array.isArray(positions)||positions.length%3)throw Error('Missing native rock topology');
  const isFinger=/^Finger (index|middle|ring|pinky) ·/.exec(part.name);
  const isThumb=/^Thumb ·/.test(part.name);
  const f=isFinger?digits.get(isFinger[1]):null;
  for(let j=0;j<positions.length;j+=3){
   let x=positions[j],y=positions[j+1],z=positions[j+2];
   // Smooth anatomical wrist-to-metacarpal taper instead of a stack of
   // swollen round rocks. Preserve the existing finger root spacing.
   const palmBand=se365Smooth(1.08,1.48,y)*
      (1-se365Smooth(2.12,2.37,y));
   x*=1-.070*palmBand;
   z*=1-.105*palmBand;
   if(f){
    const t=Math.max(0,Math.min(1,(y-f.from)/(f.to-f.from)));
    const center=f.x+f.splay*t;
    const radiusScale=.84+.08*t;
    x=center+(x-center)*radiusScale;
    z=f.z+(z-f.z)*(.86+.05*t);
    y+=se365WebXRAnatomy.rockFingerRise[f.name]*t;
   }else if(isThumb){
    // Thumb still grows from the real thenar root; don't move its base or
    // flatten the joint into a straight cylinder.
    const rootFade=se365Smooth(1.48,1.78,y);
    x=-.45+(x+.45)*(1-.07*rootFade);
    z*=.88;
   }else if(/cliff stratum|overhanging cliff|broken basalt/.test(part.name)){
    // Insets follow the reshaped solid palm instead of remaining oversized.
    z*=.93;
   }
   positions[j]=+x.toFixed(5);
   positions[j+1]=+y.toFixed(5);
   positions[j+2]=+z.toFixed(5);
  }
  // Deliberately do not rewrite UVs, texture paint, bone weights or face IDs.
 }
 m.parts=kept;
 const present=new Set(kept.map(part=>part.id));
 // Preserve established mesh groups and prune removed decorative references.
 m.meshGroups=(m.meshGroups||[]).map(group=>({
  ...group,members:group.members.filter(id=>present.has(id))
 })).filter(group=>group.members.length>=2);
 // This scene inherits no bone/rig transformations: old animations still work.
 m.reference=(m.reference||'')+
  ' · v11.365 WebXR-measured index/pinky length corrections and controlled finger taper; 28 redundant exterior stone slabs/chips removed. Native stone, wrist, thumb, 17-bone rig, texture UVs and fracture details preserved.';
 scene.engine='§wyrl§ Engine · Maker v11.365';scene.version=11.365;
 se365RockMeasurements.originalParts=initial.length;
 se365RockMeasurements.retainedParts=kept.length;
 se365RockMeasurements.removedByCategory=removed;
 se365RockMeasurements.runs++;
 return scene;
}
se281RockScene=se365RefinedRockScene;
// The separate Smooth Cliff Hand is refined in the preceding append-only patch:
// preserve one connected SDF mesh, photo-led thumb/pinky contour and the rock
// color/normal/roughness/AO shader. Do not affect Plain Hand or Arcane Glove.
window.SWYRL_ENGINE_HAND_REFERENCE_FIT_365=Object.freeze({
 ratios:se365WebXRAnatomy.tipToProximal,
 rock:()=>({...se365RockMeasurements}),
 status:()=>({source:se365WebXRAnatomy.source,stoneProjects:['plain-hand-base','rocky-anime-hand'],
  nativeRigsPreserved:true,newModelParts:0,rockPartRemovalTarget:28}),
 previewRock:se365RefinedRockScene
});
