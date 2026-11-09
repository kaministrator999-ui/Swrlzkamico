#!/usr/bin/env node
// Focused geometry/rig smoke for the generator. No browser, GPU or game suites.
const fs=require('fs'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'..');
class V {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}
 clone(){return new V(this.x,this.y,this.z)}
 sub(p){this.x-=p.x;this.y-=p.y;this.z-=p.z;return this}
 dot(p){return this.x*p.x+this.y*p.y+this.z*p.z}
 crossVectors(a,b){this.x=a.y*b.z-a.z*b.y;this.y=a.z*b.x-a.x*b.z;this.z=a.x*b.y-a.y*b.x;return this}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}
 normalize(){const n=Math.sqrt(this.lengthSq())||1;this.x/=n;this.y/=n;this.z/=n;return this}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
 addScaledVector(p,n){this.x+=p.x*n;this.y+=p.y*n;this.z+=p.z*n;return this}
}
const ctx=vm.createContext({THREE:{Vector3:V},window:{},console,structuredClone,
 createProjectFromTemplate(){}});
const load=name=>vm.runInContext(fs.readFileSync(path.join(root,'runtime',name),'utf8'),ctx);
load('model_atelier_skeletal_core_v11_220.js');
function se212HandScene(){
 const digits=[
 {name:'index',x:-.397,from:2.17,to:2.99,r:.104,splay:-.055,z:.006},
 {name:'middle',x:-.131,from:2.197,to:3.168,r:.112,splay:-.017,z:-.009},
 {name:'ring',x:.135,from:2.176,to:3.077,r:.103,splay:.028,z:-.009},
 {name:'pinky',x:.402,from:2.113,to:2.791,r:.084,splay:.083,z:.010}
 ];
 return {project:{name:'Original',environmentSettings:{},
  modelAtelier:{name:'Original',parts:[{kind:'topologyMesh',
   organicSurface:{species:'arcane-glove'},
   topologyMesh:{positions:[0,0,0,0,1,0,.2,1,0],uvs:[0,0,0,1,1,1],indices:[0,1,2]}}],
   rigging:se220CreateHandRig(digits)}}};
}
vm.runInContext(se212HandScene.toString(),ctx);
load('rocky_anime_hand_starter_v11_281.js');
load('rock_cliff_hand_v11_282.js');
load('weathered_rock_hand_v11_283.js');
const result=vm.runInContext('se281RockScene()',ctx);
const m=result.project.modelAtelier,p=m.parts;
if(!vm.runInContext('se220RigValidate(se281RockScene().project.modelAtelier.rigging)',ctx))
 throw Error('Rig invalid');
if(m.rigging.bones.length!==17||p.length<80||p.length>230)
 throw Error('Skeleton or part count invalid: '+p.length);
if(p.some(x=>x.organicSurface||/Underlying|glove|smooth/i.test(x.name)))
 throw Error('Organic glove core still exposed in Rocky Starter');
const shafts=p.filter(x=>/^Finger (index|middle|ring|pinky) · solid/.test(x.name));
if(shafts.length!==12)throw Error('Only '+shafts.length+' full-circumference finger shafts');
const thumbs=p.filter(x=>/^Thumb · entire/.test(x.name));
if(thumbs.length!==3)throw Error('Not three solid thumb sections');
const palm=p.find(x=>x.name.startsWith('Cliff foundation'));
if(!palm||palm.topologyMesh.positions.length/3<150)throw Error('Missing faceted rock palm');
for(const section of [...shafts,...thumbs]){
 const t=section.topologyMesh,px=[],pz=[];
 for(let k=0;k<t.positions.length;k+=3){px.push(t.positions[k]);pz.push(t.positions[k+2]);}
 if(Math.max(...px)-Math.min(...px)<.12||Math.max(...pz)-Math.min(...pz)<.12)
  throw Error('Stone segment appears 2D or too thin: '+section.name);
}
const weathered=vm.runInContext('window.SWYRL_ENGINE_WEATHERED_ROCK_HAND.status()',ctx);
if(weathered.meshes<40||weathered.vertices<3500||weathered.triangles<3500)
 throw Error('Weathered mesh pass missing: '+JSON.stringify(weathered));
if(!weathered.noOrganicGlove||weathered.subdivision!==1||
 weathered.relaxation<=0||weathered.relaxation>=.4)
 throw Error('Wrong smoothing strength or visible organic base');
if(new Set(palm.topologyMesh.indices).size===palm.topologyMesh.indices.length)
 throw Error('Weathered palm must weld/share vertices for smooth normals');
const byId=new Map(p.map(x=>[x.id,x]));
if(byId.size!==p.length)throw Error('Rocky hand meshes lost identity');
if(result.version!==11.283||!/11\.283$/.test(result.engine))
 throw Error('Old scene provenance carried into weathered starter');
