// §E v11.377: 2D tracing is local, editable, view-bounded, and separate from 3D.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../runtime/model_image_outlines_v11_377.js'),'utf8');
assert(source.includes('se375Load=async function(file)'), 'import must trace after loading');
assert(source.includes('Experimental old rough 3D blockout'),'original loft workflow must stay opt-in');
assert(source.includes('Export 2D SVG'),'vector export control should be present');
const cut=source.indexOf('const se377DrawOriginal=');
assert(cut>0);
const W=800,H=600,rgba=new Uint8ClampedArray(W*H*4);
for(let i=0;i<rgba.length;i+=4){rgba[i]=255;rgba[i+1]=249;rgba[i+2]=243;rgba[i+3]=255;}
function rect(x0,y0,x1,y1,color){
 for(let y=Math.floor(y0*H);y<Math.ceil(y1*H);y++)for(let x=Math.floor(x0*W);x<Math.ceil(x1*W);x++){
  const i=(y*W+x)*4;rgba[i]=color[0];rgba[i+1]=color[1];rgba[i+2]=color[2];
 }
}
// Simulated hood, robe, hair and contrasting golden trim within the front guide.
rect(.09,.18,.19,.32,[106,55,143]);
rect(.07,.32,.21,.57,[115,63,156]);
rect(.132,.205,.153,.30,[238,222,188]);
rect(.075,.36,.205,.385,[224,176,68]);
const sandbox={Math,Uint8Array,Int32Array,Set,Map,Array,Number,document:{getElementById:()=>null},
 se375Canvas:{width:W,height:H},se375Id:()=>null,se375Note:()=>{},
 se375Foreground:(data,x,y,w,h,bg)=>{
  if(x<0||y<0||x>=w||y>=h)return false;
  const i=(y*w+x)*4;return Math.hypot(data[i]-bg[0],data[i+1]-bg[1],data[i+2]-bg[2])>46;
 }};
vm.createContext(sandbox);vm.runInContext(source.slice(0,cut),sandbox);
const box={name:'Front',x:.05,y:.13,w:.20,h:.52},bg=[255,249,243];
const regions=vm.runInContext('se377TraceView',sandbox)(box,rgba,bg);
assert(regions.length>=2,'should find silhouette plus visible colored details');
assert(regions.some(r=>r.kind==='silhouette'),'outer silhouette required');
assert(regions.some(r=>r.kind==='detail'),'color-based subregion required');
for(const r of regions){
 assert(r.points.length>=3&&r.points.length<=128);
 assert(r.points.every(([x,y])=>x>=box.x-.001&&x<=box.x+box.w+.001&&y>=box.y-.001&&y<=box.y+box.h+.001));
 assert(Math.abs(vm.runInContext('se377Area',sandbox)(r.points))>0);
}
const p=regions[0].points;
const area=vm.runInContext('se377InPoly',sandbox)([.14,.24],p);
assert.equal(typeof area,'boolean');
console.log('v11.377 2D outlines: local segmentation, vector bounds, edit helpers, old 3D opt-in PASS');
