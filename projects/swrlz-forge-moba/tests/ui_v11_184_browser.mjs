import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist='/tmp/se184-browser';
const viewports=[['android-390',390,844,true],['quest-980',980,680,false]];
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'
]});
try{
 for(const [name,width,height,mobile] of viewports){
  const ctx=await browser.newContext({viewport:{width,height},isMobile:mobile,hasTouch:mobile,ignoreHTTPSErrors:true});
  const page=await ctx.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(String(e).slice(0,500)));
  await page.route('**/*',route=>{
   const url=new URL(route.request().url());
   if(url.origin===host){
    const rel=url.pathname==='/'?'index.html':url.pathname.replace(/^\/+/,'');
    const target=path.resolve(dist,rel);
    if(target===dist||!target.startsWith(dist+'/')||!fs.existsSync(target)){
     route.fulfill({status:404,body:'Not found'});return;
    }
    route.fulfill({status:200,path:target,contentType:rel.endsWith('.html')?'text/html':undefined});return;
   }
   if(url.host.includes('cdn.jsdelivr.net')){route.continue();return;}
   route.abort();
  });
  await page.goto(host+'/',{waitUntil:'load',timeout:90000});
  await page.waitForFunction(()=>!!window.SWYRL_ENGINE_SAVED_DEFAULT&&!!window.SWYRL_ENGINE_AGENT&&
    !!document.getElementById('se170-tab-mine'),null,{timeout:90000});
  await page.evaluate(()=>document.querySelector('#seReleaseNotesDialog[open]')?.close());
  await page.evaluate(async()=>{
   const native=window.SWYRL_ENGINE_AGENT.inspectScene();
   if(!native?.project||!Array.isArray(native.scene?.actors))throw Error('Native scene missing');
   const id='se184-browser-local';
   native.project.name='Preview Card Test World';
   native.project.projectName='Preview Card Test World';
   native.project.instanceId=id;
   const row={id,name:'Preview Card Test World',starterId:'test-local',
     updatedAt:new Date().toISOString(),data:native,preview:{
       schema:'se184-scene-overview-v1',kind:'sandbox',count:3,parts:0,
       background:'#16364b',points:[
        {x:-4,z:2,type:'tree'},{x:0,z:0,type:'house'},{x:3,z:4,type:'hero'}]
     }};
   const db=await new Promise((resolve,reject)=>{
    const req=indexedDB.open('swyrl-engine-projects-v1',2);
    req.onupgradeneeded=()=>{
     const d=req.result;
     if(!d.objectStoreNames.contains('projects'))d.createObjectStore('projects',{keyPath:'id'});
     if(!d.objectStoreNames.contains('metadata'))d.createObjectStore('metadata',{keyPath:'id'});
    };
    req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);
   });
   try{await new Promise((resolve,reject)=>{
    const tx=db.transaction(['projects','metadata'],'readwrite');
    tx.objectStore('projects').put(row);
    const {data,...metadata}=row;tx.objectStore('metadata').put(metadata);
    tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);
   });}finally{db.close();}
  });
  await page.evaluate(()=>{
   const hub=document.getElementById('projectHub');
   hub.classList.add('show');
   document.getElementById('se170-tab-mine').click();
  });
  const card=page.locator('#se184LocalCards .se184-project-card[data-project-id="se184-browser-local"]');
  await card.waitFor({state:'visible',timeout:30000});
  assert.ok(await card.locator('.se184-preview svg').count(),name+' missing image preview');
  assert.ok((await card.locator('.se184-preview-tag').textContent()).includes('3 scene actors'));
  const defaultBox=card.locator('input[type="checkbox"][data-se184-default]');
  assert.equal(await defaultBox.isChecked(),false);
  await defaultBox.check();
  assert.equal(await defaultBox.isChecked(),true);
  assert.equal(await page.locator('#projectHub input[data-se128-default]:checked').count(),0);
  const pref=await page.evaluate(()=>window.SWYRL_ENGINE_SAVED_DEFAULT.read());
  assert.equal(pref.source,'local');assert.equal(pref.id,'se184-browser-local');
  console.log('SE184_CARD_DEFAULT',name,pref);

  const firstStarter=page.locator('#projectHub input[data-se128-default]').first();
  await page.evaluate(()=>document.getElementById('se170-tab-starter').click());
  await firstStarter.check();
  await page.evaluate(()=>document.getElementById('se170-tab-mine').click());
  await card.waitFor({state:'visible'});
  assert.equal(await defaultBox.isChecked(),false,name+' saved default remained after starter selected');
  await defaultBox.check();
  const pref2=await page.evaluate(()=>window.SWYRL_ENGINE_SAVED_DEFAULT.read());
  assert.equal(pref2.source,'local');
  await page.reload({waitUntil:'load',timeout:90000});
  await page.waitForTimeout(6000);
  console.log('SE184_RELOAD_DEBUG',name,JSON.stringify(await page.evaluate(()=>({
   currentName:window.SWYRL_ENGINE_AGENT?.inspectScene?.()?.project?.name||'none',
   projectId:window.SWYRL_ENGINE_AGENT?.inspectScene?.()?.project?.instanceId||'',
   bootPending:window.se128StartupPending,
   default:window.SWYRL_ENGINE_SAVED_DEFAULT?.read?.(),
   pendingDefault:window.SWYRL_ENGINE_SAVED_DEFAULT?.pending?.(),
   bootStatus:document.getElementById('se184DefaultBoot')?.textContent||'',
   build:window.SWRLZ_FORGE_BUILD?.version
  }))),errors);
  await page.waitForFunction(()=>{
   const api=window.SWYRL_ENGINE_SAVED_DEFAULT;
   if(!api||!window.SWYRL_ENGINE_AGENT||window.se128StartupPending)return false;
   return window.SWYRL_ENGINE_AGENT.inspectScene()?.project?.name==='Preview Card Test World';
  },null,{timeout:60000});
  const state=await page.evaluate(()=>({
   active:window.SWYRL_ENGINE_AGENT.inspectScene().project.name,
   preference:window.SWYRL_ENGINE_SAVED_DEFAULT.read(),
   pending:window.se128StartupPending
  }));
  assert.equal(state.active,'Preview Card Test World');
  assert.equal(state.preference.id,'se184-browser-local');
  assert.equal(state.pending,false);
  console.log('SE184_SAVED_DEFAULT_BOOT_PASS',name,JSON.stringify(state));
  assert.equal(errors.length,0,name+' browser page errors '+JSON.stringify(errors));
  await ctx.close();
 }
 console.log('SE184_GALLERY_BROWSER_PASS',viewports.length);
}finally{await browser.close();}
