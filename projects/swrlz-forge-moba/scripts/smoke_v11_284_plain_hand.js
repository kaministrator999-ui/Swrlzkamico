#!/usr/bin/env node
// §E v11.284 focused plain anatomy + project gallery classification test.
const fs=require('fs'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'..');
const ctx=vm.createContext({
 window:{},console,structuredClone,THREE:{},
 document:{readyState:'loading',addEventListener(){},getElementById(){return null;}},
 createProjectFromTemplate(){},se236InstallStarterGroups(){}
});
const load=f=>vm.runInContext(fs.readFileSync(path.join(root,'runtime',f),'utf8'),ctx);
load('model_atelier_skeletal_core_v11_220.js');
const digits=[
 {name:'index',x:-.397,from:2.17,to:2.99,r:.104,splay:-.055,z:.006},
 {name:'middle',x:-.131,from:2.197,to:3.168,r:.112,splay:-.017,z:-.009},
 {name:'ring',x:.135,from:2.176,to:3.077,r:.103,splay:.028,z:-.009},
 {name:'pinky',x:.402,from:2.113,to:2.791,r:.084,splay:.083,z:.010}
];
ctx.__digits=digits;
const rig=vm.runInContext('se220CreateHandRig(__digits)',ctx);
const original={
 project:{name:'Arcane Glove',environmentSettings:{},
 modelAtelier:{name:'Arcane Glove',parts:[
  {id:'floating-hand-000',name:'Glove · organic connected palm',kind:'topologyMesh',
   organicSurface:{species:'arcane-glove',region:'shell'},
   color:'#181520',material:'silk',group:'Glove / core',
   position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],
   topologyMesh:{positions:[0,0,0,0,1,0,.2,1,0],
      uvs:[0,0,0,1,1,1],indices:[0,1,2]}},
  {id:'floating-hand-001',name:'Glove armor',kind:'sphere',
   color:'#bada55',material:'metal',group:'Armor',
   position:[0,0,0],rotation:[0,0,0],scale:[1,1,1]}],
   rigging:rig,meshGroups:[{name:'Armor',members:['floating-hand-001']}]}}
};
ctx.se212HandScene=()=>structuredClone(original);
load('plain_hand_model_v11_284.js');
const scene=vm.runInContext('se284PlainHandScene()',ctx),p=scene.project,m=p.modelAtelier;
if(p.template!=='plain-hand-base'||p.kind!=='model-atelier'||p.name!=='Plain Hand Base')
 throw Error('Plain model project identity incorrect');
if(!Array.isArray(m.parts)||m.parts.length!==1)throw Error('Expected exactly one plain mesh');
const part=m.parts[0];
if(part.kind!=='topologyMesh'||part.material!=='matte'||/armor|glove|rock/i.test(part.name))
 throw Error('Plain model retains decorated pieces');
if(part.organicSurface?.species!=='plain-hand'||part.topologyMesh?.indices?.length!==3)
 throw Error('Plain hand topology not preserved');
if(m.meshGroups.length)throw Error('Plain hand retained armor mesh groups');
if(!vm.runInContext('se220RigValidate(se284PlainHandScene().project.modelAtelier.rigging)',ctx))
 throw Error('Plain model 17-bone rig invalid');
if(m.rigging.bones.length!==17||m.rigging.timeline.length!==3)
 throw Error('Hand open/fist/open animation not preserved');
const card=(id,tag)=>({dataset:{projectTemplate:id},querySelector:()=>({textContent:tag})});
const cases=[
 ['plain-hand-base','STARTER MODEL · PLAIN RIGGED ANATOMY',true],
 ['rocky-anime-hand','STARTER MODEL · WEATHERED STONE',true],
 ['arcane-glove-left','STARTER MODEL · MIRRORED RIG',true],
 ['floating-hand-glove','NATIVE 3D MODEL · GLOWING HAND',true],
 ['sheep-barn','SHEEP BUILDING MODEL',true],
 ['blank-vr-hands','STARTER GAME · TWO VR GLOVES',false],
 ['unknown-sheep-tag','STARTER GAME · PLAYABLE',false],
 ['new-custom-model','STARTER MODEL · NEW CHARACTER',true],
 ['particle-effect','STARTER PARTICLE · VORTEX',false]
];
for(const [id,tag,expected] of cases){
 ctx.__card=card(id,tag);
 const actual=vm.runInContext('se284ModelCard(__card)',ctx);
 if(actual!==expected)throw Error('Incorrect category for '+id);
}
const gameChildren=[],modelChildren=[];
function parent(children){return {children,append(child){
 for(const list of [gameChildren,modelChildren]){
  const i=list.indexOf(child);if(i>=0)list.splice(i,1);
 }
 children.push(child);
}};}
const games=parent(gameChildren),models=parent(modelChildren);
for(const [id,tag] of cases.slice(0,8)){
 gameChildren.push({dataset:{projectTemplate:id},matches:()=>true,
    querySelector:()=>({textContent:tag})});
}
const pane={querySelector:selector=>selector==='#se236StarterGames'?games:
 selector==='#se236StarterModels'?models:null};
ctx.document.getElementById=key=>key==='se170-pane-starter'?pane:null;
vm.runInContext('se284SortStarterCards()',ctx);
if(modelChildren.length!==6||gameChildren.length!==2)
 throw Error('Model/game reclassification failed');
if(new Set([...gameChildren,...modelChildren]).size!==8)
 throw Error('Model sorting cloned or discarded original cards');
console.log('SE284_PLAIN_HAND_SMOKE '+JSON.stringify({
 plainMeshes:m.parts.length,bones:m.rigging.bones.length,
 animationKeys:m.rigging.timeline.length,
 modelsInTab:modelChildren.length,gamesInTab:gameChildren.length,
 originalCardsRetained:true,pass:true
}));
