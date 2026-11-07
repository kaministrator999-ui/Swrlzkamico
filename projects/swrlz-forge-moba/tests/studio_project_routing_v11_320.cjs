const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../runtime/studio_project_routing_v11_320.js'),'utf8');
let active='game',events=[],routes=[],tasks=[],cancelTemplate=false,importValid=false;
const context={Set,Promise,CustomEvent:class{constructor(name,options){this.type=name;this.detail=options.detail}},
 playing:false,simulating:false,currentProject:{name:'before'},
 queueMicrotask:f=>tasks.push(f),
 document:{getElementById:()=>({classList:{remove:()=>{}}})},ModelAtelier:{syncProject:()=>{}},
 window:{dispatchEvent:e=>events.push(e),SWYRL_ENGINE_STUDIOS:{active:()=>active,change:m=>{active=m;routes.push(m)}}},
 loadProject(data){if(!Array.isArray(data?.scene?.actors))throw Error('Invalid native document');context.currentProject=structuredClone(data.project);return true;},
 projectData(){return {project:structuredClone(context.currentProject),editor:{custom:'preserved'},scene:{actors:[]}};},
 createProjectFromTemplate(kind){if(cancelTemplate)return false;context.currentProject={kind,name:'created',modelAtelier:kind==='model-atelier'?{parts:[]}:undefined};return Promise.resolve(true);},
 async se223UIImport(file){if(file&&importValid)context.currentProject.particleStudio={schema:'swyrl-particle-studio-v1',emitters:[]};}
};
vm.createContext(context);vm.runInContext(source,context);
const load=(project,editor={})=>({project,editor,scene:{actors:[{id:'distinct-native-actor'}]}});
const flush=()=>{while(tasks.length)tasks.shift()();};
const classify=context.window.SWYRL_ENGINE_PROJECT_ROUTING_320.classify;
assert.equal(classify(load({kind:'model-atelier',modelAtelier:{parts:[]}}, {studioWorkspace:'game'})),'modeler');
assert.equal(classify(load({kind:'sandbox',particleStudio:{emitters:[{id:'vfx'}]}})),'game');
assert.equal(classify(load({kind:'sandbox'},{studioWorkspace:'particles'})),'particles');
assert.equal(classify(load({kind:'sandbox'},{studioWorkspace:'unknown'})),'game');
assert.equal(classify({project:{particleStudio:{emitters:[{id:'vfx'}]}},scene:{actors:[]}}),'particles');
const model=load({kind:'model-atelier',name:'distinct-model',modelAtelier:{parts:[{id:'native-mesh'}]}});
const immutable=JSON.stringify(model);context.loadProject(model);flush();assert.equal(active,'modeler');assert.equal(context.currentProject.name,'distinct-model');assert.equal(JSON.stringify(model),immutable);
context.loadProject(load({kind:'sandbox',name:'distinct-game'}));flush();assert.equal(active,'game');assert.equal(context.currentProject.name,'distinct-game');
context.loadProject(load({kind:'sandbox',name:'effects-document'},{studioWorkspace:'particles'}));flush();assert.equal(active,'particles');assert.equal(context.currentProject.name,'effects-document');
let n=routes.length;context.loadProject(model,{preserveHistory:true});flush();assert.equal(routes.length,n,'History restoration must not redirect the current studio');
context.loadProject(model);context.loadProject(load({kind:'sandbox',name:'latest-load'}));flush();assert.equal(active,'game');assert.equal(context.currentProject.name,'latest-load');
n=routes.length;assert.throws(()=>context.loadProject({project:{name:'bad'}}));flush();assert.equal(routes.length,n);
cancelTemplate=true;context.createProjectFromTemplate('model-atelier');flush();assert.equal(routes.length,n);
(async()=>{
 cancelTemplate=false;await context.createProjectFromTemplate('model-atelier');flush();assert.equal(active,'modeler');
 const p=context.currentProject;n=routes.length;await context.se223UIImport({name:'invalid.json'});flush();assert.equal(routes.length,n);assert.equal(context.currentProject,p);
 importValid=true;await context.se223UIImport({name:'valid.vfx.json'});flush();assert.equal(active,'particles');assert.equal(context.currentProject,p);
 const saved=context.projectData();assert.equal(saved.editor.studioWorkspace,'particles');assert.equal(saved.editor.custom,'preserved');
 console.log('STUDIO_PROJECT_ROUTING_V11_320_PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
