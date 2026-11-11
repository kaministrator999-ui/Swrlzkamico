#!/usr/bin/env python3
"""Native bag accessory workshop checks using pinned IWER Quest 2 input.

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
cli.add_argument('--native-project', help='Optional existing native model; guest accessory edits are undone before exit')
cli.add_argument('--record-video', action='store_true', help='Record a short actual XR menu interaction clip using CDP and system ffmpeg')
args = cli.parse_args()
html = Path(args.html).resolve()
assert html.is_file(), html
out = Path(args.output or tempfile.mkdtemp(prefix='swrlz-model-vr410-')).resolve()
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
    await page.wait_for_function('()=>window.SWRLZ_FORGE_BUILD?.version==="v11.410"&&!!window.SWYRL_ENGINE_MODEL_VR')
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
    await page.wait_for_function('()=>{const s=window.SWYRL_ENGINE_MODEL_VR.inspect(),m=s.menu;return !s.sessionAttached||!!m&&(!m.motion?.active||(!!s.gesture||!!s.creation?.active||!!s.accessory?.active)&&m.motion?.reveal>.999&&m.motion?.transition>.999)}', timeout=15000)
    if (await read(page))['sessionAttached']:
        await frames(page, 2)


def accessory(state):
    return state.get('accessory') or {}


def accessory_params(state):
    value=accessory(state)
    return value.get('params') or value.get('parameters') or {}


async def accessory_active(page):
    await page.wait_for_function('()=>!!window.SWYRL_ENGINE_MODEL_VR.inspect().accessory?.active')


async def open_accessory(page):
    await chord(page,[['left','x-button'],['right','a-button']])
    await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().page==="create"')
    await settle_menu(page)
    await action_ray(page,'accessory-menu')
    if not accessory(await read(page)).get('active'):
        await action_ray(page,'create-pouch')
    await accessory_active(page)
    await settle_menu(page)


async def finish_accessory(page):
    await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().accessory?.active')
    await frames(page,3)


async def aim_accessory_surface(page,target_id,original):
    # The reference mage already has a satchel on its +X hip. Show the new
    # reusable tool on the other hip rather than hiding two bags in one spot.
    if args.native_project and any(p.get('name')=='Mage robe' for p in original):
        state=await read(page,True)
        point=await page.evaluate('(matrix)=>new __VR_THREE.Vector3(-.43,1.02,.45).applyMatrix4(new __VR_THREE.Matrix4().fromArray(matrix)).toArray()',state['modelRootMatrix'])
        await aim(page,point)
    else:
        await aim_part(page,target_id)
    await frames(page,5)


def topology_valid(part):
    mesh=part.get('topologyMesh') or {}
    xyz=mesh.get('positions') or []
    indices=mesh.get('indices') or []
    assert len(xyz)>=9 and len(xyz)%3==0 and len(indices)>=3 and len(indices)%3==0,part.get('name')
    assert all(isinstance(v,(int,float)) and abs(v)<1e6 for v in xyz)
    assert all(isinstance(i,int) and 0<=i<len(xyz)//3 for i in indices)


async def bounded_video(page,name):
    """Record actual ray-driven workshop feedback, never a fabricated UI view."""
    if not args.record_video:
        return
    import base64,shutil,time
    executable=shutil.which('ffmpeg')
    if not executable:
        raise AssertionError('--record-video needs system ffmpeg')
    capture=out/'video-frames';capture.mkdir(exist_ok=True)
    seen=[];acks=[];started=time.monotonic()
    cdp=await page.context.new_cdp_session(page)
    def receive(event):
        if len(seen)<90 and time.monotonic()-started<=6:
            seen.append((event['metadata']['timestamp'],base64.b64decode(event['data'])))
        acks.append(asyncio.create_task(cdp.send('Page.screencastFrameAck',{'sessionId':event['sessionId']})))
    cdp.on('Page.screencastFrame',receive)
    await page.evaluate('()=>{xrTestDevice.canvasContainer.style.zIndex="2147483647";}')
    await cdp.send('Page.startScreencast',{'format':'jpeg','quality':70,'maxWidth':1280,'maxHeight':960,'everyNthFrame':1})
    try:
        await action_ray(page,'accessory-body')
        await action_ray(page,'accessory-width-plus')
        await action_ray(page,'accessory-rounding-plus')
        await action_ray(page,'accessory-menu')
        await action_ray(page,'accessory-details')
    finally:
        await cdp.send('Page.stopScreencast');await asyncio.gather(*acks,return_exceptions=True);await cdp.detach()
    assert len(seen)>=3,'Too few actual rendered frames'
    listing=[]
    for index,(stamp,data) in enumerate(seen):
        p=capture/('frame-%05d.jpg'%index);p.write_bytes(data);listing.append("file '"+p.name+"'")
        following=seen[index+1][0] if index+1<len(seen) else stamp+.08
        listing.append('duration %.6f'%max(.015,min(.4,following-stamp)))
    manifest=capture/'frames.txt';manifest.write_text('\n'.join(listing)+'\n')
    process=await asyncio.create_subprocess_exec(executable,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(manifest),'-vf','fps=12','-c:v','libx264','-crf','25','-preset','veryfast','-movflags','+faststart','-pix_fmt','yuv420p','-an','-t','6',str(out/name),stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
    _,stderr=await process.communicate();assert process.returncode==0,stderr.decode()[-1000:]
    assert (out/name).stat().st_size<=10*1024*1024
    shutil.rmtree(capture)


async def reference_mage_flow(browser,errors,record):
    """Bounded reference-specific proof; shared cancellation is checked above."""
    source_hash=hashlib.sha256(native_file.read_bytes()).hexdigest()
    context,page=await open_model(browser,errors,quest=True)
    try:
        original=await parts(page);original_ids={p['id'] for p in original}
        await enter(page);await settle_menu(page)
        depth=(await read(page))['undoDepth']
        await open_accessory(page)
        assert await parts(page)==original and (await read(page))['undoDepth']==depth
        await screenshot_xr(page,'mage-accessory-workshop.png')
        record('Reference mage opens in a fresh guest editor with a clearly visible pouch preview and unchanged source/history')

        await action_ray(page,'accessory-details')
        before=accessory_params(await read(page)).copy()
        await action_ray(page,'accessory-flap-plus')
        await action_ray(page,'accessory-strap-plus')
        await action_ray(page,'accessory-material')
        after=accessory_params(await read(page))
        assert after['flap']!=before['flap'] and after['strap']!=before['strap']
        assert after.get('bodyColor')!=before.get('bodyColor')
        assert await parts(page)==original and (await read(page))['undoDepth']==depth
        record('Reference pouch flap, belt loops and coordinated leather finish adjust through real spatial controls without changing the mage')

        await action_ray(page,'accessory-fit')
        await action_ray(page,'accessory-surface')
        target_id=next((p['id'] for p in original if p.get('name')=='Mage robe'),original[0]['id'])
        await aim_accessory_surface(page,target_id,original)
        fitted=accessory(await read(page))
        assert fitted.get('active') and fitted.get('validPose') and fitted.get('targetId')
        assert await parts(page)==original
        await screenshot_xr(page,'mage-accessory-opposite-hip-preview.png')
        record('Surface fitting positions the new pouch on the opposite hip from the mage’s existing satchel using an actual native surface hit')

        await tap(page,'right','trigger');await finish_accessory(page)
        placed=await parts(page);created=[p for p in placed if p['id'] not in original_ids]
        assert len(created)>=5
        for part in created:topology_valid(part)
        assert [p for p in placed if p['id'] in original_ids]==original
        assert len({p.get('group') for p in created})==1 and created[0].get('group')
        state=await read(page)
        assert state['undoDepth']==depth+1 and state['mode']=='grab'
        assert set(selected_ids(state))=={p['id'] for p in created}
        await screenshot_xr(page,'mage-accessory-opposite-hip-placed.png')
        record('Fresh Trigger creates the full editable pouch group on the reference mage in one Undo step and selects every component for Grab')

        await tap(page,'left','y-button')
        assert await parts(page)==original and (await read(page))['undoDepth']==depth
        await ray_find(page,'exit')
        await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
        assert (await read(page))['nativeParentRestored'] and await parts(page)==original
        assert hashlib.sha256(native_file.read_bytes()).hexdigest()==source_hash
        assert not errors,errors
        record('Undo restores all original mage parts and history exactly; Exit returns the native editor and the private reference file remains unchanged')
        return {'originalPartCount':len(original),'accessoryPartCount':len(created),'deviceProfile':await page.evaluate('()=>window.SWYRL_ENGINE_DEVICE.read().profile'),'modelDataRestored':True,'historyRestored':True,'nativeParentRestored':True,'referenceFileUnchanged':True,'guestOnly':True}
    except Exception as error:
        try:error.accessory_state=await read(page,True)
        except Exception:pass
        try:await page.screenshot(path=str(out/'failure.png'))
        except Exception:pass
        raise
    finally:
        await context.close()


async def workshop_flow(browser,errors,record):
    context,page=await open_model(browser,errors,quest=bool(args.native_project))
    try:
        original=await parts(page);original_ids={p['id'] for p in original}
        await enter(page);await settle_menu(page)
        base=await read(page,True);depth=base['undoDepth']
        assert base['modelRootBorrowed'] and len(base['targetCenters'])==len(original)
        await open_accessory(page)
        start=await read(page)
        assert accessory(start).get('active') and await parts(page)==original
        assert start['undoDepth']==depth
        await screenshot_xr(page,'accessory-workshop-overview.png')
        record('Create opens a live native accessory draft; the assembled pouch preview does not add saved parts or consume Undo')

        await action_ray(page,'accessory-body')
        before=accessory_params(await read(page)).copy()
        for field in ['width','height','depth','rounding','thickness']:
            await action_ray(page,'accessory-'+field+'-plus')
            after=accessory_params(await read(page))
            assert field in after and after[field]!=before[field],('unchanged body parameter',field,before,after)
            before=after.copy()
            assert accessory(await read(page)).get('active') and await parts(page)==original
            assert (await read(page))['undoDepth']==depth
        await screenshot_xr(page,'accessory-body-tools.png')
        record('Body size, depth, rounding and wall thickness controls adjust the live preview through real menu rays without modifying existing geometry')

        await action_ray(page,'accessory-menu')
        await action_ray(page,'accessory-details')
        before=accessory_params(await read(page)).copy()
        for field in ['flap','strap']:
            await action_ray(page,'accessory-'+field+'-plus')
            after=accessory_params(await read(page));assert after.get(field)!=before.get(field),('unchanged detail',field)
            before=after.copy()
        await action_ray(page,'accessory-stitches')
        after=accessory_params(await read(page));assert after.get('stitches')!=before.get('stitches')
        await action_ray(page,'accessory-stitches')
        assert accessory_params(await read(page)).get('stitches')==before.get('stitches')
        await action_ray(page,'accessory-material')
        assert accessory_params(await read(page))!=before
        assert await parts(page)==original and (await read(page))['undoDepth']==depth
        await screenshot_xr(page,'accessory-detail-tools.png')
        record('Flap, strap, stitching and appearance controls remain readable and change only the pending accessory')

        await action_ray(page,'accessory-menu')
        await action_ray(page,'accessory-fit')
        await action_ray(page,'accessory-free')
        await aim(page,[.7,1.2,-1.2])
        pose=accessory(await read(page))
        await axes(page,'right',.6,0,8)
        await axes(page,'right',0,-.6,8)
        await axes(page,'right',0,0,3)
        adjusted=accessory(await read(page))
        assert adjusted.get('rotation')!=pose.get('rotation'),('stick did not turn preview',pose,adjusted)
        assert adjusted.get('scale')!=pose.get('scale'),('stick did not resize preview',pose,adjusted)
        assert await parts(page)==original and (await read(page))['undoDepth']==depth
        record('Right-stick turn and size adjust only the live accessory; returning the stick to neutral leaves source and history unchanged')

        # A menu hit during placement must operate its visible control.
        await action_ray(page,'accessory-menu')
        await action_ray(page,'accessory-fit')
        await action_ray(page,'accessory-surface')
        target_id=original[0]['id']
        if args.native_project:
            target_id=next((p['id'] for p in original if any(word in p.get('name','').lower() for word in ['robe','torso','body'])),target_id)
        await aim_accessory_surface(page,target_id,original)
        fit=accessory(await read(page))
        assert fit.get('active') and await parts(page)==original
        assert fit.get('targetName') or fit.get('targetId'),('surface fit has no native target',fit)
        # Adjusting a visible menu control must not pull the draft behind the
        # panel as the pointer moves off the model and onto that control.
        pose={key:fit.get(key) for key in ['position','rotation','scale']}
        await action_ray(page,'accessory-gap-plus')
        menu_fit=accessory(await read(page))
        assert menu_fit.get('active') and await parts(page)==original
        assert menu_fit.get('targetId')==fit.get('targetId')
        for key in ['rotation','scale']:
            if pose[key] is not None:
                assert distance(pose[key],menu_fit[key])<1e-7,('menu changed draft orientation/size',key,pose,menu_fit)
        # A spacing change may deliberately move the pouch a few millimetres;
        # it must remain next to its fitted surface, never jump to the panel.
        if pose['position'] is not None:
            assert distance(pose['position'],menu_fit['position'])<.08,('menu moved draft away from its fit',pose,menu_fit)
        await aim_accessory_surface(page,target_id,original)
        await screenshot_xr(page,'accessory-surface-fit.png')
        record('Surface fitting resolves a real native mesh target while the existing character/model remains unchanged')

        fitted=accessory(await read(page))
        await action_ray(page,'focus')
        focused=accessory(await read(page))
        assert focused.get('active') and focused.get('validPose'),('Focus lost the fitted preview',focused)
        assert focused.get('targetId')==fitted.get('targetId') and focused.get('fitMode')=='surface'
        assert accessory_params(await read(page))==accessory_params({'accessory':fitted})
        assert await parts(page)==original and (await read(page))['undoDepth']==depth
        await screenshot_xr(page,'accessory-focus-fit.png')
        record('Focus keeps the surface-fitted draft active and reprojects it through the reframed workbench without changing source or history')

        await tap(page,'right','b-button');await finish_accessory(page)
        assert await parts(page)==original and (await read(page))['undoDepth']==depth
        record('B discards the full assembled preview without source writes or Undo changes')

        await open_accessory(page)
        await action_ray(page,'accessory-fit')
        await action_ray(page,'accessory-surface')
        await aim_accessory_surface(page,target_id,original)
        await tap(page,'right','trigger')
        await finish_accessory(page)
        placed=await parts(page);created=[p for p in placed if p['id'] not in original_ids]
        assert len(created)>=5,('accessory is missing native construction components',len(created))
        for part in created:topology_valid(part)
        assert len({p.get('group') for p in created})==1 and created[0].get('group'), 'new accessory components must remain one native group'
        current=await read(page)
        assert current['undoDepth']==depth+1 and current['mode']=='grab'
        assert set(selected_ids(current))=={p['id'] for p in created}
        await screenshot_xr(page,'accessory-native-placed.png')
        record('Confirm commits the complete editable topology component group atomically in one native Undo step and selects it for Grab')

        await aim(page,[1.6,1.5,-1.1]);await button(page,'right','squeeze',True,3);await wait_kind(page,'group')
        await move_hand(page,[.025,.015,0],rotate=[.08,.10,0])
        assert await parts(page)==placed
        await button(page,'right','squeeze',False,3)
        moved=await parts(page);assert moved!=placed and (await read(page))['undoDepth']==depth+2
        await tap(page,'left','y-button');assert await parts(page)==placed
        await tap(page,'left','y-button');assert await parts(page)==original and (await read(page))['undoDepth']==depth
        await chord(page,[['left','x-button'],['left','y-button']]);assert await parts(page)==placed
        await tap(page,'left','y-button');assert await parts(page)==original
        record('The whole bag immediately moves/turns as a selected group; separate Grab and batch-create Undo/Redo restore the exact original model')

        await open_accessory(page)
        await tap(page,'left','y-button');await finish_accessory(page)
        assert await parts(page)==original and (await read(page))['undoDepth']==depth
        record('Undo cancels an unfinished accessory before touching earlier model history')

        await open_accessory(page)
        await page.evaluate('()=>{xrTestDevice.controllers.right.connected=false;}')
        await frames(page,6);await finish_accessory(page)
        assert await parts(page)==original and (await read(page))['undoDepth']==depth
        await page.evaluate('()=>{const c=xrTestDevice.controllers.right;c.setButtonValueImmediate("squeeze",0);c.setButtonValueImmediate("trigger",0);c.setButtonValueImmediate("a-button",0);c.connected=true;}')
        await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().controllers.filter(c=>c.targetTracked&&c.gripTracked).length===2');await frames(page,4)
        record('Tracking loss clears the owned preview and reconnect requires fresh input without persisting partial components')

        if args.record_video:
            await open_accessory(page);await bounded_video(page,'accessory-workshop-interactions.mp4')
            await tap(page,'right','b-button');await finish_accessory(page)
        await ray_find(page,'help');await screenshot_xr(page,'accessory-controller-guide.png');await ray_find(page,'help')
        await ray_find(page,'exit')
        await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
        assert (await read(page))['nativeParentRestored'] and await parts(page)==original
        assert not errors,errors
        record('Guide and Exit remain reachable, preview resources are canceled and the native editor returns with source/history restored')
        return {'originalPartCount':len(original),'accessoryPartCount':len(created),'deviceProfile':await page.evaluate('()=>window.SWYRL_ENGINE_DEVICE.read().profile'),'modelDataRestored':True,'historyRestored':True,'nativeParentRestored':True}
    except Exception as error:
        try:error.accessory_state=await read(page,True)
        except Exception:pass
        try:await page.screenshot(path=str(out/'failure.png'))
        except Exception:pass
        raise
    finally:
        await context.close()


async def main():
    errors=[]
    receipt={'version':'v11.410','testedHtmlSha256':hashlib.sha256(html.read_bytes()).hexdigest(),
             'runtime':'IWER 2.8.0 / Meta Quest 2 / actual XR renderer and native menu input',
             'iwerSha256':IWER_SHA,'physicalHeadsetAcceptance':False,'checks':[],
             'pageErrors':errors,'status':'RUNNING'}
    def record(message):
        receipt['checks'].append(message);(out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print('VR410_CHECK',message,flush=True)
    (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    async with async_playwright() as playwright:
        browser=await playwright.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
        try:
            flow=reference_mage_flow if args.native_project else workshop_flow
            receipt['nativePreview']=await flow(browser,errors,record)
            assert not errors,errors
            receipt['status']='PASS';print('MODEL_VR_V11_410_BROWSER_PASS',json.dumps(receipt),flush=True)
        except Exception as error:
            receipt['status']='FAIL';receipt['failure']=type(error).__name__+': '+str(error)
            if hasattr(error,'accessory_state'):receipt['failureState']=error.accessory_state
            print('MODEL_VR_V11_410_BROWSER_FAIL',json.dumps(receipt),flush=True)
            raise
        finally:
            (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');await browser.close()


asyncio.run(main())


