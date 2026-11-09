#!/usr/bin/env python3
"""Native Model Studio XR checks using the pinned, test-only IWER Quest 2 runtime.

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
out = Path(args.output or tempfile.mkdtemp(prefix='swrlz-model-vr360-')).resolve()
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
    for n, part in enumerate(parts):
        part.update(id=('vr-replacement-' if replacement else 'vr-native-') + str(n),
                    name=('Replacement ' if replacement else 'VR check ') + ('sphere' if n == 0 else 'column'),
                    position=[-.5 if n == 0 else .5, 1.2, 0],
                    scale=[.3, .35 if n == 0 else .45, .3], rotation=[0, 0, 0],
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


async def action_ray(page, action):
    detail = await read(page, True)
    target = next((item for item in detail['paletteActions'] if item['action'] == action), None)
    if target is None:
        raise AssertionError('Action '+action+' missing on page '+str(detail.get('page'))+': '+str([i['action'] for i in detail['paletteActions']]))
    await aim(page, target['center'])
    await tap(page, 'right', 'trigger')
    await settle_menu(page)


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
    await page.wait_for_function('()=>window.SWRLZ_FORGE_BUILD?.version==="v11.360"&&!!window.SWYRL_ENGINE_MODEL_VR')
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
    await page.wait_for_function('()=>{const s=window.SWYRL_ENGINE_MODEL_VR.inspect(),m=s.menu;return !s.sessionAttached||!!m&&!m.motion?.active}', timeout=15000)
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
        # A short, real-input sequence shows lift, activation, page reveal and wheel motion.
        target=next(p for p in (await read(page,True))['paletteActions'] if p['action']=='rotate')
        await aim(page,target['center'])
        await tap(page,'right','trigger')
        await action_ray(page,'sculpt')
        await choose_wheel(page,'sculpt-flatten',kind='brush')
        await ray_find(page,'tools')
        await action_ray(page,'inspect')

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
    receipt={'version':'v11.360','testedHtmlSha256':hashlib.sha256(html.read_bytes()).hexdigest(),
             'runtime':'IWER 2.8.0 / Meta Quest 2 / actual renderer and XR frame loop',
             'iwerSha256':IWER_SHA,'physicalHeadsetAcceptance':False,'checks':[],
             'pageErrors':errors,'status':'RUNNING'}
    def record(message):
        receipt['checks'].append(message)
        (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print('VR360_CHECK',message,flush=True)
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
                state=await read(page,True)
                first,second=[p['id'] for p in state['targetCenters'][:2]]
                depth=state['undoDepth']
                assert state['menu']['width']>=.6 and state['menu']['height']>=.6
                assert state['menu']['buttonCount']>=12
                await screenshot_xr(page,'vr-menu-studio.png')
                move=next(p for p in state['paletteActions'] if p['action']=='move')
                await aim(page,move['center'])
                await settle_menu(page)
                assert (await read(page))['menu']['hovered']=='move'
                paint=(await read(page))['menu']['paintCount']
                await frames(page,12)
                assert (await read(page))['menu']['paintCount']==paint, 'idle UI redraws canvas textures every XR frame'
                await screenshot_xr(page,'vr-menu-hover.png')
                record('larger spatial console exposes readable actions; actual controller hover animates and settles without repainting idle canvas textures')

                # Disabled controls stay inert while their plate blocks geometry behind them.
                undo=next(p for p in (await read(page,True))['paletteActions'] if p['action']=='undo')
                await aim(page,undo['center'])
                await tap(page,'right','trigger')
                assert await parts(page)==original and (await read(page))['undoDepth']==depth
                assert not (await read(page))['gesture']
                await action_ray(page,'move')
                assert (await read(page))['mode']=='move'
                await screenshot_xr(page,'vr-menu-active-tool.png')
                record('disabled Undo remains inert and blocks pick-through; enabled spatial card selects the tool without altering model geometry')

                for action in ['sculpt','draw','views','cameras','aim']:
                    await ray_find(page,action)
                    assert not (await read(page))['gesture'] and await parts(page)==original
                await ray_find(page,'help')
                assert (await read(page))['helpVisible']
                await screenshot_xr(page,'vr-menu-controller-guide.png')
                await tap(page,'right','b-button')
                await settle_menu(page)
                guide_back=await read(page)
                assert not guide_back['helpVisible'] and guide_back['page']=='tools' and guide_back['mode']=='inspect'
                await ray_find(page,'help')
                await action_ray(page,'help')
                assert not (await read(page))['helpVisible']
                record('persistent navigation reaches Sculpt, Draw, Display, Angles, Aim and readable Guide; physical B returns to Tools/Inspect and the visible Back action also closes Guide')

                await ray_find(page,'tools')
                await choose_wheel(page,'rotate',kind='tools')
                assert (await read(page))['mode']=='rotate'
                await choose_wheel(page,'sculpt',kind='studio',side='left',key='x-button')
                assert (await read(page))['mode']=='sculpt'
                await choose_wheel(page,'sculpt-flatten',kind='brush')
                assert (await read(page))['sculptTool']=='flatten'
                await button(page,'right','a-button',True)
                await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().wheel==="brush"')
                await settle_menu(page)
                await screenshot_xr(page,'vr-menu-brush-wheel.png')
                await tap(page,'right','b-button')
                await button(page,'right','a-button',False)
                assert not (await read(page))['wheel']
                assert await parts(page)==original
                record('tool, studio and brush radial menus select through physical A/X holds and release; B cancels the wheel without executing a hidden action')

                # Keep the existing editor dispatch visible under the new shell.
                await ray_find(page,'inspect')
                await aim_part(page,first)
                await tap(page,'right','trigger')
                await aim_part(page,second,side='left')
                await tap(page,'left','trigger')
                assert set(selected_ids(await read(page)))=={first,second}
                await ray_find(page,'move')
                await aim_part(page,first)
                await button(page,'right','squeeze',True)
                await wait_kind(page,'group')
                await move_hand(page,[.04,.015,0])
                assert await parts(page)==original
                await page.evaluate('()=>{const c=xrTestDevice.controllers.right;c.updateButtonValue("b-button",1);c.updateButtonValue("squeeze",0);}')
                await frames(page,4)
                await button(page,'right','b-button',False)
                assert not (await read(page))['gesture'] and await parts(page)==original and (await read(page))['undoDepth']==depth
                record('native additive selection and right-grip group preview survive the menu redesign; B still wins over simultaneous grip release with no saved edits')

                await ray_find(page,'sculpt')
                radius=next(p for p in (await read(page,True))['paletteActions'] if p['action']=='brush-radius-plus')
                await aim(page,radius['center'])
                await button(page,'right','trigger',True,6)
                assert not (await read(page))['gesture'] and await parts(page)==original
                await button(page,'right','trigger',False)
                await aim_part(page,first)
                await button(page,'right','trigger',True)
                await wait_kind(page,'sculpt')
                await tap(page,'right','b-button')
                await button(page,'right','trigger',False)
                assert not (await read(page))['gesture'] and await parts(page)==original
                record('Sculpt controls keep UI hit priority and hold-trigger strokes remain cancelable without source/history mutations')

                await ray_find(page,'tools')
                await ray_find(page,'inspect')
                await tap(page,'left','x-button')
                assert not (await read(page))['paletteVisible']
                assert not (await read(page,True))['paletteActions'], 'hidden menu reports live actions'
                await aim_part(page,first)
                await tap(page,'right','trigger')
                assert selected_ids(await read(page))==[first]
                await tap(page,'left','x-button')
                await settle_menu(page)
                assert (await read(page))['paletteVisible']
                record('hidden palette cannot block or advertise stale buttons; re-opening restores the animated console and native selection remains usable')

                await page.emulate_media(reduced_motion='reduce')
                await frames(page,5)
                assert (await read(page))['menu']['motion']['reducedMotion']
                await action_ray(page,'views')
                assert not (await read(page))['menu']['motion']['active']
                await page.emulate_media(reduced_motion='no-preference')
                await frames(page,5)
                assert not (await read(page))['menu']['motion']['reducedMotion']
                record('system reduced-motion preference snaps menu transitions; returning to normal motion restores animation without a second render loop')

                assert await parts(page)==original and (await read(page))['undoDepth']==depth
                await ray_find(page,'help')
                # Exit is operated by the same ray hit system even from the Guide.
                await action_ray(page,'exit')
                await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
                assert (await read(page))['nativeParentRestored'] and not (await read(page))['modelRootBorrowed']
                assert await parts(page)==original
                await page.screenshot(path=str(out/'model-studio-after-vr.png'))
                await context.close()
                record('Guide Exit restores Model Studio root ownership; the full menu interaction run preserves serialized geometry and native Undo depth')
            assert not errors,errors
            receipt['status']='PASS'
            (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
            print('MODEL_VR_V11_360_BROWSER_PASS',json.dumps(receipt),flush=True)
        except Exception as error:
            receipt['status']='FAIL';receipt['failure']=type(error).__name__+': '+str(error)
            if page:
                try:
                    receipt['failureState']=await read(page,True)
                    await page.screenshot(path=str(out/'failure.png'))
                except Exception:
                    pass
            (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
            print('MODEL_VR_V11_360_BROWSER_FAIL',json.dumps(receipt),flush=True)
            raise
        finally:
            await browser.close()


asyncio.run(main())


