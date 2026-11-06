// §E v11.291 material-only regression, no GPU/browser dependencies.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const assert=require('node:assert/strict');
const events=[],contexts=[],images=[];
function mockCanvas(){
 const canvas={width:0,height:0};
 const ctx={
  canvas,globalCompositeOperation:'source-over',
  beginPath(){},ellipse(...args){events.push({method:'ellipse',args})},
  closePath(){},translate(...args){events.push({method:'translate',args})},
  rotate(){},lineTo(){},moveTo(){},fill(){},stroke(){},save(){},restore(){},
  fillRect(...args){events.push({method:'fillRect',args,composition:this.globalCompositeOperation})},
  clearRect(){},drawImage(...args){events.push({method:'drawImage',args,composition:this.globalCompositeOperation,ctx:this})},
  createLinearGradient(...args){const stops=[];events.push({method:'linearGradient',args,stops});return {addColorStop(p,v){stops.push([p,v])}}},
  createRadialGradient(){return {addColorStop(){}}},
  getImageData(){const data=new Uint8ClampedArray(384*384*4);data.fill(175);return {data}},
  putImageData(){events.push({method:'putImageData'})}
 };
 canvas.getContext=()=>ctx;contexts.push(ctx);return canvas;
}
class Material{constructor(props){Object.assign(this,props)}}
class Texture{constructor(canvas){this.canvas=canvas;this.needsUpdate=false}}
class MockImage{constructor(){images.push(this)}set src(path){this._src=path;this.onload?.()}}
const scope={
 window:{},document:{createElement(type){assert.equal(type,'canvas');return mockCanvas()}},
 Image:MockImage,console,
 THREE:{CanvasTexture:Texture,MeshStandardMaterial:Material,
  Vector2:class{constructor(x,y){this.x=x;this.y=y}},
  SRGBColorSpace:'srgb',NoColorSpace:'linear',ClampToEdgeWrapping:'clamp',
  LinearMipmapLinearFilter:'mipmap',LinearFilter:'linear',
  TangentSpaceNormalMap:0,DoubleSide:2
 },
 SE288_ATLAS:'assets/cliff-hand/cliff_pbr_atlas_384.jpg'
};
vm.createContext(scope);
vm.runInContext(fs.readFileSync(path.join(__dirname,'../runtime/cliff_knuckle_wrist_moss_v11_291.js'),'utf8'),scope);
const material=scope.window.SWYRL_ENGINE_CLIFF_MATERIAL_291.createMaterial({});
const state=scope.window.SWYRL_ENGINE_CLIFF_MATERIAL_291.status();
assert.equal(state.createdMaps,4);
assert.equal(state.knuckleMarks,4);
assert.equal(state.ready,true);
assert.equal(state.failures,0);
assert.equal(images.length,1,'one atlas decode, not repeated per map');
assert.equal(material.map.colorSpace,'srgb');
assert.equal(material.normalMap.colorSpace,'linear');
assert.equal(material.roughnessMap.colorSpace,'linear');
assert.equal(material.aoMap.colorSpace,'linear');
assert.equal(material.metalness,0);
assert.equal(material.normalScale.x,1.12);
assert.equal(state.geometryObjectsCreated,0);
assert(material.map.needsUpdate);
const draw=events.filter(e=>e.method==='drawImage');
const clean=draw.find(e=>e.args.length===9&&e.args[1]===0&&e.args[2]===384);
assert(clean,'sandstone base tile 4 must replace allover moss tile 0');
const moss=draw.find(e=>e.args.length===9&&e.args[1]===0&&e.args[2]===0);
assert(moss,'original source moss must be taken from tile 0 for wrist mask');
const fades=events.filter(e=>e.method==='linearGradient');
assert(fades.some(e=>e.args[1]===275&&e.args[3]===384&&e.stops[0][1].includes(',0)')),
 'moss starts only below the hand/palm and fades at wrist');
const ellipses=events.filter(e=>e.method==='ellipse');
assert.equal(ellipses.length,4,'one visual stone ridge drawn for each knuckle in albedo');
const marks=events.filter(e=>e.method==='translate');
assert.equal(marks.length,4);
for(let i=0;i<4;i++){
 const mark=state.knuckleUVs[i],position=marks[i].args;
 assert(Math.abs(position[0]-mark[0]*384)<.01);
 assert(Math.abs(position[1]-(1-mark[1])*384)<.01);
}
assert.equal(events.filter(e=>e.method==='putImageData').length,2,
 'matching knuckle relief for normal and occlusion maps');
console.log(JSON.stringify({pass:true,materials:state.createdMaps,moss:'wrist-gradient-only',
 knuckles:state.knuckleMarks,geometryAdded:state.geometryObjectsCreated,
 pbr:['albedo','normal','roughness','AO'],texturesLoaded:state.ready}));
