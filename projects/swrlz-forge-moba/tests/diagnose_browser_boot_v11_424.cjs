'use strict';
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path');
const root='/tmp/se-browser-boot';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--disable-web-security']});
 const page=await browser.newPage({viewport:{width:390,height:820},isMobile:true,hasTouch:true});
 const errors=[];
 page.on('pageerror',e=>errors.push('PAGE_ERROR '+e.stack));
 page.on('console',m=>{if(m.type()==='error'||m.type()==='warning')errors.push('CONSOLE '+m.type()+' '+m.text());});
 page.on('requestfailed',r=>errors.push('REQUEST '+r.url()+' '+r.failure()?.errorText));
 await page.route('https://kamiloki-swrlz-forge-moba.hf.space/**',async route=>{
  const u=new URL(route.request().url());
  const filepath=path.join(root,decodeURIComponent(u.pathname).replace(/^\//,'')||'index.html');
  if(!filepath.startsWith(root)||!fs.existsSync(filepath)||!fs.statSync(filepath).isFile())return route.fulfill({status:404,body:'Not found'});
  const b=fs.readFileSync(filepath);
  const ext=path.extname(filepath).toLowerCase();
  const c={'.html':'text/html','.json':'application/json','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp'}[ext]||'application/octet-stream';
  return route.fulfill({status:200,body:b,contentType:c});
 });
 await page.goto('https://kamiloki-swrlz-forge-moba.hf.space/index.html',{waitUntil:'domcontentloaded',timeout:120000});
 await page.waitForTimeout(3500);
 const snapshot=()=>page.evaluate(()=>{
  const hub=document.getElementById('projectHub'), win=hub?.querySelector('.project-window');
  let out={origin:location.origin,ready:document.readyState,bodyText:document.body.innerText.slice(0,350),
    version:window.SWRLZ_FORGE_BUILD?.version,tabTexts:[...hub?.querySelectorAll('button[role=tab]')||[]].map(t=>t.textContent),
    hasStarter:!!document.getElementById('se170-tab-starter'),hasMine:!!document.getElementById('se170-tab-mine'),
    hasTutorials:!!document.getElementById('se412Tab'),hasLevelBar:!!document.getElementById('st141LevelBar'),
    levelBarHidden:document.getElementById('st141LevelBar')?.hidden,
    actorCount:document.querySelectorAll('[data-actor-id]').length,
    footer:[...document.querySelectorAll('footer,.statusbar,.editor-status')].map(e=>e.innerText.slice(0,180)).slice(0,4),
    textStart:document.body.innerText.slice(0,900),
    debug:{tutorial:window.SWYRL_ENGINE_TUTORIAL_412?.status?.(), hub422:window.SWYRL_ENGINE_PROJECT_TUTORIAL_HUB_422?.inspect?.(),
           hub423:window.SWYRL_ENGINE_PROJECTS_RECOVERY_423?.inspect?.(),levels:window.SWYRL_ENGINE_LEVELS?.status?.(),levelUI:window.SWYRL_ENGINE_LEVEL_UI_RECOVERY_423?.inspect?.()}};
  return out;
 });
 console.log('SE424_BOOT_BEFORE '+JSON.stringify(await snapshot()));
 const projectBtn=page.locator('#projectBtn');
 if(await projectBtn.count())await projectBtn.click({force:true,timeout:10000}).catch(e=>errors.push('PROJECT CLICK '+e.message));
 await page.waitForTimeout(1200);
 console.log('SE424_BOOT_AFTER_OPEN '+JSON.stringify(await snapshot()));
 console.log('SE424_BOOT_ERRORS '+JSON.stringify(errors.slice(0,45)));
 await browser.close();
})().catch(e=>{console.error('SE424_DIAGNOSTIC_FAILURE',e);process.exitCode=1});
