import assert from 'node:assert/strict';
import {chromium} from 'playwright';import {readFile} from 'node:fs/promises';
const base=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile] of [
  ['desktop',{width:1280,height:900},false],
  ['android-touch',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(65000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const original=await parts();assert.equal(original.length,283);
  const dl=page.waitForEvent('download');await page.locator('#modelAtelierExport').click();
  const json=JSON.parse(await readFile(await(await dl).path(),'utf8'));
  const testPart={
   id:'v1148-safe-pyramid',name:'Real boundary repair test',
   group:'Test geometry',kind:'topologyMesh',
   position:[0,3,1],rotation:[0,0,0],scale:[.5,.5,.5],
   material:'matte',color:'#88bbdd',
   topologyMesh:{
    positions:[0,0,0,1,0,0,1,1,0,0,1,0,.5,.5,1],
    uvs:[0,0,1,0,1,1,0,1,.5,.5],
    indices:[0,1,4,1,2,4,2,3,4,3,0,4]
   }
  };
  json.model.parts.push(testPart);
  await page.locator('#modelAtelierImportFile').setInputFiles({
   name:'v1148-open-boundary.json',mimeType:'application/json',
   buffer:Buffer.from(JSON.stringify(json))});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.length===284);
  await page.locator('#modelAtelierParts').selectOption(testPart.id);
  assert(await page.locator('#modelAtelierBoundaryCapTools').isVisible());
  const originalMesh=JSON.stringify(testPart.topologyMesh);
  await page.locator('#modelAtelierBoundaryCapVertex').fill('4');
  await page.locator('#modelAtelierBoundaryCapPreview').click();
  assert.match(await page.locator('#modelAtelierStatus').textContent(),/not on a boundary/);
  assert.equal(JSON.stringify((await parts()).at(-1).topologyMesh),originalMesh);
  await page.locator('#modelAtelierBoundaryCapVertex').fill('0');
  await page.locator('#modelAtelierBoundaryCapPreview').click();
  assert.match(await page.locator('#modelAtelierBoundaryCapStatus').textContent(),
    /Boundary loop 4 vertices, \+2 real triangles. Remaining open edges: 0/);
  assert.equal(JSON.stringify((await parts()).at(-1).topologyMesh),originalMesh,
    'Preview may not alter saved topology');
  await page.locator('#modelAtelierBoundaryCapApply').click();
  let sealed=(await parts()).at(-1).topologyMesh;
  assert.equal(sealed.indices.length,18);
  assert.equal(sealed.positions.length,15);
  assert.equal(sealed.uvs.length,10);
  const savedMesh=JSON.stringify(sealed);
  await page.locator('#modelAtelierTopologyAuditCheck').click();
  assert.match(await page.locator('#modelAtelierTopologyAuditStats').textContent(),
    /0 open boundary edges · 0 nonmanifold edges · 0 inconsistent shared edges · 0 zero-area faces/);
  await page.locator('#modelAtelierUndo').click();
  assert.equal(JSON.stringify((await parts()).at(-1).topologyMesh),originalMesh);
  await page.locator('#modelAtelierRedo').click();
  assert.equal(JSON.stringify((await parts()).at(-1).topologyMesh),savedMesh);
  const save=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await save).path();
  const exported=JSON.parse(await readFile(path,'utf8'));
  assert.equal(exported.model.parts.at(-1).topologyMesh.indices.length,18);
  await page.locator('#modelAtelierUndo').click();
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
    .at(-1)?.topologyMesh?.indices?.length===18);
  const restored=await parts();
  assert.equal(JSON.stringify(restored.at(-1).topologyMesh),savedMesh);
  assert.deepEqual(restored.slice(0,283),original);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1148_REAL_DESKTOP_ANDROID_PLANAR_HOLE_CAP_AUDIT_UNDO_NATIVE_SAVE_RELOAD_PASS',device);
  await context.close();
 }
}finally{await browser.close();}
