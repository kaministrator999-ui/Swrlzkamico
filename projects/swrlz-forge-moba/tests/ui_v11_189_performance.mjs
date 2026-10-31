// §E v11.189: settings, draw-call diagnostics and invalidated-resize smoke.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist=process.env.SE189_DIST||'/tmp/se189-package';
assert.equal(fs.readFileSync(path.join(dist,'index.html')).compare(fs.readFileSync(path.join(dist,'modeler.html'))),0);
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'
]});
try{
 for(const [name,width,height,mobile] of [['android',390,844,true],['quest',980,680,false]]){
  const ctx=await browser.newContext({viewport:{width,height},isMobile:mobile,hasTouch:mobile,ignoreHTTPSErrors:true});
  const page=await ctx.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.route('**/*',route=>{
   const url=new URL(route.request().url());
   if(url.origin===host){
    const rel=url.pathname==='/'?'index.html':url.pathname.replace(/^\/+/,'');
    const target=path.resolve(dist,rel);
    if(target===dist||!target.startsWith(dist+'/')||!fs.existsSync(target)){
     void route.fulfill({status:404,body:'Focused test asset missing'});return;
    }
    void route.fulfill({status:200,path:target,contentType:rel.endsWith('.html')?'text/html':undefined});return;
   }
   if(url.hostname==='cdn.jsdelivr.net'){void route.continue();return;}
   void route.abort();
  });
  await page.goto(host+'/index.html',{waitUntil:'load',timeout:120000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_PERFORMANCE_V11189?.snapshot()?.frames>=8
    &&window.SWYRL_ENGINE_WORKSPACES?.active()==='game',null,{timeout:70000});
  await page.evaluate(()=>document.querySelector('#seReleaseNotesDialog[open]')?.close());
  const initial=await page.evaluate(()=>({
    profiler:window.SWYRL_ENGINE_PERFORMANCE_V11189.snapshot(),
    option:!!document.querySelector('#perfPreset option[value="mobile"]'),
    action:!!document.getElementById('se189MobileBoost'),
    title:document.title,route:location.pathname
  }));
  assert.equal(initial.option,true,'mobile preset missing');
  assert.equal(initial.action,true,'mobile boost action missing');
  assert.equal(initial.route,'/index.html');
  assert.equal(initial.profiler.preset,'auto','fresh account graphics mode should remain Auto');
  await page.waitForTimeout(1200);
  const sampled=await page.evaluate(()=>window.SWYRL_ENGINE_PERFORMANCE_V11189.snapshot());
  assert(sampled.frames>initial.profiler.frames,'frame statistics did not advance');
  console.log('SE189_RESIZE_DIAGNOSTICS',name,JSON.stringify({before:initial.profiler,after:sampled}));
  assert(sampled.viewportSizeChecks-initial.profiler.viewportSizeChecks<=8,
    'viewport DOM measurements exceeded the 180ms invalidation guard in 1.2s');
  assert(sampled.draws>0,'native scene should submit GPU draw calls');
  assert(sampled.triangles>0,'native scene should contain actual drawable triangles');
  await page.evaluate(()=>window.SWYRL_ENGINE_PERFORMANCE_V11189.mobileBoost());
  const boosted=await page.evaluate(()=>({
   profiler:window.SWYRL_ENGINE_PERFORMANCE_V11189.snapshot(),
   pixelRatio:renderer.getPixelRatio(),
   saved:JSON.parse(localStorage.getItem('swyrl.engine.performance.v1'))
  }));
  assert.equal(boosted.profiler.preset,'mobile');
  assert.equal(boosted.profiler.renderScale,.62);
  assert.equal(boosted.profiler.shadows,false);
  assert.equal(boosted.saved.preset,'mobile');
  assert(boosted.pixelRatio<=1.25,'mobile pixel ratio too high');
  await page.reload({waitUntil:'load',timeout:120000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_PERFORMANCE_V11189?.snapshot()?.frames>5,null,{timeout:70000});
  const after=await page.evaluate(()=>window.SWYRL_ENGINE_PERFORMANCE_V11189.snapshot());
  assert.equal(after.preset,'mobile','explicit boost graphics choice was not retained');
  assert.equal(after.shadows,false);
  await page.evaluate(()=>document.querySelector('#seReleaseNotesDialog[open]')?.close());
  await page.locator('.se187-game-tabs [data-se187-tab="modeler"]').click({timeout:15000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES?.active()==='modeler',null,{timeout:20000});
  await page.locator('#modelAtelierPanel .se187-model-tabs [data-se187-tab="game"]').click({timeout:15000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES?.active()==='game',null,{timeout:20000});
  assert.equal(errors.length,0,'new browser errors: '+JSON.stringify(errors.slice(-4)));
  console.log('SE189_PERFORMANCE_BROWSER_PASS',name,JSON.stringify({initial:initial.profiler,sampled,boosted,after}));
  await ctx.close();
 }
}finally{await browser.close()}
