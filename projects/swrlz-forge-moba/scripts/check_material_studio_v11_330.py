#!/usr/bin/env python3
"""Exercise Material Studio through native controls on desktop and phone layouts.

Uses fresh isolated profiles and a local sealed package at the canonical app
origin. Public CDN and guest Chat requests retain verified TLS; no account,
private project, or saved browser profile is reused. Requires Playwright/Chromium.
"""
import argparse
import asyncio
import json
import hashlib
import struct
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from playwright.async_api import async_playwright

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument('--html', required=True)
cli.add_argument('--output')
cli.add_argument('--chromium', default='/usr/bin/chromium')
args = cli.parse_args()
html = Path(args.html).resolve()
assert html.is_file(), html
out = Path(args.output or tempfile.mkdtemp(prefix='swrlz-material330-')).resolve()
out.mkdir(parents=True, exist_ok=True)
FORGE = 'https://kamiloki-swrlz-forge-moba.static.hf.space'
CHAT = 'https://kamiloki-swyrlz.hf.space'
CDN = 'https://cdn.jsdelivr.net'


def http(url, method, headers, body):
    try:
        response = urlopen(Request(url, data=body, headers=headers, method=method), timeout=25)
    except HTTPError as error:
        response = error
    with response:
        # Guest status streams need their initial event only; never wait on an
        # unrelated long-lived network stream while checking the local editor.
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
        status, response_headers, data = await asyncio.to_thread(
            http, request.url, request.method, headers, request.post_data_buffer)
    except Exception:
        return await route.abort('failed')
    return await route.fulfill(status=status, headers=response_headers, body=data)


async def prepare(page, selector):
    print('MATERIAL_CONTROL', selector, flush=True)
    control = page.locator(selector)
    assert await control.count() == 1, (selector, await control.count())
    # Library transfer actions live in a native disclosure. Open its summary
    # through the actual user action before checking/clicking the command.
    closed = control.locator('xpath=ancestor::details[not(@open)]')
    while await closed.count():
        summary = closed.first.locator(':scope > summary')
        await summary.scroll_into_view_if_needed()
        await summary.click()
    await control.scroll_into_view_if_needed()
    assert await control.is_visible(), selector
    assert await control.is_enabled(), selector
    # Geometry alone misses panels that render underneath another layer.
    assert await control.evaluate('''element => {
      const r=element.getBoundingClientRect(),hit=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
      return hit===element || element.contains(hit);
    }'''), 'Control is covered: ' + selector
    return control


async def click(page, selector):
    await (await prepare(page, selector)).click()


async def pane(page, name):
    tab = page.locator(f'#se330MaterialTabs [data-se330-pane="{name}"]')
    if await tab.is_visible():
        await click(page, f'#se330MaterialTabs [data-se330-pane="{name}"]')


async def edit(page, field, value):
    print('MATERIAL_EDIT', field, flush=True)
    control = page.locator(f'#se225MEdit [data-se225-field="{field}"]')
    await control.scroll_into_view_if_needed()
    await control.fill(value)
    await control.dispatch_event('change')


async def close_transfers(page):
    summary = page.locator('details.se330-library-menu[open] > summary')
    if await summary.count():
        await summary.click()


async def render_gate(page, paused, label):
    await page.wait_for_function(
        'paused=>window.SWYRL_ENGINE_MATERIAL_LAYOUT_330.inspect().renderPaused===paused', arg=paused)
    before = await page.evaluate('()=>window.SWYRL_ENGINE_MATERIAL_LAYOUT_330.inspect().renderFrame')
    assert type(before) in (int, float), (label, 'Missing native render frame counter', before)
    await page.wait_for_timeout(250)
    if not paused:
        await page.wait_for_function(
            'before=>window.SWYRL_ENGINE_MATERIAL_LAYOUT_330.inspect().renderFrame>before', arg=before)
    after = await page.evaluate('()=>window.SWYRL_ENGINE_MATERIAL_LAYOUT_330.inspect()')
    assert after['renderPaused'] is paused, (label, after)
    if paused:
        assert after['renderFrame'] == before, (label, 'Opaque workspace rendered hidden scene', before, after)
    else:
        assert after['renderFrame'] > before, (label, 'Visible native scene did not render', before, after)


