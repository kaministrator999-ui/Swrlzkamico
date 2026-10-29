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
  const make=async(coords)=>{
    await page.locator('#modelAtelierLassoStart').click();
    for(const xyz of coords){
      for(let i=0;i<3;i++)await page.locator('#modelAtelierLassoPinXYZ'+i).fill(String(xyz[i]));
      await page.locator('#modelAtelierLassoAddXYZ').click();
    }
    await page.locator('#modelAtelierLassoFinish').click();
  };
  await make([[-.23,-.24,.85],[.23,-.24,.85],[0,.18,.92]]);
  const base=(await head()).sculptLassos?.[0]?.id;assert(base);
  await make([[-.15,-.24,.85],[.31,-.24,.85],[.08,.18,.92]]);
  let p=await head();assert.equal(p.sculptLassos.length,2);
  const other=p.sculptLassos[1].id;
  await page.locator('#modelAtelierLassoRegion').selectOption(base);
  await page.locator('#modelAtelierLassoBooleanWith').selectOption(other);
  const counts={};
  for(const op of ['add','subtract','intersect']){
    await page.locator('#modelAtelierLassoBooleanOp').selectOption(op);
    await page.locator('#modelAtelierLassoBooleanApply').click();
    p=await head();
    assert.equal(p.sculptLassos[0].selectionOp,op);
    assert.equal(p.sculptLassos[0].operandRegionId,other);
    await page.locator('#modelAtelierRefinePreview').click();
    const budget=await page.locator('#modelAtelierRefineBudget').textContent();
    assert.match(budget,/Measured local preview/,op+' must produce measured actual triangle budget');
    counts[op]=Number(budget.match(/→ ([\d,]+) triangles/)?.[1].replaceAll(',',''));
    assert(Number.isFinite(counts[op]));
  }
  assert(counts.add>counts.intersect,'Union must evaluate larger refinement area than intersection');
  await page.locator('#modelAtelierLassoRegion').selectOption(other);
  await page.locator('#modelAtelierLassoDeleteRegion').click();
  p=await head();assert.equal(p.sculptLassos.length,2,
    'Referenced Boolean operand deletion must not invalidate native scene');
  await page.locator('#modelAtelierLassoRegion').selectOption(base);
  await page.locator('#modelAtelierRefineLevel').selectOption('1');
  await page.locator('#modelAtelierRefineAdd').click();
  p=await head();assert.equal(p.refinementLayers?.length,1);
  assert.equal(p.sculptLassos[0].selectionOp,'intersect');
  const shown=Number((await page.locator('#modelAtelierRefineStats').textContent())
      .match(/Current visible mesh: ([\d,]+) triangles/)?.[1].replaceAll(',',''));
  assert.equal(shown,counts.intersect,'Preview must match actual Boolean-refined mesh');
  const dl=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const file=await(await dl).path(),native=JSON.parse(await readFile(file,'utf8'));
  assert.equal(native.model.parts.find(x=>x.id==='model-0001').sculptLassos[0].selectionOp,'intersect');
  await page.locator('#modelAtelierUndo').click();
  p=await head();assert.equal(p.refinementLayers?.length||0,0,'Whole-model Undo removes Boolean refinement');
  await page.locator('#modelAtelierImportFile').setInputFiles(file);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project
    .modelAtelier.parts.find(x=>x.id==='model-0001')?.refinementLayers?.length===1);
  p=await head();assert.equal(p.sculptLassos[0].operandRegionId,other);
  assert.deepEqual(p.sculptLassos,native.model.parts.find(x=>x.id==='model-0001').sculptLassos);
  assert.deepEqual(p.headAnatomy,original.headAnatomy);
  assert.equal((await all()).length,283);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1134_NAMED_BOOLEAN_REGION_REAL_HEAD_SCULPT_REFINEMENT_NATIVE_BROWSER_PASS',
    device,counts.add,counts.subtract,counts.intersect);
  await context.close();
 }
}finally{await browser.close();}
