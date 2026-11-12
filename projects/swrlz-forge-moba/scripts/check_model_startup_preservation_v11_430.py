#!/usr/bin/env python3
"""Bounded real Chromium check of inherited v425 startup and Projects UI.

Uses the exact supplied package at its ordinary index.html entry point, with
the default authored scene, native observers and render loop intact. A fresh
guest profile exercises existing tabs only: no match, model import, account
save, tutorial start or cloud project write is performed.
"""
import argparse
import asyncio
import hashlib
import json
import mimetypes
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from playwright.async_api import async_playwright

CLI=argparse.ArgumentParser(description=__doc__)
CLI.add_argument('--html',required=True)
CLI.add_argument('--output')
CLI.add_argument('--chromium',default='/usr/bin/chromium')
CLI.add_argument('--expect-sha')
ARGS=CLI.parse_args()
HTML=Path(ARGS.html).resolve()
assert HTML.is_file()
SHA=hashlib.sha256(HTML.read_bytes()).hexdigest()
if ARGS.expect_sha:assert SHA==ARGS.expect_sha,'Startup check must use exact sealed artifact'
OUT=Path(ARGS.output or tempfile.mkdtemp(prefix='swrlz-startup430-')).resolve()
OUT.mkdir(parents=True,exist_ok=True)
FORGE='https://kamiloki-swrlz-forge-moba.static.hf.space'
CHAT='https://kamiloki-swyrlz.hf.space'
CDN='https://cdn.jsdelivr.net'
receipt={'version':'v11.430','testedHtmlSha256':SHA,'status':'RUNNING','checks':[],
         'runtime':'Chromium Android-sized guest profile / ordinary index entry',
         'physicalHeadsetAcceptance':False,'cloudAccountWrites':False,'pageErrors':[]}

