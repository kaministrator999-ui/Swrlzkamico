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
  const beforePins=p.sculptLassos[0].pins;
  const budget=async()=>{
    await page.locator('#modelAtelierRefinePreview').click();
    const text=await page.locator('#modelAtelierRefineBudget').textContent();
    assert.match(text,/Measured local preview/);
    return Number(text.match(/→ ([\d,]+) triangles/)?.[1].replaceAll(',',''));
  };
  const before=await budget();
  await page.locator('#modelAtelierLassoPinIndex').selectOption('0');
  await page.locator('#modelAtelierLassoSegmentAmount').fill('0.03');
  await page.locator('#modelAtelierLassoSegmentMove').click();
  p=await head();
  assert.equal(p.sculptLassos[0].pins.length,3);
  const movedPins=p.sculptLassos[0].pins;
  assert.notDeepEqual(movedPins.slice(0,2),beforePins.slice(0,2));
  assert.deepEqual(movedPins[2],beforePins[2],
    'Selected segment adjustment must leave other original pinned vertices untouched');
  const after=await budget();
  assert(after>before,'Growing selected boundary segment must actually select more head triangles');
  await page.locator('#modelAtelierLassoSegmentAmount').fill('9');
  await page.locator('#modelAtelierLassoSegmentMove').click();
  p=await head();assert.deepEqual(p.sculptLassos[0].pins,movedPins,
    'Invalid move cannot change attached pin data');
  const dl=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const file=await(await dl).path(),json=JSON.parse(await readFile(file,'utf8'));
  assert.deepEqual(json.model.parts.find(x=>x.id==='model-0001').sculptLassos[0].pins,movedPins);
  await page.locator('#modelAtelierUndo').click();
  p=await head();assert.deepEqual(p.sculptLassos[0].pins,beforePins,
    'Edge operation must Undo in one checkpoint');
  await page.locator('#modelAtelierImportFile').setInputFiles(file);
  await page.waitForFunction(({target})=>{
   const p=window.SWYRL_ENGINE_AGENT.inspectScene().project
    .modelAtelier.parts.find(x=>x.id==='model-0001');
   return p?.sculptLassos?.[0]?.pins?.[0]?.point?.[1]===target;
  },{target:movedPins[0].point[1]});
  p=await head();assert.deepEqual(p.sculptLassos[0].pins,movedPins);
  assert.deepEqual(p.headAnatomy,original.headAnatomy);
  assert.equal((await all()).length,283);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1136_SELECTED_EDGE_REAL_HEAD_GROW_INVALID_UNDO_SAVE_RELOAD_PASS',device,before,after);
  await context.close();
 }
}finally{await browser.close();}
