import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const url=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try {
 for (const cfg of [
  {name:'small-phone',size:{width:360,height:740},mobile:true},
  {name:'phone',size:{width:412,height:915},mobile:true},
  {name:'landscape',size:{width:700,height:400},mobile:true},
  {name:'desktop',size:{width:1280,height:850},mobile:false}
 ]) {
  const ctx=await browser.newContext({viewport:cfg.size,isMobile:cfg.mobile,hasTouch:cfg.mobile});
  const page=await ctx.newPage();page.setDefaultTimeout(30000);
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(url+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  await page.waitForFunction(()=>!!document.getElementById('atelierMobileOpenTools'),{timeout:30000});
  const panel=page.locator('#modelAtelierPanel'), context=page.locator('#atelierContextWorkbench');
  const enabled=await panel.evaluate(n=>n.classList.contains('atelier-mobile-tools'));
  assert.equal(enabled,cfg.mobile,'mobile condition must govern single-drawer mode');
  if(cfg.mobile){
   await page.locator('#atelierMobileOpenTools').click();
   assert(await context.isVisible(),'open drawer from primary rail');
   assert(!(await page.locator('#modelAtelierInspectorDock').isVisible()),'original inspector stays mounted but hidden');
   assert(await page.locator('#atelierContextOperations').isVisible());
   await page.locator('#modelAtelierToolRail').getByRole('button',{name:'Open Lasso editing tools'}).click();
   assert.equal(await page.locator('#atelierContextGroupName').textContent(),'Lasso tools');
   await context.getByRole('button',{name:'Paint mask'}).click();
   const css=await page.evaluate(()=>{
     const d=document.getElementById('atelierContextWorkbench'),body=d.querySelector('.atelier-context-body');
     const rail=document.getElementById('modelAtelierToolRail'),inspector=document.getElementById('modelAtelierInspectorDock');
     const box=d.getBoundingClientRect(),ops=d.querySelector('.atelier-context-left').getBoundingClientRect();
     return {box:{x:box.x,y:box.y,w:box.width,h:box.height},display:getComputedStyle(body).flexDirection,inspector:getComputedStyle(inspector).display,opsH:ops.height,railY:rail.getBoundingClientRect().y};
   });
   assert.equal(css.display,'column');
   assert.equal(css.inspector,'none');
   assert(css.box.x>=-2&&css.box.w<=cfg.size.width+2,'drawer fits screen horizontally');
   assert(css.box.y>=0&&css.box.h>50,'drawer stays inside visible phone viewport');
   await context.getByRole('button',{name:'Expand mobile tool drawer'}).click();
   assert(await panel.evaluate(n=>n.classList.contains('atelier-mobile-expanded')));
   await context.getByRole('button',{name:'Collapse mobile tool drawer'}).click();
   assert(await panel.evaluate(n=>n.classList.contains('atelier-mobile-collapsed')));
   await context.getByRole('button',{name:'Set tool drawer to half height'}).click();
   assert(!(await panel.evaluate(n=>n.classList.contains('atelier-mobile-collapsed'))));
   await context.getByRole('button',{name:'Close contextual tools'}).click();
   assert(!(await context.isVisible()));
   assert.equal(await page.locator('#modelAtelierParts option').count(),283);
   console.log('SWRLZ_MOBILE_LAYOUT_PASS',cfg.name,css);
  }else{
   assert(await page.locator('#modelAtelierInspectorDock').isVisible());
   assert(!(await context.isVisible()));
   console.log('SWRLZ_DESKTOP_ORIGINAL_LAYOUT_PASS',cfg.name);
  }
  assert.deepEqual(errors,[],'no uncaught errors');
  await ctx.close();
 }
}finally{await browser.close();}
