import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader',
 '--use-gl=angle','--use-angle=swiftshader'
]});
const dist=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
try{
 for(const [name,viewport,isMobile] of [
   ['desktop',{width:1366,height:900},false],
   ['mobile',{width:412,height:915},true]
 ]){
   const context=await browser.newContext({viewport,isMobile,hasTouch:isMobile});
   const page=await context.newPage(),errors=[];page.setDefaultTimeout(40000);
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
   const canvas=page.locator('#modelAtelierPanel:not([hidden]) canvas').first();
   await canvas.waitFor();
   await page.waitForFunction(()=>!!window.SWYRL_ENGINE_VIEW?.status);
   const get=()=>page.evaluate(()=>window.SWYRL_ENGINE_VIEW.status());
   const scene=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
   const original=await scene();
   assert.equal(original.length,283);
   assert(original.find(p=>p.id==='model-0001')?.headAnatomy,'Official Codex anatomical head must stay in place');
   await page.locator('#modelAtelierParts').selectOption('model-0001');
   const mode=page.locator('#modelAtelierViewportMode');
   const scope=page.locator('#modelAtelierViewportScope');
   assert(await mode.isVisible(),'Render-mode dropdown should be visible in viewport toolbar');
   await scope.selectOption('selected');
   await mode.selectOption('wireframe');
   let result=await get();
   assert.equal(result.wireframe,1,'Wireframe-selected should change exactly one mesh');
   await mode.selectOption('overlay');result=await get();
   assert.equal(result.overlay,1,'Overlay should preserve shaded mesh and draw wire edges');
   assert.equal(result.wireframe,0);
   await mode.selectOption('xray');result=await get();
   assert.equal(result.xray,1,'Selected X-Ray must be transparent');
   await scope.selectOption('all');
   await mode.selectOption('wireframe');result=await get();
   assert.equal(result.wireframe,283,'Full model wireframe must apply to every native mesh');
   await mode.selectOption('shaded');result=await get();
   assert.equal(result.wireframe,0,'Switching to shaded must restore solid materials');
   assert.equal(result.overlay,0);
   assert.equal(result.xray,0);
   const colors=page.locator('#modelAtelierViewportColors');
   const textures=page.locator('#modelAtelierViewportTextures');
   const contrast=page.locator('#modelAtelierViewportWireContrast');
   const wireTint=page.locator('#modelAtelierViewportWireTint');
   assert(await colors.isVisible()&&await textures.isVisible()&&await contrast.isVisible(),
     'Independent color and texture visibility controls must be easy to access');
   assert(await colors.isChecked()&&await textures.isChecked()&&await contrast.isChecked());
   await textures.uncheck();
   result=await get();
   assert.equal(result.originalColors,283);
   assert.equal(result.originalTextures,0,'All source texture layers must be masked in the viewport');
   assert.equal(result.selectedMaterial?.hasMap,false);
   await colors.uncheck();
   result=await get();
   assert.equal(result.originalColors,0,'All source colors must be neutralized');
   assert.equal(result.originalTextures,0,'Colors and textures must remain separate toggles');
   assert.equal(result.selectedMaterial?.vertexColors,false,
     'Disabling model colors must also disable vertex dye attributes');
   assert.equal(result.selectedMaterial?.color,'cad3de');
   await textures.check();
   result=await get();
   assert.equal(result.originalColors,0,'Restoring textures must not restore source colors');
   assert.equal(result.originalTextures,283);
   await colors.check();
   result=await get();
   assert.equal(result.originalColors,283);
   assert.equal(result.originalTextures,283);
   await scope.selectOption('selected');
   await colors.uncheck();
   await textures.uncheck();
   result=await get();
   assert.equal(result.originalColors,282,'Selected-only color toggle must not recolor other meshes');
   assert.equal(result.originalTextures,282,'Selected-only texture toggle must not hide every mesh texture');
   assert.equal(result.selectedMaterial.vertexColors,false);
   assert.equal(result.selectedMaterial.hasMap,false);
   // Changing to wireframe with the global contrast shader must not
   // accidentally mutate cached source HD materials.
   await mode.selectOption('wireframe');
   result=await get();
   assert.equal(result.wireframe,1);
   assert.equal(result.selectedMaterial.basic,true);
   assert.equal(result.selectedMaterial.wireframe,true);
   await contrast.uncheck();
   result=await get();
   assert.equal(result.selectedMaterial.basic,false,
     'Material-color wireframe should be available as a separate option');
   await contrast.check();
   await wireTint.fill('#ffffff');
   result=await get();
   assert.equal(result.wireTint,'#ffffff');
   assert.equal(result.selectedMaterial.color,'ffffff');
   await mode.selectOption('overlay');
   result=await get();
   assert.equal(result.overlay,1);
   await colors.check();
   await textures.check();
   result=await get();
   assert.equal(result.originalColors,283);
   assert.equal(result.originalTextures,283);
   await scope.selectOption('all');
   await mode.selectOption('shaded');
   result=await get();
   assert.equal(result.wireframe,0);
   assert.equal(result.overlay,0);
   assert.equal(result.xray,0);
   await page.locator('[data-at-view="right"]').click();
   assert(Math.abs((await get()).yaw-Math.PI/2)<.01);
   await page.locator('[data-at-view="top"]').click();
   assert((await get()).pitch>1.5);
   await page.locator('[data-at-view="front"]').click();
   assert(Math.abs((await get()).yaw)<.01);
   // Force canvas into viewport so real pointer events reach canvas, rather
   // than testing an unrelated DOM synthetic event.
   await canvas.scrollIntoViewIfNeeded();
   let rect=await canvas.boundingBox();
   assert(rect&&rect.width>100&&rect.height>130);
   const xc=rect.x+rect.width*.5,yc=rect.y+rect.height*.52;
   if(isMobile){
      const session=await context.newCDPSession(page);
      const fingers=(off,side)=>[
        {x:xc-side,y:yc+off,id:11},
        {x:xc+side,y:yc+off,id:12}
      ];
      const before=await get(),side=Math.min(55,rect.width*.18);
      await session.send('Input.dispatchTouchEvent',{
         type:'touchStart',touchPoints:fingers(0,side)
      });
      await session.send('Input.dispatchTouchEvent',{
         type:'touchMove',touchPoints:fingers(0,side*1.65)
      });
      await session.send('Input.dispatchTouchEvent',{
         type:'touchMove',touchPoints:fingers(25,side*1.65).map(p=>({...p,x:p.x+35}))
      });
      await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
      const after=await get();
      assert(after.distance<before.distance*.85,
        'Expanding two-finger pinch must zoom IN camera without modifying mesh');
      assert(dist(after.pan,before.pan)>.02,
        'Two-finger translation must slide the camera target');
      assert.equal(after.activeTouchCount,0,'Touch state must be cleaned when pinch finishes');
      assert.equal((await scene()).length,283,'Gestures must not remove any mesh');
   }else{
      const before=await get();
      await page.keyboard.down('Shift');
      await page.mouse.move(xc,yc);
      await page.mouse.down();
      await page.mouse.move(xc+110,yc-30,{steps:5});
      await page.mouse.up();
      await page.keyboard.up('Shift');
      const after=await get();
      assert(dist(after.pan,before.pan)>.05,'Shift + mouse drag must pan the camera');
   }
   await page.locator('#modelAtelierViewportPanReset').click();
   assert(dist((await get()).pan,[0,0,0])<1e-9,'Center pan must restore camera target');
   const final=await scene();
   assert.deepEqual(final,original,'Viewport modes and camera gestures must never edit native model data');
   assert.equal(errors.length,0,'Browser script errors: '+errors.join(' | '));
   console.log('V1121_VIEWPORT_WIREFRAME_SELECTED_ALL_XRAY_GESTURES_PASS',name,result.wireframe,original.length);
   await context.close();
 }
}finally{await browser.close();}
