import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const url=(process.env.SWYRL_MOBILE_TEST_URL||'http://127.0.0.1:8794').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const sizes=[['phone-small',320,720,false],['phone-narrow',360,640,false],['phone-standard',412,915,false],['phone-wide',430,932,false],['landscape',844,390,true],['desktop',1280,900,false]];
try{
 for(const [name,width,height,landscape] of sizes){
  const mobile=name!=='desktop',ctx=await browser.newContext({viewport:{width,height},isMobile:mobile,hasTouch:mobile});
  const page=await ctx.newPage();page.setDefaultTimeout(40000);
  const errors=[];page.on('pageerror',err=>{errors.push(err.stack||err.message);console.log('MOBILE_PAGE_ERROR',name,err.stack||err.message)});
  await page.goto(url+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  const sheet=page.locator('#atelierContextWorkbench'),rail=page.locator('#modelAtelierToolRail');
  assert(await rail.isVisible(),'The original category rail must exist');
  assert(!(await sheet.isVisible()),'Context starts closed');
  assert((await page.locator('#modelAtelierPartCount').innerText()).includes('283'),'canonical original mesh must be preserved');
  if(mobile){
   const chrome=await page.evaluate(()=>{
    const element=document.getElementById('atelierContextToggle');const r=element.getBoundingClientRect();
    const top=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
    return {toggle:{x:r.x,y:r.y,width:r.width,height:r.height},hit:top?.tagName+'#'+(top?.id||'')+'.'+(top?.className||''),inspectorZ:getComputedStyle(document.querySelector('.atelier-inspector')).zIndex,inspectorDisplay:getComputedStyle(document.querySelector('.atelier-inspector')).display};
   });
   console.log('MOBILE_CHROME_HIT',name,JSON.stringify(chrome));
   await rail.getByRole('button',{name:'Open Lasso editing tools'}).click();
  }else await page.locator('#atelierContextToggle').click();
  assert(await sheet.isVisible());
  await page.waitForFunction(()=>document.querySelector('#modelAtelierPanel')?.dataset.mobileAdaptiveInstalled==='1');
  if(mobile){
   assert(!(await page.locator('.atelier-inspector').isVisible()),'native inspector must not overlap the active sheet');
   const rects=await page.evaluate(()=>{
    const box=id=>{const r=document.querySelector(id).getBoundingClientRect();return {x:r.left,y:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height}};
    return {sheet:box('#atelierContextWorkbench'),rail:box('#modelAtelierToolRail'),viewport:box('#modelAtelierViewport'),vv:{width:innerWidth,height:innerHeight},size:document.querySelector('#atelierContextWorkbench').dataset.mobileSize};
   });
   assert(rects.sheet.x>=-1&&rects.sheet.right<=width+1,JSON.stringify(rects));
   assert(rects.rail.x>=-1&&rects.rail.right<=width+1,JSON.stringify(rects));
   assert(rects.sheet.bottom<=rects.rail.y+2,'tool sheet must end above the thumb rail');
   assert(rects.sheet.y>=50,'mobile sheet must leave viewport space visible');
   assert.equal(rects.size,'half');
   const sizeControl=page.locator('#atelierMobileSheetSize');
   await sizeControl.click();
   assert.equal(await sheet.getAttribute('data-mobile-size'),'expanded');
   await sizeControl.click();
   assert.equal(await sheet.getAttribute('data-mobile-size'),'compact');
   const collapsed=await sheet.boundingBox();
   assert(collapsed.height<=56,'compact sheet must leave the 3D view open');
   await sizeControl.click();
   assert.equal(await sheet.getAttribute('data-mobile-size'),'half');
   const hand=page.locator('#atelierMobileHand');
   await hand.click();
   assert.equal(await page.locator('#modelAtelierPanel').getAttribute('data-atelier-handed'),'left');
   assert.equal(await rail.getAttribute('dir'),'ltr');
   await hand.click();
   assert.equal(await rail.getAttribute('dir'),'rtl');
   await rail.getByRole('button',{name:'Open Lasso editing tools'}).click();
   await sheet.getByRole('button',{name:'Paint mask',exact:true}).click();
   const input=page.locator('#atelierContextProxy_modelAtelierLassoPaintRadius');
   assert(await input.isVisible(),'selected tool must expose its actual radius control');
   await input.fill('.17');await input.dispatchEvent('change');
   assert.equal(await page.locator('#modelAtelierLassoPaintRadius').inputValue(),'.17');
   await sheet.getByRole('button',{name:'Favorite Paint mask',exact:true}).click();
   await sheet.getByRole('button',{name:'Quick',exact:true}).click();
   assert(await sheet.getByRole('button',{name:'Paint mask',exact:true}).isVisible(),'a starred case must remain in Quick');
   await sheet.getByRole('button',{name:'Recent',exact:true}).click();
   assert(await sheet.getByRole('button',{name:'Paint mask',exact:true}).isVisible(),'selected case must be in recent');
   await sheet.getByRole('button',{name:'All',exact:true}).click();
   await sheet.getByRole('button',{name:'Original inspector',exact:true}).click();
   assert(!(await sheet.isVisible()),'original inspector command closes the secondary sheet');
   assert(await page.locator('.atelier-inspector').isVisible(),'original native controls must be recoverable');
   // v11.60 remembers More as the last native choice; after the v11.61
   // contextual References sheet, selecting More again must not hide both.
   const more=rail.getByRole('button',{name:'Open More editing tools'});
   await more.click();
   await rail.getByRole('button',{name:'Open References editing tools'}).click();
   assert(await sheet.isVisible(),'References must open contextual tools');
   await more.click();
   assert(!(await sheet.isVisible()),'More must close contextual tools');
   assert(await page.locator('.atelier-inspector').isVisible(),'More must restore native tools even when already selected');
   // Outside the contextual sheet, More still toggles the legacy inspector.
   await more.click();
   assert(!(await page.locator('.atelier-inspector').isVisible()),'More must still hide the native-only inspector');
   await more.click();
   assert(await page.locator('.atelier-inspector').isVisible(),'More must reopen the native-only inspector');
  }else{
   assert(await page.locator('.atelier-inspector').isVisible(),'desktop keeps the v11.61 inspector');
   assert(await page.locator('#atelierContextWorkbench').isVisible());
  }
  assert.equal(errors.length,0,'No page errors for '+name+': '+errors.join('\n'));
  console.log('SWRLZ_MOBILE_LAYOUT_PASS',name,width,height);
  await ctx.close();
 }
}finally{await browser.close()}
