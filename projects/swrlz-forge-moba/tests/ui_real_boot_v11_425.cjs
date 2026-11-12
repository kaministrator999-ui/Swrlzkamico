'use strict';
/* Actual Chromium + mobile-size viewport acceptance test. No mocked
 * observers, no skipped default scene, and no disabled editor frame loop.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('playwright');
const ROOT=process.env.SE425_DIST||'/tmp/se425-acceptance';
let complete=false;
setTimeout(()=>{if(!complete){console.error('SE425_BOOT_TIMEOUT: browser never settled');process.exit(3);}},45000);
(async()=>{
 const browser=await chromium.launch({headless:true,args:[
  '--no-sandbox','--enable-unsafe-swiftshader','--disable-dev-shm-usage'
 ]});
 const page=await browser.newPage({viewport:{width:390,height:820},isMobile:true,hasTouch:true});
 const errors=[];
 page.on('pageerror',err=>{errors.push(err.message);console.log('SE425_BROWSER_ERROR',err.message);});
 page.on('requestfailed',req=>{const url=req.url();if(!url.includes('google')&&!url.includes('analytics'))errors.push('Failed request '+url);});
 await page.route('https://kamiloki-swrlz-forge-moba.hf.space/**',route=>{
  const u=new URL(route.request().url());
  const relative=decodeURIComponent(u.pathname).replace(/^\//,'')||'index.html';
  const target=path.resolve(ROOT,relative);
  if(!target.startsWith(path.resolve(ROOT)+path.sep)||!fs.existsSync(target))
   return route.fulfill({status:404,body:'Not found'});
  const type={'.html':'text/html','.js':'text/javascript','.css':'text/css',
   '.json':'application/json','.png':'image/png','.webp':'image/webp'}[path.extname(target)]||'application/octet-stream';
  return route.fulfill({status:200,contentType:type,body:fs.readFileSync(target)});
 });
 await page.goto('https://kamiloki-swrlz-forge-moba.hf.space/index.html',{waitUntil:'commit',timeout:18000});
 await page.waitForTimeout(4200);
 const get=()=>page.evaluate(()=>{
  const levels=window.SWYRL_ENGINE_LEVELS?.status?.();
  const hub=document.querySelector('#projectHub');
  const bars=document.querySelectorAll('#st141LevelBar');
  return {
   version:window.SWRLZ_FORGE_BUILD?.version,
   ready:document.documentElement.classList.contains('se127-editor-ready'),
   splash:document.querySelector('#se185BootStage')?.textContent||'',
   actors:document.querySelector('footer')?.textContent?.match(/(\d+)\s+(?:objects|actors)/)?.[1]||'',
   footer:document.querySelector('footer')?.innerText.slice(0,260)||'',
   tabs:[...hub?.querySelectorAll('.se170-hub-tabs button[role=tab]')||[]].map(n=>n.textContent.trim()),
   categories:[...hub?.querySelectorAll('#se236StarterGroups button')||[]].map(n=>n.textContent.trim()),
   levelBarAttached:bars.length===1&&bars[0].isConnected,
   levelBarVisible:bars.length===1&&!bars[0].hidden,
   levelBarCount:bars.length,levels,
   preview:window.SWYRL_ENGINE_LEVEL_UI_RECOVERY_423?.inspect?.(),
   hubOpen:!!hub?.classList.contains('show'),
   modalScroll:hub?.querySelector('.project-window')?.style?.overflowY||''
  };
 });
 const bounded=(p,label)=>Promise.race([p,new Promise((_,rej)=>setTimeout(()=>rej(Error(label+' blocked')),8500))]);
 const snap=await bounded(get(),'startup snapshot');
 console.log('SE425_FULL_BOOT',JSON.stringify(snap));
 assert.equal(snap.version,'v11.425');
 assert.equal(snap.ready,true,'native boot gate must finish, not remain synchronizing');
 for(const tab of ['Starter Projects','My Projects','Tutorials'])
  assert.ok(snap.tabs.includes(tab),'missing '+tab);
 assert.ok((snap.levels?.levels||0)>=1,'authored editor level must be hydrated');
 assert.ok(snap.levels?.owned,'current scene owns its level package');
 assert.ok(snap.levelBarAttached&&snap.levelBarVisible,'native level selector must be visible');
 assert.ok(snap.footer.includes('170 parts'),'authored 170-part Dragon Den must be populated');
 await bounded(page.locator('#projectBtn').click({timeout:6000,force:true}),'Projects open');
 await page.waitForTimeout(250);
 const open=await bounded(page.evaluate(()=>{
  const hub=document.querySelector('#projectHub');
  const win=hub.querySelector('.project-window');
  return {visible:hub.classList.contains('show'),
   scrollStyle:getComputedStyle(win).overflowY,
   starterTab:hub.querySelector('#se170-tab-starter')?.textContent.trim(),
   mineTab:hub.querySelector('#se170-tab-mine')?.textContent.trim(),
   tutorialTab:hub.querySelector('#se412Tab')?.textContent.trim()};
 }),'Projects open snapshot');
 console.log('SE425_PROJECTS_OPEN',JSON.stringify(open));
 assert.equal(open.visible,true);
 assert.equal(open.scrollStyle,'auto','Projects window must permit vertical scroll');
 assert.equal(open.starterTab,'Starter Projects');
 assert.equal(open.mineTab,'My Projects');
 assert.equal(open.tutorialTab,'Tutorials');
 await bounded(page.locator('#se412Tab').click({timeout:5000,force:true}),'Tutorials click');
 assert.equal(await page.locator('#se412Tutorials').isVisible(),true,'Tutorial pane is actually selectable');
 await bounded(page.locator('#se170-tab-mine').click({timeout:5000,force:true}),'My Projects click');
 assert.equal(await page.locator('#se170-pane-mine').isVisible(),true,'My Projects pane is actually selectable');
 assert.equal(errors.filter(x=>/ReferenceError|TypeError|SyntaxError/.test(x)).length,0,'no JavaScript startup exceptions');
 complete=true;
 console.log('SE425_REAL_CHROMIUM_STARTUP_PASS: 170-part scene, level selector, 3 native Projects tabs, vertical scroll and working selections');
 await Promise.race([browser.close(),new Promise(r=>setTimeout(r,1800))]);process.exit(0);
})().catch(error=>{console.error('SE425_ACCEPTANCE_FAILED',error.stack||String(error));process.exit(1)});
