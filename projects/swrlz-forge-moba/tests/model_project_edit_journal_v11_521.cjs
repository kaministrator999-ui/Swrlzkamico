'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
let redraws=0,dirty=0;
const project=(id)=>({instanceId:id,modelAtelier:{schema:'swyrl-model-atelier-v1',
 parts:[{id:'sphere',name:'Sphere',kind:'sphere',position:[0,0,0],rotation:[0,0,0],
 scale:[1,1,1],color:'#334455',material:'matte'}]}});
const state={currentProject:project('project-one')};
const sandbox={window:{},structuredClone,model:()=>state.currentProject.modelAtelier,
 get currentProject(){return state.currentProject;},
 set currentProject(v){state.currentProject=v;},
 renderParts:()=>redraws++,se220RigBind:()=>{},se220RigRefresh:()=>{},
 refreshList:()=>{},refreshInspector:()=>{},markDirty:()=>dirty++,selection:null};
vm.createContext(sandbox);
const source=fs.readFileSync(path.join(__dirname,'../runtime/model_edit_journal_v11_521.js'),'utf8');
vm.runInContext(source,sandbox,{filename:'model_edit_journal_v11_521.js'});
const J=sandbox.window.SWYRL_ENGINE_EDIT_JOURNAL_521,m1=state.currentProject.modelAtelier;
J.bind();m1.parts[0].position[0]=1;
assert.equal(J.record('model','Move sphere').changed,true);
m1.parts[0].position[0]=2;
assert.equal(J.record('model','Move sphere again').changed,true);
assert.equal(J.depths('model').undoDepth,2);
assert.equal(J.step(true,'model').changed,true);
assert.equal(m1.parts[0].position[0],1);
assert.equal(J.step(true,'model').changed,true);
assert.equal(m1.parts[0].position[0],0);
assert.equal(J.step(true,'model').changed,false);
assert.equal(J.depths('model').redoDepth,2);
assert.equal(J.step(false,'model').changed,true);
assert.equal(m1.parts[0].position[0],1);
assert.equal(J.step(false,'model').changed,true);
assert.equal(m1.parts[0].position[0],2);
assert.equal(J.step(false,'model').changed,false);
assert.deepEqual(Array.from(m1.editJournal.events.map(e=>e.type)),[
 'edit','edit','undo','undo','redo','redo']);
m1.parts[0].color='#ff0000';
assert.equal(J.record('texture','Changed material color').changed,true);
assert.equal(J.step(true,'model').changed,true);
assert.equal(m1.parts[0].position[0],1);
assert.equal(m1.parts[0].color,'#ff0000','model undo must not change texture data');
assert.equal(J.step(true,'texture').changed,true);
assert.equal(m1.parts[0].color,'#334455','texture undo retains modeled position');
assert.equal(J.step(false,'texture').changed,true);
assert.equal(m1.parts[0].color,'#ff0000');
m1.rigging={bones:[{id:'root',rest:[0,0,0]}],pose:{root:[0,0,0]},timeline:[]};
J.record('rig','Rig created');
assert.equal(J.step(true,'rig').changed,true);
assert.equal(m1.rigging,undefined);
assert.equal(J.step(false,'rig').changed,true);
assert.equal(m1.rigging.bones.length,1);
const log1=m1.editJournal.events.length;
const saved=JSON.parse(JSON.stringify(state.currentProject));
state.currentProject=project('project-two');
J.bind();
assert.equal(J.depths('model').undoDepth,0,'project B may not inherit project A undo');
assert.equal(J.step(true,'model').changed,false,'project B cannot undo project A');
state.currentProject.modelAtelier.parts[0].position[1]=3;
J.record('model','Project B move');
assert.equal(J.depths('model').undoDepth,1);
state.currentProject=saved;J.bind();
assert.equal(J.depths('model').undoDepth,1,'saved project restores its own undo history');
assert.equal(J.step(false,'model').changed,true);
assert.equal(state.currentProject.modelAtelier.parts[0].position[0],2);
assert.ok(state.currentProject.modelAtelier.editJournal.events.length>log1);
const current=state.currentProject.modelAtelier;
current.parts[0].position[0]=9;
J.record('rig','Dependent out-of-band rig edit');
const result=J.step(true,'model');
assert.equal(result.changed,false,'conflicting edit must not corrupt another lab');
assert.match(result.error,/conflict/i);
assert.equal(current.parts[0].position[0],9);
assert.ok(redraws>=8&&dirty>=8);
console.log('SE521_EDIT_JOURNAL_PASS',{
 projectIsolation:true,persistentReload:true,appendOnly:true,doubleUndoRedo:true,
 labIsolation:true,dependencyGuard:true,originalEventsPreserved:true,
 savedEvents:current.editJournal.events.length,redraws,dirty});
