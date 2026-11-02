// §E v11.215 · Native Floating Hand anatomy revision (owner's four-view phone screenshots).
// Pure geometric authoring helpers; no new renderer, network, tracker, shader or event loop.
// The negative X side is the thumb; positive X is the hypothenar / little-finger edge.
const se215FingerSpec=Object.freeze([
 {x:-.43,from:2.18,to:3.075,r:.124,splay:-.066,z:.010},
 {x:-.15,from:2.20,to:3.345,r:.128,splay:-.019,z:-.006},
 {x:.15,from:2.195,to:3.225,r:.120,splay:.029,z:-.009},
 {x:.43,from:2.14,to:2.945,r:.107,splay:.093,z:.022}
]);
function se215OrganicHandSkin(digits,{ell,cap,blend}){
 const union=(left,right,soft)=>blend(left,right,soft);
 return (x,y,z)=>{
  const p=[x,y,z];
  // Carpal transition + cupped palm: broad at metacarpals, deeper through pads.
  let d=ell(p,[.012,1.735,-.008],[.660,.545,.289]);
  d=union(d,ell(p,[.018,2.063,-.027],[.586,.292,.265]),.155);
  d=union(d,ell(p,[.005,1.305,-.006],[.415,.477,.254]),.18);
  // Anatomical palmar thenar pad / saddle. It wraps over the thumb-root
  // instead of looking like a stick grafted onto the outside wall.
  d=union(d,ell(p,[-.385,1.463,.080],[.343,.432,.313]),.165);
  d=union(d,ell(p,[-.575,1.563,.092],[.294,.335,.263]),.135);
  // Opposite thumb: hypothenar pad and curved ulnar edge (no straight slab).
  d=union(d,ell(p,[.442,1.50,.040],[.278,.449,.259]),.15);
  d=union(d,ell(p,[.485,1.875,-.009],[.205,.336,.227]),.13);
  // Convex backhand tendon arch; side profile is intentionally non-planar.
  d=union(d,ell(p,[.025,1.86,-.078],[.565,.389,.254]),.13);
  for(const f of digits){
   const bottom=[f.x,2.175,f.z];
   const middle=[f.x+f.splay*.54,f.to-.40,f.z+.010];
   const end=[f.x+f.splay,f.to-.112,f.z+.026];
   // Three tapering skeletal-looking sections, smooth under a glove skin.
   d=union(d,cap(p,bottom,middle,f.r*1.20,f.r*.89),.087);
   d=union(d,ell(p,middle,[f.r*.94,.100,f.r*.92]),.041);
   d=union(d,cap(p,middle,end,f.r*.90,f.r*.69),.052);
   d=union(d,ell(p,end,[f.r*.72,.121,f.r*.72]),.040);
  }
  // A properly angled two-section thumb, projecting toward the palm/front.
  d=union(d,cap(p,[-.575,1.51,.105],[-.904,1.856,.155],.233,.166),.126);
  d=union(d,ell(p,[-.896,1.837,.155],[.166,.165,.171]),.08);
  d=union(d,cap(p,[-.898,1.85,.16],[-1.213,2.093,.212],.162,.107),.073);
  d=union(d,ell(p,[-1.222,2.103,.213],[.110,.130,.108]),.045);
  return d;
 };
}
function se215HandAnatomicalTrim({digits,wire,sphere,color}){
 // Subtle low-profile glove seam across the thenar and ulnar contours.
 // These follow the bulging surface rather than approximating a flat palm.
 wire('Palm · anatomical thenar seam',
  [[-.37,1.21,.325],[-.49,1.39,.371],[-.55,1.59,.376],[-.59,1.75,.301]],
  .012,color.seam,'silk','Palm / anatomy');
 wire('Palm · hypothenar sweep',
  [[.45,1.20,.230],[.60,1.43,.264],[.655,1.70,.220],[.58,1.96,.180]],
  .015,color.seam,'silk','Palm / anatomy');
 wire('Ulnar edge · curved silver fillet',
  [[.51,1.16,-.092],[.675,1.40,-.095],[.718,1.69,-.085],[.671,1.94,-.093],[.56,2.13,-.105]],
  .018,color.rim,'metal','Ulnar / side armor');
 wire('Ulnar edge · purple inset',
  [[.48,1.30,-.140],[.64,1.48,-.149],[.68,1.78,-.147],[.60,2.00,-.146]],
  .014,color.accent,'emissive','Ulnar / side armor');
 // Shallow dorsal knuckle bands and palmar flexion creases emphasize joints
 // without adding rigid-looking tubes across the fingers.
 for(const [i,f] of digits.entries()){
   const x=f.x+f.splay*.58,y=f.to-.42;
   wire('Finger '+(i+1)+' · dorsal joint bevel',
    [[x-f.r*.76,y,-.129],[x,y+.023,-.148],[x+f.r*.76,y,-.129]],
    .011,color.rim,'metal','Fingers / joints');
   wire('Finger '+(i+1)+' · palmar flex crease',
    [[x-f.r*.69,y-.043,.111],[x,y-.070,.133],[x+f.r*.69,y-.043,.111]],
    .008,color.seam,'silk','Fingers / joints');
 }
 // Thumb root plate sits on the sloping dorsal saddle rather than at a flat,
 // isolated tube junction.
 sphere('Thumb · saddle armor accent',[-.619,1.578,-.202],[.182,.185,.052],
  color.plate,'metal','Thumb / armor');
 wire('Thumb · saddle-to-wrist contour',
  [[-.52,1.29,-.212],[-.725,1.50,-.232],[-.827,1.698,-.175]],
  .018,color.accent,'emissive','Thumb / armor');
}
