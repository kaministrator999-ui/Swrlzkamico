import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('/tmp/swyrl-browser-test/node_modules/playwright');
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_BIN,
 args:['--no-sandbox','--enable-webgl','--enable-unsafe-swiftshader',
       '--use-gl=angle','--use-angle=swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1100,height:800},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:8765/?project=model-atelier',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__atelierArcTest?.ready(),{timeout:45000});
 await page.evaluate(()=>window.__atelierArcTest.pick());
 await page.locator('#modelAtelierMeshQuickStrip [data-mode="rotate"]').click();
 await page.waitForFunction(()=>window.__atelierArcTest.rings().length===3,{timeout:5000});
 const initial=await page.evaluate(()=>window.__atelierArcTest.state());
 const ring=await page.evaluate(()=>window.__atelierArcTest.handle('z'));
 console.log('ARC_RULER_START',JSON.stringify({ring,initial}));
 assert.equal(ring.axis,'z');
 assert.equal(await page.locator('#modelAtelierMeshQuickStrip [data-arc-ruler]').isVisible(),true);
 assert.ok(ring.r>0&&Number.isFinite(ring.x)&&Number.isFinite(ring.y));
 assert.equal(await page.evaluate(()=>window.__atelierArcTest.rings().join(',')),'x,y,z');
 await page.mouse.move(ring.x,ring.y);
 await page.mouse.down();
 const travel=65;
 await page.mouse.move(ring.x+ring.tx*travel,ring.y+ring.ty*travel,{steps:12});
 await page.waitForTimeout(120);
 const active=await page.evaluate(()=>window.__atelierArcTest.state());
 console.log('ARC_RULER_DURING',JSON.stringify(active));
 assert.equal(active.dragging,true,'Arc must capture pointer');
 assert.ok(active.arc,'Arc gesture must use rotation ruler path');
 assert.equal(active.axis,'z','Selected rotation axis must match bead');
 assert.ok(active.updates>initial.updates&&active.renders>initial.renders,
   'Real WebGL frames must render DURING the curved drag');
 assert.ok(Math.abs(active.rotation[2]-initial.rotation[2])>.002,
   'Selected mesh must rotate before pointerup');
 assert.ok(Math.abs(active.thumbAngle)>.002,
   'Bead must advance around its curved ruler before pointerup');
 await page.mouse.up();await page.waitForTimeout(120);
 const after=await page.evaluate(()=>window.__atelierArcTest.state());
 assert.equal(after.dragging,false);
 assert.ok(Math.abs(after.rotation[2]-initial.rotation[2])>.002,
   'Final rotation should persist and remain editable');
 console.log('ARC_RULER_AFTER',JSON.stringify(after));
 // Visual readout, axis toggling and optional angular snap use existing popup.
 await page.locator('[data-arc-snap]').click();
 assert.equal(await page.locator('[data-arc-snap]').textContent(),'Snap 5°');
 await page.locator('[data-arc-snap]').click();
 assert.equal(await page.locator('[data-arc-snap]').textContent(),'Snap 15°');
 await page.locator('[data-arc-snap]').click();
 assert.equal(await page.locator('[data-arc-snap]').textContent(),'Snap off');
 await page.locator('#modelAtelierMeshQuickStrip [data-mode="move"]').click();
 assert.equal(await page.locator('[data-arc-ruler]').isVisible(),false);
 assert.equal(await page.evaluate(()=>window.__atelierArcTest.rings().length),0,
   'Rotate-only helper disappears in Move mode');
 await page.locator('#modelAtelierMeshQuickStrip [data-mode="scale"]').click();
 assert.equal(await page.evaluate(()=>window.__atelierArcTest.rings().length),0,
   'Scale mode still has its existing handles, not arc ruler');
 assert.ok(!errors.length,'Browser JS errors: '+errors.join(' | '));
 console.log('SWRLZ_V1171_REAL_BROWSER_CURVED_ARC_ROTATION_PASS');
}finally{await browser.close();}
