import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('/tmp/swyrl-browser-test/node_modules/playwright');
const browser=await chromium.launch({
  headless:true,executablePath:process.env.CHROME_BIN,
  args:['--no-sandbox','--enable-webgl','--enable-unsafe-swiftshader',
    '--use-gl=angle','--use-angle=swiftshader']
});
try{
 const page=await browser.newPage({viewport:{width:1100,height:800},deviceScaleFactor:1});
 const errors=[];
 page.on('pageerror',error=>errors.push(String(error)));
 await page.goto('http://127.0.0.1:8765/?project=model-atelier',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__engineGizmoTest?.ready(),{timeout:45000});
 const selected=await page.evaluate(()=>window.__engineGizmoTest.pick());
 assert.ok(selected,'A model part should be selected');
 await page.waitForTimeout(150);
 const before=await page.evaluate(()=>window.__engineGizmoTest.state());
 const handle=await page.evaluate(()=>window.__engineGizmoTest.handle('x'));
 assert.ok(handle,'A visible x-axis handle should exist');
 console.log('LIVE_DRAG_TEST_START',JSON.stringify({name:selected,handle,before}));
 await page.mouse.move(handle.x,handle.y);
 await page.mouse.down();
 await page.mouse.move(handle.x+105,handle.y-6,{steps:9});
 await page.waitForTimeout(130);
 const during=await page.evaluate(()=>window.__engineGizmoTest.state());
 console.log('LIVE_DRAG_TEST_DURING',JSON.stringify(during));
 assert.equal(during.dragging,true,'Pointer capture must remain during drag');
 assert.ok(during.updates>0,'Preview must update during mouse movement');
 assert.ok(during.renders>0,'WebGL frame must paint during drag');
 assert.ok(during.position.some((n,i)=>Math.abs(n-before.position[i])>0.00001),
   'Selected mesh must move BEFORE pointerup');
 assert.ok(during.gizmo.some((n,i)=>Math.abs(n-before.gizmo[i])>0.00001),
   'Gizmo handles must move BEFORE pointerup');
 await page.mouse.up();
 await page.waitForTimeout(100);
 const after=await page.evaluate(()=>window.__engineGizmoTest.state());
 assert.equal(after.dragging,false,'Gizmo drag should commit on release');
 console.log('LIVE_DRAG_TEST_AFTER',JSON.stringify(after));
 assert.ok(after.position.some((n,i)=>Math.abs(n-before.position[i])>0.00001),
   'Committed mesh must retain new transform');
 assert.equal(errors.length,0,'No browser runtime exceptions expected: '+errors.join(' | '));
 console.log('SWRLZ_V1169_REAL_BROWSER_POINTER_PREVIEW_PASS');
}finally{await browser.close();}
