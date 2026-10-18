import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile]of[['desktop',{width:1280,height:880},false],
 ['mobile',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(35000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const get=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierLassoStart').click();
  for(const [x,y,z]of[[-.23,-.24,.85],[.23,-.24,.85],[0,.18,.92]]){
   for(const [i,v]of[x,y,z].entries())await page.locator('#modelAtelierLassoPinXYZ'+i).fill(String(v));
   await page.locator('#modelAtelierLassoAddXYZ').click();
  }
  await page.locator('#modelAtelierLassoFinish').click();
  let p=(await get()).find(x=>x.id==='model-0001');
  assert.equal(p.sculptLassos?.length,1,'Saved original head lasso needed before refining');
  assert(await page.locator('#modelAtelierRefineTools').isVisible());
  const count=async()=>Number((await page.locator('#modelAtelierRefineStats').textContent())
    .match(/Current visible mesh: ([\d,]+) triangles/)?.[1].replaceAll(',',''));
  const before=await count();
  assert(before>1000);
  await page.locator('#modelAtelierRefineLevel').selectOption('1');
  await page.locator('#modelAtelierRefinePreview').click();
  const preview=(await page.locator('#modelAtelierRefineBudget').textContent());
  assert.match(preview,/Measured local preview/);
  const predicted=Number(preview.match(/→ ([\d,]+) triangles/)?.[1].replaceAll(',',''));
  assert(Number.isFinite(predicted)&&predicted>before);
  assert.equal((await get()).find(x=>x.id==='model-0001').refinementLayers,undefined,
   'Preview must not create a persistent refinement layer');
  await page.locator('#modelAtelierRefineAdd').click();
  p=(await get()).find(x=>x.id==='model-0001');
  assert.equal(p.refinementLayers?.length,1,'Applying density must create a real native topology layer');
  const after=await count();
  assert.equal(after,predicted,'Preview and actual generated topology must match exactly');
  assert(after>before,'Refined selected head needs more triangles; before '+before+' after '+after);
  const save=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await save).path(),saved=JSON.parse(await readFile(path,'utf8'));
  assert.equal(saved.model.parts.find(p=>p.id==='model-0001').refinementLayers?.length,1);
  await page.locator('#modelAtelierRefineToggle').click();
  const disabled=await count();
  assert.equal(disabled,before,'Disabling the detail layer restores original density');
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await get()).find(p=>p.id==='model-0001').refinementLayers[0].enabled,true);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier
    .parts.find(x=>x.id==='model-0001')?.refinementLayers?.length===1);
  // A valid import deliberately clears the current mesh selection. Re-select
  // the restored head before reading inspector-scoped visible triangle counts.
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  assert.equal(await count(),after,'Native JSON reload must reproduce refined mesh');
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1123_LOCAL_DETAIL_BROWSER_DENSITY_UNDO_SAVE_RELOAD_PASS',device,before,after);
  await context.close();
 }
}finally{await browser.close();}