def record(message):
    receipt['checks'].append(message)
    (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('STARTUP430_CHECK',message,flush=True)

def remote(request_url,method,headers,body):
    try:response=urlopen(Request(request_url,data=body,headers=headers,method=method),timeout=25)
    except HTTPError as error:response=error
    with response:
        # Existing chat station stream is an optional bootstrap request. Read
        # its bounded first event rather than holding the browser test open.
        data=response.readline(262144) if urlsplit(request_url).path=='/api/lalm_station/stream' else response.read()
        wanted={'content-type','content-security-policy','access-control-allow-origin',
                'access-control-allow-credentials','cache-control'}
        return response.status,{k:v for k,v in response.headers.items() if k.lower() in wanted},data

async def transport(route):
    request=route.request;url=urlsplit(request.url);origin=url.scheme+'://'+url.netloc
    if origin==FORGE:
        if url.path in ('/','/index.html','/modeler.html'):
            return await route.fulfill(path=str(HTML),content_type='text/html')
        asset=(HTML.parent/url.path.lstrip('/')).resolve()
        if asset.is_relative_to(HTML.parent) and asset.is_file():
            return await route.fulfill(path=str(asset),content_type=mimetypes.guess_type(asset)[0] or 'application/octet-stream')
        return await route.fulfill(status=404,body='Missing packaged fixture asset')
    if origin not in (CHAT,CDN):return await route.abort('blockedbyclient')
    allowed={'accept','content-type','origin','referer'}
    headers={k:v for k,v in (await request.all_headers()).items() if k.lower() in allowed}
    try:status,headers,data=await asyncio.to_thread(remote,request.url,request.method,headers,request.post_data_buffer)
    except Exception:return await route.abort('failed')
    return await route.fulfill(status=status,headers=headers,body=data)

async def snapshot(page):
    return await asyncio.wait_for(page.evaluate('''()=>{
      const hub=document.querySelector('#projectHub'),bars=document.querySelectorAll('#st141LevelBar');
      return {version:window.SWRLZ_FORGE_BUILD?.version,documentState:document.readyState,
        elapsedMs:Math.round(performance.now()),ready:document.documentElement.classList.contains('se127-editor-ready'),
        splash:document.querySelector('#se185BootStage')?.textContent||'',
        footer:document.querySelector('footer')?.innerText.slice(0,300)||'',
        levels:window.SWYRL_ENGINE_LEVELS?.status?.(),
        tabs:[...hub?.querySelectorAll('.se170-hub-tabs button[role=tab]')||[]].map(n=>n.textContent.trim()),
        levelBarCount:bars.length,levelBarAttached:bars.length===1&&bars[0].isConnected,
        levelBarVisible:bars.length===1&&!bars[0].hidden,
        recovery:window.SWYRL_ENGINE_LEVEL_UI_RECOVERY_423?.inspect?.()};
    }'''),timeout=12)

async def flow(browser):
    context=await browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    for origin in (FORGE,CHAT,CDN):await context.route(origin+'/**',transport)
    page=await context.new_page()
    page.on('pageerror',lambda error:receipt['pageErrors'].append(str(error)))
    try:
        await page.goto(FORGE+'/index.html',wait_until='domcontentloaded',timeout=90000)
        await page.wait_for_function('()=>window.SWRLZ_FORGE_BUILD?.version==="v11.430"',timeout=90000)
        # The inherited native safety watchdog is eleven seconds. Check after
        # it can run, without altering any observer, timer, startup or frame code.
        await asyncio.sleep(12.8)
        await page.wait_for_function('()=>document.documentElement.classList.contains("se127-editor-ready")',timeout=30000)
        initial=await snapshot(page);receipt['initial']=initial
        assert initial['version']=='v11.430'
        assert initial['ready'] and initial['documentState']=='complete'
        assert '170 parts' in initial['footer'],initial
        assert initial['levels']['owned'] and initial['levels']['levels']>=1,initial
        assert initial['levelBarCount']==1 and initial['levelBarAttached'] and initial['levelBarVisible'],initial
        record('Ordinary index startup reaches the real ready state with the authored 170-part Dragon Den and one hydrated native level selector')

        delay=await asyncio.wait_for(page.evaluate('''()=>new Promise(resolve=>{
          const start=performance.now();setTimeout(()=>resolve(performance.now()-start),200);
        })'''),timeout=10)
        receipt['eventLoopTimerMs']=delay
        assert delay>=150
        second=await snapshot(page)
        assert second['ready'] and second['levelBarCount']==1 and '170 parts' in second['footer']
        record('The native event loop continues to run after startup and the level selector remains singular and attached')

        notes=page.locator('#seReleaseNotesDialog[open]')
        if await notes.count():await page.locator('#seReleaseNotesClose').click(timeout=10000)
        await page.locator('#projectBtn').click(timeout=12000)
        await page.locator('#projectHub.show').wait_for(state='visible')
        state=await page.evaluate('''()=>{
          const hub=document.querySelector('#projectHub');return {visible:hub.classList.contains('show'),
            scroll:getComputedStyle(hub.querySelector('.project-window')).overflowY,
            tabs:[...hub.querySelectorAll('.se170-hub-tabs button[role=tab]')].map(n=>n.textContent.trim())};
        }''')
        assert state['scroll']=='auto',state
        for name in ('Starter Projects','My Projects','Tutorials'):assert name in state['tabs'],state
        receipt['projectHub']=state
        record('The existing Projects dialog retains Starter Projects, My Projects and Tutorials with native vertical scrolling')

        for tab,pane in [('#se412Tab','#se412Tutorials'),('#se170-tab-mine','#se170-pane-mine'),('#se170-tab-starter','#se170-pane-starter')]:
            await page.locator(tab).click(timeout=12000)
            await page.locator(pane).wait_for(state='visible',timeout=12000)
        record('All three native Projects tabs switch their real panes through ordinary touch-compatible clicks without forced events')
        await page.screenshot(path=str(OUT/'projects-startup-preserved.png'))
        await page.locator('#projectClose').click(timeout=12000)
        assert not await page.locator('#projectHub.show').count()
        final=await snapshot(page);receipt['final']=final
        assert final['ready'] and '170 parts' in final['footer'] and final['levelBarCount']==1
        assert not receipt['pageErrors'],receipt['pageErrors']
        record('Closing Projects returns to the unchanged authored default scene with zero JavaScript page errors')
    except Exception:
        try:await page.screenshot(path=str(OUT/'failure.png'))
        except Exception:pass
        raise
    finally:await context.close()

async def main():
    async with async_playwright() as playwright:
        browser=await playwright.chromium.launch(executable_path=ARGS.chromium,headless=True,
            args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
        try:
            await asyncio.wait_for(flow(browser),timeout=180)
            receipt['status']='PASS'
            print('MODEL_STARTUP_PRESERVATION_V11_430_PASS',json.dumps({'sha256':SHA,'checks':len(receipt['checks'])}),flush=True)
        except Exception as error:
            receipt.update(status='FAIL',error=type(error).__name__+': '+str(error))
            raise
        finally:
            (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
            await browser.close()

if __name__=='__main__':asyncio.run(main())
