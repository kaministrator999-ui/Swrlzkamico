import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('/tmp/swyrl-browser-test/node_modules/playwright');
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_BIN,
 args:['--no-sandbox','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1390,height:900}});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:8765/?project=model-atelier',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__desktopTest?.ready(),{timeout:45000});
 const initial=await page.evaluate(()=>window.__desktopTest.initial());
 console.log('DESKTOP_BASELINE',JSON.stringify(initial));
 assert.equal(initial.parts,283);
 assert.equal(initial.groups,0);
 assert.ok(initial.toolbar&&initial.wireControls);
 const target=await page.evaluate(()=>window.__desktopTest.pickScale());
 console.log('DESKTOP_TARGET',JSON.stringify(target));
 const change=await page.evaluate(()=>window.__desktopTest.scaleCandidate(9));
 console.log('DESKTOP_SCALE_LIMIT',JSON.stringify(change));
 assert.ok(change.factor>3.01,'Scale >3x must no longer be arbitrarily capped');
 assert.ok(change.valid,'Requested size clipped to the actual safe model range');
 const before=await page.evaluate(()=>window.__desktopTest.scaleState());
 const didScale=await page.evaluate(()=>window.__desktopTest.commitScale(4));
 assert.ok(didScale,'Mesh scale commits normally');
 const after=await page.evaluate(()=>window.__desktopTest.scaleState());
 assert.ok(after.scale[0]>before.scale[0],'Scale visibly updates saved part');
 assert.ok(after.geometryMeshScale[0]>before.geometryMeshScale[0],'Scene mesh updates without Undo');
 await page.evaluate(()=>window.__desktopTest.undo());
 const undone=await page.evaluate(()=>window.__desktopTest.scaleState());
 assert.deepEqual(undone.scale,before.scale,'Undo restores original scale');
 await page.evaluate(()=>window.__desktopTest.redo());
 const redone=await page.evaluate(()=>window.__desktopTest.scaleState());
 assert.deepEqual(redone.scale,after.scale,'Redo restores the scaled part');
 // Wireframe on all meshes should not flatten every object into white.
 await page.evaluate(()=>window.__desktopTest.wireframe());
 const wire=await page.evaluate(()=>window.__desktopTest.wireState());
 console.log('DESKTOP_WIREFRAME',JSON.stringify(wire));
 assert.ok(wire.activeOpacity>.85);
 assert.ok(wire.othersOpacity<=.34);
 assert.ok(wire.dots>0&&wire.dots<=2000,'Selected mesh has visible sampled actual vertices');
 assert.ok(wire.oldWireColor!==wire.otherWireColor,'Active mesh stands out from other wire');
 await page.locator('.atelier-top-advanced summary').click();
 await page.locator('[data-desktop-wire-dots]').uncheck();
 assert.equal((await page.evaluate(()=>window.__desktopTest.wireState())).dots,0,'Dots independently switch off');
 await page.locator('[data-desktop-wire-dots]').check();
 assert.ok((await page.evaluate(()=>window.__desktopTest.wireState())).dots>0,'Dots switch on');
 // Wheel and camera zoom buttons must reach true close-inspection distance.
 const zoom=await page.evaluate(()=>window.__desktopTest.zoom());
 console.log('DESKTOP_CLOSE_ZOOM',JSON.stringify(zoom));
 assert.ok(zoom.distance<.45&&zoom.distance>=.16,'Camera zooms closer than old 3.7 world-unit bound');
 assert.ok(zoom.near<=.018,'Near clip does not hide detail at close zoom');
 // Two-finger gestures use the same lower bound, without modifying project.
 assert.equal(zoom.touchMin,.16);
 // Existing group/native project still intact.
 const final=await page.evaluate(()=>window.__desktopTest.initial());
 assert.equal(final.parts,283);
 assert.equal(final.groups,0);
 assert.deepEqual(errors,[],'No browser uncaught exceptions');
 console.log('SWRLZ_V1176_DESKTOP_SCALE_WIRE_ZOOM_PASS');
}finally{await browser.close();}
