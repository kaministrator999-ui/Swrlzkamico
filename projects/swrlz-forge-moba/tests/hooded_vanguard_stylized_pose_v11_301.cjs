// Focused §E v11.301 regression. Exercise the *real* v11.300 scene builder
// followed by corrective UV painter / head sculpt / wrist rotation.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const assert=require('node:assert/strict'),root=path.resolve(__dirname,'..');
const old=fs.readFileSync(path.join(root,'runtime/hooded_vanguard_mesh_uv_v11_300.js'),'utf8');
const next=fs.readFileSync(path.join(root,'runtime/hooded_vanguard_stylized_pose_v11_301.js'),'utf8');
const families=['uniform','skin','hair','hair','hood','scarf','scarf','armor','pauldron','pauldron','teal','teal','leather','gloves','gloves','boots','boots'];
const artworks={},lines=[],sourceDraws=[];
function fakeCanvas(w=384,h=384){
 const calls=[];
 const ctx={
  fillStyle:'',strokeStyle:'',lineWidth:1,lineCap:'',lineJoin:'',
  createLinearGradient(){return {addColorStop(){}};},
  beginPath(){},moveTo(x,y){calls.push({type:'point',x,y});},
  lineTo(x,y){calls.push({type:'point',x,y});},
  bezierCurveTo(){},arc(){},ellipse(x,y,rx,ry){calls.push({type:'eye-or-detail',x,y,rx,ry});},
  stroke(){},fill(){},fillRect(){calls.push({type:'fill'});},
  getImageData(){throw Error('No JPEG or photograph cutouts are allowed');},
  drawImage(...args){sourceDraws.push(args);throw Error('Source photo must not be pasted onto model');}
 };
 return {width:w,height:h,calls,getContext(){return ctx;}};
}
function hand(i){
 const sign=i===13?-1:1,points=[];
 for(let n=0;n<32;n++){
  points.push(sign*.888+(n%5-2)*.01,2.28+.015*(n%4),.09+.001*n);
 }
 // Distinct fingertip, used to verify orientation after cuff rotation.
 points[0]=sign*.888;points[1]=2.28;points[2]=.10;
 return {positions:points,uvs:Array.from({length:points.length/3*2},()=>.5),
  indices:[0,1,2,2,3,4,4,5,6]};
}
const scene=()=>({project:{name:'baseline',modelAtelier:{
 parts:families.map((family,i)=>({
  id:'vanguard-rebuilt-'+String(i).padStart(2,'0'),
  name:'Before '+i,kind:'topologyMesh',heroPBR:{tile:'v299:'+family},
  topologyMesh:(i===13||i===14)?hand(i):
    {positions:[0,0,0,.1,0,0,0,.1,0],
     uvs:[0,0,1,0,0,1],indices:[0,1,2]}
 }))
}}});
const context=vm.createContext({
 console,document:{createElement(kind){assert.equal(kind,'canvas');return fakeCanvas();}},
 Image:class{constructor(){throw Error('No image load should be needed for the authored textures');}},
 se298AtlasDataURL:'data:image/jpeg;base64,LEGACY_IMAGE',
 se298AtlasMetadata:{jpegSha256:'LEGACY_IMAGE_SHA'},
 se298AtlasLayout:{skin:[0,0],hair:[1,0],hood:[2,0],scarf:[3,0],
 uniform:[0,1],armor:[1,1],pauldron:[2,1],teal:[3,1],
 leather:[0,2],gloves:[1,2],boots:[2,2]},
 se291HeroScene:scene,se291HeroMaterial:p=>({legacy:p}),
 se291OpenHero:()=>true,se291Stats:{lastParts:17},window:{},
 THREE:{
  CanvasTexture:class {constructor(canvas){this.image=canvas;}},
  MeshStandardMaterial:class {constructor(opts){Object.assign(this,opts);}},
  SRGBColorSpace:'sRGB',ClampToEdgeWrapping:1,
  LinearMipmapLinearFilter:2,LinearFilter:3,DoubleSide:4
 }
});
vm.runInContext(old,context,{timeout:20000});
vm.runInContext(next,context,{timeout:20000});
const built=vm.runInContext('se291HeroScene()',context,{timeout:20000});
assert.equal(built.version,11.301);
const parts=built.project.modelAtelier.parts;
assert.equal(parts.length,17);
assert(parts[1].name.includes('refined jaw'));
assert(parts[7].name.includes('tapered painted-contour breastplate'));
for(const p of parts){
 const mesh=p.topologyMesh;
 assert(mesh.positions.length/3*2===mesh.uvs.length);
 assert(mesh.indices.every(n=>Number.isInteger(n)&&n>=0&&n<mesh.positions.length/3));
 assert(mesh.uvs.every(x=>Number.isFinite(x)&&x>=0&&x<=1));
 assert(mesh.positions.every(Number.isFinite));
 assert(p.heroPBR.tile.startsWith('v300:'));
}
for(const [i,s] of [[13,-1],[14,1]]){
 const g=parts[i].topologyMesh.positions;
 const oldFinger={x:s*.888,y:2.28};
 const expectedX=s*.86+(.028*s*.95)*Math.cos(s*.64)
  -((2.28-2.73)*.95)*Math.sin(s*.64);
 const expectedY=2.73+(.028*s*.95)*Math.sin(s*.64)
  +((2.28-2.73)*.95)*Math.cos(s*.64);
 assert(Math.abs(g[0]-expectedX)<.00001,'fingertip points outward from elbow '+s);
 assert(Math.abs(g[1]-expectedY)<.00001);
 assert(s*g[0]>.888+s*.002,'hand should extend outward '+s);
 assert(parts[i].heroPBR.wristPose==='forearm-aligned-A-pose');
 assert(Math.abs(parts[i].heroPBR.wristAngleRadians)>.55);
}
for(let i=0;i<17;i++){
 const part=parts[i],family=families[i],
  material=vm.runInContext('se291HeroMaterial',context)(part);
 assert.equal(material.name,'Model+UV '+family);
 assert.equal(material.map.image.width,384);
 // Catch the v11.300 bug where only the FIRST lazily loaded atlas was assigned.
 assert.equal(material.map.image,
  vm.runInContext('se300Atlases.get("'+family+'")',context),
  'each material must receive its own painted atlas: '+family);
}
assert.equal(sourceDraws.length,0,'no photographic source pieces pasted onto model');
const status=vm.runInContext('window.SWYRL_ENGINE_HOODED_VANGUARD.status()',context);
assert.equal(status.correctedHandAlignment,true);
assert.equal(status.photographicCutoutTextures,false);
assert.equal(status.correctedHands,2);
assert.equal(status.faceGeometryAdjusted,true);
assert.equal(status.paintedFamilies,11);
assert.equal(status.retouchedFamilies,11);
assert(vm.runInContext('se291HeroMaterial({})',context).legacy,'other models unchanged');
console.log('VANGUARD_STYLIZED_FACE_NEUTRAL_HANDS_OK',JSON.stringify({
 sourceVersion:'v11.301',paintedMaterialFamilies:status.retouchedFamilies,
 parts:parts.length,handOrientationFixes:status.correctedHands,
 photographPastes:sourceDraws.length,stagedFaceGeometry:true,
 ownerVisualAcceptance:false}));
