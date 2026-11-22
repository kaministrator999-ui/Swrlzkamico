#!/usr/bin/env node
'use strict';
// §E v11.543: test the real finder module, not a hypothetical search map.
// Search must route to native category/modes and navigate without executing
// UV export / project edits. The export button must be reparented, not cloned.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.resolve(__dirname,'../runtime/model_tool_finder_v11_543.js'),'utf8');
new vm.Script(source);
let selected=[],uvOpened=0,moved=0,exported=0,projects=0,highlighted=0;
const oldParent={};
const actualExport={
 id:'se336UVExport',parentElement:oldParent,isConnected:true,
 title:'',classList:{add(){highlighted++},remove(){}},
 closest(){return null},scrollIntoView(){},focus(){},
 click(){exported++}
};
const nativeProjects={
 id:'se320ModelProjects',isConnected:true,
 classList:{add(){},remove(){}},
 closest(){return null},scrollIntoView(){},focus(){},
 click(){projects++}
};
const previewActions={prepend(node){
 assert.strictEqual(node,actualExport);
 moved++;node.parentElement=previewActions;
}};
const panel={
 hidden:false,
 querySelector(selector){
  if(selector==='#se356UVPreview .se356-uv-preview-actions')return previewActions;
  if(selector==='#se336UVExport')return actualExport;
  if(selector==='.atelier-inspector')return null;
  return null;
 },
 querySelectorAll(){return[];},
 classList:{remove(){}}
};
const document={
 readyState:'loading',addEventListener(){},
 getElementById(id){
  return {'modelAtelierPanel':panel,'se336UVExport':actualExport,
   'se320ModelProjects':nativeProjects}[id]||null;
 }
};
const window={
 SWYRL_E_CONTEXT:{
  groups:()=>({Sculpt:['Push Pull','Smooth'],Topology:['Extrude','Inset','Vertex Ring']})
 },
 SWYRL_E_UNIFIED_TOOLS:{select(category,mode){selected.push([category,mode]);return true;}},
 SWYRLZ_E_UV_POPUP:{open(){uvOpened++;}}
};
vm.runInNewContext(source,{document,window,console,queueMicrotask:fn=>fn()},{timeout:2000});
const api=window.SWYRL_ENGINE_FIND_TOOLS_543;
assert.ok(api);
const result=api.search('extrude');
assert.ok(result.some(x=>x.name==='Extrude'&&x.category==='Topology'));
assert.ok(api.search('uv export').some(x=>x.key==='uv-export'));
assert.ok(api.search('painted image').some(x=>x.key==='uv-import'));
assert.ok(api.search('smooth').some(x=>x.category==='Sculpt'));
assert.equal(api.navigate('mode:Topology:Extrude'),true);
assert.equal(selected[0][0],'Topology');
assert.equal(selected[0][1],'Extrude');
assert.equal(api.navigate('uv-export'),true);
assert.equal(uvOpened,1);
assert.equal(exported,0,'search must never execute file download');
assert.ok(highlighted,'native control must be highlighted');
assert.equal(api.relocateExport(),true);
assert.equal(moved,1,'must move original UV export');
assert.strictEqual(actualExport.parentElement,previewActions);
assert.equal(api.relocateExport(),true);
assert.equal(moved,1,'moving twice must not duplicate button');
assert.equal(api.navigate('projects'),true);
assert.equal(projects,1,'Projects is safe navigation');
assert.equal(exported,0,'UV export remains user initiated');
actualExport.click();
assert.equal(exported,1,'original action remains attached and clickable');
console.log('SE543_TOOL_FINDER_NATIVE_ROUTE_PASS',JSON.stringify({
 modes:selected.length,uvWindowOpens:uvOpened,
 uvExportButtons:1,existingExportActionPreserved:true,
 searchDoesNotExecuteExport:true,projectsNavigation:true
}));
