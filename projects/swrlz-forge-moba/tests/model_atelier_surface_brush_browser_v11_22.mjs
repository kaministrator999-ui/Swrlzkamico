import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl',
 '--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'
]});
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
try {
 for(const [kind,viewport,isMobile]of[['desktop',{width:1300,height:860},false],
   ['mobile',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile,hasTouch:isMobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(30000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const get=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const original=await get();assert.equal(original.length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  const menu=page.locator('#modelAtelierSculptBrushSurfaceMode');
  assert(await menu.isVisible(),'Surface targeting must be accessible in sculpt inspector');
  await menu.selectOption('front');
  await page.locator('#modelAtelierSculptBrushSelectRadius').fill('.24');
  await page.locator('#modelAtelierSculptBrushRadius').fill('.2');
  await page.locator('#modelAtelierSculptBrushOffsetU').fill('.04');
  await page.locator('#modelAtelierSculptBrushOffsetV').fill('-.02');
  await page.locator('#modelAtelierSculptBrushAmount').fill('.035');
  await page.locator('#modelAtelierSculptBrushApply').click();
  let head=(await get()).find(x=>x.id==='model-0001');
  assert.equal(head.sculptBrushes.at(-1).surfaceMode,'front');
  assert.equal(head.sculptBrushes.at(-1).selectionRadius,.24);
  assert.equal(head.sculptBrushes.at(-1).radius,.2);
  assert.equal(head.sculptBrushes.at(-1).offsetU,.04);
  assert.equal(head.sculptBrushes.at(-1).offsetV,-.02);
  const download=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const fp=await(await download).path(),model=JSON.parse(await readFile(fp,'utf8'));
  assert.equal(model.model.parts.find(p=>p.id==='model-0001').sculptBrushes[0].surfaceMode,'front');
  await page.locator('#modelAtelierUndo').click();
  assert(!(await get()).find(p=>p.id==='model-0001').sculptBrushes?.length);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await menu.selectOption('connected');
  await page.locator('#modelAtelierSculptBrushApply').click();
  assert.equal((await get()).find(p=>p.id==='model-0001').sculptBrushes[0].surfaceMode,'connected');
  await page.locator('#modelAtelierUndo').click();
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await menu.selectOption('through');
  await page.locator('#modelAtelierSculptBrushApply').click();
  assert.equal((await get()).find(p=>p.id==='model-0001').sculptBrushes[0].surfaceMode,'through');
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1122_SURFACE_BRUSH_BROWSER_MODES_UNDO_SAVE_PASS',kind);
  await context.close();
 }
}finally{await browser.close();}
