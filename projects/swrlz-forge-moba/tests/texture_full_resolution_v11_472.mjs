// §E 11.472: verify byte-preserving native imports and optional GPU-only resampling.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../runtime/texture_full_resolution_v11_472.js',import.meta.url),'utf8');
new vm.Script(source);
const sizes=new Map();
const statusMessages=[];
let image=null,selectedId='mesh1',checkpoints=0,changed=0,previewCount=0,filterCalls=0;
const part={id:'mesh1',name:'UFO',kind:'sphere',scale:[1,.3,1],color:'#ffffff',material:'metal'};
const vec=()=>({x:0,y:0,set(x,y){this.x=x;this.y=y;},copy(v){this.x=v.x;this.y=v.y;return this;}});
class FakeTexture{
 constructor(){this.isTexture=true;this.center=vec();this.offset=vec();this.repeat=vec();this.repeat.set(1,1);this.userData={};this.disposed=false;}
 dispose(){this.disposed=true;}
}
class FakeImage{
 set src(value){
  this._src=value;
  const info=sizes.get(value);
  Promise.resolve().then(()=>{
   if(info){this.naturalWidth=info[0];this.naturalHeight=info[1];this.onload?.();}
   else this.onerror?.();
  });
 }
 get src(){return this._src;}
}
class FakeReader{
 readAsDataURL(file){
  Promise.resolve().then(()=>{
   if(file.fail){this.onerror?.();}
   else{this.result=file.dataURL;this.onload?.();}
  });
 }
}
const nativeMaterial=()=>({map:new FakeTexture(),needsUpdate:false});
const sandbox={
 THREE:{SRGBColorSpace:'srgb',RepeatWrapping:1000,LinearFilter:1001,
  LinearMipmapLinearFilter:1002,Texture:FakeTexture},
 Image:FakeImage,FileReader:FakeReader,
 renderer:{capabilities:{getMaxAnisotropy:()=>16}},
 document:{createElement(tag){
  if(tag!=='canvas')throw Error('Unexpected DOM tag '+tag);
  return {width:1,height:1,
   getContext(){return {imageSmoothingEnabled:false,imageSmoothingQuality:'low',
    drawImage(){filterCalls++;}};}};
 }},
 window:{SWYRL_ENGINE_VIEW_READABILITY_455:{choose:()=>true}},
 material:nativeMaterial,
 checkPart:p=>(!p.uvPaintPNG||
    (p.uvPaintPNG.length<=7000000&&/^data:image\/(?:png|jpeg);base64,[A-Za-z0-9+/=]+$/.test(p.uvPaintPNG))),
 se336ImportPaint:async()=>{throw Error('Legacy resampling should never run');},
 se336RemovePaint:()=>{delete part.uvPaintPNG;},
 se336InstallUI:()=>{},se336UpdateUI:()=>{},
 se336SelectedMesh:()=>selectedId?{part,mesh:{material:{map:new FakeTexture()}}}:null,
 se336UVLayout:()=>({triangles:1}),partById:id=>id==='mesh1'?part:null,
 selection:'mesh1',
 modelRoot:{children:[{isMesh:true,userData:{atelierId:'mesh1'},material:{map:new FakeTexture()}}]},
 checkpoint:()=>{checkpoints++;},
 signalEdited:()=>{changed++;},
 select:()=>{},se336SlideNotify:()=>{},
 se356UVPreviewSchedule:()=>{previewCount++;},
 status:(message,error)=>{statusMessages.push({message,error:!!error});},
 historyStep:()=>{throw Error('Unexpected undo rollback');},
};
const api=vm.runInNewContext(source+'\n({import:se336ImportPaint,displaySize:se472DisplaySize,validate:checkPart,material:material})',sandbox);
const png='data:image/png;base64,'+'A'.repeat(1_600_000);
sizes.set(png,[1248,1248]);
const pngFile={type:'image/png',size:1_200_000,dataURL:png};
assert.equal(await api.import(pngFile),true,'Original PNG import should succeed without conversion');
assert.equal(part.uvPaintPNG,png,'PNG source bytes must be byte-identical');
assert.equal(part.uvPaintSourceW,1248);
assert.equal(part.uvPaintSourceH,1248);
assert.equal(part.uvPaintMaxSize,0);
assert.deepEqual(Array.from(api.displaySize(part)),[1248,1248]);
assert.equal(checkpoints,1);
assert.equal(changed,1);
assert.equal(filterCalls,0,'Original import must not draw a resize canvas');
assert(api.validate(part));
part.uvPaintMaxSize=512;
assert.deepEqual(Array.from(api.displaySize(part)),[512,512]);
api.material(part);
await Promise.resolve();await Promise.resolve();
assert.equal(filterCalls,1,'Explicit display reduction should draw one scaled canvas');
assert.equal(part.uvPaintPNG,png,'Changing the view resolution cannot touch source bytes');
part.uvPaintMaxSize=0;
assert.deepEqual(Array.from(api.displaySize(part)),[1248,1248]);
api.material(part);
assert.equal(filterCalls,1,'Original must bypass resampling even after a reduction');
const jpeg='data:image/jpeg;base64,'+'B'.repeat(2_500_000);
sizes.set(jpeg,[2048,1024]);
assert.equal(await api.import({type:'image/jpeg',size:1_875_000,dataURL:jpeg}),true);
assert.equal(part.uvPaintPNG,jpeg,'JPEG must be saved as JPEG, not converted into PNG');
assert.deepEqual(Array.from(api.displaySize(part)),[2048,1024]);
part.uvPaintMaxSize=1024;
assert.deepEqual(Array.from(api.displaySize(part)),[1024,512]);
part.uvPaintMaxSize=4096;
assert.deepEqual(Array.from(api.displaySize(part)),[2048,1024],'Never upscale');
const before=part.uvPaintPNG;
assert.equal(await api.import({type:'image/png',size:5_100_000,dataURL:png}),false);
assert.equal(part.uvPaintPNG,before,'An invalid import must leave the current texture unchanged');
assert(statusMessages.some(x=>x.message.includes('ORIGINAL 1248 × 1248')));
assert(statusMessages.some(x=>x.message.includes('No image will be silently resized')));
console.log('SE472_TEXTURE_FULL_RES_PASS: original PNG/JPEG bytes preserved; size presets viewport-only; aspect maintained; rejected imports unchanged');
