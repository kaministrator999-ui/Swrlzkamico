import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist='/tmp/se183-browser';
const sizes=[
 ['portrait-390',390,844,true],
 ['portrait-430',430,932,true],
 ['landscape-844',844,390,true],
 ['quest-desktop',980,680,false],
 ['desktop-1280',1280,800,false],
];
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
try{
 for(const [name,width,height,mobile] of sizes){
  const ctx=await browser.newContext({viewport:{width,height},isMobile:mobile,hasTouch:mobile,ignoreHTTPSErrors:true});
  const page=await ctx.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(String(e).slice(0,350)));
  await page.route('**/*',route=>{
   const uri=new URL(route.request().url());
   if(uri.origin===host){
    const rel=uri.pathname==='/'?'index.html':uri.pathname.replace(/^\/+/,'');
    const target=path.resolve(dist,rel);
    if(target===dist||!target.startsWith(dist+'/')||!fs.existsSync(target)){route.fulfill({status:404,body:'Not found'});return}
    route.fulfill({status:200,path:target,contentType:rel.endsWith('.html')?'text/html':undefined});return;
   }
   if(uri.host.includes('cdn.jsdelivr.net')){route.continue();return}
   route.abort();
  });
  await page.goto(host+'/',{waitUntil:'load',timeout:90000});
  await page.waitForFunction(()=>{
    const ready=!!window.SWYRL_ENGINE_UI_AUDIT?.audit&&!!window.SWYRL_ENGINE_PROJECT_LOAD?.read&&!!window.SWYRL_ENGINE_AGENT;
    if(!ready){window.__se183ReadySince=0;return false;}
    if(!window.__se183ReadySince)window.__se183ReadySince=performance.now();
    return performance.now()-window.__se183ReadySince>800;
  },null,{timeout:90000});
  await page.evaluate(()=>document.querySelector('#seReleaseNotesDialog[open]')?.close());
  const audit=await page.evaluate(()=>window.SWYRL_ENGINE_UI_AUDIT.audit());
  assert.equal(audit.issues.length,0,name+' baseline collisions '+JSON.stringify(audit.issues));
  const pill=await page.locator('.engine-stats-pill').first().evaluate(el=>getComputedStyle(el).display).catch(()=>'absent');
  assert.ok(['absent','none'].includes(pill),name+' redundant actor badge covers editor');
  const hub=page.locator('#projectHub');
  await page.evaluate(()=>hub=void 0).catch(()=>{}); // no stored project state
  await page.evaluate(()=>document.getElementById('projectHub')?.classList.add('show'));
  const projectClose=page.locator('#projectClose');
  assert.ok(await projectClose.isVisible(),name+' project modal close missing');
  const closeHit=await projectClose.evaluate(el=>{
   const r=el.getBoundingClientRect(),h=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
   return h===el||el.contains(h);
  });
  assert.ok(closeHit,name+' modal close obscured');
  if(['portrait-390','landscape-844','quest-desktop'].includes(name)){
   const starter=page.locator('#projectHub button[data-project-template="sheep-tag-meadow"]').first();
   await starter.click({timeout:30000});
   await page.waitForFunction(()=>window.SWYRL_ENGINE_PROJECT_LOAD?.read()?.lastOutcome==='success',{timeout:90000}).catch(async error=>{
    const state=await page.evaluate(()=>window.SWYRL_ENGINE_PROJECT_LOAD?.read());
    throw Error(name+' starter did not complete '+JSON.stringify(state)+' / '+error.message);
   });
   const completed=await page.evaluate(()=>window.SWYRL_ENGINE_PROJECT_LOAD.read());
   assert.ok(completed.lastMs>=0);
   const levels=page.locator('#st141LevelBar');
   await levels.waitFor({state:'attached',timeout:30000});
   const toggle=page.locator('#se183LevelsToggle');
   await toggle.waitFor({state:'attached'});
   const mode=await page.evaluate(()=>{
    const b=document.getElementById('st141LevelBar');
    return {hidden:b.hidden,barHeight:b.getBoundingClientRect().height,
      expanded:b.classList.contains('se183-expanded'),
      rawControls:b.querySelector('#st141NewLevel')!==null};
   });
   assert.ok(mode.rawControls,name+' level actions missing');
   assert.equal(mode.expanded,false,name+' Levels starts expanded and cramped');
   if(!mode.hidden){
    await toggle.click({timeout:15000});
    assert.equal(await toggle.getAttribute('aria-expanded'),'true');
    assert.ok(await page.locator('#st141NewLevel').isVisible());
    assert.ok(await page.locator('#st141Export').isVisible());
    await toggle.click({timeout:15000});
    assert.equal(await toggle.getAttribute('aria-expanded'),'false');
   }
   console.log('SE183_PROJECT_OPEN',JSON.stringify({name,mode,completed}));
  }else await page.evaluate(()=>document.getElementById('projectHub')?.classList.remove('show'));
  const now=await page.evaluate(()=>window.SWYRL_ENGINE_UI_AUDIT.audit());
  assert.equal(now.issues.length,0,name+' after starter '+JSON.stringify(now.issues));
  assert.equal(errors.length,0,name+' page errors '+errors.join(' | '));
  console.log('SE183_BROWSER_CASE_PASS',name,'load',await page.evaluate(()=>window.SWYRL_ENGINE_PROJECT_LOAD.read()));
  await ctx.close();
 }
 console.log('SE183_BROWSER_LAYOUT_PASS',sizes.length);
}finally{await browser.close()}
