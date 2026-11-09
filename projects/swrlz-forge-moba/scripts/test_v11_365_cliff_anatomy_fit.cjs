#!/usr/bin/env node
// Source-exact SDF comparison: old Cliff Hand and the v11.365 corrections.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const constants={joints:JSON.parse(read('assets/models/webxr-hands/right.json')).joints};
function build(improved){
 const ctx={console,window:{},se292Knuckles:[],...constants};
 vm.createContext(ctx);
 let a=read('runtime/model_atelier_hand_proportions_v11_217.js');
 let b=read('runtime/cliff_hand_photo_crystal_v11_334.js')
    .replace('function se334ReferenceHandField(math){','function se334ReferenceHandField(math,skinFactory=se217OrganicHandSkin){')
    .replace('const skin=se217OrganicHandSkin(photoDigits,math);','const skin=skinFactory(photoDigits,math);');
 let c=read('runtime/cliff_ulnar_contour_v11_335.js')
    .replace('function se335NarrowUlnarField(math){','function se335NarrowUlnarField(math,skinFactory=se217OrganicHandSkin){')
    .replace('const original=se334ReferenceHandField(math);','const original=se334ReferenceHandField(math,skinFactory);');
 let d=read('runtime/cliff_hand_refinement_v11_337.js');
 let forearm=read('runtime/cliff_gauntlet_surface_material_v11_290.js')
    .replace('const hand=se217OrganicHandSkin(se217FingerSpec,math);',
             'const hand=se337HandField(math);');
 if(improved){
  b=b.replace('const length={index:.026,middle:.037,ring:.020,pinky:.023};',
              'const length={index:.074,middle:.037,ring:.020,pinky:.065};')
     .replace('const shapedX=x*(1-.035*palmBand);',
              'const shapedX=x*(1+.018*palmBand);');
  d=d.replace('f.r*1.20,f.r*.92','f.r*1.17,f.r*.90')
     .replace('f.r*.91,f.r*.77','f.r*.89,f.r*.74')
     .replace('f.r*.76,f.r*.62','f.r*.74,f.r*.59')
     .replace('f.r*.67,.099,f.r*.67','f.r*.65,.097,f.r*.65');
  forearm=forearm.replace('const forearm=cap(p,[.004,.20,-.004],[.004,1.29,-.009],.322,.232);',
    'const forearm=cap(p,[.004,.20,-.004],[.004,1.29,-.009],.298,.232);');
 }
 for(const [name,script] of [['hand-proportions',a],['photo',b],['ulnar',c],
   ['finger',d],['forearm',forearm]])
  vm.runInContext(script,ctx,{filename:name});
 return {
  hand:vm.runInContext('se337HandField(se290Math())',ctx),
  gauntlet:vm.runInContext('se290GauntletField()',ctx)
 };
}
const old=build(false),now=build(true);
function edge(field,{axis='x',fixedX=0,y,z=.02,lo,hi}){
 let get=t=>field(axis==='x'?t:fixedX,axis==='y'?t:y,z);
 // Scan for the furthest inside-to-outside transition.
 let candidates=[];
 for(let i=0;i<300;i++){
  const a=lo+(hi-lo)*i/300,b=lo+(hi-lo)*(i+1)/300;
  if(get(a)<=0&&get(b)>0)candidates.push([a,b]);
 }
 assert(candidates.length,'No positive material transition at '+JSON.stringify({axis,fixedX,y,z,lo,hi}));
 let [a,b]=candidates.at(-1);
 for(let i=0;i<38;i++){const mid=(a+b)/2;if(get(mid)>0)b=mid;else a=mid;}
 return (a+b)/2;
}
const ratios=Object.fromEntries(['index','middle','ring','pinky'].map(name=>{
 const j=Object.fromEntries(constants.joints.map(x=>[x.name,x.position]));
 return [name,(j[name+'-finger-tip'][1]-j[name+'-finger-phalanx-proximal'][1])/
  (j['middle-finger-tip'][1]-j['middle-finger-phalanx-proximal'][1])];
}));
assert(Math.abs(ratios.index-.943)<.006&&Math.abs(ratios.ring-.920)<.006&&
 Math.abs(ratios.pinky-.746)<.006,'WebXR ratios changed');
const palmOld=edge(old.hand,{y:1.8,lo:.05,hi:1.2}),palmNew=edge(now.hand,{y:1.8,lo:.05,hi:1.2});
assert(palmNew<palmOld-.005,'Cliff metacarpal palm did not narrow');
const wristOld=edge(old.gauntlet,{y:.43,lo:.05,hi:.8}),wristNew=edge(now.gauntlet,{y:.43,lo:.05,hi:.8});
assert(wristNew<wristOld-.003,'Cliff wrist did not narrow');
const tipResults={};
for(const [name,x] of [['index',-.412],['middle',-.14],['ring',.15],['pinky',.46]]){
 const oldTip=edge(old.hand,{axis:'y',fixedX:x,lo:2.4,hi:3.4,z:.03});
 const newTip=edge(now.hand,{axis:'y',fixedX:x,lo:2.4,hi:3.4,z:.03});
 tipResults[name]={old:+oldTip.toFixed(4),new:+newTip.toFixed(4)};
 if(name==='index'||name==='pinky')
  assert(newTip>oldTip+.012,'Cliff '+name+' tip did not lengthen');
 else
  assert(Math.abs(newTip-oldTip)<.015,'Middle/ring length was not retained');
}
assert.equal(typeof now.hand,'function');
console.log('SE365_CLIFF_REFERENCE_FIT_PASS '+JSON.stringify({
 ratios,palmWidth:[+palmOld.toFixed(4),+palmNew.toFixed(4)],
 wristWidth:[+wristOld.toFixed(4),+wristNew.toFixed(4)],
 fingerTipYs:tipResults,independentStoneMeshesAdded:0
}));
