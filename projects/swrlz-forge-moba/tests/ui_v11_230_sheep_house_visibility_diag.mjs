// Focused viewport diagnostic: one 390px modeler session, 5 sheep houses.
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {PNG} from 'pngjs';
import assert from 'node:assert/strict';
const base='/tmp/se230-visibility';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const ids=['sheep-free-shelter','sheep-thatched-hut','sheep-cottage','sheep-barn','sheep-ram-house'];
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']});
try{
 const ctx=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
 await ctx.route('**/*',route=>{
  const url=new URL(route.request().url());
  if(url.origin===host){
   const rel=url.pathname==='/'?'index.html':url.pathname.replace(/^\/+/,'');
   const file=path.resolve(base,rel);
   if(file===base||!file.startsWith(base+'/')||!fs.existsSync(file))return route.fulfill({status:404,body:'not bundled'});
   return route.fulfill({status:200,path:file,contentType:rel.endsWith('.html')?'text/html':undefined});
  }
  if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'].includes(url.host))return route.continue();
  return route.abort();
 });
 const page=await ctx.newPage();
 page.on('pageerror',e=>console.log('SE230_PAGE_ERROR',String(e)));
 await page.goto(host+'/modeler.html?project=sheep-free-shelter',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_MODEL_ATELIER?.status?.().count===18,null,{timeout:30000});
 await page.evaluate(()=>{const dialog=document.getElementById('seReleaseNotesDialog');if(dialog?.open)dialog.close();});
 await page.waitForTimeout(2300);
 for(const id of ids){
  await page.evaluate(id=>window.SWYRL_ENGINE_SHEEP_BUILDING_STARTERS.open(id,true),id);
  await page.waitForTimeout(440);
  const info=await page.evaluate(()=>({
   overlay:document.elementFromPoint(195,350)?.id||document.elementFromPoint(195,350)?.tagName||null,
   releaseNotesOpen:document.getElementById('seReleaseNotesDialog')?.open,
   status:window.SWYRL_ENGINE_MODEL_ATELIER?.status?.(),
   view:window.SWYRL_ENGINE_VIEW?.status?.(),
   diagram:window.SE230_HOUSE_DIAG?.(),
   viewport:(()=>{const e=document.getElementById('modelAtelierViewport'),c=e?.querySelector('canvas');return {rect:e?.getBoundingClientRect().toJSON(),canvas:c?.getBoundingClientRect().toJSON(),canvasVisible:!!c?.getClientRects().length,css:c&&getComputedStyle(c).display}})()
  }));
  assert.equal(info.status.open,true,id+' active Model Atelier panel');
  const sizes={'sheep-free-shelter':18,'sheep-thatched-hut':59,'sheep-cottage':68,'sheep-barn':37,'sheep-ram-house':60};
  assert.equal(info.diagram?.meshes,sizes[id],id+' missing live renderer meshes');
  assert(info.diagram.intersectsView,id+' camera frustum misses model');
  assert(info.diagram.projectedCorners.every(([x,y,z])=>Math.abs(x)<.97&&Math.abs(y)<.97&&z>0&&z<1.01),id+' camera crops the full house');
  assert.equal(info.diagram.visible,info.diagram.meshes,id+' hidden meshes');
  const buf=await page.locator('#modelAtelierViewport canvas').screenshot();
  if(id==='sheep-free-shelter'||id==='sheep-barn'){
   const original=PNG.sync.read(buf),thumbnail=new PNG({width:195,height:356});
   for(let y=0;y<356;y++)for(let x=0;x<195;x++){
    const src=(Math.min(original.height-1,y*2)*original.width+Math.min(original.width-1,x*2))*4;
    const dst=(y*195+x)*4;
    for(let k=0;k<4;k++)thumbnail.data[dst+k]=original.data[src+k];
   }
   console.log('SE230_SCREENSHOT_BASE64_'+id,PNG.sync.write(thumbnail).toString('base64'));
  }
  const png=PNG.sync.read(buf),pixels=png.data;
  let chromatic=0,bright=0,red=0,gold=0,total=0;
  for(let y=0;y<png.height;y+=3)for(let x=0;x<png.width;x+=3){
   const i=(y*png.width+x)*4,r=pixels[i],g=pixels[i+1],b=pixels[i+2];total++;
   if(Math.max(r,g,b)-Math.min(r,g,b)>40&&Math.max(r,g,b)>65)chromatic++;
   if(Math.max(r,g,b)>180)bright++;
   if(r>g*1.3&&r>b*1.3&&r>70)red++;
   if(r>120&&g>85&&b<100)gold++;
  }
  console.log('SE230_VIEW',id,JSON.stringify(info),'pixels',JSON.stringify({width:png.width,height:png.height,chromatic,bright,red,gold,total}));
  if(id==='sheep-barn')assert(red>200,'Red barn should be visibly drawn after camera fit, not masked by overlays');
 }
 console.log('SE231_SHEEP_HOUSE_FULL_FRAMING_PASS');
 await ctx.close();
}finally{await browser.close();}
