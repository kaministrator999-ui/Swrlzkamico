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
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const original=await parts();assert.equal(original.length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierSculptBrushSurfaceMode').selectOption('nearest');
  await page.locator('#modelAtelierSculptBrushRadius').fill('0.15');
  await page.locator('#modelAtelierSculptBrushSelectRadius').fill('0.18');
  await page.locator('#modelAtelierSculptBrushAmount').fill('0.025');
  await page.locator('#modelAtelierSculptBrushApply').click();
  let head=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(head.sculptBrushes?.at(-1).surfaceMode,'nearest');
  assert.deepEqual(head.headAnatomy,original.find(x=>x.id==='model-0001').headAnatomy);
  const d=page.waitForEvent('download');await page.locator('#modelAtelierExport').click();
  const file=await(await d).path(),json=JSON.parse(await readFile(file,'utf8'));
  assert.equal(json.model.parts.find(x=>x.id==='model-0001').sculptBrushes.at(-1).surfaceMode,'nearest');
  await page.locator('#modelAtelierUndo').click();
  head=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(head.sculptBrushes?.length||0,0);
  await page.locator('#modelAtelierImportFile').setInputFiles(file);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project
    .modelAtelier.parts.find(x=>x.id==='model-0001')?.sculptBrushes?.at(-1)?.surfaceMode==='nearest');
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1129_NEAREST_SHELL_REAL_BROWSER_NATIVE_SAVE_UNDO_RELOAD_PASS',device);
  await c.close();
 }
}finally{await browser.close();}
