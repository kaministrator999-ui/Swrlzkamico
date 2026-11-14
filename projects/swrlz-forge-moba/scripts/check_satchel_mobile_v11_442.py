#!/usr/bin/env python3
"""Android touch walkthrough of the native seven-objective satchel lesson.

Run only after sealing, with --expect-sha. The exact HTML is routed unchanged;
packaged assets and pinned Three r169 may be reused in place. All authored
geometry, materials, checks, checkpoints and saves use visible native controls.
Evaluations only read public inspectors or layout. No editor mutation API,
hidden control, injected observer, import fixture or account write is used.
"""
import argparse
import asyncio
import hashlib
import json
import math
import os
import re
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


def arguments():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--html', required=True)
    cli.add_argument('--expect-sha', required=True, help='Exact sealed HTML SHA-256')
    cli.add_argument('--output', default='/workspace/outputs/model-satchel442-mobile')
    cli.add_argument('--assets-root', help='Reuse packaged assets without copying')
    cli.add_argument('--three', help='Local pinned Three r169 ESM')
    cli.add_argument('--chromium', default='/usr/bin/chromium')
    cli.add_argument('--dialog-only', action='store_true', help='Only native dialog/layout smoke')
    cli.add_argument('--desktop', action='store_true', help='Use desktop for a separate dialog smoke')
    return cli.parse_args()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


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


async def project(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_AGENT.inspectScene().project')


async def parts(page):
    return (await project(page))['modelAtelier']['parts']


async def workshop(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect()')


async def camera(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_MODEL_CAMERA.inspect()')


async def vr(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_MODEL_VR.inspect()')


async def lesson(page):
    return await page.evaluate('''()=>({status:window.SWYRL_ENGINE_TUTORIAL_412.status(),
      steps:window.SWYRL_ENGINE_TUTORIAL_412.steps(),academy:window.SWYRL_E_SATCHEL_ACADEMY_416.inspect()})''')


async def history(page):
    state = await vr(page)
    return {'undo': state['undoDepth'], 'redo': state['redoDepth']}


async def visible(locator):
    for i in range(await locator.count()):
        candidate = locator.nth(i)
        if await candidate.is_visible():
            return candidate
    raise AssertionError('No visible native control: ' + str(locator))


async def press(locator):
    candidate = await visible(locator)
    # Locator tap/click scrolls and retries detached async library cards itself.
    # Playwright tap supplies actual touchstart/pointerdown/up/click in the
    # Android profile. Desktop smoke uses click and never authors geometry.
    if await candidate.page.evaluate('()=>navigator.maxTouchPoints>0'):
        await candidate.tap()
    else:
        await candidate.click()


async def cdp_touch(page, cdp, x, y, hold=0, destination=None):
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart',
        'touchPoints': [{'x': x, 'y': y, 'id': 1, 'radiusX': 1, 'radiusY': 1, 'force': 1}]})
    if hold:
        await page.wait_for_timeout(hold)
    if destination:
        for step in range(1, 9):
            fraction = step / 8
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{
                'x': x + (destination[0] - x) * fraction,
                'y': y + (destination[1] - y) * fraction,
                'id': 1, 'radiusX': 1, 'radiusY': 1, 'force': 1}]})
            await page.wait_for_timeout(25)
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    await page.wait_for_timeout(100)


async def number(page, cdp, control, value):
    """Use the existing 380ms mobile hold and actual native number-pad keys."""
    node = await visible(control)
    await node.scroll_into_view_if_needed()
    assert await node.is_enabled()
    if await page.evaluate('()=>matchMedia("(pointer:coarse)").matches'):
        box = await node.bounding_box()
        assert box
        await cdp_touch(page, cdp, box['x'] + box['width']/2, box['y'] + box['height']/2, hold=430)
        pad = page.locator('#seMobileNumberPad')
        await pad.wait_for(state='visible')
        await press(pad.locator('[data-se-clear]'))
        for char in str(value):
            await press(pad.locator('[data-se-digit="' + ('±' if char == '-' else char) + '"]'))
        await press(pad.locator('[data-se-apply]'))
        await pad.wait_for(state='hidden')
    else:
        await node.fill(str(value))
        await node.press('Tab')
    assert math.isclose(float(await node.input_value()), float(value), abs_tol=1e-7)


