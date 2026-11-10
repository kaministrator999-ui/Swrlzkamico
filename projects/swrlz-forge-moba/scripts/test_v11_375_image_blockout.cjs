// Fast, model-free regression: five view silhouettes produce editable native lofts.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../runtime/model_image_blockout_v11_375.js'),'utf8');
const W=960,H=720,pixels=new Uint8ClampedArray(W*H*4);
for(let y=0;y<H;y++)for(let x=0;x<W;x++){
 const i=(y*W+x)*4;pixels[i]=254;pixels[i+1]=244;pixels[i+2]=239;pixels[i+3]=255;
}
function solid(cx,half,minY,maxY,color){
 for(let y=Math.floor(minY*H);y<=Math.floor(maxY*H);y++)
 for(let x=Math.floor((cx-half)*W);x<Math.floor((cx+half)*W);x++){
  const i=(y*W+x)*4;pixels[i]=color[0];pixels[i+1]=color[1];pixels[i+2]=color[2];
 }
}
for(const [cx,hw] of [[.143,.053],[.329,.047],[.475,.047],[.692,.063]]){
 solid(cx,hw,.153,.61,[112,62,139]);
}
solid(.897,.060,.29,.46,[120,68,153]);
solid(.04,.012,.23,.607,[85,57,40]);
const status={textContent:'',dataset:{}},button={disabled:false};
const document={
 documentElement:null,
 getElementById:id=>id==='se375Prop'?{checked:true}:id==='se375Status'?status:id==='se375Generate'?button:null
};
const fakeCanvas={width:W,height:H,getContext:()=>({getImageData:()=>({data:pixels})})};
const sandbox={document,MutationObserver:class{observe(){} disconnect(){}},queueMicrotask(){},console,
 currentProject:{kind:'sandbox'},ModelAtelier:{status:()=>({open:false})},requestAnimationFrame:f=>f()};
vm.createContext(sandbox);vm.runInContext(source,sandbox,{filename:'model_image_blockout_v11_375.js'});
sandbox.fakeCanvas=fakeCanvas;
vm.runInContext('se375Canvas = fakeCanvas;',sandbox);
const parts=vm.runInContext('se375Blockout()',sandbox);
assert(parts.length>=4&&parts.length<=6);
for(const part of parts){
 assert.equal(part.op,'mesh.add');assert.equal(part.kind,'loft');
 assert(part.path.length>=2&&part.path.length<=40);
 assert.equal(part.path.length,part.radii.length);
 assert(part.path.every(row=>row.length===3&&row.every(Number.isFinite)));
 assert(part.radii.every(v=>v>0&&v<=5));
 assert(/^#[0-9a-f]{6}$/i.test(part.color));
}
assert(parts.some(p=>p.name.includes('detached side prop')),'separate prop should be detected');
vm.runInContext("se375Guides.left = .94;",sandbox);
assert.throws(()=>vm.runInContext('se375Blockout()',sandbox),/silhouettes|guides/);
vm.runInContext("se375Guides.left = .329;",sandbox);
(async()=>{
 await vm.runInContext('se375Run()',sandbox);
 assert.match(status.textContent,/Blank 3D model/);
 console.log('v11.375: five-view editable geometry, prop and blank-only gate PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
