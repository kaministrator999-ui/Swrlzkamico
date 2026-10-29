import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [name,viewport,mobile] of [['desktop',{width:1280,height:900},false],['mobile',{width:412,height:915},true]]){
  const c=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile});
  const page=await c.newPage();page.setDefaultTimeout(45000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const original=await parts();assert.equal(original.length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  const before=await parts();
  assert(await page.locator('#modelAtelierViewportInsideEnter').isVisible());
  await page.locator('#modelAtelierViewportClipNear').fill('0.03');
  await page.locator('#modelAtelierViewportClipFar').fill('40');
  await page.locator('#modelAtelierViewportClipApply').click();
  let status=await page.evaluate(()=>window.SWYRL_ENGINE_VIEW.status());
  assert.equal(status.near,.03);assert.equal(status.far,40);
  await page.locator('#modelAtelierViewportClipNear').fill('2');
  await page.locator('#modelAtelierViewportClipApply').click();
  status=await page.evaluate(()=>window.SWYRL_ENGINE_VIEW.status());
  assert.equal(status.near,.03,'Invalid near plane must reject without camera mutation');
  const originalCamera=await page.evaluate(()=>window.SWYRL_ENGINE_VIEW.status());
  await page.locator('#modelAtelierViewportInsideEnter').click();
  status=await page.evaluate(()=>window.SWYRL_ENGINE_VIEW.status());
  assert.equal(status.interior,true);assert(status.distance<.4);assert.equal(status.near,.01);
  assert.equal(status.global,'shaded','Global render mode must not be overwritten');
  await page.locator('#modelAtelierSculptBrushSurfaceMode').selectOption('inside');
  await page.locator('#modelAtelierSculptBrushAmount').fill('0.02');
  await page.locator('#modelAtelierSculptBrushApply').click();
  let head=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(head.sculptBrushes?.at(-1).surfaceMode,'inside');
  await page.locator('#modelAtelierUndo').click();
  head=(await parts()).find(x=>x.id==='model-0001');
  assert(!head.sculptBrushes?.some(s=>s.surfaceMode==='inside'),'Undo must remove last inside-sculpt stroke');
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierViewportInsideExit').click();
  status=await page.evaluate(()=>window.SWYRL_ENGINE_VIEW.status());
  assert.equal(status.interior,false);
  assert.equal(status.distance,originalCamera.distance,'Exit must restore actual prior camera distance');
  assert.equal(status.yaw,originalCamera.yaw);
  assert.equal(status.pitch,originalCamera.pitch);
  assert.equal(status.near,originalCamera.near);
  assert.equal(status.far,originalCamera.far);
  const after=await parts();
  assert.deepEqual(after,before,'Camera-only state must never mutate original native model');
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1125_INTERIOR_CAMERA_SHELL_BROWSER_UNDO_PASS',name);
  await c.close();
 }
}finally{await browser.close();}
