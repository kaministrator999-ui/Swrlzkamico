#!/usr/bin/env python3
"""Focused actual IWER Quest controls for the manual native mesh workshop.

The fixture is disposable guest geometry. Browser emulation proves software
transactions/rendering, not physical headset comfort or sustained frame time.
The pinned emulator never enters the engine package.
"""
import argparse
import asyncio
import hashlib
import json
import math
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
FORGE='https://kamiloki-swrlz-forge-moba.static.hf.space'
CHAT='https://kamiloki-swyrlz.hf.space'
CDN='https://cdn.jsdelivr.net'
THREE_URL=CDN+'/npm/three@0.169.0/+esm'
IWER_URL=CDN+'/npm/iwer@2.8.0/build/iwer.min.js'
IWER_BYTES=384266
IWER_SHA='79fb12295642d3cbab36b28a2a4ba8b4a48a5053ce70057da2f249b67daa9780'
cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument('--html',required=True)
cli.add_argument('--output')
cli.add_argument('--chromium',default='/usr/bin/chromium')
cli.add_argument('--iwer')
cli.add_argument('--expect-sha')
args=cli.parse_args()
html=Path(args.html).resolve();assert html.is_file(),html
SHA=hashlib.sha256(html.read_bytes()).hexdigest()
if args.expect_sha:assert SHA==args.expect_sha,'The test must use the sealed artifact'
out=Path(args.output or tempfile.mkdtemp(prefix='swrlz-model-vr430-')).resolve();out.mkdir(parents=True,exist_ok=True)
if args.iwer:iwer_bytes=Path(args.iwer).read_bytes()
else:
    with urlopen(IWER_URL,timeout=30) as response:iwer_bytes=response.read(IWER_BYTES+1)
assert len(iwer_bytes)==IWER_BYTES and hashlib.sha256(iwer_bytes).hexdigest()==IWER_SHA
public=json.loads((ROOT/'scenes/model-atelier-prism-jester.swyrl.json').read_text())
expected_parts=[{'id':'vr430-cube','name':'Manual practice cube','kind':'box','position':[0,1.2,0],
    'rotation':[0,0,0],'scale':[1,1,1],'color':'#b89bd7','material':'matte','group':'Practice'}]
public['project'].update(name='VR manual modeling check',canonicalId='vr430-manual-practice',template='custom')
public['project']['modelAtelier']={'schema':'swyrl-model-atelier-v1','name':'VR manual modeling check','parts':expected_parts}
public['editor']={'studioWorkspace':'modeler'};public['scene']={'background':'#141425','paths':{},'actors':[]}
native_file=out/'model-vr-manual-practice.swyrl.json';native_file.write_text(json.dumps(public))


def http(url, method, headers, body):
    try:
        response = urlopen(Request(url, data=body, headers=headers, method=method), timeout=25)
    except HTTPError as error:
        response = error
    with response:
        data = response.readline(262144) if urlsplit(url).path == '/api/lalm_station/stream' else response.read()
        wanted = {'content-type', 'content-security-policy', 'access-control-allow-origin',
                  'access-control-allow-credentials', 'cache-control'}
        return response.status, {k: v for k, v in response.headers.items() if k.lower() in wanted}, data

async def transport(route):
    request = route.request
    url = urlsplit(request.url)
    origin = url.scheme + '://' + url.netloc
    if origin == FORGE:
        if url.path in ('/', '/index.html', '/modeler.html'):
            return await route.fulfill(path=str(html), content_type='text/html')
        asset = (html.parent / url.path.lstrip('/')).resolve()
        if asset.is_relative_to(html.parent) and asset.is_file():
            return await route.fulfill(path=str(asset))
        return await route.fulfill(status=404, body='Missing packaged test asset')
    if origin not in (CHAT, CDN):
        return await route.abort('blockedbyclient')
    allowed = {'accept', 'content-type', 'origin', 'referer'}
    headers = {k: v for k, v in (await request.all_headers()).items() if k.lower() in allowed}
    try:
        status, headers, data = await asyncio.to_thread(http, request.url, request.method, headers, request.post_data_buffer)
    except Exception:
        return await route.abort('failed')
    return await route.fulfill(status=status, headers=headers, body=data)

