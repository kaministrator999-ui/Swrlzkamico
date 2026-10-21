import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('/tmp/swyrl-browser-test/node_modules/playwright');
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_BIN,
 args:['--no-sandbox','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1100,height:800},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:8765/?project=model-atelier',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__gizmoTouchTest?.ready(),{timeout:45000});
 const name=await page.evaluate(()=>window.__gizmoTouchTest.pick());
 console.log('GIZMO_TOUCH_SELECTED',name);
 // Each click must repaint in the same JS turn. No orbit, resize or camera movement.
 for(const mode of ['rotate','move','scale','rotate']){
  const t=await page.evaluate(mode=>window.__gizmoTouchTest.switchMode(mode),mode);
  console.log('GIZMO_TOUCH_SWITCH',JSON.stringify(t));
  assert.equal(t.mode,mode);
  assert.equal(t.painted,1,'Switch '+mode+' must call immediate WebGL render');
  assert.equal(t.gizmoCount,1,'Only one active gizmo root');
  assert.equal(t.arcCount,mode==='rotate'?3:0);
  assert.ok(mode!=='rotate'||t.thick===3,'All rotation arcs use thick tubes');
 }
 // Arc center is unchanged from v11.72, while visible arc thickness doubles.
 const thickness=await page.evaluate(()=>window.__gizmoTouchTest.arcDimensions());
 console.log('GIZMO_TOUCH_ARC',JSON.stringify(thickness));
 assert.ok(thickness.radius<.75,'No regression to oversized ring');
 assert.ok(thickness.thickness>=.025,'The arc must be visibly thicker');
 assert.ok(thickness.beadRadius>=.09,'The slider bead should be large enough to see');
 // Explicit axis choice resolves unavoidable screen overlap between 3D rings.
 await page.locator('#modelAtelierMeshQuickStrip [data-axis="z"]').click();
 const target=await page.evaluate(()=>window.__gizmoTouchTest.arcPoint('z',.6));
 console.log('GIZMO_TOUCH_GRAB',JSON.stringify(target));
 assert.equal(target.selectedAxis,'z','Curved ruler is selectable away from bead');
 assert.ok(target.beadDistance>17,'Test touches an arc section, not its bead');
 assert.ok(target.x>0&&target.y>0&&target.x<1100&&target.y<800);
 await page.mouse.move(target.x,target.y);
 const before=await page.evaluate(()=>window.__gizmoTouchTest.state());
 await page.mouse.down();
 const held=await page.evaluate(()=>window.__gizmoTouchTest.state());
 assert.equal(held.dragging,true,'Touching the visible curved ruler must capture the pointer');
 assert.equal(held.axis,'z');
 await page.mouse.move(target.x+target.tx*46,target.y+target.ty*46,{steps:8});
 await page.waitForTimeout(100);
 const moving=await page.evaluate(()=>window.__gizmoTouchTest.state());
 console.log('GIZMO_TOUCH_DURING',JSON.stringify(moving));
 assert.equal(moving.dragging,true);
 assert.ok(Math.abs(moving.rotation[2]-before.rotation[2])>.005,'Mesh rotates before pointer release');
 assert.ok(Math.abs(moving.beadAngle-.6)>.005,'Slider bead follows drag from its picked arc location');
 await page.mouse.up();await page.waitForTimeout(90);
 const saved=await page.evaluate(()=>window.__gizmoTouchTest.state());
 assert.equal(saved.dragging,false);
 assert.ok(Math.abs(saved.rotation[2]-before.rotation[2])>.005);
 // Test screen-pixel touch tolerance and single-mode repaint on a phone viewport.
 await page.setViewportSize({width:390,height:844});
 await page.waitForTimeout(150);
 const mobile=await page.evaluate(()=>window.__gizmoTouchTest.mobile());
 console.log('GIZMO_TOUCH_MOBILE',JSON.stringify(mobile));
 assert.equal(mobile.repaint,1,'Mode switch on narrow screen repaints immediately');
 assert.equal(mobile.arcCount,3);
 assert.ok(mobile.touchHit,'Mobile touch accepts a nearby arc segment');
 assert.deepEqual(errors,[],'No script errors');
 console.log('SWRLZ_V1173_REAL_BROWSER_INSTANT_MODE_AND_ARC_GRAB_PASS');
}finally{await browser.close();}
