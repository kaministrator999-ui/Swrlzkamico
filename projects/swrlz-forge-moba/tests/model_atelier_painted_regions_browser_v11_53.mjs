import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile]of[['desktop',{width:1280,height:900},false],
  ['android',{width:412,height:915},true]]){
  const ctx=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await ctx.newPage();page.setDefaultTimeout(70000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  assert.equal((await parts()).length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierLassoStart').click();
  const point=async(x,y,z)=>{
   for(let i=0;i<3;i++)await page.locator('#modelAtelierLassoPinXYZ'+i).fill(String([x,y,z][i]));
   await page.locator('#modelAtelierLassoAddXYZ').click();
  };
  await point(-.23,-.24,.85);await point(.23,-.24,.85);await point(0,.18,.92);
  await page.locator('#modelAtelierLassoFinish').click();
  let head=(await parts()).find(p=>p.id==='model-0001');
  assert.equal(head.sculptLassos?.length,1);
  const pins=JSON.stringify(head.sculptLassos[0].pins);
  await page.locator('#modelAtelierLassoPaintMode').selectOption('add');
  await page.locator('#modelAtelierLassoPaintRadius').fill('.10');
  await page.locator('#modelAtelierLassoPaintXYZ0').fill('0');
  await page.locator('#modelAtelierLassoPaintXYZ1').fill('0');
  await page.locator('#modelAtelierLassoPaintXYZ2').fill('.90');
  await page.locator('#modelAtelierLassoPaintAtXYZ').click();
  head=(await parts()).find(p=>p.id==='model-0001');
  assert.equal(head.sculptLassos[0].paintDabs?.length,1,'must save additive region paint');
  assert.equal(head.sculptLassos[0].paintDabs[0].op,'add');
  assert.equal(JSON.stringify(head.sculptLassos[0].pins),pins,'painting must not move pins');
  await page.locator('#modelAtelierLassoPaintMode').selectOption('subtract');
  await page.locator('#modelAtelierLassoPaintAtXYZ').click();
  head=(await parts()).find(p=>p.id==='model-0001');
  assert.equal(head.sculptLassos[0].paintDabs?.length,2);
  assert.equal(head.sculptLassos[0].paintDabs[1].op,'subtract');
  const snap=JSON.parse(JSON.stringify(head.sculptLassos[0].paintDabs));
  const dl=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await dl).path(),json=JSON.parse(await readFile(path,'utf8'));
  assert.deepEqual(json.model.parts.find(p=>p.id==='model-0001').sculptLassos[0].paintDabs,snap);
  await page.locator('#modelAtelierUndo').click();
  head=(await parts()).find(p=>p.id==='model-0001');
  assert.equal(head.sculptLassos[0].paintDabs.length,1,'paint undo must be atomic');
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project
   .modelAtelier.parts.find(p=>p.id==='model-0001')?.sculptLassos?.[0]?.paintDabs?.length===2);
  head=(await parts()).find(p=>p.id==='model-0001');
  assert.deepEqual(head.sculptLassos[0].paintDabs,snap);
  // Native import intentionally clears selection; reveal the model inspector again.
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierLassoPaintClear').click();
  assert.equal((await parts()).find(p=>p.id==='model-0001').sculptLassos[0].paintDabs.length,0);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1153_PAINT_LASSO_ADD_ERASE_REAL_BROWSER_NATIVE_SAVE_UNDO_RELOAD_PASS',device);
  await ctx.close();
 }
}finally{await browser.close();}
