import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('/tmp/swyrl-browser-test/node_modules/playwright');
const browser=await chromium.launch({
 headless:true,executablePath:process.env.CHROME_BIN,
 args:['--no-sandbox','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']
});
try{
 const page=await browser.newPage({viewport:{width:1080,height:840},deviceScaleFactor:1});
 const errors=[];
 page.on('pageerror',err=>errors.push(String(err)));
 await page.goto('http://127.0.0.1:8765/?project=model-atelier',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__atelierArcTest?.ready(),{timeout:45000});
 const chosen=await page.evaluate(()=>window.__atelierArcTest.pick());
 await page.locator('#modelAtelierMeshQuickStrip [data-mode=rotate]').click();
 await page.waitForFunction(()=>window.__atelierArcTest.rings().length===3);
 console.log('ARC_ALIGN_PART',chosen);
 const geometry=await page.evaluate(()=>window.__atelierArcTest.geometry());
 console.log('ARC_ALIGN_GEOMETRY',JSON.stringify(geometry));
 assert.ok(geometry.radius>=.2&&geometry.radius<=1.3);
 assert.ok(geometry.radius<geometry.oldZoomRadius*.91,
  'The rotation radius should be substantially smaller than v11.71 for the head mesh');
 assert.ok(geometry.centerDelta<.0001,'Gizmo remains centered on the selected mesh');
 for(const axis of ['x','y','z']){
  await page.locator('#modelAtelierMeshQuickStrip [data-axis='+axis+']').click();
  await page.waitForTimeout(100);
  const start=await page.evaluate(()=>window.__atelierArcTest.state());
  const bead=await page.evaluate(a=>window.__atelierArcTest.handle(a),axis);
  assert.ok(bead&&Number.isFinite(bead.x)&&Number.isFinite(bead.y),'Visible '+axis+' bead');
  console.log('ARC_ALIGN_START',JSON.stringify({axis,bead,rotation:start.rotation,readout:start.readout}));
  assert.ok(start.opacity[axis]>.85,'The active axis should have a highlighted ruler');
  for(const other of ['x','y','z'].filter(a=>a!==axis))
   assert.ok(start.opacity[other]<.4,'Inactive ring '+other+' should not dominate');
  await page.mouse.move(bead.x,bead.y);
  await page.mouse.down();
  await page.mouse.move(bead.x+bead.tx*49,bead.y+bead.ty*49,{steps:10});
  await page.waitForTimeout(80);
  const during=await page.evaluate(()=>window.__atelierArcTest.state());
  console.log('ARC_ALIGN_DURING',JSON.stringify({axis,during}));
  assert.equal(during.dragging,true,axis+' captured pointer');
  assert.equal(during.axis,axis,axis+' keeps its axis mapping');
  assert.ok(during.updates>start.updates&&during.renders>start.renders,
   axis+' actually renders while dragging');
  assert.ok(Math.abs(during.rotation[['x','y','z'].indexOf(axis)]-start.rotation[['x','y','z'].indexOf(axis)])>.01,
   axis+' changes the selected mesh around the requested axis before pointerup');
  assert.ok(Math.abs(during.thumbAngle)>.01,axis+' bead travels along its arc');
  assert.ok(Math.abs(during.amount)<=2*Math.PI/3+.001,'Rotation amount remains in ±120° bounds');
  assert.ok(during.readout.includes('Δ '),'Angle readout identifies a drag delta');
  await page.mouse.up();
  await page.waitForTimeout(100);
  const done=await page.evaluate(()=>window.__atelierArcTest.state());
  assert.equal(done.dragging,false);
  assert.ok(done.readout.includes('Last Δ'),'Readout identifies previous drag as a delta');
  console.log('ARC_ALIGN_COMMITTED',JSON.stringify({axis,rotation:done.rotation,readout:done.readout}));
 }
 await page.locator('#modelAtelierMeshQuickStrip [data-mode=move]').click();
 assert.equal(await page.evaluate(()=>window.__atelierArcTest.rings().length),0);
 await page.locator('#modelAtelierMeshQuickStrip [data-mode=scale]').click();
 assert.equal(await page.evaluate(()=>window.__atelierArcTest.rings().length),0);
 assert.deepEqual(errors,[],'No runtime errors');
 console.log('SWRLZ_V1172_ALL_AXIS_REAL_BROWSER_ROTATION_PASS');
}finally{
 await browser.close();
}
