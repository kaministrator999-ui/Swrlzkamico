import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile] of [['desktop',{width:1280,height:900},false],['mobile',{width:412,height:915},true]]){
   const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
   const page=await context.newPage();page.setDefaultTimeout(60000);
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
   await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
   const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
   const before=await parts(),original=before.find(p=>p.id==='model-0001');
   assert.equal(before.length,283);
   await page.locator('#modelAtelierParts').selectOption('model-0001');
   await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('front'));
   await page.locator('#modelAtelierFrameSelected').click();
   await page.locator('#modelAtelierLassoStartFreehand').click();
   const canvas=page.locator('#modelAtelierViewport canvas');
   await canvas.scrollIntoViewIfNeeded();
   const box=await canvas.boundingBox();assert(box&&box.width>100&&box.height>100);
   // Discover a truly raycastable point through the actual canvas events;
   // the camera target need not project to the CSS canvas midpoint.
   let found=null,attempts=0,lastProbe='';
   const xs=[.5,.42,.58,.33,.67,.25,.75];
   const ys=[.5,.42,.58,.33,.67,.25,.75];
   for(const fy of ys){
     if(found)break;
     for(const fx of xs){
       attempts++;
       await page.locator('#modelAtelierLassoStartFreehand').click();
       await canvas.scrollIntoViewIfNeeded();
       const r=await canvas.boundingBox();
       const x=r.x+r.width*fx,y=r.y+r.height*fy;
       await page.mouse.click(x,y);
       lastProbe=await page.locator('#modelAtelierLassoInfo').textContent();
       if(/Draft: 1 pins/.test(lastProbe)){found={fx,fy};break;}
     }
   }
   assert(found,'Unable to acquire any actual selected-head raycast in '+attempts+
     ' canvas probes; last status: '+lastProbe);
   await page.locator('#modelAtelierLassoStartFreehand').click();
   await canvas.scrollIntoViewIfNeeded();
   const actual=await canvas.boundingBox();
   const cx=actual.x+actual.width*found.fx,cy=actual.y+actual.height*found.fy;
   const rad=Math.min(actual.width,actual.height)*.037;
   const samples=Array.from({length:17},(_,i)=>({
     x:cx+Math.cos(i/16*Math.PI*2)*rad,
     y:cy+Math.sin(i/16*Math.PI*2)*rad
   }));
   console.log('FREEHAND_SURFACE_TARGET',device,found,attempts,actual);
   if(mobile){
     const session=await context.newCDPSession(page);
     await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{...samples[0],id:7}]});
     for(const p of samples.slice(1))await session.send('Input.dispatchTouchEvent',{
       type:'touchMove',touchPoints:[{...p,id:7}]
     });
     await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
   }else{
     await page.mouse.move(samples[0].x,samples[0].y);
     await page.mouse.down();
     for(const p of samples.slice(1))await page.mouse.move(p.x,p.y);
     await page.mouse.up();
   }
   const info=await page.locator('#modelAtelierLassoInfo').textContent();
   assert.match(info,/Draft: [3-9]|Draft: [12][0-9]|Draft: 3[0-2]/,
     'Real pointer trace must capture 3+ front surface samples; observed '+info);
   await page.locator('#modelAtelierLassoFinish').click();
   let head=(await parts()).find(p=>p.id==='model-0001');
   assert.equal(head.sculptLassos?.length,1,'Freehand boundary must be saved to actual selected head');
   assert(head.sculptLassos[0].pins.length>=3&&head.sculptLassos[0].pins.length<=32);
   assert(head.sculptLassos[0].pins.every(x=>Number.isInteger(x.tri)&&x.bary.length===3));
   assert.deepEqual(head.headAnatomy,original.headAnatomy,'Base Codex anatomical sections unchanged');
   const dl=page.waitForEvent('download');
   await page.locator('#modelAtelierExport').click();
   const path=await (await dl).path();
   const saved=JSON.parse(await readFile(path,'utf8'));
   assert.equal(saved.model.parts.find(p=>p.id==='model-0001').sculptLassos.length,1);
   await page.locator('#modelAtelierUndo').click();
   head=(await parts()).find(p=>p.id==='model-0001');
   assert(!head.sculptLassos?.length,'Undo must remove freehand lasso');
   await page.locator('#modelAtelierImportFile').setInputFiles(path);
   await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene()
       .project.modelAtelier.parts.find(p=>p.id==='model-0001')?.sculptLassos?.length===1);
   assert.equal(errors.length,0,errors.join(' | '));
   console.log('V1124_FREEHAND_REAL_BROWSER_SAVE_UNDO_RELOAD_PASS',device);
   await context.close();
 }
}finally{await browser.close();}
