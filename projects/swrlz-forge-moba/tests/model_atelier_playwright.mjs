import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const modes=[{name:'desktop',viewport:{width:1536,height:960},isMobile:false,hasTouch:false},
  {name:'mobile',viewport:{width:412,height:915},isMobile:true,hasTouch:true}];
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
await mkdir('model-atelier-acceptance',{recursive:true});
try{
  for(const mode of modes){
    const context=await browser.newContext(mode);
    const page=await context.newPage();
    const faults=[];
    page.on('pageerror',e=>faults.push(String(e)));
    await page.goto(base+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:60000});
    await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor({timeout:30000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_MODEL_ATELIER?.status().count===253,{timeout:20000});
    let state=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status());
    assert.equal(state.active,true);assert.equal(state.open,true);assert.equal(state.count,253);
    assert.equal(await page.locator('[data-project-template="model-atelier"]').count(),1,'Starter card missing');
    assert.equal(await page.locator('#modelAtelierParts option').count(),253,'Not individually editable meshes');
    assert.equal(await page.locator('#modelAtelierPanel canvas').isVisible(),true,'3D viewport hidden');
    assert.equal(await page.locator('#modelAtelierPartCount').isVisible(),true);
    await page.locator('#modelAtelierParts').selectOption({index:5});
    await page.locator('#modelAtelierColor').fill('#6dd5ff');
    await page.locator('#modelAtelierColor').dispatchEvent('change');
    await page.locator('#modelAtelierposition0').fill('1.4');
    await page.locator('#modelAtelierposition0').dispatchEvent('change');
    await page.locator('#modelAtelierDuplicate').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,254);
    await page.locator('#modelAtelierUndo').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,253);
    await page.locator('#modelAtelierRedo').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,254);
    await page.locator('#modelAtelierDelete').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,253);
    await page.locator('#modelAtelierOBJ').click();
    await page.locator('#modelAtelierExport').click();
    await page.locator('#modelAtelierResetCamera').click();
    await page.screenshot({path:resolve('model-atelier-acceptance',mode.name+'.png')});
    await page.locator('#modelAtelierClose').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).open,false);
    await page.locator('#modelAtelierReopen').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).open,true);
    assert.equal(faults.length,0,'JavaScript runtime errors: '+JSON.stringify(faults));
    console.log('MODEL_ATELIER_CASE_PASS '+mode.name+' registered-native-starter');
    console.log('MODEL_ATELIER_CASE_PASS '+mode.name+' 3d-viewport-and-253-meshes');
    console.log('MODEL_ATELIER_CASE_PASS '+mode.name+' color-position-duplicate-history-delete');
    console.log('MODEL_ATELIER_CASE_PASS '+mode.name+' export-reopen');
    await context.close();
  }
  console.log('MODEL_ATELIER_ALL_VIEWPORTS_PASS');
}finally{await browser.close();}
