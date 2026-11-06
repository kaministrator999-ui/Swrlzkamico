// §E v11.299 regression: actual image sampling, restored native UV and
// front-only face artwork. Browser/device appearance remains a separate gate.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../runtime/hooded_vanguard_uv_repair_v11_299.js'),'utf8');
const families=['skin','hair','hood','scarf','uniform','armor','pauldron','teal','leather','gloves','boots'];
const layout={skin:[0,0],hair:[1,0],hood:[2,0],scarf:[3,0],
 uniform:[0,1],armor:[1,1],pauldron:[2,1],teal:[3,1],
 leather:[0,2],gloves:[1,2],boots:[2,2]};
const localUVs=[0,0,.5,.5,1,1,.25,.75,.75,.25];
const g=1.5/128,s=1-2*g;
const calls=[];
function samplePart(family,i){
 const [col,row]=layout[family],uvs=[];
 for(let k=0;k<localUVs.length;k+=2){
  uvs.push((col+g+s*localUVs[k])/4,(2-row+g+s*localUVs[k+1])/3);
 }
 return {id:'vanguard-rebuilt-'+i,name:'Part '+i,heroPBR:{tile:'v298:'+family},
  topologyMesh:{positions:Array.from({length:uvs.length/2*3},()=>0),uvs}};
}
function canvas(w=256,h=256){
 const ctx={
  fillStyle:'#fff',fillRect(){},drawImage(...args){calls.push({args});},
  getImageData(x,y,width,height){return {data:new Uint8ClampedArray(width*height*4),width,height};},
  putImageData(){},save(){},restore(){},translate(){},scale(){}
 };
 return {width:w,height:h,getContext(){return ctx;}};
}
class MockImage{
 set src(v){assert.equal(v,'data:image/jpeg;base64,SEALED_IMAGE');
  this.width=512;this.height=384;
  if(this.onload)this.onload();
 }
}
const context={console,Image:MockImage,
 document:{createElement(tag){assert.equal(tag,'canvas');return canvas();}},
 window:{},se298AtlasDataURL:'data:image/jpeg;base64,SEALED_IMAGE',
 se298AtlasLayout:layout,
 se298AtlasMetadata:{source:'hooded_vanguard_game_texture_atlas.png',jpegSha256:'TEST123'},
 se291HeroScene:()=>({project:{modelAtelier:{
  parts:Array.from({length:17},(_,i)=>samplePart(families[i%families.length],i))
 }}}),
 se291HeroMaterial:part=>({legacy:part}),se291OpenHero:()=>true,se291Stats:{successes:1},
 THREE:{
  CanvasTexture:class {constructor(canvas){this.image=canvas;}},SRGBColorSpace:'srgb',
  ClampToEdgeWrapping:1,LinearMipmapLinearFilter:2,LinearFilter:3,
  DoubleSide:4,
  MeshStandardMaterial:class {constructor(props){Object.assign(this,props);}}
 }};
vm.createContext(context);
vm.runInContext(source,context,{timeout:10000});
const model=vm.runInContext('se291HeroScene()',context,{timeout:10000});
assert.equal(model.project.modelAtelier.parts.length,17);
assert.equal(model.version,11.299);
for(const part of model.project.modelAtelier.parts){
 assert(part.heroPBR.tile.startsWith('v299:'));
 for(let k=0;k<part.topologyMesh.uvs.length;k++)
  assert(Math.abs(part.topologyMesh.uvs[k]-localUVs[k])<.000003,'restore local UV');
 assert.equal(part.heroPBR.source,'actual-original-image-regions');
}
for(const family of families){
 const part=model.project.modelAtelier.parts.find(p=>p.heroPBR.tile==='v299:'+family);
 const m=vm.runInContext('se291HeroMaterial',context)(part);
 assert.equal(m.name,'Actual cropped painted '+family);
 assert.equal(m.map.image.width,256);
}
assert(calls.length>=1,'actual source image must be drawn into material canvases');
const sourceDraws=calls.filter(item=>item.args[0].width===512);
assert(sourceDraws.length>=11,'each family must sample original artwork');
for(const item of sourceDraws){
 assert(item.args[3]<128&&item.args[4]<128,
  'crop SOURCE painted region, not entire concept-sheet tile');
}
assert.equal(vm.runInContext('se299State.imageLoaded',context),true);
assert.equal(vm.runInContext('se299State.paintedFamilies',context),11);
assert.equal(vm.runInContext('se299State.atlasCorrected',context),17);
assert.equal(vm.runInContext('se299State.restoredLocalUVVertices',context),17*5);
assert(vm.runInContext('se291HeroMaterial({heroPBR:{tile:"not-vanguard"}}).legacy!==undefined',context));
console.log('VANGUARD_REAL_IMAGE_UV_ALIGNED_OK',JSON.stringify({
 restoredMeshParts:17,realImageMaterialFamilies:11,
 imageSourceDraws:calls.length,allUVsRestored:true,
 imageSource:'SEALED_v11_298_actual_art',
 ownerAppearanceAccepted:false}));
