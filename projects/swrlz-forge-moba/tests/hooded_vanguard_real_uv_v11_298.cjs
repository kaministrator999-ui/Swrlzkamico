// v11.298 focused regression: exact real artwork bytes, native UV tile mapping,
// per-part material dispatch, and preservation of 17 editable parts.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const chunks=[0,1,2,3].map(i=>fs.readFileSync(path.join(root,
  'payload/vanguard-real-art-v11-298/part-'+i+'.b64'),'utf8').trim());
const originalImage=Buffer.from(chunks.join(''),'base64');
const hash=crypto.createHash('sha256').update(originalImage).digest('hex');
const expected='d34f6afc422cbfafe54dfbbd420752b12d37967654ea5c1443c031f3b6720b27';
assert.equal(hash,expected,'must use real art image bytes, not procedural redraw');
assert.equal(originalImage.length,11291);
assert.equal(originalImage[0],0xff);assert.equal(originalImage[1],0xd8);
assert.equal(originalImage.at(-2),0xff);assert.equal(originalImage.at(-1),0xd9);
const imageURL='data:image/jpeg;base64,'+originalImage.toString('base64');
const source=fs.readFileSync(path.join(root,'runtime/hooded_vanguard_real_uv_v11_298.js'),'utf8')
  .replace('__SE298_ATLAS_DATA_URL__',JSON.stringify(imageURL));
const groups=['skin','hair','hood','scarf','uniform','armor','pauldron','teal','leather','gloves','boots'];
const positions=[0,0,0,1,0,0,0,1,0,1,1,0];
let first=null;
const context={
 console,window:{},
 THREE:{
  TextureLoader:class {load(url,onLoad){assert.equal(url,imageURL);
   const t={image:{width:512,height:384}};onLoad();return t;}},
  MeshStandardMaterial:class {constructor(options){Object.assign(this,options);}},
  SRGBColorSpace:'srgb',ClampToEdgeWrapping:1,LinearFilter:2,DoubleSide:2
 },
 se291HeroMaterial:part=>({legacy:part}),se297Palette:{},
 se291HeroScene:()=>({project:{name:'before',modelAtelier:{
  parts:Array.from({length:17},(_,i)=>({
   id:'vanguard-rebuilt-'+i,name:'Part '+i,
   heroPBR:{tile:'v296:'+groups[i%11]},
   topologyMesh:{positions:[...positions],uvs:[0,0,1,0,0,1,1,1]}
  }))
 }}})
};
for(const x of groups)context.se297Palette[x]={rough:.7,metal:0};
context.se291Stats={lastParts:17};
context.se291OpenHero=()=>true;
vm.createContext(context);vm.runInContext(source,context,{timeout:20000});
const scene=vm.runInContext('se291HeroScene()',context);
assert.equal(scene.project.modelAtelier.parts.length,17);
assert.equal(scene.project.name,'Hooded Vanguard · Real Artwork UV');
assert.equal(scene.version,11.298);
const layout={skin:[0,0],hair:[1,0],hood:[2,0],scarf:[3,0],
 uniform:[0,1],armor:[1,1],pauldron:[2,1],teal:[3,1],
 leather:[0,2],gloves:[1,2],boots:[2,2]};
for(const part of scene.project.modelAtelier.parts){
 const family=part.heroPBR.tile.slice(5),[col,row]=layout[family],g=part.topologyMesh;
 assert(g.uvs.every(Number.isFinite));
 for(let i=0;i<g.uvs.length;i+=2){
  assert(g.uvs[i]>col/4&&g.uvs[i]<(col+1)/4,'u within real art tile: '+part.name);
  assert(g.uvs[i+1]>(2-row)/3&&g.uvs[i+1]<(3-row)/3,'v within real art tile: '+part.name);
 }
 if(!first)first=part;
 const mat=vm.runInContext('se291HeroMaterial',context)(part);
 assert.equal(mat.name,'Image-mapped '+family);
 assert.equal(mat.map.image.width,512);
 assert.equal(part.heroPBR.atlasSha256,expected);
 assert.equal(part.heroPBR.source,'source-image-actual-pixels');
}
const untouched=vm.runInContext('se291HeroMaterial',context)({id:'other'});
assert(untouched.legacy,'other model material renderer still original');
const status=vm.runInContext('window.SWYRL_ENGINE_HOODED_VANGUARD.status()',context);
assert.equal(status.remappedParts,17);
assert.equal(status.loaded,true);
assert.equal(status.actualGeneratedImagePixels,true);
console.log('ACTUAL_IMAGE_UV_OK',JSON.stringify({
 sha256:hash,bytes:originalImage.length,textureSize:[512,384],cells:11,
 mappedParts:status.remappedParts,mappedVertices:status.remappedVertices,
 actualImageDecoded:true,ownerAppearanceAccepted:false}));
