import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {PNG} from 'pngjs';
import fs from 'node:fs';
import path from 'node:path';
const root='/tmp/se233-wolf-animation',host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
const errs=[];
function diff(a,b){
 const p=PNG.sync.read(a),q=PNG.sync.read(b);assert.equal(p.width,q.width);assert.equal(p.height,q.height);
 let changed=0;
 for(let i=0;i<p.data.length;i+=16){
  const d=Math.abs(p.data[i]-q.data[i])+Math.abs(p.data[i+1]-q.data[i+1])+Math.abs(p.data[i+2]-q.data[i+2]);
  if(d>40)changed++;
 }
 return changed;
}
try{
 const c=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 await c.route('**/*',route=>{
  const u=new URL(route.request().url());
  if(u.origin===host){
   const rel=u.pathname==='/'?'index.html':u.pathname.replace(/^\/+/,'');
   const file=path.resolve(root,rel);
   if(file===root||!file.startsWith(root+'/')||!fs.existsSync(file))return route.fulfill({status:404,body:'not packaged'});
   return route.fulfill({status:200,path:file,contentType:rel.endsWith('.html')?'text/html':undefined});
  }
  if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'].includes(u.hostname))return route.continue();
  return route.abort();
 });
 const page=await c.newPage();
 page.on('pageerror',e=>{errs.push(String(e));console.log('SE233_PAGE_ERROR',String(e))});
 await page.goto(host+'/modeler.html?project=wolf-model',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_WOLF_RIG?.status?.().skinned===true &&
  window.SWYRL_ENGINE_MODEL_ATELIER?.status?.().open===true,null,{timeout:45000});
 await page.evaluate(()=>document.getElementById('seReleaseNotesDialog')?.close?.());
 const canvas=page.locator('#modelAtelierViewport canvas');
 const info=await page.evaluate(()=>({state:window.SWYRL_ENGINE_WOLF_RIG.status(),
   zoom:document.querySelector('#modelAtelierZoom')?.textContent||'',
   count:window.SWYRL_ENGINE_MODEL_ATELIER.status().count}));
 console.log('SE233_INITIAL_WOLF',JSON.stringify(info));
 assert(info.state.skinnedMeshes>=50);
 await page.evaluate(()=>{const e=document.getElementById('modelAtelierWolfClip');if(!e)throw Error('Wolf clip selector missing');e.value='run';e.dispatchEvent(new Event('change',{bubbles:true}));});
 const previous=await canvas.screenshot();
 await page.evaluate(()=>{const e=document.getElementById('modelAtelierWolfPlay');if(!e)throw Error('Wolf Play button missing');e.click()});
 await page.waitForTimeout(150);
 const one=await canvas.screenshot();
 const snap1=await page.evaluate(()=>window.SE233_WOLF_INSPECT?.());
 await page.waitForTimeout(210);
 const two=await canvas.screenshot();
 const snap2=await page.evaluate(()=>window.SE233_WOLF_INSPECT?.());
 console.log('SE233_NO_ORBIT_SAMPLE',JSON.stringify({one:snap1,two:snap2,changedFromRest:diff(previous,one),changedDuringRun:diff(one,two)}));
 assert.equal(snap1?.playing,true);
 assert.equal(snap2?.playing,true);
 assert(snap1?.time>=0&&snap2?.time>=0,'Playback clock not progressing');
 assert(diff(one,two)>100,'Run animation not updating viewport with a stationary camera');
 assert(diff(previous,one)>100,'Run pose never changed from neutral before camera input');
 assert(snap1.poseFore!==snap2.poseFore,'Joint angle unchanged across different run samples');
 // Stop and scrub without moving camera; static pose must persist.
 await page.click('#modelAtelierWolfPlay');
 assert.equal((await page.evaluate(()=>window.SE233_WOLF_INSPECT?.().playing)),false);
 assert.equal(errs.length,0,'Unexpected script exceptions');
 console.log('SE233_WOLF_NO_CAMERA_ORBIT_PLAYBACK_PASS');
 await c.close();
}finally{await browser.close()}
