import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('/tmp/swyrl-browser-test/node_modules/playwright');
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_BIN,
 args:['--no-sandbox','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1060,height:850}});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:8765/?project=model-atelier',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__groupTest?.ready(),{timeout:45000});
 const get=()=>page.evaluate(()=>window.__groupTest.state());
 const initial=await get();
 console.log('ASSEMBLY_INITIAL',JSON.stringify(initial));
 assert.equal(initial.count,283);
 assert.equal(initial.groups.length,0);
 assert.ok(initial.controls);
 const [a,b,c]=initial.ids;
 // Real UI buttons, same select() path invoked by native tap handler.
 await page.locator('[data-group-multi]').click();
 await page.evaluate(id=>window.__groupTest.tap(id),a);
 await page.evaluate(id=>window.__groupTest.tap(id),b);
 assert.deepEqual((await get()).selected,[a,b]);
 await page.evaluate(id=>window.__groupTest.tap(id),a);
 assert.deepEqual((await get()).selected,[b],'tap toggles selected child OFF');
 await page.evaluate(id=>window.__groupTest.tap(id),a);
 await page.evaluate(()=>window.__groupTest.tap(null));
 assert.equal((await get()).selected.length,2,'empty taps keep selection');
 await page.locator('.atelier-group-details summary').click();
 await page.locator('[data-group-create]').click();
 const grouped=await get();
 console.log('ASSEMBLY_GROUPED',JSON.stringify(grouped));
 assert.equal(grouped.groups.length,1);
 assert.equal(grouped.groups[0].members.length,2);
 assert.equal(grouped.count,initial.count,'Grouping MUST NOT merge original parts');
 assert.deepEqual(grouped.partsFingerprint,initial.partsFingerprint,
  'Grouping MUST preserve every original mesh geometry/material/transform');
 assert.equal(grouped.selected.length,2);
 assert.equal(grouped.multi,false);
 assert.equal(grouped.scope,'group');
 assert.equal(grouped.outlines,2);
 const beforeGroupTransforms=await page.evaluate(ids=>window.__groupTest.partTransforms(ids),[a,b]);
 await page.evaluate(id=>window.__groupTest.tap(id),b);
 assert.equal((await get()).selected.length,2,'Selecting child in group mode picks entire assembly');
 const changed=await page.evaluate(()=>window.__groupTest.moveX(.12));
 assert.equal(changed,true,'Native group gizmo commit succeeds');
 const moved=await page.evaluate(ids=>window.__groupTest.partTransforms(ids),[a,b]);
 assert.ok(moved.every((p,i)=>Math.abs(p.position[0]-beforeGroupTransforms[i].position[0]-.12)<.001),
  'Both group children move together');
 assert.deepEqual(moved.map(p=>p.material),beforeGroupTransforms.map(p=>p.material),
  'Individual materials retained');
 await page.evaluate(()=>window.__groupTest.undo());
 assert.deepEqual((await page.evaluate(ids=>window.__groupTest.partTransforms(ids),[a,b])),beforeGroupTransforms,
  'Undo restores both child transforms');
 assert.equal((await get()).groups.length,1,'Undo keeps group metadata');
 await page.evaluate(()=>window.__groupTest.undo());
 assert.equal((await get()).groups.length,0,'Undo group creation restores ungrouped state');
 await page.evaluate(()=>window.__groupTest.redo());
 assert.equal((await get()).groups.length,1,'Redo restores group membership');
 await page.evaluate(id=>window.__groupTest.tap(id),a);
 await page.locator('[data-group-scope]').selectOption('child');
 await page.evaluate(id=>window.__groupTest.tap(id),b);
 assert.deepEqual((await get()).selected,[b],'Child mode edits a single part inside the group');
 assert.equal((await get()).groups.length,1,'Child editing preserves group');
 // Restore group selection; edit membership by toggling taps.
 await page.locator('[data-group-scope]').selectOption('group');
 await page.evaluate(id=>window.__groupTest.tap(id),a);
 await page.locator('[data-group-multi]').click();
 await page.evaluate(id=>window.__groupTest.tap(id),b);
 await page.evaluate(id=>window.__groupTest.tap(id),c);
 assert.deepEqual(new Set((await get()).selected),new Set([a,c]));
 await page.locator('[data-group-update]').click();
 const updated=await get();
 console.log('ASSEMBLY_UPDATED',JSON.stringify(updated));
 assert.deepEqual(new Set(updated.groups[0].members),new Set([a,c]),
   'Update members reassigns assembly without losing source parts');
 assert.equal(updated.count,283);
 // Persist group metadata through the native model JSON import path.
 const exported=await page.evaluate(()=>window.__groupTest.exportModel());
 assert.equal(exported.meshGroups.length,1);
 assert.deepEqual(new Set(exported.meshGroups[0].members),new Set([a,c]));
 const file={name:'v1174-groups.json',mimeType:'application/json',
   buffer:Buffer.from(JSON.stringify({schema:'swyrl-model-atelier-v1',model:exported}))};
 await page.locator('#modelAtelierImportFile').setInputFiles(file);
 await page.waitForFunction(()=>document.querySelector('#modelAtelierStatus')?.textContent?.includes('imported'),{timeout:5000});
 assert.deepEqual((await get()).groups,updated.groups,'Native JSON import retains editable groups');
 // Un-group, then undo it, and verify every original object still exists.
 await page.locator('[data-group-picker]').selectOption(updated.groups[0].id);
 await page.locator('[data-group-ungroup]').click();
 assert.equal((await get()).groups.length,0);
 assert.equal((await get()).count,283);
 await page.evaluate(()=>window.__groupTest.undo());
 assert.equal((await get()).groups.length,1,'Ungroup is reversible through Undo');
 await page.setViewportSize({width:390,height:844});
 await page.waitForTimeout(150);
 const mobile=await page.evaluate(()=>window.__groupTest.mobile());
 console.log('ASSEMBLY_MOBILE',JSON.stringify(mobile));
 assert.ok(mobile.toggleWidth>=55,'Mobile multi-select remains reachable');
 assert.ok(mobile.toggleHeight>=36,'Mobile control has finger-sized target');
 assert.equal(mobile.multiple,true,'Native parts list multi-select preserved');
 assert.deepEqual(errors,[],'Browser should have no uncaught exceptions');
 console.log('SWRLZ_V1174_REAL_BROWSER_NONDESTRUCTIVE_GROUPS_PASS');
}finally{await browser.close();}
