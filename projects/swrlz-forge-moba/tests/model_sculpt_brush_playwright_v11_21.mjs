import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile] of [['desktop',{width:1366,height:900},false],['mobile',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(60000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  const initial=await parts(),head=initial.find(x=>x.id==='model-0001');
  assert.equal(initial.length,283);assert(head.headAnatomy?.sections?.length>=7,'Must be Codex section-built v11.20 head');
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  assert(await page.locator('#modelAtelierSculptBrush').isVisible());
  const originalSections=JSON.stringify(head.headAnatomy);
  // Test persisted brush radius, taper, plateau, half-sphere and levelling.
  await page.locator('#modelAtelierSculptBrushRadius').fill('.4');
  await page.locator('#modelAtelierSculptBrushAmount').fill('.05');
  await page.locator('#modelAtelierSculptBrushPlateau').fill('.6');
  await page.locator('#modelAtelierSculptBrushTaper').fill('.8');
  await page.locator('#modelAtelierSculptBrushLevel').check();
  await page.locator('#modelAtelierSculptBrushHalf').check();
  await page.locator('#modelAtelierSculptBrushApply').click();
  let changed=(await parts()).find(p=>p.id==='model-0001');
  assert.equal(changed.sculptBrushes?.length,1);
  assert.equal(changed.sculptBrushes[0].plateau,.6);
  assert.equal(changed.sculptBrushes[0].taper,.8);
  assert.equal(changed.sculptBrushes[0].level,true);
  assert.equal(JSON.stringify(changed.headAnatomy),originalSections,'Must not overwrite Codex head sections');
  // Verify grid sampling is editable, reversible and distinct from face sculpt.
  await page.locator('#modelAtelierSculptBrushGridU').fill('128');
  await page.locator('#modelAtelierSculptBrushGridV').fill('80');
  await page.locator('#modelAtelierSculptBrushGridApply').click();
  changed=(await parts()).find(p=>p.id==='model-0001');
  assert.deepEqual(changed.meshDensity,{u:128,v:80});
  await page.locator('#modelAtelierUndo').click();
  changed=(await parts()).find(p=>p.id==='model-0001');
  assert.deepEqual(changed.meshDensity,{u:192,v:128});
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('front'));
  await page.locator('#modelAtelierFrameSelected').click();
  await page.locator('#modelAtelierSculptBrushIndices').fill('12400');
  await page.locator('#modelAtelierSculptBrushIndicesApply').click();
  const canvas=page.locator('#modelAtelierViewport canvas');
  const beforeBox=await canvas.boundingBox();
  let marker=await page.locator('#modelAtelierSculptBrushVertexInfo').evaluate(el=>({
   x:Number(el.dataset.gizmoX),y:Number(el.dataset.gizmoY),label:el.textContent
  }));
  // The mobile inspector click scrolls the *page* to the bottom. Return the
  // canvas to the interactive viewport and translate cached gizmo coordinates
  // into the new client frame before dispatching actual touch.
  await canvas.scrollIntoViewIfNeeded();
  const afterBox=await canvas.boundingBox();
  if(beforeBox&&afterBox){
    marker.x+=afterBox.x-beforeBox.x;
    marker.y+=afterBox.y-beforeBox.y;
  }
  assert(Number.isFinite(marker.x)&&Number.isFinite(marker.y));
  assert.match(marker.label,/1 points selected/);
  const bbox=await page.locator('#modelAtelierViewport canvas').boundingBox();
  assert(bbox&&marker.x>=bbox.x&&marker.x<=bbox.x+bbox.width
    &&marker.y>=bbox.y&&marker.y<=bbox.y+bbox.height,'Gizmo must be visible');
  const obscurer=await page.evaluate(({x,y})=>{
     const el=document.elementFromPoint(x,y);
     return {tag:el?.tagName,id:el?.id,parent:el?.parentElement?.id};
  },marker);
  console.log('VERTEX_GIZMO_TOUCH_TARGET',device,marker.x,marker.y,obscurer);
  if(mobile){
   // Real Android-style touch drag; mouse events in a touch-emulated context
   // can be swallowed/replaced by the browser's synthetic gestures.
   const session=await context.newCDPSession(page);
   const one=(x,y)=>[{x,y,id:7}];
   await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:one(marker.x,marker.y)});
   for(let i=1;i<=8;i++)await session.send('Input.dispatchTouchEvent',{
      type:'touchMove',touchPoints:one(marker.x+i*5,marker.y-i*1.5)
   });
   await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  }else{
   await page.mouse.move(marker.x,marker.y);
   await page.mouse.down();
   await page.mouse.move(marker.x+40,marker.y-12,{steps:8});
   await page.mouse.up();
  }
  changed=(await parts()).find(p=>p.id==='model-0001');
  assert.equal(changed.sculptVertexEdits?.length,1,'Point gizmo drag must persist');
  assert(changed.sculptVertexEdits[0].indices.includes(12400));
  assert(changed.sculptVertexEdits[0].delta.some(n=>Math.abs(n)>.001));
  await page.locator('#modelAtelierSculptBrushMulti').check();
  await page.locator('#modelAtelierSculptBrushIndices').fill('12400,12500');
  await page.locator('#modelAtelierSculptBrushIndicesApply').click();
  assert.match(await page.locator('#modelAtelierSculptBrushVertexInfo').textContent(),/2 points selected/);
  const d=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const file=await (await d).path();
  const saved=JSON.parse(await readFile(file,'utf8'));
  assert.equal(saved.schema,'swyrl-model-atelier-v1');
  const savedHead=saved.model.parts.find(p=>p.id==='model-0001');
  assert.equal(JSON.stringify(savedHead.headAnatomy),originalSections);
  assert.equal(savedHead.sculptBrushes.length,1);
  assert.equal(savedHead.sculptVertexEdits.length,1);
  await page.locator('#modelAtelierImportFile').setInputFiles(file);
  await page.waitForTimeout(3000);
  const after=(await parts()).find(p=>p.id==='model-0001');
  assert.equal(after.sculptBrushes?.length,1);
  assert.equal(after.sculptVertexEdits?.length,1);
  assert.equal(JSON.stringify(after.headAnatomy),originalSections);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1121_CODEX_HEAD_SPHERE_BRUSH_VERTEX_GIZMO_AND_ROUNDTRIP_PASS',device,initial.length);
  await context.close();
 }
}finally{await browser.close();}
