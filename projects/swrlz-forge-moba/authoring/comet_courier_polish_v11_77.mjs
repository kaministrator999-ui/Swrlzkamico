import {chromium} from 'playwright';import fs from 'node:fs/promises';import assert from 'node:assert/strict';
const input=process.env.SWYRL_COURIER_INPUT||'/workspace/fox-finished/astra.model.json',out=process.env.SWYRL_COURIER_OUT||'/workspace/fox-polished',base=process.env.SWYRL_COURIER_URL||'http://127.0.0.1:8788';await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});const page=await browser.newPage({viewport:{width:1320,height:1000},acceptDownloads:true});page.setDefaultTimeout(90000);const errors=[];page.on('pageerror',e=>{errors.push(e.message);console.log('PAGEERROR',e.message)});page.on('dialog',d=>d.accept());
const snap=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene()),hit=id=>page.evaluate(id=>document.getElementById('modelAtelier'+id).click(),id);
try{
 await page.goto(base+'/?project=comet-courier',{waitUntil:'domcontentloaded'});await page.locator('#modelAtelierCourierStudio').click();await page.locator('#modelAtelierParts').waitFor();await page.locator('#modelAtelierImportFile').setInputFiles(input);await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'));
 const parts=(await snap()).project.modelAtelier.parts;
 for(const p of parts.filter(p=>p.name.startsWith('Chest · fur blade'))){await page.locator('#modelAtelierParts').selectOption(p.id);await page.evaluate(()=>{for(const [id,v] of [['scale2',.18],['position2',.52]]){const e=document.getElementById('modelAtelier'+id);e.value=String(v);e.dispatchEvent(new Event('change',{bubbles:true}));}});console.log('NATIVE_COURIER_FUR_LAYER',p.name);}
 const groups=(await snap()).project.modelAtelier.meshGroups;
 const event=page.waitForEvent('download');await hit('Export');await(await event).saveAs(out+'/astra.model.json');const saved=JSON.parse(await fs.readFile(out+'/astra.model.json','utf8'));await page.locator('#modelAtelierImportFile').setInputFiles(out+'/astra.model.json');await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'));assert.deepEqual((await snap()).project.modelAtelier,saved.model);
 await fs.writeFile(out+'/astra.swyrl.json',JSON.stringify(await snap(),null,2)+'\n');
 for(const view of ['front','three','right','back']){await page.evaluate(v=>window.SWYRL_ENGINE_MODEL_ATELIER.view(v),view);await page.screenshot({path:out+'/'+view+'.png'});}
 await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('three'));const png=page.waitForEvent('download');await hit('RenderPNG');await(await png).saveAs(out+'/astra-studio-2k.png');
 const glb=page.waitForEvent('download');await hit('ExportGLB');await(await glb).saveAs(out+'/astra-comet-courier.glb');
 await page.setViewportSize({width:412,height:915});await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('three'));await page.screenshot({path:out+'/phone.png'});
 assert.deepEqual(errors,[]);await fs.writeFile(out+'/receipt.json',JSON.stringify({parts:parts.length,assemblies:groups.length,nativeSaveReimport:true,project:(await snap()).project.name,errors},null,2));console.log('NATIVE_COURIER_POLISH_PASS');
}finally{await browser.close();}
