// §E v11.302: UV-coherent surface depth for the refined Vanguard.
// Native texture art from v11.301 remains the ALBEDO source of truth.
// Corresponding, lightweight 256px tangent-space normal / roughness maps
// supply relief only where fabric, leather seams and armor engravings exist.
// IMPORTANT: no whole-image JPEG pasting, no new model parts, no new rig.
const se302Maps=new Map();
const se302SurfaceStatus={version:'v11.302',generatedMapFamilies:0,
 normalFamilies:0,roughnessFamilies:0,normalPixels:256,
 paintedUVConsistent:true,additionalGeometry:0,visualAcceptance:false};
const se302Config=Object.freeze({
 skin:{rough:.87,metal:0,normal:.02},
 hair:{rough:.79,metal:0,normal:.13},
 hood:{rough:.89,metal:0,normal:.19},
 scarf:{rough:.93,metal:0,normal:.17},
 uniform:{rough:.82,metal:.015,normal:.11},
 armor:{rough:.46,metal:.3,normal:.29},
 pauldron:{rough:.43,metal:.36,normal:.27},
 teal:{rough:.85,metal:0,normal:.22},
 leather:{rough:.82,metal:0,normal:.20},
 gloves:{rough:.90,metal:0,normal:.10},
 boots:{rough:.80,metal:.02,normal:.22}
});
function se302Height(family){
 const c=se300Canvas(256,256),ctx=c.getContext('2d');
 ctx.fillStyle='#808080';ctx.fillRect(0,0,256,256);
 const wave=(row,bend,color,width=2)=>{
  ctx.beginPath();ctx.moveTo(-15,row);
  ctx.bezierCurveTo(72,row+bend,173,row-bend,272,row+3);
  ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();
 };
 const outline=(inset,color,width=3)=>{
  ctx.strokeStyle=color;ctx.lineWidth=width;
  ctx.strokeRect(inset,inset,256-2*inset,256-2*inset);
 };
 if(family==='hood'||family==='scarf'||family==='uniform'||family==='teal'){
  const subtle=family==='uniform'?1.5:3;
  for(let y=22;y<260;y+=family==='scarf'?37:49){
   wave(y,7+(y%4), '#9a9a9a',subtle);
   wave(y+5,6,'#6f6f6f',subtle*.8);
  }
  if(family==='hood'||family==='teal'){
   outline(10,'#aeaeae',6);
   outline(15,'#737373',3);
  }
 }
 if(family==='armor'||family==='pauldron'){
  outline(9,'#b6b6b6',7);
  outline(17,'#656565',3);
  for(let n=0;n<3;n++){
   const y=61+n*48;
   ctx.beginPath();ctx.moveTo(26,y);
   ctx.quadraticCurveTo(122,y+22,128,y+23);
   ctx.quadraticCurveTo(157,y+21,230,y);
   ctx.strokeStyle='#a8a8a8';ctx.lineWidth=4.2;ctx.stroke();
   ctx.beginPath();ctx.moveTo(27,y+5);
   ctx.quadraticCurveTo(126,y+26,231,y+5);
   ctx.strokeStyle='#606060';ctx.lineWidth=2.4;ctx.stroke();
  }
 }
 if(family==='leather'||family==='boots'){
  for(let x=22;x<255;x+=54){
   ctx.beginPath();ctx.moveTo(x,0);ctx.bezierCurveTo(x-6,88,x+6,190,x,256);
   ctx.strokeStyle='#959595';ctx.lineWidth=1.6;ctx.stroke();
  }
  wave(224,8,'#9e9e9e',2.4);
 }
 if(family==='hair'){
  for(let x=13;x<255;x+=12){
   ctx.beginPath();ctx.moveTo(x,-5);
   ctx.bezierCurveTo(x+13,74,x-17,180,x+7,260);
   ctx.strokeStyle='#969696';ctx.lineWidth=1.4;ctx.stroke();
  }
 }
 if(family==='gloves'){
  for(let y=77;y<250;y+=47)wave(y,3,'#898989',1.7);
 }
 return c;
}
function se302BuildSet(family){
 if(se302Maps.has(family))return se302Maps.get(family);
 const spec=se302Config[family],size=256;
 if(!spec)throw Error('No matched PBR surface category '+family);
 const height=se302Height(family),
  raw=height.getContext('2d',{willReadFrequently:true}).getImageData(0,0,size,size).data,
  normal=se300Canvas(size,size),rough=se300Canvas(size,size);
 const nctx=normal.getContext('2d'),rctx=rough.getContext('2d'),
  nd=nctx.createImageData(size,size),rd=rctx.createImageData(size,size);
 const shade=spec.normal===0?0:.065;
 for(let y=0;y<size;y++)for(let x=0;x<size;x++){
  const k=(y*size+x)*4,il=(y*size+Math.max(0,x-1))*4,
   ir=(y*size+Math.min(size-1,x+1))*4,
   iu=(Math.max(0,y-1)*size+x)*4,
   id=(Math.min(size-1,y+1)*size+x)*4;
  const dx=(raw[ir]-raw[il])*shade,dy=(raw[id]-raw[iu])*shade;
  const len=Math.hypot(dx,dy,1);
  nd.data[k]=Math.round(127.5*(1-dx/len));
  nd.data[k+1]=Math.round(127.5*(1+dy/len));
  nd.data[k+2]=Math.round(127.5*(1+1/len));
  nd.data[k+3]=255;
  const grain=((Math.imul(x+17,73856093)^Math.imul(y+31,19349663))>>>0)%91/91-.5;
  // Roughness is MATERIAL response, not printed albedo/photographic shading.
  const val=Math.max(.05,Math.min(1,spec.rough+grain*.052+
   (raw[k]-128)*.00032));
  rd.data[k]=rd.data[k+1]=rd.data[k+2]=Math.round(255*val);rd.data[k+3]=255;
 }
 nctx.putImageData(nd,0,0);rctx.putImageData(rd,0,0);
 const ntex=new THREE.CanvasTexture(normal),rtex=new THREE.CanvasTexture(rough);
 for(const t of [ntex,rtex]){
  t.colorSpace=THREE.NoColorSpace;
  t.wrapS=t.wrapT=THREE.ClampToEdgeWrapping;
  t.minFilter=THREE.LinearMipmapLinearFilter;
  t.magFilter=THREE.LinearFilter;
  t.anisotropy=2;t.needsUpdate=true;
 }
 ntex.name='Vanguard native-UV raised seams / '+family;
 rtex.name='Vanguard native-UV micro roughness / '+family;
 const set={normal:ntex,roughness:rtex};
 se302Maps.set(family,set);
 se302SurfaceStatus.generatedMapFamilies=se302Maps.size;
 se302SurfaceStatus.normalFamilies=se302Maps.size;
 se302SurfaceStatus.roughnessFamilies=se302Maps.size;
 return set;
}
const se302PreviousHeroMaterial=se291HeroMaterial;
se291HeroMaterial=function(part){
 const mat=se302PreviousHeroMaterial(part),
  tag=part?.heroPBR?.tile;
 if(!tag?.startsWith('v300:'))return mat;
 const family=tag.slice(5),spec=se302Config[family],maps=se302BuildSet(family);
 mat.normalMap=maps.normal;
 mat.normalScale=new THREE.Vector2(spec.normal,spec.normal);
 mat.roughnessMap=maps.roughness;
 mat.roughness=1; // roughnessMap already contains per-surface response
 mat.metalness=spec.metal;
 mat.needsUpdate=true;
 return mat;
};
const se302PreviousHeroScene=se291HeroScene;
se291HeroScene=function(){
 const scene=se302PreviousHeroScene();
 scene.engine='§wyrl§ Engine · Maker v11.302';scene.version=11.302;
 scene.project.modelAtelier.name='Hooded Vanguard · Painted PBR Study';
 scene.project.name=scene.project.modelAtelier.name;
 scene.project.modelAtelier.reference=
  'v11.302 adds UV-matched normal and grayscale roughness maps to eleven native painted material families. Subtle cloth fold relief, engraved metal seams and leather micro grain enhance v11.301 face, hand pose and geometry. No image cutouts. Static; no bird, weapon or full rig.';
 return scene;
};
window.SWYRL_ENGINE_HOODED_VANGUARD=Object.freeze({
 id:'hooded-vanguard',open:se291OpenHero,createScene:se291HeroScene,
 status:()=>({...se291Stats,...se300Status,...se301Result,...se302SurfaceStatus,
  correctedHandAlignment:true,photographicCutoutTextures:false,
  nativeUVPBRMaps:true,editableParts:17,weapon:false,bird:false,rigged:false})
});
