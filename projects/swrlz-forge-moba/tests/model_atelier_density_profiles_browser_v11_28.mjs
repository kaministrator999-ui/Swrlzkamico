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
  assert(await page.locator('#modelAtelierSculptDensityTools').isVisible());
  const before=(await parts()).find(p=>p.id==='model-0001');
  const baseU=Number(await page.locator('#modelAtelierSculptBrushGridU').inputValue());
  const baseV=Number(await page.locator('#modelAtelierSculptBrushGridV').inputValue());
  await page.locator('#modelAtelierSculptDensityPreset').selectOption('preview');
  const u=Number(await page.locator('#modelAtelierSculptBrushGridU').inputValue());
  const v=Number(await page.locator('#modelAtelierSculptBrushGridV').inputValue());
  assert(u<baseU&&v<baseV);
  await page.locator('#modelAtelierSculptDensityPreview').click();
  const info=await page.locator('#modelAtelierSculptDensityBudget').textContent();
  assert.match(info,/Measured native base/);
  assert.match(info,/vertex slots/);
  assert.match(info,/triangles/);
  assert.deepEqual((await parts()).find(p=>p.id==='model-0001'),before,
    'Density preview must never modify native project');
  await page.locator('#modelAtelierSculptBrushGridApply').click();
  let current=(await parts()).find(p=>p.id==='model-0001');
  assert.deepEqual(current.meshDensity,{u,v});
  assert.deepEqual(current.headAnatomy,before.headAnatomy,'Anatomical construction must stay intact');
  const dl=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await dl).path();
  const saved=JSON.parse(await readFile(path,'utf8'));
  assert.deepEqual(saved.model.parts.find(p=>p.id==='model-0001').meshDensity,{u,v});
  await page.locator('#modelAtelierUndo').click();
  current=(await parts()).find(p=>p.id==='model-0001');
  assert.deepEqual(current.meshDensity,before.meshDensity);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(({u,v})=>{
    const d=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.find(p=>p.id==='model-0001')?.meshDensity;
    return d?.u===u&&d?.v===v;
  },{u,v});
  current=(await parts()).find(p=>p.id==='model-0001');
  assert.deepEqual(current.meshDensity,{u,v});
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1128_EXACT_NATIVE_DENSITY_PRESET_BROWSER_UNDO_JSON_PASS',device,u,v);
  await c.close();
 }
}finally{await browser.close();}
