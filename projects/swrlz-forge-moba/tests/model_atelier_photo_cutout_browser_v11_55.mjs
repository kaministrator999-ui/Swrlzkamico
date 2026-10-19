import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
import {deflateSync} from 'node:zlib';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
function png(){
 const crc=b=>{let c=0xffffffff;for(const v of b){c^=v;for(let i=0;i<8;i++)c=c&1?(c>>>1)^0xedb88320:c>>>1;}return(c^0xffffffff)>>>0};
 const chunk=(name,bytes)=>{const header=Buffer.alloc(4),sum=Buffer.alloc(4),
  payload=Buffer.concat([Buffer.from(name),bytes]);header.writeUInt32BE(bytes.length);
  sum.writeUInt32BE(crc(payload));return Buffer.concat([header,payload,sum])};
 const hdr=Buffer.alloc(13);hdr.writeUInt32BE(16,0);hdr.writeUInt32BE(16,4);hdr[8]=8;hdr[9]=6;
 const arr=Buffer.alloc(16*(1+16*4));
 for(let y=0;y<16;y++)for(let x=0;x<16;x++){const at=y*65+1+x*4;arr[at]=x*15;arr[at+1]=150;arr[at+2]=y*15;arr[at+3]=255}
 return Buffer.concat([Buffer.from('89504e470d0a1a0a','hex'),chunk('IHDR',hdr),chunk('IDAT',deflateSync(arr)),chunk('IEND',Buffer.alloc(0))]);
}
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader',
 '--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile] of [['desktop',{width:1280,height:900},false],
  ['android-touch',{width:412,height:915},true]]){
  const ctx=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await ctx.newPage();page.setDefaultTimeout(80000);
  const errs=[];page.on('pageerror',e=>errs.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const get=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier);
  const before=await get();assert.equal(before.parts.length,283);
  await page.locator('#modelAtelierReferenceToggle').click();
  await page.locator('#modelAtelierReferenceFile').setInputFiles({name:'cutout.png',
   mimeType:'image/png',buffer:png()});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_REFERENCE.status().count===1);
  await page.locator('#modelAtelierFaceSheetCreate').click();
  let current=await get();assert.equal(current.parts.length,284);
  assert(await page.locator('#modelAtelierFaceCutoutTools').isVisible());
  const originalPhoto=current.references[0].data;
  const id=current.parts.at(-1).id;
  const polygon=[[.2,.2],[.8,.2],[.8,.8],[.2,.8]];
  await page.locator('#modelAtelierFaceCutoutPoints').fill(polygon.map(x=>x.join(',')).join('; '));
  await page.locator('#modelAtelierFaceCutoutFeather').fill('.045');
  await page.locator('#modelAtelierFaceCutoutApply').click();
  current=await get();
  const part=current.parts.at(-1);
  assert.deepEqual(part.faceSheet.cutout,{points:polygon,feather:.045});
  assert.equal(current.references[0].data,originalPhoto,'original photo must be unchanged');
  const exported=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await exported).path(),saved=JSON.parse(await readFile(path,'utf8'));
  assert.deepEqual(saved.model.parts.at(-1).faceSheet.cutout,part.faceSheet.cutout);
  assert.equal(saved.model.references[0].data,originalPhoto);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await get()).parts.at(-1).faceSheet.cutout,undefined);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.at(-1)?.faceSheet?.cutout?.points?.length===4);
  current=await get();
  assert.deepEqual(current.parts.at(-1).faceSheet.cutout,saved.model.parts.at(-1).faceSheet.cutout);
  // After native import, select the actual face-sheet part again and verify
  // source-image tap tracing, independent of numeric UV mask application.
  await page.locator('#modelAtelierParts').selectOption(id);
  await page.locator('#modelAtelierFaceCutoutStart').click();
  const frame=page.locator('#modelAtelierReferenceImageFrame');
  await frame.waitFor({state:'visible'});
  const layout=await frame.evaluate(e=>{
   const rect=e.getBoundingClientRect(),img=e.querySelector('img');
   const ratio=img.naturalWidth/img.naturalHeight;
   const w=Math.min(rect.width,rect.height*ratio),h=Math.min(rect.height,rect.width/ratio);
   return {x:(rect.width-w)/2,y:(rect.height-h)/2,w,h};
  });
  assert(layout.w>5&&layout.h>5);
  for(const [u,v] of [[.3,.3],[.7,.3],[.7,.7],[.3,.7]]){
   await frame.click({position:{x:layout.x+u*layout.w,y:layout.y+(1-v)*layout.h}});
  }
  assert.match(await page.locator('#modelAtelierFaceCutoutPoints').inputValue(),/0.3/);
  await page.locator('#modelAtelierFaceCutoutFinish').click();
  current=await get();
  assert.equal(current.parts.at(-1).faceSheet.cutout.points.length,4);
  assert.equal(current.parts.at(-1).faceSheet.cutout.feather,.045);
  assert.equal(current.references[0].data,originalPhoto);
  await page.locator('#modelAtelierFaceCutoutClear').click();
  assert.equal((await get()).parts.at(-1).faceSheet.cutout,undefined);
  assert.deepEqual(errs,[]);
  console.log('V1155_FACE_ALPHA_CUTOUT_NATIVE_BROWSER_UV_TAP_UNDO_EXPORT_IMPORT_PASS',device);
  await ctx.close();
 }
}finally{await browser.close();}
