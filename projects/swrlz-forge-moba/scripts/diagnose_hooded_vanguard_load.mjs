import {chromium} from 'playwright';
import {writeFile} from 'node:fs/promises';
const base=process.env.SWYRL_TEST_URL||'https://kamiloki-swrlz-forge-moba.static.hf.space';
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const context=await browser.newContext({viewport:{width:412,height:900},deviceScaleFactor:1,isMobile:true,hasTouch:true});
const page=await context.newPage();
const errors=[],messages=[];
page.on('pageerror',e=>errors.push('PAGE_ERROR '+String(e?.stack||e)));
page.on('console',msg=>{if(['warning','error'].includes(msg.type()))errors.push('CONSOLE_'+msg.type()+' '+msg.text());else if(messages.length<8)messages.push(msg.text().slice(0,240));});
page.on('dialog',dialog=>dialog.accept());
let navigation=null;
try{
 navigation=await page.goto(base+'/index.html?project=hooded-vanguard&modeldiag='+Date.now(),{waitUntil:'domcontentloaded',timeout:70000});
 await page.waitForFunction(()=>!!window.SWYRL_ENGINE_HOODED_VANGUARD,{timeout:70000}).catch(e=>errors.push('REGISTER_TIMEOUT '+e.message.slice(0,180)));
 await page.waitForTimeout(16000);
 const receipt=await page.evaluate(()=>{
  const mod=window.SWYRL_ENGINE_HOODED_VANGUARD;
  const status=mod?.status?.()||{};
  const atelier=window.SWYRL_ENGINE_MODEL_ATELIER?.status?.()||{};
  const hub=window.SWYRL_ENGINE_PROJECT_HUB_285?.status?.()||{};
  let counts={};
  try{counts={card:document.querySelectorAll('[data-project-template="hooded-vanguard"]').length,modelCards:document.querySelectorAll('#se236StarterModels [data-project-template="hooded-vanguard"]').length}}catch(e){counts.error=String(e)}
  const canvas=Array.from(document.querySelectorAll('canvas')).map(c=>({w:c.width,h:c.height,display:getComputedStyle(c).display})).slice(0,20);
  const toastNodes=Array.from(document.querySelectorAll('[role="status"],[class*="toast"],#modelAtelierStatus')).map(e=>e.textContent?.trim().slice(0,240)).filter(Boolean).slice(-10);
  return {build:window.SWRLZ_FORGE_BUILD?.version,status,atelier,hub,counts,canvas,toastNodes,project:window.currentProject?.projectName||window.currentProject?.name,modelName:window.currentProject?.modelAtelier?.name,modelParts:window.currentProject?.modelAtelier?.parts?.length,workspace:window.SWYRL_ENGINE_WORKSPACES?.status?.()};
 });
 const output={httpStatus:navigation?.status(),...receipt,errors,messages,now:new Date().toISOString()};
 console.log('VANGUARD_NATIVE_LOAD_RECEIPT',JSON.stringify(output));
 try{await page.screenshot({path:'vanguard-load-diagnostic.png',fullPage:false,timeout:12000})}catch(e){console.log('SCREENSHOT_UNAVAILABLE',e.message)}
 await writeFile('vanguard-load-diagnostic.json',JSON.stringify(output,null,2));
 if(!receipt.status?.successes||!receipt.atelier?.open||!receipt.atelier?.count)process.exitCode=2;
}catch(error){console.error('VANGUARD_BROWSER_EXCEPTION',error.stack);process.exitCode=3}
finally{await context.close();await browser.close();}