async def geometry(page, label):
    assert await page.evaluate('()=>document.documentElement.scrollWidth<=innerWidth+1'), label + ' page overflow'
    shell = page.locator('#se225Shell')
    assert await shell.is_visible(), label + ' shell'
    for name in ('library', 'texture', 'properties'):
        tab = page.locator(f'#se330MaterialTabs [data-se330-pane="{name}"]')
        if not await tab.is_visible():
            continue
        await click(page, f'#se330MaterialTabs [data-se330-pane="{name}"]')
        box = await tab.bounding_box()
        width = await page.evaluate('innerWidth')
        assert box and box['x'] >= -1 and box['x'] + box['width'] <= width + 1, (label, name, box)
        assert await page.locator('#se225MaterialsPanel').evaluate(
            'x=>x.scrollWidth<=x.clientWidth+1'), label + ' panel overflow'
    await pane(page, 'texture')
    for mode in ('texture', 'scene', 'texture'):
        button = f'#se330PreviewModes [data-se330-preview="{mode}"]'
        await click(page, button)
        if mode == 'texture':
            await page.wait_for_function('()=>!window.SWYRL_ENGINE_MATERIAL_LAYOUT_330.inspect().sampleVisible')
            await render_gate(page, True, label + ' texture')
            canvas = await page.locator('#se225MCanvas').bounding_box()
            assert canvas and canvas['width'] >= 140 and canvas['height'] >= 140, (label, canvas)
        else:
            await page.wait_for_function('''()=>{const s=window.SWYRL_ENGINE_MATERIAL_LAYOUT_330.inspect();
              return s.sampleVisible && s.sampleInsideStage;}''')
            await render_gate(page, False, label + ' scene')
            assert await page.locator('#viewport').is_visible(), label + ' native 3D viewport'
            hit = await page.locator('#se330MaterialSceneStage').evaluate('''stage => {
              const r=stage.getBoundingClientRect();
              const hit=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
              return {accepted:hit===document.querySelector('#viewport') || stage.contains(hit),
                tag:hit?.tagName,id:hit?.id,className:String(hit?.className||'')};
            }''')
            assert hit['accepted'], (label, 'Foreign overlay covers the native 3D preview', hit)
            await page.screenshot(path=str(out / (label + '-scene.png')))
    await page.screenshot(path=str(out / (label + '.png')))


async def open_materials(context, errors):
    for origin in (FORGE, CHAT, CDN):
        await context.route(origin + '/**', transport)
    page = await context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('dialog', lambda dialog: asyncio.create_task(dialog.accept()))
    await page.goto(FORGE + '/index.html#studio-materials', wait_until='domcontentloaded', timeout=90000)
    await page.wait_for_function('''()=>window.SWRLZ_FORGE_BUILD?.version==='v11.330' &&
      window.SWYRL_ENGINE_STUDIOS?.active()==='materials' &&
      !!document.querySelector('#se330MaterialTabs')''', timeout=60000)
    if await page.locator('#seReleaseNotesDialog[open]').count():
        await page.locator('#seReleaseNotesDialog[open] button').last.click()
    await page.wait_for_timeout(300)
    return page


