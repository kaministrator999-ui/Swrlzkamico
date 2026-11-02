// Focused native Model Atelier loading reproduction for the five sheep starter cards.
// One browser viewport / existing JS and WebGL, no broad Sheep Tag or full UI suites.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist='/tmp/se229-sheep-loader';
const ids=['sheep-free-shelter','sheep-thatched-hut','sheep-cottage','sheep-barn','sheep-ram-house'];
const expectedCounts={'sheep-free-shelter':18,'sheep-thatched-hut':59,'sheep-cottage':68,'sheep-barn':37,'sheep-ram-house':60};
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'
]});
const pageErrors=[];
try{
 const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 await context.route('**/*',route=>{
  const u=new URL(route.request().url());
  if(u.origin===host){
   const rel=u.pathname==='/'?'index.html':u.pathname.replace(/^\/+/,'');
   const file=path.resolve(dist,rel);
   if(file===dist||!file.startsWith(dist+'/')||!fs.existsSync(file))
    return route.fulfill({status:404,body:'not bundled'});
   return route.fulfill({status:200,path:file,contentType:rel.endsWith('.html')?'text/html':undefined});
  }
  if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'].includes(u.hostname))return route.continue();
  return route.abort();
 });
 const p=await context.newPage();
 p.on('pageerror',e=>{pageErrors.push(String(e));console.log('SHEEP_HOUSE_PAGE_ERROR',String(e).slice(0,1000))});
 p.on('console',msg=>{if(msg.type()==='error')console.log('SHEEP_HOUSE_CONSOLE_ERROR',msg.text().slice(0,1000))});
 // Test user-facing deep link and the same native Model Atelier status as existing hand models.
 await p.goto(host+'/modeler.html?project=sheep-free-shelter',{waitUntil:'domcontentloaded',timeout:90000});
 await p.waitForFunction(()=>!!window.SWYRL_ENGINE_SHEEP_BUILDING_STARTERS,null,{timeout:25000});
 await p.waitForTimeout(2000);
 async function facts(){
  return p.evaluate(()=>({
   version:window.SWRLZ_FORGE_BUILD?.version||null,
   active:window.SWYRL_ENGINE_MODEL_ATELIER?.status?.()||null,
   current:typeof currentProject==='object' ? {
    id:currentProject?.canonicalId,name:currentProject?.name,kind:currentProject?.kind,
    count:currentProject?.modelAtelier?.parts?.length,
    schema:currentProject?.modelAtelier?.schema
   }:null,
   panelHidden:document.getElementById('modelAtelierPanel')?.hidden,
   partOptions:document.querySelectorAll('#modelAtelierParts option').length,
   cards:document.querySelectorAll('[data-project-template^="sheep-"]').length,
   status:document.querySelector('#modelAtelierStatus')?.textContent?.slice(0,260),
   toast:document.querySelector('#statusBar')?.textContent?.slice(0,260)
  }));
 }
 let first=await facts();console.log('SHEEP_HOUSE_DIRECT_OPEN_FACTS',JSON.stringify(first));
 assert.equal(first.active?.count,expectedCounts['sheep-free-shelter'],'Deep link must open complete shelter model');
 assert.equal(first.active?.open,true,'Model Atelier panel must be open from a deep link');
 assert(first.active.count>=15,'Expected native house meshes');
 // Exercise the actual same native starter dispatch path as a Projects card.
 for(const id of ids){
  const result=await p.evaluate(id=>window.SWYRL_ENGINE_SHEEP_BUILDING_STARTERS.open(id,true),id);
  await p.waitForTimeout(300);
  const state=await facts();
  console.log('SHEEP_HOUSE_NATIVE_OPEN',id,'returned=',result,JSON.stringify(state));
  assert.equal(result,true,id+' did not open');
  assert.equal(state.active?.count,expectedCounts[id],id+' wrong editable model parts');
  assert.equal(state.active?.open,true,'Model Atelier panel failed to open '+id);
  assert(state.active.count>=15,'Model Atelier missing editable house parts '+id);
  assert(state.partOptions>=15,'House parts list blank '+id);
 }
 assert.deepEqual(pageErrors,[],'Unexpected page errors');
 console.log('SHEEP_HOUSE_ALL_NATIVE_LOADING_PASS five projects and direct route');
 await context.close();
}finally{await browser.close()}
