const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const N=384,colors=new Uint8ClampedArray(N*N*4),mask=new Uint8ClampedArray(N*N*4);
for(let y=0;y<N;y++)for(let x=0;x<N;x++){
 const i=(y*N+x)*4;
 colors[i]=195;colors[i+1]=142;colors[i+2]=102;colors[i+3]=255;
 const crack=(x===192 || (x>192 && y===155));
 mask[i]=mask[i+1]=mask[i+2]=crack?255:0;mask[i+3]=255;
}
let painted=null,draw=[];
const baseCtx={getImageData(){return {data:colors.slice()}},
  putImageData(image){painted=image.data}};
const maskCtx={drawImage(...args){draw.push(args)},
  getImageData(){return {data:mask}}};
let count=0;
const scope={console,window:{},Float32Array,Math,document:{createElement(type){
 assert.equal(type,'canvas');count++;
 return {width:0,height:0,getContext:()=>maskCtx};
}}};
vm.createContext(scope);
vm.runInContext(fs.readFileSync(path.join(__dirname,'../runtime/cliff_fracture_overlay_v11_332.js'),'utf8'),scope);
const output=vm.runInContext('se332OverlayRockFractures({},globalAlbedo)',Object.assign(scope,{globalAlbedo:baseCtx}));
assert.equal(count,1);
assert.deepEqual(draw[0].slice(1,5),[1152,384,384,384],
  'must read the actual authored fracture tile, not another atlas tile');
const at=(x,y)=>painted.slice((y*N+x)*4,(y*N+x)*4+4);
assert(at(192,100)[0]<90 && at(192,100)[1]<90,
 'fracture-core color must be visibly darker than clean sandstone');
assert(at(191,100)[0]<195,
 'one-pixel shoulder helps fractures survive model viewport reduction');
assert.deepEqual(Array.from(at(20,20)),[195,142,102,255],
 'clean stone away from cracks must retain its original albedo');
assert.equal(at(192,100)[3],255,'preserve opaque material');
assert(output.pixels>400 && output.pixels<3000,
 'darken only fracture lines and their narrow shoulders');
assert.equal(scope.window.SWYRL_ENGINE_CLIFF_FRACTURES_332.status().geometryAdded,0);
console.log('SE332_CLIFF_FRACTURES_PASS',JSON.stringify({
 changedPixels:output.pixels,maxContrast:output.maxContrast,
 pixelCore:[...at(192,100)],pixelUnaffected:[...at(20,20)],
 geometryAdded:0,atlasTile:7
}));