async def choose_category(page, category, operation=None):
    rail = page.locator('#modelAtelierToolRail')
    if not await rail.is_visible():
        await press(page.get_by_role('button', name='Show inspector', exact=True))
    await press(rail.get_by_role('button', name='Open ' + category + ' editing tools', exact=True))
    if operation:
        current = await page.evaluate('()=>window.SWYRL_E_CONTEXT.current()')
        if current.get('operation') != operation:
            choices = page.locator('#seAtelierModes').get_by_role('button', name=operation, exact=True)
            if not any([await choices.nth(i).is_visible() for i in range(await choices.count())]):
                choices = page.locator('#atelierContextOperations').get_by_role('button', name=operation, exact=True)
            await press(choices)
        await page.wait_for_function('(name)=>window.SWYRL_E_CONTEXT.current().operation===name', arg=operation)
    await page.locator('#atelierContextWorkbench:not([hidden])').wait_for(state='visible')


async def manual(page):
    await choose_category(page, 'Topology', 'Manual mesh modeling')


async def native_action(page, name):
    await press(page.locator('#atelierContextFields').get_by_role('button', name=re.compile(name, re.I)))


async def undo_redo(page, action):
    await choose_category(page, 'Meshes', 'Select & organize')
    await native_action(page, '^' + action + '$')


async def set_operation(page, cdp, operation, amount):
    await manual(page)
    await page.locator('#atelierContextProxy_modelAtelierWorkshopOperation').select_option(operation)
    await number(page, cdp, page.locator('#atelierContextProxy_modelAtelierWorkshopAmount'), amount)


async def open_views(page):
    menu = page.locator('#seAtelierViewMenu')
    settings = page.locator('#se185AtelierTopToggle')
    if await settings.count() and await settings.get_attribute('aria-expanded') == 'false':
        await press(settings)
    for _ in range(8):
        parents = menu.locator('xpath=ancestor::details[not(@open)]')
        if not await parents.count():
            break
        opened = False
        for i in range(await parents.count()):
            summary = parents.nth(i).locator(':scope > summary')
            if await summary.is_visible():
                await press(summary)
                opened = True
                break
        assert opened, 'No visible camera disclosure exposes Views'
    if not await menu.evaluate('(n)=>n.open'):
        await press(menu.locator(':scope > summary'))


async def close_views(page):
    menu = page.locator('#seAtelierViewMenu')
    if await menu.count() and await menu.evaluate('(n)=>n.open'):
        await press(menu.locator(':scope > summary'))
    parents = menu.locator('xpath=ancestor::details[@open]')
    for i in range(await parents.count()):
        summary = parents.nth(i).locator(':scope > summary')
        if await summary.is_visible():
            await press(summary)
    settings = page.locator('#se185AtelierTopToggle')
    if await settings.count() and await settings.get_attribute('aria-expanded') == 'true':
        await press(settings)


async def view_ui(page, direction):
    await open_views(page)
    await press(page.locator('[data-at-view="' + direction + '"]'))
    await page.wait_for_function('(v)=>window.SWYRL_ENGINE_MODEL_CAMERA.inspect().view===v', arg=direction)
    await close_views(page)


async def projection_ui(page, projection):
    await open_views(page)
    await press(page.locator('[data-se430-projection="' + projection + '"]'))
    await page.wait_for_function('(v)=>window.SWYRL_ENGINE_MODEL_CAMERA.inspect().projection===v', arg=projection)
    await close_views(page)


def transform_xyz(point, part):
    x, y, z = [n*s for n, s in zip(point, part['scale'])]
    ax, ay, az = part['rotation']
    x, y = math.cos(az)*x - math.sin(az)*y, math.sin(az)*x + math.cos(az)*y
    x, z = math.cos(ay)*x + math.sin(ay)*z, -math.sin(ay)*x + math.cos(ay)*z
    y, z = math.cos(ax)*y - math.sin(ax)*z, math.sin(ax)*y + math.cos(ax)*z
    return [x + part['position'][0], y + part['position'][1], z + part['position'][2]]


def project_world(point, state):
    matrix = state['matrixWorld']
    delta = [point[k] - matrix[12+k] for k in range(3)]
    local = [sum(delta[k]*matrix[4*j+k] for k in range(3)) for j in range(3)] + [1]
    projection = state['projectionMatrix']
    clip = [sum(projection[4*j+i]*local[j] for j in range(4)) for i in range(4)]
    return [clip[0]/clip[3], clip[1]/clip[3], clip[2]/clip[3]]


