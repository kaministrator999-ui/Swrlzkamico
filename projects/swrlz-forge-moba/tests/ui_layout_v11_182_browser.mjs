import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist='/tmp/se182-browser';
const sizes=[['phone-390',390,844,true],['phone-wide',430,932,true],['landscape',844,390,true],['quest-window',980,680,false],['desktop',1280,800,false]];
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
const results=[];let errors=0;
try{
 for(const [name,width,height,mobile] of sizes){
  const context=await browser.newContext({viewport:{width,height},isMobile:mobile,hasTouch:mobile,ignoreHTTPSErrors:true});
  const page=await context.newPage(),pageErrors=[];
  page.on('pageerror',e=>pageErrors.push(String(e).slice(0,280)));
  page.on('framenavigated',frame=>{if(frame===page.mainFrame())console.log('SE182_NAV',name,frame.url());});
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
  await page.goto(host+'/',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction("()=>!!window.SWYRL_ENGINE_UI_AUDIT && !!window.SWYRL_ENGINE_AGENT",{timeout:90000});
  await page.evaluate(()=>document.querySelector('#seReleaseNotesDialog[open]')?.close());
  const quickState=()=>page.evaluate(()=>({url:location.href,hasAudit:!!window.SWYRL_ENGINE_UI_AUDIT,auditType:typeof window.SWYRL_ENGINE_UI_AUDIT?.audit,hasAgent:!!window.SWYRL_ENGINE_AGENT,ready:document.readyState,build:window.SWRLZ_FORGE_BUILD?.version}));
  console.log('SE182_BOOT_STATE',name,JSON.stringify(await quickState()));
  await page.waitForTimeout(250);
  console.log('SE182_SETTLED_STATE',name,JSON.stringify(await quickState()));
  const baseline=await page.evaluate(()=>window.SWYRL_ENGINE_UI_AUDIT.audit());
  const toolbar=baseline.rects.toolbar;
  assert.ok(toolbar?.visible,name+' toolbar missing');
  assert.ok(toolbar.width>width-10&&toolbar.width<=width+3,name+' toolbar out of width');
  assert.equal(baseline.issues.length,0,name+' default overlap '+JSON.stringify(baseline.issues));
  assert.ok(baseline.rects.viewport?.visible,name+' main viewport not visible');
  const bar=await page.locator('.app > .topbar').evaluate(el=>({scrollWidth:el.scrollWidth,clientWidth:el.clientWidth,overflow:getComputedStyle(el).overflowX}));
  assert.ok(bar.scrollWidth>=bar.clientWidth,name+' topbar not scrollable');
  await page.evaluate(()=>document.querySelector('#projectHub').classList.add('show'));
  const project=await page.evaluate(()=>window.SWYRL_ENGINE_UI_AUDIT.audit());
  assert.ok(project.rects.projectWindow?.visible,name+' project modal not visible');
  assert.ok(project.rects.projectWindow.x>=-2&&project.rects.projectWindow.right<=width+2,name+' project dialog side overflow');
  assert.ok(project.rects.projectWindow.y>=-2&&project.rects.projectWindow.bottom<=height+2,name+' project dialog vertical overflow');
  const hit=await page.evaluate(()=>{
   const b=document.getElementById('projectClose'),r=b.getBoundingClientRect();
   const h=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
   return {close:{left:r.left,top:r.top,right:r.right,bottom:r.bottom},
     hitId:h?.id||'',hitTag:h?.tagName||'',targetClickable:b===h||b.contains(h)}
  });
  assert.ok(hit.targetClickable,name+' project close obscured by '+hit.hitId);
  await page.evaluate(()=>document.querySelector('#projectHub').classList.remove('show'));
  if(mobile){
   const a=await page.evaluate(()=>window.SWYRL_ENGINE_UI_AUDIT.audit());
   assert.equal(a.issues.length,0,name+' mobile collision '+JSON.stringify(a.issues));
  }
  const record={name,size:[width,height],toolbar:bar,
   baseline:baseline.issues,projects:project.issues,hit,errors:pageErrors};
  console.log('SE182_BROWSER_LAYOUT',JSON.stringify(record));results.push(record);
  errors+=pageErrors.length;
  await context.close();
 }
 assert.equal(errors,0,'Unexpected JavaScript errors in layout browser');
 console.log('SE182_BROWSER_LAYOUT_PASS',results.length);
}finally{await browser.close()}
