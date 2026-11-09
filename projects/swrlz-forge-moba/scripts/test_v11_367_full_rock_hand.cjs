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


load('hand_reference_fit_v11_365.js');
load('stone_hand_anatomy_v11_367.js');
const original=vm.runInContext('se365OriginalStoneScene()',ctx);
const corrected=vm.runInContext('se281RockScene()',ctx);
const old=original.project.modelAtelier.parts, next=corrected.project.modelAtelier.parts;
if(old.length!==89||next.length!==old.length)
 throw Error('Do not remove the rocks: '+old.length+' -> '+next.length);
const classifications=[
 {name:'palm strata',rx:/^(Palm|Back) · cliff stratum/,expected:20},
 {name:'side rocks',rx:/side · overhanging cliff block/,expected:10},
 {name:'finger chips',rx:/^Finger .* · jutting outer rock/,expected:12},
 {name:'stone finger shafts',rx:/^Finger .* · solid/,expected:12},
 {name:'stone thumb sections',rx:/^Thumb · entire/,expected:3},
 {name:'wrist stones',rx:/^Wrist root/,expected:6}
];
for(const c of classifications){
 const prev=old.filter(p=>c.rx.test(p.name)).length;
 const now=next.filter(p=>c.rx.test(p.name)).length;
 if(prev!==c.expected||now!==c.expected)throw Error(c.name+' was lost '+prev+' '+now);
}
const b=new Map(old.map(x=>[x.id,x]));
function range(mesh,axis){
 const values=[];for(let i=axis;i<mesh.positions.length;i+=3)values.push(mesh.positions[i]);
 return [Math.min(...values),Math.max(...values)];
}
const anatomy={};
for(const key of ['Cliff foundation · entire faceted palm and deep jagged sides',
 'Finger index · solid root cliff rock',
 'Finger middle · solid root cliff rock',
 'Finger ring · solid root cliff rock',
 'Finger pinky · solid root cliff rock',
 'Thumb · entire base cliff stone']){
 const fresh=next.find(x=>x.name===key),before=old.find(x=>x.name===key);
 if(!fresh||!before)throw Error('Missing anatomical stone '+key);
 const oldWidth=range(before.topologyMesh,0);
 const newWidth=range(fresh.topologyMesh,0);
 const oldDepth=range(before.topologyMesh,2);
 const newDepth=range(fresh.topologyMesh,2);
 if(newWidth[1]-newWidth[0]>=(oldWidth[1]-oldWidth[0])*.93||
    newDepth[1]-newDepth[0]>=(oldDepth[1]-oldDepth[0])*.93)
  throw Error('Stone anatomy not effectively slimmed: '+key);
 anatomy[key]={oldWidth:+(oldWidth[1]-oldWidth[0]).toFixed(3),
    newWidth:+(newWidth[1]-newWidth[0]).toFixed(3)};
}
let changed=0;
for(const part of next){
 const before=b.get(part.id);
 if(!before||before.name!==part.name||!part.topologyMesh?.indices||
    part.topologyMesh.uvs.length!==part.topologyMesh.positions.length/3*2)
  throw Error('Native rock topology mutated incorrectly '+part.name);
 const topology=part.topologyMesh,oldMesh=before.topologyMesh;
 if(topology.indices.length!==oldMesh.indices.length||topology.uvs.length!==oldMesh.uvs.length||
    topology.indices.some((id,j)=>id!==oldMesh.indices[j])||
    topology.uvs.some((v,j)=>v!==oldMesh.uvs[j]))
  throw Error('Rock UV/triangle data changed '+part.name);
 if(topology.positions.some((v,i)=>Math.abs(v-oldMesh.positions[i])>1e-5))changed++;
}
if(changed<75)throw Error('Most actual stone objects were not reshaped '+changed);
if(corrected.project.modelAtelier.rigging.bones.length!==17||
 !vm.runInContext('se220RigValidate(se281RockScene().project.modelAtelier.rigging)',ctx))
 throw Error('Stone rig was lost');
const idSet=new Set(next.map(x=>x.id));
for(const group of corrected.project.modelAtelier.meshGroups){
 if(group.members.some(id=>!idSet.has(id)))throw Error('Stale stone group member');
}
const status=vm.runInContext('window.SWYRL_ENGINE_STONE_HAND_ANATOMY_367.status()',ctx);
if(status.rockParts!==89||status.retainedExteriorRocks<30)throw Error('Status not recording all 89 rocks');
if(!corrected.project.modelAtelier.name.includes('Anatomical Rock Formation'))throw Error('No visible new load identity');
console.log('SE367_FULL_ROCK_HAND_PASS '+JSON.stringify({
 originalParts:old.length,anatomicalParts:next.length,modifiedMeshes:changed,
 intact17BoneRig:true,originalUVIndices:true,stoneGroups:corrected.project.modelAtelier.meshGroups.length,
 exteriorStones:status.retainedExteriorRocks,anatomy
}));
