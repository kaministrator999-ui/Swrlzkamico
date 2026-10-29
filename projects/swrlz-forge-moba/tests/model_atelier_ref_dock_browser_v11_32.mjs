import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile]of[['desktop',{width:1280,height:900},false],
 ['android-touch',{width:412,height:915},true]]){
  const c=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await c.newPage();page.setDefaultTimeout(60000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const status=()=>page.evaluate(()=>window.SWYRL_ENGINE_REFERENCE.status());
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const original=await parts();assert.equal(original.length,283);
  await page.locator('#modelAtelierReferenceToggle').click();
  assert.equal((await status()).open,true);
  await page.locator('#modelAtelierReferenceWidth').fill(mobile?'310':'400');
  await page.locator('#modelAtelierReferenceHeight').fill(mobile?'420':'480');
  await page.locator('#modelAtelierReferenceApplySize').click();
  let state=await status();
  const width=mobile?310:400,height=mobile?420:480;
  assert.equal(state.width,width);assert.equal(state.height,height);
  await page.locator('#modelAtelierReferenceWidth').fill('9999');
  await page.locator('#modelAtelierReferenceApplySize').click();
  state=await status();assert.equal(state.width,width,'Invalid resize must not change native layout');
  assert.equal(state.height,height);
  const dock=page.locator('#modelAtelierReferenceDock');
  const panelRect=await dock.boundingBox();
  assert(panelRect?.width<=viewport.width,'Dock must be capped by narrow viewport');
  assert(panelRect?.height<=viewport.height,'Dock must be clipped to viewport');
  await page.locator('#modelAtelierReferencePin').click();
  const pinned=await status();assert.equal(pinned.pinned,true);
  assert.equal(await page.locator('#modelAtelierReferencePin').getAttribute('aria-pressed'),'true');
  // A pinned header must never begin a drag; UI users may still transform
  // the underlying reference image independently.
  const strong=page.locator('#modelAtelierReferenceHandle strong');
  const h=await strong.boundingBox();
  assert(h,'Reference drag text must be visible');
  const x=h.x+h.width/2,y=h.y+h.height/2;
  if(mobile){
   const session=await c.newCDPSession(page);
   await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y,id:7}]});
   await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x+35,y:y+35,id:7}]});
   await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  }else{
   await page.mouse.move(x,y);await page.mouse.down();
   await page.mouse.move(x+35,y+35,{steps:4});await page.mouse.up();
  }
  state=await status();assert.equal(state.x,pinned.x);assert.equal(state.y,pinned.y);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await status()).pinned,false,'Pin must be one native Undo checkpoint');
  await page.locator('#modelAtelierReferencePin').click();
  assert.equal((await status()).pinned,true);
  const download=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await download).path();
  const saved=JSON.parse(await readFile(path,'utf8'));
  assert.equal(saved.model.referenceLayout.width,width);
  assert.equal(saved.model.referenceLayout.height,height);
  assert.equal(saved.model.referenceLayout.pinned,true);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await status()).pinned,false);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_REFERENCE.status().pinned===true);
  state=await status();
  assert.equal(state.width,width);assert.equal(state.height,height);
  assert.equal(state.open,true);assert.equal(state.pinned,true);
  assert.equal((await parts()).length,283);
  assert.deepEqual((await parts()).find(x=>x.id==='model-0001').headAnatomy,
    original.find(x=>x.id==='model-0001').headAnatomy);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1132_REFERENCE_DOCK_PIN_SIZE_UNDO_NATIVE_ROUNDTRIP_PASS',device,width,height);
  await c.close();
 }
}finally{await browser.close();}
