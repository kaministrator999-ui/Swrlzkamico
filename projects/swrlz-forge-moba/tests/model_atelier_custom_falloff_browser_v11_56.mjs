import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile]of[['desktop',{width:1280,height:900},false],
  ['android-touch',{width:412,height:915},true]]){
  const ctx=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await ctx.newPage();page.setDefaultTimeout(90000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const original=await parts();assert.equal(original.length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierSculptBrushRadius').fill('.4');
  await page.locator('#modelAtelierSculptBrushAmount').fill('.05');
  await page.locator('#modelAtelierSculptBrushCurveEnabled').check();
  await page.locator('#modelAtelierSculptBrushCurveValues').fill('.95, .45, .10');
  await page.locator('#modelAtelierSculptBrushApply').click();
  let p=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(p.sculptBrushes?.length,1);
  assert.deepEqual(p.sculptBrushes[0].falloffCurve,[1,.95,.45,.1,0]);
  const saved=JSON.parse(JSON.stringify(p.sculptBrushes[0]));
  await page.locator('#modelAtelierSculptBrushCurveValues').fill('.1,.9,.2');
  await page.locator('#modelAtelierSculptBrushApply').click();
  p=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(p.sculptBrushes?.length,1,'invalid pressure must not change native project');
  await page.locator('#modelAtelierSculptBrushCurveEnabled').uncheck();
  await page.locator('#modelAtelierSculptBrushApply').click();
  p=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(p.sculptBrushes?.length,2);
  assert.equal(p.sculptBrushes[1].falloffCurve,undefined,'legacy unmodified brush remains unchanged');
  const dl=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await dl).path();
  const json=JSON.parse(await readFile(path,'utf8'));
  assert.deepEqual(json.model.parts.find(x=>x.id==='model-0001').sculptBrushes[0],saved);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await parts()).find(x=>x.id==='model-0001').sculptBrushes?.length,1);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier
   .parts.find(x=>x.id==='model-0001')?.sculptBrushes?.length===2);
  assert.deepEqual((await parts()).find(x=>x.id==='model-0001').sculptBrushes[0],saved);
  assert.deepEqual((await parts()).find(x=>x.id==='model-0001').headAnatomy,
   original.find(x=>x.id==='model-0001').headAnatomy);
  assert.deepEqual(errors,[]);
  console.log('V1156_FIVE_KNOT_FALLOFF_NATIVE_DESKTOP_ANDROID_SAVE_UNDO_REIMPORT_PASS',device);
  await ctx.close();
 }
}finally{await browser.close();}
