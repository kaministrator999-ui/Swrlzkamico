#!/usr/bin/env node
'use strict';
/* §E v11.543 native search navigation contract.
 * Uses a small deterministic DOM fixture and real runtime source, verifying
 * that lookup labels and jump actions resolve the actual Model Studio
 * workspace, category controller, mini-studios and UV Editor buttons.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const ROOT=path.resolve(__dirname,'..');
const script=fs.readFileSync(path.join(ROOT,'runtime/tool_navigation_search_v11_543.js'),'utf8');
const css=fs.readFileSync(path.join(ROOT,'runtime/tool_navigation_search_v11_543.css'),'utf8');
new vm.Script(script);
assert.ok(css.includes('.se543-search-dialog'));
const versioned=process.argv[2]&&fs.readFileSync(process.argv[2],'utf8');
if(versioned){
 assert.ok(versioned.includes('SE543_TOOL_SEARCH_END'));
 assert.ok(versioned.includes('id="se543SearchDialog"')===false,
  'Navigation search dialog is generated lazily, never stored as static model HTML');
 assert.ok(versioned.includes('.se543-find-button'));
 assert.ok(versioned.includes('UV wireframe'));
 assert.ok(versioned.includes('V11_543_TOOL_NAVIGATION_SEARCH'));
}

let workspace='modeler',selected={group:'Meshes',operation:'Select & organize'};
const calls=[];
const groupNames={
 Meshes:['Select & organize','Assemblies & selection'],
 Sculpt:['Push-pull','Smooth'],
 Lasso:['Select region'],
 Topology:['Manual mesh modeling','Refinement'],
 Face:['Face editing'],
 Appearance:['Materials'],
 Motion:['Pose'],
 References:['References']
};
const popupButtons=[
 {textContent:'UV wireframe',disabled:false,click(){calls.push('click:wireframe')},scrollIntoView(){}},
 {textContent:'Applied texture',disabled:false,click(){calls.push('click:texture')}},
 {textContent:'Surface map (optional)',disabled:false,click(){calls.push('click:surface')}},
 {textContent:'Stretch heatmap',disabled:false,click(){calls.push('click:stretch')}}
];
let uvOpened=false,exportClicks=0,exportMoves=0,exportHighlights=0;
const exportArea={prepend(button){
 assert.equal(button,nativeUVExport);
 nativeUVExport.parentElement=this;exportMoves++;
}};
const nativeUVExport={
 id:'se336UVExport',disabled:false,parentElement:{},
 classList:{add(){exportHighlights++}},focus(){},scrollIntoView(){},
 click(){exportClicks++}
};
const popup={
 get hidden(){return !uvOpened;},
 querySelectorAll(selector){return selector==='button'?popupButtons:[];},
 querySelector(selector){
  if(selector==='#se336UVExport')return nativeUVExport;
  if(selector==='[data-se355-section="whole"]')
   return {disabled:false,click(){calls.push('click:whole')}};
  return null;
 }
};
const project={
 hidden:false,
 querySelector(selector){
  if(selector==='.atelier-inspector')return {scrollIntoView(){}};
  if(selector==='#se355UVPopup')return popup;
  if(selector==='#se320ModelProjects')return {disabled:false,click(){calls.push('click:projects')}};
  if(selector==='#seAtelierExportMenu > summary')return {disabled:false,click(){calls.push('click:file')}};
  return null;
 },
 querySelectorAll(selector){return selector==='.atelier-head button'?[
  {textContent:'Settings ▾',disabled:false,click(){calls.push('click:settings')}}
 ]:[];}
};
const document={
 readyState:'loading',body:null,
 querySelector(selector){
  if(selector==='#modelAtelierPanel')return project;
  if(selector==='#se336UVExport')return nativeUVExport;
  if(selector==='#se356UVPreview .se356-uv-preview-actions')return exportArea;
  return null;
 },
 addEventListener(){}
};
const win={
 SWYRL_E_CONTEXT:{
  groups:()=>groupNames,current:()=>selected,
 },
 SWYRL_E_UNIFIED_TOOLS:{
  select(category,operation){calls.push('select:'+category+'/'+operation);
   selected={group:category,operation};},
 },
 SWYRL_ENGINE_STUDIOS:{
  active:()=>workspace,
  change:(next)=>{workspace=next;calls.push('workspace:'+next);return true;}
 },
 SWYRL_ENGINE_MINI_STUDIOS_496:{
  set:mode=>{calls.push('mini:'+mode);return true;}
 },
 SWYRLZ_E_UV_POPUP:{
  open:()=>{uvOpened=true;calls.push('uv:open');}
 }
};
const context={window:win,document,console,MutationObserver:class{},requestAnimationFrame:cb=>cb()};
vm.createContext(context);vm.runInContext(script,context,{timeout:1000});
const api=win.SWYRL_E_TOOL_SEARCH_543;
const ids=query=>api.search(query).map(x=>x.id);
assert.ok(ids('UV wireframe').includes('uv-wireframe'));
assert.ok(ids('Current UV Guide').includes('uv-export'),'old guide wording must lead to the actual export, not the preview toggle');
assert.ok(ids('UV map').includes('uv'));
assert.ok(ids('surface map').includes('uv-surface'));
assert.ok(ids('smoothing').length===0,'unsupported synthetic action must not be fabricated');
assert.ok(ids('Sculpt').includes('group-Sculpt'));
assert.ok(ids('Manual mesh modeling').includes('mode-Topology-Manual mesh modeling'));
assert.ok(ids('Rigging').includes('rig'));
assert.ok(ids('Material').includes('workspace-materials'));
(async()=>{
 const names={'uv-export':'Export UV wireframe','uv-wireframe':'UV wireframe','uv-surface':'Surface map',
   'uv-stretch':'Stretch heatmap','uv-atlas':'Whole model UV atlas',
   'projects':'Starter Projects','group-Sculpt':'Sculpt',
   'mode-Topology-Manual mesh modeling':'Manual mesh modeling',
   'rig':'Rigging','workspace-materials':'Materials & Textures'};
 const find=id=>{
   const entry=api.search(names[id]).find(e=>e.id===id);
   assert.ok(entry,'Search result missing: '+id);
   return entry;
 };
 assert.equal(await api.navigate(find('uv-export')),true);
 assert.equal(exportClicks,0,'search must never automatically export files');
 assert.equal(exportMoves,1,'the real export button must be reparented to the preview');
 assert.equal(exportHighlights,1,'search must highlight the real button');
 assert.equal(api.relocateExport(),true);
 assert.equal(exportMoves,1,'do not duplicate export controls');
 assert.equal(await api.navigate(find('uv-wireframe')),true);
 assert.equal(await api.navigate(find('uv-surface')),true);
 assert.equal(await api.navigate(find('uv-stretch')),true);
 assert.equal(await api.navigate(find('uv-atlas')),true);
 assert.equal(await api.navigate(find('projects')),true);
 assert.equal(await api.navigate(find('group-Sculpt')),true);
 assert.equal(await api.navigate(find('mode-Topology-Manual mesh modeling')),true);
 assert.equal(await api.navigate(find('rig')),true);
 assert.equal(await api.navigate(find('workspace-materials')),true);
 assert.equal(exportClicks,0,'preview/search may never trigger an export');
 nativeUVExport.click();
 assert.equal(exportClicks,1,'original UV export handler remains directly clickable');
 assert.ok(calls.includes('click:wireframe'));
 assert.ok(calls.includes('click:surface'));
 assert.ok(calls.includes('click:stretch'));
 assert.ok(calls.includes('click:whole'));
 assert.ok(calls.includes('click:projects'));
 assert.ok(calls.includes('select:Sculpt/Push-pull'));
 assert.ok(calls.includes('select:Topology/Manual mesh modeling'));
 assert.ok(calls.includes('mini:rig'));
 assert.ok(calls.includes('workspace:materials'));
 console.log('SE543_NATIVE_SEARCH_OK',JSON.stringify({searchAliases:true,
  realUV:true,exportNearPreview:true,exportSearchDoesNotDownload:true,
  realModelMode:true,realProjects:true,realWorkspace:true,calls:calls.length}));
})().catch(err=>{console.error(err);process.exitCode=1;});
