// Focused visual-runtime acceptance: open the actual Model Atelier hand starter
// and prove anatomical XYZ geometry, not merely a JSON build or a title string.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist='/tmp/se215-candidate';
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
try{
 const ctx=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 const page=await ctx.newPage(),errors=[],consoleErrors=[];
 page.on('pageerror',e=>{errors.push(String(e));console.log('SE215_PAGE_ERROR',String(e));});
 page.on('console',e=>{if(e.type()==='error'){consoleErrors.push(e.text());console.log('SE215_CONSOLE_ERROR',e.text().slice(0,1200));}});
 await page.route('**/*',route=>{
  const url=new URL(route.request().url());
  if(url.origin===host){
   const rel=url.pathname==='/'?'index.html':url.pathname.replace(/^\/+/, '');
   const file=path.resolve(dist,rel);
   if(file===dist||!file.startsWith(dist+'/')||!fs.existsSync(file)){
    route.fulfill({status:404,body:'Missing candidate asset'});return;
   }
   route.fulfill({status:200,path:file,contentType:rel.endsWith('.html')?'text/html':undefined});return;
  }
  if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'].includes(url.host)){route.continue();return;}
  route.abort();
 });
 await page.goto(host+'/modeler.html?project=floating-hand-glove',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_MODEL_ATELIER?.status?.().count>=50,null,{timeout:60000});
 const facts=await page.evaluate(()=>{
  const api=window.SWYRL_ENGINE_FLOATING_HAND,scene=api.createScene(),m=scene.project.modelAtelier;
  const core=m.parts.find(p=>p.id==='floating-hand-000');
  const pos=core.topologyMesh.positions;
  const rows=[];
  for(let i=0;i<pos.length;i+=3)rows.push([pos[i],pos[i+1],pos[i+2]]);
  const slice=(predicate)=>{
   const selected=rows.filter(predicate);
   const ext=[0,1,2].map(axis=>[Math.min(...selected.map(v=>v[axis])),Math.max(...selected.map(v=>v[axis]))]);
   return {n:selected.length,x:ext[0],y:ext[1],z:ext[2]};
  };
  const palm=slice(v=>v[1]>1.53&&v[1]<1.82&&v[0]>-.27&&v[0]<.25);
  const pinky=slice(v=>v[1]>1.42&&v[1]<1.90&&v[0]>.38);
  const thumb=slice(v=>v[0]<-.83&&v[1]>1.56&&v[1]<2.13);
  return {
   build:window.SWRLZ_FORGE_BUILD?.version,
   status:window.SWYRL_ENGINE_MODEL_ATELIER.status(),
   name:m.name,parts:m.parts.length,hasOldSockets:!!m.assemblies,
   groups:m.meshGroups?.length,coreVertices:pos.length/3,
   palm,pinky,thumb,
   fingerJointPieces:m.parts.filter(p=>p.name.includes('palmar flex crease')).length,
   ulnarPieces:m.parts.filter(p=>p.name.includes('Ulnar edge')).length,
   armorPieces:m.parts.filter(p=>p.name.includes('Backhand')||p.name.includes('Thumb')).length,
   panelVisible:!document.getElementById('modelAtelierPanel')?.hidden
  };
 });
 console.log('SE215_ANATOMY_FACTS',JSON.stringify(facts));
 assert.equal(facts.build,'v11.215');
 assert.equal(facts.panelVisible,true,'native model editor is not visible');
 assert.equal(facts.status.active,true);
 assert.equal(facts.status.open,true);
 assert.equal(facts.status.count,facts.parts);
 assert(facts.parts>=50,'anatomy trim parts did not load');
 assert.equal(facts.hasOldSockets,false);
 assert(facts.coreVertices>3500,'connected hand surface was not generated');
 assert(facts.palm.n>100,'palm cross section missing');
 assert(facts.palm.z[1]-facts.palm.z[0]>.48,'palm still planar');
 assert(facts.pinky.n>30&&facts.pinky.x[1]>.67,'opposite-thumb ulnar edge still straight / narrow');
 assert(facts.thumb.n>20&&facts.thumb.z[1]>.22,'thumb pad and forward projecting root missing');
 assert.equal(facts.fingerJointPieces,4,'finger flexion seams missing');
 assert(facts.ulnarPieces>=2,'side armor absent');
 assert.equal(errors.length,0,'uncaught browser error');
 assert.equal(consoleErrors.length,0,'browser console errors');
 await ctx.close();
}finally{await browser.close();}
