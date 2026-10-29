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
  await page.locator('#modelAtelierReferenceFile').setInputFiles([
    {name:'front.png',mimeType:'image/png',buffer:png()},
    {name:'profile.png',mimeType:'image/png',buffer:png()}
  ]);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_REFERENCE.status().count===2);
  const refs=(await get()).references;
  assert.equal(refs[0].angle,'front');
  assert.equal(refs[1].angle,'right');
  await page.locator('#modelAtelierFaceSheetCreate').click();
  assert.equal((await get()).parts.length,284);
  assert(await page.locator('#modelAtelierFaceProfileTools').isVisible());
  const add=async(name,u,v,radius,depth)=>{
    await page.locator('#modelAtelierFaceLandmarkPreset').selectOption(name);
    await page.locator('#modelAtelierFaceLandmarkU').fill(String(u));
    await page.locator('#modelAtelierFaceLandmarkV').fill(String(v));
    await page.locator('#modelAtelierFaceLandmarkRadius').fill(String(radius));
    await page.locator('#modelAtelierFaceLandmarkDepth').fill(String(depth));
    await page.locator('#modelAtelierFaceLandmarkApply').click();
  };
  await add('noseTip',.5,.5,.15,.1);
  await add('eyeLeft',.32,.68,.1,-.05);
  let part=(await get()).parts.at(-1);
  assert.equal(part.faceSheet.landmarks.length,2);
  await page.locator('#modelAtelierFaceProfileReference').selectOption(refs[1].id);
  await page.locator('#modelAtelierFaceProfileOrigin').fill('.5');
  await page.locator('#modelAtelierFaceProfileScale').fill('1');
  await page.locator('#modelAtelierFaceProfileDirection').selectOption('1');
  await page.locator('#modelAtelierFaceProfileCalibrate').click();
  part=(await get()).parts.at(-1);
  assert.equal(part.faceSheet.profileGuide.refId,refs[1].id);
  assert.equal(part.faceSheet.profileGuide.originU,.5);
  await page.locator('#modelAtelierFaceLandmarkPreset').selectOption('noseTip');
  await page.locator('#modelAtelierFaceProfilePoint').fill('.7');
  await page.locator('#modelAtelierFaceProfileLink').click();
  part=(await get()).parts.at(-1);
  let nose=part.faceSheet.landmarks.find(l=>l.name==='noseTip');
  assert.equal(nose.profileU,.7);
  assert(Math.abs(nose.depth-.2)<1e-8);
  await page.locator('#modelAtelierFaceLandmarkPreset').selectOption('eyeLeft');
  await page.locator('#modelAtelierFaceProfilePoint').fill('.44');
  await page.locator('#modelAtelierFaceProfileLink').click();
  part=(await get()).parts.at(-1);
  let eye=part.faceSheet.landmarks.find(l=>l.name==='eyeLeft');
  assert.equal(eye.profileU,.44);
  assert(Math.abs(eye.depth+.06)<1e-8);
  await page.locator('#modelAtelierFaceProfilePoint').fill('.99');
  await page.locator('#modelAtelierFaceProfileLink').click();
  part=(await get()).parts.at(-1);
  assert.equal(part.faceSheet.landmarks.find(l=>l.name==='eyeLeft').profileU,.44,
    'Invalid image-derived depth must not alter saved landmark');
  await page.locator('#modelAtelierFaceProfileScale').fill('.5');
  await page.locator('#modelAtelierFaceProfileCalibrate').click();
  part=(await get()).parts.at(-1);
  assert.equal(part.faceSheet.profileGuide.unitsPerU,.5);
  assert(Math.abs(part.faceSheet.landmarks.find(l=>l.name==='noseTip').depth-.1)<1e-8);
  assert(Math.abs(part.faceSheet.landmarks.find(l=>l.name==='eyeLeft').depth+.03)<1e-8);
  const file=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await file).path(),json=JSON.parse(await readFile(path,'utf8'));
  assert.equal(json.model.parts.at(-1).faceSheet.profileGuide.refId,refs[1].id);
  assert.equal(json.model.parts.at(-1).faceSheet.landmarks.length,2);
  assert.equal(json.model.references.length,2);
  await page.locator('#modelAtelierUndo').click();
  assert.equal((await get()).parts.at(-1).faceSheet.profileGuide.unitsPerU,1);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier
    .parts.at(-1)?.faceSheet?.profileGuide?.unitsPerU===.5);
  const loaded=await get();
  assert.equal(loaded.parts.at(-1).faceSheet.landmarks.find(l=>l.name==='noseTip').profileU,.7);
  assert.equal(JSON.stringify(loaded.parts.slice(0,283)),originalParts);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1147_REAL_DESKTOP_ANDROID_FRONT_PROFILE_GUIDE_ACTUAL_DEPTH_NATIVE_UNDO_RELOAD_PASS',device);
  await context.close();
 }
}finally{await browser.close();}
