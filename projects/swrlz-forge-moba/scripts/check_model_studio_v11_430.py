#!/usr/bin/env python3
"""Focused real-browser checks for the native beginner modeling workshop.

Imports a disposable public-shape fixture into fresh guest profiles. Operations
use the real rendered viewport and existing contextual inspector. Read-only
public inspectors establish source/history/camera results; they do not execute
the modeling workflow. No account, cloud project or starter asset is changed.
"""
import argparse
import asyncio
import hashlib
import json
import math
import re
import struct
import tempfile
import zlib
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
CLI = argparse.ArgumentParser(description=__doc__)
CLI.add_argument('--html', required=True)
CLI.add_argument('--output')
CLI.add_argument('--chromium', default='/usr/bin/chromium')
CLI.add_argument('--modes', default='desktop,android')
CLI.add_argument('--expect-sha', help='Require the exact sealed artifact digest')
ARGS = CLI.parse_args()
HTML = Path(ARGS.html).resolve()
assert HTML.is_file(), HTML
SHA = hashlib.sha256(HTML.read_bytes()).hexdigest()
if ARGS.expect_sha:
    assert SHA == ARGS.expect_sha, 'The browser fixture must use the sealed HTML'
OUT = Path(ARGS.output or tempfile.mkdtemp(prefix='swrlz-model-studio430-')).resolve()
OUT.mkdir(parents=True, exist_ok=True)
MODES = [value.strip() for value in ARGS.modes.split(',') if value.strip()]
assert MODES and all(value in ('desktop', 'android') for value in MODES)


def fixture():
    public = json.loads((ROOT / 'scenes/model-atelier-prism-jester.swyrl.json').read_text())
    seed = {'id': 'workshop430-seed', 'name': 'Practice sphere', 'kind': 'sphere',
            'position': [0, 1.1, 0], 'rotation': [0, 0, 0], 'scale': [.25, .25, .25],
            'color': '#77c6cf', 'material': 'matte', 'group': 'Practice'}
    public['project'].update(name='Manual modeling practice', projectName='Manual modeling practice',
                             canonicalId='model-workshop430-practice', template='blank-model',
                             se371TemplateSource=True)
    public['project'].pop('instanceId', None)
    public['project']['modelAtelier'] = {'schema': 'swyrl-model-atelier-v1',
        'name': 'Manual modeling practice', 'parts': [seed]}
    public['editor'] = {'studioWorkspace': 'modeler'}
    public['scene'] = {'background': '#141425', 'paths': {}, 'actors': []}
    return public


FIXTURE = OUT / 'manual-modeling-practice.swyrl.json'
FIXTURE.write_text(json.dumps(fixture(), indent=2))
FIXTURE_SHA = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
# A tiny controlled local image exercises the real portable-reference import.
# It contains no user project/image data and adds no dependency or network asset.
def png_chunk(kind, content):
    return struct.pack('>I', len(content))+kind+content+struct.pack('>I', zlib.crc32(kind+content)&0xffffffff)


