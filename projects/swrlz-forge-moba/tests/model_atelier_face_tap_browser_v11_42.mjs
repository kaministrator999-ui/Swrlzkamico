import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFile} from 'node:fs/promises';
import {deflateSync} from 'node:zlib';
const root=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
function png(){
 const crc=b=>{let c=0xffffffff;for(const v of b){c^=v;for(let i=0;i<8;i++)c=c&1?(c>>>1)^0xedb88320:c>>>1;}return (c^0xffffffff)>>>0};
 const chunk=(type,data)=>{const payload=Buffer.concat([Buffer.from(type),data]),n=Buffer.alloc(4),end=Buffer.alloc(4);
 n.writeUInt32BE(data.length);end.writeUInt32BE(crc(payload));return Buffer.concat([n,payload,end])};
 const header=Buffer.alloc(13);header.writeUInt32BE(16,0);header.writeUInt32BE(16,4);header[8]=8;header[9]=6;
 const b=Buffer.alloc(16*(1+16*4));
 for(let y=0;y<16;y++)for(let x=0;x<16;x++){
 const i=y*65+1+x*4;b[i]=Math.round(255*x/16);b[i+1]=70;b[i+2]=Math.round(255*y/16);b[i+3]=255;
 }
 return Buffer.concat([Buffer.from('89504e470d0a1a0a','hex'),
 chunk('IHDR',header),chunk('IDAT',deflateSync(b)),chunk('IEND',Buffer.alloc(0))]);
}
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile]of[['desktop',{width:1280,height:900},false],
  ['android-touch',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(65000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const get=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier);
  const original=await get(),originalParts=JSON.stringify(original.parts);
  assert.equal(original.parts.length,283);
  await page.locator('#modelAtelierReferenceToggle').click();
  await page.locator('#modelAtelierReferenceFile').setInputFiles({
   name:'front.png',mimeType:'image/png',buffer:png()
  });
  await page.waitForFunction(()=>window.SWYRL_ENGINE_REFERENCE.status().count===1);
  await page.locator('#modelAtelierFaceSheetCreate').click();
  const created=await get();assert.equal(created.parts.length,284);
  assert(await page.locator('#modelAtelierFaceLandmarkTools').isVisible());
  await page.locator('#modelAtelierFaceLandmarkPreset').selectOption('noseTip');
  await page.locator('#modelAtelierFaceLandmarkPick').check();
  const refRect=await page.locator('#modelAtelierReferenceImageFrame').boundingBox();
  assert(refRect&&refRect.width>20&&refRect.height>20);
  await page.locator('#modelAtelierReferenceImageFrame').click({
    position:{x:Math.floor(refRect.width/2),y:Math.floor(refRect.height/2)}
  });
  const tapped=(await get()).parts.at(-1).faceSheet.landmarks;
  assert.equal(tapped?.length,1);
  assert.equal(tapped[0].name,'noseTip');
  assert(Math.abs(tapped[0].uv[0]-.5)<.025&&Math.abs(tapped[0].uv[1]-.5)<.025,
    'Touching center of actual contained image must land near UV center');
  await page.locator('#modelAtelierFaceLandmarkPick').uncheck();
  const contour=[.55,.75,.98,1,1,.9,.75,.9,1,1,.98,.75];
  await page.locator('#modelAtelierFaceContourValues').fill(contour.join(', '));
  await page.locator('#modelAtelierFaceContourApply').click();
  assert.deepEqual((await get()).parts.at(-1).faceSheet.contour,contour);
  await page.locator('#modelAtelierFaceContourValues').fill(Array(12).fill(2).join(', '));
  await page.locator('#modelAtelierFaceContourApply').click();
  assert.deepEqual((await get()).parts.at(-1).faceSheet.contour,contour,
    'Invalid face silhouette must leave saved geometry unchanged');
  await page.locator('#modelAtelierFaceLandmarkPreset').selectOption('noseTip');
  await page.locator('#modelAtelierFaceLandmarkU').fill('.5');
  await page.locator('#modelAtelierFaceLandmarkV').fill('.5');
  await page.locator('#modelAtelierFaceLandmarkRadius').fill('.15');
  await page.locator('#modelAtelierFaceLandmarkDepth').fill('.2');
  await page.locator('#modelAtelierFaceLandmarkApply').click();
  let part=(await get()).parts.at(-1);
  assert.deepEqual(part.faceSheet.landmarks,[{name:'noseTip',uv:[.5,.5],radius:.15,depth:.2}]);
  await page.locator('#modelAtelierFaceLandmarkPreset').selectOption('eyeLeft');
  await page.locator('#modelAtelierFaceLandmarkU').fill('.32');
  await page.locator('#modelAtelierFaceLandmarkV').fill('.68');
  await page.locator('#modelAtelierFaceLandmarkRadius').fill('.12');
  await page.locator('#modelAtelierFaceLandmarkDepth').fill('-.12');
  await page.locator('#modelAtelierFaceLandmarkApply').click();
  part=(await get()).parts.at(-1);assert.equal(part.faceSheet.landmarks.length,2);
  await page.locator('#modelAtelierFaceSheetHeadDepth').fill('.65');
  await page.locator('#modelAtelierFaceSheetApply').click();
  part=(await get()).parts.at(-1);assert.equal(part.faceSheet.headDepth,.65);
  assert.equal(part.faceSheet.landmarks.length,2);
  await page.locator('#modelAtelierFaceLandmarkDepth').fill('.6');
  await page.locator('#modelAtelierFaceLandmarkApply').click();
  part=(await get()).parts.at(-1);
  assert.equal(part.faceSheet.landmarks.find(x=>x.name==='eyeLeft').depth,-.12,
    'Invalid feature depth may not mutate the project');
  const dl=page.waitForEvent('download');await page.locator('#modelAtelierExport').click();
  const path=await(await dl).path(),json=JSON.parse(await readFile(path,'utf8'));
  assert.equal(json.model.parts.at(-1).faceSheet.landmarks.length,2);
  assert.deepEqual(json.model.parts.at(-1).faceSheet.contour,contour);
  assert.equal(json.model.references.length,1);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await get()).parts.at(-1).faceSheet.headDepth,0);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await get()).parts.at(-1).faceSheet.landmarks.length,1);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier
    .parts.at(-1)?.faceSheet?.landmarks?.length===2);
  const loaded=await get();
  assert.equal(loaded.parts.at(-1).faceSheet.headDepth,.65);
  assert.deepEqual(loaded.parts.at(-1).faceSheet.contour,contour);
  assert.equal(JSON.stringify(loaded.parts.slice(0,283)),originalParts);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1142_REAL_ANDROID_TAP_REFERENCE_UV_CONTOUR_FACE_SAVED_PASS',device);
  await context.close();
 }
}finally{await browser.close();}
