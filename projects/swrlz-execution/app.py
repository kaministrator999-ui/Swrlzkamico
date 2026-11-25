import os
import shutil
import time
from io import BytesIO

import gradio as gr
from PIL import Image
from playwright.sync_api import sync_playwright

FIXTURE = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{background:#101321;color:#e8e5ff;font:18px sans-serif;margin:32px}canvas{width:480px;height:240px;border:1px solid #7965bf}button{padding:10px}
</style></head><body><h1>§Execution — Chromium probe</h1><p id="state">Ready</p><button id="test" onclick="document.querySelector('#state').textContent='Click passed'">Test interaction</button><p>WebGL test surface</p><canvas id="gl" width="480" height="240"></canvas></body></html>'''


def probe():
    started = time.monotonic()
    result = {'chromium': 'not tested', 'javascript': 'not tested', 'interaction': 'not tested', 'webgl': 'not tested', 'screenshot': 'not tested'}
    screenshot = None
    errors = []
    executable = shutil.which('chromium') or shutil.which('chromium-browser')
    if not executable:
        result['chromium'] = 'FAIL: Chromium executable not found'
        return result, None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=executable, headless=True, chromium_sandbox=False, timeout=15000,
                args=['--disable-dev-shm-usage', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
            try:
                result['chromium'] = 'PASS'
                result['browser_version'] = browser.version
                page = browser.new_page(viewport={'width': 800, 'height': 560}, device_scale_factor=1)
                page.set_default_timeout(5000)
                page.route('**/*', lambda route: route.abort())
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.set_content(FIXTURE, wait_until='domcontentloaded', timeout=5000)
                result['javascript'] = 'PASS' if page.evaluate('6 * 7') == 42 else 'FAIL'
                page.locator('#test').click()
                result['interaction'] = 'PASS' if page.locator('#state').inner_text() == 'Click passed' else 'FAIL'
                result['webgl'] = page.evaluate('''() => {
                    const canvas = document.querySelector('#gl');
                    const gl = canvas.getContext('webgl2', {preserveDrawingBuffer:true}) || canvas.getContext('webgl', {preserveDrawingBuffer:true});
                    if (!gl) return {status:'FAIL', reason:'WebGL context unavailable'};
                    gl.clearColor(0.36, 0.19, 0.76, 1); gl.clear(gl.COLOR_BUFFER_BIT);
                    const pixel = new Uint8Array(4); gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,pixel);
                    const expected = [92,48,194,255];
                    const ok = expected.every((v,i) => Math.abs(pixel[i]-v)<=2) && gl.getError()===gl.NO_ERROR;
                    const ext = gl.getExtension('WEBGL_debug_renderer_info');
                    return {status:ok?'PASS':'FAIL', version:gl.getParameter(gl.VERSION), renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER), pixel:Array.from(pixel)};
                }''')
                screenshot = Image.open(BytesIO(page.screenshot(timeout=5000))).copy()
                result['screenshot'] = 'PASS'
            finally:
                browser.close()
    except Exception as exc:
        result['error'] = str(exc)[:1600]
        if result['chromium'] == 'not tested':
            result['chromium'] = 'FAIL'
    result['page_errors'] = errors
    result['elapsed_seconds'] = round(time.monotonic() - started, 2)
    return result, screenshot

with gr.Blocks(title='§Execution — diagnostics', analytics_enabled=False) as demo:
    gr.Markdown('# §Execution — browser diagnostics\nFixed local test fixture only. No user-supplied code, URLs, credentials or network requests.')
    run = gr.Button('Run Chromium diagnostics', variant='primary')
    result = gr.JSON(label='Diagnostic results')
    screenshot = gr.Image(label='Browser screenshot', interactive=False)
    run.click(probe, outputs=[result, screenshot], concurrency_limit=1, api_name=False)

if __name__ == '__main__':
    demo.queue(max_size=4).launch(server_name='0.0.0.0', server_port=int(os.getenv('PORT', '7860')))
