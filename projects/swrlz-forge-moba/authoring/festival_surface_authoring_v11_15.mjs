// Author through the real native inspector, then save its validated model export.
import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const root=new URL('../',import.meta.url),out=process.env.SWYRL_SURFACE_OUT||'surface-study',base=process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8781';
await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const page=await browser.newPage({viewport:{width:1440,height:1100},acceptDownloads:true}),errors=[],completed=[];
page.on('pageerror',e=>errors.push(String(e)));page.setDefaultTimeout(30000);
const hit=async id=>{const el=page.locator('#modelAtelier'+id);await el.scrollIntoViewIfNeeded();await el.click();};
const set=async(id,value)=>{await page.locator('#modelAtelier'+id).fill(String(value));await page.locator('#modelAtelier'+id).dispatchEvent('change');};
const shot=async name=>{await page.waitForTimeout(120);await page.screenshot({path:out+'/'+name+'.png'});};
try{
 await page.goto(base+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:60000});await page.locator('#modelAtelierPanel canvas').waitFor();
 const edits=JSON.parse(await fs.readFile(new URL('festival_surface_edits_v11_15.json',import.meta.url),'utf8'));
 for(const e of edits){
  await page.locator('#modelAtelierParts').selectOption(e.id);
  if(e.path){await page.locator('#modelAtelierLoftPath').fill(JSON.stringify(e.path));await page.locator('#modelAtelierLoftRadii').fill(JSON.stringify(e.radii));await hit('ApplyLoft');}
  if(e.surface){for(const [key,value] of Object.entries(e.surface))key==='preset'?await page.locator('#modelAtelierSurfacePreset').selectOption(value):await page.locator('#modelAtelier'+key[0].toUpperCase()+key.slice(1)).fill(String(value));await hit('SurfaceApply');}
  if(e.color)await set('Color',e.color);
  for(const key of ['position','rotation','scale'])if(e[key])for(let i=0;i<3;i++)await set(key+i,e[key][i]);
  completed.push(e.id);
 }
 const snap=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene());
 const authored=await snap();assert.equal(authored.project.modelAtelier.parts.length,301);
 const wait=page.waitForEvent('download');await hit('Export');const download=await wait;await download.saveAs(out+'/authored.model.json');
 let saved=JSON.parse(await fs.readFile(out+'/authored.model.json','utf8'));assert.deepEqual(saved.model,authored.project.modelAtelier);
 for(const e of edits){const p=saved.model.parts.find(p=>p.id===e.id);for(const [k,v] of Object.entries(e)){if(k==='id')continue;if(k==='surface'){for(const [key,value] of Object.entries(v))assert.equal(p[key==='preset'?'surfaceStyle':key],value);}else assert.deepEqual(p[k],v);}}
 // Native import and whole-model undo must retain the new surface parameters.
 await page.locator('#modelAtelierImportFile').setInputFiles(out+'/authored.model.json');await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'));
 const normalized=(await snap()).project.modelAtelier;
 assert.deepEqual(normalized,{...saved.model,poseFrames:saved.model.poseFrames??[],poseNeutral:saved.model.poseNeutral??null});
 const again=page.waitForEvent('download');await hit('Export');await (await again).saveAs(out+'/authored.model.json');saved=JSON.parse(await fs.readFile(out+'/authored.model.json','utf8'));assert.deepEqual(saved.model,normalized);
 for(const v of ['front','three','right','back']){await page.evaluate(v=>window.SWYRL_ENGINE_MODEL_ATELIER.view(v),v);await shot('desktop-'+v);}
 for(const id of ['model-0001','azure-skull','skirt-panel-0']){await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('front'));await page.locator('#modelAtelierParts').selectOption(id);await hit('FrameSelected');await shot('detail-'+id);}
 await page.setViewportSize({width:412,height:915});await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('front'));await shot('phone-front');
 const scene=JSON.parse(await fs.readFile(new URL('scenes/model-atelier-festival-refined-v11-14.swyrl.json',root),'utf8'));
 scene.version=11.15;scene.project.modelAtelier=saved.model;
 await fs.writeFile(out+'/model-atelier-festival-surface-v11-15.swyrl.json',JSON.stringify(scene,null,2)+'\n');
 assert.deepEqual(errors,[]);await fs.writeFile(out+'/authoring-receipt.json',JSON.stringify({completed,errors,parts:301,metrics:await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.metrics()),nativeExportRoundTrip:true},null,2));
 console.log('NATIVE_SURFACE_AUTHORING_PASS',completed.length);
}catch(e){await shot('failure').catch(()=>{});await fs.writeFile(out+'/failure.json',JSON.stringify({error:String(e),stack:e.stack,completed,errors},null,2));throw e;}finally{await browser.close();}
