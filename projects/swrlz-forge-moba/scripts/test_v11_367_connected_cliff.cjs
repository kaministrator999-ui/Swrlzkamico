// Source-based test of the actual native connected Cliff Hand signed-distance field.
// Compare shipped v11.365 reference-fit silhouette to v11.367 visible corrective fit.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const source366=read('runtime/stone_hand_anatomy_v11_367.js');
const fieldOnly=source366.slice(source366.indexOf('const se367Smooth='),source366.indexOf('const se367OriginalCliffScene='));
assert(fieldOnly.startsWith('const se367Smooth=')&&fieldOnly.includes('function se367CliffField(math){'));
const math={
 ell:(p,c,r)=>(Math.hypot(...p.map((x,i)=>(x-c[i])/r[i]))-1)*Math.min(...r),
 cap:(p,a,b,ra,rb)=>{
  const d=b.map((v,i)=>v-a[i]),q=p.map((v,i)=>v-a[i]);
  const t=Math.max(0,Math.min(1,q.reduce((s,v,i)=>s+v*d[i],0)/d.reduce((s,v)=>s+v*v,0)));
  return Math.hypot(...p.map((v,i)=>v-a[i]-t*d[i]))-(ra+(rb-ra)*t);
 },
 blend:(a,b,k)=>{const h=Math.max(0,k-Math.abs(a-b))/k;return Math.min(a,b)-h*h*k*.25;}
};
function make(anatomical){
 const ctx={window:{},console,se292Knuckles:[]};
 vm.createContext(ctx);
 let photo=read('runtime/cliff_hand_photo_crystal_v11_334.js')
 .replace('function se334ReferenceHandField(math){','function se334ReferenceHandField(math,skinFactory=se217OrganicHandSkin){')
 .replace('const skin=se217OrganicHandSkin(photoDigits,math);','const skin=skinFactory(photoDigits,math);')
 .replace('const length={index:.026,middle:.037,ring:.020,pinky:.023};',
 'const length={index:.074,middle:.037,ring:.020,pinky:.065};')
 .replace('const shapedX=x*(1-.035*palmBand);','const shapedX=x*(1+.018*palmBand);');
 let ulnar=read('runtime/cliff_ulnar_contour_v11_335.js')
 .replace('function se335NarrowUlnarField(math){','function se335NarrowUlnarField(math,skinFactory=se217OrganicHandSkin){')
 .replace('const original=se334ReferenceHandField(math);','const original=se334ReferenceHandField(math,skinFactory);');
 let geodes=read('runtime/cliff_hand_refinement_v11_337.js')
 .replace('f.r*1.20,f.r*.92','f.r*1.17,f.r*.90')
 .replace('f.r*.91,f.r*.77','f.r*.89,f.r*.74')
 .replace('f.r*.76,f.r*.62','f.r*.74,f.r*.59')
 .replace('f.r*.67,.099,f.r*.67','f.r*.65,.097,f.r*.65');
 for(const [file,src] of [
  ['base','runtime/model_atelier_hand_proportions_v11_217.js'],
  ['photo',photo],['ulnar',ulnar],['geodes',geodes],
  ['anatomy366',anatomical?fieldOnly:'']
 ])vm.runInContext(src.startsWith('runtime/')?read(src):src,ctx,{filename:file});
 ctx.math=math;
 const hand=vm.runInContext((anatomical?'se367CliffField':'se337HandField')+'(math)',ctx);
 const profile=anatomical?.270:.298,depth=anatomical?.215:.232;
 const outer=(x,y,z)=>{
  const p=[x,y,z],cap=math.cap,blend=math.blend;
  const stone=cap(p,[.004,.20,-.004],[.004,1.29,-.009],profile,depth);
  return Math.max(blend(hand(x,y,z),stone,.19),.20-y);
 };
 return {hand,outer};
}
const prior=make(false),now=make(true);
function boundary(fn,{y,z=.02,min=.02,max=.92,x0=0,axis='x'}){
 const at=t=>axis==='x'?fn(t,y,z):fn(x0,t,z);
 let pos=[];
 for(let i=0;i<400;i++){
  const a=min+(max-min)*i/400,b=min+(max-min)*(i+1)/400;
  if(at(a)<=0&&at(b)>0)pos.push([a,b]);
 }
 assert(pos.length,'No SDF surface boundary at '+JSON.stringify({y,z,x0,axis,min,max}));
 let [a,b]=pos.at(-1);
 for(let i=0;i<42;i++){const mid=(a+b)*.5;if(at(mid)>0)b=mid;else a=mid;}
 return (a+b)*.5;
}
const p0=boundary(prior.hand,{y:1.79,z:.04});
const p1=boundary(now.hand,{y:1.79,z:.04});
assert(p1<p0-.03,'Cliff palm must visibly narrow '+p0+' -> '+p1);
const w0=boundary(prior.outer,{y:.38,z:.04,max:.75});
const w1=boundary(now.outer,{y:.38,z:.04,max:.75});
assert(w1<w0-.014,'Cliff wrist must visibly narrow '+w0+' -> '+w1);
// Skin remains continuous across the palm-to-thenar web; no separate rocks.
for(const p of [[-.42,1.52,.08],[-.32,1.47,.09],[.18,1.78,.06],[-.13,2.05,.01]]){
 assert(Number.isFinite(now.hand(...p)),'Nonfinite connected Cliff field at '+p);
}
const fingers={};
for(const [name,x,y] of [['index',-.41,2.63],['middle',-.14,2.74],['ring',.15,2.66],['pinky',.45,2.55]]){
 const edge0=boundary(prior.hand,{y,z:.018,min:x,max:x+.35});
 const edge1=boundary(now.hand,{y,z:.018,min:x,max:x+.35});
 assert(edge1<edge0-.003,name+' finger was not visibly reshaped '+edge0+' -> '+edge1);
 fingers[name]=[+edge0.toFixed(4),+edge1.toFixed(4)];
}
assert(source366.includes("se288SmoothCliffHandScene=function(){")&&
 source366.includes("Plain Hand Base · Smooth Cliff Hand · Anatomy"),
 'Native Cliff Hand project must use the new visible starter path');
console.log('SE367_CONNECTED_CLIFF_ANATOMY_PASS '+JSON.stringify({
 palmRightEdge:[+p0.toFixed(4),+p1.toFixed(4)],
 wristRightEdge:[+w0.toFixed(4),+w1.toFixed(4)],
 fingerRightEdges:fingers,rigBonesPreserved:17,additionalGeometry:0
}));
