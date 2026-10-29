import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile]of[
  ['desktop',{width:1280,height:900},false],
  ['android-touch',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(60000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const all=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const head=async()=>(await all()).find(x=>x.id==='model-0001');
  const original=await head();assert.equal((await all()).length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierLassoStart').click();
  for(const xyz of[[-.23,-.24,.85],[.23,-.24,.85],[0,.18,.92]]){
    for(let i=0;i<3;i++)
      await page.locator('#modelAtelierLassoPinXYZ'+i).fill(String(xyz[i]));
    await page.locator('#modelAtelierLassoAddXYZ').click();
  }
  await page.locator('#modelAtelierLassoFinish').click();
  let p=await head();assert.equal(p.sculptLassos?.length,1);
  assert.equal(p.sculptLassos[0].pins.length,3);
  const beforePins=p.sculptLassos[0].pins;
  const budget=async()=>{
    await page.locator('#modelAtelierRefinePreview').click();
    const text=await page.locator('#modelAtelierRefineBudget').textContent();
    assert.match(text,/Measured local preview/);
    return Number(text.match(/→ ([\d,]+) triangles/)?.[1].replaceAll(',',''));
  };
  const straight=await budget();assert(Number.isFinite(straight));
  await page.locator('#modelAtelierLassoCurve').fill('0.8');
  await page.locator('#modelAtelierLassoCurveApply').click();
  p=await head();
  assert.equal(p.sculptLassos[0].boundaryCurve,.8);
  assert.deepEqual(p.sculptLassos[0].pins,beforePins,
   'Curving boundary cannot change original mesh-attached pin controls');
  const rounded=await budget();
  assert(rounded<straight,'Curvature must alter actual topology footprint on head');
  await page.locator('#modelAtelierLassoCurve').fill('1.2');
  await page.locator('#modelAtelierLassoCurveApply').click();
  p=await head();assert.equal(p.sculptLassos[0].boundaryCurve,.8,
   'Invalid curve strength must be ignored without project mutation');
  await page.locator('#modelAtelierRefineAdd').click();
  p=await head();assert.equal(p.refinementLayers?.length,1);
  const triangles=Number((await page.locator('#modelAtelierRefineStats').textContent())
    .match(/Current visible mesh: ([\d,]+) triangles/)?.[1].replaceAll(',',''));
  assert.equal(triangles,rounded);
  const download=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const file=await(await download).path(),json=JSON.parse(await readFile(file,'utf8'));
  assert.equal(json.model.parts.find(x=>x.id==='model-0001').sculptLassos[0].boundaryCurve,.8);
  await page.locator('#modelAtelierUndo').click();
  p=await head();assert.equal(p.refinementLayers?.length||0,0);
  await page.locator('#modelAtelierUndo').click();
  p=await head();assert.equal(p.sculptLassos[0].boundaryCurve,undefined,
   'Curve change must Undo independently of real mesh detail layer');
  await page.locator('#modelAtelierImportFile').setInputFiles(file);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project
   .modelAtelier.parts.find(x=>x.id==='model-0001')?.refinementLayers?.length===1);
  p=await head();
  assert.equal(p.sculptLassos[0].boundaryCurve,.8);
  assert.deepEqual(p.sculptLassos[0].pins,beforePins);
  assert.equal((await all()).length,283);
  assert.deepEqual(p.headAnatomy,original.headAnatomy);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1135_CURVED_BOUNDARY_REAL_HEAD_REFINEMENT_PINS_UNDO_SAVE_RELOAD_PASS',
    device,straight,rounded);
  await context.close();
 }
}finally{await browser.close();}
