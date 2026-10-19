import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
import {deflateSync} from 'node:zlib';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:[
  '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader',
  '--use-gl=angle','--use-angle=swiftshader'
]});
function pngSolid(r,g,b){
 // Valid deterministic 4x4 RGBA PNG, no external image/stock assets.
 const crc=(data)=>{let c=0xffffffff;for(const v of data){c^=v;for(let i=0;i<8;i++)c=c&1?(c>>>1)^0xedb88320:c>>>1;}return (c^0xffffffff)>>>0;};
 const chunk=(type,data)=>{
   const t=Buffer.from(type),payload=Buffer.concat([t,data]),size=Buffer.alloc(4),sum=Buffer.alloc(4);
   size.writeUInt32BE(data.length);sum.writeUInt32BE(crc(payload));
   return Buffer.concat([size,payload,sum]);
 };
 const header=Buffer.alloc(13);header.writeUInt32BE(4,0);header.writeUInt32BE(4,4);header[8]=8;header[9]=6;
 const pixels=Buffer.alloc(4*(1+4*4),0);
 for(let y=0;y<4;y++)for(let x=0;x<4;x++){
   const i=y*17+1+x*4;pixels[i]=r;pixels[i+1]=g;pixels[i+2]=b;pixels[i+3]=255;
 }
 return Buffer.concat([
   Buffer.from('89504e470d0a1a0a','hex'),
   chunk('IHDR',header),chunk('IDAT',deflateSync(pixels)),chunk('IEND',Buffer.alloc(0))
 ]);
}
try{
 for(const [device,viewport,mobile]of[['desktop',{width:1280,height:900},false],
   ['android-touch',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(60000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const get=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier);
  const before=await get(),head=before.parts.find(p=>p.id==='model-0001');
  assert.equal(before.parts.length,283);
  await page.locator('#modelAtelierReferenceToggle').click();
  await page.locator('#modelAtelierReferenceFile').setInputFiles([
    {name:'front.png',mimeType:'image/png',buffer:pngSolid(233,93,45)},
    {name:'side.png',mimeType:'image/png',buffer:pngSolid(44,121,222)}
  ]);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_REFERENCE.status().count===2);
  const first=await get(),front=first.references[0],side=first.references[1];
  assert.equal(first.referenceLayout.active,front.id);
  await page.locator('#modelAtelierReferenceCompare').selectOption(side.id);
  const selected=await get();
  assert.equal(selected.referenceLayout.compareId,side.id);
  const second=page.locator('#modelAtelierReferenceCompareImage');
  assert(await second.isVisible());
  assert((await second.getAttribute('src')).startsWith('data:image/'));
  assert.equal(await second.getAttribute('data-ref-id'),side.id);
  assert.notEqual(await page.locator('#modelAtelierReferenceImage').getAttribute('src'),
    await second.getAttribute('src'),'Front and side view must differ');
  const box=await page.locator('#modelAtelierReferenceDock').boundingBox();
  assert(box?.width<=viewport.width);
  assert(box?.height<=viewport.height);
  // Changing the active tab to the side image swaps the compare target,
  // preserving two simultaneous *different* images.
  await page.locator('#modelAtelierReferenceTabs button').nth(1).click();
  let pair=await get();
  assert.equal(pair.referenceLayout.active,side.id);
  assert.equal(pair.referenceLayout.compareId,front.id);
  const opacity=page.locator('#modelAtelierReferenceOpacity');
  await opacity.evaluate(el=>{el.value='.45';el.dispatchEvent(new Event('change',{bubbles:true}));});
  pair=await get();assert.equal(pair.references.find(r=>r.id===side.id).opacity,.45);
  await page.locator('#modelAtelierReferenceTabs button').nth(0).click();
  pair=await get();
  assert.equal(pair.referenceLayout.active,front.id);
  assert.equal(pair.referenceLayout.compareId,side.id);
  assert.equal(await second.getAttribute('data-ref-id'),side.id);
  assert.equal(Number(await second.evaluate(el=>el.style.opacity)),.45);
  const dl=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const file=await(await dl).path(),saved=JSON.parse(await readFile(file,'utf8'));
  assert.equal(saved.model.referenceLayout.compareId,side.id);
  assert.equal(saved.model.references.find(r=>r.id===side.id).opacity,.45);
  await page.locator('#modelAtelierReferenceCompare').selectOption('');
  assert.equal((await get()).referenceLayout.compareId,null);
  assert(await page.locator('#modelAtelierReferenceComparePane').isHidden());
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await get()).referenceLayout.compareId,side.id);
  assert(await second.isVisible());
  await page.locator('#modelAtelierImportFile').setInputFiles(file);
  await page.waitForFunction(id=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier
   .referenceLayout.compareId===id,side.id);
  pair=await get();assert.equal(pair.references.length,2);
  assert.equal(pair.parts.length,283);
  assert.deepEqual(pair.parts.find(p=>p.id==='model-0001').headAnatomy,head.headAnatomy);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1145_SIDE_BY_SIDE_REFERENCES_DESKTOP_ANDROID_INDEPENDENT_TRANSFORMS_NATIVE_PASS',device);
  await context.close();
 }
}finally{await browser.close();}
