import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const url=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl',
 '--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'
]});
try{
 for(const [device,viewport,mobile] of [
  ['desktop',{width:1280,height:860},false],
  ['android',{width:412,height:915},true]
 ]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(90000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const initial=await parts();assert.equal(initial.length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  // Unlike local-unit strokes, pixel sizing needs its center inside the
  // camera projection. Frame the actual selected anatomical head first.
  await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('front'));
  await page.locator('#modelAtelierFrameSelected').click();
  for(const [id,v] of [['Center0','0'],['Center1','0'],['Center2','0']])
   await page.locator('#modelAtelierSculptBrush'+id).fill(v);
  await page.locator('#modelAtelierSculptBrushRadiusUnits').selectOption('screen');
  const local=page.locator('#modelAtelierSculptBrushRadius');
  assert(!(await local.isVisible()),'world input must hide when using pixel sizing');
  const screen=page.locator('#modelAtelierSculptBrushRadiusScreen');
  assert(await screen.isVisible(),'mobile pixel input must be usable');
  await screen.fill('18');
  await page.locator('#modelAtelierSculptBrushSelectRadiusScreen').fill('22');
  await page.locator('#modelAtelierSculptBrushAmount').fill('.04');
  await page.locator('#modelAtelierSculptBrushApply').click();
  const changed=(await parts()).find(p=>p.id==='model-0001');
  if(!changed.sculptBrushes?.length){
   const info=await page.evaluate(()=>({
    statuses:[...document.querySelectorAll('#modelAtelierPanel [role="status"], #modelAtelierPanel output')]
     .map(e=>({id:e.id,text:e.textContent?.slice(0,350)})),
    sizing:[...document.querySelectorAll('#modelAtelierSculptBrush input')]
     .filter(e=>/Radius|Center|Axis/i.test(e.id)).map(e=>[e.id,e.value]),
    canvas:(()=>{const e=document.querySelector('#modelAtelierViewport canvas'),r=e?.getBoundingClientRect();
     return r&&{width:r.width,height:r.height,top:r.top,left:r.left};})()
   }));
   console.error('V1152_PIXEL_BRUSH_DIAGNOSTIC',device,JSON.stringify(info));
  }
  assert.equal(changed.sculptBrushes?.length,1,
   'screen-space button must commit one native stroke at visible picked center');
  const saved=changed.sculptBrushes[0];
  assert(Number.isFinite(saved.radius)&&saved.radius>=.03&&saved.radius<=2.5);
  assert(Number.isFinite(saved.selectionRadius)&&saved.selectionRadius>=.03&&saved.selectionRadius<=2.5);
  assert(saved.selectionRadius>saved.radius);
  assert.equal(saved.screenPixels,undefined,'CSS pixels are never stored as runtime brush geometry');
  assert.deepEqual(changed.headAnatomy,initial.find(p=>p.id==='model-0001').headAnatomy);
  const downloading=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await downloading).path();
  const exported=JSON.parse(await readFile(path,'utf8'));
  assert.deepEqual(exported.model.parts.find(p=>p.id==='model-0001').sculptBrushes[0],saved);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await parts()).find(p=>p.id==='model-0001').sculptBrushes?.length||0,0);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
   .find(p=>p.id==='model-0001')?.sculptBrushes?.length===1);
  assert.deepEqual((await parts()).find(p=>p.id==='model-0001').sculptBrushes[0],saved);
  assert.deepEqual(errors,[]);
  console.log('V1152_SCREEN_PIXEL_RADIUS_DESKTOP_ANDROID_NATIVE_APPLY_UNDO_IMPORT_PASS',device);
  await context.close();
 }
}finally{await browser.close();}
