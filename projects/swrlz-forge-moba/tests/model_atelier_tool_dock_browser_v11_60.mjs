import assert from 'node:assert/strict';
import {chromium} from 'playwright';

const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl',
 '--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'
]});
try{
 const layouts=[
 ['desktop',{width:1280,height:850},false],
 ['android',{width:412,height:915},true]
];
for(const [label,viewport,isMobile] of (process.env.SWYRL_DOCK_DESKTOP_ONLY==='1'?layouts.slice(0,1):layouts)){
  const context=await browser.newContext({viewport,isMobile,hasTouch:isMobile,acceptDownloads:true});
  const page=await context.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  page.setDefaultTimeout(60000);
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  const canvas=page.locator('#modelAtelierPanel:not([hidden]) canvas');
  await canvas.waitFor();
  const panel=page.locator('#modelAtelierPanel');
  const inspector=page.locator('#modelAtelierInspectorDock');
  const rail=page.locator('#modelAtelierToolRail');
  assert(await rail.isVisible(),'vertical tool shortcuts must always be discoverable');
  const scene=await canvas.boundingBox();
  assert(scene&&scene.height>viewport.height*.57,'scene must have substantial room');
  assert.equal(await inspector.isVisible(),true,'floating tools are initially discoverable and remain dismissible');
  if(!(await inspector.isVisible()))await rail.getByRole('button',{name:'Open Meshes editing tools'}).click();
  assert(await inspector.isVisible());
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  assert(await page.locator('#modelAtelierSculptBrush').isVisible(),'native sculpt controls must remain available');
  await rail.getByRole('button',{name:'Open Sculpt editing tools'}).click();
  assert(await page.locator('#modelAtelierSculptBrush').isVisible());
  const selected=await page.locator('#modelAtelierParts').inputValue();
  assert.equal(selected,'model-0001');
  const dragHandle=page.locator('.atelier-tool-handle');
  const before=await inspector.boundingBox();
  const box=await dragHandle.boundingBox();
  assert(before&&box);
  const dragX=box.x+55,dragY=box.y+15;
  await page.mouse.move(dragX,dragY);
  await page.mouse.down();
  await page.mouse.move(dragX-20,dragY+34,{steps:6});
  await page.mouse.up();
  const after=await inspector.boundingBox();
  assert(after&&Math.abs(after.y-before.y)>10,'tool panel must move after handle drag');
  await dragHandle.getByRole('button',{name:'Hide editing tools'}).click();
  assert(!(await inspector.isVisible()),'hide must restore unobstructed viewport');
  assert(await canvas.isVisible());
  await rail.getByRole('button',{name:'Open Sculpt editing tools'}).click();
  assert(await inspector.isVisible(),'dock can reopen without regenerating native tools');
  await page.locator('#modelAtelierSculptBrushRadius').fill('.45');
  assert.equal(await page.locator('#modelAtelierSculptBrushRadius').inputValue(),'.45');
  assert.equal(await page.locator('#modelAtelierPartCount').textContent().then(s=>s.includes('283')),true);
  assert.deepEqual(errors,[],'no uncaught editor exceptions');
  console.log('ATELIER_V1160_DOCK_PREVIEW_PASS',label,{height:scene.height,dragDeltaY:after.y-before.y});
  await context.close();
 }
}finally{await browser.close();}
