// §E v11.537 native mannequin geometry/registration contract (no browser required).
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const filename=path.resolve(__dirname,'../runtime/robotic_humanoid_mannequin_v11_537.js');
const input=fs.readFileSync(filename,'utf8');
new vm.Script(input,{filename});
const buttons=[];
let loads=0,dirty=false,currentProject=null,history=0,saved=0,workspace='modeler';
const context={
 window:{SWYRL_ENGINE_STUDIOS:{active:()=>workspace,change:x=>{workspace=x}},
 SWYRL_ENGINE_MODEL_ATELIER:{view:()=>{}}},
 document:{readyState:'complete',getElementById:()=>({dataset:{},addEventListener(){},classList:{remove(){}}}),
  querySelector:()=>({})},console,URLSearchParams,requestAnimationFrame:fn=>fn(),
 toast:()=>{},initializeHistory:()=>{history++},markSaved:()=>{saved++},
 se232ActivateSelectedModelWorkspace:()=>{},
 createProjectFromTemplate:()=>false,dirty,
 ModelAtelier:{close(){},syncProject(){}},
 loadProject:data=>{currentProject=data.project;context.currentProject=currentProject;loads++},
 currentProject:null,
};
vm.createContext(context);
vm.runInContext(input,context,{timeout:3000});
const scene=context.window.SWYRL_ENGINE_HUMANOID_537.create();
const count=context.window.SWYRL_ENGINE_HUMANOID_537.validate(scene);
assert.ok(count>120&&count<=400,'expected a fully detailed native multi-part mesh');
assert.equal(scene.project.kind,'model-atelier');
assert.equal(scene.project.modelAtelier.schema,'swyrl-model-atelier-v1');
assert.equal(scene.project.modelAtelier.poseFrames.length,0);
assert.equal(scene.project.modelAtelier.parts.length,count);
assert.ok(scene.project.modelAtelier.parts.every(p=>p.kind==='topologyMesh'&&p.material==='matte'));
assert.ok(scene.project.modelAtelier.parts.every(p=>!('texture' in p)&&!('textureUrl' in p)));
assert.ok(scene.project.modelAtelier.parts.some(p=>p.name.includes('finger 4 phalanx 3')));
assert.ok(scene.project.modelAtelier.parts.some(p=>p.name.includes('patella')));
const all=scene.project.modelAtelier.parts.flatMap(p=>p.topologyMesh.positions);
const xs=all.filter((_,i)=>i%3===0), ys=all.filter((_,i)=>i%3===1);
assert.ok(Math.max(...xs)>2.45&&Math.min(...xs)<-2.45,'horizontal T-pose reach');
assert.ok(Math.min(...ys)<.13&&Math.max(...ys)>4.7,'head to foot height');
for(const group of scene.project.modelAtelier.meshGroups){
 assert.ok(group.members.length>=2&&group.members.length<=32);
 assert.ok(group.members.every(id=>scene.project.modelAtelier.parts.some(p=>p.id===id)));
}
(async()=>{
 assert.equal(await context.window.SWYRL_ENGINE_HUMANOID_537.open(true),true);
 assert.equal(loads,1);assert.equal(history,1);assert.equal(saved,1);
 assert.equal(context.currentProject.canonicalId,'robotic-humanoid-mannequin');
 console.log('SE537_NATIVE_HUMANOID_OK',JSON.stringify({meshParts:count,meshGroups:scene.project.modelAtelier.meshGroups.length,
  vertices:scene.project.modelAtelier.parts.reduce((n,p)=>n+p.topologyMesh.positions.length/3,0),
  triangles:scene.project.modelAtelier.parts.reduce((n,p)=>n+p.topologyMesh.indices.length/3,0),
  bounding:{xmin:Math.min(...xs),xmax:Math.max(...xs),ymin:Math.min(...ys),ymax:Math.max(...ys)}}));
})().catch(e=>{console.error(e);process.exitCode=1});
