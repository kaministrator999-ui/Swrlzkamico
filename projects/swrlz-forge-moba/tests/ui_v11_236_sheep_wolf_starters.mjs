// Focused Android-width candidate: house solid gables, face weights,
// wolf root preview constraints, Starter Games vs Starter Models grouping.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const base='/tmp/se236-combined';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
try{
 const ctx=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 await ctx.route('**/*',route=>{
  const u=new URL(route.request().url());
  if(u.origin===host){
   const rel=u.pathname==='/'?'index.html':u.pathname.replace(/^\/+/,'');
   const file=path.resolve(base,rel);
   if(file===base||!file.startsWith(base+'/')||!fs.existsSync(file))return route.fulfill({status:404,body:'not bundled'});
   return route.fulfill({status:200,path:file,contentType:rel.endsWith('.html')?'text/html':undefined});
  }
  if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'].includes(u.hostname))return route.continue();
  return route.abort();
 });
 const page=await ctx.newPage();
 const errors=[];page.on('pageerror',err=>errors.push(String(err)));
 await page.goto(host+'/index.html',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_SHEEP_BUILDING_STARTERS?.createScene&&
   window.SE236_TEST_DIAG,null,{timeout:40000});
 const houses=await page.evaluate(()=>{
  const counts={'sheep-free-shelter':18,'sheep-thatched-hut':62,'sheep-cottage':71,'sheep-barn':40,'sheep-ram-house':63};
  return Object.entries(counts).map(([id,expected])=>{
   const m=window.SWYRL_ENGINE_SHEEP_BUILDING_STARTERS.createScene(id).project.modelAtelier;
   const gables=m.parts.filter(p=>p.name.startsWith('Gable · '));
   const floor=m.parts.filter(p=>p.name==='Interior · timber floor');
   return {id,expected,parts:m.parts.length,gables:gables.map(p=>({name:p.name,vertices:p.topologyMesh?.positions?.length/3,triangles:p.topologyMesh?.indices?.length/3,group:p.group})),floor:floor.length};
  });
 });
 console.log('SE236_HOUSES',JSON.stringify(houses));
 for(const h of houses){
  assert.equal(h.parts,h.expected,h.id+' incorrect editable part count');
  assert.equal(h.gables.length,h.id==='sheep-free-shelter'?0:2,'Enclosed house must have front and rear attic solid');
  assert.equal(h.floor,h.id==='sheep-free-shelter'?0:1,'Enclosed house must have floor');
  assert(h.gables.every(x=>x.triangles===8&&x.vertices===6),'Gable should be real closed 3D triangle prism, not billboard');
 }
 // Project hub is account-aware, so wait for existing native starter navigation.
 await page.waitForFunction(()=>document.getElementById('se236StarterGroups'),null,{timeout:30000});
 const grouping=await page.evaluate(()=>{
  const sel=id=>document.getElementById(id);
  const cards=id=>[...sel(id).querySelectorAll('button[data-project-template]')].map(b=>b.dataset.projectTemplate);
  const games=cards('se236StarterGames'),models=cards('se236StarterModels');
  sel('se236StarterTab-models').click();
  const selected=sel('se236StarterTab-models').getAttribute('aria-selected');
  const hidden={games:sel('se236StarterGames').hidden,models:sel('se236StarterModels').hidden};
  return {games,models,selected,hidden,defaults:sel('se236StarterModels').querySelectorAll('input[data-se128-default]').length,
   myProjectsStillPresent:!!sel('se170-tab-mine')};
 });
 console.log('SE236_STARTER_TABS',JSON.stringify(grouping));
 assert(grouping.games.length>=3,'Starter Games should keep original game cards');
 assert(grouping.models.length>=7,'Starter Models should show multiple native models');
 assert(grouping.models.includes('sheep-ram-house')&&grouping.models.includes('wolf-model'));
 assert(!grouping.games.includes('sheep-ram-house'));
 assert.equal(grouping.selected,'true');assert.equal(grouping.hidden.games,true);assert.equal(grouping.hidden.models,false);
 assert(grouping.defaults>=5,'Default project checkboxes must remain with model cards');
 assert(grouping.myProjectsStillPresent,'Existing My Projects must remain separate');

 await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.loadAnimal('wolf',{force:true}));
 await page.waitForFunction(()=>window.SWYRL_ENGINE_WOLF_RIG?.status?.().skinned&&
  window.SWYRL_ENGINE_WORKSPACES?.active?.()==='modeler',null,{timeout:65000});
 const face=await page.evaluate(()=>window.SE236_TEST_DIAG.faces());
 console.log('SE236_WOLF_FACE_WEIGHTS',JSON.stringify(face));
 for(const p of face){
  assert(p.head>0.999,'Face detail must follow skull: '+p.name+' '+JSON.stringify(p));
  assert(p.spine<0.001,'Face detail must not lag on torso: '+p.name);
 }
 assert(face.length>=3,'Expected nose and cheek face test cases');
 const preview=await page.evaluate(()=>{
  const clip=document.getElementById('modelAtelierWolfClip');
  clip.value='run';clip.dispatchEvent(new Event('change',{bubbles:true}));
  const time=document.getElementById('modelAtelierWolfTime');
  time.value='.25';time.dispatchEvent(new Event('input',{bubbles:true}));
  const before=window.SE236_TEST_DIAG.preview();
  const place=document.getElementById('se236WolfInPlace'),steady=document.getElementById('se236WolfSteady');
  place.checked=false;steady.checked=false;steady.dispatchEvent(new Event('change',{bubbles:true}));
  time.value='.25';time.dispatchEvent(new Event('input',{bubbles:true}));
  const authored=window.SE236_TEST_DIAG.preview();
  place.checked=true;steady.checked=true;steady.dispatchEvent(new Event('change',{bubbles:true}));
  time.value='.25';time.dispatchEvent(new Event('input',{bubbles:true}));
  const restored=window.SE236_TEST_DIAG.preview();
  return {before,authored,restored,controls:{inPlace:!!place,steady:!!steady}};
 });
 console.log('SE236_WOLF_ROOT_PREVIEW',JSON.stringify(preview));
 assert(preview.controls.inPlace&&preview.controls.steady);
 assert(Math.abs(preview.before.rootY)<1e-8,'In-place root should be locked by default');
 assert(Math.abs(preview.authored.rootY)>0.001,'Uncheck root lock to reveal authored bob');
 assert(Math.abs(preview.restored.rootY)<1e-8,'Re-enabling in-place must restore level root');
 assert(Math.abs(preview.restored.spineX)<Math.abs(preview.authored.spineX)*.25,
  'Steady torso must suppress run rocking, while authored pose remains available');
 assert.deepEqual(errors,[],'Unexpected browser errors');
 console.log('SE236_NATIVE_GABLE_WOLF_ROOT_STARTERS_PASS');
 await ctx.close();
}finally{await browser.close();}
