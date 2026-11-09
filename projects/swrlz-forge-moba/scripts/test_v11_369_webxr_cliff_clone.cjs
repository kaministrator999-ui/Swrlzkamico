// Native isolated Cliff Hand model build and normal project-open acceptance.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const ROOT=path.resolve(__dirname,'..');
const json=JSON.parse(fs.readFileSync(path.join(ROOT,'assets/models/webxr-hands/right.json'),'utf8'));
const source=fs.readFileSync(path.join(ROOT,'runtime/webxr_cliff_stone_v11_369.js'),'utf8');
const sculpt=fs.readFileSync(path.join(ROOT,'runtime/model_atelier_skeletal_core_v11_220.js'),'utf8');
const f=fs.readFileSync(path.join(ROOT,'runtime/model_atelier_hand_proportions_v11_217.js'),'utf8');
const origPositions=structuredClone(json.mesh.positions),origUV=structuredClone(json.mesh.uvs),origFaces=structuredClone(json.mesh.indices);
let opens=0,history=0,saved=0,view=0,toastNotes=[];
const windowObj={SWYRL_ENGINE_STUDIOS:{active:()=> 'modeler'}};
const ctx={
 structuredClone,console,window:windowObj,
 SE288_ATLAS:'assets/cliff-hand/cliff_pbr_atlas_384.jpg',
 currentProject:null,dirty:false,confirm:()=>true,
 document:{getElementById:()=>({classList:{remove:()=>{}}})},
 requestAnimationFrame:fn=>fn(),
 toast:s=>toastNotes.push(String(s)),
 initializeHistory:()=>history++,
 markSaved:()=>saved++,
 se232ActivateSelectedModelWorkspace:()=>{},
 ModelAtelier:{close:()=>{},syncProject:()=>{},status:()=>({open:true})},
 loadProject:(scene)=>{ctx.currentProject=scene.project;opens++;},
 createProjectFromTemplate:()=>false,
 se284OpenPlainHand:()=>false,
 async se358WebXRHandScene(side){
  assert.equal(side,'right');
  return {
   project:{
    kind:'model-atelier',name:'WebXR Right Hand · Reference',
    canonicalId:'webxr-hand-right',template:'webxr-hand-right',
    environmentSettings:{showTerrain:true},
    modelAtelier:{
     name:'WebXR Right Hand · Reference',parts:[{
      id:'webxr-hand-right-surface',name:'editable WebXR hand',
      kind:'topologyMesh',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],
      color:'#cbb6a7',material:'matte',topologyMesh:structuredClone(json.mesh)
     }],referenceJoints:structuredClone(json.joints),
     meshGroups:[],poseFrames:[],poseNeutral:null
    }
   },scene:{actors:[]}
  }
 }
};
vm.createContext(ctx);
vm.runInContext(sculpt,ctx,{filename:'native-17-bone-hand-rig.js'});
vm.runInContext(f,ctx,{filename:'native-hand-finger-proportions.js'});
vm.runInContext(source,ctx,{filename:'webxr-cliff-stone-v11_369.js'});
(async()=>{
 const mScene=await vm.runInContext('window.SWYRL_ENGINE_WEBXR_CLIFF_369.createScene()',ctx);
 const m=mScene.project.modelAtelier,part=m.parts[0],mesh=part.topologyMesh;
 assert.equal(mScene.project.canonicalId,'plain-hand-base');
 assert.equal(mScene.project.template,'plain-hand-base');
 assert.match(m.name,/WebXR Anatomy \+ Stone/);
 assert.equal(mesh.positions.length/3,1360);
 assert.equal(mesh.indices.length/3,2314);
 assert.deepEqual(mesh.uvs,origUV,'keep all original hand UV islands');
 assert.deepEqual(mesh.indices,origFaces,'keep actual WebXR topology intact');
 assert.notDeepEqual(mesh.positions,origPositions,'orient original mesh into native rig');
 assert.deepEqual(json.mesh.positions,origPositions,'original bundled WebXR hand still unmodified');
 assert.equal(m.referenceJoints.length,25);
 assert.equal(m.rigging.bones.length,17);
 assert(vm.runInContext('se220RigValidate(window.SWYRL_ENGINE_WEBXR_CLIFF_369.createScene)',ctx)===false);
 assert.equal(part.cliffPBR.variant,'webxr-cliff');
 assert.equal(part.cliffPBR.atlas,'cliff_pbr_atlas_384');
 assert.equal(m.assemblies,null);
 const map=vm.runInContext('window.SWYRL_ENGINE_WEBXR_CLIFF_369.mapVertex',ctx);
 const wrist=json.joints.find(j=>j.name==='wrist');
 const mWrist=m.referenceJoints.find(j=>j.name==='wrist');
 const raw=map(...wrist.position);
 assert(Math.hypot(...raw.map((x,i)=>x-mWrist.position[i]))<.00001);
 const root=Object.fromEntries(m.referenceJoints.map(j=>[j.name,j.position]));
 const fingerX=['index','middle','ring','pinky'].map(k=>root[k+'-finger-phalanx-proximal'][0]);
 assert(fingerX.every((x,i)=>i===0||x>fingerX[i-1]),'normal index/middle/ring/pinky order');
 const hand={min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity]};
 for(let i=0;i<mesh.positions.length;i+=3)
  for(let a=0;a<3;a++){hand.min[a]=Math.min(hand.min[a],mesh.positions[i+a]);hand.max[a]=Math.max(hand.max[a],mesh.positions[i+a]);}
 assert(hand.min[0]<-1.2&&hand.max[0]>.62,'natural thumb vs pinky span');
 assert(hand.min[1]>.58&&hand.max[1]>3.3,'full WebXR fingertips and wrist');
 const pts=['index','middle','ring','pinky','thumb'].map(n=>root[(n==='thumb'?'thumb':n+'-finger')+'-tip']);
 for(const point of pts){
  const inf=vm.runInContext('se220RigWeights('+JSON.stringify(point)+',window.SWYRL_ENGINE_WEBXR_CLIFF_369_TEST_RIG)',Object.assign(ctx,{window:{...windowObj,SWYRL_ENGINE_WEBXR_CLIFF_369_TEST_RIG:m.rigging}}));
  assert.equal(inf.indices.length,4);
  assert(Math.abs(inf.weights.reduce((a,b)=>a+b,0)-1)<.00001,'normalized skin weights');
 }
 const ok=await vm.runInContext('createProjectFromTemplate("plain-hand-base",true)',ctx);
 assert.equal(ok,true);
 assert.equal(opens,1);
 assert.equal(history,1);assert.equal(saved,1);
 assert.equal(ctx.currentProject.kind,'model-atelier');
 assert.equal(ctx.currentProject.modelAtelier.parts.length,1);
 assert(toastNotes.some(x=>x.includes('sandstone texture maps ready')));
 const stats=vm.runInContext('window.SWYRL_ENGINE_WEBXR_CLIFF_369.status()',ctx);
 assert.equal(stats.loaded,2);
 console.log('SE369_WEBXR_CLIFF_NATIVE_OPEN_PASS '+JSON.stringify({
  vertices:mesh.positions.length/3,faces:mesh.indices.length/3,uvPairs:mesh.uvs.length/2,
  bones:m.rigging.bones.length,landmarks:m.referenceJoints.length,
  fingerXs:fingerX.map(x=>+x.toFixed(3)),bounds:hand,
  nativeOpen:opens,originalUnchanged:true
 }));
})().catch(e=>{console.error(e);process.exitCode=1});
