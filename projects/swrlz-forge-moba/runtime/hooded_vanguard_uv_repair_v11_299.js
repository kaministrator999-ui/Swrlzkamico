// §E v11.299 — correct the verified v11.298 concept-sheet UV accident.
// Reuse the EXACT embedded JPEG pixels, but separate usable painted regions
// from their presentation-sheet whitespace. Per-material artwork canvases map
// to the part's original local UVs, not a 4x3 tile of illustrated cut-outs.
const se299Regions=Object.freeze({
 // source crop coordinates are *within* the genuine 128px atlas tile.
 // These rectangles select painted materials, never captions/preview columns.
 skin:{crop:[.08,.06,.84,.91],base:'#caa38f',rough:.88,metal:0},
 hair:{crop:[.11,.06,.58,.76],base:'#382b25',rough:.76,metal:0},
 hood:{crop:[.24,.06,.51,.69],base:'#e2ded6',rough:.91,metal:0},
 scarf:{crop:[.06,.05,.50,.70],base:'#e5e5e2',rough:.92,metal:0},
 uniform:{crop:[.14,.14,.29,.65],base:'#404951',rough:.83,metal:0},
 armor:{crop:[.04,.04,.48,.79],base:'#434f59',rough:.56,metal:.14},
 pauldron:{crop:[.03,.05,.34,.31],base:'#5d6267',rough:.52,metal:.19},
 teal:{crop:[.22,.12,.42,.78],base:'#146f75',rough:.83,metal:0},
 leather:{crop:[.15,.04,.62,.16],base:'#4b342b',rough:.86,metal:0},
 gloves:{crop:[.24,.12,.33,.70],base:'#e7e6e3',rough:.88,metal:0},
 boots:{crop:[.54,.12,.35,.71],base:'#413932',rough:.83,metal:.03}
});
const se299ImageResolution=256;
const se299MaterialCanvases=new Map();
const se299MaterialTextures=new Map();
const se299State={imageLoaded:false,imageError:null,atlasCorrected:0,restoredLocalUVVertices:0,paintedFamilies:0};
function se299Canvas(w=se299ImageResolution,h=se299ImageResolution){
 const c=document.createElement('canvas');c.width=w;c.height=h;return c;
}
function se299ExtractImage(image,family){
 const def=se299Regions[family],location=se298AtlasLayout[family],out=se299Canvas();
 if(!def||!location)throw Error('Invalid vanguard material artwork region '+family);
 const ctx=out.getContext('2d',{willReadFrequently:family==='skin'});
 ctx.fillStyle=def.base;ctx.fillRect(0,0,out.width,out.height);
 const [cx,cy,cw,ch]=def.crop;
 const sx=(location[0]+cx)*128,sy=(location[1]+cy)*128,sw=cw*128,sh=ch*128;
 if(family==='skin'){
  // The original image contains a *front* face only. Stamp it on the frontal
  // longitude and keep the rear/side mesh neutral skin — never wrap a second
  // mouth and eye around the back of the skull.
  const patch=se299Canvas(164,224),p=patch.getContext('2d',{willReadFrequently:true});
  p.drawImage(image,sx,sy,sw,sh,0,0,patch.width,patch.height);
  const pixels=p.getImageData(0,0,patch.width,patch.height);
  for(let y=0;y<patch.height;y++)for(let x=0;x<patch.width;x++){
   const k=(y*patch.width+x)*4,edgeX=Math.min(x,patch.width-1-x)/18,
    edgeY=Math.min(y,patch.height-1-y)/20;
   pixels.data[k+3]=255*Math.max(0,Math.min(1,edgeX,edgeY));
  }
  p.putImageData(pixels,0,0);
  ctx.drawImage(patch,49,16,158,224);
 }else{
  // Sample actual *surface* material pixels rather than a whole illustrated
  // garment including its empty background and neighboring cut-outs.
  // The artwork is mirrored for reduced obvious JPEG repetition.
  const tile=se299Canvas(128,128),tc=tile.getContext('2d');
  tc.fillStyle=def.base;tc.fillRect(0,0,128,128);
  tc.drawImage(image,sx,sy,sw,sh,0,0,128,128);
  // Remove presentation-paper holes only on dark materials. Do not erase
  // naturally pale hood, scarf or white gloves.
  if(!['hood','scarf','gloves'].includes(family)){
   const data=tc.getImageData(0,0,128,128),px=data.data;
   const rgb=def.base.match(/[a-f0-9]{2}/gi).map(x=>parseInt(x,16));
   for(let k=0;k<px.length;k+=4){
    const r=px[k],g=px[k+1],b=px[k+2],
      pale=r>220&&g>215&&b>207&&Math.max(r,g,b)-Math.min(r,g,b)<42;
    if(pale){px[k]=rgb[0];px[k+1]=rgb[1];px[k+2]=rgb[2];}
   }
   tc.putImageData(data,0,0);
  }
  for(let yi=0;yi<2;yi++)for(let xi=0;xi<2;xi++){
   ctx.save();ctx.translate(xi*128,yi*128);
   if(xi===1){ctx.translate(128,0);ctx.scale(-1,1);}
   if(yi===1){ctx.translate(0,128);ctx.scale(1,-1);}
   ctx.drawImage(tile,0,0,128,128);
   ctx.restore();
  }
 }
 return out;
}
let se299Source=null;
function se299InitImage(){
 if(se299Source)return;
 const img=new Image();se299Source=img;
 img.onload=()=>{
  try{
   for(const family of Object.keys(se299Regions)){
    const canvas=se299ExtractImage(img,family);
    se299MaterialCanvases.set(family,canvas);
    const texture=se299MaterialTextures.get(family);
    if(texture){texture.image=canvas;texture.needsUpdate=true;}
   }
   se299State.imageLoaded=true;se299State.imageError=null;
   se299State.paintedFamilies=se299MaterialCanvases.size;
  }catch(error){
   se299State.imageError=String(error?.message||error);
   console.error('Vanguard region-aligned source artwork',error);
  }
 };
 img.onerror=e=>{
  se299State.imageError=String(e?.message||'Original art image unavailable');
  console.error('Vanguard original art image unavailable',e);
 };
 img.src=se298AtlasDataURL; // Exact image bytes already sealed in v11.298.
}
function se299Material(family){
 let texture=se299MaterialTextures.get(family);
 const def=se299Regions[family];
 if(!def)throw Error('Missing vanguard material '+family);
 if(!texture){
  const canvas=se299Canvas();
  const ctx=canvas.getContext('2d');ctx.fillStyle=def.base;
  ctx.fillRect(0,0,canvas.width,canvas.height);
  texture=new THREE.CanvasTexture(canvas);
  texture.name='Vanguard real artwork / local UV / '+family;
  texture.colorSpace=THREE.SRGBColorSpace;
  texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;
  texture.minFilter=THREE.LinearMipmapLinearFilter;
  texture.magFilter=THREE.LinearFilter;
  texture.anisotropy=2;
  se299MaterialTextures.set(family,texture);
 }
 se299InitImage();
 return new THREE.MeshStandardMaterial({
  name:'Actual cropped painted '+family,
  map:texture,color:'#ffffff',roughness:def.rough,
  metalness:def.metal,side:THREE.DoubleSide
 });
}
const se299PreviousHeroMaterial=se291HeroMaterial;
se291HeroMaterial=function(part){
 const tag=part.heroPBR?.tile;
 if(typeof tag!=='string'||!tag.startsWith('v299:'))
  return se299PreviousHeroMaterial(part);
 return se299Material(tag.slice(5));
};
const se299PreviousHeroScene=se291HeroScene;
se291HeroScene=function(){
 const scene=se299PreviousHeroScene();
 const model=scene?.project?.modelAtelier;
 if(!model||model.parts.length!==17)throw Error('Expected 17-part image-backed Vanguard');
 const gutter=1.5/128,span=1-2*gutter;
 let verts=0;
 for(const part of model.parts){
  const tag=part.heroPBR?.tile;
  if(typeof tag!=='string'||!tag.startsWith('v298:'))
   throw Error('Unexpected previous UV format for '+part.name);
  const family=tag.slice(5),loc=se298AtlasLayout[family];
  const uv=part.topologyMesh?.uvs;
  if(!loc||!Array.isArray(uv))throw Error('Missing native image UVs '+part.name);
  for(let i=0;i<uv.length;i+=2){
   const oldU=uv[i],oldV=uv[i+1];
   // Undo the precise v11.298 4x3 mosaic mapping and recover the original
   // part-local [0..1] UV positions. This is NOT a new geometric projection.
   const u=(oldU*4-loc[0]-gutter)/span;
   const v=(oldV*3-(2-loc[1])-gutter)/span;
   if(!Number.isFinite(u)||!Number.isFinite(v)||
       u<-.002||u>1.002||v<-.002||v>1.002)
    throw Error('UV restoration out of bounds '+part.name);
   uv[i]=+Math.max(0,Math.min(1,u)).toFixed(6);
   uv[i+1]=+Math.max(0,Math.min(1,v)).toFixed(6);
   verts++;
  }
  part.heroPBR={
   ...part.heroPBR,tile:'v299:'+family,
   source:'actual-original-image-regions',
   sourceSha256:se298AtlasMetadata.jpegSha256,
   coordinates:'native-local-uv-restored',
   region:se299Regions[family].crop
  };
 }
 model.name='Hooded Vanguard · Corrected Real Image UV';
 model.reference='v11.299: extracted real surface regions of the generated reference image, not illustrated cutout tiles. Local UVs restored per part; front-only facial artwork; neutral back-of-head; real cloth, hair, metal and leather source pixels. Static model, no bird/weapon/rig.';
 scene.project.name=model.name;
 scene.engine='§wyrl§ Engine · Maker v11.299';scene.version=11.299;
 se299State.atlasCorrected=model.parts.length;
 se299State.restoredLocalUVVertices=verts;
 return scene;
};
window.SWYRL_ENGINE_HOODED_VANGUARD=Object.freeze({
 id:'hooded-vanguard',createScene:se291HeroScene,open:se291OpenHero,
 status:()=>({...se291Stats,...se299State,version:'v11.299',
  imageBacked:true,sourceImage:se298AtlasMetadata.source,
  originalImageSha256:se298AtlasMetadata.jpegSha256,
  correctedLocalUVs:true,weapon:false,bird:false,rigged:false})
});
