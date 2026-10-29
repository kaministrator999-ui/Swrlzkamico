import assert from 'node:assert/strict';
import {chromium} from 'playwright';import {readFile} from 'node:fs/promises';
const base=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile] of [['desktop',{width:1280,height:900},false],
  ['android-touch',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(65000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const get=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const original=await get();assert.equal(original.length,283);
  const before=page.waitForEvent('download');await page.locator('#modelAtelierExport').click();
  const source=JSON.parse(await readFile(await(await before).path(),'utf8'));
  const item={id:'v1149-uv-square',name:'Broken-UV planar sheet',
   group:'Test geometry',kind:'topologyMesh',material:'matte',color:'#eec1a2',
   position:[0,3,1],rotation:[0,0,0],scale:[.5,.5,.5],
   topologyMesh:{positions:[0,0,0,2,0,0,2,1,0,0,1,0],
    uvs:[0,0,0,0,0,0,0,0],indices:[0,1,2,0,2,3]}};
  source.model.parts.push(item);
  await page.locator('#modelAtelierImportFile').setInputFiles({
   name:'broken-uv.json',mimeType:'application/json',
   buffer:Buffer.from(JSON.stringify(source))});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
   .some(p=>p.id==='v1149-uv-square'));
  await page.locator('#modelAtelierParts').selectOption(item.id);
  assert(await page.locator('#modelAtelierUVTools').isVisible());
  await page.locator('#modelAtelierUVInspect').click();
  assert.match(await page.locator('#modelAtelierUVStatus').textContent(),
   /2 zero-area UV triangles/);
  await page.locator('#modelAtelierUVPlane').selectOption('XZ');
  await page.locator('#modelAtelierUVPreview').click();
  assert.match(await page.locator('#modelAtelierStatus').textContent(),/unavailable/);
  assert.deepEqual((await get()).at(-1).topologyMesh.uvs,item.topologyMesh.uvs);
  await page.locator('#modelAtelierUVPlane').selectOption('XY');
  await page.locator('#modelAtelierUVPreview').click();
  assert.match(await page.locator('#modelAtelierUVStatus').textContent(),
   /collapsed faces 2 → 0/);
  assert.deepEqual((await get()).at(-1).topologyMesh.uvs,item.topologyMesh.uvs,
   'Preview should never mutate source UVs');
  await page.locator('#modelAtelierUVApply').click();
  let repaired=(await get()).at(-1).topologyMesh;
  assert.deepEqual(repaired.uvs,[0,0,1,0,1,1,0,1]);
  assert.deepEqual(repaired.indices,item.topologyMesh.indices);
  assert.deepEqual(repaired.positions,item.topologyMesh.positions);
  const savedMesh=JSON.stringify(repaired);
  await page.locator('#modelAtelierUndo').click();
  assert.deepEqual((await get()).at(-1).topologyMesh.uvs,item.topologyMesh.uvs);
  await page.locator('#modelAtelierRedo').click();
  assert.equal(JSON.stringify((await get()).at(-1).topologyMesh),savedMesh);
  const out=page.waitForEvent('download');await page.locator('#modelAtelierExport').click();
  const path=await(await out).path();
  assert.deepEqual(JSON.parse(await readFile(path,'utf8')).model.parts.at(-1).topologyMesh.uvs,
   [0,0,1,0,1,1,0,1]);
  await page.locator('#modelAtelierUndo').click();
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
   .find(p=>p.id==='v1149-uv-square')?.topologyMesh?.uvs?.[2]===1);
  const restored=await get();
  assert.equal(JSON.stringify(restored.at(-1).topologyMesh),savedMesh);
  assert.deepEqual(restored.slice(0,283),original);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1149_REAL_DESKTOP_ANDROID_UV_TRIANGLE_REPAIR_BOUNDED_PREVIEW_UNDO_RELOAD_PASS',device);
  await context.close();
 }
}finally{await browser.close();}
