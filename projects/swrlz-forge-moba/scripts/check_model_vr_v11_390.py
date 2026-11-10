#!/usr/bin/env python3
"""Ergonomic Model VR controller workflow checks using pinned IWER Quest 2 input.

Runs the actual engine renderer/session/controllers in fresh guest profiles.
IWER emulation establishes software contracts, not physical-headset comfort.
The emulator and fixtures never enter the engine package.
"""
import argparse
import asyncio
import hashlib
import json
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
FORGE = 'https://kamiloki-swrlz-forge-moba.static.hf.space'
CHAT = 'https://kamiloki-swyrlz.hf.space'
CDN = 'https://cdn.jsdelivr.net'
THREE_URL = CDN + '/npm/three@0.169.0/+esm'
IWER_URL = CDN + '/npm/iwer@2.8.0/build/iwer.min.js'
IWER_BYTES = 384266
IWER_SHA = '79fb12295642d3cbab36b28a2a4ba8b4a48a5053ce70057da2f249b67daa9780'
cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument('--html', required=True)
cli.add_argument('--output')
cli.add_argument('--chromium', default='/usr/bin/chromium')
cli.add_argument('--iwer', help='Optional local exact iwer@2.8.0 browser bundle')
cli.add_argument('--native-project', help='Optional read-only native model preview; never packaged')
cli.add_argument('--record-video', action='store_true', help='Record a short actual XR menu interaction clip using CDP and system ffmpeg')
args = cli.parse_args()
html = Path(args.html).resolve()
assert html.is_file(), html
out = Path(args.output or tempfile.mkdtemp(prefix='swrlz-model-vr390-')).resolve()
out.mkdir(parents=True, exist_ok=True)
if args.iwer:
    iwer_bytes = Path(args.iwer).read_bytes()
else:
    with urlopen(IWER_URL, timeout=30) as response:
        iwer_bytes = response.read(IWER_BYTES + 1)
assert len(iwer_bytes) == IWER_BYTES and hashlib.sha256(iwer_bytes).hexdigest() == IWER_SHA


def public_fixture(name='Model VR controller check', replacement=False):
    public = json.loads((ROOT / 'scenes/model-atelier-prism-jester.swyrl.json').read_text())
    parts = public['project']['modelAtelier']['parts'][:2]
    parts.append(json.loads(json.dumps(parts[0])))
    for n, part in enumerate(parts):
        part.update(id=('vr-replacement-' if replacement else 'vr-native-') + str(n),
                    name=('Replacement ' if replacement else 'VR check ') + ['sphere','column','cap'][n],
                    position=[[-.5,1.2,0],[.5,1.2,0],[0,1.9,-.02]][n],
                    scale=[[.3,.35,.3],[.3,.45,.3],[.23,.23,.23]][n], rotation=[0, 0, 0],
                    color='#b88bec' if n == 0 else '#68d1d2')
    public['project'].update(name=name, canonicalId='model-vr-check-' + ('replacement' if replacement else 'original'), template='custom')
    public['project']['modelAtelier'] = {'schema': 'swyrl-model-atelier-v1', 'name': name, 'parts': parts}
    public['editor'] = {'studioWorkspace': 'modeler'}
    public['scene'] = {'background': '#141425', 'paths': {}, 'actors': []}
    return public


native_file = Path(args.native_project).resolve() if args.native_project else out / 'model-vr-check.swyrl.json'
if not args.native_project:
    native_file.write_text(json.dumps(public_fixture()))
replacement_file = out / 'model-vr-replacement.swyrl.json'
replacement = public_fixture('Model VR replacement check', True)
replacement_file.write_text(json.dumps(replacement))
expected_parts = json.loads(native_file.read_text())['project']['modelAtelier']['parts']
assert expected_parts


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


async def axes(page, side, x, y, count=4):
    await page.evaluate('([side,x,y])=>xrTestDevice.controllers[side].updateAxes("thumbstick",x,y)', [side,x,y])
    await frames(page,count)


