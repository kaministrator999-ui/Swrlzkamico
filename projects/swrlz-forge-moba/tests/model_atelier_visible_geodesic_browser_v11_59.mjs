import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl',
 '--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try {
 for(const [label,viewport,mobile] of [
  ['desktop',{width:1280,height:900},false],
  ['android-touch',{width:412,height:915},true]
 ]){
  const ctx=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await ctx.newPage();
  page.setDefaultTimeout(90000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const original=await parts();assert.equal(original.length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierSculptBrushSurfaceMode').selectOption('visible-geodesic');
  // Exercise a non-push operator: it must use surface-path weights too.
  await page.locator('#modelAtelierSculptBrushMode').selectOption('inflate');
  await page.locator('#modelAtelierSculptBrushRadius').fill('.12');
  await page.locator('#modelAtelierSculptBrushSelectRadius').fill('.15');
  await page.locator('#modelAtelierSculptBrushAmount').fill('.025');
  await page.locator('#modelAtelierSculptBrushApply').click();
  const get=()=>parts().then(x=>x.find(p=>p.id==='model-0001'));
  const updated=await get();
  const saved=updated.sculptBrushes?.at(-1);
  assert.equal(saved?.surfaceMode,'visible-geodesic','new mode must save to real model');
  assert.equal(saved?.operation,'inflate');
  assert.equal(saved?.cameraLocal?.length,3,'must freeze eye in native model coordinates');
  assert(saved.cameraLocal.every(Number.isFinite));
  assert.deepEqual(updated.headAnatomy,original.find(p=>p.id==='model-0001').headAnatomy);
  const download=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const file=await(await download).path(),json=JSON.parse(await readFile(file,'utf8'));
  const exported=json.model.parts.find(p=>p.id==='model-0001').sculptBrushes.at(-1);
  assert.deepEqual(exported.cameraLocal,saved.cameraLocal);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await get()).sculptBrushes?.length||0,0,'Undo restores prior model');
  await page.locator('#modelAtelierImportFile').setInputFiles(file);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
     .find(p=>p.id==='model-0001')?.sculptBrushes?.at(-1)?.surfaceMode==='visible-geodesic');
  assert.deepEqual((await get()).sculptBrushes.at(-1).cameraLocal,saved.cameraLocal);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1159_CAMERA_VISIBLE_GEODESIC_REAL_BROWSER_NATIVE_SAVE_UNDO_IMPORT_PASS',label);
  await ctx.close();
 }
}finally{await browser.close();}
