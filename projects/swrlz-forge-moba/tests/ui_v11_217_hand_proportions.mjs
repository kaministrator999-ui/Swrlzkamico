// Owner's 2nd review: focused mobile-width native Model Atelier verification.
// This checks model fidelity (relative finger lengths, taper, and outer-palm
// contour) plus loader safety, not a generic all-engine browser suite.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist='/tmp/se217-hand-candidate';
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
try{
 const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 const page=await context.newPage();
 const errors=[],consoleErrors=[];
 page.on('pageerror',e=>{errors.push(String(e));console.log('HAND217_PAGE_ERROR',String(e));});
 page.on('console',e=>{if(e.type()==='error'){consoleErrors.push(e.text());console.log('HAND217_CONSOLE_ERROR',e.text().slice(0,1300));}});
 await page.route('**/*',route=>{
  const url=new URL(route.request().url());
  if(url.origin===host){
   const rel=url.pathname==='/'?'index.html':url.pathname.replace(/^\/+/, '');
   const file=path.resolve(dist,rel);
   if(file===dist||!file.startsWith(dist+'/')||!fs.existsSync(file)){route.fulfill({status:404,body:'missing asset'});return;}
   route.fulfill({status:200,path:file,contentType:rel.endsWith('.html')?'text/html':undefined});return;
  }
  if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'].includes(url.host)){route.continue();return;}
  route.abort();
 });
 await page.goto(host+'/modeler.html?project=floating-hand-glove',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_MODEL_ATELIER?.status?.().count>=45,null,{timeout:60000});
 const facts=await page.evaluate(()=>{
  const scene=window.SWYRL_ENGINE_FLOATING_HAND.createScene();
  const m=scene.project.modelAtelier,p=m.parts;
  const hand=p.find(o=>o.id==='floating-hand-000').topologyMesh;
  const vertices=[];
  for(let i=0;i<hand.positions.length;i+=3)vertices.push([hand.positions[i],hand.positions[i+1],hand.positions[i+2]]);
  function bounds(cond){
   const v=vertices.filter(cond);
   return {count:v.length,
     x:[Math.min(...v.map(q=>q[0])),Math.max(...v.map(q=>q[0]))],
     y:[Math.min(...v.map(q=>q[1])),Math.max(...v.map(q=>q[1]))],
     z:[Math.min(...v.map(q=>q[2])),Math.max(...v.map(q=>q[2]))]};
  }
  const tips=p.filter(x=>/^Digit [1-4] · glowing tip/.test(x.name)).sort((a,b)=>a.name.localeCompare(b.name));
  const gems=p.filter(x=>/^Digit [1-4] · silver knuckle gem/.test(x.name)).sort((a,b)=>a.name.localeCompare(b.name));
  return {
   build:window.SWRLZ_FORGE_BUILD?.version,
   status:window.SWYRL_ENGINE_MODEL_ATELIER.status(),
   total:p.length,groups:m.meshGroups?.length,
   hasOldSockets:!!m.assemblies,
   coreVertices:vertices.length,
   palm:bounds(v=>v[1]>1.53&&v[1]<1.85&&Math.abs(v[0])<.25),
   pinkySide:bounds(v=>v[1]>1.41&&v[1]<1.92&&v[0]>.35),
   thumb:bounds(v=>v[0]<-.80&&v[1]>1.55&&v[1]<2.10),
   tipY:tips.map(x=>x.position[1]),tipX:tips.map(x=>x.position[0]),
   gemWidths:gems.map(x=>x.scale[0]),gems:gems.length,
   modelVisible:!document.getElementById('modelAtelierPanel')?.hidden,
   thumbTrim:p.filter(x=>x.name.startsWith('Thumb')).length,
   outerTrim:p.filter(x=>x.name.startsWith('Ulnar')).length
  };
 });
 console.log('HAND217_ANATOMY_FACTS',JSON.stringify(facts));
 assert.equal(facts.build,'v11.217');
 assert.equal(facts.status.open,true);
 assert.equal(facts.status.active,true);
 assert.equal(facts.modelVisible,true);
 assert.equal(facts.status.count,facts.total);
 assert(facts.total>=50&&facts.groups>=8);
 assert(!facts.hasOldSockets);
 assert(facts.coreVertices>7000,'continuous organic hand not generated');
 assert(facts.palm.count>100&&facts.palm.z[1]-facts.palm.z[0]>.47,'palm became a slab');
 assert(facts.pinkySide.count>75&&facts.pinkySide.x[1]>.52&&facts.pinkySide.x[1]<.72,
  'pinky-side hypothenar contour still swollen or missing');
 assert(facts.thumb.count>100&&facts.thumb.x[0]<-1.09&&facts.thumb.z[1]>.20,
  'thumb web/root projection missing');
 assert.equal(facts.gems,4);
 const [index,middle,ring,pinky]=facts.tipY;
 assert(middle>ring&&ring>index&&index>pinky,'fingers do not follow natural relative length');
 assert(middle-pinky>.30&&ring-index<.17,'unbalanced finger heights');
 assert(facts.gemWidths[3]<facts.gemWidths[1]*.85,'pinky knuckle still uniform/oversized');
 assert(facts.thumbTrim>=4&&facts.outerTrim===2,'thumb/ulnar contour parts missing');
 assert.deepEqual(errors,[],'browser page errors');
 assert.deepEqual(consoleErrors,[],'browser console errors');
 await context.close();
}finally{await browser.close();}
