// v11.300 narrow regression: re-modelled silhouette AND its authored UVs
// are a coherent native 17-part scene using real owner-generated art pixels.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const assert=require('node:assert/strict');
const file=path.resolve(__dirname,'../runtime/hooded_vanguard_mesh_uv_v11_300.js');
const source=fs.readFileSync(file,'utf8');
const families=[
 'uniform','skin','hair','hair','hood','scarf','scarf','armor',
 'pauldron','pauldron','teal','teal','leather','gloves','gloves',
 'boots','boots'
];
const sourcePixels=[];
function fakeCanvas(w=384,h=384){
 const context={fillStyle:'',strokeStyle:'',lineWidth:1,
  fillRect(){},drawImage(...args){
   if(args[0]&&args[0].width===512&&args[0].height===384)sourcePixels.push(args);
  },createImageData(w,h){return {data:new Uint8ClampedArray(w*h*4)};},
  getImageData(x,y,w,h){return {data:new Uint8ClampedArray(w*h*4)};},
  putImageData(){},save(){},restore(){},translate(){},scale(){},
  strokeRect(){},beginPath(){},moveTo(){},quadraticCurveTo(){},stroke(){}
 };
 return {width:w,height:h,getContext(){return context;}};
}
class FakeImage{
 set src(src){assert.equal(src,'data:image/jpeg;base64,ORIGINAL_SEALED_OWNER_ART');
  this.width=512;this.height=384;if(this.onload)this.onload();}
}
const mock=vm.createContext({
 console,Image:FakeImage,Uint8ClampedArray,Math,Object,Map,Array,
 document:{createElement(kind){assert.equal(kind,'canvas');return fakeCanvas();}},
 se298AtlasDataURL:'data:image/jpeg;base64,ORIGINAL_SEALED_OWNER_ART',
 se298AtlasMetadata:{jpegSha256:'OWNER_ORIGINAL_IMAGE_SHA256'},
 se298AtlasLayout:{skin:[0,0],hair:[1,0],hood:[2,0],scarf:[3,0],
  uniform:[0,1],armor:[1,1],pauldron:[2,1],teal:[3,1],
  leather:[0,2],gloves:[1,2],boots:[2,2]},
 se291HeroMaterial:part=>({old:part}),
 se291HeroScene:()=>({project:{name:'baseline',modelAtelier:{
   parts:families.map((family,i)=>({
    id:'vanguard-rebuilt-'+String(i).padStart(2,'0'),
    name:'Before '+i,kind:'topologyMesh',heroPBR:{tile:'v299:'+family},
    topologyMesh:{
     positions:[0,0,0,.1,0,0,0,.1,0],
     uvs:[0,0,1,0,0,1],
     indices:[0,1,2]
    }
   }))
 }}}),
 se291Stats:{successes:1},se291OpenHero:()=>true,
 window:{},
 THREE:{
  CanvasTexture:class{constructor(image){this.image=image;}},
  SRGBColorSpace:'srgb',ClampToEdgeWrapping:1,
  LinearMipmapLinearFilter:2,LinearFilter:3,DoubleSide:4,
  MeshStandardMaterial:class{constructor(opts){Object.assign(this,opts);}}
 }
});
vm.runInContext(source,mock,{filename:file,timeout:20000});
const fresh=vm.runInContext('se291HeroScene()',mock,{timeout:20000});
assert.equal(fresh.version,11.300);
const parts=fresh.project.modelAtelier.parts;
assert.equal(parts.length,17);
let total=0,revised=0;
for(let i=0;i<parts.length;i++){
 const part=parts[i],g=part.topologyMesh;
 assert.equal(part.heroPBR.tile,'v300:'+families[i]);
 assert(g.positions.length>=9);
 assert.equal(g.uvs.length,2*g.positions.length/3,part.name+' UV parity');
 assert.equal(g.indices.length%3,0);
 assert(g.indices.every(n=>Number.isInteger(n)&&n>=0&&n<g.positions.length/3));
 assert(g.positions.every(Number.isFinite),part.name+' finite geometry');
 assert(g.uvs.every(n=>Number.isFinite(n)&&n>=0&&n<=1),part.name+' UV is normalized');
 if(i>=1&&i<=11){
  assert(g.positions.length>200,part.name+' should actually have rebuilt topology');
  revised++;
 }
 total+=g.positions.length/3;
}
assert.equal(revised,11);
assert(parts[4].name.includes('face framing'),'hood shape should be new');
assert(parts[7].name.includes('tapered breastplate'),'actual shaped armor');
assert(parts[10].name.includes('draped outer & inner cloth'),'cloth double sided');
// Face posterior longitude must not show the original painted face.
const face=parts[1].topologyMesh;
const rows=54,cols=96;
for(const row of [8,24,40]){
 const edgeIndex=row*(cols+1);
 const centerIndex=edgeIndex+cols/2;
 assert(Math.abs(face.positions[edgeIndex*3])<.01,'head seam / rear x');
 assert(face.positions[centerIndex*3+2]>face.positions[edgeIndex*3+2],
   'actual projected face relief projects forward');
}
for(let i=0;i<parts.length;i++){
 const mat=vm.runInContext('se291HeroMaterial',mock)(parts[i]);
 assert(mat.name==='Model+UV '+families[i]);
 assert.equal(mat.map.image.width,384,'per-family real-art UV canvas');
}
const status=vm.runInContext('window.SWYRL_ENGINE_HOODED_VANGUARD.status()',mock);
assert.equal(status.paintedFamilies,11);
assert.equal(status.rebuiltParts,17);
assert.equal(status.imageReady,true);
assert(sourcePixels.length>=11,'real owner art must supply texture pixels');
for(const args of sourcePixels){
 assert(args[3]>0&&args[3]<128,'real image material sample not whole illustration tile');
 assert(args[4]>0&&args[4]<128,'real image material sample not whole illustration tile');
}
assert(vm.runInContext('se291HeroMaterial({})',mock).old,'other model material unaffected');
console.log('VANGUARD_MESH_AND_UV_REBUILD_OK',JSON.stringify({
 version:'v11.300',rebuiltGeometryParts:revised,editableParts:parts.length,
 geometryVertices:total,textureFamilies:status.paintedFamilies,
 actualOwnerArtDraws:sourcePixels.length,
 ownerAppearanceAccepted:false}));
