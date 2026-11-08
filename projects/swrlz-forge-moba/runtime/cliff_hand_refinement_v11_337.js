// §E v11.337: photographic anatomy refinements and inlaid crystal geodes.
// ONLY the Smooth Cliff Hand uses these native SDF and CanvasTexture functions.
// Keep the v11.336 UV image guide, one mesh, 17 bones and original PBR maps.

const se337State={fieldBuilds:0,geodeTextures:0,shaderInstalls:0,
  crystalInlays:4,additionalGeometry:0,originalUVMap:true,
  lowerUlnarCurve:'feathered wrist transition',jointSmoothing:'round PIP/DIP/distal tips'};

function se337OrganicFingerSkin(digits,{ell,cap,blend}){
 const add=(a,b,k)=>blend(a,b,k);
 return (x,y,z)=>{
  const p=[x,y,z];
  // Keep the original v11.217 anatomical palms and both thumb joints
  // unchanged. Change only the four finger transition radii and tips.
  let d=ell(p,[.002,1.765,-.013],[.573,.497,.266]);
  d=add(d,ell(p,[-.007,2.067,-.021],[.540,.291,.237]),.130);
  d=add(d,ell(p,[.004,1.299,-.009],[.363,.445,.224]),.156);
  d=add(d,ell(p,[-.335,1.498,.074],[.258,.346,.257]),.123);
  d=add(d,ell(p,[-.515,1.625,.104],[.214,.280,.233]),.106);
  d=add(d,ell(p,[.363,1.495,.024],[.191,.351,.222]),.115);
  d=add(d,ell(p,[.411,1.871,-.019],[.152,.270,.210]),.088);
  d=add(d,ell(p,[.016,1.89,-.076],[.493,.305,.229]),.085);
  for(const f of digits){
   const h=f.to-f.from;
   const root=[f.x,f.from,f.z];
   const pip=[f.x+f.splay*.47,f.from+h*.60,f.z+.010];
   const dip=[f.x+f.splay*.78,f.from+h*.83,f.z+.014];
   const tip=[f.x+f.splay,f.to-.083,f.z+.018];
   // Longer, overlapping smooth blends remove the stacked capsule/joint
   // ridges at mid-fingers while preserving their slender taper.
   d=add(d,cap(p,root,pip,f.r*1.20,f.r*.92),.102);
   d=add(d,ell(p,pip,[f.r*.94,.080,f.r*.94]),.075);
   d=add(d,cap(p,pip,dip,f.r*.91,f.r*.77),.078);
   d=add(d,ell(p,dip,[f.r*.79,.068,f.r*.79]),.067);
   d=add(d,cap(p,dip,tip,f.r*.76,f.r*.62),.070);
   // Rounded fingertip pads replace the visibly chiseled terminal tips.
   d=add(d,ell(p,tip,[f.r*.67,.099,f.r*.67]),.066);
  }
  d=add(d,cap(p,[-.485,1.517,.111],[-.818,1.774,.182],.196,.139),.106);
  d=add(d,ell(p,[-.826,1.789,.187],[.144,.129,.145]),.058);
  d=add(d,cap(p,[-.820,1.785,.19],[-1.115,2.008,.231],.135,.093),.061);
  d=add(d,ell(p,[-1.117,2.014,.235],[.096,.104,.091]),.035);
  return d;
 };
}

function se337HandField(math){
 // v11.335 already narrows the pinky-side palm. Preserve that shape,
 // original thenar/thumb pad, and old metacarpal/finger joint positions.
 const original=se335NarrowUlnarField(math,se337OrganicFingerSkin);
 const smooth=(a,b,x)=>{
  const t=Math.max(0,Math.min(1,(x-a)/(b-a)));
  return t*t*(3-2*t);
 };
 se337State.fieldBuilds++;
 return (x,y,z)=>{
  // Owner close-up: at the heel of the palm the ulnar side still sticks
  // out as a lump before connecting to the wrist. Move its outer SDF
  // sample inward progressively at the palm heel, then fade seamlessly
  // before the pinky MCP. Do not clip the surface or add any object.
  const wristJoin=smooth(1.10,1.33,y);
  const palmHeel=1-smooth(1.37,1.65,y);
  const pinkyEdge=smooth(.03,.44,x);
  const lowerInward=.110*wristJoin*palmHeel*pinkyEdge;
  return original(x+lowerInward,y,z);
 };
}

