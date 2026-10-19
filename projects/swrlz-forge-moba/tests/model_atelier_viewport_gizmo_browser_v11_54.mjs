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
  const page=await ctx.newPage();page.setDefaultTimeout(90000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  assert.equal((await parts()).length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('front'));
  await page.locator('#modelAtelierFrameSelected').click();
  // Nearby head vertices keep a 55° group rotation within the native ±0.5 delta cap.
  await page.locator('#modelAtelierSculptBrushIndices').fill('12400,12410');
  await page.locator('#modelAtelierSculptBrushIndicesApply').click();
  await page.locator('#modelAtelierGroupViewportMode').selectOption('rotate');
  await page.locator('#modelAtelierGroupViewportAxis').selectOption('z');
  await page.locator('#modelAtelierGroupViewportAngleSnap').fill('5');
  const canvas=page.locator('#modelAtelierViewport canvas');
  const beforeBox=await canvas.boundingBox();
  let marker=await page.locator('#modelAtelierSculptBrushVertexInfo').evaluate(el=>({
   x:Number(el.dataset.gizmoX),y:Number(el.dataset.gizmoY),text:el.textContent
  }));
  await canvas.scrollIntoViewIfNeeded();
  const afterBox=await canvas.boundingBox();
  if(beforeBox&&afterBox){
   marker.x+=afterBox.x-beforeBox.x;marker.y+=afterBox.y-beforeBox.y;
  }
  const box=await canvas.boundingBox();
  assert(box&&marker.x>=box.x&&marker.x<=box.x+box.width);
  assert(marker.y>box.y+20&&marker.y<box.y+box.height-20);
  const sx=marker.x+20,sy=marker.y;
  const target=await page.evaluate(({x,y})=>{
   const el=document.elementFromPoint(x,y);
   return {tag:el?.tagName,id:el?.id,parent:el?.parentElement?.id};
  },{x:sx,y:sy});
  console.log('V1154_HANDLE_START_TARGET',device,{sx,sy,marker,target});
  if(mobile){
   const session=await ctx.newCDPSession(page);
   await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:sx,y:sy,id:7}]});
   for(let i=1;i<=8;i++)await session.send('Input.dispatchTouchEvent',{
    type:'touchMove',touchPoints:[{x:sx,y:sy-3*i,id:7}]
   });
   await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  }else{
   await page.mouse.move(sx,sy);await page.mouse.down();
   await page.mouse.move(sx,sy-30,{steps:9});await page.mouse.up();
  }
  const part=(await parts()).find(x=>x.id==='model-0001');
  if(!part.sculptVertexEdits?.length){
   const dbg=await page.evaluate(()=>({
    status:document.querySelector('#modelAtelierStatus')?.textContent,
    selected:document.querySelector('#modelAtelierSculptBrushVertexInfo')?.textContent,
    mode:document.querySelector('#modelAtelierGroupViewportMode')?.value,
    axis:document.querySelector('#modelAtelierGroupViewportAxis')?.value
   }));
   console.error('V1154_HANDLE_REJECTED',device,JSON.stringify(dbg));
  }
  assert.equal(part.sculptVertexEdits?.length,1,'viewport rotate must save native vertex edit');
  const edit=part.sculptVertexEdits[0];
  assert(edit.moves?.some(m=>m.some(n=>Math.abs(n)>.00001)),'rotation must move real vertices');
  assert(!part.refinementLayers?.length);
  const dl=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await dl).path();
  const json=JSON.parse(await readFile(path,'utf8'));
  assert.deepEqual(json.model.parts.find(p=>p.id==='model-0001').sculptVertexEdits[0],edit);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await parts()).find(p=>p.id==='model-0001').sculptVertexEdits?.length||0,0);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
   .find(p=>p.id==='model-0001')?.sculptVertexEdits?.length===1);
  assert.deepEqual((await parts()).find(p=>p.id==='model-0001').sculptVertexEdits[0],edit);
  assert.deepEqual(errors,[]);
  console.log('V1154_REAL_VIEWPORT_ROTATION_DESKTOP_ANDROID_SAVE_UNDO_RELOAD_PASS',device);
  await ctx.close();
 }
}finally{await browser.close();}