async def chord(page, controls, count=3):
    """Depress/release the named hardware controls together in actual XR frames."""
    await page.evaluate('(items)=>{for(const [side,key]of items)xrTestDevice.controllers[side].updateButtonValue(key,1)}',controls)
    await frames(page,count)
    await page.evaluate('(items)=>{for(const [side,key]of items)xrTestDevice.controllers[side].updateButtonValue(key,0)}',controls)
    await frames(page,3)


async def hints(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_VR_CONTROLLER_HINTS?.inspect?.()||null')


async def target_center(page, part_id):
    return next(item['center'] for item in (await read(page,True))['targetCenters'] if item['id']==part_id)


def distance(a,b):
    return sum((x-y)**2 for x,y in zip(a,b))**.5


async def move_hand(page, delta, rotate=None, side='right'):
    await page.evaluate('''([side,delta,rotate])=>{
      const c=xrTestDevice.controllers[side];c.position.set(c.position.x+delta[0],c.position.y+delta[1],c.position.z+delta[2]);
      if(rotate){const T=window.__VR_THREE,base=new T.Quaternion(c.quaternion.x,c.quaternion.y,c.quaternion.z,c.quaternion.w);
       const q=new T.Quaternion().setFromEuler(new T.Euler(...rotate)).multiply(base);c.quaternion.set(q.x,q.y,q.z,q.w);}
    }''', [side, delta, rotate])
    await frames(page, 5)


async def begin_grip(page, part_id, mode, side='right'):
    if (await read(page))['mode'] != mode:
        await action_ray(page, mode)
        assert (await read(page))['mode'] == mode
    await aim_part(page, part_id, side=side)
    await button(page, side, 'squeeze', True)
    await page.wait_for_function('(side)=>window.SWYRL_ENGINE_MODEL_VR.inspect().gesture?.hand===side', arg=side)


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
    await page.wait_for_function('()=>window.SWRLZ_FORGE_BUILD?.version==="v11.390"&&!!window.SWYRL_ENGINE_MODEL_VR')
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



def selected_ids(state):
    return state.get('selectionIds', state.get('selection', {}).get('ids', []))


async def wait_kind(page, kind):
    await page.wait_for_function('(kind)=>window.SWYRL_ENGINE_MODEL_VR.inspect().gesture?.kind===kind', arg=kind)


async def choose_wheel(page, action, kind=None, side='right', key='a-button'):
    await button(page, side, key, True)
    await page.wait_for_function('()=>!!window.SWYRL_ENGINE_MODEL_VR.inspect().wheel', timeout=10000)
    state = await read(page, True)
    if kind:
        assert state['wheel'] == kind, state['wheel']
    await settle_menu(page)
    state = await read(page, True)
    target = next(item for item in state['paletteActions'] if item['action'] == action)
    await aim(page, target['center'], side=side)
    await button(page, side, key, False)
    await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().wheel')
    await settle_menu(page)


async def ray_find(page, action):
    """Use actual spatial menu navigation, never call editor actions directly."""
    if action=='inspect':
        return await choose_wheel(page,action,kind='tools')
    for _ in range(4):
        state = await read(page, True)
        available = {item['action'] for item in state['paletteActions']}
        if action in available:
            return await action_ray(page, action)
        if 'studio' in available:
            await action_ray(page, 'studio')
        elif 'tools' in available:
            await action_ray(page, 'tools')
        elif 'mesh' in available:
            await action_ray(page, 'mesh')
        else:
            raise AssertionError('Cannot navigate to '+action+': '+str(available))
    raise AssertionError('Spatial menu did not expose '+action)


async def settle_menu(page):
    if not (await read(page))['sessionAttached']:
        return
    await page.wait_for_function('()=>{const s=window.SWYRL_ENGINE_MODEL_VR.inspect(),m=s.menu;return !s.sessionAttached||!!m&&(!m.motion?.active||(!!s.gesture||!!s.creation?.active)&&m.motion?.reveal>.999&&m.motion?.transition>.999)}', timeout=15000)
    if (await read(page))['sessionAttached']:
        await frames(page, 2)


async def video_menus(page, name):
    """Record actual XR canvas updates; the capture never drives editor actions."""
    if not args.record_video:
        return
    import base64
    import shutil
    import time
    executable = shutil.which('ffmpeg')
    if not executable:
        raise AssertionError('--record-video requires installed ffmpeg')
    capture = out / 'video-frames'
    capture.mkdir(exist_ok=True)
    frames_seen = []
    capture_started=time.monotonic()
    acknowledgements = []
    cdp = await page.context.new_cdp_session(page)
    def receive(event):
        if len(frames_seen) < 90 and time.monotonic()-capture_started<=6:
            frames_seen.append((event['metadata']['timestamp'], base64.b64decode(event['data'])))
        acknowledgements.append(asyncio.create_task(cdp.send('Page.screencastFrameAck', {'sessionId': event['sessionId']})))
    cdp.on('Page.screencastFrame', receive)
    await page.evaluate('()=>{xrTestDevice.canvasContainer.style.zIndex="2147483647";}')
    await cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 70, 'maxWidth': 1280, 'maxHeight': 960, 'everyNthFrame': 1})
    try:
        # Show the new shortcut and native placement preview without saving it.
        await chord(page,[['left','x-button'],['right','a-button']])
        await settle_menu(page)
        await action_ray(page,'create-box')
        await aim(page,[.8,1.4,-1.0])
        await frames(page,12)
        await tap(page,'right','b-button')
        await ray_find(page,'tools')
        await choose_wheel(page,'inspect',kind='tools')

    finally:
        await cdp.send('Page.stopScreencast')
        await asyncio.gather(*acknowledgements, return_exceptions=True)
        await cdp.detach()
    assert len(frames_seen) >= 3, 'XR video capture contained too few actual frames'
    lines = []
    for index, (timestamp, data) in enumerate(frames_seen):
        frame = capture / ('frame-%05d.jpg' % index)
        frame.write_bytes(data)
        lines.append("file '"+frame.name+"'")
        following = frames_seen[index+1][0] if index+1 < len(frames_seen) else timestamp+.08
        lines.append('duration %.6f' % max(.015, min(.4, following-timestamp)))
    listing = capture / 'frames.txt'
    listing.write_text('\n'.join(lines)+'\n')
    process = await asyncio.create_subprocess_exec(executable, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-vf', 'fps=12', '-c:v', 'libx264', '-crf', '25', '-preset', 'veryfast', '-movflags', '+faststart', '-pix_fmt', 'yuv420p', '-an', '-t', '6', str(out / name), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    assert process.returncode == 0, stderr.decode()[-1000:]
    assert (out/name).stat().st_size<=10*1024*1024, 'Menu preview video exceeded bounded artifact size'
    shutil.rmtree(capture)


async def readonly_preview(browser, errors, record):
    context, page = await open_model(browser, errors, quest=True)
    try:
        original = await parts(page)
        await enter(page)
        await settle_menu(page)
        state = await read(page, True)
        depth = state['undoDepth']
        assert state['modelRootBorrowed'] and len(state['targetCenters']) == len(original)
        await screenshot_xr(page, 'mage-vr-menu-studio.png')
        await ray_find(page, 'move')
        move = next(t for t in (await read(page, True))['paletteActions'] if t['action'] == 'rotate')
        await aim(page, move['center'])
        await settle_menu(page)
        await screenshot_xr(page, 'mage-vr-menu-hover.png')
        await ray_find(page, 'sculpt')
        await screenshot_xr(page, 'mage-vr-menu-sculpt.png')
        await button(page, 'right', 'a-button', True)
        await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().wheel==="brush"')
        await settle_menu(page)
        await screenshot_xr(page, 'mage-vr-brush-wheel.png')
        await tap(page, 'right', 'b-button')
        await button(page, 'right', 'a-button', False)
        await ray_find(page, 'help')
        await screenshot_xr(page, 'mage-vr-controller-guide.png')
        await ray_find(page, 'help')
        await ray_find(page, 'tools')
        await ray_find(page, 'inspect')
        await chord(page,[['left','x-button'],['right','a-button']])
        await settle_menu(page)
        await screenshot_xr(page,'mage-vr-create-menu.png')
        await action_ray(page,'create-box')
        await aim(page,[.8,1.4,-1.0])
        await frames(page,8)
        assert (await read(page))['creation']['active']
        await screenshot_xr(page,'mage-vr-creation-preview.png')
        await tap(page,'right','b-button')
        await ray_find(page,'tools')
        await video_menus(page, 'mage-vr-menu-interactions.mp4')
        assert await parts(page) == original and (await read(page))['undoDepth'] == depth
        await action_ray(page, 'exit')
        await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
        assert (await read(page))['nativeParentRestored'] and await parts(page) == original
        assert not errors, errors
        await page.screenshot(path=str(out / 'mage-model-studio-restored.png'))
        record('Quest-browser native model preview: all targets visible, animated menu/wheel navigation leaves source data/history unchanged and restores the native editor')
        return {'partCount':len(original),'nativeMeshTargets':len(state['targetCenters']),'deviceProfile':await page.evaluate('()=>window.SWYRL_ENGINE_DEVICE.read().profile'),'modelDataUnchanged':True,'historyUnchanged':True,'nativeParentRestored':True,'inspectOnly':True}
    finally:
        await context.close()


async def main():
    errors=[]
    receipt={'version':'v11.390','testedHtmlSha256':hashlib.sha256(html.read_bytes()).hexdigest(),
             'runtime':'IWER 2.8.0 / Meta Quest 2 / actual renderer and XR frame loop',
             'iwerSha256':IWER_SHA,'physicalHeadsetAcceptance':False,'checks':[],
             'pageErrors':errors,'status':'RUNNING'}
    def record(message):
        receipt['checks'].append(message)
        (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print('VR390_CHECK',message,flush=True)
    (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    async with async_playwright() as playwright:
        browser=await playwright.chromium.launch(executable_path=args.chromium,headless=True,
            args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
        page=None
        try:
            if args.native_project:
                receipt['nativePreview']=await readonly_preview(browser,errors,record)
            else:
                context,page=await open_model(browser,errors)
                original=await parts(page)
                await enter(page)
                await settle_menu(page)
                first,second,third=[item['id'] for item in original]
                depth=(await read(page))['undoDepth']
                assert (await read(page))['mode']=='inspect'
                await aim_part(page,first)
                await button(page,'right','squeeze',True)
                await move_hand(page,[.025,0,0])
                await button(page,'right','squeeze',False)
                assert not (await read(page))['gesture'] and await parts(page)==original
                await aim_part(page,first)
                await tap(page,'right','trigger')
                await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().mode==="grab"')
                assert selected_ids(await read(page))==[first]
                await screenshot_xr(page,'vr390-select-grab.png')
                record('Inspect remains source-safe; deliberate trigger selection immediately arms visible Grab for the selected mesh')

                # Selected-only grip works even while the pointer is in empty space.
                await aim(page,[1.6,1.5,-1.1])
                await button(page,'right','squeeze',True)
                await wait_kind(page,'group')
                assert (await read(page))['gesture']['mode']=='grab'
                await move_hand(page,[.045,.02,0],rotate=[.13,.22,0])
                await axes(page,'right',0,-.7,22)
                await axes(page,'right',0,0)
                assert await parts(page)==original
                assert (await read(page))['undoDepth']==depth
                await button(page,'right','squeeze',False)
                grabbed=await parts(page)
                assert grabbed!=original and (await read(page))['undoDepth']==depth+1
                updated=next(item for item in grabbed if item['id']==first)
                initial=next(item for item in original if item['id']==first)
                assert updated['position']!=initial['position'] and updated['rotation']!=initial['rotation'] and updated['scale']!=initial['scale']
                await tap(page,'left','y-button')
                assert await parts(page)==original
                record('selected-only right Grip combines translation and wrist rotation; right-stick sizing previews native geometry and release commits one reversible edit')

                # The fine clutch must rebase its preview rather than jump when gain changes.
                await aim_part(page,first)
                await tap(page,'right','trigger')
                await aim(page,[1.6,1.5,-1.1])
                await button(page,'right','squeeze',True)
                await wait_kind(page,'group')
                await move_hand(page,[.03,0,0])
                before_fine=await target_center(page,first)
                await button(page,'left','trigger',True,38)
                after_fine=await target_center(page,first)
                assert distance(before_fine,after_fine)<.002,'engaging fine clutch jumps the selected geometry'
                await move_hand(page,[.04,0,0])
                fine_end=await target_center(page,first)
                fine_delta=distance(after_fine,fine_end)
                assert .0002<fine_delta<.02,('fine clutch does not reduce physical motion',fine_delta)
                await button(page,'left','trigger',False,4)
                coarse_start=await target_center(page,first)
                assert distance(fine_end,coarse_start)<.002,'releasing fine clutch jumps the selected geometry'
                await move_hand(page,[.04,0,0])
                coarse_delta=distance(coarse_start,await target_center(page,first))
                assert coarse_delta>fine_delta*1.7,('normal transform gain did not return',fine_delta,coarse_delta)
                assert selected_ids(await read(page))==[first] and await parts(page)==original
                await button(page,'right','squeeze',False)
                assert (await read(page))['undoDepth']==depth+1
                await tap(page,'left','y-button')
                assert await parts(page)==original
                record('left-trigger fine clutch rebases without jumps, keeps selection, reduces held-grip motion and restores normal gain before one native commit')

                # A is a small transform cycle; the hold wheel retains broader tools.
                states=[]
                for _ in range(4):
                    await tap(page,'right','a-button')
                    states.append((await read(page))['mode'])
                assert states==['move','rotate','scale','move'],states
                await choose_wheel(page,'grab',kind='tools')
                assert (await read(page))['mode']=='grab'
                guide=await hints(page)
                rg=[b for controller in guide['labels'] for b in controller['bindings'] if b['key']=='RG']
                assert any(b['visible'] and any(word in b['text'].lower() for word in ['grab','move','turn']) for b in rg),rg
                assert await parts(page)==original and (await read(page))['undoDepth']==depth
                record('A tap cycles only Move/Rotate/Scale while A hold offers Grab and the controller Grip label describes the actual resolved tool')

                # Preserve the owner's reversible sweep, including retracing only new additions.
                await aim_part(page,first)
                await tap(page,'right','trigger')
                await aim_part(page,second,side='left')
                await button(page,'left','trigger',True,5)
                await aim_part(page,third,side='left')
                await frames(page,8)
                assert set(selected_ids(await read(page)))=={first,second,third}
                await aim_part(page,second,side='left')
                await frames(page,8)
                assert set(selected_ids(await read(page)))=={first,second}
                await button(page,'left','trigger',False)
                assert await parts(page)==original and (await read(page))['undoDepth']==depth
                await tap(page,'right','thumbstick')
                focused=await read(page,True)
                assert set(selected_ids(focused))=={first,second}
                mid=[(min(t['center'][i]-t['size'][i]/2 for t in focused['targetCenters'] if t['id'] in (first,second))+max(t['center'][i]+t['size'][i]/2 for t in focused['targetCenters'] if t['id'] in (first,second)))/2 for i in range(3)]
                assert distance(mid,focused['presentation']['position'])<.025,('Focus frames only one part of the selected group',mid,focused['presentation'])
                assert await parts(page)==original
                record('reversible trigger sweep retains prior selection and whole-group Focus frames every selected mesh without modifying source data')

                # The easy creation shortcut is a chord; neither face tap may leak through.
                await chord(page,[['left','x-button'],['right','a-button']])
                await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().page==="create"')
                await settle_menu(page)
                assert (await read(page))['paletteVisible']
                await action_ray(page,'create-box')
                await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().creation?.active')
                await frames(page,12)
                assert await parts(page)==original and (await read(page))['undoDepth']==depth
                await screenshot_xr(page,'vr390-create-preview.png')
                await tap(page,'right','b-button')
                assert not (await read(page))['creation']['active']
                assert await parts(page)==original and (await read(page))['undoDepth']==depth
                record('X+A opens Create without leaking tool/menu taps; choosing a primitive produces a pending ghost and B discards it without source/history edits')

                await chord(page,[['left','x-button'],['right','a-button']])
                await settle_menu(page)
                await action_ray(page,'create-box')
                assert (await read(page))['creation']['active']
                await page.evaluate('()=>{xrTestDevice.controllers.right.connected=false;}')
                await frames(page,6)
                await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().creation?.active')
                assert await parts(page)==original and (await read(page))['undoDepth']==depth
                await page.evaluate('()=>{const c=xrTestDevice.controllers.right;c.setButtonValueImmediate("squeeze",0);c.setButtonValueImmediate("trigger",0);c.setButtonValueImmediate("a-button",0);c.connected=true;}')
                await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().controllers.filter(c=>c.targetTracked&&c.gripTracked).length===2')
                await frames(page,5)
                record('controller disconnection discards a pending creation ghost without native edits; reconnect requires fresh released input before placement')

                await chord(page,[['left','x-button'],['right','a-button']])
                await settle_menu(page)
                await action_ray(page,'create-box')
                assert (await read(page))['creation']['active']
                # A second UI choice must change the draft rather than place behind the panel.
                await action_ray(page,'create-sphere')
                assert (await read(page))['creation']['active'] and await parts(page)==original
                await aim_part(page,first)
                await tap(page,'right','trigger')
                await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().creation?.active')
                placed=await parts(page)
                created=[p for p in placed if p['id'] not in {x['id'] for x in original}]
                assert len(created)==1 and created[0]['kind']=='sphere',created
                created_id=created[0]['id']
                assert selected_ids(await read(page))==[created_id] and (await read(page))['mode']=='grab'
                assert (await read(page))['undoDepth']==depth+1
                await screenshot_xr(page,'vr390-created-selected.png')
                # Freshly created geometry is ready for a selected-only Grip immediately.
                await aim(page,[1.6,1.5,-1.1])
                await button(page,'right','squeeze',True)
                await wait_kind(page,'group')
                await move_hand(page,[.025,.025,0])
                assert await parts(page)==placed
                await button(page,'right','squeeze',False)
                assert await parts(page)!=placed and (await read(page))['undoDepth']==depth+2
                moved_created=await parts(page)
                await chord(page,[['left','x-button'],['right','a-button']])
                await settle_menu(page)
                await action_ray(page,'create-cone')
                await tap(page,'left','y-button')
                assert not (await read(page))['creation']['active']
                assert await parts(page)==moved_created and (await read(page))['undoDepth']==depth+2
                await tap(page,'left','y-button')
                assert await parts(page)==placed
                await tap(page,'left','y-button')
                assert await parts(page)==original
                await chord(page,[['left','x-button'],['left','y-button']])
                assert await parts(page)==placed
                await tap(page,'left','y-button')
                assert await parts(page)==original
                record('fresh trigger placement commits exactly one selected native primitive; immediate Grip editing and native Undo/Redo complete the creation-to-modeling handoff')

                # Either hand can operate a menu; placement keeps the mapped primary hand.
                await chord(page,[['left','x-button'],['right','a-button']])
                await settle_menu(page)
                await action_ray(page,'create-cone',side='left')
                assert (await read(page))['creation']['active'] and await parts(page)==original
                await aim(page,[1.0,1.4,-1.1])
                await tap(page,'right','trigger')
                assert not (await read(page))['creation']['active']
                assert len(await parts(page))==len(original)+1 and (await read(page))['undoDepth']==depth+1
                await tap(page,'left','y-button')
                assert await parts(page)==original
                record('the off-hand can choose a primitive without stranding its draft; the mapped primary trigger places it in one reversible edit')

                # Drawing hands the selected face directly to grip extrusion.
                await ray_find(page,'draw')
                await page.evaluate('()=>{const c=xrTestDevice.controllers.right;c.position.set(.65,1.15,-.45);c.quaternion.set(0,0,0,1);}')
                await frames(page,4)
                await button(page,'right','trigger',True,3)
                for dx,dy in [(.08,0),(0,.08),(-.08,0),(0,-.08)]:
                    await move_hand(page,[dx,dy,0])
                await button(page,'right','trigger',False,4)
                assert (await read(page))['mode']=='extrude'
                face_state=await parts(page)
                assert len(face_state)==len(original)+1
                face_id=selected_ids(await read(page))[0]
                await aim(page,[1.6,1.5,-1.1])
                await button(page,'right','squeeze',True,3)
                await wait_kind(page,'extrude')
                assert (await read(page))['gesture']['id']==face_id
                await move_hand(page,[0,0,.045])
                assert await parts(page)==face_state
                await button(page,'right','squeeze',False,4)
                assert await parts(page)!=face_state and (await read(page))['undoDepth']==depth+2
                await tap(page,'left','y-button')
                assert await parts(page)==face_state
                await tap(page,'left','y-button')
                assert await parts(page)==original
                record('Draw release selects its native face; grip extrudes that selection without precise re-aiming, with separate reversible draw and extrusion steps')

                await ray_find(page,'inspect')
                await aim_part(page,first)
                await tap(page,'right','trigger')
                await aim_part(page,second,side='left')
                await tap(page,'left','trigger')
                assert set(selected_ids(await read(page)))=={first,second}
                await aim(page,[1.6,1.5,-1.1])
                # X is a real modifier: waiting for its studio hold must not
                # make Duplicate fail or select an old wheel card on release.
                await button(page,'left','x-button',True,38)
                await tap(page,'right','trigger')
                await button(page,'left','x-button',False,3)
                duplicated=await parts(page)
                assert len(duplicated)==len(original)+2 and (await read(page))['undoDepth']==depth+1
                duplicate_ids=set(selected_ids(await read(page)))
                assert len(duplicate_ids)==2 and not duplicate_ids.intersection({p['id'] for p in original})
                assert (await read(page))['mode']=='grab'
                await tap(page,'left','y-button')
                assert await parts(page)==original
                # The same chord over a menu must operate its button, never duplicate geometry.
                await ray_find(page,'tools')
                rotate=next(p for p in (await read(page,True))['paletteActions'] if p['action']=='rotate')
                await aim(page,rotate['center'])
                await chord(page,[['left','x-button'],['right','trigger']])
                assert len(await parts(page))==len(original) and (await read(page))['undoDepth']==depth
                assert (await read(page))['mode']=='rotate'
                record('long-held X+trigger duplicates the selected group in one Undo transaction without leaking an old wheel choice; menu ray priority prevents duplication behind a button')

                # Fine control must also remain stable in explicit two-hand editing.
                await aim_part(page,first)
                await tap(page,'right','trigger')
                await aim_part(page,second,side='left')
                await tap(page,'left','trigger')
                await ray_find(page,'two-hand')
                await aim(page,[1.2,1.1,-1.2],side='left')
                await aim(page,[1.6,1.5,-1.1])
                await button(page,'left','squeeze',True,2)
                await button(page,'right','squeeze',True,3)
                await wait_kind(page,'two-hand')
                await move_hand(page,[.035,.015,0])
                pair_before=await target_center(page,first)
                await button(page,'left','trigger',True,3)
                assert distance(pair_before,await target_center(page,first))<.002
                await button(page,'left','trigger',False,3)
                assert distance(pair_before,await target_center(page,first))<.002
                await tap(page,'right','b-button')
                await button(page,'right','squeeze',False)
                await button(page,'left','squeeze',False)
                assert await parts(page)==original and (await read(page))['undoDepth']==depth
                record('fine-clutch boundaries also preserve the explicit two-hand preview; B cancels the grouped transform without history changes')

                await choose_wheel(page,'grab',kind='tools')
                await aim_part(page,first)
                await tap(page,'right','trigger')
                await aim(page,[1.6,1.5,-1.1])
                await button(page,'right','squeeze',True)
                await wait_kind(page,'group')
                await move_hand(page,[.04,.02,0])
                await page.evaluate('()=>{const c=xrTestDevice.controllers.right;c.updateButtonValue("b-button",1);c.updateButtonValue("squeeze",0);}')
                await frames(page,4)
                await button(page,'right','b-button',False)
                assert not (await read(page))['gesture'] and await parts(page)==original and (await read(page))['undoDepth']==depth
                record('B cancels before a same-frame right-Grip release and discards the complete preview without consuming native history')

                # Profile imports remain the source of actual bindings, including held sweep keys.
                await ray_find(page,'exit')
                await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
                assert (await read(page))['nativeParentRestored'] and await parts(page)==original
                profile=await page.evaluate('()=>window.SWYRL_VR_CONTROLS.currentProfile()')
                profile.update(profileId='vr390-remapped-sweep',profileName='VR390 remapped selection')
                for row in profile['bindings']['model']:
                    if row[0]=='select':row[1]='tap:LT'
                    elif row[0]=='multiselect':row[1]='tap:RT'
                profile_file=out/'remapped-selection.vr.json';profile_file.write_text(json.dumps(profile))
                await page.locator('#se179VRControlsOpen').evaluate('(node)=>node.click()')
                await page.wait_for_function('()=>!!document.querySelector("#se179VRStudio[open]")')
                await page.locator('#se179VRStudio input[type=file]').set_input_files(str(profile_file))
                await page.wait_for_function('()=>window.SWYRL_VR_CONTROLS.read().profileId==="vr390-remapped-sweep"')
                await page.locator('#se179VRStudio button').filter(has_text='Close').first.evaluate('(node)=>node.click()')
                await enter(page)
                await aim_part(page,first,side='left')
                await tap(page,'left','trigger')
                assert selected_ids(await read(page))==[first]
                await aim_part(page,second)
                await button(page,'right','trigger',True,5)
                await aim_part(page,third)
                await frames(page,8)
                assert set(selected_ids(await read(page)))=={first,second,third}
                await aim_part(page,second)
                await frames(page,8)
                assert set(selected_ids(await read(page)))=={first,second}
                await button(page,'right','trigger',False)
                assert await parts(page)==original and (await read(page))['undoDepth']==depth
                record('normal Controller Studio import remaps selection hands; reversible sweep follows the mapped physical trigger instead of a hardcoded left button')
                await ray_find(page,'exit')
                await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
                assert (await read(page))['nativeParentRestored'] and not (await read(page))['modelRootBorrowed']
                assert await parts(page)==original
                await page.screenshot(path=str(out/'vr390-model-studio-restored.png'))
                await context.close()
                record('leaving the ergonomic workflow restores native Model Studio ownership with unchanged fixture geometry after all Undo/cancel checks')
            assert not errors,errors
            receipt['status']='PASS'
            (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
            print('MODEL_VR_V11_390_BROWSER_PASS',json.dumps(receipt),flush=True)
        except Exception as error:
            receipt['status']='FAIL';receipt['failure']=type(error).__name__+': '+str(error)
            if page:
                try:
                    receipt['failureState']=await read(page,True)
                    await page.screenshot(path=str(out/'failure.png'))
                except Exception:
                    pass
            (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
            print('MODEL_VR_V11_390_BROWSER_FAIL',json.dumps(receipt),flush=True)
            raise
        finally:
            await browser.close()


asyncio.run(main())
