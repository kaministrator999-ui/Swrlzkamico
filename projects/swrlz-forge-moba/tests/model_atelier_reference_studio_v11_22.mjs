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
 for(const [name,viewport,isMobile] of [
  ['desktop',{width:1366,height:900},false],
  ['mobile',{width:412,height:915},true]
 ]){
  const context=await browser.newContext({viewport,isMobile,hasTouch:isMobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(60000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const get=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier);
  let m=await get();
  const partsBefore=JSON.stringify(m.parts);
  assert.equal(m.parts.length,283,'Must use Codex head and all native parts');
  assert(m.parts.find(x=>x.id==='model-0001').headAnatomy,'Reference extension must preserve original anatomical head');
  const toggle=page.locator('#modelAtelierReferenceToggle');
  assert(await toggle.isVisible(),'Floating reference launcher should be in viewport toolbar');
  await toggle.click();
  assert(await page.locator('#modelAtelierReferenceDock').isVisible());
  // A floating image must NEVER hide the scene-wide render-mode controls.
  // This especially matters on phones where the toolbar wraps to extra rows.
  const toolbarBox=await page.locator('#modelAtelierViewportModes').boundingBox();
  const refBox=await page.locator('#modelAtelierReferenceDock').boundingBox();
  assert(toolbarBox&&refBox&&refBox.y>=toolbarBox.y+toolbarBox.height+3,
    'Floating reference studio must stay below the render modes on '+name);
  const display=page.locator('#modelAtelierViewportMode');
  await display.selectOption('wireframe');
  const view=await page.evaluate(()=>window.SWYRL_ENGINE_VIEW.status());
  assert.equal(view.wireframe,283,'Wireframe must work while References is open');
  await display.selectOption('shaded');
  await page.locator('#modelAtelierReferenceFile').setInputFiles([
    {name:'front-reference.png',mimeType:'image/png',buffer:pngSolid(255,70,65)},
    {name:'right-reference.png',mimeType:'image/png',buffer:pngSolid(52,220,240)}
  ]);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_REFERENCE?.status().count===2);
  m=await get();
  assert.equal(m.references.length,2);
  assert(m.references.every(r=>r.data.startsWith('data:image/')&&r.data.length<240000));
  assert.equal(m.references[0].angle,'front');
  assert.equal(m.references[1].angle,'right');
  assert.equal(JSON.stringify(m.parts),partsBefore,'Loading references must not change character geometry');
  assert(await page.locator('#modelAtelierReferenceImage').isVisible(),'First reference should render inside overlay');
  const tabs=page.locator('#modelAtelierReferenceTabs button');assert.equal(await tabs.count(),2);
  const mobileRects=await page.evaluate(()=>{
    const names=['modelAtelierViewport','modelAtelierViewportModes','modelAtelierReferenceDock','modelAtelierReferenceHandle','modelAtelierReferenceBody','modelAtelierReferenceTabs'];
    return Object.fromEntries(names.map(id=>{const e=document.getElementById(id),r=e.getBoundingClientRect();
      return [id,{x:r.x,y:r.y,bottom:r.bottom,height:r.height,scrollTop:e.scrollTop,scrollHeight:e.scrollHeight,
        clientHeight:e.clientHeight,top:e.style.top,z:window.getComputedStyle(e).zIndex}]}));
  });
  console.log('REFERENCE_LAYOUT_AFTER_IMPORT',name,JSON.stringify(mobileRects));
  assert(mobileRects.modelAtelierReferenceDock.y>=mobileRects.modelAtelierViewportModes.bottom+3,
    'After import the reference panel must still be below render modes.');
  await tabs.nth(1).click({timeout:12000});
  assert.equal(await page.locator('#modelAtelierReferenceAngle').inputValue(),'right');
  await page.locator('#modelAtelierReferenceCamera').click();
  const yaw=Number(await page.locator('#modelAtelierViewport').getAttribute('data-camera-yaw'));
  assert(Math.abs(yaw-Math.PI/2)<.02,'Right reference should align the camera to a right-side view');
  await page.locator('#modelAtelierReferenceFlip').click();
  await page.locator('#modelAtelierReferenceRotateRight').click();
  await page.locator('#modelAtelierReferenceZoom').evaluate(el=>{
    el.value='1.9';el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  });
  await page.locator('#modelAtelierReferenceOpacity').evaluate(el=>{
    el.value='.55';el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  });
  m=await get();
  const ref=m.references[1];assert(ref.mirror&&ref.rotation===90);
  assert.equal(ref.zoom,1.9);assert.equal(ref.opacity,.55);
  // Collapsing keeps a touch-friendly floating thumbnail; expanding restores
  // transforms, and neither action edits the modeled character.
  await page.locator('#modelAtelierReferenceCollapse').click();
  assert((await page.locator('#modelAtelierReferenceDock').getAttribute('class')).includes('collapsed'));
  assert(await page.locator('#modelAtelierReferenceThumbnail').isVisible(),'Collapsed overlay must display a clickable image thumbnail');
  await page.locator('#modelAtelierReferenceThumbnail').click();
  assert(await page.locator('#modelAtelierReferenceImageFrame').isVisible());
  // Remove and Undo using actual native model history with references included.
  await page.locator('#modelAtelierReferenceDelete').click();
  assert.equal((await get()).references.length,1);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await get()).references.length,2,'Undo should restore removed portable reference');
  const downloadPromise=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const download=await downloadPromise;
  const jsonPath=await download.path();const parsed=JSON.parse(await readFile(jsonPath,'utf8'));
  assert.equal(parsed.schema,'swyrl-model-atelier-v1');
  assert.equal(parsed.model.references.length,2);
  assert.equal(parsed.model.referenceLayout.open,true);
  assert.equal(JSON.stringify(parsed.model.parts),partsBefore);
  await page.locator('#modelAtelierReferenceClose').click();
  assert(!(await page.locator('#modelAtelierReferenceDock').isVisible()));
  await page.locator('#modelAtelierImportFile').setInputFiles(jsonPath);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_REFERENCE.status().open===true);
  m=await get();
  assert.equal(m.references.length,2,'Save/Import must keep embedded photos');
  assert.equal(m.references[1].zoom,1.9);
  assert.equal(m.references[1].rotation,90);
  assert.equal(JSON.stringify(m.parts),partsBefore,'Import must not alter original model geometry');
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1122_REFERENCE_STUDIO_IMPORT_FLOATING_ANGLE_SAVE_RELOAD_UNDO_PASS',name,m.parts.length,m.references.length);
  await context.close();
 }
}finally{await browser.close();}
