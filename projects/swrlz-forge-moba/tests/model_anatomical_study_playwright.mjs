import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile} from 'node:fs/promises';
const url=(process.env.SWYRL_ANATOMY_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
await mkdir('anatomical-study-evidence',{recursive:true});
try{
 for(const [name,size,mobile] of [['desktop',{width:1440,height:1000},false],['mobile',{width:412,height:915},true]]){
  const ctx=await browser.newContext({viewport:size,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await ctx.newPage(),errors=[];page.setDefaultTimeout(60000);
  page.on('pageerror',err=>errors.push(err.message));
  await page.goto(url+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const get=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const parts=await get();assert.equal(parts.length,283,'New candidate must load all 283 editable parts');
  let head=parts.find(p=>p.id==='model-0001');
  assert(head.anatomyStudy,'Anatomical head parameters lost from canonical native project');
  assert(parts.find(p=>p.id==='left-ear').earStudy,'Anatomical ear missing');
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  assert(await page.locator('#modelAtelierAnatomyHead').isVisible());
  const original=head.anatomyStudy.jaw;
  await page.locator('#modelAtelierAnatomyjaw').fill('0.74');
  await page.locator('#modelAtelierAnatomyHeadApply').click();
  head=(await get()).find(p=>p.id==='model-0001');
  assert.equal(head.anatomyStudy.jaw,.74,'Inspector Apply did not save head geometry');
  await page.locator('#modelAtelierUndo').click();
  head=(await get()).find(p=>p.id==='model-0001');
  assert.equal(head.anatomyStudy.jaw,original,'Whole-model Undo lost head morphology');
  await page.locator('#modelAtelierRedo').click();
  head=(await get()).find(p=>p.id==='model-0001');
  assert.equal(head.anatomyStudy.jaw,.74,'Redo did not restore morphology');
  await page.locator('#modelAtelierParts').selectOption('left-ear');
  assert(await page.locator('#modelAtelierAnatomyEar').isVisible());
  await page.locator('#modelAtelierAnatomyconcha').fill('0.80');
  await page.locator('#modelAtelierAnatomyEarApply').click();
  assert.equal((await get()).find(p=>p.id==='left-ear').earStudy.concha,.8);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('front'));
  await page.locator('#modelAtelierFrameSelected').click();
  await page.screenshot({path:'anatomical-study-evidence/'+name+'-front.png'});
  await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('right'));
  await page.locator('#modelAtelierFrameSelected').click();
  await page.screenshot({path:'anatomical-study-evidence/'+name+'-profile.png'});
  await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('three-quarter'));
  await page.locator('#modelAtelierFrameSelected').click();
  await page.screenshot({path:'anatomical-study-evidence/'+name+'-three-quarter.png'});
  const downloaded=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const download=await downloaded,file=await download.path();
  const saved=JSON.parse(await readFile(file,'utf8'));
  assert.equal(saved.model.parts.find(p=>p.id==='model-0001').anatomyStudy.jaw,.74);
  assert.equal(saved.model.parts.find(p=>p.id==='left-ear').earStudy.concha,.8);
  assert.equal(saved.schema,'swyrl-model-atelier-v1');
  await page.evaluate(()=>{
    window.__anatomyImportChangeObserved=false;
    document.getElementById('modelAtelierImportFile').addEventListener('change',()=>{window.__anatomyImportChangeObserved=true;},{once:true});
  });
  await page.locator('#modelAtelierImportFile').setInputFiles(file);
  await page.waitForFunction(()=>window.__anatomyImportChangeObserved,null,{timeout:8000});
  await page.waitForTimeout(3500);
  const diagnostic=await page.evaluate(()=>({
    status:document.getElementById('modelAtelierStatus')?.textContent||'',
    fileCount:document.getElementById('modelAtelierImportFile')?.files?.length??-1,
    parts:window.SWYRL_ENGINE_AGENT.inspectScene()?.project?.modelAtelier?.parts?.length??-1,
    head:window.SWYRL_ENGINE_AGENT.inspectScene()?.project?.modelAtelier?.parts?.find(p=>p.id==='model-0001')?.anatomyStudy?.jaw
  }));
  console.log('ANATOMICAL_IMPORT_DIAGNOSTIC',JSON.stringify(diagnostic),'PAGE_ERRORS',JSON.stringify(errors));
  assert.match(diagnostic.status,/^Validated model, poses and independent attachments imported\./,'Round-trip import result: '+JSON.stringify(diagnostic));
  assert.equal((await get()).find(p=>p.id==='model-0001').anatomyStudy.jaw,.74,'Native JSON round-trip changed anatomical head');
  assert.equal((await get()).find(p=>p.id==='left-ear').earStudy.concha,.8,'Native JSON round-trip changed the ear');
  assert.equal(errors.length,0,'Browser runtime errors: '+errors.join(' | '));
  console.log('ANATOMICAL_STUDY_NATIVE_EDITOR_PASS',name,saved.model.parts.length);
  await ctx.close();
 }
}finally{await browser.close();}
