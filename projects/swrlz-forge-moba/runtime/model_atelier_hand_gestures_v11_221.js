// §E v11.221 — hand articulation and distinct authored gesture targets.
// All joints use the existing named THREE.Bone hierarchy, skinning and native
// saved animation timeline. Thumb has its own opposable CMC/MCP/IP movement.
// Rig-neutral geometry, old saves and other models remain untouched.
const se221Gestures=Object.freeze([
 ['open','Open palm'],['relaxed','Relaxed hand'],['fist','Fist'],
 ['point','Point'],['pinch','Precision pinch'],['ok','OK sign'],
 ['thumbs-up','Thumbs up'],['peace','Peace / V'],['horns','Rock horns'],
 ['ily','I love you'],['shaka','Shaka / call me'],['wave','Wave / spread'],
 ['grab','Grasp'],['finger-gun','Finger gun']
]);
function se221GesturePose(rig,kind){
 const pose=Object.fromEntries(rig.bones.map(b=>[b.id,[0,0,0]]));
 const digit=(name,mcp=0,pip=0,dip=0,spread=0)=>{
  pose[name+'_mcp']=[mcp,0,spread];
  pose[name+'_pip']=[pip,0,0];pose[name+'_dip']=[dip,0,0];
 };
 const thumb=(cmc=[0,0,0],mcp=[0,0,0],ip=[0,0,0])=>{
  pose.thumb_cmc=cmc.slice();pose.thumb_mcp=mcp.slice();pose.thumb_ip=ip.slice();
 };
 const curl=(names,mcp=.81,pip=1.03,dip=.56)=>{
  for(const name of names)digit(name,mcp,pip,dip);
 };
 switch(kind){
  case 'open':
   break;
  case 'relaxed':
   digit('index',.13,.18,.08,.04);digit('middle',.17,.19,.10,.015);
   digit('ring',.21,.27,.12,-.017);digit('pinky',.23,.32,.16,-.06);
   thumb([.04,.18,-.10],[.08,.01,.03],[.06,0,.03]);break;
  case 'fist':
   curl(['index','middle','ring','pinky'],.88,1.10,.63);
   // Cross the thumb IN FRONT of the folded fingers, rather than
   // pivoting every thumb phalanx around a single sideways axis.
   thumb([.29,1.02,-.37],[.17,.12,.05],[.14,.01,.10]);break;
  case 'point':
   curl(['middle','ring','pinky'],.86,1.06,.55);
   digit('index',0,.02,.02,.02);
   thumb([.20,.72,-.27],[.15,.05,.08],[.06,0,.04]);break;
  case 'pinch':
   digit('index',.95,1.10,.50,.0);
   digit('middle',.28,.40,.17,.01);
   digit('ring',.30,.43,.19,-.02);
   digit('pinky',.30,.44,.21,-.04);
   // Calibrated against the indexed model's distal position:
   // thumb and index fingertips approach within ~0.03 model units.
   thumb([.33,1.20,-.44],[.09,.13,-.05],[.06,-.04,-.07]);break;
  case 'ok':
   digit('index',.95,1.10,.50,0);
   digit('middle',.08,.09,.07,-.065);
   digit('ring',.09,.11,.05,-.025);
   digit('pinky',.08,.09,.05,.065);
   thumb([.33,1.20,-.44],[.09,.13,-.05],[.06,-.04,-.07]);break;
  case 'thumbs-up':
   curl(['index','middle','ring','pinky'],.91,1.04,.57);
   // This CMC Z rotation stands the anatomical thumb almost upright.
   thumb([0,.10,-1.12],[0,0,-.15],[0,0,.02]);break;
  case 'peace':
   digit('index',.015,.04,.025,.13);
   digit('middle',.015,.04,.025,-.11);
   curl(['ring','pinky'],.89,1.06,.58);
   thumb([.20,.82,-.27],[.11,.04,.06],[.05,0,.03]);break;
  case 'horns':
   digit('index',0,.02,.02,.05);
   digit('pinky',0,.04,.02,-.075);
   curl(['middle','ring'],.87,1.04,.56);
   thumb([.25,.85,-.30],[.15,.05,.08],[.06,0,.04]);break;
  case 'ily':
   digit('index',0,.02,.02,.04);
   digit('pinky',0,.03,.02,-.09);
   curl(['middle','ring'],.87,1.04,.56);
   thumb([0,.12,-1.00],[.03,0,-.07],[0,0,0]);break;
  case 'shaka':
   curl(['index','middle','ring'],.86,1.04,.54);
   digit('pinky',.02,.04,.01,-.14);
   thumb([0,.08,-1.10],[0,0,-.08],[0,0,.01]);break;
  case 'wave':
   digit('index',.08,.10,.04,.16);
   digit('middle',.05,.08,.04,.055);
   digit('ring',.06,.10,.04,-.045);
   digit('pinky',.06,.10,.04,-.16);
   pose.wrist=[0,0,.13];
   thumb([.07,.14,-.34],[.03,0,-.02],[.02,0,0]);break;
  case 'grab':
   digit('index',.52,.66,.30,.03);
   digit('middle',.53,.68,.30,.015);
   digit('ring',.58,.72,.34,-.02);
   digit('pinky',.60,.76,.37,-.05);
   thumb([.20,.77,-.33],[.16,.05,.17],[.11,0,.19]);break;
  case 'finger-gun':
   digit('index',0,.01,0,.04);
   curl(['middle','ring','pinky'],.87,1.03,.56);
   thumb([0,.11,-1.06],[0,0,-.10],[0,0,.02]);break;
  default:
   return pose;
 }
 return pose;
}
// Replace legacy gesture handler while retaining the exported function and
// the v11.220 keyframe/store protocol, so existing saved clips remain valid.
function se221ThumbInfluences(pt,rig){
 const [x,y,z]=pt;
 const lines=[
  [[-.515,1.53,.11],[-.818,1.785,.19]],
  [[-.818,1.785,.19],[-1.005,1.94,.22]],
  [[-1.005,1.94,.22],[-1.117,2.014,.235]]
 ];
 let nearest=Infinity,along=0;
 for(let i=0;i<lines.length;i++){
  const [a,b]=lines[i],d=b.map((v,k)=>v-a[k]);
  const dd=d.reduce((v,w)=>v+w*w,0)||1;
  const t=se220Clamp(d.reduce((sum,w,k)=>sum+w*(pt[k]-a[k]),0)/dd);
  const gap=Math.hypot(...a.map((v,k)=>pt[k]-v-t*d[k]));
  if(gap<nearest){nearest=gap;along=(i+t)/3;}
 }
 // Keep the thumb saddle welded to the thenar/palm while extending ownership
 // to the decorative helix and the tapered distal tip; never skin index web.
 const radial=1-se220Smooth((nearest-.115)/.22);
 const side=se220Smooth((-.46-x)/.27);
 const rise=se220Smooth((y-1.435)/.22);
 const mix=se220Clamp(radial*side*rise);
 const mid=se220Smooth((along-.24)/.25),tip=se220Smooth((along-.59)/.22);
 return {mix,links:[
  ['thumb_cmc',mix*(1-mid)],
  ['thumb_mcp',mix*mid*(1-tip)],
  ['thumb_ip',mix*mid*tip]
 ]};
}
