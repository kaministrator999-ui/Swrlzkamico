// §E v11.367: actually visible Cliff Hand anatomy + fully rocky hand silhouette.
// No WebXR mesh substitution, no changed hand rig, no user project mutation.
// The source reference is the locally bundled 25-joint WebXR right-hand mesh.
// Preserve two DIFFERENT designs: painted single-mesh Cliff Hand and separate
// weathered stone parts Rocky Anime Hand (all 89 original parts, not 61).
const se367AnatomyState={cliffOpens:0,rockOpens:0,rockParts:0,
 rockGroups:0,retainedExteriorRocks:0,reference:'assets/models/webxr-hands/right.json'};
const se367Smooth=(a,b,v)=>{
 const t=Math.max(0,Math.min(1,(v-a)/(b-a)));
 return t*t*(3-2*t);
};
function se367CliffField(math){
 const original=se337HandField(math);
 return (x,y,z)=>{
  // This remaps the *input coordinates* of the native connected SDF, so
  // palm/wrist/fingers stay welded and the source 17-bone rig still applies.
  // Scale >1 in sampling space narrows a real physical silhouette.
  const metacarpal=se367Smooth(1.22,1.58,y)*
      (1-se367Smooth(2.08,2.31,y));
  const finger=se367Smooth(2.17,2.43,y);
  const heel=se367Smooth(1.10,1.27,y)*
      (1-se367Smooth(1.52,1.77,y));
  let xx=x*(1+.245*metacarpal+.045*heel);
  // Further soften the tiny remaining pinky-side lump rather than cutting a
  // plane through the mesh. Owner reference ulnar edge is almost straight.
  xx+=.033*metacarpal*se367Smooth(.12,.48,x);
  // Thumb root stays connected to the thenar base. Its length is preserved,
  // but the radius of the projecting saddle is more anatomically proportional.
  const thumbRoot=se367Smooth(1.35,1.56,y)*(1-se367Smooth(1.94,2.18,y))*
      (1-se367Smooth(-.52,-.27,x));
  if(x<-.45)xx+=(x+.45)*.09*thumbRoot;
  // Finger widths are refined inside the original connected organic field
  // itself (by the append-only patch), avoiding discontinuous nearest-bone
  // coordinate switches between the middle/index/ring finger web valleys.
  const zz=z*(1+.15*metacarpal+.10*finger+.045*heel);
  return original(xx,y,zz);
 };
}
const se367OriginalCliffScene=se288SmoothCliffHandScene;
se288SmoothCliffHandScene=function(){
 const scene=se367OriginalCliffScene();
 const m=scene.project?.modelAtelier;
 if(!m||m.parts.length!==1||!se220RigValidate(m.rigging)||
    m.rigging.bones.length!==17||!m.parts[0].cliffPBR)
  throw Error('Reshaped Cliff Hand must retain its single UV-painted 17-bone stone shell.');
 m.name='Plain Hand Base · Smooth Cliff Hand · Anatomy';
 scene.project.name=m.name;
 m.reference=(m.reference||'')+
  ' · §E v11.367: visibly narrower metacarpals, stronger wrist taper, separated finger barrels, straightened ulnar side and continuous thumb saddle. 25-joint WebXR comparison; no added rocks or broken UVs.';
 scene.version=11.367;scene.engine='§wyrl§ Engine · Maker v11.367';
 se367AnatomyState.cliffOpens++;
 return scene;
};
// The existing v11.365 wrapper permanently captured the unpruned 89-piece
// generator as se365OriginalStoneScene. Reuse that version rather than
// reconstructing rocks, dropping details, or cloning another hand model.
function se367AnatomicalRockScene(){
 const scene=se365OriginalStoneScene();
 const m=scene.project?.modelAtelier,parts=m?.parts;
 if(!Array.isArray(parts)||parts.length<80||!se220RigValidate(m.rigging)||
    m.rigging.bones.length!==17)throw Error('Original full-rock hand/rigger unavailable.');
 const digits=new Map(m.rigging.digits.map(f=>[f.name,f]));
 if(digits.size!==4)throw Error('Expected four independently rigged stone fingers.');
 let exterior=0;
 const groupedByName={finger:0,palm:0,side:0,wrist:0,thumb:0};
 for(const part of parts){
  const p=part.topologyMesh?.positions;
  if(!Array.isArray(p)||p.length<9||p.length%3)
   throw Error('Native stone segment missing topology: '+part.name);
  const finger=/^Finger (index|middle|ring|pinky) ·/.exec(part.name);
  const thumb=/^Thumb ·/.test(part.name);
  const isSide=/side · overhanging cliff block/.test(part.name);
  const isPalm=/^(?:Palm|Back) · cliff stratum/.test(part.name);
  const isWrist=/^Wrist/.test(part.name);
  const isFoundation=/^Cliff foundation/.test(part.name);
  const isEnergy=part.material==='emissive';
  if(/jutting outer rock|overhanging cliff block|cliff stratum|broken basalt/.test(part.name))
   exterior++;
  if(finger)groupedByName.finger++;
  if(isPalm)groupedByName.palm++;
  if(isSide)groupedByName.side++;
  if(isWrist)groupedByName.wrist++;
  if(thumb)groupedByName.thumb++;
  for(let i=0;i<p.length;i+=3){
   let x=p[i],y=p[i+1],z=p[i+2];
   const palmBand=se367Smooth(1.08,1.48,y)*
       (1-se367Smooth(2.12,2.36,y));
   if(finger){
    const f=digits.get(finger[1]),h=f.to-f.from;
    const t=Math.max(0,Math.min(1,(y-f.from)/h));
    const origin=f.x+f.splay*t;
    // Re-center each boulder/chip/crack on its actual digit bone instead of
    // forming a four-column clump. Keep separate stones and bone animation.
    // The outer chips have smaller relief than full fingertip rocks.
    const factor=/jutting outer rock/.test(part.name)?.55:.64;
    x=origin+(x-origin)*factor;
    z=f.z+(z-f.z)*(isEnergy?.73:.68);
    const extra={index:.055,middle:0,ring:.006,pinky:.045}[f.name];
    y+=extra*t;
   }else if(thumb){
    // Thumb remains diagonal and visibly opposable, never tucked into palm.
    x=-.51+(x+.51)*.88;
    z=.11+(z-.11)*.79;
   }else{
    // Actual anatomical wrist -> palm -> knuckle envelope. In particular the
    // very wide original side slabs must stop sticking beyond the hand edge.
    let scale=.86-.072*palmBand;
    if(isFoundation)scale=.84-.055*palmBand;
    else if(isSide)scale=.68-.015*palmBand;
    else if(isPalm)scale=.79-.02*palmBand;
    else if(isWrist)scale=.79;
    x*=scale;
    z*=isFoundation?.84:isSide?.72:isPalm?.81:isWrist?.79:.83;
   }
   p[i]=+x.toFixed(5);
   p[i+1]=+y.toFixed(5);
   p[i+2]=+z.toFixed(5);
  }
  // Keep original UVs and triangle indexing so every rock remains editable.
  if(part.topologyMesh.uvs.length!==p.length/3*2)
   throw Error('Original rock UV count unexpectedly changed: '+part.name);
 }
 // No stones discarded: the foundation, all faceted slabs, the full dozen
 // closed finger shafts, thumb, wrist stones and crack strands remain.
 if(exterior<30||groupedByName.finger<20||groupedByName.thumb<3||
    groupedByName.side!==10||groupedByName.palm!==20)
  throw Error('Rock Hand lost its original multi-rock detailing.');
 const ids=new Set(parts.map(part=>part.id));
 for(const group of m.meshGroups||[])
  if(group.members.some(id=>!ids.has(id)))
   throw Error('Broken original rock mesh group '+group.name);
 m.name='Rocky Anime Hand · Anatomical Rock Formation';
 scene.project.name=m.name;
 m.reference=(m.reference||'')+
  ' · v11.367 all original 89 separate stone objects retained: finger-length hierarchy and joint-centered rock barrels, anatomically tapered wrist and metacarpal core, recentered side slabs and individually editable rugged rocks. 17-bone rig and original UV maps unchanged.';
 scene.version=11.367;scene.engine='§wyrl§ Engine · Maker v11.367';
 se367AnatomyState.rockOpens++;
 se367AnatomyState.rockParts=parts.length;
 se367AnatomyState.rockGroups=m.meshGroups?.length||0;
 se367AnatomyState.retainedExteriorRocks=exterior;
 return scene;
}
se281RockScene=se367AnatomicalRockScene;
window.SWYRL_ENGINE_STONE_HAND_ANATOMY_367=Object.freeze({
 createRockScene:se367AnatomicalRockScene,
 createCliffScene:()=>se288SmoothCliffHandScene(),
 status:()=>({...se367AnatomyState,sourceIsWebXRReference:true,
  sourceBuild:'v11.367',cliffOneContinuousShell:true,rocksAreSeparate:true})
});
