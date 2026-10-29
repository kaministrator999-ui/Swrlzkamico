import {chromium} from 'playwright';import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {design} from './comet_courier_design_v11_77.mjs';
const out=process.env.SWYRL_COURIER_OUT||'/workspace/fox-authored',base=process.env.SWYRL_COURIER_URL||'http://127.0.0.1:8788';await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.SWYRL_CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const page=await browser.newPage({viewport:{width:1100,height:800},acceptDownloads:true});page.setDefaultTimeout(90000);const errors=[];page.on('pageerror',e=>{errors.push(e.message);console.log('PAGEERROR',e.message)});page.on('dialog',d=>d.accept());
const snap=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene()),get=id=>page.locator('#modelAtelier'+id),hit=id=>get(id).click(),set=async(id,v)=>{await get(id).fill(String(v));await get(id).dispatchEvent('change');};
try{
 await page.goto(base+'/?project=blank-model',{waitUntil:'domcontentloaded'});await get('Parts').waitFor();assert.equal((await snap()).project.modelAtelier.parts.length,1);
 // The authoring pass uses the existing native inspector, spline, density, HD and atlas controls.
 for(let i=0;i<design.length;i++){
  const d=design[i];if(i)await hit('Add');const id=(await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).selected||'model-seed';await get('Parts').selectOption(id);
  await page.evaluate(d=>{
   const field=(id,value)=>{const el=document.getElementById('modelAtelier'+id);if(!el)throw Error('Missing native control '+id);el.value=String(value);el.dispatchEvent(new Event('change',{bubbles:true}));};
   const fill=(id,value)=>{document.getElementById('modelAtelier'+id).value=String(value);};
   const click=id=>document.getElementById('modelAtelier'+id).click();
   field('Name',d.name);field('Kind',d.kind);field('Color',d.color||'#ffffff');field('Material',d.material||'silk');
   for(const key of ['position','scale','rotation'])for(let k=0;k<3;k++)field(key+k,(d[key]||(key==='scale'?[1,1,1]:[0,0,0]))[k]);
   if(d.kind==='loft'){fill('LoftPath',JSON.stringify(d.path));fill('LoftRadii',JSON.stringify(d.radii));click('ApplyLoft');}
   if(d.hd){field('HDStyle',d.hd);document.getElementById('modelAtelierHDSampling').checked=false;click('HDApply');}
   fill('DensityU','48');fill('DensityV',d.kind==='loft'?'24':'32');click('DensityApply');
   if(d.tile){field('AtlasTile',d.tile);fill('AtlasNormal','.65');click('AtlasApply');}
  },d);
  const actual=(await snap()).project.modelAtelier.parts.find(p=>p.id===id);assert.equal(actual.name,d.name);assert.equal(actual.kind,d.kind);if(d.tile)assert.equal(actual.textureBinding?.tile,d.tile);if(d.kind==='loft')assert.deepEqual(actual.path,d.path);console.log('NATIVE_COURIER_PART',i+1,design.length,d.name);
 }
 const dl=page.waitForEvent('download');await hit('Export');await(await dl).saveAs(out+'/astra.model.json');
 const saved=JSON.parse(await fs.readFile(out+'/astra.model.json','utf8'));await get('ImportFile').setInputFiles(out+'/astra.model.json');await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'));assert.deepEqual((await snap()).project.modelAtelier,saved.model);
 await fs.writeFile(out+'/astra.swyrl.json',JSON.stringify(await snap(),null,2)+'\n');
 for(const view of ['front','three','right','back']){await page.evaluate(v=>window.SWYRL_ENGINE_MODEL_ATELIER.view(v),view);await page.screenshot({path:out+'/'+view+'.png'});}
 await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('three'));const png=page.waitForEvent('download');await hit('RenderPNG');await(await png).saveAs(out+'/astra-studio-2k.png');
 const glb=page.waitForEvent('download');await hit('ExportGLB');await(await glb).saveAs(out+'/astra-comet-courier.glb');
 assert.deepEqual(errors,[]);await fs.writeFile(out+'/receipt.json',JSON.stringify({nativeParts:design.length,nativeSaveReimport:true,errors},null,2));console.log('NATIVE_COURIER_AUTHORING_PASS',design.length);
}finally{await browser.close();}
