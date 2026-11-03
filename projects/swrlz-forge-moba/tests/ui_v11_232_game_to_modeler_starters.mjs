// Focused regression for owner's mobile screenshot:
// Selecting Model Atelier assets from Game Engine must show 3D Modeling,
// not leave Game Engine selected with only World Ground.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const base='/tmp/se232-model-routing';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'
]});
const errors=[];
try{
 const context=await browser.newContext({viewport:{width:390,height:844},
  isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 await context.route('**/*',route=>{
  const u=new URL(route.request().url());
  if(u.origin===host){
   const rel=u.pathname==='/'?'index.html':u.pathname.replace(/^\/+/,'');
   const file=path.resolve(base,rel);
   if(file===base||!file.startsWith(base+'/')||!fs.existsSync(file))
    return route.fulfill({status:404,body:'Missing package file'});
   return route.fulfill({status:200,path:file,contentType:rel.endsWith('.html')?'text/html':undefined});
  }
  if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'].includes(u.hostname))return route.continue();
  return route.abort();
 });
 const page=await context.newPage();
 page.on('pageerror',e=>{errors.push(String(e));console.log('SE232_PAGE_ERROR',String(e).slice(0,500))});
 await page.goto(host+'/index.html',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES?.active?.()==='game'&&
  typeof window.SE232_TEST_OPEN_TEMPLATE==='function',null,{timeout:30000});
 const initial=await page.evaluate(()=>({
  workspace:window.SWYRL_ENGINE_WORKSPACES.inspect(),
  opened:window.SWYRL_ENGINE_MODEL_ATELIER.status().open
 }));
 assert.equal(initial.workspace.active,'game');
 assert.equal(initial.opened,false,'Game-first startup must never open the Modeler');
 console.log('SE232_START_GAME',JSON.stringify(initial));
 async function openCheck(id,min,max){
  const started=Date.now();
  const result=await page.evaluate(async id=>await Promise.resolve(
   window.SE232_TEST_OPEN_TEMPLATE(id)),id);
  await page.waitForFunction(([min,max])=>{
   const ws=window.SWYRL_ENGINE_WORKSPACES?.inspect?.();
   const state=window.SWYRL_ENGINE_MODEL_ATELIER?.status?.();
   return ws?.active==='modeler'&&ws?.projectKind==='model-atelier'&&
    location.pathname.endsWith('/modeler.html')&&
    state?.open===true&&state.count>=min&&state.count<=max;
  },[min,max],{timeout:50000});
  const facts=await page.evaluate(()=>({
   version:window.SWRLZ_FORGE_BUILD?.version,
   workspace:window.SWYRL_ENGINE_WORKSPACES.inspect(),
   atelier:window.SWYRL_ENGINE_MODEL_ATELIER.status(),
   gameTab:document.querySelector('.se187-game-tabs [data-se187-tab="game"]')?.getAttribute('aria-selected'),
   modelTab:document.querySelector('.se187-game-tabs [data-se187-tab="modeler"]')?.getAttribute('aria-selected'),
   panelHidden:document.querySelector('#modelAtelierPanel')?.hidden,
   nativeCanvas:document.querySelector('#modelAtelierViewport canvas')?.getBoundingClientRect()?.toJSON(),
   modelPartOptions:document.querySelectorAll('#modelAtelierParts option').length,
   wolf:window.SWYRL_WOLF_LOAD_AUDIT||null,
   studioMode:document.querySelector('#modelAtelierPanel')?.classList.contains('courier-studio')
  }));
  console.log('SE232_MODEL_VISIBLE',id,'result=',result,'elapsedMs=',Date.now()-started,
   JSON.stringify(facts));
  assert.notEqual(result,false,'Native starter returned false: '+id);
  assert.equal(facts.workspace.active,'modeler');
  assert.equal(facts.workspace.route,'/modeler.html');
  assert.equal(facts.modelTab,'true');
  assert.equal(facts.gameTab,'false');
  assert.equal(facts.panelHidden,false);
  assert.equal(facts.atelier.open,true);
  assert(facts.nativeCanvas?.width>100&&facts.nativeCanvas?.height>140,
   'Modeler renderer must be visible');
  assert.equal(facts.modelPartOptions,facts.atelier.count);
  assert.equal(facts.studioMode,false,'Model starter must expose editing tools');
  return facts;
 }
 const home=await openCheck('sheep-ram-house',60,60);
 assert.equal(home.atelier.count,60);
 await page.evaluate(()=>window.SWYRL_ENGINE_WORKSPACES.change('game'));
 await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES.active()==='game');
 const wolf=await openCheck('wolf-model',60,400);
 assert.equal(wolf.wolf?.rig,true,'Wolf rig must be attached before initial rendering');
 assert(wolf.wolf?.clips>=10,'Wolf rig clips lost');
 // The Courier card is a different loader than wolf-model; route it too.
 await page.evaluate(()=>window.SWYRL_ENGINE_WORKSPACES.change('game'));
 await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES.active()==='game');
 await openCheck('blank-model',1,1);
 assert(errors.length===0,'Unexpected page exceptions: '+errors.join('; '));
 console.log('SE232_GAME_TO_MODELER_PASS houses, wolf, blank model; Game default preserved');
 await context.close();
}finally{await browser.close();}
