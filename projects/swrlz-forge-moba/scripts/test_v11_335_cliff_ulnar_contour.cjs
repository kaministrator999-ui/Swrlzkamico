// Focused geometry proof using the ACTUAL §E photo-hand signed distance field.
// Test the full source fields rather than a mock of the narrowing algorithm.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const scope={window:{},console,se292Knuckles:[]};
vm.createContext(scope);
for(const file of [
 'runtime/model_atelier_hand_proportions_v11_217.js',
 'runtime/cliff_hand_photo_crystal_v11_334.js',
 'runtime/cliff_ulnar_contour_v11_335.js']){
 vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),scope,{filename:file});
}
const math={
 ell:(p,c,r)=>(Math.hypot(...p.map((x,i)=>(x-c[i])/r[i]))-1)*Math.min(...r),
 cap:(p,a,b,ra,rb)=>{
  const d=b.map((x,i)=>x-a[i]),q=p.map((x,i)=>x-a[i]);
  const k=Math.max(0,Math.min(1,q.reduce((s,x,i)=>s+x*d[i],0)/d.reduce((s,x)=>s+x*x,0)));
  return Math.hypot(...p.map((x,i)=>x-a[i]-k*d[i]))-(ra+(rb-ra)*k);
 },
 blend:(a,b,k)=>{
  const h=Math.max(0,k-Math.abs(a-b))/k;
  return Math.min(a,b)-h*h*k*.25;
 }
};
scope.math=math;
const oldField=vm.runInContext('se334ReferenceHandField(math)',scope);
const newField=vm.runInContext('se335NarrowUlnarField(math)',scope);
function edge(fn,y,z){
 let lo=.15,hi=.9;
 assert(fn(lo,y,z)<0,'sample must be inside palm at '+y+','+z);
 assert(fn(hi,y,z)>0,'sample must be outside palm at '+y+','+z);
 for(let j=0;j<50;j++){
  const mid=(lo+hi)/2;
  if(fn(mid,y,z)>0)hi=mid;else lo=mid;
 }
 return (lo+hi)/2;
}
const samples=[];
for(const y of [1.36,1.56,1.74,1.92,2.06,2.14]){
 for(const z of [-.065,.06]){
  const before=edge(oldField,y,z),after=edge(newField,y,z),inward=before-after;
  assert(inward>=-.00001,'new ulnar edge widened unexpectedly');
  samples.push({y,z,before:+before.toFixed(4),after:+after.toFixed(4),
    inward:+inward.toFixed(4)});
 }
}
for(const y of [1.56,1.74,1.92]){
 const sample=samples.find(x=>x.y===y&&x.z===.06);
 assert(sample.inward>=.045,'pinky-side palm should be measurably straighter at y '+y+': '+JSON.stringify(sample));
}
for(const y of [1.15,2.32,2.7]){
 for(const x of [-.65,-.3,.18,.42,.58]){
  for(const z of [-.07,.07])
   assert.equal(newField(x,y,z),oldField(x,y,z),
     'wrist/finger roots were changed at '+JSON.stringify({x,y,z}));
 }
}
// Thumb side is unchanged at every palm height.
for(const y of [1.3,1.5,1.7,2.05]){
 for(const x of [-1.05,-.6,-.4,-.1,0]){
  assert.equal(newField(x,y,.08),oldField(x,y,.08),
     'thumb side must be identical at '+JSON.stringify({x,y}));
 }
}
const state=scope.window.SWYRL_ENGINE_CLIFF_ULNAR_335.status();
assert.equal(state.meshObjectsAdded,0);
assert.equal(state.maximumInwardShift,.105);
console.log('SE335_REAL_SDF_ULNAR_CONTOUR_PASS',JSON.stringify({
 samples,geometryAdded:state.meshObjectsAdded,thumbSideUntouched:true,
 restingFingerAndWristUnchanged:true,nearStraightPinkyEdge:true
}));
