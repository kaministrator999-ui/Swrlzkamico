import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader',
 '--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile]of[['desktop',{width:1280,height:900},false],
  ['android',{width:412,height:915},true]]){
  const ctx=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await ctx.newPage();page.setDefaultTimeout(90000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const initial=await parts();assert.equal(initial.length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierLODProtectUV').check();
  await page.locator('#modelAtelierLODRatio').fill('.12');
  await page.locator('#modelAtelierLODPreview').click();
  const desc=await page.locator('#modelAtelierLODStats').textContent();
  assert.match(desc,/strict 32-bin UV-island separation/);
  const match=desc.match(/→ ([\d,]+) actual triangles/);
  assert(match,'must report real reduced source triangles');
  const tris=Number(match[1].replaceAll(',',''));
  assert(tris>10&&tris<49000);
  const dlObj=page.waitForEvent('download');await page.locator('#modelAtelierLODOBJ').click();
  const obj=await readFile(await(await dlObj).path(),'utf8');
  assert.match(obj,/# strict UV-island guard enabled/);
  assert.equal(obj.match(/^f /mg).length,tris);
  const originalHead=JSON.stringify(initial.find(p=>p.id==='model-0001'));
  await page.locator('#modelAtelierLODBake').click();
  const latest=await parts();
  assert.equal(latest.length,284,'strict UV safety LOD bakes separate topology copy');
  const copy=latest.find(p=>p.kind==='topologyMesh');assert(copy);
  assert.equal(copy.topologyMesh.indices.length/3,tris);
  assert.equal(JSON.stringify(latest.find(p=>p.id==='model-0001')),originalHead);
  const downloading=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await downloading).path();
  const saved=JSON.parse(await readFile(path,'utf8'));
  assert.equal(saved.model.parts.find(p=>p.kind==='topologyMesh').topologyMesh.indices.length/3,tris);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await parts()).length,283);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.length===284);
  assert.equal((await parts()).find(p=>p.kind==='topologyMesh').topologyMesh.indices.length/3,tris);
  assert.deepEqual(errors,[]);
  console.log('V1158_STRICT_UV_ISLAND_NATIVE_DESKTOP_ANDROID_LOD_OBJ_UNDO_SAVE_PASS',device,tris);
  await ctx.close();
 }
}finally{await browser.close();}
