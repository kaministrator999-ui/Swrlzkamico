import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist='/tmp/swrlz-hand-ui';
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
try{
 const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 const page=await context.newPage();
 const errors=[],logs=[];
 page.on('pageerror',e=>{errors.push(String(e));console.log('HAND_PAGE_ERROR',String(e));});
 page.on('console',m=>{if(m.type()==='error'){logs.push(m.text());console.log('HAND_CONSOLE_ERROR',m.text().slice(0,1500));}});
 page.on('requestfailed',r=>console.log('HAND_REQUEST_FAILED',r.url(),r.failure()?.errorText));
 await page.route('**/*',route=>{
  const url=new URL(route.request().url());
  if(url.origin===host){
   const rel=url.pathname==='/'?'index.html':url.pathname.replace(/^\/+/, '');
   const target=path.resolve(dist,rel);
   if(target===dist||!target.startsWith(dist+'/')||!fs.existsSync(target)){
    route.fulfill({status:404,body:'not found'});return;
   }
   route.fulfill({status:200,path:target,contentType:rel.endsWith('.html')?'text/html':undefined});return;
  }
  if(url.host.includes('cdn.jsdelivr.net')||url.host.includes('cdnjs.cloudflare.com')||url.host.includes('unpkg.com')){
   route.continue();return;
  }
  route.abort();
 });
 await page.goto(host+'/modeler.html?project=floating-hand-glove',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForTimeout(12000);
 const snap=await page.evaluate(()=>{
   const modal=document.getElementById('modelAtelierPanel');
   const hub=document.getElementById('projectHub');
   return {
     route:location.href,hand:!!window.SWYRL_ENGINE_FLOATING_HAND,boot:!!window.SWRLZ_FORGE_BUILD,
     bridge:!!window.SWYRL_ENGINE_HAND_SURFACE,modeler:!!window.SWYRL_ENGINE_MODEL_ATELIER,
     handStatus:window.SWYRL_ENGINE_FLOATING_HAND?.status?.(),
     modelStatus:window.SWYRL_ENGINE_MODEL_ATELIER?.status?.(),
     panelPresent:!!modal,panelHidden:modal?.hidden,panelText:modal?.textContent?.slice(0,200),
     cards:document.querySelectorAll('[data-project-template="floating-hand-glove"]').length,
     checkedCards:document.querySelectorAll('input[data-se128-default]:checked').length,
     hubShow:hub?.classList.contains('show'),
     mainBody:document.body?.innerText?.slice(0,600),
     scripts:document.scripts.length
   };
 });
 console.log('HAND_SNAPSHOT',JSON.stringify(snap));
 assert.equal(snap.hand,true,'Hand starter API missing');
 assert.equal(snap.bridge,true,'organic mesh helper bridge missing');
 assert.equal(snap.modelStatus?.active,true,'hand native project did not load');
 assert.equal(snap.panelHidden,false,'modeler panel not open');
 assert(snap.modelStatus.count>10,'not enough native hand parts');
 assert.equal(errors.length,0,'Uncaught page errors');
 await context.close();
}finally{await browser.close();}