async def click_top_face(page, part):
    if await page.locator('#se412Panel').is_visible():
        await press(page.locator('#se442SatchelClose'))
    await view_ui(page, 'top')
    await press(page.get_by_role('button', name='Hide inspector', exact=True))
    await press(page.locator('#modelAtelierFrameSelected'))
    await page.wait_for_timeout(220)
    data = part['topologyMesh']
    top = max(data['positions'][1::3])
    samples = []
    for offset in range(0, len(data['indices']), 3):
        points = [data['positions'][i*3:i*3+3] for i in data['indices'][offset:offset+3]]
        if all(abs(p[1]-top) < 1e-7 for p in points):
            for weights in ((1/3, 1/3, 1/3), (.6,.2,.2), (.2,.6,.2), (.2,.2,.6), (.45,.45,.1), (.45,.1,.45), (.1,.45,.45)):
                samples.append(transform_xyz([sum(p[k]*w for p, w in zip(points, weights)) for k in range(3)], part))
    assert samples
    state = await camera(page)
    ndcs = [project_world(point, state) for point in samples]
    canvas = page.locator('#modelAtelierViewport > canvas')
    rect = await canvas.bounding_box()
    assert rect
    candidates = [[rect['x']+(p[0]+1)*rect['width']/2, rect['y']+(1-p[1])*rect['height']/2]
                  for p in ndcs if all(abs(v)<.99 for v in p[:2])]
    target = await page.evaluate('''(points)=>{
      const controls=[...document.querySelectorAll('#modelAtelierPanel button,#modelAtelierPanel summary,#modelAtelierPanel input,#modelAtelierPanel select')]
        .filter(n=>n.getClientRects().length&&getComputedStyle(n).visibility!=='hidden'&&getComputedStyle(n).pointerEvents!=='none')
        .filter(n=>{const r=n.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return hit===n||n.contains(hit);})
        .map(n=>n.getBoundingClientRect());
      return points.filter(([x,y])=>document.elementFromPoint(x,y)?.tagName==='CANVAS')
        .map(([x,y])=>({x,y,clearance:Math.min(...controls.map(r=>Math.hypot(Math.max(r.left-x,0,x-r.right),Math.max(r.top-y,0,y-r.bottom))))}))
        .sort((a,b)=>b.clearance-a.clearance)[0];}''', candidates)
    assert target and target['clearance'] > 15, ('No unobstructed top-face touch', target)
    await canvas.tap(position={'x': target['x']-rect['x'], 'y': target['y']-rect['y']})
    await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().selection.faceIds.length>0')
    await press(page.get_by_role('button', name='Show inspector', exact=True))


