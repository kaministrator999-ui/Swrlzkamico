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
      uvs:[0,0,1,0,1,1,0,1],indices:[0,1,2,0,3,2]}
  };
  exported.model.parts.push(item);
  await page.locator('#modelAtelierImportFile').setInputFiles({
   name:'topology-test.json',mimeType:'application/json',
   buffer:Buffer.from(JSON.stringify(exported))
  });
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.length===284);
  await page.locator('#modelAtelierParts').selectOption(item.id);
  assert(await page.locator('#modelAtelierTopologyAuditTools').isVisible());
  await page.locator('#modelAtelierTopologyAuditCheck').click();
  assert.match(await page.locator('#modelAtelierTopologyAuditStats').textContent(),
    /4 open boundary edges · 0 nonmanifold edges · 1 inconsistent shared edges/);
  await page.locator('#modelAtelierTopologyAuditRepair').click();
  let current=(await parts()).find(x=>x.id===item.id);
  assert.notDeepEqual(current.topologyMesh.indices,item.topologyMesh.indices);
  assert.deepEqual(current.topologyMesh.uvs,item.topologyMesh.uvs);
  assert.match(await page.locator('#modelAtelierTopologyAuditStats').textContent(),
    /0 inconsistent shared edges/);
  const valid=JSON.stringify(current.topologyMesh);
  await page.locator('#modelAtelierUndo').click();
  current=(await parts()).find(x=>x.id===item.id);
  assert.deepEqual(current.topologyMesh.indices,item.topologyMesh.indices);
  await page.locator('#modelAtelierRedo').click();
  current=(await parts()).find(x=>x.id===item.id);
  assert.equal(JSON.stringify(current.topologyMesh),valid);
  const saved=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const json=await(await saved).path();
  await page.locator('#modelAtelierUndo').click();
  await page.locator('#modelAtelierImportFile').setInputFiles(json);
  await page.waitForFunction(expected=>JSON.stringify(
    window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
    .find(p=>p.id==='test-winding-square')?.topologyMesh)===expected,valid);
  const restored=await parts();
  assert.equal(JSON.stringify(restored.find(x=>x.id===item.id).topologyMesh),valid);
  assert.deepEqual(restored.slice(0,283),original);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1144_REAL_DESKTOP_ANDROID_FACE_WINDING_DIAG_REPAIR_UNDO_REDO_SAVED_PASS',device);
  await context.close();
 }
}finally{await browser.close();}
