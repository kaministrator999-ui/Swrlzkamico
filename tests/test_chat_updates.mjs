// Real Chromium: native modal, persisted per-update preference, update refresh and mobile.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const html=fs.readFileSync(path.join(repo,'chat/§wyrlz/index.html'),'utf8');
const script=fs.readFileSync(path.join(repo,'chat/§wyrlz/assets/chat-updates-v1.js'),'utf8');
const production=JSON.parse(fs.readFileSync(path.join(repo,'chat/§wyrlz/assets/chat-updates-v1.json'),'utf8'));
assert.equal(production.historyCoverage.registryRecords,249);
assert.equal(production.history.length,265);
assert.equal(new Set(production.history.map(x=>x.id)).size,265);
assert(production.history.some(x=>x.version==='1.0.0'));
assert(html.includes('id="chatUpdatesOpen"'));
assert(html.includes('<script src="/chat/§wyrlz/assets/chat-updates-v1.js" defer>'));
assert(!script.includes('innerHTML'),'release data must be rendered as text');
const css=html.match(/<style>([\s\S]*?)<\/style>/)[1];
let manifest=structuredClone(production), mode='valid';let requests=0;
const hostile='<img src=x onerror="window.badNotes=true"> & § exact notes';
manifest.latest.changes.push(hostile);
const server=http.createServer((req,res)=>{
  if(req.url==='/') {res.setHeader('Content-Type','text/html; charset=utf-8');res.end('<!doctype html><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style><div id="topEdge" data-state="ready"></div><button id="chatUpdatesOpen">Chat updates</button><textarea id="prompt"></textarea><script src="/notes.js"></script>');return;}
  if(req.url==='/notes.js') {res.setHeader('Content-Type','application/javascript; charset=utf-8');res.end(script);return;}
  if(decodeURI(req.url)==='/chat/§wyrlz/assets/chat-updates-v1.json'){
    requests++;assert.match(req.headers['cache-control']||'',/no-cache/);res.setHeader('Content-Type','application/json');
    if(mode==='fail'){res.statusCode=503;res.end('{}');return;}
    if(mode==='invalid'){res.end('{"schema":"wrong"}');return;}
    res.end(JSON.stringify(manifest));return;
  }
  res.statusCode=404;res.end();
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'/opt/codex/cua_node/lib/node_modules/playwright/index.mjs');
const executablePath=process.env.CHROMIUM_PATH||(fs.existsSync('/usr/lib/chromium/chromium')?'/usr/lib/chromium/chromium':undefined);
const browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{}),args:['--no-sandbox','--disable-dev-shm-usage']});
const origin='http://127.0.0.1:'+server.address().port;
try{
  const context=await browser.newContext(); const page=await context.newPage();page.setDefaultTimeout(5000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(origin);const dialog=page.locator('#chatUpdatesDialog');
  await dialog.waitFor({state:'visible'});
  assert.equal(await dialog.getAttribute('data-update-id'),production.latest.id);
  assert.equal(await page.locator('#chatUpdatesLatest li').last().textContent(),hostile);
  assert.equal(await page.evaluate(()=>window.badNotes),undefined);
  assert.equal(await page.locator('#chatUpdatesHistory .chat-updates-entry').count(),265);
  await page.locator('#chatUpdatesHistory>summary').click();
  assert.match(await page.locator('#chatUpdatesHistory>summary').textContent(),/265/);
  await page.locator('#chatUpdatesClose').focus();await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(()=>document.activeElement.parentElement.id),'chatUpdatesHistory','native modal traps Tab at its first control');
  await page.keyboard.press('Shift+Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'chatUpdatesClose');
  await page.keyboard.press('Escape');assert.equal(await dialog.isVisible(),false);
  await page.reload();await page.waitForTimeout(250);assert.equal(await dialog.isVisible(),false,'close dismisses this session');
  await page.locator('#chatUpdatesOpen').click();await dialog.waitFor({state:'visible'});
  await page.locator('#chatUpdatesHide').check();await page.locator('#chatUpdatesClose').click();
  assert.equal(await page.evaluate(()=>document.activeElement.id),'chatUpdatesOpen','manual opener receives focus back');
  await page.reload();await page.waitForTimeout(250);assert.equal(await dialog.isVisible(),false,'checked preference survives reload');
  const second=await context.newPage();await second.goto(origin);await second.waitForTimeout(250);
  assert.equal(await second.locator('#chatUpdatesDialog').isVisible(),false,'same browser preference survives a new tab');
  await second.close();
  manifest.latest.id='newer-chat-update';manifest.latest.title='A newer update';
  await page.evaluate(()=>window.dispatchEvent(new Event('focus')));await dialog.waitFor({state:'visible'});
  assert.equal(await page.locator('#chatUpdatesHide').isChecked(),false,'new update is not suppressed');
  assert.match(await page.locator('#chatUpdatesSubtitle').textContent(),/A newer update/);
  assert.equal(await page.evaluate(id=>localStorage.getItem('swrlz:chat-updates:hidden:'+id),production.latest.id),'true','old preference retains its original scope');
  await page.keyboard.press('Escape');
  manifest.latest.id='busy-update';
  await page.evaluate(()=>{document.querySelector('#topEdge').dataset.state='busy';window.dispatchEvent(new Event('focus'));});
  await page.waitForTimeout(300);assert.equal(await dialog.isVisible(),false,'generation defers automatic popup');
  assert.equal(await page.evaluate(()=>sessionStorage.getItem('swrlz:chat-updates:seen:busy-update')),null,'closing the prior dialog cannot dismiss a newly fetched update');
  await page.evaluate(()=>document.querySelector('#topEdge').dataset.state='ready');await dialog.waitFor({state:'visible'});
  await page.keyboard.press('Escape');manifest.latest.id='composing-update';
  await page.locator('#prompt').fill('Keep my draft intact');
  await page.evaluate(()=>window.dispatchEvent(new Event('focus')));await page.waitForTimeout(300);
  assert.equal(await dialog.isVisible(),false,'nonempty composing defers automatic popup');
  assert.equal(await page.locator('#prompt').inputValue(),'Keep my draft intact');
  await page.locator('#chatUpdatesOpen').focus();await dialog.waitFor({state:'visible'});
  await page.keyboard.press('Escape');
  manifest.latest.id='empty-composer-update';await page.locator('#prompt').fill('');
  await page.evaluate(()=>window.dispatchEvent(new Event('focus')));await dialog.waitFor({state:'visible'});
  await page.keyboard.press('Escape');
  mode='fail';await page.locator('#chatUpdatesOpen').click();
  await page.getByText('Couldn’t load Chat updates. Try again when connected.').waitFor();
  mode='valid';await page.getByRole('button',{name:'Retry',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.chat-updates-status').textContent==='');
  await page.keyboard.press('Escape');assert.deepEqual(errors,[]);
  await context.close();
  const mobile=await browser.newContext({viewport:{width:360,height:640},isMobile:true,hasTouch:true});
  const mp=await mobile.newPage();await mp.goto(origin);await mp.locator('#chatUpdatesDialog').waitFor({state:'visible'});
  const bounds=await mp.locator('#chatUpdatesDialog').boundingBox();
  assert(bounds.x>=0&&bounds.y>=0&&bounds.x+bounds.width<=361&&bounds.y+bounds.height<=641,'mobile modal fits viewport');
  await mp.locator('#chatUpdatesHistory>summary').click();await mp.locator('#chatUpdatesHide').check();await mp.locator('#chatUpdatesClose').tap();
  assert.equal(await mp.locator('#chatUpdatesDialog').isVisible(),false,'mobile close remains reachable with expanded history');
  await mobile.close();
  const blocked=await browser.newContext();await blocked.addInitScript(()=>{
    Object.defineProperty(window,'localStorage',{get(){throw new Error('disabled');}});
    Object.defineProperty(window,'sessionStorage',{get(){throw new Error('disabled');}});
  });
  const bp=await blocked.newPage();await bp.goto(origin);await bp.locator('#chatUpdatesDialog').waitFor({state:'visible'});
  await bp.locator('#chatUpdatesHide').check();await bp.getByText('This browser couldn’t save the preference. You can still close these notes for this session.').waitFor();
  await bp.locator('#chatUpdatesClose').click();await bp.evaluate(()=>window.dispatchEvent(new Event('focus')));await bp.waitForTimeout(250);
  assert.equal(await bp.locator('#chatUpdatesDialog').isVisible(),false,'memory session dismissal still works without storage');
  await blocked.close();
  for (const action of ['Escape','Continue']) {
    const immediate=await browser.newContext();const ip=await immediate.newPage();await ip.goto(origin);
    await ip.locator('#chatUpdatesDialog').waitFor({state:'visible'});
    const saved=await ip.evaluate(action=>{
      const d=document.querySelector('#chatUpdatesDialog');let closeEventRan=false;
      d.addEventListener('close',()=>{closeEventRan=true;},{once:true});
      if(action==='Escape')d.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));
      else document.querySelector('#chatUpdatesClose').click();
      return {open:d.open,seen:sessionStorage.getItem('swrlz:chat-updates:seen:'+d.dataset.updateId),closeEventRan};
    },action);
    assert.deepEqual(saved,{open:false,seen:'true',closeEventRan:false},action+' saves synchronously before the native queued close event');
    await ip.reload();await ip.waitForTimeout(250);assert.equal(await ip.locator('#chatUpdatesDialog').isVisible(),false,action+' immediate reload retains dismissal');
    await immediate.close();
  }
  console.log('PASS Chat updates: 265 historical records, literal text, native focus/Escape, per-update persistence, newer update, deferred generation/draft, retry, mobile, restricted storage; '+requests+' no-store manifest requests.');
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
