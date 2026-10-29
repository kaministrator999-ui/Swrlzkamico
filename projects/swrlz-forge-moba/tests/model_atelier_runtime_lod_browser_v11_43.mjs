import assert from 'node:assert/strict';import {chromium} from 'playwright';import {readFile} from 'node:fs/promises';
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
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  assert.equal((await parts()).length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierLODRatio').fill('0.15');
  await page.locator('#modelAtelierLODPreview').click();
  const desc=await page.locator('#modelAtelierLODStats').textContent();
  assert.match(desc,/actual triangles/);
  const before=Number(desc.match(/^([\d,]+) →/)?.[1].replaceAll(',',''));
  const after=Number(desc.match(/→ ([\d,]+) actual triangles/)?.[1].replaceAll(',',''));
  assert(after<before&&after>1);
  const objD=page.waitForEvent('download');await page.locator('#modelAtelierLODOBJ').click();
  const obj=await objD;const objText=await readFile(await obj.path(),'utf8');
  assert.equal(objText.match(/^f /mg).length,after);
  assert.equal(objText.match(/^vt /mg).length,Number(desc.match(/· ([\d,]+) actual mesh vertices/)?.[1].replaceAll(',','')));
  await page.locator('#modelAtelierLODBake').click();
  let ps=await parts();assert.equal(ps.length,284);
  const copy=ps.find(x=>x.kind==='topologyMesh');assert(copy);
  assert.equal(copy.topologyMesh.indices.length/3,after);
  assert(ps.find(x=>x.id==='model-0001')?.headAnatomy,'Original head must remain unchanged');
  assert(await page.locator('#modelAtelierRuntimeLODTools').isVisible());
  await page.locator('#modelAtelierRuntimeLODRatio').fill('0.30');
  await page.locator('#modelAtelierRuntimeLODDistance').fill('4');
  await page.locator('#modelAtelierRuntimeLODGenerate').click();
  const withLOD=(await parts()).find(x=>x.id===copy.id);
  assert(withLOD.runtimeLOD?.enabled);
  assert.equal(withLOD.runtimeLOD.switchDistance,4);
  const lowCount=withLOD.runtimeLOD.low.indices.length/3;
  assert(lowCount<after&&lowCount>0);
  assert.equal(withLOD.topologyMesh.indices.length/3,after);
  assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_RUNTIME_LOD.report()))
    .meshes.find(x=>x.id===copy.id)?.active,'high',
    'Selected mesh must not degrade during editing');
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.waitForFunction(id=>window.SWYRL_ENGINE_RUNTIME_LOD.report()
    .meshes.find(x=>x.id===id)?.active==='low',copy.id);
  let display=await page.evaluate(()=>window.SWYRL_ENGINE_RUNTIME_LOD.report());
  assert.equal(display.meshes.find(x=>x.id===copy.id).triangles,lowCount);
  // A farther transition prevents reduction at the same camera distance.
  await page.locator('#modelAtelierParts').selectOption(copy.id);
  await page.locator('#modelAtelierRuntimeLODDistance').fill('120');
  await page.locator('#modelAtelierRuntimeLODDistance').dispatchEvent('change');
  assert.equal((await parts()).find(x=>x.id===copy.id).runtimeLOD.switchDistance,120);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.waitForFunction(id=>window.SWYRL_ENGINE_RUNTIME_LOD.report()
    .meshes.find(x=>x.id===id)?.active==='high',copy.id);
  display=await page.evaluate(()=>window.SWYRL_ENGINE_RUNTIME_LOD.report());
  assert.equal(display.meshes.find(x=>x.id===copy.id).triangles,after);
  await page.locator('#modelAtelierParts').selectOption(copy.id);
  await page.locator('#modelAtelierRuntimeLODDistance').fill('4');
  await page.locator('#modelAtelierRuntimeLODDistance').dispatchEvent('change');
  assert.equal((await parts()).find(x=>x.id===copy.id).runtimeLOD.switchDistance,4);
    const dl=page.waitForEvent('download');await page.locator('#modelAtelierExport').click();
  const path=await(await dl).path(),json=JSON.parse(await readFile(path,'utf8'));
  assert.equal(json.model.parts.find(x=>x.kind==='topologyMesh')?.topologyMesh.indices.length/3,after);
  assert.equal(json.model.parts.find(x=>x.kind==='topologyMesh').runtimeLOD.low.indices.length/3,lowCount);
  await page.locator('#modelAtelierUndo').click();
  ps=await parts();assert.equal(ps.find(x=>x.id===copy.id).runtimeLOD.switchDistance,120);
  await page.locator('#modelAtelierUndo').click();
  ps=await parts();assert.equal(ps.find(x=>x.id===copy.id).runtimeLOD.switchDistance,4);
  await page.locator('#modelAtelierUndo').click();
  ps=await parts();assert.equal(ps.find(x=>x.id===copy.id).runtimeLOD,undefined);
  await page.locator('#modelAtelierUndo').click();
  ps=await parts();assert.equal(ps.length,283);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.length===284);
  ps=await parts();assert.equal(ps.find(x=>x.kind==='topologyMesh')?.topologyMesh.indices.length/3,after);
  assert.equal(ps.find(x=>x.kind==='topologyMesh')?.runtimeLOD.low.indices.length/3,lowCount);
  assert.equal(ps.find(x=>x.id==='model-0001')?.headAnatomy!==undefined,true);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1143_ACTUAL_CAMERA_SWITCHED_LOW_POLY_HEAD_NATIVE_LOD_UNDO_RELOAD_PASS',device,before,after);
  await context.close();
 }
}finally{await browser.close();}
