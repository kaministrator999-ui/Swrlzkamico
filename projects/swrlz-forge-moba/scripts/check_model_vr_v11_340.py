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
out = Path(args.output or tempfile.mkdtemp(prefix='swrlz-model-vr340-')).resolve()
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


async def button(page, side, key, pressed, count=3):
    await page.evaluate('([side,key,value])=>xrTestDevice.controllers[side].updateButtonValue(key,value)', [side, key, 1 if pressed else 0])
    await frames(page, count)


async def tap(page, side, key):
    await button(page, side, key, True)
    await button(page, side, key, False)


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
    target = next(item for item in detail['paletteActions'] if item['action'] == action)
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
    await page.wait_for_function('()=>window.SWRLZ_FORGE_BUILD?.version==="v11.340"&&!!window.SWYRL_ENGINE_MODEL_VR')
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


async def main():
    errors = []
    receipt = {'version': 'v11.340', 'testedHtmlSha256': hashlib.sha256(html.read_bytes()).hexdigest(),
               'runtime': 'IWER 2.8.0 / Meta Quest 2 / real native renderer and XR session',
               'iwerSha256': IWER_SHA, 'physicalHeadsetAcceptance': False, 'checks': [], 'pageErrors': errors}
    receipt['status'] = 'RUNNING'
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
            part_id = state['targetCenters'][0]['id']
            await screenshot_xr(page, 'model-vr-stage.png')
            initial_depth = state['undoDepth']
            await aim_part(page, part_id)
            await tap(page, 'right', 'trigger')
            assert (await read(page))['selectedId'] == part_id
            await button(page, 'right', 'squeeze', True)
            await move_hand(page, [.07, 0, 0])
            await button(page, 'right', 'squeeze', False)
            assert await parts(page) == original
            assert (await read(page))['undoDepth'] == initial_depth
            receipt['checks'].append('actual Quest target-ray trigger selects native parts; default Inspect grip does not edit or consume history')

            # A stale selection must not become a grab when the ray misses.
            await action_ray(page, 'move')
            await aim(page, [3, 2.8, -.3])
            missed = next(controller for controller in (await read(page))['controllers'] if controller['handedness'] == 'right')
            assert missed['hoverId'] is None and missed['reticleVisible'] is False, ('Miss ray retained a surface reticle', missed)
            await button(page, 'right', 'squeeze', True)
            assert not (await read(page))['gesture']
            await move_hand(page, [.04, 0, 0])
            await button(page, 'right', 'squeeze', False)
            assert await parts(page) == original
            assert (await read(page))['undoDepth'] == initial_depth
            receipt['checks'].append('gripping a miss ray cannot transform a previously selected part')

            await begin_grip(page, part_id, 'move')
            center_before = next(item['center'] for item in (await read(page, True))['targetCenters'] if item['id'] == part_id)
            await move_hand(page, [.07, .02, 0])
            assert await parts(page) == original, 'Grip preview mutated saved data before release'
            await screenshot_xr(page, 'model-vr-moving.png')
            # Sample final hand motion and Grip-up in the same native XR frame.
            await page.evaluate('''()=>{const c=xrTestDevice.controllers.right;
              c.position.set(c.position.x+.02,c.position.y+.01,c.position.z);
              c.updateButtonValue('squeeze',0);
            }''')
            await frames(page, 5)
            moved = await parts(page)
            assert moved != original and len(moved) == len(original)
            assert (await read(page))['undoDepth'] == initial_depth + 1
            center_after = next(item['center'] for item in (await read(page, True))['targetCenters'] if item['id'] == part_id)
            observed_delta = [after - before for before, after in zip(center_before, center_after)]
            assert all(abs(observed - expected) < .002 for observed, expected in zip(observed_delta, [.09, .03, 0])), ('Final release-frame motion was not committed', observed_delta)
            for before, after in zip(original, moved):
                if before['id'] != part_id:
                    assert before == after
            await tap(page, 'left', 'y-button')
            assert await parts(page) == original
            await action_ray(page, 'redo')
            assert await parts(page) == moved
            receipt['checks'].append('tracked grip-space Move previews derived mesh only; same-frame release motion is included in one native history step; controller Undo and panel Redo round trip')

            await begin_grip(page, part_id, 'move')
            await move_hand(page, [.06, 0, 0])
            await tap(page, 'right', 'b-button')
            await button(page, 'right', 'squeeze', False)
            assert await parts(page) == moved
            assert (await read(page))['undoDepth'] == initial_depth + 1
            await begin_grip(page, part_id, 'move')
            await move_hand(page, [.045, 0, 0])
            await page.evaluate('''()=>{const c=xrTestDevice.controllers.right;
              c.updateButtonValue('b-button',1);c.updateButtonValue('squeeze',0);
            }''')
            await frames(page, 5)
            assert not (await read(page))['gesture']
            assert await parts(page) == moved
            assert (await read(page))['undoDepth'] == initial_depth + 1
            await button(page, 'right', 'b-button', False)
            await begin_grip(page, part_id, 'move', side='left')
            await move_hand(page, [.035, 0, 0], side='left')
            await page.evaluate('''()=>{xrTestDevice.controllers.right.updateButtonValue('b-button',1);
              xrTestDevice.controllers.left.updateButtonValue('squeeze',0);
            }''')
            await frames(page, 5)
            assert not (await read(page))['gesture']
            assert await parts(page) == moved
            assert (await read(page))['undoDepth'] == initial_depth + 1
            await button(page, 'right', 'b-button', False)
            await begin_grip(page, part_id, 'move')
            await button(page, 'right', 'squeeze', False)
            assert (await read(page))['undoDepth'] == initial_depth + 1
            await begin_grip(page, part_id, 'move')
            await move_hand(page, [.05, 0, 0])
            await page.evaluate('()=>{xrTestDevice.controllers.right.connected=false;}')
            await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().gesture')
            assert await parts(page) == moved
            assert (await read(page))['undoDepth'] == initial_depth + 1
            await page.evaluate('()=>{const c=xrTestDevice.controllers.right;c.setButtonValueImmediate("squeeze",0);c.setButtonValueImmediate("trigger",0);c.connected=true;}')
            await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().controllers.some(c=>c.handedness==="right"&&c.gripTracked)')
            await frames(page, 3)
            receipt['checks'].append('B cancel, same-frame right-B plus either hand Grip release, no-op grip and controller disconnection preserve native descriptors and history')

            await begin_grip(page, part_id, 'rotate')
            await move_hand(page, [0, 0, 0], [0, 0, .18])
            await button(page, 'right', 'squeeze', False)
            rotated = await parts(page)
            assert rotated != moved
            target_before = next(p for p in moved if p['id'] == part_id)
            target_after = next(p for p in rotated if p['id'] == part_id)
            assert target_before['rotation'] != target_after['rotation']
            assert target_before['position'] == target_after['position']
            assert target_before['scale'] == target_after['scale']
            await begin_grip(page, part_id, 'scale')
            await move_hand(page, [0, .07, 0])
            await button(page, 'right', 'squeeze', False)
            scaled = await parts(page)
            scaled_target = next(p for p in scaled if p['id'] == part_id)
            assert scaled_target['scale'] != target_after['scale'] and all(0 < n <= 20 for n in scaled_target['scale'])
            assert scaled_target['rotation'] == target_after['rotation']
            receipt['checks'].append('tracked wrist rotation and grip-height uniform scaling commit only their native transform fields')

            # Holding the trigger over a toggle must fire once, not every XR frame.
            before_precision = (await read(page))['precision']
            target = next(t for t in (await read(page, True))['paletteActions'] if t['action'] == 'precision')
            await aim(page, target['center'])
            await button(page, 'right', 'trigger', True, 8)
            assert (await read(page))['precision'] is not before_precision
            await button(page, 'right', 'trigger', False)
            assert (await read(page))['precision'] is not before_precision
            assert await parts(page) == scaled
            await action_ray(page, 'help')
            assert (await read(page))['helpVisible']
            await screenshot_xr(page, 'model-vr-controller-guide.png')
            await action_ray(page, 'help')
            await action_ray(page, 'snap')
            assert (await read(page))['snap']
            assert await parts(page) == scaled
            receipt['checks'].append('ray-selectable panel toggles fire once per trigger edge; guide, precision and snap do not mutate native model data')

            await begin_grip(page, part_id, 'move')
            await move_hand(page, [.04, 0, 0])
            await page.evaluate('()=>window.SWYRL_ENGINE_MODEL_VR.exit()')
            await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().active&&!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
            state = await read(page)
            assert not state['modelRootBorrowed'] and state['nativeParentRestored']
            assert await parts(page) == scaled
            assert await page.locator('#modelAtelierPanel').is_visible()
            assert await page.evaluate('()=>window.SWYRL_ENGINE_AGENT.inspectScene().scene.actors') == actors_before
            await page.screenshot(path=str(out / 'model-studio-after-vr.png'))
            await enter(page)
            assert (await read(page))['mode'] == 'inspect'
            assert await parts(page) == scaled
            await page.evaluate('()=>window.SWYRL_ENGINE_MODEL_VR.exit()')
            await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
            assert not (await read(page))['modelRootBorrowed']
            receipt['checks'].append('session end cancels pending preview and restores exact native Modeler ownership; reentry creates a fresh session without model or Game-actor changes')

            # The new Model session must not claim the existing Game doorway.
            await page.locator('#modelAtelierPanel [data-se187-tab="game"]').evaluate('(node)=>node.click()')
            await page.wait_for_function('()=>window.SWYRL_ENGINE_STUDIOS.active()==="game"')
            assert await page.evaluate('()=>window.SWYRL_ENGINE_XR.enter()') is True
            await page.wait_for_function('()=>window.SWYRL_ENGINE_XR.read().active&&window.SWYRL_ENGINE_XR.read().nativeSceneShared')
            assert not (await read(page))['active'] and not (await read(page))['modelRootBorrowed']
            assert await page.evaluate('()=>window.SWYRL_ENGINE_XR.exit()') is True
            await page.wait_for_function('()=>!window.SWYRL_ENGINE_XR.read().active')
            await page.locator('#se320GameHeader [data-se187-tab="modeler"]').evaluate('(node)=>node.click()')
            await page.wait_for_function('()=>window.SWYRL_ENGINE_STUDIOS.active()==="modeler"')
            assert await parts(page) == scaled
            assert await page.evaluate('()=>window.SWYRL_ENGINE_AGENT.inspectScene().scene.actors') == actors_before
            receipt['checks'].append('legacy Game XR enters and exits after Model XR without claiming Model ownership or changing model and actor data')

            await enter(page)
            await begin_grip(page, part_id, 'move')
            await move_hand(page, [.04, 0, 0])
            await page.locator('#fileInput').set_input_files(str(replacement_file))
            await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
            assert await parts(page) == replacement['project']['modelAtelier']['parts']
            assert not (await read(page))['modelRootBorrowed']
            receipt['checks'].append('document replacement during a gesture exits safely without restoring stale native part data')
            await context.close()

            denied_context, denied_page = await open_model(browser, errors, denied=True)
            denied_before = await parts(denied_page)
            await denied_page.locator('#se340EnterModelVR').click()
            await denied_page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().busy&&!!window.SWYRL_ENGINE_MODEL_VR.inspect().error')
            denied_state = await read(denied_page)
            assert not denied_state['active'] and not denied_state['modelRootBorrowed']
            assert await parts(denied_page) == denied_before
            await denied_context.close()
            plain_context, plain_page = await open_model(browser, errors, emulated=False)
            plain_before = await parts(plain_page)
            result = await plain_page.evaluate('()=>window.SWYRL_ENGINE_MODEL_VR.enter()')
            assert result is False and not (await read(plain_page))['active']
            assert await parts(plain_page) == plain_before
            assert await plain_page.locator('#modelAtelierPanel').is_visible()
            await plain_context.close()
            receipt['checks'].append('permission denial and unsupported immersive browser leave the normal Modeler document usable and unchanged')
            assert not errors, errors
            receipt['status'] = 'PASS'
            (out / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print('MODEL_VR_V11_340_BROWSER_PASS', json.dumps(receipt), flush=True)
        except Exception as error:
            receipt['status'] = 'FAIL'
            receipt['failure'] = type(error).__name__ + ': ' + str(error)
            (out / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print('MODEL_VR_V11_340_BROWSER_FAIL', json.dumps(receipt), flush=True)
            raise
        finally:
            await browser.close()


asyncio.run(main())
