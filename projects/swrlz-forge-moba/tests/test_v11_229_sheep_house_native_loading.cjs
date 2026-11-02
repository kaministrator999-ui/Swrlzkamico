// Native validation of the RELEASED assembled house builder, not old v11.226 source.
// Fail a release if a decorative material becomes a non-finite rotation.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const file=process.argv[2];
assert(file,'Supply the generated index.html path');
const html=fs.readFileSync(file,'utf8');
const start=html.indexOf('const SE226_BUILDINGS=Object.freeze([');
assert(start>=0,'Sheep starter builder missing from assembled engine');
const tail=html.indexOf('window.SWYRL_ENGINE_SHEEP_BUILDING_STARTERS=Object.freeze({',start);
assert(tail>start,'Sheep house API missing');
const end=html.indexOf('\n});',tail);
assert(end>tail,'Sheep house API end missing');
const code=html.slice(start,end+4);
assert(code.includes("P.glass,'Windows',0,'gloss'"));
assert(code.includes("P.glass,'Decor / lantern',0,'emissive'"));
const template={project:{
 name:'Base',kind:'model-atelier',
 modelAtelier:{schema:'swyrl-model-atelier-v1',parts:[],meshGroups:[]},
 environmentSettings:{showTerrain:true,showScenery:true,background:'#111111'}
}};
const context={MODEL_ATELIER_CANONICAL_PROJECT:template,structuredClone};
context.window=context;
context.createProjectFromTemplate=()=>false;
vm.createContext(context);
vm.runInContext(code,context,{timeout:3000});
const api=context.SWYRL_ENGINE_SHEEP_BUILDING_STARTERS;
assert(api);
const starters=api.list();
assert.equal(starters.length,5);
const mats=new Set(['matte','silk','gloss','metal','emissive']);
const kinds=new Set(['sphere','box','cone','cylinder','topologyMesh','loft']);
const groupsAllowed=96;
for(const {id} of starters){
 const scene=api.createScene(id),parts=scene.project.modelAtelier.parts;
 assert.equal(scene.project.kind,'model-atelier');
 assert.equal(scene.project.canonicalId,id);
 assert.equal(scene.project.modelAtelier.schema,'swyrl-model-atelier-v1');
 assert(parts.length>=15&&parts.length<=400,'Invalid Model Atelier part count');
 assert.equal(new Set(parts.map(p=>p.id)).size,parts.length,'Duplicate part IDs');
 for(const p of parts){
  assert(p.id.length<=90&&kinds.has(p.kind),id+' invalid part kind '+p.name);
  assert(mats.has(p.material),id+' invalid material '+p.name);
  assert(/^#[a-fA-F0-9]{6}$/.test(p.color),id+' invalid color '+p.name);
  for(const key of ['position','rotation','scale']){
   assert.equal(p[key].length,3,id+' invalid '+key+' length '+p.name);
   assert(p[key].every(Number.isFinite),id+' nonfinite '+key+' '+p.name);
   assert(p[key].every(n=>Math.abs(n)<=100),id+' out-of-range '+key+' '+p.name);
  }
  assert(p.scale.every(n=>n>.005&&n<=20),id+' invalid scale '+p.name);
  if(p.kind==='topologyMesh'){
   const t=p.topologyMesh;
   assert.deepEqual(Object.keys(t).sort(),['indices','positions','uvs']);
   assert(t.positions.length>=9&&t.positions.length%3===0);
   assert(t.uvs.length===t.positions.length/3*2);
   assert(t.positions.every(n=>Number.isFinite(n)&&Math.abs(n)<=100));
   assert(t.uvs.every(n=>Number.isFinite(n)&&Math.abs(n)<=20));
   assert(t.indices.length%3===0&&t.indices.length>0);
   assert(t.indices.every(n=>Number.isInteger(n)&&n>=0&&n<t.positions.length/3));
   for(let i=0;i<t.indices.length;i+=3)
    assert(new Set(t.indices.slice(i,i+3)).size===3,id+' collapsed triangle '+p.name);
  }
 }
 const groups=scene.project.modelAtelier.meshGroups;
 assert(groups.length<=groupsAllowed);
 const assigned=new Set();
 for(const g of groups){
  assert(g.name.length>=1&&g.name.length<=100,id+' bad group');
  assert(g.members.length>=2&&g.members.length<=32,id+' group exceeds native edit limit: '+g.name);
  for(const member of g.members){
   assert(parts.some(p=>p.id===member),id+' unknown group member');
   assert(!assigned.has(member),id+' overlapping mesh groups');
   assigned.add(member);
  }
 }
 console.log('SHEEP_HOUSE_MODEL_VALID '+id+' '+parts.length+' native editable parts');
}
console.log('SHEEP_HOUSE_V11229_VALIDATION_PASS all 5 full native part transforms, indexed topology and group limits');
