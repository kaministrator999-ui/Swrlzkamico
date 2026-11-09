// §E v11.370: real WebXR topology + unchanged UVs; mapped cliff material test.
// Runs headlessly with a small fake Canvas2D, no browser or other editor changes.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const data=JSON.parse(read('assets/models/webxr-hands/right.json'));
const model=structuredClone(data.mesh),raw=structuredClone(data.mesh);
for(let i=0;i<model.positions.length;i+=3){
 const [x,y,z]=model.positions.slice(i,i+3);
 model.positions[i]=+((z-.09)*1.17-.135).toFixed(6);
 model.positions[i+1]=+(y*1.06+.28).toFixed(6);
 model.positions[i+2]=+((.4-x)*.68).toFixed(6);
}
const originalUV=JSON.stringify(model.uvs),originalIndices=JSON.stringify(model.indices);
const sources=[];
class FakeCanvas{
 constructor(){this.width=384;this.height=384;this.data=new Uint8ClampedArray(384*384*4);this.ctx=new FakeCtx(this);}
 getContext(){return this.ctx;}
}
class FakeCtx{
 constructor(canvas){this.canvas=canvas;}
 drawImage(img,sx,sy){let type=sx===0&&sy===384?'base':sx===0?'moss':
   sx===384?'normal':sx===768?'rough':sx===1152&&sy===384?'fracture':'ao';
  const values={base:[187,132,99],moss:[79,117,66],normal:[128,128,244],
   rough:[206,206,206],ao:[227,227,227],fracture:[165,165,165]}[type];
  for(let y=0;y<384;y++)for(let x=0;x<384;x++){
   const o=(y*384+x)*4;const isSeam=x%47<3||y%59<2;
   for(let k=0;k<3;k++)this.canvas.data[o+k]=
    type==='fracture'?(isSeam?values[k]:33):values[k];
   this.canvas.data[o+3]=255;
  }
 }
 getImageData(){return {data:new Uint8ClampedArray(this.canvas.data)};}
 putImageData(image){this.canvas.data.set(image.data);}
}
class FakeTexture{
 constructor(canvas){this.canvas=canvas;this.offset={};this.repeat={};}
}
const THREE={
 CanvasTexture:FakeTexture,SRGBColorSpace:'srgb',NoColorSpace:'linear',
 ClampToEdgeWrapping:'clamp',LinearMipmapLinearFilter:'mipmap',LinearFilter:'linear'
};
let materialCalls=0;
const ctx={
 console,Math,Map,Set,Uint8Array,Uint8ClampedArray,Float32Array,Image:class {
  set src(value){this.url=value;this.onload();}
 },
 document:{createElement:type=>{assert.equal(type,'canvas');return new FakeCanvas();}},
 THREE,SE288_ATLAS:'assets/cliff-hand/cliff_pbr_atlas_384.jpg',
 se290CliffMaterial(part){
  materialCalls++;
  return {part,map:{old:true},normalMap:{old:true},roughnessMap:{old:true},aoMap:{old:true},
    normalScale:{x:1.12,y:1.12,set(x,y){this.x=x;this.y=y}},
    color:{value:'old',set(v){this.value=v;}}};
 },
 window:{}
};
vm.createContext(ctx);
vm.runInContext(read('runtime/webxr_cliff_material_polish_v11_370.js'),ctx,{filename:'polish.js'});
const api=ctx.window.SWYRL_ENGINE_CLIFF_POLISH_370;
const mkResult=api.bake({},model);
assert.equal(mkResult.maps.length,4);
assert(mkResult.mapped>13000,'real WebXR UV triangles should cover the majority of texture');
assert(mkResult.cracks>150,'at least some natural seams visible');
assert(mkResult.mossed>150,'anatomical moss should occupy some UV areas');
const mapColor=mkResult.maps[0].canvas.data;
function sample(x,y){
 const i=(y*384+x)*4;return Array.from(mapColor.slice(i,i+3));
}
const colored=sample(100,108);
assert(colored.every(v=>Number.isFinite(v)));
const palmAndWrist=new Set();
const polish=api.refine;
let lowMoss=0,highMoss=0,edgeEffect=0;
for(let y=0;y<100;y++)for(let x=0;x<100;x++){
 const xx=x/75-.80, zz=x/500-.1, yy=.74+y*.008;
 const low=polish(xx,yy,zz,[187,132,99],[79,117,66],168,206,227);
 const high=polish(xx,2.85,zz,[187,132,99],[79,117,66],168,206,227);
 lowMoss+=low.moss;highMoss+=high.moss;edgeEffect+=low.cuff;
}
assert(lowMoss>highMoss*7,'moss should favor wrist/crease over fingertips');
assert(edgeEffect>100,'wrist needs weathering material lip');
const part={kind:'topologyMesh',topologyMesh:model,cliffPBR:{variant:'webxr-cliff'}};
const material=api.material(part);
assert.equal(material.normalScale.x,.85);
assert.equal(material.name,'Cliff · graded mineral seams / joint moss / eroded sandstone cuff');
assert.equal(material.map.canvas.width,384);
assert.strictEqual(material.map,api.material(part).map,'shared maps, no re-bake per material');
const status=api.status();
assert.equal(status.requests,1);
assert.equal(status.successes,1);
assert.equal(status.errors,0);
assert.equal(status.ready,true);
assert.equal(status.geometryChanged,false);
assert.equal(materialCalls,2);
assert.equal(JSON.stringify(model.uvs),originalUV);
assert.equal(JSON.stringify(model.indices),originalIndices);
assert.deepEqual(data.mesh.uvs,raw.uvs);
assert.deepEqual(data.mesh.indices,raw.indices);
const noChanges=read('runtime/stone_hand_anatomy_v11_367.js');
assert(noChanges.includes('se281RockScene=se367AnatomicalRockScene;'));
console.log('SE370_CLIFF_MATERIAL_PASS '+JSON.stringify({
 uvPixels:mkResult.mapped,crackPixels:mkResult.cracks,mossPixels:mkResult.mossed,
 anatomicalWristToFingertipMossRatio:+(lowMoss/Math.max(.0001,highMoss)).toFixed(2),
 materials:4,originalWebXRVertices:model.positions.length/3,
 originalWebXRUvUnchanged:true,rockHandUntouched:true,
 bakeCount:status.successes
}));
