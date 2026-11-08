// §E v11.334 — user's left-palm photo: proportion study and dorsal-only crystal knuckles.
// A single connected hand/gauntlet surface. Existing rig + rock atlas remain native.
// Z+ is the PALM; Z- is the BACK. No transparent rock/cystal objects inside the palm.
const se334State={crystalMaps:0,shaderInstalls:0,photoShapeApplied:0,
   crystalKnuckles:4,palmKnucklePaintRemoved:true,extraMeshObjects:0};
function se334ReferenceHandField(math){
 const photoDigits=se217FingerSpec.map(d=>({...d}));
 // Photo: middle longest; softly tapered index/ring; naturally shorter pinky.
 // Stay close to existing joint origins and rest pose so 17-bone LBS still fits.
 const length={index:.026,middle:.037,ring:.020,pinky:.023};
 const splay={index:-.012,middle:-.003,ring:.005,pinky:.011};
 for(const d of photoDigits){d.to+=length[d.name];d.splay+=splay[d.name];}
 const skin=se217OrganicHandSkin(photoDigits,math);
 const smooth=(a,b,x)=>{const t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t)};
 se334State.photoShapeApplied++;
 return (x,y,z)=>{
  // Photo has a broader metacarpal palm and more substantial thumb root,
  // but keeps tapered wrist, finger web valleys and joint geometry intact.
  const palmBand=smooth(1.25,1.52,y)*(1-smooth(2.02,2.27,y));
  const shapedX=x*(1-.035*palmBand);
  let d=skin(shapedX,y,z);
  const pad=math.ell([x,y,z],[-.352,1.57,.100],[.261,.321,.259]);
  d=math.blend(d,pad,.056);
  return d;
 };
}
const se334Crystals=se292Knuckles.map((k,i)=>({...k,index:i}));
let se334Layer=null;
function se334PaintCrystal(ctx,k){
 const x=k.u*384,y=(1-k.v)*384;
 const s=[.83,1.05,.91,.70][k.index];
 ctx.save();ctx.translate(x,y);ctx.rotate(k.twist);ctx.scale(s,s);
 // A stony socket and teal veins are COLOR, not an object penetrating the hand.
 const halo=ctx.createRadialGradient(0,0,2,0,0,29);
 halo.addColorStop(0,'rgba(19,94,94,.74)');
 halo.addColorStop(.54,'rgba(18,83,86,.36)');
 halo.addColorStop(1,'rgba(18,84,82,0)');
 ctx.fillStyle=halo;ctx.beginPath();ctx.ellipse(0,0,28,20,0,0,Math.PI*2);ctx.fill();
 // Faceted mineral crystals centered on each dorsal metacarpophalangeal joint.
 // Closed silhouettes, separate lit and shaded planes, glass-like sharp glints.
 const facets=[
  {dx:-12,dy:5,w:8,h:13,lean:-3},
  {dx:0,dy:1,w:11,h:22,lean:1},
  {dx:12,dy:6,w:8,h:12,lean:3},
  {dx:5,dy:10,w:5,h:8,lean:2}
 ];
 for(const [j,f] of facets.entries()){
  const bottom=f.dy+f.h*.46,tip=f.dy-f.h*.62;
  ctx.beginPath();
  ctx.moveTo(f.dx-f.w*.58,bottom);
  ctx.lineTo(f.dx-f.w*.48,f.dy-f.h*.12);
  ctx.lineTo(f.dx+f.lean,tip);
  ctx.lineTo(f.dx+f.w*.48,f.dy-f.h*.08);
  ctx.lineTo(f.dx+f.w*.53,bottom-1);
  ctx.closePath();
  const gradient=ctx.createLinearGradient(f.dx-f.w,tip,f.dx+f.w,bottom);
  gradient.addColorStop(0,'rgba(141,255,232,.95)');
  gradient.addColorStop(.34,'rgba(40,204,188,.92)');
  gradient.addColorStop(.77,'rgba(13,99,124,.90)');
  gradient.addColorStop(1,'rgba(9,53,72,.92)');
  ctx.fillStyle=gradient;ctx.fill();
  ctx.lineWidth=1.1;ctx.strokeStyle='rgba(7,48,66,.95)';ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(f.dx+f.lean,tip);
  ctx.lineTo(f.dx+f.w*.05,bottom);
  ctx.lineTo(f.dx-f.w*.48,f.dy-f.h*.12);
  ctx.closePath();ctx.fillStyle='rgba(154,255,236,.31)';ctx.fill();
  ctx.beginPath();ctx.moveTo(f.dx+f.lean,tip);
  ctx.lineTo(f.dx+f.w*.05,bottom);
  ctx.strokeStyle='rgba(194,255,247,.73)';ctx.lineWidth=j===1?1.35:.8;ctx.stroke();
 }
 // Small refractive-looking highlights, kept inside knuckle rather than palm.
 ctx.fillStyle='rgba(225,255,245,.82)';
 for(const [dx,dy,r] of [[-4,-10,1.15],[8,-3,.9],[-13,7,.7]]){
  ctx.beginPath();ctx.arc(dx,dy,r,0,Math.PI*2);ctx.fill();
 }
 ctx.restore();
}
function se334CrystalTexture(){
 if(se334Layer)return se334Layer;
 const canvas=document.createElement('canvas');
 canvas.width=canvas.height=384;
 const ctx=canvas.getContext('2d');
 if(!ctx)throw Error('Dorsal knuckle crystal material canvas unavailable');
 ctx.clearRect(0,0,384,384);
 for(const k of se334Crystals)se334PaintCrystal(ctx,k);
 const tex=new THREE.CanvasTexture(canvas);
 tex.colorSpace=THREE.SRGBColorSpace;
 tex.wrapS=tex.wrapT=THREE.ClampToEdgeWrapping;
 tex.minFilter=THREE.LinearMipmapLinearFilter;
 tex.magFilter=THREE.LinearFilter;
 tex.anisotropy=2;
 tex.needsUpdate=true;
 se334Layer=tex;
 se334State.crystalMaps++;
 return tex;
}
function se334DorsalOnlyCrystalMaterial(mat){
 const crystal=se334CrystalTexture();
 mat.onBeforeCompile=(shader)=>{
  shader.uniforms.se334CrystalAtlas={value:crystal};
  const vertAnchor='#include <beginnormal_vertex>';
  const fragAnchor='#include <map_fragment>';
  if(!shader.vertexShader.includes(vertAnchor)||!shader.fragmentShader.includes(fragAnchor))
   throw Error('Cliff Hand dorsal crystal shader missing expected Three.js shader hooks');
  shader.vertexShader='varying float se334DorsalWeight;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace(vertAnchor,
    vertAnchor+'\n se334DorsalWeight = smoothstep(0.13, 0.67, -objectNormal.z);');
  shader.fragmentShader='varying float se334DorsalWeight;\nuniform sampler2D se334CrystalAtlas;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace(fragAnchor,
    fragAnchor+'\n vec4 se334Facet = texture2D(se334CrystalAtlas, vMapUv);\n'+
    ' diffuseColor.rgb = mix(diffuseColor.rgb, se334Facet.rgb, se334Facet.a * se334DorsalWeight);');
  se334State.shaderInstalls++;
 };
 mat.customProgramCacheKey=()=> 'se334-dorsal-crystals-v1';
 mat.name='Smooth Cliff · photo-refined stone + dorsal-only teal crystal knuckles';
 mat.userData.se334DorsalCrystal=true;
 mat.userData.se334CrystalSource='canvas-texture-dorsal-only';
 mat.needsUpdate=true;
 return mat;
}
window.SWYRL_ENGINE_CLIFF_HAND_334=Object.freeze({
 status:()=>({...se334State,crystalTextureReady:!!se334Layer,
   materialMode:'dorsal-normal-masked;palmar-rock-only',
   photoReference:'user-supplied left palm photograph'})
});
