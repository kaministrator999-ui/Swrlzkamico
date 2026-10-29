import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const read=p=>fs.readFileSync(new URL('../runtime/'+p,import.meta.url),'utf8');
let pixels=null;
const document={createElement:kind=>{
 assert.equal(kind,'canvas');
 return {width:0,height:0,getContext:()=>({
  createImageData:(w,h)=>({width:w,height:h,data:new Uint8ClampedArray(w*h*4)}),
  putImageData:im=>{pixels=im.data;}
 })};
}};
const ctx=vm.createContext({THREE,console,MODEL_ATELIER_KINDS:['sphere'],document});
vm.runInContext([
 read('model_atelier_face_volume_v11_23.js'),
 read('model_atelier_photo_cutout_v11_55.js'),
 read('model_atelier_face_sheet_v11_23.js')
].join('\n'),ctx);
const good={points:[[.22,.2],[.78,.2],[.78,.8],[.22,.8]],feather:.08};
const original={refId:'image0',shape:'oval',gridU:48,gridV:20,crop:[0,0,1,1],headDepth:0};
const part=faceSheet=>({kind:'faceSheet',faceSheet});
assert(ctx.atelierCutoutValid(good));
assert(ctx.atelierFaceSheetValid(part({...original,cutout:good})));
assert(ctx.atelierFaceSheetValid(part(original)),'legacy face remains valid');
assert(ctx.atelierCutoutWeight([.5,.5],good)>.999);
assert.equal(ctx.atelierCutoutWeight([.02,.5],good),0);
assert(Math.abs(ctx.atelierCutoutWeight([.22,.5],good)-.5)<1e-7);
assert(ctx.atelierCutoutWeight([.24,.5],good)>.5);
assert(ctx.atelierCutoutWeight([.20,.5],good)<.5);
assert.equal(ctx.atelierCutoutWeight([.5,.5],null),1);
assert.equal(ctx.atelierCutoutWeight([.22,.5],{...good,feather:0}),1);
assert.equal(ctx.atelierCutoutWeight([.1,.5],{...good,feather:0}),0);
const wrong=[
 {...good,points:good.points.slice(0,2)},
 {...good,points:[[-.1,.2],[.8,.2],[.8,.8]]},
 {...good,points:[[0,0],[1,1],[0,1],[1,0]]},
 {...good,points:Array(33).fill([.5,.5])},
 {...good,feather:NaN},{...good,feather:.15},
 {...good,points:[[0,0],[0,0],[1,0],[1,1]]},
 {...good,points:[[.5,.5],[.6,.6],[.7,.7]]},
 {...good,bogus:true}
];
for(const bad of wrong){
 assert(!ctx.atelierCutoutValid(bad),'reject invalid or crossing source photo polygons');
 assert(!ctx.atelierFaceSheetValid(part({...original,cutout:bad})));
}
const g1=ctx.atelierFaceSheetGeometry(part(original)),
 g2=ctx.atelierFaceSheetGeometry(part({...original,cutout:good}));
assert.deepEqual(Array.from(g1.attributes.position.array),Array.from(g2.attributes.position.array),
 'Cutout does not alter native source vertices');
assert.deepEqual(Array.from(g1.attributes.uv.array),Array.from(g2.attributes.uv.array),
 'Cutout retains original photo UV');
const materialTexture=ctx.atelierCutoutTexture({id:'test1',faceSheet:{cutout:good}});
assert(materialTexture&&pixels.length===256*256*4,'create real WebGL alphaMap texture');
function green(u,v){const x=Math.floor(u*256),y=Math.floor((1-v)*256);
 return pixels[(y*256+x)*4+1];
}
assert(green(.5,.5)>250,'face texture center remains visible');
assert(green(.01,.5)<5,'background is transparent');
assert(green(.2,.5)>0&&green(.2,.5)<128,'feather is rasterized and partial');
const old=materialTexture;
assert.equal(ctx.atelierCutoutTexture({id:'test1',faceSheet:{cutout:good}}),old,'reuse bounded face mask texture cache');
assert.equal(JSON.stringify(good),JSON.stringify(JSON.parse(JSON.stringify(good))));
console.log('V1155_PHOTO_CUTOUT_BOUNDARY_FEATHER_ALPHA_TEXTURE_UV_NATIVE_SCHEMA_PASS');
