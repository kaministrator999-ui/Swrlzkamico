#!/usr/bin/env node
// Focused native Delete Selected transaction checks against generated HTML.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const html=fs.readFileSync(process.argv[2],'utf8');
for(const f of ['SE444_DELETE_SELECTED_VR_ACTION_START',"['delete-selected','Delete',null]",'se444DeleteSelected','deleteSelected:deleteSelectedObjects']){
 assert.ok(html.includes(f),'Missing Delete Selected binding: '+f);
}
const a=html.indexOf('  function deleteSelectedObjects(){'),b=html.indexOf('  function cameraUpdate(){',a);
assert.ok(a>=0&&b>a,'Missing native delete function');
const body=html.slice(a,b);
function run({selected=['a'],parts=['a','b','c'],mode='mesh',nativeGesture=false,groupGesture=false,preview=false}={}){
 const data={parts:parts.map(id=>({id})),meshGroups:[{id:'group',name:'test',members:['a','b']}]};
 let checkpoints=0,dirty=0;
 const model=()=>data,partById=id=>data.parts.find(p=>p.id===id);
 const checkpoint=()=>{checkpoints++;};
 const signalEdited=()=>{dirty++;data.meshGroups=data.meshGroups.map(g=>({...g,members:g.members.filter(id=>data.parts.some(p=>p.id===id))})).filter(g=>g.members.length>=2);};
 const status=()=>{};
 const bridge={inspect:()=>({gesture:nativeGesture?{}:null})};
 const group={inspect:()=>({gesture:groupGesture?{}:null})};
 const workshop={inspect:()=>({preview:{active:preview}})};
 const fn=new Function('model','partById','checkpoint','signalEdited','status','se340ModelBridge','se350ModelTools','se430ModelWorkshop','atelierComponentMode','atelierMeshIds','selection','atelierMeshAdding','atelierGroupCurrent','atelierComponentIds','atelierComponentPartId',body+'\nreturn deleteSelectedObjects();');
 const result=fn(model,partById,checkpoint,signalEdited,status,bridge,group,workshop,mode,[...selected],selected.at(-1)||null,false,null,[],null);
 return {result,parts:data.parts.map(p=>p.id),groups:data.meshGroups,checkpoints,dirty};
}
let t=run({selected:['a','b']});assert.equal(t.result.deletedCount,2);assert.deepEqual(t.parts,['c']);assert.equal(t.checkpoints,1);assert.equal(t.dirty,1);assert.deepEqual(t.groups,[]);
t=run({selected:['b']});assert.deepEqual(t.parts,['a','c']);assert.equal(t.checkpoints,1);
for(const options of [{selected:[]},{selected:['a','b','c']},{mode:'face'},{nativeGesture:true},{groupGesture:true},{preview:true}]){
 t=run(options);assert.equal(t.result.ok,false);assert.equal(t.checkpoints,0);assert.equal(t.dirty,0);
}
console.log('Model Delete Selected transaction/guard test passed');
