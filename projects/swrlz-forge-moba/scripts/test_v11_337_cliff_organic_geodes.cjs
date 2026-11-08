// §E v11.337: source-exact geometric regression using original and newly injected fields.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const scope={console,window:{},se292Knuckles:[
 {u:.454,v:.648,twist:-.15},{u:.592,v:.654,twist:.08},
 {u:.738,v:.644,twist:-.09},{u:.868,v:.625,twist:.13}]};
vm.createContext(scope);
for(const f of ['runtime/model_atelier_hand_proportions_v11_217.js',
 'runtime/cliff_hand_photo_crystal_v11_334.js',
 'runtime/cliff_ulnar_contour_v11_335.js',
 'runtime/cliff_hand_refinement_v11_337.js']){
  vm.runInContext(fs.readFileSync(path.join(root,f),'utf8'),scope,{filename:f});
}
const math={
 ell:(p,c,r)=>(Math.hypot(...p.map((x,i)=>(x-c[i])/r[i]))-1)*Math.min(...r),
 cap:(p,a,b,ra,rb)=>{
  const d=b.map((v,i)=>v-a[i]),q=p.map((v,i)=>v-a[i]);
  const k=Math.max(0,Math.min(1,q.reduce((t,v,i)=>t+v*d[i],0)/d.reduce((t,v)=>t+v*v,0)));
  return Math.hypot(...p.map((v,i)=>v-a[i]-k*d[i]))-(ra+(rb-ra)*k);
 },
 blend:(a,b,k)=>{const h=Math.max(0,k-Math.abs(a-b))/k;return Math.min(a,b)-h*h*k*.25;}
};
scope.math=math;
const oldField=vm.runInContext('se335NarrowUlnarField(math)',scope);
const updated=vm.runInContext('se337HandField(math)',scope);
function edge(fn,y,z,lo=.12,hi=.9){
 assert(fn(lo,y,z)<0,'must be inside at '+JSON.stringify({lo,y,z}));
 assert(fn(hi,y,z)>0,'must be outside at '+JSON.stringify({hi,y,z}));
 for(let i=0;i<48;i++){
  const mid=(lo+hi)/2;
  if(fn(mid,y,z)>0)hi=mid;else lo=mid;
 }
 return (lo+hi)*.5;
}
const samples=[];
for(const y of [1.16,1.25,1.36,1.45,1.56,1.74,1.95,2.27]){
 const a=edge(oldField,y,.06),b=edge(updated,y,.06);
 samples.push({y,old:+a.toFixed(5),new:+b.toFixed(5),
   shifted:+(a-b).toFixed(5)});
 assert(b<=a+.001,'lower ulnar must not widen at '+y);
}
for(const y of [1.36,1.45]){
 const s=samples.find(x=>x.y===y);
 assert(s.shifted>.065,'heel of palm must curve inward rather than form a lump '+JSON.stringify(s));
}
const x=(y)=>samples.find(s=>s.y===y).new;
assert(x(1.36)+.024<x(1.56),'ulnar edge should curve outward naturally as it approaches the palm');
assert(Math.abs(samples.find(s=>s.y===1.74).shifted)<.003,
   'do not narrow pinky roots or upper palm');
for(const y of [1.05,1.30,1.55,1.85,2.16,2.65]){
 for(const x0 of [-1.0,-.75,-.52,-.28,-.08,0]){
   const a=oldField(x0,y,.08),b=updated(x0,y,.08);
   assert(Math.abs(a-b)<1e-9,'thumb-side field changed '+JSON.stringify({x0,y,a,b}));
 }
}
const fingers=vm.runInContext('se217FingerSpec.map(d=>({...d}))',scope);
for(const d of fingers){d.to+=({index:.026,middle:.037,ring:.020,pinky:.023})[d.name];
 d.splay+=({index:-.012,middle:-.003,ring:.005,pinky:.011})[d.name]}
const oldSkin=vm.runInContext('se217OrganicHandSkin(fingers,math)',Object.assign(scope,{fingers}));
const newSkin=vm.runInContext('se337OrganicFingerSkin(fingers,math)',scope);
const tipChanges=fingers.map(f=>{
 const x0=f.x+f.splay,tip=f.to-.083;
 const points=[tip-.115,tip-.06,tip,tip+.052,tip+.090];
 const samples=points.map(y=>({y,old:oldSkin(x0,y,f.z+.018),
   next:newSkin(x0,y,f.z+.018)}));
 assert(samples.every(s=>Number.isFinite(s.next)),'invalid fingertip SDF '+f.name);
 assert(samples.some(s=>Math.abs(s.old-s.next)>.00015),
  'PIP/DIP/tip shaping has not actually changed '+f.name);
 return {finger:f.name,delta:samples.map(s=>+(s.old-s.next).toFixed(5))};
});
const status=scope.window.SWYRL_ENGINE_CLIFF_HAND_337.status();
assert.equal(status.additionalGeometry,0);
assert.equal(status.crystalInlays,4);
console.log('SE337_HAND_SHAPE_PASS',JSON.stringify({edgeSamples:samples,
 tipChanges,crystals:status.crystalInlays,geometryAdded:0,thumbPreserved:true}));
