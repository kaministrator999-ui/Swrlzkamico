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
cli.add_argument('--native-project', help='Optional read-only native model fixture; never packaged')
args = cli.parse_args()
html = Path(args.html).resolve()
assert html.is_file(), html
out = Path(args.output or tempfile.mkdtemp(prefix='swrlz-model-vr350-')).resolve()
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
    start = (await read(page))['frameCount']
    await page.wait_for_function('(n)=>window.SWYRL_ENGINE_MODEL_VR.inspect().frameCount>=n', arg=start + count, timeout=20000)


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


async def open_model(browser, errors, emulated=True, denied=False):
    context = await browser.new_context(viewport={'width': 1280, 'height': 960}, accept_downloads=True)
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
    await page.wait_for_function('()=>window.SWRLZ_FORGE_BUILD?.version==="v11.350"&&!!window.SWYRL_ENGINE_MODEL_VR')
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
    target = next(item for item in state['paletteActions'] if item['action'] == action)
    await aim(page, target['center'], side=side)
    await button(page, side, key, False)
    await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().wheel')


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


async def main():
    errors = []
    receipt = {'version': 'v11.350', 'testedHtmlSha256': hashlib.sha256(html.read_bytes()).hexdigest(),
               'runtime': 'IWER 2.8.0 / Meta Quest 2 / real native renderer and XR session',
               'iwerSha256': IWER_SHA, 'physicalHeadsetAcceptance': False, 'checks': [], 'pageErrors': errors,
               'status': 'RUNNING'}
    def record(message):
        receipt['checks'].append(message)
        (out / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print('VR350_CHECK', message, flush=True)
    (out / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=args.chromium, headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--enable-unsafe-swiftshader'])
        try:
            context, page = await open_model(browser, errors)
            original = await parts(page)
            actors_before = await page.evaluate('()=>window.SWYRL_ENGINE_AGENT.inspectScene().scene.actors')
            await enter(page)
            state = await read(page, True)
            assert state['mode'] == 'inspect' and state['modelRootBorrowed']
            assert state['partCount'] == len(original)
            assert len(original) >= 2, 'Group checks require a two-part native fixture'
            first, second = [item['id'] for item in state['targetCenters'][:2]]
            depth = state['undoDepth']
            await screenshot_xr(page, 'model-vr-two-hand-studio.png')
            await aim_part(page, first)
            await tap(page, 'right', 'trigger')
            assert selected_ids(await read(page)) == [first]
            await aim_part(page, second, side='left')
            await tap(page, 'left', 'trigger')
            assert set(selected_ids(await read(page))) == {first, second}
            await tap(page, 'left', 'trigger')
            assert selected_ids(await read(page)) == [first]
            await tap(page, 'left', 'trigger')
            assert set(selected_ids(await read(page))) == {first, second}
            assert await parts(page) == original and (await read(page))['undoDepth'] == depth
            record('right trigger selects; left trigger toggles additive selection without saved edits or Undo steps')

            # Left grip belongs to the workbench, even with geometry selected.
            view_before = (await read(page, True))['presentation']
            await button(page, 'left', 'squeeze', True)
            await move_hand(page, [.08, .03, 0], side='left')
            await button(page, 'right', 'squeeze', True)
            await move_hand(page, [.03, 0, 0], side='right')
            await button(page, 'right', 'squeeze', False)
            released_view = (await read(page, True))['presentation']
            assert not (await read(page))['gesture'], 'paired presentation followed a released grip'
            await move_hand(page, [.06, 0, 0], side='right')
            assert (await read(page, True))['presentation'] == released_view
            await button(page, 'left', 'squeeze', False)
            view_after = (await read(page, True))['presentation']
            assert view_before != view_after, 'Inspect grip did not reposition presentation'
            assert await parts(page) == original and (await read(page))['undoDepth'] == depth
            record('Inspect left/both grips move presentation only; releasing either grip ends paired motion and cannot follow a free hand or edit native history')
            await ray_find(page, 'recenter')

            # Group transform previews must not write native descriptors per frame.
            await ray_find(page, 'move')
            await aim_part(page, first)
            await button(page, 'right', 'squeeze', True)
            await wait_kind(page, 'group')
            await move_hand(page, [.07, .02, 0])
            assert await parts(page) == original, 'group preview wrote native descriptors'
            await page.evaluate('''()=>{const c=xrTestDevice.controllers.right;
              c.position.set(c.position.x+.02,c.position.y+.01,c.position.z);c.updateButtonValue('squeeze',0);}''')
            await frames(page, 4)
            moved = await parts(page)
            assert moved != original
            assert all(before['position'] != after['position'] for before, after in zip(original, moved))
            assert (await read(page))['undoDepth'] == depth + 1
            await tap(page, 'left', 'y-button')
            assert await parts(page) == original
            palette_before = (await read(page))['paletteVisible']
            await page.evaluate('''()=>{const c=xrTestDevice.controllers.left;c.updateButtonValue('x-button',1);c.updateButtonValue('y-button',1);}''')
            await frames(page, 3)
            await page.evaluate('''()=>{const c=xrTestDevice.controllers.left;c.updateButtonValue('x-button',0);c.updateButtonValue('y-button',0);}''')
            await frames(page, 3)
            assert await parts(page) == moved
            assert (await read(page))['paletteVisible'] == palette_before
            record('right-grip group Move is preview-only until release, commits one native Undo step; Y Undo and X+Y Redo consume no extra palette action')

            await aim_part(page, first)
            await button(page, 'right', 'squeeze', True)
            await wait_kind(page, 'group')
            await move_hand(page, [.045, 0, 0])
            await page.evaluate('''()=>{const c=xrTestDevice.controllers.right;c.updateButtonValue('b-button',1);c.updateButtonValue('squeeze',0);}''')
            await frames(page, 4)
            assert not (await read(page))['gesture']
            assert await parts(page) == moved and (await read(page))['undoDepth'] == depth + 1
            await button(page, 'right', 'b-button', False)
            record('B wins over same-frame grip release and cancels every selected part without consuming history')

            await ray_find(page, 'two-hand')
            await aim_part(page, first)
            await page.evaluate('''()=>{xrTestDevice.controllers.left.updateButtonValue('squeeze',1);xrTestDevice.controllers.right.updateButtonValue('squeeze',1);}''')
            await frames(page, 4)
            await wait_kind(page, 'two-hand')
            await move_hand(page, [-.045, .015, 0], side='left')
            await move_hand(page, [.045, -.015, 0], side='right')
            assert await parts(page) == moved
            await screenshot_xr(page, 'model-vr-two-hand-preview.png')
            await button(page, 'right', 'squeeze', False)
            await button(page, 'left', 'squeeze', False)
            two_hand = await parts(page)
            assert two_hand != moved and (await read(page))['undoDepth'] == depth + 2
            await tap(page, 'left', 'y-button')
            assert await parts(page) == moved
            await ray_find(page, 'redo')
            assert await parts(page) == two_hand
            record('deliberate two-hand tool scales/rotates the additive selection, previewing both parts and committing one reversible native transaction')

            # A tap cycles; A hold opens the wheel and executes only on release.
            await button(page, 'right', 'a-button', True)
            await page.wait_for_function('()=>!!window.SWYRL_ENGINE_MODEL_VR.inspect().wheel', timeout=10000)
            wheel = await read(page, True)
            wheel_move = next(t for t in wheel['paletteActions'] if t['action'] == 'move')
            await aim(page, wheel_move['center'])
            await button(page, 'right', 'a-button', False)
            await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().mode==="move"&&!window.SWYRL_ENGINE_MODEL_VR.inspect().wheel')
            before_precision = (await read(page))['precision']
            await tap(page, 'left', 'thumbstick')
            assert (await read(page))['precision'] is not before_precision
            await tap(page, 'left', 'thumbstick')
            assert (await read(page))['precision'] is before_precision
            await tap(page, 'right', 'thumbstick')
            assert (await read(page))['lastAction'] in ('focus', 'Focus') or 'focus' in (await read(page))['lastAction'].lower()
            record('A hold opens a ray-selectable tool wheel and release chooses Move; left stick click toggles Precision and right stick click focuses')
            before_navigation = await parts(page)
            navigation_depth = (await read(page))['undoDepth']
            before_view = (await read(page, True))['presentation']
            await page.evaluate('()=>xrTestDevice.controllers.left.updateAxes("thumbstick",.6,0)')
            await frames(page, 6)
            await page.evaluate('()=>xrTestDevice.controllers.left.updateAxes("thumbstick",0,0)')
            await frames(page, 2)
            panned = (await read(page, True))['presentation']
            assert panned['position'] != before_view['position']
            await page.evaluate('()=>xrTestDevice.controllers.right.updateAxes("thumbstick",.6,.3)')
            await frames(page, 6)
            await page.evaluate('()=>xrTestDevice.controllers.right.updateAxes("thumbstick",0,0)')
            await frames(page, 2)
            orbited = (await read(page, True))['presentation']
            assert orbited['yaw'] != panned['yaw']
            await button(page, 'left', 'squeeze', True)
            await page.evaluate('()=>xrTestDevice.controllers.right.updateAxes("thumbstick",0,.6)')
            await frames(page, 6)
            await page.evaluate('()=>xrTestDevice.controllers.right.updateAxes("thumbstick",0,0)')
            await button(page, 'left', 'squeeze', False)
            zoomed = (await read(page, True))['presentation']
            assert zoomed['scale'] != orbited['scale']
            assert await parts(page) == before_navigation and (await read(page))['undoDepth'] == navigation_depth
            record('left stick pans, right stick orbits, and left grip plus right vertical stick zooms presentation without native edits')
            await ray_find(page, 'recenter')

            # A UI hit must never start a stroke on geometry behind the panel.
            await ray_find(page, 'sculpt')
            await choose_wheel(page, 'sculpt-flatten', kind='brush')
            assert (await read(page))['sculptTool'] == 'flatten'
            await choose_wheel(page, 'sculpt-push', kind='brush')
            assert (await read(page))['sculptTool'] == 'push'
            record('Sculpt A-hold wheel chooses native Flatten and Push brush operations on release')
            await aim_part(page, second, side='left')
            await tap(page, 'left', 'trigger')
            assert (await read(page))['selectedId'] == second
            before_sculpt = await parts(page)
            sculpt_depth = (await read(page))['undoDepth']
            radius_target = next(t for t in (await read(page, True))['paletteActions'] if t['action'] == 'brush-radius-plus')
            await aim(page, radius_target['center'])
            await button(page, 'right', 'trigger', True, 8)
            assert not (await read(page))['gesture'] and await parts(page) == before_sculpt
            await button(page, 'right', 'trigger', False)
            record('holding a sculpt trigger on a spatial UI button never edits geometry behind the menu')
            await aim_part(page, first)
            await button(page, 'right', 'trigger', True)
            await wait_kind(page, 'sculpt')
            assert (await read(page))['selectedId'] == first
            await button(page, 'right', 'squeeze', True)
            await button(page, 'right', 'squeeze', False)
            assert (await read(page))['gesture']['kind'] == 'sculpt', 'grip release incorrectly ended trigger-owned stroke'
            assert await parts(page) == before_sculpt
            brush_before = await read(page)
            await page.evaluate('()=>xrTestDevice.controllers.left.updateAxes("thumbstick",.6,-.5)')
            await frames(page, 6)
            await page.evaluate('()=>xrTestDevice.controllers.left.updateAxes("thumbstick",0,0)')
            await frames(page, 2)
            brush_after = await read(page)
            assert brush_after['brushRadius'] > brush_before['brushRadius']
            assert brush_after['brushStrength'] > brush_before['brushStrength']
            assert await parts(page) == before_sculpt
            await tap(page, 'right', 'b-button')
            await button(page, 'right', 'trigger', False)
            assert not (await read(page))['gesture']
            assert await parts(page) == before_sculpt and (await read(page))['undoDepth'] == sculpt_depth
            record('grip release cannot end a trigger-owned sculpt stroke; left stick adjusts the live brush and B cancels preview without native writes/history')
            await aim_part(page, first)
            await button(page, 'right', 'trigger', True)
            await wait_kind(page, 'sculpt')
            await move_hand(page, [.012, .01, 0])
            assert await parts(page) == before_sculpt
            await button(page, 'right', 'trigger', False)
            sculpted = await parts(page)
            assert sculpted != before_sculpt and (await read(page))['undoDepth'] == sculpt_depth + 1
            await tap(page, 'left', 'y-button')
            assert await parts(page) == before_sculpt
            await ray_find(page, 'redo')
            assert await parts(page) == sculpted
            record('right-trigger sculpt can target a different native part, previews its real mesh and persists native vertex edits in one Undo/Redo transaction')

            # Save an actual surface-attached native lasso and exercise its history.
            await ray_find(page, 'draw')
            await action_ray(page, 'lasso')
            before_lasso = await parts(page)
            lasso_depth = (await read(page))['undoDepth']
            await aim_part(page, first)
            await button(page, 'right', 'trigger', True)
            await wait_kind(page, 'lasso')
            for delta in ([.02, 0, 0], [0, .02, 0], [-.02, 0, 0], [0, -.02, 0]):
                await move_hand(page, delta)
            assert await parts(page) == before_lasso
            await button(page, 'right', 'trigger', False)
            lassoed = await parts(page)
            first_before = next(p for p in before_lasso if p['id'] == first)
            first_after = next(p for p in lassoed if p['id'] == first)
            assert len(first_after.get('sculptLassos', [])) == len(first_before.get('sculptLassos', [])) + 1
            assert (await read(page))['surface']['selectedRegionId'] == first_after['sculptLassos'][-1]['id']
            assert (await read(page))['undoDepth'] == lasso_depth + 1
            await tap(page, 'left', 'y-button')
            assert await parts(page) == before_lasso
            await ray_find(page, 'redo')
            assert await parts(page) == lassoed
            await tap(page, 'left', 'y-button')
            assert await parts(page) == before_lasso
            record('tracked lasso trace saves a native surface-attached sculpt region in one reversible history step')

            # Draw an outline by moving the tracked controller across its first ray plane.
            await ray_find(page, 'draw')
            before_draw = await parts(page)
            draw_depth = (await read(page))['undoDepth']
            await aim(page, [.5, 1.25, -1.4], origin=[.5, 1.25, -.35])
            await button(page, 'right', 'trigger', True)
            await wait_kind(page, 'draw')
            for delta in ([.08, 0, 0], [0, .08, 0], [-.08, 0, 0], [0, -.08, 0]):
                await move_hand(page, delta)
            assert await parts(page) == before_draw
            await button(page, 'right', 'trigger', False)
            drawn = await parts(page)
            assert len(drawn) == len(before_draw) + 1 and (await read(page))['undoDepth'] == draw_depth + 1
            new_id = next(p['id'] for p in drawn if p['id'] not in {p['id'] for p in before_draw})
            await ray_find(page, 'extrude')
            await aim_part(page, new_id)
            await button(page, 'right', 'squeeze', True)
            await wait_kind(page, 'extrude')
            await move_hand(page, [0, 0, .035])
            assert await parts(page) == drawn
            await button(page, 'right', 'squeeze', False)
            extruded = await parts(page)
            assert extruded != drawn and (await read(page))['undoDepth'] == draw_depth + 2
            await tap(page, 'left', 'y-button')
            assert await parts(page) == drawn
            await tap(page, 'left', 'y-button')
            assert await parts(page) == before_draw
            record('tracked trigger outline creates a real indexed native face on release; grip extrusion creates thickness with separate single-step Undo transactions')

            await ray_find(page, 'help')
            await screenshot_xr(page, 'model-vr-controller-guide.png')
            await ray_find(page, 'help')
            await page.evaluate('()=>window.SWYRL_ENGINE_MODEL_VR.exit()')
            await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
            assert (await read(page))['nativeParentRestored'] and not (await read(page))['modelRootBorrowed']
            assert await page.evaluate('()=>window.SWYRL_ENGINE_AGENT.inspectScene().scene.actors') == actors_before
            await page.screenshot(path=str(out / 'model-studio-after-vr.png'))
            record('leaving VR restores native Model Studio ownership and leaves Game actors unchanged')

            # Import a supported custom profile through the same file UI a user uses.
            profile = await page.evaluate('()=>window.SWYRL_VR_CONTROLS.currentProfile()')
            for key in list(profile):
                if key not in ('schema', 'profileId', 'profileName', 'profileVersion', 'createdAt', 'modifiedAt', 'dominantHand', 'thresholds', 'bindings'):
                    del profile[key]
            profile.update(profileId='vr-browser-test', profileName='VR browser dispatch check')
            found = False
            for row in profile['bindings']['model']:
                if row[1] == 'tap:A':
                    row[0], row[2], found = 'precision', 'Precision via custom A', True
            assert found, 'Default model profile did not expose editable tap:A'
            profile_file = out / 'custom-profile.vr.json'
            profile_file.write_text(json.dumps(profile))
            await page.locator('#se179VRControlsOpen').evaluate('(node)=>node.click()')
            await page.wait_for_function('()=>!!document.querySelector("#se179VRStudio[open]")')
            await page.locator('#se179VRStudio input[type=file]').set_input_files(str(profile_file))
            await page.wait_for_function('()=>window.SWYRL_VR_CONTROLS.read().profileId==="vr-browser-test"')
            await page.locator('#se179VRStudio button').filter(has_text='Close').first.evaluate('(node)=>node.click()')
            await enter(page)
            state = await read(page)
            old_mode, old_precision = state['mode'], state['precision']
            await tap(page, 'right', 'a-button')
            assert (await read(page))['precision'] is not old_precision
            assert (await read(page))['mode'] == old_mode
            assert await parts(page) == before_draw
            record('normal Controller Studio JSON import remaps A to Precision; actual hardware dispatch obeys custom binding instead of hardcoded tool cycling')
            await page.evaluate('()=>window.SWYRL_ENGINE_MODEL_VR.exit()')
            await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
            await context.close()

            denied_context, denied_page = await open_model(browser, errors, denied=True)
            denied_before = await parts(denied_page)
            await denied_page.locator('#se340EnterModelVR').click()
            await denied_page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().busy&&!!window.SWYRL_ENGINE_MODEL_VR.inspect().error')
            assert not (await read(denied_page))['active'] and await parts(denied_page) == denied_before
            await denied_context.close()
            plain_context, plain_page = await open_model(browser, errors, emulated=False)
            plain_before = await parts(plain_page)
            assert await plain_page.evaluate('()=>window.SWYRL_ENGINE_MODEL_VR.enter()') is False
            assert await parts(plain_page) == plain_before
            await plain_context.close()
            record('permission denial and unsupported browser preserve usable native Model Studio')
            assert not errors, errors
            receipt['status'] = 'PASS'
            (out / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print('MODEL_VR_V11_350_BROWSER_PASS', json.dumps(receipt), flush=True)
        except Exception as error:
            receipt['status'], receipt['failure'] = 'FAIL', type(error).__name__ + ': ' + str(error)
            try:
                receipt['failureState'] = await read(page, True)
                await page.screenshot(path=str(out / 'failure.png'))
            except Exception:
                pass
            (out / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print('MODEL_VR_V11_350_BROWSER_FAIL', json.dumps(receipt), flush=True)
            raise
        finally:
            await browser.close()


asyncio.run(main())
