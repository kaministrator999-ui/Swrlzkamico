// §E v11.188: game page lands on Game Engine, not Modeler,
// even when an older model starter / saved-model default was selected.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const host='https://kamiloki-swrlz-forge-moba.static.hf.space';
const dist=process.env.SE188_DIST||'/tmp/se188-package';
assert.equal(
 fs.readFileSync(path.join(dist,'index.html')).compare(fs.readFileSync(path.join(dist,'modeler.html'))),
 0,'Both routes must share the same verified native runtime');
const browser=await chromium.launch({headless:true,args:[
 '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'
]});
try{
 for(const [name,width,height,mobile] of [['android',390,844,true],['quest',980,680,false]]){
  const ctx=await browser.newContext({viewport:{width,height},isMobile:mobile,hasTouch:mobile,ignoreHTTPSErrors:true});
  const page=await ctx.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.route('**/*',route=>{
   const url=new URL(route.request().url());
   if(url.origin===host){
    const rel=url.pathname==='/'?'index.html':url.pathname.replace(/^\/+/,'');
    const target=path.resolve(dist,rel);
    if(target===dist||!target.startsWith(dist+'/')||!fs.existsSync(target)){
     void route.fulfill({status:404,body:'Missing focused test asset'});return;
    }
    void route.fulfill({status:200,path:target,contentType:rel.endsWith('.html')?'text/html':undefined});return;
   }
   if(url.hostname==='cdn.jsdelivr.net'){void route.continue();return;}
   void route.abort();
  });
  async function checkGame(hint){
   await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES?.active()==='game'&&
     !!document.querySelector('.app>.topbar .se187-game-tabs [data-se187-tab="game"]'),
     null,{timeout:70000});
   await page.evaluate(()=>document.querySelector('#seReleaseNotesDialog[open]')?.close());
   await page.waitForTimeout(1100);
   const state=await page.evaluate(()=>{
    const nav=document.querySelector('.app>.topbar .se187-game-tabs');
    const buttons=[...nav.querySelectorAll('[data-se187-tab]')];
    const panel=document.getElementById('modelAtelierPanel');
    const first=buttons[0]?.getBoundingClientRect();
    return {route:location.pathname,active:window.SWYRL_ENGINE_WORKSPACES?.active(),
      labels:buttons.map(b=>b.textContent.trim()),tabIds:buttons.map(b=>b.dataset.se187Tab),
      selected:buttons.map(b=>b.getAttribute('aria-selected')),
      visible:buttons.map(b=>!!b.getClientRects().length&&getComputedStyle(b).display!=='none'),
      firstX:Math.round(first?.x??-1),
      panelHidden:!panel||panel.hidden,
      panelVisible:!!panel && !!panel.getClientRects().length,
      modelStatus:window.SWYRL_ENGINE_MODEL_ATELIER?.status(),
      projectKind:window.SWYRL_ENGINE_AGENT?.inspectScene?.()?.project?.kind,
      selectedPref:localStorage.getItem('swyrl.engine.defaultStarter.v1')};
   });
   assert.equal(state.active,'game',hint+' active');
   assert.equal(state.route,'/index.html',hint+' route');
   assert.deepEqual(state.tabIds,['game','modeler'],hint+' tab order');
   assert.deepEqual(state.labels,['Game Engine','Modeling'],hint+' tab labels');
   assert.deepEqual(state.selected,['true','false'],hint+' selected tab');
   assert.deepEqual(state.visible,[true,true],hint+' both top tabs visible');
   assert.equal(state.panelVisible,false,hint+' Modeler must not cover Game Engine');
   assert.equal(state.panelHidden,true,hint+' Modeler hidden');
   console.log('SE188_GAME_LANDING_PASS',name,hint,JSON.stringify(state));
   return state;
  }
  await page.goto(host+'/index.html',{waitUntil:'load',timeout:120000});
  await checkGame('ordinary load');
  await page.locator('.se187-game-tabs [data-se187-tab="modeler"]').click({timeout:15000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES?.active()==='modeler'&&
    window.SWYRL_ENGINE_MODEL_ATELIER?.status()?.open,null,{timeout:60000});
  assert.equal(new URL(page.url()).pathname,'/modeler.html');
  await page.locator('#modelAtelierPanel .se187-model-tabs [data-se187-tab="game"]').click({timeout:15000});
  await checkGame('after tab return');
  // The remembered Model Atelier starter must NOT hijack the Game tab
  // when someone opens index.html later.
  await page.evaluate(()=>localStorage.setItem('swyrl.engine.defaultStarter.v1','model-atelier'));
  await page.reload({waitUntil:'load',timeout:120000});
  await checkGame('saved model starter default');
  assert.equal(await page.evaluate(()=>localStorage.getItem('swyrl.engine.defaultStarter.v1')),'model-atelier');
  // Reproduce the saved local model from the real v11.184 project store.
  await page.evaluate(async()=>{
   const id='se188-model-default-fixture';
   const snapshot=window.SWYRL_ENGINE_AGENT.inspectScene();
   snapshot.project.kind='model-atelier';
   snapshot.project.projectName='Saved Independent Model';
   snapshot.project.name='Saved Independent Model';
   snapshot.scene.actors=Array.isArray(snapshot.scene.actors)?snapshot.scene.actors:[];
   const row={id,name:'Saved Independent Model',updatedAt:'2026-10-31T00:00:00Z',
     starterId:'model-atelier',data:snapshot};
   const db=await new Promise((resolve,reject)=>{
    const req=indexedDB.open('swyrl-engine-projects-v1',2);
    req.onupgradeneeded=()=>{
     const d=req.result;
     if(!d.objectStoreNames.contains('projects'))d.createObjectStore('projects',{keyPath:'id'});
     if(!d.objectStoreNames.contains('metadata'))d.createObjectStore('metadata',{keyPath:'id'});
    };
    req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);
   });
   await new Promise((resolve,reject)=>{
    const tx=db.transaction(['projects','metadata'],'readwrite');
    tx.objectStore('projects').put(row);
    const {data,...meta}=row;tx.objectStore('metadata').put(meta);
    tx.oncomplete=resolve;tx.onerror=tx.onabort=()=>reject(tx.error);
   });
   db.close();
   localStorage.setItem('swyrl.engine.defaultStarter.v1','saved:local:'+id);
  });
  await page.reload({waitUntil:'load',timeout:120000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_WORKSPACES?.active()==='game'&&!window.se128StartupPending,null,{timeout:60000});
  const local=await checkGame('saved local model default');
  assert.notEqual(local.projectKind,'model-atelier','Saved model must not replace the Game Engine landing scene');
  assert.equal(local.selectedPref,'saved:local:se188-model-default-fixture','Model preference was overwritten');
  assert.equal(errors.length,0,name+' browser errors: '+JSON.stringify(errors.slice(-3)));
  await ctx.close();
 }
 console.log('SE188_LANDING_BROWSER_PASS');
}finally{await browser.close();}
