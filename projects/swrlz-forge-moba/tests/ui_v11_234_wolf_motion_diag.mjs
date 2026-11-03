// Focused reproduction of owner's Astra Wolf screenshot: animation timing and skin deformation.
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {PNG} from 'pngjs';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const base='/tmp/se234-wolf-diagnostic';
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
function compare(a,b){
 const A=PNG.sync.read(a),B=PNG.sync.read(b);if(A.width!==B.width||A.height!==B.height)return {dimensionMismatch:true};
 let checked=0,changed=0,squareDiff=0;
 for(let y=0;y<A.height;y+=6)for(let x=0;x<A.width;x+=6){
  let i=(y*A.width+x)*4,delta=Math.max(...[0,1,2].map(j=>Math.abs(A.data[i+j]-B.data[i+j])));
  checked++;if(delta>16)changed++;squareDiff+=delta*delta;
 }
 return {changed,checked,ratio:+(changed/checked).toFixed(4),rms:+Math.sqrt(squareDiff/checked).toFixed(2)};
}
try{
 const ctx=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 await ctx.route('**/*',route=>{
  const u=new URL(route.request().url());
  if(u.origin===host){
   const rel=u.pathname==='/'?'index.html':u.pathname.replace(/^\/+/,'');
   const file=path.resolve(base,rel);
   if(file===base||!file.startsWith(base+'/')||!fs.existsSync(file))return route.fulfill({status:404,body:'not bundled'});
   return route.fulfill({status:200,path:file,contentType:rel.endsWith('.html')?'text/html':undefined});
  }
  if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'].includes(u.hostname))return route.continue();
  return route.abort();
 });
 const page=await ctx.newPage();
 page.on('pageerror',e=>console.log('SE234_PAGE_ERROR',String(e).slice(0,650)));
 await page.goto(host+'/index.html',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>typeof window.SWYRL_ENGINE_MODEL_ATELIER?.loadAnimal==='function',null,{timeout:35000});
 const ok=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.loadAnimal('wolf',{force:true}));
 console.log('SE234_LOAD',ok);
 await page.waitForFunction(()=>window.SWYRL_ENGINE_WOLF_RIG?.status?.().skinned&&window.SWYRL_ENGINE_WORKSPACES?.active?.()==='modeler'&&window.SE234_WOLF_DIAG,null,{timeout:60000});
 const before=await page.evaluate(()=>window.SE234_WOLF_DIAG());
 console.log('SE234_NEUTRAL',JSON.stringify(before).slice(0,11000));
 await page.evaluate(()=>{const e=document.getElementById('seReleaseNotesDialog');if(e?.open)e.close();});
 const c=page.locator('#modelAtelierViewport canvas');
 const shots=[];
 const capture=async label=>{
  const data=await page.evaluate(()=>window.SE234_WOLF_DIAG());
  const png=await c.screenshot();shots.push({label,png,data});
  console.log('SE234_FRAME',label,JSON.stringify(data).slice(0,4400));
 };
 await capture('before');
 await page.evaluate(()=>{
   const clip=document.getElementById('modelAtelierWolfClip');
   clip.value='run';clip.dispatchEvent(new Event('change',{bubbles:true}));
   document.getElementById('modelAtelierWolfPlay').click();
 });
 await page.waitForTimeout(280);await capture('run280');
 await page.waitForTimeout(350);await capture('run630');
 await page.waitForTimeout(360);await capture('run990');
 await page.waitForTimeout(420);await capture('run1410');
 for(let i=1;i<shots.length;i++)console.log('SE234_PIXEL_DIFF',shots[i-1].label,shots[i].label,JSON.stringify(compare(shots[i-1].png,shots[i].png)));
 const first=shots[1].data,last=shots.at(-1).data;
 console.log('SE234_SUMMARY',JSON.stringify({
  initialFrame:before.frameCount,finalFrame:last.frameCount,
  renderCalls:await page.evaluate(()=>window.SE234_RENDER_CALLS||0),
  frameDelta:last.frameCount-before.frameCount,
  renderDelta:last.renderFrame-before.renderFrame,
  initialHead:before.head,lastHead:last.head,
  samples:shots.map(x=>({label:x.label,elapsed:x.data.elapsed,frame:x.data.frameCount,render:x.data.renderFrame,fore:x.data.fore,tail:x.data.tail})),
  partsByRegion:before.partsByRegion,
  weirdParts:before.unmatchedParts
 }).slice(0,15000));
 await ctx.close();
}finally{await browser.close();}
