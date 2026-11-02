/* Focused model-only starter contract. No browser/VR suite or Sheep Tag play. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const code=fs.readFileSync(path.resolve(__dirname,'../runtime/sheep_building_model_starters_v11_226.js'),'utf8');
const base={project:{name:'Blank',kind:'model-atelier',modelAtelier:{parts:[],meshGroups:[]},
 environmentSettings:{showTerrain:true,showScenery:true,background:'#ffffff'}}};
let forwarded=0;
const context={
 structuredClone,
 MODEL_ATELIER_CANONICAL_PROJECT:base,
 createProjectFromTemplate:()=>{forwarded++;return 'original';},
};
context.window=context;
vm.createContext(context);
vm.runInContext(code,context,{timeout:3000});
const api=context.SWYRL_ENGINE_SHEEP_BUILDING_STARTERS;
assert(api);
const list=api.list();
assert.equal(list.length,5);
assert.equal(new Set(list.map(x=>x.id)).size,5);
const summaries=[];
for(const {id,name} of list){
 const first=api.createScene(id),second=api.createScene(id);
 assert.equal(first.project.template,id);
 assert.equal(first.project.canonicalId,id);
 assert.equal(first.project.kind,'model-atelier');
 assert.equal(first.project.name,name);
 assert.equal(first.project.modelAtelier.parts.length,second.project.modelAtelier.parts.length);
 assert(first.project.modelAtelier.parts.length>=15);
 assert(first.project.modelAtelier.parts.length<=120,'Keep starter mobile-editable');
 assert.equal(first.project.environmentSettings.showTerrain,false);
 assert.equal(first.project.environmentSettings.showScenery,false);
 const parts=first.project.modelAtelier.parts,groups=first.project.modelAtelier.meshGroups;
 assert.equal(new Set(parts.map(p=>p.id)).size,parts.length);
 assert(parts.every(p=>Array.isArray(p.position)&&Array.isArray(p.rotation)&&Array.isArray(p.scale)));
 assert(groups.every(g=>g.members.every(id=>parts.some(p=>p.id===id))));
 for(const part of parts){
  if(part.kind==='topologyMesh'){
   const mesh=part.topologyMesh;
   assert(mesh.positions.length>0&&mesh.positions.length%3===0);
   assert.equal(mesh.uvs.length,mesh.positions.length/3*2);
   assert(mesh.indices.length>0&&mesh.indices.length%3===0);
   assert(mesh.indices.every(i=>Number.isInteger(i)&&i>=0&&i<mesh.positions.length/3));
   assert(mesh.positions.every(Number.isFinite));
  }else assert.equal(part.kind,'sphere');
 }
 second.project.modelAtelier.parts[0].name='CHANGED';
 assert.notEqual(first.project.modelAtelier.parts[0].name,'CHANGED');
 assert(parts.some(p=>/Roof/.test(p.name))&&parts.some(p=>/Foundation|plinth|Doorstep/.test(p.name)));
 summaries.push(id+': '+parts.length+' parts');
}
assert.equal(context.createProjectFromTemplate('not-sheep',true),'original');
assert.equal(forwarded,1);
assert.throws(()=>api.createScene('unknown building'));
console.log('SE226_SHEEP_BUILDING_MODELER_PASS '+summaries.join(' | '));
