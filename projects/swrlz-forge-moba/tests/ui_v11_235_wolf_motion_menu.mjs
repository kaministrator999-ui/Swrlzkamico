// One Android-size native menu regression; no gameplay, browser matrix or VR emulation.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const base='/tmp/se235-wolf-menu';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
try{
 const ctx=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 await ctx.route('**/*',route=>{
  const url=new URL(route.request().url());
  if(url.origin===host){
   const rel=url.pathname==='/'?'index.html':url.pathname.replace(/^\/+/,'');
   const file=path.resolve(base,rel);
   if(file===base||!file.startsWith(base+'/')||!fs.existsSync(file))return route.fulfill({status:404,body:'not bundled'});
   return route.fulfill({status:200,path:file,contentType:rel.endsWith('.html')?'text/html':undefined});
  }
  if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'].includes(url.hostname))return route.continue();
  return route.abort();
 });
 const page=await ctx.newPage();const errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(host+'/index.html',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>typeof window.SWYRL_ENGINE_MODEL_ATELIER?.loadAnimal==='function',null,{timeout:35000});
 await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.loadAnimal('wolf',{force:true}));
 await page.waitForFunction(()=>window.SWYRL_ENGINE_WOLF_RIG?.status?.().skinned &&
  window.SWYRL_ENGINE_WORKSPACES?.active?.()==='modeler',null,{timeout:40000});
 const dialog=page.locator('#seReleaseNotesDialog');if(await dialog.count())await dialog.evaluate(el=>{if(el.open)el.close()});
 // This reproduces pressing the same bottom "Motion" button shown in owner's screenshot.
 await page.evaluate(()=>{
  const panel=document.getElementById('modelAtelierPanel');
  const rail=panel.querySelector('#modelAtelierToolRail');
  const button=[...rail.querySelectorAll('button')].find(el=>el.textContent.trim()==='Motion');
  if(!button)throw Error('Native Motion category missing from tool rail');
  button.click();
 });
 const state=await page.evaluate(()=>{
  const panel=document.getElementById('modelAtelierPanel');
  const wolf=panel.querySelector('#modelAtelierWolfStudio');
  const insp=panel.querySelector('.atelier-inspector');
  const ids=['modelAtelierWolfClip','modelAtelierWolfPlay','modelAtelierWolfTime',
    'modelAtelierWolfBone','modelAtelierWolfSaveKey'];
  const status=id=>{const e=document.getElementById(id),style=e&&getComputedStyle(e),rect=e?.getBoundingClientRect();return {id,found:!!e,visible:!!e&&style.display!=='none'&&rect.width>0&&rect.height>0,rect:rect?.toJSON()};};
  return {version:window.SWRLZ_FORGE_BUILD.version,
   active:window.SWYRL_ENGINE_WORKSPACES.active(),
   className:panel.className,
   wolfOpen:wolf?.open,wolfHidden:wolf?.hidden,wolfDisplay:wolf&&getComputedStyle(wolf).display,
   inspectorVisible:insp&&getComputedStyle(insp).display,
   controls:ids.map(status),railSelected:window.SWYRL_E_UNIFIED_TOOLS?.current?.()};
 });
 console.log('SE235_WOLF_MOTION_MENU',JSON.stringify(state));
 assert.equal(state.active,'modeler');
 assert.equal(state.wolfOpen,true);
 assert.equal(state.wolfHidden,false);
 assert(state.className.includes('se-wolf-motion-focus'));
 assert(state.controls.every(c=>c.visible),'The complete Play/clip/key controls must be visible after tapping Motion');
 await page.evaluate(()=>{document.getElementById('modelAtelierWolfPlay').click()});
 await page.waitForTimeout(260);
 const playing=await page.evaluate(()=>window.SWYRL_ENGINE_WOLF_RIG.status().playing);
 console.log('SE235_WOLF_MOTION_PLAY_ENABLED',playing);
 assert.equal(playing,true);
 await page.evaluate(()=>{const el=document.getElementById('modelAtelierWolfPlay');el.click()});
 await page.evaluate(()=>{
  const rail=document.getElementById('modelAtelierToolRail');
  [...rail.querySelectorAll('button')].find(e=>e.textContent.trim()==='More')?.click();
 });
 const restored=await page.evaluate(()=>!document.getElementById('modelAtelierPanel').classList.contains('se-wolf-motion-focus'));
 assert(restored,'More should restore the usual inspector');
 console.log('SE235_WOLF_MOTION_MENU_PASS');
 assert.deepEqual(errors,[]);
 await ctx.close();
}finally{await browser.close()}
