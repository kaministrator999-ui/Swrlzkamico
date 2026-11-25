'use strict';
// Exercise the actual delivered module in Chromium, not a standalone syntax check.
// Candidate uses the real production origin with packaged files routed locally.
// Public mode uses the real HF deployment with no response substitution.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('playwright');
const origin='https://kamiloki-swrlz-forge-moba.static.hf.space';
const root=path.resolve(process.argv[2]||'dist/swrlz-forge-moba');
const live=process.argv.includes('--live');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml','.glb':'model/gltf-binary'};
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});
 try{
  const page=await browser.newPage({viewport:{width:412,height:915},isMobile:true,hasTouch:true,deviceScaleFactor:2});
  const errors=[];
  page.on('pageerror',e=>{errors.push(String(e.stack||e));console.log('BROWSER_PAGEERROR',String(e.stack||e).slice(0,1200));});
  if(!live)await page.route(origin+'/**',async route=>{
   const name=decodeURIComponent(new URL(route.request().url()).pathname).replace(/^\/+/,'')||'index.html';
   const file=path.resolve(root,name);
   if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile())return route.fulfill({status:404,body:'Not found'});
   return route.fulfill({status:200,body:fs.readFileSync(file),contentType:mime[path.extname(file)]||'application/octet-stream'});
  });
  await page.goto(origin+'/modeler.html?bootcheck='+Date.now(),{waitUntil:'domcontentloaded',timeout:90000});
  await page.waitForFunction(()=>!!window.SWRLZ_FORGE_BUILD?.version &&
    !!window.SWYRL_ENGINE_UV_UNWRAP && !!window.SWYRL_ENGINE_STARTUP_476?.inspect?.()?.ready &&
    !!document.getElementById('seChatFrame')?.getAttribute('src'),null,{timeout:90000});
  assert.equal(errors.filter(x=>/se552Open|se555|ReferenceError|SyntaxError/.test(x)).length,0,errors.join('\n'));
  const info=await page.evaluate(()=>({version:window.SWRLZ_FORGE_BUILD.version,
   startup:window.SWYRL_ENGINE_STARTUP_476.inspect(),bridge:!!window.SWYRL_ENGINE_STARTUP_ACCOUNT_476,
   frame:document.getElementById('seChatFrame').src,uv:window.SWYRL_ENGINE_UV_UNWRAP.status(),
   signalLost:!document.getElementById('se476SignalLost').hidden}));
  assert(info.bridge&&info.frame.startsWith('https://kamiloki-swyrlz.hf.space/'),JSON.stringify(info));
  assert(!info.signalLost,'False outage while account is initializing');
  if(live){
   await page.waitForFunction(()=>window.SWYRL_ENGINE_STARTUP_ACCOUNT_476?.ready?.()===true,null,{timeout:90000});
   const state=await page.evaluate(()=>({ready:window.SWYRL_ENGINE_STARTUP_ACCOUNT_476.ready(),account:window.SWYRL_ENGINE_STARTUP_476.inspect().account}));
   assert(state.ready,'Real cross-origin Chat bridge did not connect');
   console.log('SE555_LIVE_CHAT_BRIDGE_READY',JSON.stringify(state));
  }
  // No account bypass: exercise the existing explicit local-workspace action.
  if(await page.locator('#se476StartupGate').isVisible()){
   await page.locator('#se476ContinueLocal').click({timeout:15000});
  }
  await page.waitForFunction(()=>document.getElementById('se476StartupGate')?.hidden===true &&
    document.documentElement.classList.contains('se127-editor-ready'),null,{timeout:45000});
  assert.equal(errors.filter(x=>/se552Open|se555|ReferenceError|SyntaxError/.test(x)).length,0,errors.join('\n'));
  const opened=await page.evaluate(()=>window.SWYRL_ENGINE_CLEAN_TOPOLOGY.open(true));
  assert.equal(opened,true,'Clean humanoid starter must load');
  await page.locator('#se355UVEditorOpen').click({timeout:20000});
  await page.locator('[data-se551="expand"]').click({timeout:20000});
  await page.locator('#se552UVHost [data-se552-regions]').check({timeout:20000});
  try{
   await page.waitForFunction(()=>window.SWYRL_ENGINE_UV_NUMBERING.inspect().labels>=1,null,{timeout:20000});
  }catch(e){
   console.log('SE556_OVERLAY_STATE',JSON.stringify(await page.evaluate(()=>({state:window.SWYRL_ENGINE_UV_NUMBERING.inspect(),info:document.getElementById('se356UVInfo')?.textContent,host:!!document.getElementById('se552UVHost'),checkbox:document.querySelector('[data-se552-regions]')?.checked}))));
   throw e;
  }
  const labels=await page.evaluate(()=>window.SWYRL_ENGINE_UV_NUMBERING.inspect());
  assert(labels.enabled&&labels.model&&labels.labels>=1,JSON.stringify(labels));
  await page.locator('[data-se556-model]').uncheck();
  await page.waitForFunction(()=>window.SWYRL_ENGINE_UV_NUMBERING.inspect().labels===0);
  await page.locator('[data-se556-model]').check();
  await page.locator('[data-se556-view]').click();
  await page.waitForFunction(()=>!document.getElementById('se552UVHost')&&window.SWYRL_ENGINE_UV_NUMBERING.inspect().labels>=1);
  assert.equal(errors.filter(x=>/ReferenceError|TypeError|SyntaxError/.test(x)).length,0,errors.join('\n'));
  console.log('SE556_NUMBERED_MODEL_UV_BROWSER_PASS',JSON.stringify({live,labels}));
  console.log('SE555_DELIVERED_BROWSER_BOOT_PASS',JSON.stringify({live,info,errors:errors.slice(0,5)}));
 }finally{await browser.close();}
})().catch(e=>{console.error('SE555_DELIVERED_BROWSER_BOOT_FAIL',e.stack||e);process.exitCode=1;});
