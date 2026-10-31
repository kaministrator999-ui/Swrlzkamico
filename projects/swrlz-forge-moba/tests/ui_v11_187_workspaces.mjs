// §E v11.187: direct Modeler route, empty draft, native tab switching without reload.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist=process.env.SE187_DIST||'/tmp/se187-package';
const index=fs.readFileSync(path.join(dist,'index.html'));
const modeler=fs.readFileSync(path.join(dist,'modeler.html'));
assert.equal(index.compare(modeler),0,'Modeler and Game must ship identical verified native runtime');
const cases=[['android',390,844,true],['quest',980,680,false]];
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'
]});
try{
 for(const [name,width,height,mobile] of cases){
  const ctx=await browser.newContext({viewport:{width,height},isMobile:mobile,hasTouch:mobile,ignoreHTTPSErrors:true});
  const page=await ctx.newPage();
  const errors=[];
  page.on('pageerror',e=>{errors.push(String(e));console.log('SE187_PAGE_ERROR',name,String(e).slice(0,500));});
  await page.route('**/*',route=>{
   const url=new URL(route.request().url());
   if(url.origin===host){
    const rel=url.pathname==='/'?'index.html':url.pathname.replace(/^\/+/,'');
    const target=path.resolve(dist,rel);
    if(target===dist||!target.startsWith(dist+'/')||!fs.existsSync(target)){
     void route.fulfill({status:404,body:'Missing local test asset'});return;
    }
    void route.fulfill({status:200,path:target,contentType:rel.endsWith('.html')?'text/html':undefined});return;
   }
   if(url.hostname==='cdn.jsdelivr.net'){void route.continue();return;}
   void route.abort();
  });
  await page.goto(host+'/modeler.html',{waitUntil:'load',timeout:120000});
  try{
   await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES?.active()==='modeler'&&
     document.getElementById('modelAtelierPanel')?.hidden===false&&
     window.SWYRL_ENGINE_MODEL_ATELIER?.status()?.open===true,null,{timeout:65000});
  }catch(e){
   console.log('SE187_BOOT_DEBUG',name,JSON.stringify(await page.evaluate(()=>({
    title:document.title,build:window.SWRLZ_FORGE_BUILD?.version,
    workspaces:window.SWYRL_ENGINE_WORKSPACES?.inspect(),
    native:window.SWYRL_ENGINE_MODEL_ATELIER?.status(),
    active:document.querySelector('#modelAtelierPanel')?.hidden,
    splash:document.querySelector('#se185BootStage')?.textContent
   }))),errors.slice(-10));
   throw e;
  }
  await page.evaluate(()=>document.querySelector('#seReleaseNotesDialog[open]')?.close());
  assert.equal(new URL(page.url()).pathname,'/modeler.html');
  const initial=await page.evaluate(()=>window.SWYRL_ENGINE_WORKSPACES.inspect());
  assert.equal(initial.active,'modeler');
  assert.equal(initial.draftParts,0,'untitled draft should begin empty on a fresh profile');
  assert.ok(initial.projectKind!=='model-atelier','Modeler route should not require a named model project');
  assert.equal(await page.locator('#modelAtelierPanel .se187-model-tabs [data-se187-tab]').count(),2);
  await page.locator('#modelAtelierAdd').click({timeout:15000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES.inspect().draftParts===1,null,{timeout:10000});
  const afterAdd=await page.evaluate(()=>window.SWYRL_ENGINE_WORKSPACES.inspect());
  assert.equal(afterAdd.active,'modeler');
  assert.equal(afterAdd.draftParts,1);
  await page.locator('#modelAtelierPanel .se187-model-tabs [data-se187-tab="game"]').click({timeout:10000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES.active()==='game');
  assert.equal(new URL(page.url()).pathname,'/index.html');
  assert.equal(await page.locator('#modelAtelierPanel').getAttribute('hidden')!==null,true);
  assert.equal(await page.locator('#modelAtelierPanel').isVisible(),false,'Hidden Modeler must not cover the Game Engine workspace');
  console.log('SE187_GAME_NAV_LAYOUT',name,JSON.stringify(await page.evaluate(()=>{
   const e=document.querySelector('.se187-game-tabs [data-se187-tab="modeler"]');
   const list=[];
   for(let n=e;n&&list.length<12;n=n.parentElement){
    const s=getComputedStyle(n),r=n.getBoundingClientRect();
    list.push({tag:n.tagName,id:n.id,cls:String(n.className).slice(0,140),
      display:s.display,visibility:s.visibility,opacity:s.opacity,
      position:s.position,overflow:s.overflow,
      x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)});
   }
   return {route:location.pathname,active:window.SWYRL_ENGINE_WORKSPACES?.active(),
     panel:document.getElementById('modelAtelierPanel')?.hidden,layout:list};
  })));
  await page.locator('.se187-game-tabs [data-se187-tab="modeler"]').click({timeout:10000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES.active()==='modeler'&&
    window.SWYRL_ENGINE_MODEL_ATELIER.status().open);
  assert.equal(new URL(page.url()).pathname,'/modeler.html');
  assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_WORKSPACES.inspect())).draftParts,1);
  await page.waitForTimeout(900);
  await page.reload({waitUntil:'load',timeout:120000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES?.active()==='modeler'&&
    window.SWYRL_ENGINE_MODEL_ATELIER?.status()?.open,null,{timeout:65000});
  assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_WORKSPACES.inspect())).draftParts,1,
   'draft lost on reloading independent Modeler route');
  await page.evaluate(()=>document.querySelector('#seReleaseNotesDialog[open]')?.close());
  page.once('dialog',dialog=>void dialog.accept());
  await page.locator('#modelAtelierPanel .se187-new-model').click({timeout:10000});
  assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_WORKSPACES.inspect())).draftParts,0);
  console.log('SE187_ROUTED_MODELER_PASS',name,{initial,afterAdd,errors:errors.length});
  await ctx.close();
 }
 console.log('SE187_BROWSER_PASS',cases.length);
}finally{await browser.close();}
