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
console.log('SE281_MODEL_SMOKE '+JSON.stringify(info));