REFERENCE = OUT / 'reference-square.png'
pixels=b''.join(b'\0'+b''.join(bytes((80,190,165,255) if (x//4+y//4)%2 else (30,50,75,255))
                              for x in range(16)) for y in range(16))
REFERENCE.write_bytes(b'\x89PNG\r\n\x1a\n'+png_chunk(b'IHDR',struct.pack('>IIBBBBB',16,16,8,6,0,0,0))+
                      png_chunk(b'IDAT',zlib.compress(pixels))+png_chunk(b'IEND',b''))


def request_http(url, method, headers, body):
    try:
        response = urlopen(Request(url, data=body, headers=headers, method=method), timeout=25)
    except HTTPError as error:
        response = error
    with response:
        content = response.readline(262144) if urlsplit(url).path == '/api/lalm_station/stream' else response.read()
        allowed = {'content-type', 'content-security-policy', 'access-control-allow-origin',
                   'access-control-allow-credentials', 'cache-control'}
        return response.status, {k: v for k, v in response.headers.items() if k.lower() in allowed}, content


async def transport(route):
    request = route.request
    url = urlsplit(request.url)
    origin = url.scheme + '://' + url.netloc
    if origin == FORGE:
        if url.path in ('/', '/index.html', '/modeler.html'):
            return await route.fulfill(path=str(HTML), content_type='text/html')
        asset = (HTML.parent / url.path.lstrip('/')).resolve()
        if asset.is_relative_to(HTML.parent) and asset.is_file():
            return await route.fulfill(path=str(asset))
        return await route.fulfill(status=404, body='Missing packaged fixture asset')
    if origin not in (CHAT, CDN):
        return await route.abort('blockedbyclient')
    allowed = {'accept', 'content-type', 'origin', 'referer'}
    headers = {k: v for k, v in (await request.all_headers()).items() if k.lower() in allowed}
    try:
        code, headers, body = await asyncio.to_thread(request_http, request.url, request.method,
                                                     headers, request.post_data_buffer)
    except Exception:
        return await route.abort('failed')
    return await route.fulfill(status=code, headers=headers, body=body)


async def source(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier')


async def workshop(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect()')


async def camera(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_MODEL_CAMERA.inspect()')


async def history(page):
    return await page.evaluate('''()=>{const s=window.SWYRL_ENGINE_MODEL_VR.inspect();
      return {undo:s.undoDepth,redo:s.redoDepth};}''')


async def first_visible(locator):
    for index in range(await locator.count()):
        candidate = locator.nth(index)
        if await candidate.is_visible():
            return candidate
    raise AssertionError('No visible element: ' + str(locator))


async def click_visible(locator):
    candidate = await first_visible(locator)
    await candidate.scroll_into_view_if_needed()
    await candidate.click()


async def choose_category(page, category, operation=None):
    rail = page.locator('#modelAtelierToolRail')
    if not await rail.is_visible():
        await click_visible(page.locator('#modelAtelierMeshToolsOpen'))
    await click_visible(rail.get_by_role('button', name='Open '+category+' editing tools', exact=True))
    if operation:
        # Selecting a category already selects its first operation. A single
        # mode may have no separate visible mode button, so do not require a
        # second click when the real UI has already reached the requested tool.
        current = await page.evaluate('()=>window.SWYRL_E_CONTEXT.current()')
        if current.get('operation') != operation:
            choices = page.locator('#seAtelierModes').get_by_role('button', name=operation, exact=True)
            if not any([await choices.nth(i).is_visible() for i in range(await choices.count())]):
                choices = page.locator('#atelierContextOperations').get_by_role('button', name=operation, exact=True)
            await click_visible(choices)
        await page.wait_for_function('(name)=>window.SWYRL_E_CONTEXT.current().operation===name',arg=operation)
    await page.wait_for_function('()=>!!document.querySelector("#atelierContextWorkbench:not([hidden])")')


async def manual(page):
    await choose_category(page, 'Topology', 'Manual mesh modeling')
    await page.locator('#atelierContextProxy_modelAtelierWorkshopOperation').wait_for(state='visible')


async def native_action(page, name):
    await click_visible(page.locator('#atelierContextFields').get_by_role('button', name=re.compile(name, re.I)))


async def set_operation(page, operation, amount=None):
    await manual(page)
    await page.locator('#atelierContextProxy_modelAtelierWorkshopOperation').select_option(operation)
    if amount is not None:
        control = page.locator('#atelierContextProxy_modelAtelierWorkshopAmount')
        await control.fill(str(amount))
        await control.dispatch_event('change')


async def projection_ui(page, projection):
    node = page.locator('[data-se430-projection="'+projection+'"]')
    if not any([await node.nth(i).is_visible() for i in range(await node.count())]):
        await open_views(page)
    await click_visible(node)
    await page.wait_for_function('(p)=>window.SWYRL_ENGINE_MODEL_CAMERA.inspect().projection===p', arg=projection)


async def frame_ui(page, scope='all'):
    node = page.locator('[data-se430-frame="'+scope+'"]')
    if not any([await node.nth(i).is_visible() for i in range(await node.count())]):
        await open_views(page)
    await click_visible(node)


async def open_views(page):
    menu=page.locator('#seAtelierViewMenu')
    # The existing Settings button collapses the entire display/camera bar by
    # default on phones. Reveal it through its actual header control first.
    settings=page.locator('#se185AtelierTopToggle')
    if await settings.count() and await settings.get_attribute('aria-expanded')=='false':
        await click_visible(settings)
    # Also support a native disclosure ancestor if a responsive layout nests
    # the bar. Only visible summaries are clicked; hidden controls are never
    # forced or opened through a DOM setter.
    for _ in range(8):
        parents=menu.locator('xpath=ancestor::details[not(@open)]')
        if not await parents.count():
            break
        opened=False
        for i in range(await parents.count()):
            summary=parents.nth(i).locator(':scope > summary')
            if await summary.is_visible():
                await click_visible(summary)
                opened=True
                break
        assert opened, 'No visible native camera-window disclosure can reveal Views'
    if await menu.count() and not await menu.evaluate('(n)=>n.open'):
        await click_visible(menu.locator(':scope > summary'))


async def close_views(page):
    menu=page.locator('#seAtelierViewMenu')
    if await menu.count() and await menu.evaluate('(n)=>n.open'):
        await click_visible(menu.locator(':scope > summary'))
    # Dismiss the camera window before picking actual geometry beneath it.
    # There is no geometry selection through an opaque menu in this test.
    parents=menu.locator('xpath=ancestor::details[@open]')
    for i in range(await parents.count()):
        summary=parents.nth(i).locator(':scope > summary')
        if await summary.is_visible():
            await click_visible(summary)
    if await page.evaluate('()=>matchMedia("(max-width:700px), (pointer:coarse)").matches'):
        settings=page.locator('#se185AtelierTopToggle')
        if await settings.count() and await settings.get_attribute('aria-expanded')=='true':
            await click_visible(settings)


async def view_ui(page, direction):
    # The compact axis widget naturally occludes its opposite axis when viewed
    # exactly along it. The existing Views disclosure always exposes all six.
    await open_views(page)
    await click_visible(page.locator('[data-at-view="'+direction+'"]'))
    await page.wait_for_function('(v)=>window.SWYRL_ENGINE_MODEL_CAMERA.inspect().view===v', arg=direction)
    await close_views(page)


def transform_xyz(point, part):
    x, y, z = [n*s for n, s in zip(point, part['scale'])]
    ax, ay, az = part['rotation']
    # THREE Euler XYZ => quaternion/matrix Rz applied first, then Ry, then Rx.
    x, y = math.cos(az)*x-math.sin(az)*y, math.sin(az)*x+math.cos(az)*y
    x, z = math.cos(ay)*x+math.sin(ay)*z, -math.sin(ay)*x+math.cos(ay)*z
    y, z = math.cos(ax)*y-math.sin(ax)*z, math.sin(ax)*y+math.cos(ax)*z
    return [x+part['position'][0], y+part['position'][1], z+part['position'][2]]


def project_world(point, state):
    matrix = state['matrixWorld']
    delta = [point[k]-matrix[12+k] for k in range(3)]
    local = [sum(delta[k]*matrix[4*j+k] for k in range(3)) for j in range(3)] + [1]
    projection = state['projectionMatrix']
    clip = [sum(projection[4*j+i]*local[j] for j in range(4)) for i in range(4)]
    return [clip[0]/clip[3], clip[1]/clip[3], clip[2]/clip[3]]


async def click_top_face(page, part):
    await view_ui(page, 'top')
    mobile=await page.evaluate('()=>navigator.maxTouchPoints>0')
    if mobile:
        # The existing focus-workspace control gives direct touch modeling
        # the full canvas; restore the inspector after the real face pick.
        await click_visible(page.get_by_role('button',name='Hide inspector',exact=True))
        await click_visible(page.locator('#modelAtelierFrameSelected'))
    # Settings changes resize the actual phone surface. Derive the touch
    # target only after the native ResizeObserver has settled.
    await page.wait_for_timeout(180)
    data = part['topologyMesh']
    samples=[]
    top=max(data['positions'][1::3])
    for offset in range(0,len(data['indices']),3):
        points=[data['positions'][index*3:index*3+3] for index in data['indices'][offset:offset+3]]
        if all(abs(point[1]-top)<1e-7 for point in points):
            for weights in ((1/3,1/3,1/3),(.6,.2,.2),(.2,.6,.2),(.2,.2,.6),(.45,.45,.1),(.45,.1,.45),(.1,.45,.45)):
                samples.append(transform_xyz([sum(p[k]*w for p,w in zip(points,weights)) for k in range(3)],part))
    assert samples, 'Fixture has no top face'
    state=await camera(page)
    ndcs=[project_world(point,state) for point in samples]
    canvas=page.locator('#modelAtelierViewport > canvas')
    rect=await canvas.bounding_box()
    assert rect
    candidates=[[rect['x']+(p[0]+1)*rect['width']/2,rect['y']+(1-p[1])*rect['height']/2] for p in ndcs if all(abs(v)<.99 for v in p[:2])]
    # Chromium expands nearby touch targets. Prefer an interior face point
    # clear of real floating controls instead of tapping just below a toolbar.
    target=await page.evaluate('''(points)=>{
      const controls=[...document.querySelectorAll('#modelAtelierPanel button,#modelAtelierPanel summary,#modelAtelierPanel input,#modelAtelierPanel select,#se320ModelTransform')]
        .filter(n=>n.getClientRects().length&&getComputedStyle(n).visibility!=='hidden')
        .map(n=>n.getBoundingClientRect());
      return points.filter(([x,y])=>document.elementFromPoint(x,y)?.tagName==='CANVAS')
        .map(([x,y])=>({x,y,clearance:Math.min(...controls.map(r=>Math.hypot(Math.max(r.left-x,0,x-r.right),Math.max(r.top-y,0,y-r.bottom))))}))
        .sort((a,b)=>b.clearance-a.clearance)[0];
    }''',candidates)
    assert target and target['clearance']>15, ('No unobstructed interior face target',target)
    x,y=target['x'],target['y']
    if await page.evaluate('()=>navigator.maxTouchPoints>0'):
        await canvas.tap(position={'x':x-rect['x'],'y':y-rect['y']})
    else:
        await page.mouse.click(x,y)
    await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().selection.faceIds.length>0',timeout=5000)
    if mobile:
        await click_visible(page.get_by_role('button',name='Show inspector',exact=True))



def signed_volume(data):
    total = 0
    for i in range(0, len(data['indices']), 3):
        a, b, c = [data['positions'][v*3:v*3+3] for v in data['indices'][i:i+3]]
        total += (a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    return total


async def undo_redo(page, action):
    await choose_category(page, 'Meshes', 'Select & organize')
    await native_action(page, '^Run.*'+action+'$|^'+action+'$')


async def export_json(page, directory):
    button = page.locator('#modelAtelierExport')
    if not await button.is_visible():
        details = page.locator('#seAtelierExportMenu')
        await details.locator('summary').click()
    async with page.expect_download() as download:
        await click_visible(button)
    result = await download.value
    destination = directory / 'native-container.model.json'
    await result.save_as(destination)
    return destination, json.loads(destination.read_text())


async def check_mode(browser, mode):
    directory = OUT / mode
    directory.mkdir(exist_ok=True)
    mobile = mode == 'android'
    context = await browser.new_context(viewport={'width':390 if mobile else 1440,'height':844 if mobile else 1000},
        is_mobile=mobile, has_touch=mobile, device_scale_factor=1, accept_downloads=True)
    for origin in (FORGE, CHAT, CDN):
        await context.route(origin+'/**', transport)
    page = await context.new_page()
    page.set_default_timeout(30000)
    errors, checks = [], []
    def page_error(error):
        errors.append(str(error))
        print(mode.upper()+' PAGE_ERROR '+str(error), flush=True)
    page.on('pageerror', page_error)
    async def accept_dialog(dialog):
        await dialog.accept('Manual container copy' if dialog.type == 'prompt' else None)
    page.on('dialog', lambda dialog: asyncio.create_task(accept_dialog(dialog)))
    def passed(text):
        checks.append(text)
        (directory/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
        print(mode.upper()+' PASS '+str(len(checks))+': '+text, flush=True)
    result = {'mode':mode,'testedHtmlSha256':SHA,'checks':checks,'pageErrors':errors,'status':'RUNNING'}
    def stage(text):
        result['stage']=text
        (directory/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
        print(mode.upper()+' STAGE '+text, flush=True)
    try:
        stage('Load assembled editor')
        await page.goto(FORGE+'/modeler.html', wait_until='domcontentloaded', timeout=90000)
        await page.wait_for_function('()=>window.SWRLZ_FORGE_BUILD?.version==="v11.430"&&!!window.SWYRL_ENGINE_MODEL_WORKSHOP&&!!window.SWYRL_ENGINE_MODEL_CAMERA', timeout=90000)
        stage('Import disposable practice project')
        notes=page.locator('#seReleaseNotesDialog[open]')
        if await notes.count():
            await notes.locator('button').last.click()
        await page.locator('#fileInput').set_input_files(str(FIXTURE))
        await page.wait_for_function('()=>window.SWYRL_ENGINE_AGENT.inspectScene().project?.modelAtelier?.parts?.[0]?.id==="workshop430-seed"')
        await page.locator('#modelAtelierPanel:not([hidden])').wait_for()
        stage('Choose primitive through the existing contextual inspector')
        await choose_category(page, 'Meshes', 'Select & organize')
        await page.locator('#atelierContextProxy_modelAtelierParts').select_option('workshop430-seed')
        initial_source=await source(page)
        kind=page.locator('#atelierContextProxy_modelAtelierPrimitiveKind')
        await kind.select_option('box')
        await native_action(page, 'Add cube')
        await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().selection.name==="Cube"')
        cube_id=(await workshop(page))['selection']['partId']
        assert len((await source(page))['parts'])==2
        assert next(p for p in (await source(page))['parts'] if p['id']=='workshop430-seed')==initial_source['parts'][0]
        await manual(page)
        blocked=await workshop(page)
        assert not blocked['operations']['inset']['available'] and blocked['operations']['inset']['reason']
        await page.screenshot(path=str(directory/'01-overview.png'))
        passed('A real native Cube is created through the existing Add control; contextual face tools explain the conversion prerequisite')

        stage('Convert and select a real viewport face')
        await native_action(page, 'Make mesh editable')
        await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().convert.available&&window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().selection.mode==="face"')
        converted=await source(page)
        cube=next(part for part in converted['parts'] if part['id']==cube_id)
        assert cube['kind']=='topologyMesh' and len(cube['topologyMesh']['positions'])==24
        await projection_ui(page, 'orthographic')
        await click_top_face(page, cube)
        await native_action(page, 'Select flat region')
        assert len((await workshop(page))['selection']['faceIds'])==2
        passed('Exact editable conversion preserves the cube surface; a real viewport face pick expands to its connected coplanar region')

        stage('Inset preview, cancel and apply')
        baseline=await source(page)
        before_history=await history(page)
        await set_operation(page, 'inset', .2)
        await native_action(page, 'Preview geometry')
        assert (await workshop(page))['preview']['active'] and (await source(page))==baseline
        assert (await history(page))==before_history
        await page.screenshot(path=str(directory/'02-inset-preview.png'))
        await native_action(page, 'Cancel preview')
        assert not (await workshop(page))['preview']['active'] and (await source(page))==baseline
        assert (await history(page))==before_history
        await native_action(page, 'Preview geometry')
        await native_action(page, 'Apply geometry')
        inset=await source(page)
        assert (await history(page))['undo']==before_history['undo']+1
        assert len((await workshop(page))['selection']['faceIds'])==2
        inset_cube=next(part for part in inset['parts'] if part['id']==cube_id)
        assert len(inset_cube['topologyMesh']['indices'])==60
        passed('Inset previews actual geometry without source/history writes; Cancel restores it and Apply commits one Undo step with only the inner region selected')

        stage('Connected inward extrusion')
        await set_operation(page, 'extrude', -.35)
        inset_history=await history(page)
        await native_action(page, 'Preview geometry')
        assert (await source(page))==inset and (await history(page))==inset_history
        await native_action(page, 'Apply geometry')
        cavity=await source(page)
        cavity_cube=next(part for part in cavity['parts'] if part['id']==cube_id)
        assert len(cavity_cube['topologyMesh']['indices'])==84
        volume=signed_volume(cavity_cube['topologyMesh'])
        assert .01<volume<signed_volume(cube['topologyMesh'])-.05,volume
        await page.screenshot(path=str(directory/'03-manual-container.png'))
        passed('Negative connected-region Extrude forms real cavity walls and a retained floor; source topology and signed volume change')

        stage('Native Undo and Redo')
        await undo_redo(page,'Undo')
        assert (await source(page))['parts']==inset['parts']
        await undo_redo(page,'Undo')
        assert (await source(page))['parts']==converted['parts']
        await undo_redo(page,'Redo')
        assert (await source(page))['parts']==inset['parts']
        await undo_redo(page,'Redo')
        assert (await source(page))['parts']==cavity['parts']
        passed('Two native Undo and Redo steps restore the exact converted, inset and cavity meshes')

        stage('Exact camera views and projection controls')
        model_before=await source(page)
        history_before=await history(page)
        expected={'front':[0,0,-1],'back':[0,0,1],'left':[1,0,0],'right':[-1,0,0],'top':[0,-1,0],'bottom':[0,1,0]}
        for direction,wanted in expected.items():
            await view_ui(page,direction)
            view=await camera(page)
            assert view['projection']=='orthographic' and view['cameraType']=='OrthographicCamera'
            assert sum((x-y)**2 for x,y in zip(view['direction'],wanted))<1e-10,(direction,view)
        await frame_ui(page,'all')
        await projection_ui(page,'perspective')
        await close_views(page)
        assert (await camera(page))['cameraType']=='PerspectiveCamera'
        assert (await source(page))==model_before and (await history(page))==history_before
        passed('All six camera views use exact axes in a real OrthographicCamera; Frame all and Perspective do not modify geometry/history')

        stage('Contextual requirements and optional animated teaching')
        await manual(page)
        await click_visible(page.locator('[data-component-mode="vertex"]'))
        await set_operation(page,'inset',.2)
        state=await workshop(page)
        assert not state['operations']['inset']['available'] and state['operations']['inset']['reason']
        preview=page.locator('#atelierContextFields').get_by_role('button',name=re.compile('Preview geometry',re.I))
        assert await (await first_visible(preview)).is_disabled()
        await click_visible(page.locator('[data-component-mode="face"]'))
        teaching=page.locator('#se430ToolHelp')
        if not await teaching.evaluate('(n)=>n.open'):
            await teaching.locator('summary').click()
        assert await teaching.locator('canvas').is_visible()
        assert await page.locator('#modelAtelierPanel svg.se430-icon').count()>0
        await teaching.locator('canvas').scroll_into_view_if_needed()
        first_frame=await teaching.locator('canvas').evaluate('(n)=>n.toDataURL()')
        await page.wait_for_function('(previous)=>document.querySelector("#se430ToolDemo").toDataURL()!==previous',arg=first_frame,timeout=5000)
        await page.locator('#se430StudyTool').select_option('bevel')
        assert 'not implemented' in (await page.locator('#se430HelpLimitation').inner_text()).lower()
        assert (await page.locator('#atelierContextProxy_modelAtelierWorkshopOperation').input_value())=='inset'
        assert (await source(page))['parts']==cavity['parts']
        await page.screenshot(path=str(directory/'04-contextual-teaching.png'))
        await teaching.locator('summary').click()
        assert not await teaching.locator('canvas').is_visible()
        passed('Component modes drive valid/invalid actions and reasons; optional animated help illustrates tools and truthfully labels incomplete Bevel without applying a fake operation')

        stage('Persistent assembly and selection framing through existing tools')
        await click_visible(page.locator('[data-component-mode="mesh"]'))
        await choose_category(page,'Meshes','Assemblies & selection')
        await native_action(page,'Select 32')
        assert (await workshop(page))['selection']['objectCount']==2
        await native_action(page,'Group selected')
        grouped=await source(page)
        groups=grouped.get('meshGroups',[])
        assert len(groups)==1 and set(groups[0]['members'])=={p['id'] for p in cavity['parts']}
        assert grouped['parts']==cavity['parts']
        await frame_ui(page,'selected')
        assert len((await camera(page))['selectedIds'])==2
        assert (await source(page))==grouped
        passed('The organized assembly controls create a real persistent group without changing its meshes or materials; Frame selection includes both objects')

        stage('Portable reference import and camera matching')
        await close_views(page)
        before_reference_parts=(await source(page))['parts']
        await page.locator('#modelAtelierReferenceFile').set_input_files(str(REFERENCE))
        await page.wait_for_function('()=>window.SWYRL_ENGINE_REFERENCE.status().count===1')
        await click_visible(page.locator('#modelAtelierReferenceAngle'))
        await page.locator('#modelAtelierReferenceAngle').select_option('top')
        await click_visible(page.locator('#modelAtelierReferenceCamera'))
        assert (await camera(page))['view']=='top'
        assert (await source(page))['parts']==before_reference_parts
        references=(await source(page))['references']
        assert len(references)==1 and references[0]['angle']=='top' and references[0]['data'].startswith('data:image/')
        await click_visible(page.locator('#modelAtelierReferenceClose'))
        passed('A local image imports through the existing portable reference studio; its Top camera match uses the improved exact view without editing model geometry')

        stage('Native export, import, reopen and starter-safe saving')
        exported_file,exported=await export_json(page,directory)
        exported_model=exported.get('model',exported.get('project',{}).get('modelAtelier'))
        assert exported_model and exported_model['parts']==cavity['parts']
        assert exported_model.get('meshGroups')==groups
        assert exported_model.get('references')==references
        await page.locator('#modelAtelierImportFile').set_input_files(str(exported_file))
        await page.wait_for_function('(n)=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.length===n',arg=len(cavity['parts']))
        assert (await source(page))['parts']==cavity['parts']
        assert (await source(page)).get('meshGroups')==groups
        assert (await source(page)).get('references')==references
        await click_visible(page.locator('#modelAtelierClose'))
        # Close returns to the Game Engine workspace. The historical Reopen
        # button belongs to a hidden older toolbar; use the visible native
        # Modeling workspace tab, which reopens this same model document.
        await click_visible(page.locator('[data-se187-tab="modeler"]'))
        await page.locator('#modelAtelierPanel:not([hidden])').wait_for()
        assert (await source(page))['parts']==cavity['parts']
        assert (await source(page)).get('meshGroups')==groups
        assert (await source(page)).get('references')==references
        passed('Native JSON export/import and closing/reopening the existing studio preserve edited topology, UVs, material descriptors, references and the persistent assembly')

        await click_visible(page.locator('#modelAtelierPanel [data-se371-action="save"]'))
        await page.wait_for_function('()=>{const s=window.SWYRL_ENGINE_SAFE_PROJECTS_371.status();return !s.busy&&s.saved&&!!s.id}',timeout=30000)
        saved=await page.evaluate('()=>window.SWYRL_ENGINE_SAFE_PROJECTS_371.status()')
        assert saved['id']!='model-workshop430-practice'
        assert (await source(page))['parts']==cavity['parts']
        await click_visible(page.locator('#modelAtelierClose'))
        await click_visible(page.locator('[data-se187-tab="modeler"]'))
        await page.locator('#modelAtelierPanel:not([hidden])').wait_for()
        reopened=await page.evaluate('()=>window.SWYRL_ENGINE_SAFE_PROJECTS_371.status()')
        assert reopened['saved'] and reopened['id']==saved['id']
        await click_visible(page.locator('#modelAtelierPanel [data-se371-action="save"]'))
        await page.wait_for_function('(id)=>{const s=window.SWYRL_ENGINE_SAFE_PROJECTS_371.status();return !s.busy&&s.saved&&s.id===id}',arg=saved['id'])
        notice=await page.locator('#se371ProjectNotice').text_content()
        assert notice and notice.startswith('Saved '),notice
        assert (await source(page))['parts']==cavity['parts']
        assert hashlib.sha256(FIXTURE.read_bytes()).hexdigest()==FIXTURE_SHA
        passed('Save Project clones starter-derived practice into an independent local identity; reopening and saving again retain that identity, the authored mesh and the unchanged original fixture')

        layout=await page.evaluate('''()=>{const p=document.querySelector('#modelAtelierPanel'),v=document.querySelector('#modelAtelierViewport > canvas'),r=v.getBoundingClientRect();return {innerWidth,documentWidth:document.documentElement.scrollWidth,panelWidth:p.clientWidth,panelScrollWidth:p.scrollWidth,viewport:{width:r.width,height:r.height}}}''')
        assert layout['documentWidth']<=layout['innerWidth']+2,layout
        assert layout['panelScrollWidth']<=layout['panelWidth']+2,layout
        assert layout['viewport']['width']>=200 and layout['viewport']['height']>=180,layout
        assert not errors,errors
        result.update(status='PASS',layout=layout,modelParts=len(cavity['parts']),cavityVolume=volume,savedIdentity=saved['id'])
        await page.screenshot(path=str(directory/'05-finished-layout.png'))
        passed('The assembled studio fits the viewport with readable touch controls and no horizontal overflow or page errors')
    except Exception as error:
        result.update(status='FAIL',error=str(error))
        try:
            result['workshop']=await workshop(page)
            result['camera']=await camera(page)
            result['safeProjectStatus']=await page.evaluate('''()=>({
              state:window.SWYRL_ENGINE_SAFE_PROJECTS_371?.status?.(),
              notice:document.querySelector('#se371ProjectNotice')?.textContent,
              project:window.SWYRL_ENGINE_AGENT?.inspectScene?.().project
            })''')
            result['navigation']=await page.evaluate('''()=>({
              current:window.SWYRL_E_CONTEXT?.current?.(),groups:window.SWYRL_E_CONTEXT?.groups?.(),
              modes:[...document.querySelectorAll('#seAtelierModes button,#atelierContextOperations button')].map(n=>({
                text:n.textContent.trim(),label:n.getAttribute('aria-label'),visible:!!(n.getBoundingClientRect().width&&n.getBoundingClientRect().height)
              }))
            })''')
            await page.screenshot(path=str(directory/'failure.png'))
        except Exception:
            pass
        raise
    finally:
        (directory/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
        await context.close()
    return result


async def main():
    async with async_playwright() as playwright:
        browser=await playwright.chromium.launch(executable_path=ARGS.chromium,headless=True,
            args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
        try:
            results=[]
            for mode in MODES:
                results.append(await check_mode(browser,mode))
            result={'version':'v11.430','status':'PASS','testedHtmlSha256':SHA,
                'runtime':'Chromium / actual native Model Studio / desktop and Android touch profiles',
                'physicalHeadsetAcceptance':False,'cloudAccountWrites':False,'results':results}
            (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps({'status':'PASS','sha256':SHA,'checks':sum(len(r['checks']) for r in results),'modes':MODES,'output':str(OUT)},indent=2),flush=True)
        finally:
            await browser.close()


if __name__=='__main__':
    asyncio.run(main())