const ids=new Set(p.map(x=>x.id));
if(ids.size!==p.length)throw Error('Duplicate IDs');
for(const x of p){
 const t=x.topologyMesh,n=t.positions.length/3;
 if(x.kind!=='topologyMesh'||!/^#[0-9a-f]{6}$/i.test(x.color)||
  n<3||t.positions.length%3||t.uvs.length!==n*2||t.indices.length%3||
  !t.positions.every(Number.isFinite)||
  !t.indices.every(i=>Number.isInteger(i)&&i>=0&&i<n))
  throw Error('Bad topology or metadata: '+x.name);
}
for(const group of m.meshGroups)if(group.members.some(id=>!ids.has(id)))
 throw Error('Bad member IDs in '+group.name);
const info={parts:p.length,glowingSeams:p.filter(x=>x.material==='emissive').length,
 bones:m.rigging.bones.length,groups:m.meshGroups.length,
 stoneFingers:shafts.length,solidThumbs:thumbs.length,organicCore:0,valid:true};
if(info.glowingSeams<12)throw Error('Cracked seams missing');
console.log('SE283_WEATHERED_MODEL_SMOKE '+JSON.stringify({...info,weathered}));

// Verify real 89-part baseline and subsequent derived extras without hardcoding it.
load('hand_reference_fit_v11_365.js');
const source=vm.runInContext('se365OriginalStoneScene()',ctx);
const aligned=vm.runInContext('se281RockScene()',ctx);
const baseParts=source.project.modelAtelier.parts,model=aligned.project.modelAtelier;
const sourceRef=JSON.parse(fs.readFileSync(path.join(root,'assets/models/webxr-hands/right.json'),'utf8'));
const joints=Object.fromEntries(sourceRef.joints.map(j=>[j.name,j.position]));
const dist=d=>joints[d+'-finger-tip'][1]-joints[d+'-finger-phalanx-proximal'][1];
const ratios=['index','middle','ring','pinky'].map(d=>dist(d)/dist('middle'));
const targets=[.943,1,.920,.746];
for(let i=0;i<ratios.length;i++)if(Math.abs(ratios[i]-targets[i])>.006)
 throw Error('WebXR anatomical ratio source mismatch '+ratios[i]+' / '+targets[i]);
if(baseParts.length-model.parts.length!==28)throw Error('Decorative pruning not exactly 28');
if(model.rigging.bones.length!==17||!vm.runInContext('se220RigValidate(se281RockScene().project.modelAtelier.rigging)',ctx))
 throw Error('17-bone rock rig was not preserved');
for(const token of ['Cliff foundation','Finger index · solid','Finger middle · solid','Finger ring · solid','Finger pinky · solid','Thumb · entire']){
 if(!model.parts.some(p=>p.name.includes(token)))throw Error('Lost structural rock part '+token);
}
if(model.parts.filter(p=>/^Finger (index|middle|ring|pinky) · solid/.test(p.name)).length!==12)
 throw Error('Lost native finger articulation');
if(model.parts.filter(p=>/^Thumb · entire/.test(p.name)).length!==3)
 throw Error('Lost native 3-section thumb');
for(const entry of model.parts){
 const t=entry.topologyMesh,n=t.positions.length/3;
 if(n<3||t.indices.length%3||t.uvs.length!==n*2||
    !t.positions.every(Number.isFinite)||!t.indices.every(v=>Number.isInteger(v)&&v>=0&&v<n))
  throw Error('Invalid refined native mesh '+entry.name);
}
const ids2=new Set(model.parts.map(p=>p.id));
for(const g of model.meshGroups){
 if(g.members.length<2||g.members.some(id=>!ids2.has(id)))
  throw Error('Invalid new rock model group '+g.name);
}
const baseFinger=baseParts.find(p=>p.name==='Finger index · solid root cliff rock');
const newFinger=model.parts.find(p=>p.name==='Finger index · solid root cliff rock');
if(!baseFinger||!newFinger)throw Error('Could not compare anatomical finger radii');
function bbox(points){let min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];for(let i=0;i<points.length;i+=3)for(let j=0;j<3;j++){min[j]=Math.min(min[j],points[i+j]);max[j]=Math.max(max[j],points[i+j]);}return min.map((v,j)=>max[j]-v)}
const a=bbox(baseFinger.topologyMesh.positions),b=bbox(newFinger.topologyMesh.positions);
if(b[0]>=a[0]||b[2]>=a[2])throw Error('Rock fingers did not narrow in both dimensions');
const state=vm.runInContext('window.SWYRL_ENGINE_HAND_REFERENCE_FIT_365.rock()',ctx);
if(state.removedByCategory.palm!==10||state.removedByCategory.side!==8||
 state.removedByCategory.fingerChips!==8||state.removedByCategory.wrist!==2)
 throw Error('Decorative rock pruning categories changed');
console.log('SE365_ROCK_REFERENCE_FIT_PASS '+JSON.stringify({
 original:baseParts.length,refined:model.parts.length,removed:state.removedByCategory,
 ratios:ratios.map(n=>+n.toFixed(3)),widthBefore:a[0],widthAfter:b[0],
 depthBefore:a[2],depthAfter:b[2],bones:17,parts:model.parts.length
}));
