import os
import hashlib
import hmac
import json
import re
import threading
import shutil
import time
from io import BytesIO

import spaces
import torch
import gradio as gr
from PIL import Image
from playwright.sync_api import sync_playwright

FIXTURE = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{background:#101321;color:#e8e5ff;font:18px sans-serif;margin:32px}canvas{width:480px;height:240px;border:1px solid #7965bf}button{padding:10px}
</style></head><body><h1>§Execution — Chromium probe</h1><p id="state">Ready</p><button id="test" onclick="document.querySelector('#state').textContent='Click passed'">Test interaction</button><p>WebGL test surface</p><canvas id="gl" width="480" height="240"></canvas></body></html>'''


_probe_lock = threading.Lock()

def probe():
    if not _probe_lock.acquire(blocking=False):
        return {'error': 'BROWSER_BUSY'}, None
    try:
        return _probe()
    finally:
        _probe_lock.release()

def _probe():
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

@spaces.GPU(duration=20)
def compare_screenshots(reference, candidate):
    """GPU-accelerated local structural similarity and pixel-change heatmap."""
    if reference is None or candidate is None:
        return {"status": "Supply both images"}, None
    if reference.shape != candidate.shape:
        return {"status": "Dimension mismatch", "reference": list(reference.shape), "candidate": list(candidate.shape)}, None
    height, width = reference.shape[:2]
    if min(height, width) < 8 or max(height, width) > 4096 or height * width > 16777216:
        return {"status": "Use equal-sized RGB images between 8 and 4096 pixels per side"}, None
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable for GPU visual regression")
    with torch.inference_mode():
        a = torch.from_numpy(reference.copy()).to(device="cuda", dtype=torch.float32).permute(2, 0, 1).unsqueeze(0) / 255.0
        b = torch.from_numpy(candidate.copy()).to(device="cuda", dtype=torch.float32).permute(2, 0, 1).unsqueeze(0) / 255.0
        diff = (a - b).abs().amax(dim=1)[0]
        changed = diff > (2.0 / 255.0)
        # Local windowed structural similarity (SSIM), calculated on CUDA.
        # Downsample only the SSIM inputs to bound GPU working memory for 4K images.
        scale = min(1.0, 1024.0 / max(height, width))
        if scale < 1:
            size = (max(8, round(height * scale)), max(8, round(width * scale)))
            x = torch.nn.functional.interpolate(a, size=size, mode="area")
            y = torch.nn.functional.interpolate(b, size=size, mode="area")
        else:
            x, y = a, b
        pool = lambda t: torch.nn.functional.avg_pool2d(t, 7, stride=1, padding=0)
        mx, my = pool(x), pool(y)
        vx = (pool(x*x) - mx*mx).clamp_min(0)
        vy = (pool(y*y) - my*my).clamp_min(0)
        cov = pool(x*y) - mx*my
        c1, c2 = 0.01**2, 0.03**2
        score = ((2*mx*my+c1)*(2*cov+c2)/((mx.square()+my.square()+c1)*(vx+vy+c2))).mean().item()
        heat = torch.stack((diff, diff*0.15, torch.zeros_like(diff)), dim=-1)
        heat = (heat.clamp(0, 1)*255).to(torch.uint8).cpu().numpy()
        return {"status": "PASS", "device": torch.cuda.get_device_name(0), "width": width, "height": height,
                "ssim": round(score, 6), "changed_pixels_percent": round(changed.float().mean().item()*100, 4),
                "mean_absolute_pixel_delta": round((a-b).abs().mean().item()*255, 4),
                "note": "SSIM uses a 7x7 local window and is evaluated at up to 1024 pixels per side; pixel differences use original resolution."}, heat


# Signed, fixed-fixture diagnostic only. No arbitrary HTML or URLs accepted.
_remote_seen = {}
_remote_lock = threading.Lock()

def _wire(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def _mac(key, kind, raw):
    return hmac.new(key.encode(), kind.encode()+bytes([0])+raw, hashlib.sha256).hexdigest()

def remote_probe(request_json, signature):
    key = os.environ.get("SWRLZ_X_DIAGNOSTIC_KEY", "")
    if len(key) != 64 or not isinstance(request_json, str) or len(request_json) > 512 or not isinstance(signature, str) or len(signature) != 64:
        raise gr.Error("REMOTE_DENIED")
    if not hmac.compare_digest(_mac(key, "request", request_json.encode()), signature):
        raise gr.Error("REMOTE_DENIED")
    try:
        obj = json.loads(request_json)
        now = int(time.time())
        if set(obj) != {"schema", "nonce", "timestamp"} or obj["schema"] != "swrlz-x-diagnostic-v1" or not re.fullmatch(r"[0-9a-f]{32}", obj["nonce"]) or type(obj["timestamp"]) is not int or abs(now-obj["timestamp"]) > 120:
            raise ValueError()
    except (ValueError, TypeError, KeyError):
        raise gr.Error("REMOTE_INVALID")
    with _remote_lock:
        for nonce in list(_remote_seen):
            if now - _remote_seen[nonce] > 241:
                del _remote_seen[nonce]
        if obj["nonce"] in _remote_seen or len(_remote_seen) >= 256:
            raise gr.Error("REMOTE_REPLAY_OR_LIMIT")
        _remote_seen[obj["nonce"]] = now
    result, screenshot = probe()
    result["screenshot_sha256"] = None
    if screenshot is not None:
        buf = BytesIO()
        screenshot.save(buf, format="PNG")
        result["screenshot_sha256"] = hashlib.sha256(buf.getvalue()).hexdigest()
    passed = (all(result.get(k) == "PASS" for k in ("chromium", "javascript", "interaction", "screenshot"))
              and isinstance(result.get("webgl"), dict) and result["webgl"].get("status") == "PASS"
              and result.get("page_errors") == [] and bool(result["screenshot_sha256"]))
    receipt = {"schema":obj["schema"], "nonce":obj["nonce"], "timestamp":int(time.time()), "passed":passed,
               "fixture_sha256":hashlib.sha256(FIXTURE.encode()).hexdigest(), "diagnostics":result,
               "arbitrary_execution":False, "isolation_verified":False}
    return {"receipt":receipt, "signature":_mac(key, "receipt", _wire(receipt))}


with gr.Blocks(title='§Execution — diagnostics', analytics_enabled=False) as demo:
    gr.Markdown('# §Execution — browser diagnostics\nFixed local test fixture only. No user-supplied code, URLs, credentials or network requests.')
    run = gr.Button('Run Chromium diagnostics', variant='primary')
    result = gr.JSON(label='Diagnostic results')
    screenshot = gr.Image(label='Browser screenshot', interactive=False)
    run.click(probe, outputs=[result, screenshot], concurrency_limit=1, api_name=False)
    request_json = gr.Textbox(visible=False)
    request_signature = gr.Textbox(visible=False)
    remote_result = gr.JSON(visible=False)
    remote_button = gr.Button(visible=False)
    remote_button.click(remote_probe, inputs=[request_json, request_signature], outputs=remote_result, api_name="swrlz_diagnostics_v1", concurrency_limit=1)
    gr.Markdown("## GPU visual regression\nCompare two screenshots of the same dimensions. This optional CUDA diagnostic uses the caller's ZeroGPU quota. Do not upload private images to this public Space.")
    with gr.Row():
        reference = gr.Image(label="Reference screenshot", type="numpy", image_mode="RGB", sources=["upload"])
        candidate = gr.Image(label="Candidate screenshot", type="numpy", image_mode="RGB", sources=["upload"])
    compare = gr.Button("Compare screenshots on GPU")
    metrics = gr.JSON(label="Visual comparison metrics")
    heatmap = gr.Image(label="Pixel-change heatmap", interactive=False)
    compare.click(compare_screenshots, inputs=[reference, candidate], outputs=[metrics, heatmap], concurrency_limit=1, api_name=False)

if __name__ == '__main__':
    demo.queue(max_size=4).launch(server_name='0.0.0.0', server_port=int(os.getenv('PORT', '7860')))
