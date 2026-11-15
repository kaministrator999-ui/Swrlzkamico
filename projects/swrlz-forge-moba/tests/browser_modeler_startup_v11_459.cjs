'use strict';
// Real-headless mobile startup smoke: the editor must leave scene/tool sync.
// Run from repo root with playwright installed and /tmp/se459-browser built.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path');
const root='/tmp/se459-browser';
const browserHost='https://kamiloki-swrlz-forge-moba.hf.space';
const deadline=setTimeout(()=>{console.error('SE459_BROWSER_HARD_TIMEOUT');process.exit(9)},75000);
(async()=>{
 const browser=await chromium.launch({headless:true,
  args:['--no-sandbox','--enable-unsafe-swiftshader','--disable-web-security']});
 const page=await browser.newPage({viewport:{width:412,height:915},isMobile:true,hasTouch:true,deviceScaleFactor:2});
 const errors=[],failed=[];
 page.on('pageerror',e=>{errors.push(String(e.stack||e));console.log('SE459_BROWSER_PAGEERROR '+String(e.stack||e).slice(0,1100))});
 page.on('requestfailed',r=>failed.push({url:r.url(),reason:r.failure()?.errorText}));
 page.on('console',m=>{if(m.type()==='error')console.log('SE459_BROWSER_CONSOLE_ERROR '+m.text().slice(0,350))});
 await page.route(browserHost+'/**',async route=>{
  const u=new URL(route.request().url());
  const name=decodeURIComponent(u.pathname).replace(/^\/+/,'')||'index.html';
  const target=path.resolve(root,name);
  if(!target.startsWith(root+path.sep)||!fs.existsSync(target)||!fs.statSync(target).isFile()){
   return route.fulfill({status:404,body:'Not found'});
  }
  const b=fs.readFileSync(target);
  const ext=path.extname(target).toLowerCase();
  const type={'.html':'text/html','.js':'text/javascript','.css':'text/css',
   '.json':'application/json','.png':'image/png','.jpg':'image/jpeg',
   '.webp':'image/webp','.glb':'model/gltf-binary'}[ext]||'application/octet-stream';
  return route.fulfill({status:200,body:b,contentType:type});
 });
 await page.goto(browserHost+'/modeler.html',{waitUntil:'domcontentloaded',timeout:35000});
 await page.waitForTimeout(9500);
 const result=await page.evaluate(()=>{
  const p=document.querySelector('#modelAtelierPanel');
  const bodyText=(document.body?.innerText||'').slice(0,1300);
  const status=[...document.querySelectorAll('[role="status"],.statusbar,.loading,.loading-status')]
   .filter(x=>{const css=getComputedStyle(x);return x.getBoundingClientRect().height>0&&
     css.display!=='none'&&css.visibility!=='hidden'&&Number(css.opacity)>.1;})
   .map(x=>x.textContent.trim().slice(0,180)).slice(0,15);
  return {documentReady:document.readyState,
   version:window.SWRLZ_FORGE_BUILD?.version||null,
   editorReady:document.documentElement.classList.contains('se127-editor-ready'),
   splashVisibility:getComputedStyle(document.getElementById('se185Init')).visibility,
   panelPresent:!!p,panelVisible:!!p&&!p.hidden,
   hasViewport:!!p?.querySelector('canvas'),
   toolRail:!!p?.querySelector('#modelAtelierToolRail'),
   topText:bodyText,visibleStatuses:status,
   helper:window.SWYRL_ENGINE_MODEL_VIEW_STABILITY_458?.inspect?.()||null};
 });
 console.log('SE459_BROWSER_RESULT '+JSON.stringify(result));
 console.log('SE459_BROWSER_REQUESTS_FAILED '+JSON.stringify(failed.slice(0,16)));
 console.log('SE459_BROWSER_ERRORS '+JSON.stringify(errors.slice(0,12)));
 await browser.close();clearTimeout(deadline);
 const fatal=errors.filter(e=>/ReferenceError|SyntaxError|TypeError|atelierViewModeApply|se458|se459/i.test(e));
 if(fatal.length)throw Error('Native script/runtime exception in actual browser: '+fatal.slice(0,3).join('; '));
 if(result.version!=='v11.459')throw Error('Engine build version never initialized in browser');
 if(!result.editorReady||result.splashVisibility!=='hidden')
  throw Error('Initial loading screen is actually displayed over the editor');
 if(!result.panelPresent||!result.toolRail)throw Error('Model Studio tool rail did not initialize');
 if(!result.hasViewport)throw Error('Model Studio canvas did not initialize');
 if(/Synchronizing scene and tools|Startup is taking longer than expected/i.test(result.visibleStatuses.join(' ')))
  throw Error('Scene/tools startup warning still visible after initialization');
 console.log('SE459_REAL_BROWSER_BOOT_PASS: v11.459 page and Model Studio canvas/tool rail initialized without fatal script errors');
 process.exit(0);
})().catch(e=>{clearTimeout(deadline);console.error('SE459_REAL_BROWSER_BOOT_FAIL '+(e.stack||e));process.exit(1)});
