// §E v11.225: single 390px wolf-model / Sheep Tag visual rig smoke.
// Only the wolf paths, not the historic game/browser suite.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist='/tmp/se225-wolf-smoke';
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
const failures=[];
try{
 const context=await browser.newContext({
  viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 const page=await context.newPage();
 page.on('pageerror',e=>failures.push(e.message));
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
 await page.goto(host+'/modeler.html?project=wolf-model',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>{
  const r=window.SWYRL_ENGINE_WOLF_RIG?.status?.();
  return r?.available && r.skinned && r.bones===14&&r.clips===10&&r.skinnedMeshes>=10;
 },null,{timeout:120000});
 const facts=await page.evaluate(()=>({
  version:window.SWRLZ_FORGE_BUILD.version,
  model:window.SWYRL_ENGINE_MODEL_ATELIER?.status?.(),
  wolf:window.SWYRL_ENGINE_WOLF_RIG.status(),
  visible:!document.getElementById('modelAtelierWolfStudio')?.hidden
 }));
 console.log('WOLF225_EDITOR_FACTS',JSON.stringify(facts));
 assert.equal(facts.version,'v11.225');
 assert(facts.visible && facts.wolf.skinnedMeshes>10);
 await page.evaluate(()=>document.getElementById('seReleaseNotesDialog')?.close());
 const studio=page.locator('#modelAtelierWolfStudio');
 await studio.locator('summary').click({force:true});
 await page.locator('#modelAtelierWolfClip').selectOption('howl');
 await page.locator('#modelAtelierWolfTime').evaluate(el=>{
  el.value='.90';el.dispatchEvent(new Event('input',{bubbles:true}));});
 const howling=await page.evaluate(()=>window.SWYRL_ENGINE_WOLF_RIG.status());
 console.log('WOLF225_HOWL',JSON.stringify(howling));
 assert(howling.headX<-.12 && howling.jawX>.05,'howl must raise muzzle and open jaw');
 await page.locator('#modelAtelierWolfClip').selectOption('run');
 await page.locator('#modelAtelierWolfTime').evaluate(el=>{
  el.value='.11';el.dispatchEvent(new Event('input',{bubbles:true}));});
 const running=await page.evaluate(()=>window.SWYRL_ENGINE_WOLF_RIG.status());
 assert(Math.abs(running.foreLegX)>.1,'run must articulate a front leg');
 await page.locator('#modelAtelierWolfPlay').click({force:true});
 assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_WOLF_RIG.status())).playing,true);
 await page.locator('#modelAtelierWolfPlay').click({force:true});
 assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_WOLF_RIG.status())).playing,false);
 await page.locator('#modelAtelierWolfBone').selectOption('wolf_jaw');
 await page.locator('#modelAtelierWolfX').evaluate(el=>{
  el.value='.3';el.dispatchEvent(new Event('input',{bubbles:true}));
  el.dispatchEvent(new Event('change',{bubbles:true}));});
 await page.locator('#modelAtelierWolfSaveKey').click({force:true});
 assert(Math.abs((await page.evaluate(()=>window.SWYRL_ENGINE_WOLF_RIG.status())).jawX-.3)<.03);
 assert.deepEqual(failures,[],'wolf modeler runtime errors');
 console.log('WOLF225_EDITOR_SMOKE_PASS=skinned wolf model, 14 bones, 10 clips, howl/run motions and save key');
 await page.close();
 const game=await context.newPage();
 game.on('pageerror',e=>failures.push(e.message));
 await game.goto(host+'/index.html?project=sheep-tag-meadow',{waitUntil:'domcontentloaded',timeout:90000});
 await game.waitForFunction(()=>typeof window.SWYRL_ENGINE_WOLF_224?.active==='function',null,{timeout:60000});
 const gameState=await game.evaluate(()=>{
  const api=window.SWYRL_ENGINE_WOLF_224.active();
  const wolves=typeof actors!=='undefined'?actors.filter(a=>a.userData?.actorType==='st-wolf'):[];
  return {api,visuals:wolves.map(a=>({
   jaw:!!a.getObjectByName('stJaw'),
   face:!!a.getObjectByName('Astra · enhanced head'),
   body:!!a.getObjectByName('Astra · enhanced body')
  }))};
 });
 console.log('WOLF225_GAME_FACTS',JSON.stringify(gameState));
 assert.equal(gameState.api.animations.length,10);
 assert(gameState.visuals.length>=1);
 assert(gameState.visuals.every(w=>w.jaw&&w.face&&w.body),'Astra game wolf visual overlay');
 assert.deepEqual(failures,[],'game runtime errors');
 console.log('WOLF225_GAME_SMOKE_PASS=Sheep Tag wolf jaw, face and body detail, shared 10 clips');
 await context.close();
}finally{await browser.close();}
