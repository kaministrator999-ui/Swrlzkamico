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
  const part=async()=>(await parts()).find(p=>p.id==='model-0001');
  const count=async()=>Number((await page.locator('#modelAtelierRefineStats').textContent())
      .match(/Current visible mesh: ([\d,]+) triangles/)?.[1].replaceAll(',',''));
  assert.equal((await parts()).length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  const original=await part();
  await page.locator('#modelAtelierLassoStart').click();
  for(const coords of[[-.23,-.24,.85],[.23,-.24,.85],[0,.18,.92]]){
    for(let i=0;i<3;i++)
      await page.locator('#modelAtelierLassoPinXYZ'+i).fill(String(coords[i]));
    await page.locator('#modelAtelierLassoAddXYZ').click();
  }
  await page.locator('#modelAtelierLassoFinish').click();
  await page.locator('#modelAtelierRefineLevel').selectOption('1');
  await page.locator('#modelAtelierRefineAdd').click();
  let p=await part();assert.equal(p.refinementLayers?.length,1);
  assert.equal(p.refinementLayers[0].locked,false);
  const firstId=p.refinementLayers[0].id;
  const refined=await count();
  await page.locator('#modelAtelierRefineLock').click();
  p=await part();assert.equal(p.refinementLayers[0].locked,true);
  await page.locator('#modelAtelierRefineRemove').click();
  p=await part();assert.equal(p.refinementLayers.length,1,
    'Structurally locked layer must reject removal');
  await page.locator('#modelAtelierRefineDuplicate').click();
  p=await part();assert.equal(p.refinementLayers.length,2);
  assert.equal(p.refinementLayers[0].id,firstId);
  assert.equal(p.refinementLayers[0].locked,true);
  assert.equal(p.refinementLayers[1].locked,false);
  assert.equal(p.refinementLayers[1].enabled,false);
  assert.notEqual(p.refinementLayers[0].id,p.refinementLayers[1].id);
  assert.equal(await count(),refined,
    'Disabled duplicate must not multiply generated triangles');
  const clonedId=p.refinementLayers[1].id;
  await page.locator('#modelAtelierRefineLayer').selectOption('1');
  await page.locator('#modelAtelierRefineUp').click();
  p=await part();assert.equal(p.refinementLayers[0].id,firstId,
    'Cannot move unlocked clone through locked layer');
  await page.locator('#modelAtelierRefineLayer').selectOption('0');
  await page.locator('#modelAtelierRefineLock').click();
  p=await part();assert.equal(p.refinementLayers[0].locked,false);
  await page.locator('#modelAtelierRefineDown').click();
  p=await part();assert.equal(p.refinementLayers[0].id,clonedId);
  assert.equal(p.refinementLayers[1].id,firstId);
  await page.locator('#modelAtelierUndo').click();
  p=await part();assert.equal(p.refinementLayers[0].id,firstId,
    'Reorder must be one Undo checkpoint');
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierRefineLayer').selectOption('1');
  await page.locator('#modelAtelierRefineLock').click();
  p=await part();assert.equal(p.refinementLayers[1].locked,true);
  await page.locator('#modelAtelierRefineRemove').click();
  p=await part();assert.equal(p.refinementLayers.length,2);
  await page.locator('#modelAtelierRefineToggle').click();
  p=await part();assert.equal(p.refinementLayers[1].enabled,true,
    'Visibility remains independent of structural lock');
  await page.locator('#modelAtelierRefineToggle').click();
  p=await part();assert.equal(p.refinementLayers[1].enabled,false);
  const savedSnapshot=p.refinementLayers;
  const dl=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const file=await(await dl).path(),native=JSON.parse(await readFile(file,'utf8'));
  assert.deepEqual(native.model.parts.find(x=>x.id==='model-0001').refinementLayers,savedSnapshot);
  await page.locator('#modelAtelierUndo').click();
  p=await part();assert.equal(p.refinementLayers[1].enabled,true);
  await page.locator('#modelAtelierImportFile').setInputFiles(file);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene()
    .project.modelAtelier.parts.find(x=>x.id==='model-0001')?.refinementLayers?.length===2);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  p=await part();assert.deepEqual(p.refinementLayers,savedSnapshot);
  assert.deepEqual(p.headAnatomy,original.headAnatomy,
    'Original eleven-section native anatomical head must remain unchanged');
  assert.equal((await parts()).length,283);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1131_REFINEMENT_LOCK_DUPLICATE_REORDER_UNDO_NATIVE_ROUNDTRIP_PASS',device);
  await c.close();
 }
}finally{await browser.close();}