async def main():
    errors = []
    receipt = {'version': 'v11.330', 'testedHtmlSha256': hashlib.sha256(html.read_bytes()).hexdigest(),
               'checks': [], 'pageErrors': errors}
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=args.chromium, headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--enable-unsafe-swiftshader'])
        try:
            desktop = await browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
            page = await open_materials(desktop, errors)
            assert await page.evaluate('()=>window.SWYRL_ENGINE_MATERIALS.list().length') == 0
            assert not await page.locator('#se225MEdit').is_visible(), 'Empty library must hide uninitialized fields'
            assert await page.locator('.se330-empty').is_visible(), 'Empty library needs a visible creation state'
            await page.screenshot(path=str(out / 'materials-desktop-empty.png'))
            identity = await page.evaluate('''()=>{const d=window.SWYRL_ENGINE_AGENT.inspectScene();
              return {name:d.project.name,canonicalId:d.project.canonicalId,actors:d.scene.actors.map(a=>a.id)};}''')
            await pane(page, 'library')
            await page.locator('#se225MPreset').select_option('gold')
            await click(page, '#se225MCreate')
            await page.wait_for_function('()=>window.SWYRL_ENGINE_MATERIALS.list().length===1')
            await page.locator('#se251MaterialsTree .se251-model-tree-item').focus()
            await page.keyboard.press('Delete')
            after_delete = await page.evaluate('''()=>{const d=window.SWYRL_ENGINE_AGENT.inspectScene();
              return {name:d.project.name,canonicalId:d.project.canonicalId,actors:d.scene.actors.map(a=>a.id)};}''')
            assert after_delete == identity, 'Delete in the material library must not delete a game actor'
            assert await page.evaluate('()=>window.SWYRL_ENGINE_MATERIALS.list().length') == 1
            receipt['checks'].append('Delete on focused material library row preserves scene actors and material data')
            await pane(page, 'properties')
            assert await page.locator('[data-se225-field="name"]').input_value() == 'Golden Armor'
            await edit(page, 'name', 'Studio check gold')
            await edit(page, 'baseColor', '#bd77f8')
            await edit(page, 'roughness', '0.38')
            material = await page.evaluate('()=>window.SWYRL_ENGINE_MATERIALS.list()[0]')
            edited = (material['name'], material['baseColor'], material['roughness'])
            assert edited == ('Studio check gold', '#bd77f8', .38), edited
            targets = await page.locator('#se225MTarget option').evaluate_all(
                'items=>items.map(x=>x.value).filter(Boolean)')
            assert targets, 'Public baseline must provide a scene actor for native assignment checks'
            await page.locator('#se225MTarget').select_option(targets[0])
            await click(page, '#se225MAssign')
            assert await page.evaluate('()=>window.SWYRL_ENGINE_MATERIALS.inspect().assignments') == 1
            assert 'Assigned: Studio check gold' in await page.locator('#se225MAssigned').inner_text()
            await click(page, '#se225MUnassign')
            assert await page.evaluate('()=>window.SWYRL_ENGINE_MATERIALS.inspect().assignments') == 0
            await pane(page, 'texture')
            await click(page, '#se330PreviewModes [data-se330-preview="texture"]')
            canvas = page.locator('#se225MCanvas')
            await canvas.scroll_into_view_if_needed()
            box = await canvas.bounding_box()
            print('MATERIAL_PAINT', 'hover', flush=True)
            await asyncio.wait_for(page.mouse.move(box['x'] + box['width'] * .25, box['y'] + box['height'] * .4), 20)
            print('MATERIAL_PAINT', 'down', flush=True)
            await asyncio.wait_for(page.mouse.down(), 20)
            print('MATERIAL_PAINT', 'drag', flush=True)
            await asyncio.wait_for(page.mouse.move(box['x'] + box['width'] * .7, box['y'] + box['height'] * .6, steps=1), 20)
            print('MATERIAL_PAINT', 'up', flush=True)
            await asyncio.wait_for(page.mouse.up(), 20)
            await page.wait_for_function('()=>window.SWYRL_ENGINE_MATERIALS.list()[0].strokes.length===1')
            await click(page, '#se225MPaintUndo')
            await page.wait_for_function('()=>window.SWYRL_ENGINE_MATERIALS.list()[0].strokes.length===0')
            texture_export = await prepare(page, '#se225MExportTexture')
            async with page.expect_download() as png_download:
                await texture_export.click()
            png = await png_download.value
            png_path = out / 'native-material-texture.png'
            await png.save_as(str(png_path))
            binary = png_path.read_bytes()
            assert binary[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', binary[16:24]) == (256, 256)
            image_import = await prepare(page, '#se225MImportImage')
            async with page.expect_file_chooser() as image_chooser:
                await image_import.click()
            await (await image_chooser.value).set_files(str(png_path))
            await page.wait_for_function('''()=>{const m=window.SWYRL_ENGINE_MATERIALS.list()[0];
              return m.pattern==='image' && m.imageData.startsWith('data:image/png;base64,');}''')
            await pane(page, 'properties')
            await click(page, '#se225MDuplicate')
            assert await page.evaluate('()=>window.SWYRL_ENGINE_MATERIALS.list().length') == 2
            await click(page, '#se225MDelete')
            assert await page.evaluate('()=>window.SWYRL_ENGINE_MATERIALS.list().length') == 1
            library_export = await prepare(page, '#se225MExportLibrary')
            async with page.expect_download() as library_download:
                await library_export.click()
            library = await library_download.value
            library_path = out / 'native-material-library.json'
            await library.save_as(str(library_path))
            await close_transfers(page)
            exported = json.loads(library_path.read_text())
            assert exported['schema'] == 'swyrl-material-studio-v1' and exported['assignments'] == []
            assert exported['materials'][0]['name'] == 'Studio check gold'
            serialized = await page.evaluate('()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.materialStudio')
            assert serialized == exported, 'Native project serialization must retain material definitions'
            await geometry(page, 'materials-desktop')
            receipt['checks'].append('native empty/create/edit/assign/restore/paint/undo/PNG export+image filechooser import/duplicate/delete/JSON/project serialization')
            for _ in range(2):
                for selector, mode in (
                    ('#se225Shell .se225-studio-tabs [data-se225-tab="game"]', 'game'),
                    ('#se320GameHeader [data-se187-tab="modeler"]', 'modeler'),
                    ('#modelAtelierPanel [data-se225-tab="particles"]', 'particles'),
                    ('#se249Root [data-se249-workspace="materials"]', 'materials')):
                    await click(page, selector)
                    await page.wait_for_function('(mode)=>window.SWYRL_ENGINE_STUDIOS.active()===mode', arg=mode)
                    await page.wait_for_timeout(120)
                assert await page.locator('#se225MaterialsPanel').count() == 1
                assert await page.locator('.app .se187-game-tabs').count() == 1
                current = await page.evaluate('''()=>{const d=window.SWYRL_ENGINE_AGENT.inspectScene();
                  return {name:d.project.name,canonicalId:d.project.canonicalId,actors:d.scene.actors.map(a=>a.id)};}''')
                assert current == identity, 'Studio switching must preserve the loaded scene'
                assert await page.evaluate('()=>window.SWYRL_ENGINE_MATERIALS.export()') == exported
            receipt['checks'].append('two complete Game/Model/Particle/Material round trips, one panel, unchanged scene/material data')
            await desktop.close()
            mobile = await browser.new_context(viewport={'width': 390, 'height': 844},
                is_mobile=True, has_touch=True, device_scale_factor=1, accept_downloads=True)
            phone = await open_materials(mobile, errors)
            await pane(phone, 'library')
            library_import = await prepare(phone, '#se225MImportLibrary')
            async with phone.expect_file_chooser() as chooser:
                await library_import.click()
            await (await chooser.value).set_files(str(library_path))
            await phone.wait_for_function('()=>window.SWYRL_ENGINE_MATERIALS.list().length===1')
            await close_transfers(phone)
            assert await phone.evaluate('()=>window.SWYRL_ENGINE_MATERIALS.export()') == exported
            await geometry(phone, 'materials-phone')
            await phone.set_viewport_size({'width': 980, 'height': 1800})
            await phone.wait_for_timeout(200)
            await geometry(phone, 'materials-wide-phone-iframe')
            receipt['checks'].append('390x844 touch phone and 980x1800 portrait iframe panels/preview modes: bounds, hit-tests, no horizontal overflow')
            receipt['checks'].append('native render frames pause under opaque texture UI, advance for visible 3D preview, pause again on return')
            await mobile.close()
            assert not errors, errors
            receipt['status'] = 'PASS'
            (out / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print('MATERIAL_STUDIO_V11_330_BROWSER_PASS', json.dumps(receipt), flush=True)
        finally:
            await browser.close()


asyncio.run(main())
