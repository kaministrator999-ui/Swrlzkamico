// v11.302 focused native-UV PBR test: no generic engine/browser CI.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../runtime/hooded_vanguard_uv_pbr_v11_302.js'),'utf8');
const families=['skin','hair','hood','scarf','uniform','armor','pauldron','teal','leather','gloves','boots'];
let drawCalls=0,contexts=0;
function canvas(w=256,h=256){
 const ctx={
  fillStyle:'',strokeStyle:'',lineWidth:1,
  fillRect(){drawCalls++;},beginPath(){},moveTo(){},
  bezierCurveTo(){},quadraticCurveTo(){},lineTo(){},
  stroke(){drawCalls++;},strokeRect(){drawCalls++;},
  getImageData(x,y,width,height){
   const pixels=new Uint8ClampedArray(width*height*4);
   for(let j=0;j<pixels.length;j+=4)pixels[j]=pixels[j+1]=pixels[j+2]=128,pixels[j+3]=255;
   return {data:pixels};
  },
  createImageData(w,h){return {data:new Uint8ClampedArray(w*h*4)};},
  putImageData(image){assert.equal(image.data.length,256*256*4);}
 };
 return {width:w,height:h,getContext(){contexts++;return ctx;}};
}
const baseScene=()=>({engine:'old',version:11.301,project:{
 name:'old',modelAtelier:{name:'old',parts:families.map((f,i)=>({
 id:'vanguard-rebuilt-'+String(i).padStart(2,'0'),
 heroPBR:{tile:'v300:'+f},
 topologyMesh:{positions:[0,0,0,.1,0,0,0,.1,0],uvs:[0,0,1,0,0,1],indices:[0,1,2]}
 }))}}});
const ctx=vm.createContext({
 console,Math,Map,Object,Uint8ClampedArray,
 se300Canvas:canvas,se291HeroScene:baseScene,
 se291HeroMaterial:part=>({name:'original',map:{existingOriginalPaint:true}}),
 se291OpenHero:()=>true,se291Stats:{successes:1},
 se300Status:{created:11},se301Result:{correctedHands:2,retouchedFamilies:11},
 window:{},
 THREE:{
  CanvasTexture:class{constructor(c){this.image=c;}},
  Vector2:class{constructor(x,y){this.x=x;this.y=y;}},
  NoColorSpace:'none',ClampToEdgeWrapping:1,
  LinearMipmapLinearFilter:2,LinearFilter:3
 }
});
vm.runInContext(source,ctx,{timeout:12000});
const scene=vm.runInContext('se291HeroScene()',ctx);
assert.equal(scene.version,11.302);
assert(scene.project.modelAtelier.name.includes('Painted PBR'));
assert.equal(scene.project.modelAtelier.parts.length,families.length);
const surfaces=[];
for(const family of families){
 const part={heroPBR:{tile:'v300:'+family}};
 const material=vm.runInContext('se291HeroMaterial',ctx)(part);
 assert(material.map.existingOriginalPaint,'keep v11.301 albedo and face');
 assert.equal(material.normalMap.image.width,256);
 assert.equal(material.roughnessMap.image.height,256);
 assert.equal(material.normalMap.colorSpace,'none');
 assert.equal(material.roughnessMap.colorSpace,'none');
 assert.equal(material.roughness,1,'roughnessMap owns per-texel roughness');
 assert(material.normalScale.x>0&&material.normalScale.x<.4);
 assert.equal(material.normalScale.x,material.normalScale.y);
 assert(material.needsUpdate);
 const again=vm.runInContext('se291HeroMaterial',ctx)(part);
 assert.equal(again.normalMap,material.normalMap,'reuse map across repeat meshes');
 assert.equal(again.roughnessMap,material.roughnessMap);
 surfaces.push(family);
}
const unaffected=vm.runInContext('se291HeroMaterial',ctx)({});
assert.equal(unaffected.name,'original','unrelated models remain untouched');
const status=vm.runInContext('window.SWYRL_ENGINE_HOODED_VANGUARD.status()',ctx);
assert.equal(status.nativeUVPBRMaps,true);
assert.equal(status.generatedMapFamilies,11);
assert.equal(status.normalFamilies,11);
assert.equal(status.roughnessFamilies,11);
assert.equal(status.additionalGeometry,0);
assert(drawCalls>25,'at least actual authored height markings on UV maps');
console.log('VANGUARD_STYLED_PBR_UV_OK',JSON.stringify({
 version:'v11.302',families:surfaces,pbrMaps:22,
 mappedAlbedoPreserved:true,drawCalls,
 additionalMeshes:0,ownerVisualAcceptance:false
}));
