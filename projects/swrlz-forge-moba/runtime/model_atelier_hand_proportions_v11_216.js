// §E v11.216. Owner's second phone review: correct finger ratios and over-round
// ulnar/pinky-side palm. This is ONLY a new Floating Hand starter builder.
// x<0 = thumb/index side; x>0 = pinky/hypothenar side.
// Smaller distal radii and differing finger phalange ratios are deliberate.
const se216FingerSpec=Object.freeze([
 {x:-.397,from:2.170,to:2.990,r:.104,splay:-.055,z:.006,name:'index'},
 {x:-.131,from:2.197,to:3.168,r:.112,splay:-.017,z:-.009,name:'middle'},
 {x:.135,from:2.176,to:3.077,r:.103,splay:.028,z:-.009,name:'ring'},
 {x:.402,from:2.113,to:2.791,r:.084,splay:.083,z:.010,name:'pinky'}
]);
// Signed-distance field with smooth connected skin, not separate finger tubes.
// Z front is the palm side, Z negative is the dorsal/backhand side.
function se216OrganicHandSkin(digits,{ell,cap,blend}){
 const add=(a,b,k)=>blend(a,b,k);
 return (x,y,z)=>{
  const p=[x,y,z];
  // Taper the hand gently between wider knuckles and narrower carpal/wrist.
  // Remove the previous huge round disk-like palm at y=1.7.
  let d=ell(p,[.002,1.765,-.013],[.573,.497,.266]);
  d=add(d,ell(p,[-.007,2.067,-.021],[.540,.291,.237]),.130);
  d=add(d,ell(p,[.004,1.299,-.009],[.363,.445,.224]),.156);
  // Thenar pad blends into the actual thumb root; preserve a visible web valley.
  d=add(d,ell(p,[-.335,1.498,.074],[.258,.346,.257]),.123);
  d=add(d,ell(p,[-.515,1.625,.104],[.214,.280,.233]),.106);
  // Opposite thumb: smaller elongated pinky-side hypothenar pad, not a sphere
  // glued to the palm. Lower edge joins the wrist and supports the pinky root.
  d=add(d,ell(p,[.363,1.495,.024],[.191,.351,.222]),.115);
  d=add(d,ell(p,[.411,1.871,-.019],[.152,.270,.210]),.088);
  // Subtle dorsal arch, narrower than the old circular armored shield region.
  d=add(d,ell(p,[.016,1.89,-.076],[.493,.305,.229]),.085);
  for(const f of digits){
   const h=f.to-f.from;
   const root=[f.x,f.from,f.z];
   const pip=[f.x+f.splay*.47,f.from+h*.60,f.z+.010];
   const dip=[f.x+f.splay*.78,f.from+h*.83,f.z+.014];
   const tip=[f.x+f.splay,f.to-.083,f.z+.018];
   // Pronounced tapered proximal, middle and distal phalanges. The joint
   // thickness changes continuously; proximal roots remain blended to palm.
   d=add(d,cap(p,root,pip,f.r*1.23,f.r*.91),.069);
   d=add(d,ell(p,pip,[f.r*.91,.079,f.r*.91]),.038);
   d=add(d,cap(p,pip,dip,f.r*.90,f.r*.74),.038);
   d=add(d,ell(p,dip,[f.r*.78,.060,f.r*.78]),.026);
   d=add(d,cap(p,dip,tip,f.r*.74,f.r*.58),.034);
   d=add(d,ell(p,tip,[f.r*.62,.087,f.r*.62]),.031);
  }
  // Root anchored BELOW index base, thumb turned forward and away from palm.
  // Smooth first metacarpal -> thumb MCP -> short distal thumb, without
  // filling the index-thumb web into a mitten.
  d=add(d,cap(p,[-.485,1.517,.111],[-.818,1.774,.182],.196,.139),.106);
  d=add(d,ell(p,[-.826,1.789,.187],[.144,.129,.145]),.058);
  d=add(d,cap(p,[-.820,1.785,.19],[-1.115,2.008,.231],.135,.093),.061);
  d=add(d,ell(p,[-1.117,2.014,.235],[.096,.104,.091]),.035);
  return d;
 };
}
function se216HandAnatomicalTrim({digits,wire,sphere,color}){
 // Trim follows the thinner three-dimensional outline; none of these
 // contours is a substitute for organic palm geometry.
 wire('Palm · thumb-pad contour',
  [[-.34,1.234,.278],[-.455,1.402,.314],[-.504,1.558,.314],[-.545,1.726,.255]],
  .011,color.seam,'silk','Palm / anatomy');
 wire('Palm · pinky-side flex crease',
  [[.345,1.250,.247],[.487,1.460,.259],[.531,1.652,.253],[.466,1.888,.218]],
  .011,color.seam,'silk','Palm / anatomy');
 wire('Ulnar · tapered edge piping',
  [[.397,1.161,-.082],[.514,1.360,-.097],[.582,1.601,-.104],[.579,1.831,-.126],[.508,2.043,-.127]],
  .014,color.rim,'metal','Ulnar / side armor');
 wire('Ulnar · inset purple seam',
  [[.402,1.30,-.160],[.526,1.51,-.181],[.550,1.757,-.169],[.489,1.968,-.164]],
  .011,color.accent,'emissive','Ulnar / side armor');
 for(const [i,f] of digits.entries()){
  const h=f.to-f.from,x=f.x+f.splay*.47,y=f.from+h*.60;
  wire('Finger '+(i+1)+' · proximal knuckle arc',
    [[x-f.r*.72,y,-.109],[x,y+.014,-.133],[x+f.r*.72,y,-.109]],
    .009,color.rim,'metal','Fingers / joints');
  wire('Finger '+(i+1)+' · palmar flex crease',
    [[x-f.r*.66,y-.033,.095],[x,y-.055,.112],[x+f.r*.66,y-.033,.095]],
    .008,color.seam,'silk','Fingers / joints');
 }
 sphere('Thumb · beveled saddle joint',[-.613,1.613,-.190],[.150,.132,.046],
   color.plate,'metal','Thumb / armor');
 wire('Thumb · root to wrist energy channel',
   [[-.440,1.315,-.203],[-.632,1.496,-.237],[-.760,1.667,-.160]],
   .013,color.accent,'emissive','Thumb / armor');
}
