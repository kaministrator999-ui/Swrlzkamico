// §E v11.220 single-case mobile runtime smoke.
// No broad browser suite: load only the native hand, inspect real skinning,
// pose it, verify visible deformation, scrub and play one skeletal clip.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist='/tmp/se220-hand-sealed';
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
try{
 const context=await browser.newContext({
  viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 const page=await context.newPage();
 const pageErrors=[],consoleErrors=[];
 page.on('pageerror',e=>pageErrors.push(String(e)));
 page.on('console',e=>{if(e.type()==='error')consoleErrors.push(e.text());});
 await page.route('**/*',route=>{
  const url=new URL(route.request().url());
  if(url.origin===host){
   const rel=url.pathname==='/'?'index.html':url.pathname.replace(/^\/+/, '');
   const local=path.resolve(dist,rel);
   if(local===dist||!local.startsWith(dist+'/')||!fs.existsSync(local)){
    route.fulfill({status:404,body:'not bundled'});return;
   }
   route.fulfill({status:200,path:local,contentType:rel.endsWith('.html')?'text/html':undefined});return;
  }
  if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'].includes(url.host)){route.continue();return;}
  route.abort();
 });
 await page.goto(host+'/modeler.html?project=floating-hand-glove',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>{
  const m=window.SWYRL_ENGINE_MODEL_ATELIER?.status?.();
  const r=window.SWYRL_ENGINE_RIG_STUDIO?.status?.();
  return m?.open===true && m.count>80 && r?.available && r?.skinned && r.bones===17;
 },null,{timeout:60000});
 const facts=await page.evaluate(()=>{
  const scene=window.SWYRL_ENGINE_FLOATING_HAND.createScene();
  const rig=scene.project.modelAtelier.rigging;
  return {version:window.SWRLZ_FORGE_BUILD.version,
   rig:window.SWYRL_ENGINE_RIG_STUDIO.status(),bones:rig.bones.map(b=>b.id),
   coreVertices:scene.project.modelAtelier.parts.find(p=>p.id==='floating-hand-000').topologyMesh.positions.length/3,
   oldDeckHidden:document.getElementById('modelAtelierPoseDeck')?.hidden,
   studioVisible:!document.getElementById('modelAtelierRigStudio')?.hidden};
 });
 console.log('RIG220_MOBILE_FACTS',JSON.stringify(facts));
 assert.equal(facts.version,'v11.220');
 assert(facts.coreVertices>8000);
 assert(facts.rig.skinned&&facts.studioVisible&&facts.oldDeckHidden);
 assert.equal(facts.bones.length,17);
 // Dismiss the product release-notes modal before interacting with studio controls.
 await page.evaluate(()=>{const dialog=document.getElementById('seReleaseNotesDialog');if(dialog?.open)dialog.close();});
 const stage=page.locator('#modelAtelierViewport');
 const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
 await page.waitForTimeout(300);
 const neutral=sha(await stage.screenshot());
 const hit=await page.evaluate(()=>{
  const summary=document.querySelector('#modelAtelierRigStudio summary');
  const box=summary.getBoundingClientRect(),cx=box.left+box.width/2,cy=box.top+box.height/2;
  const over=document.elementFromPoint(cx,cy);
  const panel=document.getElementById('modelAtelierRigStudio');
  return {x:cx,y:cy,front:over?.className||over?.tagName,
   own:over===summary||summary.contains(over),
   rigZ:getComputedStyle(panel).zIndex,
   dockZ:getComputedStyle(document.querySelector('.atelier-component-dock')).zIndex};
 });
 console.log('RIG220_TOUCH_HIT',JSON.stringify(hit));
 await page.locator('#modelAtelierRigStudio summary').click();
 await page.locator('#modelAtelierRigFist').click();
 await page.waitForTimeout(350);
 const fist=sha(await stage.screenshot());
 assert.notEqual(neutral,fist,'GPU weighted glove did not visibly change after Fist pose');
 await page.locator('#modelAtelierRigJoint').selectOption('index_pip');
 const slider=page.locator('#modelAtelierRigX');
 await slider.evaluate(el=>{el.value='.28';el.dispatchEvent(new Event('input',{bubbles:true}));
                             el.dispatchEvent(new Event('change',{bubbles:true}));});
 assert.equal(await page.locator('#modelAtelierRigXValue').textContent(),'16°');
 await page.locator('#modelAtelierRigKey').click();
 await page.locator('#modelAtelierRigPlay').click();
 await page.waitForTimeout(180);
 assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_RIG_STUDIO.status())).playing,true);
 await page.locator('#modelAtelierRigStop').click();
 assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_RIG_STUDIO.status())).playing,false);
 assert.deepEqual(pageErrors,[],'page exceptions');
 assert.deepEqual(consoleErrors,[],'console errors');
 console.log('RIG220_MOBILE_SMOKE_PASS=17 bones, native model loads, weighted skin visibly bends, pose/key/clip usable');
 await context.close();
}finally{await browser.close();}