// Faceted aqua / jade geodes inset in a shadowed mineral socket.
// Unlike the v11.334 upright spike stencil, these are low-profile,
// varied knuckle inlays with stone lips, internal crystal facets,
// colored edge reflections and tiny luminous imperfections.
let se337InlayTexture=null;
function se337PaintGeode(ctx,k,i){
 const cx=k.u*384,cy=(1-k.v)*384+1;
 const sizes=[.89,1.07,.98,.78];
 const palettes=[
  ['#91e6d4','#43bcae','#1d677f'],
  ['#abfff0','#40c5ce','#15598a'],
  ['#84f4e2','#35b5b4','#185b78'],
  ['#a1e9fd','#4aa9ce','#244f81']
 ];
 const [light,mid,dark]=palettes[i];
 ctx.save();ctx.translate(cx,cy);ctx.rotate(k.twist*.66);
 ctx.scale(sizes[i],sizes[i]);

 // Rock socket silhouette: uneven slate lip, dark natural depth and
 // a narrow jade mineral halo within the actual knuckle UV region.
 const lip=[[-25,-2],[-19,-10],[-7,-12],[4,-10],[17,-9],[24,-1],
            [23,7],[12,11],[-4,12],[-18,8]];
 const path=(pts)=>{ctx.beginPath();pts.forEach(([x,y],n)=>
   n?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();};
 ctx.save();ctx.shadowColor='rgba(2,20,26,.54)';ctx.shadowBlur=3;
 ctx.shadowOffsetY=2;path(lip);ctx.fillStyle='rgba(18,36,38,.82)';ctx.fill();ctx.restore();
 path(lip);ctx.strokeStyle='rgba(6,24,34,.87)';ctx.lineWidth=1.6;ctx.stroke();

 const inner=ctx.createLinearGradient(-12,-11,15,10);
 inner.addColorStop(0,'rgba(4,39,52,.93)');
 inner.addColorStop(.45,'rgba(14,72,76,.80)');
 inner.addColorStop(1,'rgba(23,46,59,.90)');
 ctx.beginPath();ctx.ellipse(0,0,20,7.7,-.08,0,Math.PI*2);
 ctx.fillStyle=inner;ctx.fill();

 // Two small satellites and a broader hex-cut central crystal, with
 // different orientations rather than four identical cyan spike brushes.
 const shapes=i===0
  ? [{x:-11,y:1,w:8,h:11,tilt:-2},{x:0,y:-1,w:12,h:17,tilt:2},{x:12,y:2,w:7,h:9,tilt:1}]
  :i===1
  ? [{x:-12,y:1,w:7,h:10,tilt:-2},{x:0,y:-2,w:13,h:19,tilt:0},{x:12,y:2,w:9,h:12,tilt:2}]
  :i===2
  ? [{x:-13,y:2,w:7,h:9,tilt:-3},{x:-1,y:-2,w:12,h:18,tilt:1},{x:12,y:1,w:8,h:11,tilt:3}]
  : [{x:-8,y:1,w:7,h:11,tilt:-2},{x:2,y:-1,w:11,h:16,tilt:2}];

 for(const [j,s] of shapes.entries()){
  const X=s.x,Y=s.y,W=s.w,H=s.h;
  const poly=[
   [X-W*.49,Y+H*.37],[X-W*.54,Y-H*.18],
   [X+s.tilt-W*.15,Y-H*.53],[X+s.tilt+W*.27,Y-H*.55],
   [X+W*.54,Y-H*.12],[X+W*.52,Y+H*.34],
   [X+W*.10,Y+H*.50]
  ];
  path(poly);
  const g=ctx.createLinearGradient(X-W,Y-H*.5,X+W,Y+H*.5);
  g.addColorStop(0,light);g.addColorStop(.33,mid);
  g.addColorStop(.75,dark);g.addColorStop(1,'#102e4c');
  ctx.fillStyle=g;ctx.fill();
  ctx.strokeStyle='rgba(9,31,50,.95)';ctx.lineWidth=1;ctx.stroke();
  // Dark side facet and bright cut facet read as depth under light.
  path([poly[3],poly[4],poly[5],[X+W*.05,Y+H*.38]]);
  ctx.fillStyle='rgba(8,31,60,.39)';ctx.fill();
  path([poly[0],poly[1],poly[2],[X-W*.09,Y+H*.12]]);
  ctx.fillStyle='rgba(201,255,244,.40)';ctx.fill();
  ctx.beginPath();ctx.moveTo(...poly[3]);ctx.lineTo(X+W*.05,Y+H*.38);
  ctx.strokeStyle='rgba(180,255,241,.63)';ctx.lineWidth=.72;ctx.stroke();
  ctx.beginPath();ctx.moveTo(X-W*.34,Y-H*.12);ctx.lineTo(X+s.tilt-W*.15,Y-H*.47);
  ctx.strokeStyle='rgba(245,255,255,.88)';ctx.lineWidth=j===1?1.15:.8;ctx.stroke();
 }
 // Broken mineral veins tether the geode to the stone, not floating tips.
 ctx.beginPath();ctx.moveTo(-24,0);ctx.lineTo(-28,3);ctx.moveTo(22,3);
 ctx.lineTo(27,5);ctx.moveTo(4,11);ctx.lineTo(6,16);
 ctx.strokeStyle='rgba(19,94,109,.65)';ctx.lineWidth=1.05;ctx.stroke();
 ctx.fillStyle='rgba(221,255,251,.84)';
 for(const [dx,dy,r] of [[-6,-5,.8],[5,-3,.85],[13,4,.48]]){
  ctx.beginPath();ctx.arc(dx,dy,r,0,Math.PI*2);ctx.fill();
 }
 ctx.restore();
}
function se337GeodeTexture(){
 if(se337InlayTexture)return se337InlayTexture;
 const canvas=document.createElement('canvas');
 canvas.width=canvas.height=384;
 const ctx=canvas.getContext('2d');
 if(!ctx)throw Error('Cliff Hand geode texture context unavailable');
 ctx.clearRect(0,0,384,384);
 se292Knuckles.forEach((k,i)=>se337PaintGeode(ctx,k,i));
 const tex=new THREE.CanvasTexture(canvas);
 tex.colorSpace=THREE.SRGBColorSpace;
 tex.wrapS=tex.wrapT=THREE.ClampToEdgeWrapping;
 tex.minFilter=THREE.LinearMipmapLinearFilter;
 tex.magFilter=THREE.LinearFilter;
 tex.anisotropy=2;
 tex.needsUpdate=true;
 se337InlayTexture=tex;
 se337State.geodeTextures++;
 return tex;
}
function se337DorsalGeodeMaterial(mat){
 const geode=se337GeodeTexture();
 mat.onBeforeCompile=(shader)=>{
  shader.uniforms.se337CrystalAtlas={value:geode};
  const normalKey='#include <beginnormal_vertex>';
  const colorKey='#include <map_fragment>';
  const roughKey='#include <roughnessmap_fragment>';
  const emissiveKey='#include <emissivemap_fragment>';
  for(const key of [normalKey,colorKey,roughKey,emissiveKey]){
   if(!shader.vertexShader.includes(key)&&!shader.fragmentShader.includes(key))
    throw Error('Smooth Cliff geode shader missing expected PBR hook '+key);
  }
  shader.vertexShader='varying float se337Dorsal;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace(normalKey,normalKey+
    '\n se337Dorsal=smoothstep(0.25,0.68,-objectNormal.z);');
  shader.fragmentShader='varying float se337Dorsal;\nuniform sampler2D se337CrystalAtlas;\n'+
    shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace(colorKey,colorKey+
    '\n vec4 se337Gem=texture2D(se337CrystalAtlas,vMapUv);'+
    '\n float se337Coverage=clamp(se337Gem.a*se337Dorsal,0.0,1.0);'+
    '\n diffuseColor.rgb=mix(diffuseColor.rgb,se337Gem.rgb,se337Coverage);');
  // Physical material contrast: smooth gem, rough stone socket, restrained glow.
  shader.fragmentShader=shader.fragmentShader.replace(roughKey,roughKey+
    '\n roughnessFactor=mix(roughnessFactor,0.19,se337Coverage*0.86);');
  shader.fragmentShader=shader.fragmentShader.replace(emissiveKey,emissiveKey+
    '\n totalEmissiveRadiance+=se337Gem.rgb*(se337Coverage*0.085);');
  se337State.shaderInstalls++;
 };
 mat.customProgramCacheKey=()=> 'se337-inlaid-dorsal-geodes-v1';
 mat.name='Cliff Hand · organic smooth fingers / inlaid faceted crystal knuckles';
 mat.userData.se337GeodeInlays=4;
 mat.userData.se337CrystalOnlyDorsal=true;
 mat.needsUpdate=true;
 return mat;
}
window.SWYRL_ENGINE_CLIFF_HAND_337=Object.freeze({
 status:()=>({...se337State,geodeTextureReady:!!se337InlayTexture,
   material:'dorsal-inlaid-PBR;polished-facets;rough-stone;no palm bleed',
   geometry:'one connected photo-refined hand+gauntlet',
   referenceImagesStored:false})
});
