import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
import {deflateSync} from 'node:zlib';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
function png(){
 const crc=b=>{let c=0xffffffff;for(const v of b){c^=v;for(let i=0;i<8;i++)c=c&1?(c>>>1)^0xedb88320:c>>>1;}return(c^0xffffffff)>>>0};
 const chunk=(kind,d)=>{const s=Buffer.from(kind),body=Buffer.concat([s,d]),l=Buffer.alloc(4),end=Buffer.alloc(4);
  l.writeUInt32BE(d.length);end.writeUInt32BE(crc(body));return Buffer.concat([l,body,end]);};
 const h=Buffer.alloc(13);h.writeUInt32BE(16,0);h.writeUInt32BE(16,4);h[8]=8;h[9]=6;
 const raw=Buffer.alloc(16*65);
 for(let y=0;y<16;y++)for(let x=0;x<16;x++){const i=y*65+1+x*4;raw[i]=90;raw[i+1]=x*15;raw[i+2]=y*15;raw[i+3]=255;}
 return Buffer.concat([Buffer.from('89504e470d0a1a0a','hex'),chunk('IHDR',h),chunk('IDAT',deflateSync(raw)),chunk('IEND',Buffer.alloc(0))]);
}
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile]of[['desktop',{width:1280,height:900},false],
  ['android',{width:412,height:915},true]]){
  const ctx=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await ctx.newPage();page.setDefaultTimeout(90000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const data=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier);
  const original=await data();assert.equal(original.parts.length,283);
  await page.locator('#modelAtelierReferenceToggle').click();
  await page.locator('#modelAtelierReferenceFile').setInputFiles([
   {name:'front.png',mimeType:'image/png',buffer:png()},
   {name:'profile.png',mimeType:'image/png',buffer:png()}]);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_REFERENCE.status().count===2);
  const refIds=(await data()).references.map(x=>x.id);
  await page.locator('#modelAtelierReferenceFloatOpen').click();
  if(await page.locator('.atelier-float-reference').count()!==1){
   const diag=await page.evaluate(()=>({
    host:!!document.querySelector('#modelAtelierFloatingReferences'),
    hostHtml:document.querySelector('#modelAtelierFloatingReferences')?.innerHTML?.slice(0,300),
    viewport:document.querySelector('#modelAtelierViewport')?.getBoundingClientRect().toJSON(),
    statuses:[...document.querySelectorAll('[role="status"]')]
      .filter(x=>/Reference|Status/.test(x.id)).map(x=>[x.id,x.textContent?.slice(0,250)])
   }));
   console.error('V1157_FLOAT_OPEN_DIAGNOSTIC',device,JSON.stringify({
    nativeRefs:(await data()).references.map(r=>({name:r.name,floatWindow:r.floatWindow})),
    pageErrors:errors,...diag
   }));
  }
  assert.equal(await page.locator('.atelier-float-reference').count(),1);
  await page.locator('#modelAtelierReferenceTabs button').nth(1).click();
  await page.locator('#modelAtelierReferenceFloatOpen').click();
  assert.equal(await page.locator('.atelier-float-reference').count(),2,
   'two actual independent floating photo panels must coexist');
  let refs=(await data()).references;
  assert(refs.every(r=>r.floatWindow?.open===true));
  assert.notDeepEqual(refs[0].floatWindow,refs[1].floatWindow);
  const header=page.locator('.atelier-float-reference').first().locator('.atelier-float-reference-handle');
  const bounds=await header.boundingBox();assert(bounds&&bounds.width>100);
  const sx=bounds.x+28,sy=bounds.y+17;
  const orig=refs[0].floatWindow;
  const otherOriginal=JSON.parse(JSON.stringify(refs[1].floatWindow));
  if(mobile){
   const session=await ctx.newCDPSession(page);
   await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:sx,y:sy,id:6}]});
   for(let i=1;i<=8;i++)await session.send('Input.dispatchTouchEvent',{
    type:'touchMove',touchPoints:[{x:sx+i*3,y:sy+i*2,id:6}]
   });
   await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  }else{
   await page.mouse.move(sx,sy);await page.mouse.down();
   await page.mouse.move(sx+24,sy+16,{steps:9});await page.mouse.up();
  }
  refs=(await data()).references;
  if(refs[0].floatWindow.x===orig.x&&refs[0].floatWindow.y===orig.y){
   const dbg=await page.evaluate(({x,y})=>{
    const el=document.elementFromPoint(x,y);
    const host=document.querySelector('#modelAtelierFloatingReferences');
    const panel=host?.querySelector('.atelier-float-reference');
    const hdr=panel?.querySelector('.atelier-float-reference-handle');
    return {
     atPointer:{tag:el?.tagName,id:el?.id,classes:el?.className,parent:el?.parentElement?.className},
     host:!!host,panelCount:host?.children.length,headDataset:{...hdr?.dataset},
     headBounds:hdr?.getBoundingClientRect().toJSON(),panelStyle:panel?.getAttribute('style'),
     status:document.querySelector('#modelAtelierStatus')?.textContent
    };
   },{x:sx,y:sy});
   console.error('V1157_DRAG_DIAGNOSTIC',device,JSON.stringify({
    start:{x:sx,y:sy},orig,after:refs[0].floatWindow,errors,...dbg
   }));
  }
  assert(refs[0].floatWindow.x!==orig.x||refs[0].floatWindow.y!==orig.y,
    'dragging own header saves native per-image position');
  assert.deepEqual(refs[1].floatWindow,otherOriginal,
    'other window must remain independently placed');
  const snapshot=JSON.parse(JSON.stringify(refs.map(r=>r.floatWindow)));
  const dl=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await dl).path(),saved=JSON.parse(await readFile(path,'utf8'));
  assert.deepEqual(saved.model.references.map(r=>r.floatWindow),snapshot);
  await page.locator('#modelAtelierUndo').click();
  assert.notDeepEqual((await data()).references.map(r=>r.floatWindow),snapshot);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  // Both windows were already open *before* importing. Wait for the
  // specifically restored coordinates, not merely a pre-existing count.
  await page.waitForFunction(({id,x,y})=>{
   const refs=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.references||[];
   const chosen=refs.find(r=>r.id===id);
   return refs.filter(r=>r.floatWindow?.open).length===2&&
     chosen?.floatWindow?.x===x&&chosen?.floatWindow?.y===y;
  },{id:refIds[0],x:snapshot[0].x,y:snapshot[0].y});
  const restored=await data();
  assert.deepEqual(restored.references.map(r=>r.floatWindow),snapshot);
  assert.deepEqual(restored.references.map(r=>r.id),refIds);
  assert.equal(restored.parts.length,283);
  assert.equal(await page.locator('.atelier-float-reference').count(),2);
  await page.locator('#modelAtelierReferenceFloatCloseAll').click();
  assert.equal((await data()).references.filter(r=>r.floatWindow.open).length,0);
  assert.equal(await page.locator('.atelier-float-reference').count(),0);
  assert.deepEqual(errors,[]);
  console.log('V1157_INDEPENDENT_FLOATING_REFERENCES_DESKTOP_ANDROID_DRAG_UNDO_IMPORT_PASS',device);
  await ctx.close();
 }
}finally{await browser.close();}
