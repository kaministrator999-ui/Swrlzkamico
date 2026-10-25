// §E v11.118 test the production category selector and native rail ordering.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const source=fs.readFileSync('/tmp/se-v11118.mjs','utf8');
function extract(name){
 const key='function '+name+'(';
 const start=source.indexOf(key);
 assert.ok(start>=0, 'missing compiled function '+name);
 const open=source.indexOf('{',start);
 let depth=0;
 for(let i=open;i<source.length;i++){
  if(source[i]==='{')depth++;
  if(source[i]==='}'&&--depth===0)return source.slice(start,i+1);
 }
 throw Error('unterminated '+name);
}
const originalNames=['Appearance','Motion','References','Meshes','Sculpt','Lasso','Face','Topology','More','Plugin'];
const items=originalNames.map(label=>({textContent:label,title:'',dataset:{},clickListeners:[()=>label]}));
const original=new Map(items.map(item=>[item.textContent,item]));
const rail={
 items:[...items],dataset:{},
 querySelectorAll(sel){assert.equal(sel,'button');return this.items;},
 append(button){
  const i=this.items.indexOf(button);
  if(i>=0)this.items.splice(i,1);
  this.items.push(button);
 }
};
const panel={querySelector:sel=>sel==='#modelAtelierToolRail'?rail:null};
const context={console};vm.createContext(context);
vm.runInContext(extract('atelierToolRailArrange')+'\n'+extract('detectGroup'),context);
assert.equal(context.atelierToolRailArrange(panel),true);
assert.deepEqual(rail.items.map(x=>x.textContent),[
 'Meshes','Sculpt','Lasso','Topology','Face','Appearance',
 'Motion','References','More','Plugin'
],'tool rail order incorrect');
for(const item of items){
 assert.strictEqual(original.get(item.textContent),item,'node replaced');
 assert.equal(item.clickListeners.length,1,'native listeners disturbed');
}
assert.equal(rail.dataset.organized,'v11.118');
assert.equal(original.get('Sculpt').dataset.atelierToolCategory,'Sculpt');
assert.match(original.get('Topology').title,/vertices/i);
assert.equal(context.atelierToolRailArrange(panel),true);
assert.deepEqual(rail.items.map(x=>x.textContent).slice(0,9),[
 'Meshes','Sculpt','Lasso','Topology','Face','Appearance','Motion','References','More'
],'reorganization not idempotent');
assert.equal(context.atelierToolRailArrange({querySelector:()=>null}),false);
const cases={
 BoreRadius:'Sculpt',BoreGizmoDepth:'Sculpt',SculptBrushPick:'Sculpt',
 LassoBooleanApply:'Lasso',TopologyAuditRepair:'Topology',
 AdaptiveTopologyPreview:'Topology',LODRatio:'Topology',
 HeadAnatomy:'Face',FaceExtrudeDepth:'Face',Color:'Appearance',
 HDDetail:'Appearance',ReferenceOpacity:'References',
 PoseFrameAdd:'Motion',position0:'Meshes',MeshDensityOpen:'Meshes'
};
for(const [id,want] of Object.entries(cases))
 assert.equal(context.detectGroup(id),want,'misclassified '+id);
assert.equal(context.detectGroup('FutureNewBrushOption','Sculpt'),'section fallback lost');
assert.equal(context.detectGroup('FutureNewBrushOption','Topology'),'Topology','section fallback lost');
assert.equal(context.detectGroup('SomethingNew'),'Meshes','safe default wrong');
assert.ok(source.includes("GROUPS.Sculpt.splice(1,0,['Precision circle cut'"),'precision cut absent');
assert.ok(source.includes("GROUPS.Face.unshift(['Portrait & anatomy'"),'portrait absent');
assert.ok(source.includes("GROUPS.Appearance=[\n  ['Materials & colors'"),'appearance misplaced');
assert.ok(source.includes("const buckets={};"),'section-level mixed classification unchanged');
assert.ok(source.includes("atelierToolRailArrange(panel);"),'native rail call missing');
assert.ok(source.includes('V11_117_EDITOR_NATIVE_CALLOUT_GUARD')===false,'stale marker present');
console.log('SE_V11118_SEMANTIC_GROUPS_RAIL_NODES_AND_CONTEXT_CATALOG_PASS');