async def read(page, geometry=False):
    return await page.evaluate('(geometry)=>window.SWYRL_ENGINE_MODEL_VR.inspect({geometry})', geometry)

async def parts(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts')

async def frames(page, count=3):
    state=await read(page)
    if not state['sessionAttached']:
        return
    start=state['frameCount']
    await page.wait_for_function('(n)=>{const s=window.SWYRL_ENGINE_MODEL_VR.inspect();return !s.sessionAttached||s.frameCount>=n}', arg=start+count, timeout=20000)

async def button(page, side, key, pressed, count=2):
    await page.evaluate('([side,key,value])=>xrTestDevice.controllers[side].updateButtonValue(key,value)', [side, key, 1 if pressed else 0])
    await frames(page, count)

async def tap(page, side, key):
    await button(page, side, key, True, 1)
    await button(page, side, key, False, 2)

async def aim(page, target, side='right', origin=None):
    origin = origin or ([.22, 1.3, -.35] if side == 'right' else [-.22, 1.3, -.35])
    await page.evaluate('''([side,origin,target])=>{
      const T=window.__VR_THREE,c=xrTestDevice.controllers[side];
      const d=new T.Vector3(...target).sub(new T.Vector3(...origin)).normalize();
      const q=new T.Quaternion().setFromUnitVectors(new T.Vector3(0,0,-1),d);
      c.position.set(...origin);c.quaternion.set(q.x,q.y,q.z,q.w);
    }''', [side, origin, target])
    await frames(page)

async def aim_part(page, part_id, side='right'):
    detail = await read(page, True)
    target = next(item for item in detail['targetCenters'] if item['id'] == part_id)
    await aim(page, target['center'], side=side)
    await page.wait_for_function('([id,side])=>window.SWYRL_ENGINE_MODEL_VR.inspect().controllers.some(c=>c.handedness===side&&c.hoverId===id)', arg=[part_id, side])
    return target

async def action_ray(page, action, side='right'):
    detail = await read(page, True)
    target = next((item for item in detail['paletteActions'] if item['action'] == action), None)
    if target is None:
        raise AssertionError('Action '+action+' missing on page '+str(detail.get('page'))+': '+str([i['action'] for i in detail['paletteActions']]))
    await aim(page, target['center'], side=side)
    await tap(page, side, 'trigger')
    await settle_menu(page)

async def chord(page, controls, count=3):
    """Depress/release the named hardware controls together in actual XR frames."""
    await page.evaluate('(items)=>{for(const [side,key]of items)xrTestDevice.controllers[side].updateButtonValue(key,1)}',controls)
    await frames(page,count)
    await page.evaluate('(items)=>{for(const [side,key]of items)xrTestDevice.controllers[side].updateButtonValue(key,0)}',controls)
    await frames(page,3)

async def hints(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_VR_CONTROLLER_HINTS?.inspect?.()||null')

def distance(a,b):
    return sum((x-y)**2 for x,y in zip(a,b))**.5

async def screenshot_xr(page, name):
    # A real headset excludes browser DOM. Raise only IWER's test preview
    # container so the screenshot reflects the actual XR canvas, not DOM UI.
    await page.evaluate('()=>{xrTestDevice.canvasContainer.style.zIndex="2147483647";}')
    await page.screenshot(path=str(out / name))

async def open_model(browser, errors, emulated=True, denied=False, quest=False):
    options={'viewport': {'width': 1280, 'height': 960}, 'accept_downloads': True}
    if quest:
        options['user_agent']='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) OculusBrowser/33.0.0.0 Chrome/126.0.0.0 VR Safari/537.36'
    context = await browser.new_context(**options)
    if emulated:
        setup = iwer_bytes.decode() + '''\nif(location.origin===''' + json.dumps(FORGE) + '''){
          window.xrTestDevice=new IWER.XRDevice(IWER.metaQuest2,{stereoEnabled:false});
          xrTestDevice.installRuntime({forceInstall:true});xrTestDevice.position.set(0,1.65,0);
          xrTestDevice.controllers.left.position.set(-.3,1.22,-.4);xrTestDevice.controllers.right.position.set(.3,1.22,-.4);
        }'''
        await context.add_init_script(script=setup)
    for origin in (FORGE, CHAT, CDN):
        await context.route(origin + '/**', transport)
    page = await context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('dialog', lambda dialog: asyncio.create_task(dialog.accept()))
    await page.goto(FORGE + '/modeler.html', wait_until='domcontentloaded', timeout=90000)
    await page.wait_for_function('()=>window.SWRLZ_FORGE_BUILD?.version==="v11.430"&&!!window.SWYRL_ENGINE_MODEL_VR&&!!window.SWYRL_ENGINE_MODEL_WORKSHOP')
    if await page.locator('#seReleaseNotesDialog[open]').count():
        await page.locator('#seReleaseNotesDialog[open] button').last.evaluate('(node)=>node.click()')
    await page.locator('#fileInput').set_input_files(str(native_file))
    await page.wait_for_function('(n)=>window.SWYRL_ENGINE_AGENT.inspectScene().project?.modelAtelier?.parts?.length===n', arg=len(expected_parts))
    await page.wait_for_function('()=>!!document.querySelector("#se340EnterModelVR")')
    if emulated:
        await page.evaluate('async(url)=>{window.__VR_THREE=await import(url)}', THREE_URL)
    if denied:
        await page.evaluate('()=>{navigator.xr.requestSession=()=>Promise.reject(new Error("Test permission denial"));}')
    return context, page

async def enter(page):
    entry = page.locator('#se340EnterModelVR')
    await entry.scroll_into_view_if_needed()
    assert await entry.is_enabled()
    await entry.click()
    await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().active&&window.SWYRL_ENGINE_MODEL_VR.inspect().frameCount>4', timeout=30000)
    await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().controllers.filter(c=>c.targetTracked&&c.gripTracked).length===2')
    await frames(page, 3)

async def settle_menu(page):
    if not (await read(page))['sessionAttached']:
        return
    await page.wait_for_function('()=>{const s=window.SWYRL_ENGINE_MODEL_VR.inspect(),m=s.menu;return !s.sessionAttached||!!m&&(!m.motion?.active||(!!s.gesture||!!s.creation?.active||!!s.accessory?.active)&&m.motion?.reveal>.999&&m.motion?.transition>.999)}', timeout=15000)
    if (await read(page))['sessionAttached']:
        await frames(page, 2)


def native(state):
    return state.get('manual',{}).get('native',{})


def topology_audit(data):
    xyz=data['positions'];indices=data['indices'];edges={};volume=0
    assert len(xyz)%3==0 and len(indices)%3==0
    for f in range(0,len(indices),3):
        ids=indices[f:f+3];assert len(set(ids))==3
        a,b,c=[xyz[i*3:i*3+3] for i in ids]
        ab=[b[k]-a[k] for k in range(3)];ac=[c[k]-a[k] for k in range(3)]
        cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
        assert sum(x*x for x in cross)>1e-18,'A rendered operation collapsed a triangle'
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        for k in range(3):
            edge=(ids[k],ids[(k+1)%3]);edges.setdefault(tuple(sorted(edge)),[]).append(edge)
    assert all(len(value)==2 and value[0]==value[1][::-1] for value in edges.values()),'The cavity must remain consistently wound and manifold'
    return {'vertices':len(xyz)//3,'triangles':len(indices)//3,'signedVolume':volume}


async def manual_menu(page):
    await action_ray(page,'studio')
    await action_ray(page,'mesh')
    await action_ray(page,'manual-mesh')
    state=await read(page);assert state['manual']['active'] and state['page']=='manual-mesh'


async def flow(browser,errors,record):
    context,page=await open_model(browser,errors,quest=True)
    try:
        original=await parts(page)
        assert original==expected_parts
        await enter(page);await settle_menu(page)
        baseline=await read(page);depth=baseline['undoDepth']
        assert baseline['modelRootBorrowed']
        await aim_part(page,'vr430-cube');await tap(page,'right','trigger')
        assert (await read(page))['selectionIds']==['vr430-cube']
        assert await parts(page)==original
        await manual_menu(page)
        await action_ray(page,'manual-convert')
        converted=await parts(page);state=await read(page)
        assert converted[0]['kind']=='topologyMesh' and state['undoDepth']==depth+1
        assert topology_audit(converted[0]['topologyMesh'])=={'vertices':8,'triangles':12,'signedVolume':1.0}
        record('Actual spatial menu converts the selected plain cube into exact welded editable topology in one native Undo step')

        await aim_part(page,'vr430-cube');await tap(page,'right','trigger')
        state=await read(page)
        assert len(native(state)['selection']['faceIds'])==2, state['manual']
        assert native(state)['selection']['mode']=='face'
        assert await parts(page)==converted and state['undoDepth']==depth+1
        await screenshot_xr(page,'manual-flat-region-selected.png')
        record('A real controller Trigger picks two connected coplanar triangles as a highlighted flat face region without changing saved geometry')

        await action_ray(page,'manual-inset')
        await action_ray(page,'manual-learn',side='left')
        lesson=await read(page,True)
        assert lesson['helpVisible'] and lesson['manual']['learning']=='inset' and lesson['menu']['learningTool']=='inset'
        paints=lesson['menu']['paintCount']
        anchor=next(item['center'] for item in lesson['paletteActions'] if item['action']=='help')
        await frames(page,18)
        assert (await read(page))['menu']['paintCount']>paints,'Visible teaching diagrams must advance in the existing XR loop'
        await page.evaluate('()=>xrTestDevice.position.set(.12,1.65,0)');await frames(page,5)
        moved=await read(page,True);new_anchor=next(item['center'] for item in moved['paletteActions'] if item['action']=='help')
        assert distance(anchor,new_anchor)<1e-7,'The teaching window must remain in world space while the head moves'
        await page.evaluate('()=>xrTestDevice.position.set(0,1.65,0)');await frames(page,3)
        assert await parts(page)==converted and (await read(page))['undoDepth']==depth+1
        await screenshot_xr(page,'manual-inset-visual-lesson.png')
        await action_ray(page,'help')
        assert not (await read(page))['helpVisible']
        record('Both controllers operate the shared animated tool lesson; its world-space window stays fixed during head movement and does not edit the model')

        await action_ray(page,'manual-preview')
        state=await read(page)
        assert native(state)['preview']['active'] and native(state)['preview']['operation']=='inset'
        assert native(state)['preview']['stats']['facesAfter']==20 and len(native(state)['preview']['selectedFaces'])==2
        assert await parts(page)==converted and state['undoDepth']==depth+1
        await screenshot_xr(page,'manual-inset-preview.png')
        await tap(page,'right','b-button')
        state=await read(page)
        assert not native(state)['preview']['active'] and state['manual']['active']
        assert await parts(page)==converted and state['undoDepth']==depth+1
        record('Inset previews real border geometry while saved source and history stay unchanged; B cancels the owned preview and keeps manual modeling active')

        await action_ray(page,'manual-preview');await action_ray(page,'manual-apply')
        inset=await parts(page);state=await read(page)
        assert not native(state)['preview']['active'] and state['undoDepth']==depth+2
        assert len(native(state)['selection']['faceIds'])==2 and topology_audit(inset[0]['topologyMesh'])['triangles']==20
        record('Apply commits the inset as one native Undo step and retains only the inner cap faces for the next operation')

        await action_ray(page,'manual-mesh');await action_ray(page,'manual-extrude')
        await action_ray(page,'manual-direction')
        assert (await read(page))['manual']['amount']<0
        await action_ray(page,'manual-preview')
        state=await read(page)
        assert native(state)['preview']['active'] and native(state)['preview']['operation']=='extrude'
        assert await parts(page)==inset and state['undoDepth']==depth+2
        await screenshot_xr(page,'manual-inward-extrude-preview.png')
        await action_ray(page,'manual-apply')
        cavity=await parts(page);state=await read(page);audit=topology_audit(cavity[0]['topologyMesh'])
        assert audit['vertices']==16 and audit['triangles']==28 and 0<audit['signedVolume']<1
        assert state['undoDepth']==depth+3 and len(native(state)['selection']['faceIds'])==2
        await screenshot_xr(page,'manual-cavity-applied.png')
        record('Negative connected-region extrusion creates a real closed, consistently wound cavity with retained floor and one native Undo checkpoint')

        await action_ray(page,'manual-preview')
        assert native(await read(page))['preview']['active']
        await tap(page,'left','y-button')
        state=await read(page)
        assert not native(state)['preview']['active'] and await parts(page)==cavity and state['undoDepth']==depth+3
        await tap(page,'left','y-button')
        assert await parts(page)==inset and (await read(page))['undoDepth']==depth+2
        await chord(page,[['left','x-button'],['left','y-button']])
        assert await parts(page)==cavity and (await read(page))['undoDepth']==depth+3
        record('First Undo cancels an uncommitted preview; the next Undo and controller Redo restore the exact committed native meshes')

        await action_ray(page,'manual-preview')
        assert native(await read(page))['preview']['active']
        await page.evaluate('()=>{xrTestDevice.controllers.right.connected=false;}');await frames(page,6)
        assert not native(await read(page))['preview']['active'] and await parts(page)==cavity and (await read(page))['undoDepth']==depth+3
        await page.evaluate('()=>{const c=xrTestDevice.controllers.right;c.setButtonValueImmediate("trigger",0);c.setButtonValueImmediate("squeeze",0);c.connected=true;}')
        await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().controllers.filter(c=>c.targetTracked&&c.gripTracked).length===2')
        await frames(page,4)
        record('Tracking loss cancels a pending manual preview without committing geometry or touching history; reconnect resumes with fresh input')

        for _ in range(3):await tap(page,'left','y-button')
        assert await parts(page)==original and (await read(page))['undoDepth']==depth
        await action_ray(page,'tools');await action_ray(page,'exit')
        await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
        state=await read(page)
        assert state['nativeParentRestored'] and await parts(page)==original
        assert not errors,errors
        record('Native Undo restores the original primitive and Exit restores the desktop model root with all source data intact')
        return {'originalPartCount':1,'historyRestored':True,'sourceRestored':True,'nativeParentRestored':True,'cavityAudit':audit,'guestOnly':True}
    except Exception as error:
        try:error.manual_state=await read(page,True)
        except Exception:pass
        try:await screenshot_xr(page,'failure.png')
        except Exception:pass
        raise
    finally:
        await context.close()


async def main():
    errors=[]
    receipt={'version':'v11.430','testedHtmlSha256':SHA,
        'runtime':'IWER 2.8.0 / Meta Quest 2 / actual XR renderer and native menu input',
        'iwerSha256':IWER_SHA,'physicalHeadsetAcceptance':False,'checks':[], 'pageErrors':errors,'status':'RUNNING'}
    def record(message):
        receipt['checks'].append(message);(out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print('VR430_CHECK',message,flush=True)
    (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    async with async_playwright() as playwright:
        browser=await playwright.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
        try:
            receipt['nativePreview']=await flow(browser,errors,record);assert not errors,errors;receipt['status']='PASS'
            print('MODEL_VR_V11_430_BROWSER_PASS',json.dumps(receipt),flush=True)
        except Exception as error:
            receipt['status']='FAIL';receipt['failure']=type(error).__name__+': '+str(error)
            if hasattr(error,'manual_state'):receipt['failureState']=error.manual_state
            print('MODEL_VR_V11_430_BROWSER_FAIL',json.dumps(receipt),flush=True)
            raise
        finally:
            (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');await browser.close()


asyncio.run(main())

