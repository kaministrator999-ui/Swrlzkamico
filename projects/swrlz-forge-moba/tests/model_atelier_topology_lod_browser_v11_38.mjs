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
  const dl=page.waitForEvent('download');await page.locator('#modelAtelierExport').click();
  const path=await(await dl).path(),json=JSON.parse(await readFile(path,'utf8'));
  assert.equal(json.model.parts.find(x=>x.kind==='topologyMesh')?.topologyMesh.indices.length/3,after);
  await page.locator('#modelAtelierUndo').click();
  ps=await parts();assert.equal(ps.length,283);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.length===284);
  ps=await parts();assert.equal(ps.find(x=>x.kind==='topologyMesh')?.topologyMesh.indices.length/3,after);
  assert.equal(ps.find(x=>x.id==='model-0001')?.headAnatomy!==undefined,true);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1138_REAL_HEAD_BAKED_INDEXED_LOD_OBJ_UV_SAVE_UNDO_ANDROID_PASS',device,before,after);
  await context.close();
 }
}finally{await browser.close();}
