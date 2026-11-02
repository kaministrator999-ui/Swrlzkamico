// §E v11.226: single 390px wolf-model / Sheep Tag visual rig smoke.
// Only the wolf paths, not the historic game/browser suite.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist='/tmp/se226-wolf-smoke';
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
const failures=[];
try{
 const context=await browser.newContext({
  viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 const page=await context.newPage();
 page.on('framenavigated',f=>console.log('WOLF_FRAME_NAV',f.url()));
 page.on('pageerror',e=>{failures.push(e.message);console.log('WOLF226_PAGE_ERROR',e.message);});
 page.on('response',r=>{if(r.status()>=400&&r.url().includes('model-atelier'))console.log('WOLF226_ASSET_STATUS',r.status(),r.url());});
 await context.route('**/*',route=>{
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
 await page.goto(host+'/modeler.html',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>typeof window.SWYRL_ENGINE_MODEL_ATELIER?.loadAnimal==='function',null,{timeout:30000});
 const opened=await page.evaluate(async()=>await window.SWYRL_ENGINE_MODEL_ATELIER.loadAnimal('wolf',{force:true}));
 console.log('WOLF226_OPEN_WOLF_MODEL',opened);
 assert.equal(opened,true,'Wolf Model starter must open via its actual user-facing API');
 await page.waitForFunction(()=>{
  const r=window.SWYRL_ENGINE_WOLF_RIG?.status?.();
  return r?.available && r.skinned && r.bones===14&&r.clips===10&&r.skinnedMeshes>=10;
 },null,{timeout:45000,polling:300}).catch(async e=>{
  console.log('WOLF226_LOAD_DEBUG',JSON.stringify(await page.evaluate(()=>({
   build:window.SWRLZ_FORGE_BUILD?.version,
   model:window.SWYRL_ENGINE_MODEL_ATELIER?.status?.(),
   rig:window.SWYRL_ENGINE_WOLF_RIG?.status?.(),
   project:typeof currentProject!=='undefined'?currentProject?.canonicalId:null,
   toast:document.getElementById('statusBar')?.textContent?.slice(-250),
   wolfPanel:!!document.getElementById('modelAtelierWolfStudio'),
   audit:window.SWYRL_WOLF_LOAD_AUDIT||null,
   loader:typeof window.SWYRL_ENGINE_MODEL_ATELIER?.loadAnimal==='function'?String(window.SWYRL_ENGINE_MODEL_ATELIER.loadAnimal).slice(0,240):null,
   actualLoader:typeof loadAnimalProject==='function'?String(loadAnimalProject).slice(0,2800):null,
   activeProject:typeof currentProject!=='undefined'?{kind:currentProject?.kind,modelName:currentProject?.modelAtelier?.name,parts:currentProject?.modelAtelier?.parts?.length,rig:!!currentProject?.modelAtelier?.wolfRig}:null,
   url:location.href
  })).catch(err=>({evalError:String(err)}))));
  console.log('WOLF226_ERRORS',JSON.stringify(failures));
  throw e;
 });
 const facts=await page.evaluate(()=>({
  version:window.SWRLZ_FORGE_BUILD.version,
  model:window.SWYRL_ENGINE_MODEL_ATELIER?.status?.(),
  wolf:window.SWYRL_ENGINE_WOLF_RIG.status(),
  visible:!document.getElementById('modelAtelierWolfStudio')?.hidden
 }));
 console.log('WOLF226_EDITOR_FACTS',JSON.stringify(facts));
 assert.equal(facts.version,'v11.226');
 assert(facts.visible && facts.wolf.skinnedMeshes>10);
 await page.evaluate(()=>document.getElementById('seReleaseNotesDialog')?.close());
 const studio=page.locator('#modelAtelierWolfStudio');
 await studio.locator('summary').scrollIntoViewIfNeeded();
 const wasOpen=await studio.evaluate(el=>el.open);
 console.log('WOLF226_PANEL_INITIAL',JSON.stringify(await studio.evaluate(el=>({
  open:el.open,hidden:el.hidden,rect:el.getBoundingClientRect().toJSON(),
  selectVisible:!!document.getElementById('modelAtelierWolfClip')?.getClientRects().length
 }))));
 console.log('WOLF226_PANEL_HIT',JSON.stringify(await studio.evaluate(el=>{
  const summary=el.querySelector('summary'),r=summary.getBoundingClientRect();
  const top=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
  return {summaryHit:top===summary||summary.contains(top),
    target:top?.id||top?.className||top?.tagName,
    targetParent:top?.parentElement?.id||top?.parentElement?.className||null,
    ownZ:getComputedStyle(el).zIndex,
    sceneZ:getComputedStyle(el.parentElement).zIndex};
 })));
 const hit=await studio.evaluate(el=>{
  const summary=el.querySelector('summary'),r=summary.getBoundingClientRect();
  const top=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
  return top===summary||summary.contains(top);
 });
 assert(hit,'wolf animation summary must receive a real tap, not an overlapping tool button');
 if(!wasOpen)await studio.locator('summary').click();

 console.log('WOLF226_PANEL_AFTER',JSON.stringify(await studio.evaluate(el=>({
  open:el.open,hidden:el.hidden,selectVisible:!!document.getElementById('modelAtelierWolfClip')?.getClientRects().length
 }))));
 assert(await studio.evaluate(el=>el.open),'wolf studio should expand by tapping summary');
 await page.locator('#modelAtelierWolfClip').selectOption('howl');
 await page.locator('#modelAtelierWolfTime').evaluate(el=>{
  el.value='.90';el.dispatchEvent(new Event('input',{bubbles:true}));});
 const howling=await page.evaluate(()=>window.SWYRL_ENGINE_WOLF_RIG.status());
 console.log('WOLF226_HOWL',JSON.stringify(howling));
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
 console.log('WOLF226_EDITOR_SMOKE_PASS=skinned wolf model, 14 bones, 10 clips, howl/run motions and save key');
 await page.close();
 const game=await context.newPage();
 game.on('pageerror',e=>failures.push(e.message));
 await game.goto(host+'/index.html?project=sheep-tag-meadow',{waitUntil:'domcontentloaded',timeout:90000});
 await game.waitForFunction(()=>typeof window.SWYRL_ENGINE_WOLF_224?.active==='function',null,{timeout:60000,polling:200});
 const gameState=await game.evaluate(()=>({
  api:window.SWYRL_ENGINE_WOLF_224.active(),
  prefab:window.SWYRL_ENGINE_WOLF_224.prefab()
 }));
 console.log('WOLF226_GAME_PREFAB',JSON.stringify(gameState));
 assert.equal(gameState.api.animations.length,10);
 assert(gameState.prefab.furred && gameState.prefab.head && gameState.prefab.jaw &&
  gameState.prefab.face && gameState.prefab.body && gameState.prefab.paws===4,
  'Sheep Tag wolf prefab must include furred Astra, four leg joints and enhanced head/jaw');
 assert(gameState.prefab.visualMeshes>=25,'wolf game prefab must have renderable meshes');
 assert.deepEqual(failures,[],'game runtime errors');
 console.log('WOLF226_GAME_PREFAB_PASS=Sheep Tag wolf prefab, four legs, jaw, enhanced fur and 10 shared motion clips');
 await context.close();
}finally{await browser.close();}