def signed_volume(data):
    total = 0
    for i in range(0, len(data['indices']), 3):
        a, b, c = [data['positions'][v*3:v*3+3] for v in data['indices'][i:i+3]]
        total += (a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    return total


async def select_part(page, part_id):
    await choose_category(page, 'Meshes', 'Select & organize')
    control = await visible(page.locator('#atelierContextProxy_modelAtelierParts'))
    await control.select_option(part_id)
    await page.wait_for_function('(id)=>window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().selection.partId===id', arg=part_id)


async def edit_trs(page, cdp, position=None, scale=None):
    await choose_category(page, 'Meshes', 'Transform')
    for key, values in (('position', position), ('scale', scale)):
        if values is None:
            continue
        for axis, value in enumerate(values):
            control = page.locator('#atelierContextProxy_modelAtelier' + key + str(axis))
            await number(page, cdp, control, value)
    selected = (await workshop(page))['selection']['partId']
    actual = next(p for p in await parts(page) if p['id'] == selected)
    for key, expected in (('position', position), ('scale', scale)):
        if expected is not None:
            assert all(math.isclose(a,b,abs_tol=1e-6) for a,b in zip(actual[key], expected)), (key, actual, expected)


async def add_part(page, cdp, kind, name, position, scale):
    await choose_category(page, 'Meshes', 'Select & organize')
    before = {p['id'] for p in await parts(page)}
    await page.locator('#atelierContextProxy_modelAtelierPrimitiveKind').select_option(kind)
    await native_action(page, '^Add ' + ('cube' if kind == 'box' else kind) + '$')
    added = [p for p in await parts(page) if p['id'] not in before]
    assert len(added) == 1
    part_id = added[0]['id']
    await edit_trs(page, cdp, position=position, scale=scale)
    await choose_category(page, 'Meshes', 'Material & shape')
    control = await visible(page.locator('#atelierContextProxy_modelAtelierName'))
    await control.fill(name)
    await control.press('Tab')
    assert next(p for p in await parts(page) if p['id'] == part_id)['name'] == name
    return part_id


async def paint(page, part_id, material, color):
    await select_part(page, part_id)
    await choose_category(page, 'Meshes', 'Material & shape')
    await (await visible(page.locator('#atelierContextProxy_modelAtelierMaterial'))).select_option(material)
    control = await visible(page.locator('#atelierContextProxy_modelAtelierColor'))
    await control.fill(color)
    # A real user input fill followed by blur invokes the existing proxy's
    # change/input path. No color setter or native paint API is evaluated.
    await control.press('Tab')
    actual = next(p for p in await parts(page) if p['id'] == part_id)
    assert actual['material'] == material and actual['color'].lower() == color, actual


async def open_projects(page):
    studio = page.locator('#se320ModelProjects')
    await press(studio if await studio.is_visible() else page.locator('#projectBtn'))
    await page.locator('#projectHub.show').wait_for(state='visible')


async def expand_lesson(page):
    if await page.locator('#se442SatchelLauncher').is_visible():
        await press(page.locator('#se442SatchelLauncher'))
    panel = page.locator('#se412Panel')
    if 'collapsed' in (await panel.get_attribute('class') or '').split():
        await press(page.locator('#se412Fold'))
    return panel


async def collapse_lesson(page):
    panel = page.locator('#se412Panel')
    if not await panel.is_visible():
        return panel
    if 'collapsed' not in (await panel.get_attribute('class') or '').split():
        await press(page.locator('#se412Fold'))
    return panel


async def choose_step(page, index):
    await expand_lesson(page)
    await press(page.locator('#se412Checks button').nth(index))
    await page.wait_for_function('(i)=>window.SWYRL_ENGINE_TUTORIAL_412.status().current===i', arg=index)


async def show_me(page, index):
    await choose_step(page, index)
    before = await parts(page)
    await press(page.locator('#se416-show'))
    assert await parts(page) == before, 'Show Me must navigate without authoring geometry'
    await collapse_lesson(page)


async def check_step(page, index, success=True):
    await choose_step(page, index)
    # This actual rendered button reaches the tutorial check handler. Never
    # call TUTORIAL.check/mark/applyProgress from an evaluation.
    await press(page.locator('#se412ActionBar .se412-assess'))
    state = await lesson(page)
    assert state['steps'][index]['done'] == success, (index, state, await page.locator('#se412Note').inner_text())
    await collapse_lesson(page)


async def save_local(page):
    button = page.locator('#modelAtelierPanel [data-se371-action="save"]')
    candidates = [button.nth(i) for i in range(await button.count())]
    if not any([await candidate.is_visible() for candidate in candidates]):
        # Save Project normally remains the primary header control. Reveal the
        # native File disclosure only if this build puts Save inside it.
        menu = page.locator('#seAtelierExportMenu')
        if not await menu.evaluate('(n)=>n.open'):
            await press(menu.locator(':scope > summary'))
    await press(button)
    await page.wait_for_function('()=>{const s=window.SWYRL_ENGINE_SAFE_PROJECTS_371.status();return !s.busy&&s.saved&&!!s.id}')
    menu = page.locator('#seAtelierExportMenu')
    if await menu.count() and await menu.evaluate('(n)=>n.open'):
        await press(menu.locator(':scope > summary'))


async def reopen_local(page, lesson_id):
    token = (await vr(page)).get('documentToken')
    await open_projects(page)
    await press(page.locator('#se170-tab-mine'))
    card = page.locator('#se184LocalCards .se184-project-card[data-source="local"][data-project-id="' + lesson_id + '"]')
    await press(card.get_by_role('button', name='Open project', exact=True))
    await page.wait_for_function('''(id)=>window.SWYRL_ENGINE_TUTORIAL_412.status().active&&
        window.SWYRL_ENGINE_TUTORIAL_412.status().projectId===id&&
        !document.querySelector('#projectHub').classList.contains('show')''', arg=lesson_id)
    if token is not None:
        await page.wait_for_function('(token)=>window.SWYRL_ENGINE_MODEL_VR.inspect().documentToken!==token', arg=token)
    return {'beforeDocumentToken': token, 'afterDocumentToken': (await vr(page)).get('documentToken')}


async def dialog_bounds(page):
    return await page.locator('#se412Panel').evaluate('''(p)=>{const r=p.getBoundingClientRect(),h=p.querySelector('header').getBoundingClientRect();
      return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height,
      innerWidth,innerHeight,documentWidth:document.documentElement.scrollWidth,
      header:{left:h.left,top:h.top,right:h.right,bottom:h.bottom,width:h.width,height:h.height},
      role:p.getAttribute('role'),modal:p.getAttribute('aria-modal'),insideScene:!!p.closest('.atelier-scene'),
      fixed:getComputedStyle(p).position==='fixed'};}''')


def assert_clamped(bounds):
    assert bounds['documentWidth'] <= bounds['innerWidth']+2, bounds
    assert bounds['left'] >= -1 and bounds['top'] >= -1, bounds
    assert bounds['right'] <= bounds['innerWidth']+1 and bounds['bottom'] <= bounds['innerHeight']+1, bounds
    assert bounds['width'] >= 200 and bounds['header']['height'] >= 36, bounds


async def dialog_smoke(page, cdp, record, mobile=True):
    panel = await expand_lesson(page)
    await panel.wait_for(state='visible')
    assert await panel.get_attribute('role') == 'dialog'
    assert await panel.get_attribute('aria-modal') == 'false'
    before_parts = await parts(page)
    before_history = await history(page)
    initial = await dialog_bounds(page)
    assert_clamped(initial)
    assert initial['fixed'] and not initial['insideScene'], initial
    header = page.locator('#se412Drag')
    box = await header.bounding_box()
    assert box
    x, y = box['x']+min(80,box['width']/3), box['y']+box['height']/2
    destination = (max(16,x-80), min(initial['innerHeight']-80,y+120))
    if mobile:
        await cdp_touch(page, cdp, x,y, destination=destination)
    else:
        await page.mouse.move(x,y)
        await page.mouse.down()
        await page.mouse.move(*destination, steps=10)
        await page.mouse.up()
    moved = await dialog_bounds(page)
    assert math.hypot(moved['left']-initial['left'],moved['top']-initial['top']) > 20, (initial,moved)
    assert_clamped(moved)
    await collapse_lesson(page)
    collapsed = await dialog_bounds(page)
    assert collapsed['height'] < moved['height']-60, (moved,collapsed)
    assert not await page.locator('#se412Task').is_visible()
    # The real native rail, primitive selector and Add control remain usable
    # while this independent dialog is collapsed.
    await choose_category(page,'Meshes','Select & organize')
    assert await (await visible(page.locator('#atelierContextProxy_modelAtelierPrimitiveKind'))).is_enabled()
    assert await (await visible(page.locator('#atelierContextFields').get_by_role('button',name='Add cube',exact=True))).is_enabled()
    await expand_lesson(page)
    assert await page.locator('#se412Task').is_visible()
    await press(page.locator('#se442SatchelClose'))
    assert not await panel.is_visible()
    overlaps=await page.evaluate('''()=>{
      const r=document.querySelector('#se442SatchelLauncher').getBoundingClientRect();
      return ['#seChatToggle','#se320ModelTransform'].filter(selector=>{
        const n=document.querySelector(selector);if(!n||n.hidden||!n.getClientRects().length)return false;
        const b=n.getBoundingClientRect();return Math.max(r.left,b.left)<Math.min(r.right,b.right)&&Math.max(r.top,b.top)<Math.min(r.bottom,b.bottom);
      });}''')
    assert not overlaps,('Tutorial launcher must clear existing controls',overlaps)
    await press(page.locator('#se442SatchelLauncher'))
    assert await panel.is_visible() and await page.locator('#se412Task').is_visible()
    dialog_status = await page.evaluate('()=>window.SWYRL_E_SATCHEL_DIALOG_442.status()')
    assert dialog_status['parent'] == 'BODY' and dialog_status['active'] and not dialog_status['xr'], dialog_status
    # A separate responsive pass starts from the same live touch page.
    layouts = []
    for width,height in ([(320,700),(844,390),(390,844)] if mobile else [(1280,800),(1440,1000)]):
        await page.set_viewport_size({'width':width,'height':height})
        await page.wait_for_timeout(200)
        layout = await dialog_bounds(page)
        assert_clamped(layout)
        layouts.append(layout)
    reset = page.locator('#se442SatchelReset')
    if not await reset.count():
        reset = panel.get_by_role('button',name=re.compile('Reset.*(?:position|window)|Reset position',re.I))
    await press(reset)
    reset_bounds = await dialog_bounds(page)
    assert_clamped(reset_bounds)
    assert await parts(page) == before_parts and await history(page) == before_history
    await collapse_lesson(page)
    record('Independent nonmodal dialog supports real header touch drag, collapse/reopen, close/launcher reopen, reset and clamping at 320px, 390px and landscape; collapsed lesson leaves native mesh controls usable',
           {'initial':initial,'moved':moved,'collapsed':collapsed,'responsive':layouts,'reset':reset_bounds,'dialogStatus':dialog_status})


async def flow(page, cdp, record, out):
    initial = await parts(page)
    p = await project(page)
    lesson_id = p['instanceId']
    assert p['se412Tutorial'] == 'satchel-001' and p['se441TutorialWorkflow'] == 'one-body-v1', p
    assert len(initial) == 1 and initial[0]['id'] == 'model-seed' and initial[0]['kind'] == 'box'
    assert initial[0]['position'] == [0,1.5,0] and initial[0]['scale'] == [1.4,1,.65], initial
    assert p.get('se371TemplateSource') is not True and lesson_id != p.get('canonicalId')
    await select_part(page,'model-seed')
    await show_me(page,0)
    # One actual transform and its native Undo prove this lesson uses the
    # ordinary source/history path before committing a modeling checkpoint.
    await edit_trs(page,cdp,position=[.05,1.5,0])
    assert await parts(page) != initial
    await undo_redo(page, 'Undo')
    assert await parts(page) == initial
    await check_step(page,0)
    await expand_lesson(page)
    await press(page.locator('#se416-checkpoint'))
    assert (await lesson(page))['academy']['checkpoints'] >= 1
    await collapse_lesson(page)
    await page.screenshot(path=str(out/'01-independent-one-cube.png'))
    record('Projects → Tutorials → Start new creates one independent cube; touch numeric editing and native Undo preserve it; real Check my work and Save checkpoint work')

    await select_part(page,'model-seed')
    await show_me(page,1)
    await manual(page)
    await native_action(page,'^Make mesh editable$')
    converted = await parts(page)
    cube = converted[0]
    assert cube['kind'] == 'topologyMesh' and len(cube['topologyMesh']['positions']) == 24
    await projection_ui(page,'orthographic')
    await click_top_face(page,cube)
    await native_action(page,'^Select flat region$')
    assert len((await workshop(page))['selection']['faceIds']) == 2
    await set_operation(page,cdp,'inset',.2)
    h0 = await history(page)
    await native_action(page,'^Preview geometry$')
    assert (await workshop(page))['preview']['active'] and await parts(page) == converted
    assert await history(page) == h0
    await native_action(page,'^Cancel preview$')
    assert not (await workshop(page))['preview']['active'] and await parts(page) == converted
    await native_action(page,'^Preview geometry$')
    await native_action(page,'^Apply geometry$')
    inset = await parts(page)
    assert len(inset[0]['topologyMesh']['indices']) == 60
    assert len((await workshop(page))['selection']['faceIds']) == 2
    assert (await history(page))['undo'] == h0['undo']+1
    await set_operation(page,cdp,'extrude',-.75)
    h1 = await history(page)
    await native_action(page,'^Preview geometry$')
    assert (await workshop(page))['preview']['active'] and await parts(page) == inset
    assert await history(page) == h1
    await page.screenshot(path=str(out/'02-inward-extrude-preview.png'))
    await native_action(page,'^Apply geometry$')
    cavity = await parts(page)
    mesh = cavity[0]['topologyMesh']
    assert len(mesh['positions']) == 48 and len(mesh['indices']) == 84
    volume = signed_volume(mesh)
    assert 0 < volume < signed_volume(cube['topologyMesh'])-.05, volume
    await undo_redo(page, 'Undo')
    assert await parts(page) == inset
    await undo_redo(page, 'Redo')
    assert await parts(page) == cavity
    await check_step(page,1)
    record('Actual top-face canvas tap, flat-region selection, Inset .20 and Extrude −.75 use native Preview/Cancel/Apply; source remains unchanged before Apply and native Undo/Redo restore exact topology',
           {'vertices':len(mesh['positions'])//3,'triangles':len(mesh['indices'])//3,'signedVolume':volume})

    await show_me(page,2)
    flap_id = await add_part(page,cdp,'box','Satchel flap',[0,1.75,.355],[1.3,.5,.06])
    await check_step(page,2)
    await show_me(page,3)
    strap_ids = []
    for name,position,scale in [('Satchel strap left',[-.66,2.37,0],[.08,.98,.06]),
                                ('Satchel strap right',[.66,2.37,0],[.08,.98,.06]),
                                ('Satchel strap top',[0,2.84,0],[1.32,.08,.06])]:
        strap_ids.append(await add_part(page,cdp,'box',name,position,scale))
    await check_step(page,3)
    await expand_lesson(page)
    await press(page.locator('#se416-checkpoint'))
    assert (await lesson(page))['academy']['checkpoints'] >= 2
    await collapse_lesson(page)
    await show_me(page,4)
    clasp_id = await add_part(page,cdp,'sphere','Satchel clasp',[0,1.68,.465],[.08,.08,.08])
    assert next(p for p in await parts(page) if p['id'] == clasp_id)['material'] != 'metal'
    await check_step(page,4)
    record('Native Add primitive, visible Transform fields and mobile number pad create a thin box flap, three ordinary strap boxes with an empty middle, and small sphere clasp; real stage checks accept their fit')

    await check_step(page,5,success=False)
    await show_me(page,5)
    for part_id in ['model-seed',flap_id]+strap_ids:
        await paint(page,part_id,'matte','#916b48')
    await paint(page,clasp_id,'metal','#c9a56c')
    await check_step(page,5)
    record('Materials stage initially rejects unfinished hardware; native Material and Color fields paint actual leather parts matte brown and actual clasp metal gold, then Check my work passes')

    await show_me(page,6)
    for direction in ['top','front','left','back','right','front']:
        await view_ui(page,direction)
    await projection_ui(page,'perspective')
    final_parts = await parts(page)
    assert len(final_parts) == 6
    assert final_parts[0] == dict(cavity[0],material='matte',color='#916b48')
    await check_step(page,6,success=False)
    await save_local(page)
    first_reopen = await reopen_local(page,lesson_id)
    assert await parts(page) == final_parts
    assert (await lesson(page))['status']['progress'] == 6
    await choose_step(page,6)
    await press(page.locator('#se412Mark'))
    assert (await lesson(page))['status']['progress'] == 7
    await collapse_lesson(page)
    await save_local(page)
    final_reopen = await reopen_local(page,lesson_id)
    reopened_project = await project(page)
    reopened_lesson = await lesson(page)
    assert await parts(page) == final_parts
    assert reopened_project['se412Tutorial'] == 'satchel-001'
    assert reopened_project['se441TutorialWorkflow'] == 'one-body-v1'
    assert reopened_project['se416TutorialState']['done'] == list(range(7))
    assert reopened_lesson['status']['progress'] == 7 and all(s['done'] for s in reopened_lesson['steps'])
    await collapse_lesson(page)
    await page.screenshot(path=str(out/'03-six-parts-seven-objectives-saved.png'))
    record('Native Views inspect all sides; Save Project and visible My Projects card → Open project load the saved document with a changed document token; final deliberate Mark and second save/reopen retain all six editable parts, materials and seven flags',
           {'lessonId':lesson_id,'partsSha256':digest(final_parts),'firstReopen':first_reopen,'finalReopen':final_reopen,
            'completedObjectives':[s['index'] for s in reopened_lesson['steps'] if s['done']]})

    # Reopen the real starter through its visible project card. The pristine
    # blank starter remains the stock sphere, independent of the lesson copy.
    await open_projects(page)
    await press(page.locator('#se170-tab-starter'))
    await press(page.locator('#se236StarterTab-models'))
    await press(page.locator('[data-project-template="blank-model"]'))
    await page.wait_for_function('()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.canonicalId==="blank-model"&&!window.SWYRL_ENGINE_TUTORIAL_412.status().active')
    starter_parts = await parts(page)
    assert len(starter_parts) == 1 and starter_parts[0]['id'] == 'model-seed'
    assert starter_parts[0]['kind'] == 'sphere' and starter_parts[0]['scale'] == [.6,.6,.6]
    assert starter_parts[0]['material'] == 'silk' and starter_parts[0]['color'] == '#ffffff'
    await reopen_local(page,lesson_id)
    assert await parts(page) == final_parts and (await lesson(page))['status']['progress'] == 7
    await collapse_lesson(page)
    record('Visible New Model Project still opens the untouched one-sphere starter; reopening My Projects restores the separately saved six-part satchel and all seven flags',
           {'starterPartsSha256':digest(starter_parts)})
    return {'lessonId':lesson_id,'parts':6,'partsSha256':digest(final_parts),'progressAfterReopen':7,
            'cavityVolume':volume,'nativeStarterUnchanged':True}


async def main():
    args = arguments()
    html = Path(args.html).resolve()
    assert html.is_file(), html
    sha = hashlib.sha256(html.read_bytes()).hexdigest()
    assert re.fullmatch('[0-9a-f]{64}', args.expect_sha) and sha == args.expect_sha, 'Browser input must match the exact sealed HTML'
    assets = Path(args.assets_root).resolve() if args.assets_root else html.parent
    three = Path(args.three).resolve() if args.three else None
    if three:
        assert three.is_file()
        assert "REVISION = '169'" in three.read_text()[:6000], 'Use pinned Three r169'
    out = Path(args.output).resolve()
    out.mkdir(parents=True,exist_ok=True)
    # Chromium profiles/cache use shared memory, not the nearly full overlay.
    os.environ.setdefault('TMPDIR','/dev/shm')
    receipt = {'version':'v11.442','testedHtmlSha256':sha,'htmlBytes':html.stat().st_size,
        'runtime':'Headless Chromium desktop native dialog' if args.desktop else 'Headless Chromium Android 390×844 touch-first native UI',
        'profile':'desktop-dialog-smoke' if args.desktop else 'android-touch',
        'instrumentation':'None: exact sealed HTML; read-only public inspectors and DOM layout reads',
        'physicalDeviceAcceptance':False,'authenticatedAccountSave':'UNTESTED','cloudAccountWrites':False,
        'status':'RUNNING','checks':[],'pageErrors':[]}
    def write():
        (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    def record(message, evidence=None):
        item = {'message':message}
        if evidence is not None:
            item['evidence'] = evidence
        receipt['checks'].append(item)
        write()
        print('SATCHEL442_MOBILE_CHECK',message,flush=True)
    async def transport(route):
        request = route.request
        url = urlsplit(request.url)
        origin = url.scheme+'://'+url.netloc
        if origin == FORGE:
            if url.path in ('/','/index.html','/modeler.html'):
                return await route.fulfill(path=str(html),content_type='text/html')
            asset = (assets/url.path.lstrip('/')).resolve()
            if asset.is_relative_to(assets) and asset.is_file():
                return await route.fulfill(path=str(asset))
            return await route.fulfill(status=404,body='Missing packaged fixture asset')
        if three and request.url == THREE_URL:
            return await route.fulfill(path=str(three),content_type='text/javascript')
        if origin not in (CHAT,CDN):
            return await route.abort('blockedbyclient')
        headers = {k:v for k,v in (await request.all_headers()).items() if k.lower() in {'accept','content-type','origin','referer'}}
        try:
            status,headers,data = await asyncio.to_thread(http,request.url,request.method,headers,request.post_data_buffer)
        except Exception:
            return await route.abort('failed')
        return await route.fulfill(status=status,headers=headers,body=data)
    write()
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=args.chromium,headless=True,
            args=['--no-sandbox','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
        context = await browser.new_context(viewport={'width':1440 if args.desktop else 390,'height':1000 if args.desktop else 844},
            is_mobile=not args.desktop,has_touch=not args.desktop,device_scale_factor=1,accept_downloads=True)
        page = await context.new_page()
        page.set_default_timeout(20000)
        page.on('pageerror',lambda error:receipt['pageErrors'].append(str(error)))
        page.on('dialog',lambda dialog:asyncio.create_task(dialog.accept()))
        for origin in (FORGE,CHAT,CDN):
            await context.route(origin+'/**',transport)
        cdp = await context.new_cdp_session(page)
        try:
            receipt['stage'] = 'Projects → Tutorials → Start new'
            write()
            await page.goto(FORGE+'/modeler.html',wait_until='domcontentloaded',timeout=90000)
            await page.wait_for_function('()=>window.SWRLZ_FORGE_BUILD?.version==="v11.442"&&!!window.SWYRL_ENGINE_MODEL_WORKSHOP&&!!window.SWYRL_ENGINE_MODEL_CAMERA',timeout=90000)
            notes = page.locator('#seReleaseNotesDialog[open]')
            if await notes.count():
                await press(notes.locator('button').last)
            await open_projects(page)
            await press(page.locator('#se412Tab'))
            await press(page.get_by_role('button',name='Start new satchel quest',exact=True))
            await page.wait_for_function('()=>window.SWYRL_ENGINE_TUTORIAL_412.status().active')
            await dialog_smoke(page,cdp,record,mobile=not args.desktop)
            await page.screenshot(path=str(out/'00-dialog-collapsed.png'))
            if not args.dialog_only:
                assert not args.desktop,'Desktop flag is for --dialog-only smoke'
                receipt['stage'] = 'Author satchel through native mobile UI'
                write()
                receipt['flow'] = await flow(page,cdp,record,out)
            assert not receipt['pageErrors'],receipt['pageErrors']
            assert hashlib.sha256(html.read_bytes()).hexdigest() == sha,'Sealed source changed during browser run'
            receipt.update(status='PASS',stage='Complete',layout=await dialog_bounds(page))
            write()
            print(json.dumps({'status':'PASS','sha256':sha,'checks':len(receipt['checks']),'output':str(out)},indent=2),flush=True)
        except Exception as error:
            receipt.update(status='FAIL',error=str(error))
            try:
                receipt['failure'] = {'project':await project(page),'lesson':await lesson(page),
                    'workshop':await workshop(page),'camera':await camera(page),'dialog':await dialog_bounds(page),
                    'context':await page.evaluate('()=>window.SWYRL_E_CONTEXT?.current?.()'),
                    'visibleControls':await page.locator('#atelierContextFields').evaluate('''n=>[...n.querySelectorAll('button,input,select')].filter(e=>e.getClientRects().length).map(e=>({id:e.id,label:e.getAttribute('aria-label'),text:e.textContent.trim().slice(0,90),value:e.value,disabled:e.disabled}))''')}
                await page.screenshot(path=str(out/'failure.png'))
            except Exception as diagnostic_error:
                receipt['diagnosticError'] = str(diagnostic_error)
            write()
            raise
        finally:
            await context.close()
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
