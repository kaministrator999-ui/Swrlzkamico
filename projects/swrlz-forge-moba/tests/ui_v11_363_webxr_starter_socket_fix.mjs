// Targeted four-card mobile browser smoke: actual Projects → Starter Models clicks.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const base='/tmp/se363-model-starters';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'
]});
const errors=[];
try{
 const context=await browser.newContext({viewport:{width:390,height:844},
  isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 await context.route('**/*',route=>{
  const url=new URL(route.request().url());
  if(url.origin===host){
   const rel=url.pathname==='/'?'index.html':url.pathname.replace(/^\/+/, '');
   const full=path.resolve(base,rel);
   if(!full.startsWith(base+'/')||!fs.existsSync(full))
    return route.fulfill({status:404,body:'Missing package test asset: '+rel});
   const contentType=rel.endsWith('.html')?'text/html':
     rel.endsWith('.json')?'application/json':undefined;
   return route.fulfill({status:200,path:full,contentType});
  }
  if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'].includes(url.hostname))
   return route.continue();
  return route.abort();
 });
 const page=await context.newPage();
 page.on('pageerror',e=>{errors.push(String(e));console.log('SE363_PAGE_ERROR',String(e).slice(0,500))});
 page.on('dialog',dialog=>{
  console.log('SE363_NATIVE_DIALOG',dialog.type(),dialog.message().slice(0,160));
  void dialog.accept();
 });
 page.on('console',entry=>{
  if(entry.type()==='error'||entry.text().includes('Could not open'))
   console.log('SE363_CONSOLE',entry.type(),entry.text().slice(0,500));
 });

 await page.goto(host+'/index.html',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_WEBXR_MODEL_STARTERS_361?.status?.()?.templates?.length===4,
   null,{timeout:45000});
 // Fresh §E releases intentionally show the native What's New modal.
 // Dismiss it via the real Continue button before interacting with Projects.
 const updates=page.locator('#seReleaseNotesDialog[open]');
 if(await updates.count())await page.locator('#seReleaseNotesClose').click();

 for(const [id,count] of [['webxr-hand-left',1],['webxr-hand-right',1],['webxr-touch-left',7],['webxr-touch-right',7]]){
  await page.evaluate(()=>{
   const hub=document.getElementById('projectHub');if(!hub)throw Error('Project hub absent');
   hub.classList.add('show');
   const models=document.getElementById('se236StarterTab-models');
   if(!models)throw Error('Starter Models tab missing');
   models.click();
  });
  const card=page.locator('#se236StarterModels button[data-project-template="'+id+'"]');
  await card.waitFor({state:'visible',timeout:12000});
  await card.click({timeout:15000});
  try{
    await page.waitForFunction(target=>{
     const editor=window.SWYRL_ENGINE_MODEL_ATELIER?.status?.();
     const ws=window.SWYRL_ENGINE_WORKSPACES?.inspect?.();
     const load=window.SWYRL_ENGINE_WEBXR_MODEL_STARTERS_361?.status?.();
     return load&&!load.busy&&editor?.open===true&&editor.count===target&&
       ws?.active==='modeler'&&ws?.projectKind==='model-atelier';
    },count,{timeout:35000});
  }catch(error){
   console.log('SE363_OPEN_DIAG',id,JSON.stringify(await page.evaluate(()=>({
    busy:window.SWYRL_ENGINE_WEBXR_MODEL_STARTERS_361?.status?.(),
    workspace:window.SWYRL_ENGINE_WORKSPACES?.inspect?.(),
    editor:window.SWYRL_ENGINE_MODEL_ATELIER?.status?.(),
    notesOpen:document.getElementById('seReleaseNotesDialog')?.open,
    projectHubOpen:document.getElementById('projectHub')?.classList.contains('show'),
    status:document.getElementById('modelAtelierStatus')?.textContent
   }))));
   throw error;
  }
  const info=await page.evaluate(()=>({
   workspace:window.SWYRL_ENGINE_WORKSPACES.inspect().active,
   editor:window.SWYRL_ENGINE_MODEL_ATELIER.status(),
   canvas:document.querySelector('#modelAtelierViewport canvas')?.getBoundingClientRect()?.toJSON(),
   parts:document.querySelectorAll('#modelAtelierParts option').length,
   modal:document.getElementById('projectHub')?.classList.contains('show')
  }));
  console.log('SE363_CARD_OPEN',id,JSON.stringify(info));
  assert.equal(info.editor.count,count);
  assert.equal(info.parts,count);
  assert(info.canvas?.width>80 && info.canvas?.height>120,'native Model Studio viewport not displayed');
  assert.equal(info.modal,false);
 }
 assert.deepEqual(errors,[],'No unexpected page exceptions');
 console.log('SE363_FOUR_MODEL_STARTER_CLICKS_PASS');
 await context.close();
}finally{await browser.close();}
