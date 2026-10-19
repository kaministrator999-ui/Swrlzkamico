import assert from 'node:assert/strict';
import {chromium} from 'playwright';import {readFile} from 'node:fs/promises';
const base=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile] of [
  ['desktop',{width:1280,height:900},false],['android-touch',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(65000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const get=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const original=await get();assert.equal(original.length,283);
  const dl=page.waitForEvent('download');await page.locator('#modelAtelierExport').click();
  const exported=JSON.parse(await readFile(await(await dl).path(),'utf8'));
  const item={id:'v1150-face-extrude',name:'Manual indexed tetra face cap',
   group:'Test geometry',kind:'topologyMesh',material:'matte',color:'#f5b56f',
   position:[0,3,1],rotation:[0,0,0],scale:[.5,.5,.5],
   topologyMesh:{positions:[0,0,0,1,0,0,0,1,0,0,0,1],
    uvs:[0,0,1,0,0,1,.5,.5],
    indices:[0,2,1,0,1,3,1,2,3,2,0,3]}};
  exported.model.parts.push(item);
  await page.locator('#modelAtelierImportFile').setInputFiles({
   name:'editable-face.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(exported))});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.some(p=>p.id==='v1150-face-extrude'));
  await page.locator('#modelAtelierParts').selectOption(item.id);
  assert(await page.locator('#modelAtelierFaceExtrudeTools').isVisible());
  await page.locator('#modelAtelierFaceExtrudeFace').fill('999');
  await page.locator('#modelAtelierFaceExtrudePreview').click();
  assert.match(await page.locator('#modelAtelierStatus').textContent(),/rejected/);
  await page.locator('#modelAtelierFaceExtrudeFace').fill('0');
  await page.locator('#modelAtelierFaceExtrudeDepth').fill('.05');
  await page.locator('#modelAtelierFaceExtrudePreview').click();
  assert.match(await page.locator('#modelAtelierFaceExtrudeStatus').textContent(),
   /4 → 10 real triangles, 4 → 7 vertices/);
  assert.deepEqual((await get()).at(-1).topologyMesh,item.topologyMesh,
   'Never mutate source during preview');
  await page.locator('#modelAtelierFaceExtrudeApply').click();
  let edited=(await get()).at(-1).topologyMesh;
  assert.equal(edited.indices.length/3,10);
  assert.equal(edited.positions.length/3,7);
  assert.equal(edited.uvs.length/2,7);
  const committed=JSON.stringify(edited);
  await page.locator('#modelAtelierTopologyAuditCheck').click();
  assert.match(await page.locator('#modelAtelierTopologyAuditStats').textContent(),
   /0 open boundary edges · 0 nonmanifold edges · 0 inconsistent shared edges · 0 zero-area faces/);
  await page.locator('#modelAtelierUndo').click();
  assert.deepEqual((await get()).at(-1).topologyMesh,item.topologyMesh);
  await page.locator('#modelAtelierRedo').click();
  assert.equal(JSON.stringify((await get()).at(-1).topologyMesh),committed);
  const save=page.waitForEvent('download');await page.locator('#modelAtelierExport').click();
  const path=await(await save).path(),native=JSON.parse(await readFile(path,'utf8'));
  assert.equal(native.model.parts.at(-1).topologyMesh.indices.length/3,10);
  await page.locator('#modelAtelierUndo').click();
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
   .find(p=>p.id==='v1150-face-extrude')?.topologyMesh?.indices?.length===30);
  const restored=await get();
  assert.equal(JSON.stringify(restored.at(-1).topologyMesh),committed);
  assert.deepEqual(restored.slice(0,283),original);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1150_DESKTOP_ANDROID_REAL_SIGNED_FACE_WALLS_TOPOLOGY_UNDO_REDO_NATIVE_RELOAD_PASS',device);
  await context.close();
 }
}finally{await browser.close();}
