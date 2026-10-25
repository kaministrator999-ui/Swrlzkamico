// §E v11.119 real Chromium mobile viewport: no duplicate sheet,
// mode ribbon controls existing proxies inside native moveable inspector.
// The full 3D application must mount via ?project=model-atelier.
import {chromium} from 'playwright';
import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';
import path from 'node:path';
const server=spawn('python3',['-m','http.server','8765','--bind','127.0.0.1'],
 {cwd:'/tmp/se-v11119-smoke',stdio:'ignore'});
let browser,page;let pageErrors=[];
try{
 for(let n=0;n<40;n++){
  try{const r=await fetch('http://127.0.0.1:8765/');if(r.ok)break;}catch{}
  await new Promise(r=>setTimeout(r,250));
 }
 browser=await chromium.launch({channel:'chrome',headless:true,
  args:['--no-sandbox','--enable-unsafe-swiftshader','--disable-dev-shm-usage']});
 const context=await browser.newContext({viewport:{width:412,height:915},
  isMobile:true,hasTouch:true,deviceScaleFactor:2,ignoreHTTPSErrors:true});
 page=await context.newPage();
 // The test URL can open with an unsaved bootstrap scene. Patch only the
 // in-memory test response so calling the public starter bypasses its confirm
 // gate; no production file or scene is changed.
 await page.route('**/*',async route=>{
  const request=route.request();
  if(!request.isNavigationRequest()||
      !request.url().includes('?project=model-atelier'))return route.continue();
  const response=await route.fetch();
  let body=await response.text();
  const source='loadStarter:()=>loadModelAtelierStarter(),';
  assert.ok(body.includes(source),'cannot find test starter wrapper');
  body=body.replace(source,'loadStarter:()=>loadModelAtelierStarter(true),');
  await route.fulfill({response,body});
 });


 page.on('pageerror',e=>pageErrors.push(String(e).slice(0,250)));
 page.on('dialog',dialog=>dialog.accept());
 page.on('requestfailed',r=>pageErrors.push('request '+r.url().slice(0,100)+' '+r.failure()?.errorText));
 await page.goto('http://127.0.0.1:8765/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:30000});
 await page.waitForFunction(()=>!!window.SWYRL_ENGINE_MODEL_ATELIER?.loadStarter,
   {timeout:20000});
 if(!(await page.locator('#modelAtelierPanel').count())){
  const started=await page.evaluate(()=>{
   window.confirm=()=>true;
   return window.SWYRL_ENGINE_MODEL_ATELIER.loadStarter();
  });
  console.log('SE_V11119_CHROME_STARTER',started);

 }
 await page.waitForSelector('#modelAtelierToolRail button',{timeout:16000});
 const installed=await page.evaluate(()=>({
  version:window.SWRLZ_FORGE_BUILD?.version,
  inspector:!!document.querySelector('.atelier-inspector'),
  modeApi:!!window.SWYRL_E_UNIFIED_TOOLS,
  toolApi:!!window.SWYRL_E_CONTEXT,
  exportMenu:!!document.getElementById('seAtelierExportMenu'),
  cameraMenu:!!document.getElementById('seAtelierViewMenu')
 }));
 assert.equal(installed.version,'v11.119',JSON.stringify(installed));
 assert.ok(installed.modeApi&&installed.toolApi&&installed.exportMenu&&installed.cameraMenu,
  'missing mobile UI install '+JSON.stringify({installed,pageErrors}));
 const category=page.locator('#modelAtelierToolRail button').filter({hasText:/^Sculpt$/});
 await category.click();
 const afterSculpt=await page.evaluate(()=>{
  const inspector=document.querySelector('.atelier-inspector'),
   panel=document.getElementById('modelAtelierPanel'),
   ui=document.getElementById('atelierContextWorkbench'),
   modes=document.getElementById('seAtelierModes');
  const outer=inspector.getBoundingClientRect(),inner=ui.getBoundingClientRect();
  return {
   category:window.SWYRL_E_CONTEXT.current()?.group,
   mobileSheetClass:panel.classList.contains('atelier-mobile-context-mode'),
   nativeHidden:panel.classList.contains('atelier-tools-closed'),
   inspectorDisplay:getComputedStyle(inspector).display,
   modeBarDisplay:getComputedStyle(modes).display,
   contextParent:ui.parentElement===inspector,
   inspectorRect:{top:outer.top,bottom:outer.bottom,left:outer.left,right:outer.right},
   modeRect:{top:inner.top,bottom:inner.bottom,left:inner.left,right:inner.right},
   modes:[...modes.querySelectorAll('button')].map(b=>b.textContent.trim())
  };
 });
 assert.equal(afterSculpt.category,'Sculpt',JSON.stringify(afterSculpt));
 assert.equal(afterSculpt.mobileSheetClass,false);
 assert.equal(afterSculpt.nativeHidden,false);
 assert.equal(afterSculpt.contextParent,true,'former bottom popup still detached');
 assert.equal(afterSculpt.inspectorDisplay,'flex','native movable inspector is not visible');
 assert.notEqual(afterSculpt.modeBarDisplay,'none','missing secondary toolbar');
 assert.ok(afterSculpt.modes.includes('Precision circle cut'));
 assert.ok(afterSculpt.modeRect.top>=afterSculpt.inspectorRect.top-2
   &&afterSculpt.modeRect.bottom<=afterSculpt.inspectorRect.bottom+2,
   'context panel escaped the native inspector '+JSON.stringify(afterSculpt));
 await page.locator('#seAtelierModes button').filter({hasText:/^Precision circle cut$/}).click();
 const cut=await page.evaluate(()=>({
  operation:window.SWYRL_E_CONTEXT.current()?.operation,
  title:document.querySelector('#atelierContextOpName')?.textContent,
  fields:document.querySelector('#atelierContextFields')?.textContent,
  modeLabel:document.querySelector('.se-inspector-mode-label')?.textContent,
  aria:document.querySelector('#seAtelierModes button[aria-pressed=true]')?.textContent
 }));
 assert.equal(cut.operation,'Precision circle cut',JSON.stringify(cut));
 assert.ok(/Radius|Depth|Apply/.test(cut.fields),'cut controls not in inspector '+JSON.stringify(cut));
 assert.match(cut.modeLabel,/Precision circle cut/);
 assert.equal(cut.aria,'Precision circle cut');
 await page.locator('#modelAtelierToolRail button').filter({hasText:/^More$/}).click();
 const more=await page.evaluate(()=>({
  modeDisplay:getComputedStyle(document.getElementById('seAtelierModes')).display,
  fullView:!document.getElementById('modelAtelierPanel').classList.contains('se-inspector-mode-view')
 }));
 assert.equal(more.fullView,true);
 assert.equal(more.modeDisplay,'none');
 await page.locator('#seAtelierExportMenu > summary').click();
 const exports=await page.locator('#seAtelierExportMenu .se-export-options button').allTextContents();
 assert.ok(exports.some(x=>/OBJ/i.test(x)),'OBJ export hidden');
 assert.ok(exports.some(x=>/GLB/i.test(x)),'GLB export hidden');
 assert.ok(exports.some(x=>/PNG/i.test(x)),'PNG export hidden');
 await page.locator('#seAtelierViewMenu > summary').click();
 assert.ok(await page.locator('#seAtelierViewMenu .atelier-top-camera button').count()>3,
   'camera direction buttons missing');
 console.log('SE_V11119_MOBILE_CHROME_SINGLE_INSPECTOR_MODES_EXPORT_VIEWS_PASS',JSON.stringify({
   installed,afterSculpt:{category:afterSculpt.category,modes:afterSculpt.modes.length},
   cut:{operation:cut.operation,title:cut.title},exportButtons:exports.length,pageErrors
 }));
 await context.close();
}catch(e){
 let diagnostic=null;
 try{diagnostic=await page?.evaluate(()=>({url:location.href,title:document.title,
  readyState:document.readyState,bodyLength:document.body?.innerHTML?.length,
  sourceBuild:window.SWRLZ_FORGE_BUILD?.version,
  modelApi:!!window.SWYRL_ENGINE_MODEL_ATELIER,
  panelExists:!!document.getElementById('modelAtelierPanel'),
  panelHidden:document.getElementById('modelAtelierPanel')?.hidden,
  railExists:!!document.getElementById('modelAtelierToolRail'),
  scripts:[...document.scripts].slice(0,5).map(s=>s.src||s.type),
  moduleHead:document.querySelector('script[type="module"]')?.textContent?.slice(0,900)
 }));}catch{}
 console.error('SE_V11119_MOBILE_CHROME_DIAGNOSTIC',JSON.stringify(diagnostic));
 console.error('SE_V11119_MOBILE_CHROME_REQUESTS',JSON.stringify(pageErrors.slice(-15)));

 console.error('SE_V11119_MOBILE_CHROME_SMOKE_FAILURE',String(e));throw e;}
finally{await browser?.close().catch(()=>{});server.kill();}
