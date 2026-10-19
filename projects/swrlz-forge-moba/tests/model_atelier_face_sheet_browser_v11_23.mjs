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
 ['mobile',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(45000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const project=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier);
  const base=await project(),partsBefore=JSON.stringify(base.parts);
  assert.equal(base.parts.length,283);
  await page.locator('#modelAtelierReferenceToggle').click();
  await page.locator('#modelAtelierReferenceFile').setInputFiles({
   name:'face-reference.png',mimeType:'image/png',buffer:png()
  });
  await page.waitForFunction(()=>window.SWYRL_ENGINE_REFERENCE.status().count===1);
  await page.locator('#modelAtelierFaceSheetCreate').click();
  const data=await project();
  assert.equal(data.parts.length,284,'One separate native sculptable face surface must be added');
  assert.equal(JSON.stringify(data.parts.slice(0,283)),partsBefore,'Original Codex head/character stays unchanged');
  const face=data.parts.at(-1);
  assert.equal(face.kind,'faceSheet');
  assert.equal(face.faceSheet.shape,'oval');
  assert.equal(face.faceSheet.refId,data.references[0].id);
  assert(await page.locator('#modelAtelierFaceSheetControls').isVisible());
  await page.locator('#modelAtelierFaceSheetGridU').fill('60');
  await page.locator('#modelAtelierFaceSheetGridV').fill('26');
  await page.locator('#modelAtelierFaceSheetCropX').fill('.1');
  await page.locator('#modelAtelierFaceSheetCropW').fill('.8');
  await page.locator('#modelAtelierFaceSheetHeadDepth').fill('.65');
  await page.locator('#modelAtelierFaceSheetApply').click();
  assert.equal((await project()).parts.at(-1).faceSheet.headDepth,.65);
  await page.locator('#modelAtelierFaceSheetUVHeatmap').check();
  let render=await page.evaluate(()=>window.SWYRL_ENGINE_VIEW.status().selectedMaterial);
  assert.equal(render.vertexColors,true,'UV stretch view must use explicit per-vertex diagnostic color');
  assert.equal(render.basic,true);
  await page.locator('#modelAtelierFaceSheetUVHeatmap').uncheck();
  render=await page.evaluate(()=>window.SWYRL_ENGINE_VIEW.status().selectedMaterial);
  assert.equal(render.vertexColors,false,'Restoring shaded view must remove diagnostic colors');
  assert.match(await page.locator('#modelAtelierFaceSheetUVStats').textContent(),/UV stretch/);
  let updated=(await project()).parts.at(-1);
  assert.equal(updated.faceSheet.gridU,60);
  assert.equal(updated.faceSheet.gridV,26);
  assert.equal(updated.faceSheet.crop[0],.1);
  assert.equal(updated.faceSheet.crop[2],.8);
  // A UV face sheet is an actual mesh, so native radial sculpt operations
  // must apply to it and survive the exact project JSON roundtrip.
  await page.locator('#modelAtelierSculptBrushSurfaceMode').selectOption('through');
  await page.locator('#modelAtelierSculptBrushRadius').fill('.35');
  await page.locator('#modelAtelierSculptBrushAmount').fill('.05');
  for(const [i,value]of[[0,0],[1,0],[2,0]])await page.locator('#modelAtelierSculptBrushCenter'+i).fill(String(value));
  await page.locator('#modelAtelierSculptBrushApply').click();
  updated=(await project()).parts.at(-1);
  assert.equal(updated.sculptBrushes?.length,1);
  const dl=page.waitForEvent('download');
  await page.locator('#modelAtelierExport').click();
  const path=await(await dl).path(),saved=JSON.parse(await readFile(path,'utf8'));
  assert.equal(saved.model.parts.length,284);
  assert.equal(saved.model.parts.at(-1).faceSheet.gridU,60);
  assert.equal(saved.model.parts.at(-1).faceSheet.headDepth,.65);
  assert.equal(saved.model.references.length,1,'Image must be portable in same model JSON');
  await page.locator('#modelAtelierUndo').click();
  assert(!(await project()).parts.at(-1).sculptBrushes?.length);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier
    .parts.at(-1)?.sculptBrushes?.length===1);
  assert.equal((await project()).parts.at(-1).faceSheet.headDepth,.65);
  assert.equal(JSON.stringify((await project()).parts.slice(0,283)),partsBefore);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1123_FACE_IMAGE_SHEET_BROWSER_NATIVE_MESH_UV_SCULPT_UNDO_JSON_PASS',device);
  await context.close();
 }
}finally{await browser.close();}
