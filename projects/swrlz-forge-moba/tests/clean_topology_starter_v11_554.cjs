#!/usr/bin/env node
'use strict';
/* Verify real Starter Models card installs and loads distinct saved-local project. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'runtime/clean_topology_humanoid_v11_554.js'),'utf8');
const scene=JSON.parse(fs.readFileSync(path.join(root,'scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json'),'utf8'));
new vm.Script(source);
let card=null, loaded=null, history=0, views=0;
const original={insertAdjacentElement(where,value){assert.equal(where,'afterend');card=value}};
const doc={
 baseURI:'https://example.test/modeler.html',readyState:'complete',
 querySelector(selector){
   if(selector==='button[data-project-template="robotic-humanoid-mannequin"]')return original;
   if(selector==='[data-project-template="clean-topology-humanoid"]')return card;
   return null;
 },
 createElement(tag){
   assert.equal(tag,'button');
   return {dataset:{},addEventListener(type,fn,capture){assert.equal(type,'click');assert.equal(capture,true);this.clickHandler=fn}};
 },
 getElementById(){return {classList:{remove(){}}}},
 addEventListener(){throw Error('DOM is already ready')}
};
const ctx={console,document:doc,URL,dirty:false,
 currentProject:null,toast(){},confirm:()=>true,
 fetch:async url=>{assert.ok(url.toString().endsWith('clean-topology-humanoid-v11-554.swyrl.json'));return {ok:true,json:async()=>scene}},
 ModelAtelier:{close(){},syncProject(){}},loadProject(obj){loaded=obj;ctx.currentProject=obj.project},
 se232ActivateSelectedModelWorkspace(){},initializeHistory(){history++},markSaved(){},
 requestAnimationFrame:fn=>fn(),
 window:{SWYRL_ENGINE_STUDIOS:{active:()=> 'modeler',change(){}},
         SWYRL_ENGINE_MODEL_ATELIER:{view(mode){assert.equal(mode,'front');views++}}}
};
vm.createContext(ctx);vm.runInContext(source,ctx);
assert.equal(card?.dataset.projectTemplate,'clean-topology-humanoid');
assert.ok(card.innerHTML.includes('STARTER MODEL'));
assert.equal(ctx.window.SWYRL_ENGINE_CLEAN_TOPOLOGY.validate(scene).triangles,scene.project.modelAtelier.parts[0].topologyMesh.indices.length/3);
let cancelled=0;
card.clickHandler({preventDefault(){cancelled++},stopPropagation(){},stopImmediatePropagation(){}});
setImmediate(()=>{
 try{
 assert.equal(cancelled,1);
 assert.equal(loaded?.project.canonicalId,'clean-topology-humanoid');
 assert.equal(history,1);assert.equal(views,1);
 assert.equal(ctx.window.SWYRL_ENGINE_CLEAN_TOPOLOGY.status().active,true);
 console.log('SE554_NATIVE_STARTER_UI_AND_LOADER_PASS');
 }catch(e){console.error(e);process.exitCode=1}
});
