// v11.378 source-backed rough 3D regression: stable 2D-driven lofts.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const read=f=>fs.readFileSync(path.join(__dirname,'../runtime/',f),'utf8');
const W=960,H=720,pixels=new Uint8ClampedArray(W*H*4);
for(let i=0;i<pixels.length;i+=4){pixels[i]=251;pixels[i+1]=245;pixels[i+2]=239;pixels[i+3]=255;}
function fill(cx,y0,y1,w){
 for(let y=Math.floor(y0*H);y<Math.ceil(y1*H);y++)for(let x=Math.floor((cx-w)*W);x<Math.ceil((cx+w)*W);x++){
  const j=(y*W+x)*4;pixels[j]=105;pixels[j+1]=67;pixels[j+2]=151;
 }
}
fill(.143,.15,.62,.055);fill(.329,.15,.62,.038);fill(.475,.15,.62,.042);
const fakeCanvas={width:W,height:H,getContext:()=>({getImageData:()=>({data:pixels})})};
const sandbox={document:{documentElement:null,getElementById(id){return id==='se375Prop'?{checked:false}:null;}},
 MutationObserver:class{observe(){}disconnect(){}},queueMicrotask(){},requestAnimationFrame:f=>f(),
 console,Math,Array,Uint8Array,Uint8ClampedArray,Map,Set,Int32Array};
vm.createContext(sandbox);
for(const name of ['model_image_blockout_v11_375.js','model_image_outlines_v11_377.js','model_image_stable_lofts_v11_378.js'])
 vm.runInContext(read(name),sandbox,{filename:name});
vm.runInContext('se375Canvas=fakeCanvas;',Object.assign(sandbox,{fakeCanvas}));
function outline(cx,top,bottom,upper,lower){
 return [[cx-upper,top],[cx+upper,top],[cx+upper*.8,top+.1],[cx+lower,bottom],[cx-lower,bottom],[cx-upper*.8,top+.1]];
}
function setRegions(front,side,right){
 sandbox.polys=JSON.stringify([
  {id:'f',name:'Main',kind:'silhouette',view:'Front',visible:true,size:1000,points:front},
  {id:'l',name:'Main',kind:'silhouette',view:'Left',visible:true,size:800,points:side},
  {id:'r',name:'Main',kind:'silhouette',view:'Right',visible:true,size:800,points:right}
 ]);
 vm.runInContext('se377.regions=JSON.parse(polys);',sandbox);
}
setRegions(outline(.143,.15,.62,.052,.072),outline(.329,.20,.63,.035,.045),outline(.475,.16,.61,.045,.046));
let parts=vm.runInContext('se375Blockout()',sandbox);
assert.equal(parts.length,3,'split into three nonoverlapping named pieces');
for(const part of parts){
 assert.equal(part.op,'mesh.add');assert.equal(part.kind,'loft');
 assert.equal(part.position.join(','),'0,0,0');
 assert(part.path.length<=40&&part.path.length>=10);
 assert(part.path.every(p=>p.length===3&&p.every(Number.isFinite)&&p[2]===0&&Math.abs(p[0])<=.15));
 assert(part.path.every((p,i)=>!i||p[1]<part.path[i-1][1]),'one stable descending vertical centerline');
 assert(part.radii.every(r=>r>.02&&r<=1.12));
 assert(part.scale[2]>=.57&&part.scale[2]<=.90);
 assert.equal(part.material,'matte');
}
assert(parts[0].path.at(-1)[1]>parts[1].path[0][1],'upper and middle do not overlap');
assert(parts[1].path.at(-1)[1]>parts[2].path[0][1],'middle and lower do not overlap');
const baseline=JSON.stringify(parts);
// Side image x offset cannot cause twisted / off-center geometry.
setRegions(outline(.143,.15,.62,.052,.072),outline(.61,.20,.63,.035,.045),outline(.75,.16,.61,.045,.046));
parts=vm.runInContext('se375Blockout()',sandbox);
assert.equal(JSON.stringify(parts.map(p=>p.path)),JSON.stringify(JSON.parse(baseline).map(p=>p.path)));
vm.runInContext('se377.regions=[];',sandbox);
assert.throws(()=>vm.runInContext('se375Blockout()',sandbox),/Front silhouette/);
console.log('v11.378: three stable independently editable 3D lofts, side-depth cues, no corkscrew, 2D source safety PASS');
