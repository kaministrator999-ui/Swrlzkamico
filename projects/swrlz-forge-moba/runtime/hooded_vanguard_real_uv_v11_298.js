// §E v11.298: actual generated art IMAGE pixels, not a procedural approximation.
// The 4x3 JPEG atlas is cut directly from the generated Hooded Vanguard texture
// artwork. Each painted region matches ONE editor material family.
// The native mesh topology remains exactly the v11.297 17-part model.
const se298AtlasDataURL=__SE298_ATLAS_DATA_URL__;
const se298AtlasLayout=Object.freeze({
 skin:[0,0],hair:[1,0],hood:[2,0],scarf:[3,0],
 uniform:[0,1],armor:[1,1],pauldron:[2,1],teal:[3,1],
 leather:[0,2],gloves:[1,2],boots:[2,2]
});
const se298AtlasMetadata=Object.freeze({
 source:'hooded_vanguard_game_texture_atlas.png',
 pipeline:'actual-image-crop-then-native-uv-tile-remapping',
 jpegSha256:'d34f6afc422cbfafe54dfbbd420752b12d37967654ea5c1443c031f3b6720b27',
 sheetPixels:[512,384],cellPixels:[128,128],layout:[4,3],
 materialFamilies:Object.keys(se298AtlasLayout)
});
let se298Texture=null;
const se298State={attempts:0,loaded:false,error:null,remappedParts:0,remappedVertices:0};
function se298GetActualImageTexture(){
 if(se298Texture)return se298Texture;
 se298Texture=new THREE.TextureLoader().load(
  se298AtlasDataURL,
  ()=>{se298State.loaded=true;se298State.error=null;},
  undefined,
  e=>{se298State.error=String(e?.message||e||'Image atlas load failed');
      console.error('Hooded Vanguard image-backed atlas failed',e);}
 );
 se298Texture.name='Hooded Vanguard — actual generated atlas pixels';
 se298Texture.colorSpace=THREE.SRGBColorSpace;
 se298Texture.wrapS=THREE.ClampToEdgeWrapping;
 se298Texture.wrapT=THREE.ClampToEdgeWrapping;
 // All 11 paintings share one texture; disable cross-tile mipmap bleeding.
 se298Texture.generateMipmaps=false;
 se298Texture.minFilter=THREE.LinearFilter;
 se298Texture.magFilter=THREE.LinearFilter;
 se298Texture.anisotropy=2;
 return se298Texture;
}
const se298OlderHeroMaterial=se291HeroMaterial;
se291HeroMaterial=function(part){
 const tag=part.heroPBR?.tile;
 if(typeof tag!=='string'||!tag.startsWith('v298:'))return se298OlderHeroMaterial(part);
 const family=tag.slice(5),pos=se298AtlasLayout[family];
 if(!pos)throw Error('Unknown image-atlas UV tile: '+family);
 const spec=se297Palette[family];
 return new THREE.MeshStandardMaterial({
  name:'Image-mapped '+family,
  color:'#ffffff',
  map:se298GetActualImageTexture(),
  roughness:spec?.rough??.8,
  metalness:family==='armor'?.23:family==='pauldron'?.27:0,
  side:THREE.DoubleSide,
  transparent:false
 });
};
const se298OlderHeroScene=se291HeroScene;
se291HeroScene=function(){
 se298State.attempts++;
 const scene=se298OlderHeroScene();
 const model=scene.project?.modelAtelier;
 if(!model||model.parts.length!==17)throw Error('Expected 17-part v11.297 Vanguard');
 let vertices=0,mapped=0;
 for(const part of model.parts){
  const tag=part.heroPBR?.tile;
  if(typeof tag!=='string'||!tag.startsWith('v296:'))
   throw Error('Expected v11.297 native UV material for '+part.name);
  const family=tag.slice(5),coord=se298AtlasLayout[family],uv=part.topologyMesh?.uvs;
  if(!coord||!Array.isArray(uv)||uv.length!==part.topologyMesh.positions.length/3*2)
    throw Error('Missing valid image UVs for '+part.name);
  // Existing editor UVs refer to one complete square [0,1]^2. Pack each
  // square into its corresponding real artwork tile in the 4x3 raster atlas.
  // Three.js UV V starts at the bottom; the art sheet rows start at the top.
  const gutter=1.5/128;
  for(let i=0;i<uv.length;i+=2){
   const u=Math.max(0,Math.min(1,uv[i]));
   const v=Math.max(0,Math.min(1,uv[i+1]));
   uv[i]=+((coord[0]+gutter+(1-2*gutter)*u)/4).toFixed(6);
   uv[i+1]=+((2-coord[1]+gutter+(1-2*gutter)*v)/3).toFixed(6);
  }
  vertices+=uv.length/2;mapped++;
  part.heroPBR={
   ...part.heroPBR,
   tile:'v298:'+family,
   source:'source-image-actual-pixels',
   atlasSha256:se298AtlasMetadata.jpegSha256,
   channels:['source-albedo-image','physical-roughness','physical-metalness']
  };
 }
 if(mapped!==17)throw Error('Incomplete real-image UV material binding');
 model.name='Hooded Vanguard · Real Artwork UV';
 model.reference='v11.298: real generated Hooded Vanguard artwork pixels, cropped into 11 atlas regions, mapped to 17 native mesh UVs; reused shared JPEG albedo with material roughness/metalness. Image source is NOT a procedural imitation. Static; no bird, weapon or full rig.';
 scene.project.name=model.name;
 scene.engine='§wyrl§ Engine · Maker v11.298';scene.version=11.298;
 se298State.remappedParts=mapped;se298State.remappedVertices=vertices;
 return scene;
};
window.SWYRL_ENGINE_HOODED_VANGUARD=Object.freeze({
 id:'hooded-vanguard',open:se291OpenHero,createScene:se291HeroScene,
 status:()=>({...se291Stats,...se298State,version:'v11.298',
   sourceImage:se298AtlasMetadata.source,
   atlasSourceSha256:se298AtlasMetadata.jpegSha256,
   atlasLayout:se298AtlasMetadata.layout,
   materialFamilies:se298AtlasMetadata.materialFamilies,
   actualGeneratedImagePixels:true,weapon:false,bird:false,rigged:false})
});
