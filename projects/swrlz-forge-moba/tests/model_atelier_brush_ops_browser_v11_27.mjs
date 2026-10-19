import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl',
 '--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'
]});
try{
 for(const [device,viewport,mobile]of[
  ['desktop',{width:1280,height:900},false],['android-touch',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(60000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const readParts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const original=await readParts(),head=original.find(x=>x.id==='model-0001');
  assert.equal(original.length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  const modes=['smooth','flatten','inflate','pinch','translate'];
  for(const mode of modes){
   await page.locator('#modelAtelierSculptBrushMode').selectOption(mode);
   await page.locator('#modelAtelierSculptBrushFalloff').selectOption('sharp');
   await page.locator('#modelAtelierSculptBrushMirrorX').check();
   await page.locator('#modelAtelierSculptBrushAmount').fill('0.04');
   await page.locator('#modelAtelierSculptBrushRadius').fill('0.25');
   await page.locator('#modelAtelierSculptBrushSelectRadius').fill('0.25');
   await page.locator('#modelAtelierSculptBrushApply').click();
   const edit=(await readParts()).find(x=>x.id==='model-0001');
   assert.equal(edit.sculptBrushes?.at(-1).operation,mode);
   assert.equal(edit.sculptBrushes?.at(-1).mirrorX,true);
   assert.equal(edit.sculptBrushes?.at(-1).falloff,'sharp');
  }
  let updated=(await readParts()).find(x=>x.id==='model-0001');
  assert.equal(updated.sculptBrushes.length,5);
  assert.deepEqual(updated.headAnatomy,head.headAnatomy,
   'New operators may not overwrite original section-built anatomy');
  const download=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const savedPath=await(await download).path();
  const saved=JSON.parse(await readFile(savedPath,'utf8'));
  assert.equal(saved.model.parts.find(x=>x.id==='model-0001').sculptBrushes.length,5);
  await page.locator('#modelAtelierUndo').click();
  updated=(await readParts()).find(x=>x.id==='model-0001');
  assert.equal(updated.sculptBrushes.length,4);
  await page.locator('#modelAtelierImportFile').setInputFiles(savedPath);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene()
   .project.modelAtelier.parts.find(x=>x.id==='model-0001')?.sculptBrushes?.length===5);
  updated=(await readParts()).find(x=>x.id==='model-0001');
  assert.deepEqual(updated.sculptBrushes,saved.model.parts.find(x=>x.id==='model-0001').sculptBrushes);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1127_ADVANCED_BRUSH_REAL_BROWSER_NATIVE_ROUNDTRIP_PASS',device,modes.join(','));
  await context.close();
 }
}finally{await browser.close();}
