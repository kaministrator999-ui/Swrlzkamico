import assert from 'node:assert/strict';
import {chromium} from 'playwright';import {readFile} from 'node:fs/promises';
const url=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile] of [
  ['desktop',{width:1280,height:900},false],
  ['android-touch',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(65000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const original=await parts();assert.equal(original.length,283);
  const download=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const exported=JSON.parse(await readFile(await(await download).path(),'utf8'));
  const item={
    id:'test-winding-square',name:'Test UV triangle winding',group:'Test geometry',
    kind:'topologyMesh',material:'matte',color:'#88bbdd',
    position:[0,3,1],rotation:[0,0,0],scale:[.5,.5,.5],
    topologyMesh:{positions:[0,0,0,1,0,0,1,1,0,0,1,0],
      uvs:[0,0,1,0,1,1,0,1],indices:[0,1,2,0,2,3]}
  };
  exported.model.parts.push(item);
  await page.locator('#modelAtelierImportFile').setInputFiles({
   name:'topology-test.json',mimeType:'application/json',
   buffer:Buffer.from(JSON.stringify(exported))
  });
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.length===284);
  await page.locator('#modelAtelierParts').selectOption(item.id);
  assert(await page.locator('#modelAtelierAdaptiveTopologyTools').isVisible());
  await page.locator('#modelAtelierAdaptiveTopologyCenter0').fill(String(2/3));
  await page.locator('#modelAtelierAdaptiveTopologyCenter1').fill(String(1/3));
  await page.locator('#modelAtelierAdaptiveTopologyCenter2').fill('0');
  await page.locator('#modelAtelierAdaptiveTopologyRadius').fill('.1');
  await page.locator('#modelAtelierAdaptiveTopologyEdge').fill('.65');
  const nativeBefore=JSON.stringify((await parts()).find(x=>x.id===item.id).topologyMesh);
  await page.locator('#modelAtelierAdaptiveTopologyPreview').click();
  assert.match(await page.locator('#modelAtelierAdaptiveTopologyStatus').textContent(),/2 → 10 actual triangles/);
  assert.equal(JSON.stringify((await parts()).find(x=>x.id===item.id).topologyMesh),nativeBefore,
    'Preview must not mutate native geometry');
  await page.locator('#modelAtelierAdaptiveTopologyApply').click();
  let refined=(await parts()).find(x=>x.id===item.id).topologyMesh;
  assert.equal(refined.indices.length/3,10);
  assert.equal(refined.positions.length/3,9);
  const post=JSON.stringify(refined);
  await page.locator('#modelAtelierUndo').click();
  assert.equal(JSON.stringify((await parts()).find(x=>x.id===item.id).topologyMesh),nativeBefore);
  await page.locator('#modelAtelierRedo').click();
  refined=(await parts()).find(x=>x.id===item.id).topologyMesh;
  assert.equal(JSON.stringify(refined),post);
  await page.locator('#modelAtelierParts').selectOption(item.id);
  assert(await page.locator('#modelAtelierTopologyAuditTools').isVisible());
  await page.locator('#modelAtelierTopologyAuditCheck').click();
  assert.match(await page.locator('#modelAtelierTopologyAuditStats').textContent(),
     /0 nonmanifold edges · 0 inconsistent shared edges · 0 zero-area faces/);
  const full=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const exportedPath=await(await full).path();
  const saved=JSON.parse(await readFile(exportedPath,'utf8'));
  assert.equal(saved.model.parts.find(p=>p.id===item.id).topologyMesh.indices.length/3,10);
  await page.locator('#modelAtelierUndo').click();
  await page.locator('#modelAtelierImportFile').setInputFiles(exportedPath);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
     .find(p=>p.id==='test-winding-square')?.topologyMesh?.indices?.length===30);
  assert.equal(JSON.stringify((await parts()).find(p=>p.id===item.id).topologyMesh),post);
  assert.deepEqual((await parts()).slice(0,283),original);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1146_REAL_INDEXED_LOCAL_REFINE_STITCH_PREVIEW_UNDO_REDO_SAVE_RELOAD_PASS',
    device,2,10);
  await context.close();
 }
}finally{await browser.close();}
