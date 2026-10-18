import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile]of[['desktop',{width:1280,height:900},false],
   ['mobile',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(30000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  assert(await page.locator('#modelAtelierLassoTools').isVisible(),'Lasso controls must appear when a mesh is selected');
  await page.locator('#modelAtelierLassoStart').click();
  const add=async(x,y,z)=>{
   for(let i=0;i<3;i++)await page.locator('#modelAtelierLassoPinXYZ'+i).fill(String([x,y,z][i]));
   await page.locator('#modelAtelierLassoAddXYZ').click();
  };
  await add(-.23,-.24,.85);
  await add(.23,-.24,.85);
  await add(0,.18,.92);
  assert.match(await page.locator('#modelAtelierLassoInfo').textContent(),/Draft: 3 pins/);
  await page.locator('#modelAtelierLassoFinish').click();
  let p=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(p.sculptLassos?.length,1,'Completing a polygon should save a native lasso');
  assert.equal(p.sculptLassos[0].pins.length,3);
  assert(p.sculptLassos[0].pins.every(x=>Number.isInteger(x.tri)&&x.bary.length===3));
  const initialPins=JSON.stringify(p.sculptLassos[0].pins);
  await page.locator('#modelAtelierLassoGroupPins').fill('1,2');
  await page.locator('#modelAtelierLassoGroupDelta1').fill('.02');
  await page.locator('#modelAtelierLassoGroupMove').click();
  p=(await parts()).find(x=>x.id==='model-0001');
  assert.notEqual(JSON.stringify(p.sculptLassos[0].pins),initialPins,
    'Grouped boundary edit must reproject selected pins');
  assert.equal(p.sculptLassos[0].pins.length,3);
  const movedPins=JSON.stringify(p.sculptLassos[0].pins);
  await page.locator('#modelAtelierUndo').click();
  p=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(JSON.stringify(p.sculptLassos[0].pins),initialPins,
    'One group edit must be one Undo transaction');
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierLassoGroupPins').fill('1,2');
  await page.locator('#modelAtelierLassoGroupDelta1').fill('.02');
  await page.locator('#modelAtelierLassoGroupMove').click();
  p=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(JSON.stringify(p.sculptLassos[0].pins),movedPins,
    'Native surface reprojection must be deterministic');
  await page.locator('#modelAtelierLassoGroupPins').fill('99');
  await page.locator('#modelAtelierLassoGroupMove').click();
  p=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(JSON.stringify(p.sculptLassos[0].pins),movedPins,
    'Invalid group selection must not mutate a saved boundary');
  await page.locator('#modelAtelierLassoMorph').fill('.025');
  await page.locator('#modelAtelierLassoFeather').fill('.03');
  await page.locator('#modelAtelierLassoApplyMorph').click();
  p=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(p.sculptLassos[0].morph,.025);
  const d=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await d).path(),json=JSON.parse(await readFile(path,'utf8'));
  assert.equal(json.model.parts.find(x=>x.id==='model-0001').sculptLassos.length,1);
  await page.locator('#modelAtelierUndo').click();
  p=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(p.sculptLassos[0].morph,0,'Undo should restore the prior region operation');
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene()
    .project.modelAtelier.parts.find(p=>p.id==='model-0001')?.sculptLassos?.[0]?.morph===.025);
  p=(await parts()).find(x=>x.id==='model-0001');
  assert.equal(p.sculptLassos[0].morph,.025);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1122_LASSO_POLYGON_NUMERIC_SURFACE_PIN_MORPH_UNDO_JSON_PASS',device);
  await context.close();
 }
}finally{await browser.close();}
