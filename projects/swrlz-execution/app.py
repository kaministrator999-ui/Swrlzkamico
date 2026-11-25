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


# Fixed child script. It tests only synthetic files and loopback sockets.
_LANDLOCK_CHILD = r'''
import ctypes as C
import errno, json, os, platform, socket, struct, tempfile
from pathlib import Path

out = {"schema":"swrlz-landlock-probe-v1","abi":None,"enforced":False,
       "unprivileged":os.geteuid()!=0,"noNewPrivileges":False,
       "checks":{},"status":"UNVERIFIED"}
libc=C.CDLL(None,use_errno=True)
libc.syscall.restype=C.c_long
libc.prctl.restype=C.c_int
def syscall(n,*args):
    C.set_errno(0)
    v=libc.syscall(C.c_long(n),*args)
    if v<0: raise OSError(C.get_errno(), "landlock syscall")
    return v
def record(name,fn,deny=False):
    try:
        fn()
        out["checks"][name]={"pass":not deny,"result":"ALLOWED"}
    except OSError as e:
        out["checks"][name]={"pass":deny and e.errno in (errno.EACCES,errno.EPERM),
                             "result":"ERRNO_"+str(e.errno)}
def main():
    if platform.machine() not in ("x86_64","aarch64","riscv64"):
        out["status"]="ARCH_UNSUPPORTED";return
    try: abi=syscall(444,C.c_void_p(),C.c_size_t(0),C.c_uint(1))
    except OSError as e:
        out["status"]="ABI_QUERY_ERRNO_"+str(e.errno);return
    out["abi"]=abi
    if abi<1: return
    # ABI 1 filesystem rights; ABI 2 refer; ABI 3 truncate.
    fs=(1<<13)-1
    if abi>=2: fs|=1<<13
    if abi>=3: fs|=1<<14
    net=3 if abi>=4 else 0
    out["tcpSupported"]=bool(net)
    root=Path(tempfile.mkdtemp(dir=os.environ["HOME"]))
    inside=root/"allowed";outside=root/"denied"
    inside.mkdir();outside.mkdir()
    a=inside/"fixture.txt"; b=outside/"fixture.txt"
    a.write_text("allowed");b.write_text("synthetic canary")
    def read(p): p.read_bytes()
    def write(p): p.write_text("test")
    def truncate(p): os.truncate(p,0)
    # Prove both canaries were accessible before restriction.
    record("baselineAllowedRead",lambda:read(a))
    record("baselineOutsideRead",lambda:read(b))
    record("baselineOutsideWrite",lambda:write(b))
    record("baselineOutsideTruncate",lambda:truncate(b))
    listener=None
    def bind():
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1",0))
    def connect():
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.settimeout(1);s.connect(("127.0.0.1",port))
    try:
        if net:
            listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                listener.bind(("127.0.0.1",0));listener.listen(2)
                port=listener.getsockname()[1]
                record("baselineTcpBind",bind)
                record("baselineTcpConnect",connect)
                if out["checks"]["baselineTcpConnect"]["pass"]:
                    peer,_=listener.accept();peer.close()
            except OSError as e:
                out["tcpBaselineError"]="ERRNO_"+str(e.errno)
        # Ruleset attributes use only fields supported by the detected ABI.
        attr=C.create_string_buffer(struct.pack("=QQ",fs,net) if net else struct.pack("=Q",fs))
        fd=syscall(444,C.byref(attr),C.c_size_t(16 if net else 8),C.c_uint(0))
        try:
            d=os.open(inside,os.O_PATH|os.O_CLOEXEC)
            try:
                rule=C.create_string_buffer(struct.pack("=Qi",fs,d))
                syscall(445,C.c_int(fd),C.c_int(1),C.byref(rule),C.c_uint(0))
            finally: os.close(d)
            if libc.prctl(C.c_int(38),C.c_ulong(1),C.c_ulong(0),C.c_ulong(0),C.c_ulong(0))!=0:
                raise OSError(C.get_errno(),"no_new_privs")
            out["noNewPrivileges"]=libc.prctl(C.c_int(39),C.c_ulong(0),C.c_ulong(0),C.c_ulong(0),C.c_ulong(0))==1
            syscall(446,C.c_int(fd),C.c_uint(0))
            out["enforced"]=True
        finally: os.close(fd)
        record("allowedRead",lambda:read(a))
        record("allowedWrite",lambda:write(a))
        record("outsideReadDenied",lambda:read(b),True)
        record("outsideWriteDenied",lambda:write(b),True)
        record("outsideCreateDenied",lambda:write(outside/"new.txt"),True)
        record("outsideUnlinkDenied",lambda:b.unlink(),True)
        if abi>=3: record("outsideTruncateDenied",lambda:truncate(b),True)
        if net and listener is not None and out["checks"].get("baselineTcpBind",{}).get("pass") and out["checks"].get("baselineTcpConnect",{}).get("pass"):
            record("tcpBindDenied",bind,True)
            record("tcpConnectDenied",connect,True)
        expected=["baselineAllowedRead","baselineOutsideRead","baselineOutsideWrite","baselineOutsideTruncate","allowedRead","allowedWrite","outsideReadDenied","outsideWriteDenied","outsideCreateDenied","outsideUnlinkDenied"]
        out["filesystemChecksPassed"]=all(out["checks"].get(k,{}).get("pass") for k in expected)
        out["truncateProtectionPassed"]=out["checks"].get("outsideTruncateDenied",{}).get("pass",False)
        out["tcpChecksPassed"]=all(out["checks"].get(k,{}).get("pass") for k in ("baselineTcpBind","baselineTcpConnect","tcpBindDenied","tcpConnectDenied"))
        out["status"]="CAPABILITY_TESTED"
    finally:
        if listener is not None: listener.close()
try: main()
except OSError as e: out["status"]="ENFORCEMENT_ERRNO_"+str(e.errno)
except Exception as e: out["status"]="PROBE_ERROR_"+type(e).__name__
print(json.dumps(out),flush=True)
'''


def landlock_probe():
    import subprocess
    import tempfile
    import sys
    import pwd
    import signal
    result={"schema":"swrlz-landlock-probe-v1","status":"UNVERIFIED","enforced":False}
    try:
        with tempfile.TemporaryDirectory(prefix="swrlz-landlock-") as home:
            kwargs={}
            if os.geteuid()==0:
                account=pwd.getpwnam("nobody")
                if account.pw_uid==0: return result
                os.chown(home,account.pw_uid,account.pw_gid)
                kwargs={"user":account.pw_uid,"group":account.pw_gid,"extra_groups":[]}
            env={"PATH":"/usr/bin:/bin:/usr/local/bin","HOME":home,"TMPDIR":home,
                 "LANG":"C.UTF-8","PYTHONDONTWRITEBYTECODE":"1"}
            proc=subprocess.Popen([sys.executable,"-I","-c",_LANDLOCK_CHILD],
                cwd=home,env=env,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                start_new_session=True,**kwargs)
            try: raw,_=proc.communicate(timeout=12)
            except subprocess.TimeoutExpired:
                try: os.killpg(proc.pid,signal.SIGKILL)
                except ProcessLookupError: pass
                proc.communicate()
                result["status"]="TIMEOUT";return result
            if proc.returncode!=0 or len(raw)>12000:
                result["status"]="CHILD_FAILED";result["exitCode"]=proc.returncode;return result
            data=json.loads(raw)
            if data.get("schema")!="swrlz-landlock-probe-v1":return result
            return data
    except Exception as exc:
        result["status"]="PROBE_INFRASTRUCTURE_"+type(exc).__name__
        return result


def isolation_probe():
    """Trusted fixed probes only; never accepts candidate bytes or commands."""
    import subprocess
    import tempfile
    import signal
    import sys
    evidence = {"schema": "swrlz-x-isolation-v03", "browserSandbox": False,
                "userNamespace": False, "networkNamespace": False,
                "mountNamespace": False, "filesystemIsolation": False,
                "processIsolation": False, "candidateExecutionEnabled": False,
                "isolationVerified": False, "status": "BLOCKED", "reasons": []}
    from pathlib import Path
    evidence["probeSourceSha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if not _probe_lock.acquire(blocking=False):
        evidence["status"] = "BUSY"
        return evidence
    try:
        with tempfile.TemporaryDirectory(prefix="swrlz-isolation-probe-") as home:
            env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": home,
                   "TMPDIR": home, "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"}
            evidence["effectiveUserIsRoot"] = os.geteuid() == 0
            evidence["probeDetails"] = {}
            evidence["landlock"] = landlock_probe()
            def invoke(command, timeout=10):
                p = subprocess.Popen(command, cwd=home, env=env, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, start_new_session=True)
                try:
                    out, err = p.communicate(timeout=timeout)
                    msg = err.decode(errors="replace").lower()
                    # Expose only predefined categories, never raw paths, environment or logs.
                    category = "OK" if p.returncode == 0 else "NONZERO_EXIT"
                    for needle, label in (
                        ("running as root without --no-sandbox", "ROOT_SANDBOX_UNSUPPORTED"),
                        ("no usable sandbox", "NO_USABLE_SANDBOX"),
                        ("operation not permitted", "OPERATION_NOT_PERMITTED"),
                        ("permission denied", "PERMISSION_DENIED"),
                        ("modulenotfounderror", "PYTHON_DEPENDENCY_MISSING"),
                        ("not supported", "NOT_SUPPORTED"),
                        ("no such file or directory", "MISSING_PATH_OR_EXECUTABLE"),
                    ):
                        if needle in msg and p.returncode != 0:
                            category = label
                            break
                    return p.returncode == 0, out[:4096], {"category": category, "exitCode": p.returncode}
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(p.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    p.communicate()
                    return False, b"", {"category": "TIMEOUT", "exitCode": None}
            unshare = shutil.which("unshare")
            if unshare:
                for name, flag, ns in (
                    ("userNamespace", "--user", "user"),
                    ("networkNamespace", "--net", "net"),
                    ("mountNamespace", "--mount", "mnt"),
                    ("processIsolation", "--pid", "pid"),
                ):
                    parent = os.readlink("/proc/self/ns/" + ns)
                    args = [unshare, "--user", "--map-root-user"]
                    if flag != "--user":
                        args += [flag]
                    args += ["--fork", "--", "/usr/bin/readlink", "/proc/self/ns/" + ns]
                    ok, out, detail = invoke(args)
                    evidence["probeDetails"][name] = detail
                    evidence[name] = bool(ok and out.strip() and out.decode(errors="replace").strip() != parent)
            else:
                evidence["reasons"].append("UNSHARE_UNAVAILABLE")
            # Independently test each namespace without first requiring a user namespace.
            evidence["independentNamespaceChecks"] = {}
            if unshare:
                for name, flag, ns in (
                    ("userNamespace", "--user", "user"),
                    ("networkNamespace", "--net", "net"),
                    ("mountNamespace", "--mount", "mnt"),
                    ("processIsolation", "--pid", "pid"),
                ):
                    parent = os.readlink("/proc/self/ns/" + ns)
                    ok, out, detail = invoke([unshare, flag, "--fork", "--", "/usr/bin/readlink", "/proc/self/ns/" + ns])
                    evidence["independentNamespaceChecks"][name] = {
                        **detail, "namespaceChanged": bool(ok and out.strip() and out.decode(errors="replace").strip() != parent)}
            # Chromium must launch with its own sandbox explicitly enabled.
            # A separate child receives no application credentials.
            chromium = shutil.which("chromium") or shutil.which("chromium-browser")
            if chromium:
                code = """
from playwright.sync_api import sync_playwright
import sys
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=sys.argv[1],headless=True,chromium_sandbox=True,
        args=['--disable-dev-shm-usage','--use-angle=swiftshader'],timeout=12000)
    try:
        page=b.new_page()
        page.set_content('<p>trusted sandbox probe</p>')
        assert page.locator('p').inner_text()=='trusted sandbox probe'
        print('SANDBOX_LAUNCH_OK',flush=True)
    finally:
        b.close()
"""
                ok, out, detail = invoke([sys.executable, "-I", "-c", code, chromium], timeout=20)
                evidence["probeDetails"]["browserSandbox"] = detail
                evidence["browserSandbox"] = bool(ok and b"SANDBOX_LAUNCH_OK" in out)
            # Test native Chromium sandbox under an existing unprivileged account.
            # This is a fixed trusted fixture; no user-controlled source or command.
            evidence["nonRootBrowserSandbox"] = False
            if chromium and os.geteuid() == 0:
                import pwd
                setpriv = shutil.which("setpriv")
                try:
                    account = pwd.getpwnam("nobody")
                except KeyError:
                    account = None
                if setpriv and account is not None and account.pw_uid != 0:
                    os.chown(home, account.pw_uid, account.pw_gid)
                    env["USER"] = account.pw_name
                    env["LOGNAME"] = account.pw_name
                    # Use the installed Chromium directly to distinguish sandbox
                    # startup from Python package accessibility under this account.
                    command = [setpriv, "--reuid", str(account.pw_uid),
                               "--regid", str(account.pw_gid), "--clear-groups",
                               chromium, "--headless", "--disable-dev-shm-usage",
                               "--disable-background-networking",
                               "--no-first-run", "--user-data-dir=" + home + "/profile",
                               "--dump-dom", "data:text/html,<p>swrlz-sandbox-probe</p>"]
                    ok, out, detail = invoke(command, timeout=20)
                    evidence["probeDetails"]["nonRootBrowserSandbox"] = detail
                    evidence["nonRootBrowserSandbox"] = bool(ok and b"<p>swrlz-sandbox-probe</p>" in out)
                else:
                    evidence["probeDetails"]["nonRootBrowserSandbox"] = {"category": "UNPRIVILEGED_USER_OR_SETPRIV_UNAVAILABLE", "exitCode": None}
            elif chromium:
                evidence["nonRootBrowserSandbox"] = evidence["browserSandbox"]
            # A changed mount namespace is NOT proof of a restricted filesystem.
            # No production sandbox runner exists yet, so always fail closed.
            for name in ("browserSandbox","userNamespace","networkNamespace","mountNamespace","processIsolation"):
                if not evidence[name]:
                    evidence["reasons"].append(name + "_UNVERIFIED")
            evidence["reasons"].append("FILESYSTEM_BOUNDARY_AND_COMBINED_SANDBOX_NOT_VERIFIED")
            return evidence
    except Exception:
        evidence["reasons"].append("PROBE_INFRASTRUCTURE_ERROR")
        return evidence
    finally:
        _probe_lock.release()


# Trusted fixed browser fixture only. This is NOT a replacement for Chromium's native sandbox.
_COMBINED_CHILD = r'''
import ctypes as C
import errno, hashlib, json, os, platform, shutil, socket, struct, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

out={"schema":"swrlz-x-combined-v04","status":"UNVERIFIED","abi":None,
     "landlockEnforced":False,"unprivileged":os.geteuid()!=0,"nativeChromiumSandbox":False,
     "candidateExecutionEnabled":False,"isolationVerified":False,"checks":{}}
libc=C.CDLL(None,use_errno=True)
libc.syscall.restype=C.c_long
libc.prctl.restype=C.c_int
def syscall(n,*args):
    C.set_errno(0)
    v=libc.syscall(C.c_long(n),*args)
    if v<0: raise OSError(C.get_errno(),"landlock syscall")
    return v
def test(name,fn,deny=False):
    try:
        fn()
        out["checks"][name]={"pass":not deny,"result":"ALLOWED"}
    except OSError as e:
        out["checks"][name]={"pass":deny and e.errno in (errno.EACCES,errno.EPERM),"result":"ERRNO_"+str(e.errno)}
def browser_failure(exc):
    msg=str(exc).lower()
    # Fixed categories only: never expose exception text, environment or paths.
    patterns=(
        ("openssl configuration error", "OPENSSL_CONFIG_ERROR"),
        ("openssl.cnf", "OPENSSL_CONFIG_PATH"),
        ("calling fopen", "FOPEN"),
        ("openssl", "OPENSSL"),
        ("node:internal", "NODE_INTERNAL"),
        ("uv_get", "LIBUV_INIT"),
        ("crashpad", "CRASHPAD"),
        ("--database is required", "CRASH_REPORTER_DATABASE"),
        ("permission denied", "PERMISSION_DENIED"),
        ("eacces", "PERMISSION_DENIED"),
        ("operation not permitted", "OPERATION_NOT_PERMITTED"),
        ("no such file or directory", "MISSING_RUNTIME_PATH"),
        ("error while loading shared libraries", "SHARED_LIBRARY"),
        ("cannot open shared object", "SHARED_LIBRARY"),
        ("failed to move to new namespace", "NAMESPACE_DENIED"),
        ("no usable sandbox", "NATIVE_SANDBOX_UNAVAILABLE"),
        ("running as root", "ROOT_BROWSER"),
        ("devtoolsactiveport", "DEVTOOLS_PORT"),
        ("/dev/null", "DEV_NULL"),
        ("/proc/", "PROC_ACCESS"),
        ("dbus", "DBUS"),
        ("zygote", "ZYGOTE"),
        ("sigtrap", "SIGTRAP"),
        ("sigsegv", "SIGSEGV"),
        ("sigabrt", "SIGABRT"),
        ("timeout", "TIMEOUT"),
        ("closed", "BROWSER_CLOSED"),
    )
    return sorted({label for needle,label in patterns if needle in msg}) or [type(exc).__name__]

def runtime_paths():
    # Check only known public system resources. No file content is returned.
    paths={"devNullRead":("/dev/null",os.O_RDONLY),
           "devNullWrite":("/dev/null",os.O_WRONLY),
           "procSelfStatus":("/proc/self/status",os.O_RDONLY),
           "procSelfMaps":("/proc/self/maps",os.O_RDONLY),
           "procCpuInfo":("/proc/cpuinfo",os.O_RDONLY),
           "procMemInfo":("/proc/meminfo",os.O_RDONLY),
           "devUrandom":("/dev/urandom",os.O_RDONLY),
           "loaderCache":("/etc/ld.so.cache",os.O_RDONLY),
           "fontConfig":("/etc/fonts/fonts.conf",os.O_RDONLY),
           "opensslConfig":("/etc/ssl/openssl.cnf",os.O_RDONLY),
           "opensslRuntimeConfig":("/usr/lib/ssl/openssl.cnf",os.O_RDONLY),
           "opensslCertificateBundle":("/etc/ssl/certs/ca-certificates.crt",os.O_RDONLY),
           "procSelfExe":("/proc/self/exe",os.O_RDONLY),
           "procSelfAuxv":("/proc/self/auxv",os.O_RDONLY)}
    result={}
    for name,(path,mode) in paths.items():
        try:
            fd=os.open(path,mode|os.O_CLOEXEC);os.close(fd)
            result[name]="ALLOWED"
        except OSError as e:result[name]="ERRNO_"+str(e.errno)
    return result

def main():
    if not out["unprivileged"] or platform.machine() not in ("x86_64","aarch64","riscv64"):
        out["status"]="UNSUPPORTED_RUNTIME";return
    home=Path(os.environ["HOME"])
    work=home/"work";work.mkdir()
    outside=home/"canary.txt";outside.write_text("synthetic only")
    allowed=work/"canary.txt";allowed.write_text("inside")
    chromium=shutil.which("chromium") or shutil.which("chromium-browser")
    if not chromium:out["status"]="CHROMIUM_MISSING";return
    abi=syscall(444,C.c_void_p(),C.c_size_t(0),C.c_uint(1));out["abi"]=abi
    if abi<4:out["status"]="LANDLOCK_ABI_TOO_OLD";return
    # The original child cwd was the parent of the permitted workspace.
    # Keep cwd inside the workspace for both baseline and restricted runs.
    os.chdir(work)
    out["cwdInsideWorkspace"]=Path.cwd()==work
    out["stage"]="baseline_browser"
    # Same UID, clean environment and same arguments, before applying Landlock.
    # Both launches are trusted fixtures, not candidate execution.
    os.environ.update({"HOME":str(work),"TMPDIR":str(work),"XDG_CACHE_HOME":str(work/"cache"),"XDG_CONFIG_HOME":str(work/"config")})
    launch_args=["--disable-dev-shm-usage","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader",
                 "--disable-background-networking","--disable-sync","--disable-component-update"]
    def node_startup_checks():
        from playwright._impl._driver import compute_driver_executable
        node,_=compute_driver_executable()
        result={}
        for label,args in (("version",["--version"]),("pureJavaScript",["-e","console.log(42)"]),
                           ("builtinFs",["-e","require('fs');console.log(42)"]),
                           ("builtinCrypto",["-e","require('crypto');console.log(42)"])):
            try:
                run=subprocess.run([node,*args],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,timeout=4,check=False)
                msg=run.stderr.decode(errors="replace")
                # Fixed markers rather than raw stderr; preserve exact known public
                # configuration dependency names without exposing private paths.
                markers=[label for label,needle in (
                    ("OPENSSL_CONFIG_ERROR","openssl configuration error"),
                    ("OPENSSL_CONFIG_FILE","openssl.cnf"),
                    ("FOPEN","fopen("),("PERMISSION_DENIED","permission denied"),
                    ("SYSTEM_LIB_SSL","/usr/lib/ssl/"),
                    ("ETC_SSL","/etc/ssl/"),("PROC_SELF","/proc/self/"),
                    ("NODE_INTERNAL","node:internal"),("LIBUV","uv_"),
                    ("EACCES","eacces"),("ERRNO_13","errno: -13")) if needle in msg.lower()]
                result[label]={"exitCode":run.returncode,"pass":run.returncode==0,
                               "markers":markers}
            except Exception as e:result[label]={"pass":False,"failureCategories":browser_failure(e)}
        return result
    out["baselineRuntimeAccess"]=runtime_paths()
    out["baselineNodeStartup"]=node_startup_checks()
    out["baselineBrowserLaunch"]=False
    try:
        with sync_playwright() as baseline:
            b=baseline.chromium.launch(executable_path=chromium,headless=True,chromium_sandbox=False,timeout=10000,args=launch_args)
            try:
                page=b.new_page();page.set_content("<p>trusted baseline</p>",timeout=3000)
                out["baselineBrowserLaunch"]=page.locator("p").inner_text(timeout=3000)=="trusted baseline"
            finally:b.close()
    except Exception as e:out["baselineBrowserFailureCategories"]=browser_failure(e)
    out["stage"]="stage_trusted_driver"
    staged_cli=None
    try:
        from playwright._impl._driver import compute_driver_executable
        installed_node,installed_cli=compute_driver_executable()
        package=Path(installed_cli).resolve().parent
        # Copy only the installed Playwright package, never application files.
        # Bound staging size and avoid following symlinks.
        if package.name!="package" or package.parent.name!="driver":
            out["driverStaging"]="UNEXPECTED_PACKAGE_LAYOUT"
        else:
            total=0;count=0
            for folder,dirs,files in os.walk(package,followlinks=False):
                for name in files:
                    f=Path(folder)/name
                    if not f.is_symlink():
                        total+=f.stat().st_size;count+=1
                    if total>100*1024*1024 or count>12000:raise ValueError("staging limit")
            staged=work/"trusted-playwright-package"
            shutil.copytree(package,staged,symlinks=True)
            staged_cli=str(staged/Path(installed_cli).name)
            out["driverStaging"]="COPIED"
    except Exception as e:
        out["driverStaging"]="FAILED_"+type(e).__name__
    out["stage"]="landlock_boundary"
    fs=(1<<15)-1
    read_exec=(1<<0)|(1<<2)|(1<<3)
    def read(p):p.read_bytes()
    def write(p):p.write_text("probe")
    def bind():
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:s.bind(("127.0.0.1",0))
    # Positive controls are performed before restrictions. No real secret is read.
    test("baselineOutsideRead",lambda:read(outside))
    test("baselineOutsideWrite",lambda:write(outside))
    test("baselineTcpBind",bind)
    listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        listener.bind(("127.0.0.1",0));listener.listen(2)
        port=listener.getsockname()[1]
        def connect():
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
                s.settimeout(1);s.connect(("127.0.0.1",port))
        test("baselineTcpConnect",connect)
        if out["checks"]["baselineTcpConnect"]["pass"]:
            conn,_=listener.accept();conn.close()
        fd=syscall(444,C.byref(C.create_string_buffer(struct.pack("=QQ",fs,3))),C.c_size_t(16),C.c_uint(0))
        try:
            # Only a disposable working directory is writable. System runtime
            # paths are read/execute allowlisted for this fixed compatibility test.
            # These broad runtime read rules are NOT a production credential boundary.
            def allow(path,rights):
                if not Path(path).exists():return
                d=os.open(path,os.O_PATH|os.O_CLOEXEC)
                try:
                    if not Path(path).is_dir():rights&=~(1<<3)
                    rule=C.create_string_buffer(struct.pack("=Qi",rights,d))
                    syscall(445,C.c_int(fd),C.c_int(1),C.byref(rule),C.c_uint(0))
                finally:os.close(d)
            allow(str(work),fs)
            for p in ("/usr","/bin","/lib","/lib64","/etc/fonts","/etc/ld.so.cache",
                      "/etc/localtime","/etc/nsswitch.conf","/etc/passwd","/etc/group",
                      "/etc/os-release","/dev/null","/dev/zero","/dev/urandom","/dev/random",
                      "/sys/devices/system/cpu"):
                allow(p,read_exec if Path(p).is_dir() else (1<<2))
            # /dev/null discards writes; allow this exact device, not /dev.
            # The two proc entries are public system metadata, never other PIDs.
            out["runtimeRuleResults"]={}
            for label,path,rights in (("devNullWrite","/dev/null",(1<<1)|(1<<2)),
                                      ("procCpuInfo","/proc/cpuinfo",1<<2),
                                      ("procMemInfo","/proc/meminfo",1<<2),
                                      ("opensslConfig","/etc/ssl/openssl.cnf",1<<2)):
                try:
                    allow(path,rights)
                    out["runtimeRuleResults"][label]="RULE_ADDED" if Path(path).exists() else "MISSING"
                except OSError as e:
                    out["runtimeRuleResults"][label]="ERRNO_"+str(e.errno)
            if libc.prctl(C.c_int(38),C.c_ulong(1),C.c_ulong(0),C.c_ulong(0),C.c_ulong(0))!=0:
                raise OSError(C.get_errno(),"no_new_privs")
            out["noNewPrivileges"]=libc.prctl(C.c_int(39),C.c_ulong(0),C.c_ulong(0),C.c_ulong(0),C.c_ulong(0))==1
            syscall(446,C.c_int(fd),C.c_uint(0));out["landlockEnforced"]=True
        finally:os.close(fd)
        test("workspaceRead",lambda:read(allowed))
        test("workspaceWrite",lambda:write(allowed))
        test("outsideReadDenied",lambda:read(outside),True)
        test("outsideWriteDenied",lambda:write(outside),True)
        test("outsideTruncateDenied",lambda:os.truncate(outside,0),True)
        test("tcpBindDenied",bind,True)
        test("tcpConnectDenied",connect,True)
    finally:listener.close()
    needed=("baselineOutsideRead","baselineOutsideWrite","baselineTcpBind","baselineTcpConnect","workspaceRead","workspaceWrite","outsideReadDenied","outsideWriteDenied","outsideTruncateDenied","tcpBindDenied","tcpConnectDenied")
    out["boundaryChecksPassed"]=all(out["checks"].get(n,{}).get("pass") is True for n in needed)
    if not out["boundaryChecksPassed"]:out["status"]="BOUNDARY_TEST_FAILED";return
    os.environ.update({"HOME":str(work),"TMPDIR":str(work),"XDG_CACHE_HOME":str(work/"cache"),"XDG_CONFIG_HOME":str(work/"config")})
    out["restrictedRuntimeAccess"]=runtime_paths()
    out["restrictedNodeStartup"]=node_startup_checks()
    # Confirm the exact runtime exception did not introduce write access.
    def open_for_write(path):
        fd=os.open(path,os.O_WRONLY|os.O_CLOEXEC)
        os.close(fd)
    test("opensslConfigWriteDenied",lambda:open_for_write("/etc/ssl/openssl.cnf"),True)
    out["opensslReadOnlyVerified"]=(out["restrictedRuntimeAccess"].get("opensslConfig")=="ALLOWED"
        and out["checks"]["opensslConfigWriteDenied"]["pass"])
    out["stage"]="restricted_driver_diagnostics"
    # Probe the installed driver's own runtime using only fixed version commands.
    # Do not emit stdout/stderr or filesystem paths in the public receipt.
    try:
        from playwright._impl._driver import compute_driver_executable
        node,cli=compute_driver_executable()
        out["driverVersionChecks"]={}
        out["driverPathChecks"]={}
        for label,path in (("node",node),("cli",cli),("cliDirectory",str(Path(cli).parent)),("cwd",os.getcwd())):
            try:
                if Path(path).is_dir():
                    with os.scandir(path) as entries:next(entries,None)
                else:
                    with open(path,"rb") as stream:stream.read(1)
                out["driverPathChecks"][label]="ALLOWED"
            except OSError as e:out["driverPathChecks"][label]="ERRNO_"+str(e.errno)
        # Return only operation and path classes, never raw stderr or path values.
        def classify_driver_error(raw):
            import re
            msg=raw.decode(errors="replace")
            ops=set(re.findall(r"\b(?:open|readlink|realpath|stat|lstat|scandir|uv_cwd|chdir|access|mkdir|execve)\b",msg,re.I))
            labels=[]
            for label,needle in (("WORKSPACE_PARENT",str(home)+"/"),("PLAYWRIGHT_PACKAGE",str(Path(cli).parent)),
                                 ("PROC_SELF","/proc/self/"),("PROC","/proc/"),("DEV","/dev/"),
                                 ("SYSTEM_RUNTIME","/usr/"),("TEMP","/tmp/")):
                if needle in msg:labels.append(label)
            return {"operations":sorted(ops),"pathClasses":labels}
        commands=[("node",[node,"--version"]),("cli",[node,cli,"--version"])]
        if staged_cli:commands.append(("stagedCli",[node,staged_cli,"--version"]))
        # Fixed JS checks exercise Node's resolver rather than just Python reads.
        js="""const fs=require('fs'),path=require('path');const result={};
const p=process.argv[1];function test(k,fn){try{fn();result[k]={pass:true}}catch(e){result[k]={pass:false,code:typeof e.code==='string'?e.code:'UNKNOWN',syscall:['open','readlink','realpath','stat','lstat','scandir','access','uv_cwd'].includes(e.syscall)?e.syscall:'OTHER'}}}
test('cwd',()=>process.cwd());test('cliRead',()=>fs.readFileSync(p));
test('realpath',()=>fs.realpathSync(p));test('nativeRealpath',()=>fs.realpathSync.native(p));
test('resolveCli',()=>require.resolve(p));test('packageJson',()=>require(path.join(path.dirname(p),'package.json')));
console.log(JSON.stringify(result));"""
        out["nodeModuleChecks"]={}
        for label,target in [("installed",cli),("staged",staged_cli)]:
            if not target:continue
            try:
                run=subprocess.run([node,"-e",js,target],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,timeout=5,check=False)
                if run.returncode==0 and len(run.stdout)<4096:
                    out["nodeModuleChecks"][label]=json.loads(run.stdout)
                else:
                    out["nodeModuleChecks"][label]={"exitCode":run.returncode,
                       "failureCategories":browser_failure(RuntimeError(run.stderr.decode(errors="replace"))),
                       "errorDetails":classify_driver_error(run.stderr)}
            except Exception as e:out["nodeModuleChecks"][label]={"failureCategories":browser_failure(e)}
        for label,cmd in commands:
            try:
                completed=subprocess.run(cmd,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,timeout=5,check=False)
                out["driverVersionChecks"][label]={"exitCode":completed.returncode,
                    "pass":completed.returncode==0,
                    "failureCategories":browser_failure(RuntimeError(completed.stderr.decode(errors="replace"))) if completed.returncode else [],
                    "errorDetails":classify_driver_error(completed.stderr) if completed.returncode else {}}
            except Exception as e:
                out["driverVersionChecks"][label]={"pass":False,"failureCategories":browser_failure(e)}
    except Exception as e:
        out["driverVersionChecks"]={"status":"UNAVAILABLE","failureCategories":browser_failure(e)}
    out["stage"]="restricted_driver_start"
    # Fixed fixture only: no external assets, URLs, candidate bytes or credentials.
    # Native Chromium sandbox is still unavailable on this host.
    with sync_playwright() as p:
        out["stage"]="restricted_browser_launch"
        browser=p.chromium.launch(executable_path=chromium,headless=True,chromium_sandbox=False,timeout=12000,args=launch_args)
        try:
            out["chromiumLaunch"]=True
            out["stage"]="browser_context"
            context=browser.new_context(viewport={"width":640,"height":480},service_workers="block")
            context.route("**/*",lambda route:route.abort())
            page=context.new_page();page.set_default_timeout(4000)
            errors=[];page.on("pageerror",lambda e:errors.append("PAGE_ERROR"))
            out["stage"]="fixture_execution"
            page.set_content("<button id='go' onclick=\"this.textContent='Clicked'\">Go</button><canvas id='c' width='64' height='64'></canvas>")
            out["javascriptPassed"]=page.evaluate("6*7")==42
            page.locator("#go").click();out["interactionPassed"]=page.locator("#go").inner_text()=="Clicked"
            out["webglPassed"]=page.evaluate("""() => {const g=document.querySelector('#c').getContext('webgl2',{preserveDrawingBuffer:true});if(!g)return false;g.clearColor(0.36,0.19,0.76,1);g.clear(g.COLOR_BUFFER_BIT);let p=new Uint8Array(4);g.readPixels(0,0,1,1,g.RGBA,g.UNSIGNED_BYTE,p);return [92,48,194,255].every((v,i)=>Math.abs(v-p[i])<=2)&&g.getError()===g.NO_ERROR;}""")
            out["stage"]="screenshot"
            shot=page.screenshot(timeout=4000);out["screenshotSha256"]=hashlib.sha256(shot).hexdigest()
            out["pageErrors"]=errors
            context.close()
            out["browserChecksPassed"]=all(out.get(k) is True for k in ("chromiumLaunch","javascriptPassed","interactionPassed","webglPassed")) and not errors and bool(shot)
            out["stage"]="complete"
            out["status"]="FIXTURE_COMPATIBLE" if out["browserChecksPassed"] else "FIXTURE_FAILED"
        finally:browser.close()
try:main()
except OSError as e:out["status"]="OS_ERRNO_"+str(e.errno)
except Exception as e:
    out["status"]="BROWSER_OR_RUNTIME_FAILED"
    out["failureCategories"]=browser_failure(e)
    out["failureCategory"]=out["failureCategories"][0]
print(json.dumps(out),flush=True)
'''


def combined_probe():
    import subprocess, tempfile, sys, pwd, signal
    result={"schema":"swrlz-x-combined-v04","status":"UNVERIFIED","candidateExecutionEnabled":False,"isolationVerified":False}
    if not _probe_lock.acquire(blocking=False):
        result["status"]="BUSY";return result
    try:
        with tempfile.TemporaryDirectory(prefix="swrlz-combined-") as home:
            kwargs={}
            if os.geteuid()==0:
                account=pwd.getpwnam("nobody")
                if account.pw_uid==0:return result
                os.chown(home,account.pw_uid,account.pw_gid)
                kwargs={"user":account.pw_uid,"group":account.pw_gid,"extra_groups":[]}
            env={"PATH":"/usr/bin:/bin:/usr/local/bin","HOME":home,"TMPDIR":home,
                 "LANG":"C.UTF-8","PYTHONDONTWRITEBYTECODE":"1"}
            proc=subprocess.Popen([sys.executable,"-I","-c",_COMBINED_CHILD],
                cwd=home,env=env,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,start_new_session=True,**kwargs)
            try:
                raw,_=proc.communicate(timeout=110)
                if proc.returncode or len(raw)>16000:
                    result.update(status="CHILD_FAILED",exitCode=proc.returncode)
                else:
                    data=json.loads(raw)
                    if data.get("schema")==result["schema"]:result=data
            except subprocess.TimeoutExpired:
                result["status"]="TIMEOUT"
            finally:
                # Best-effort process group cleanup; not proof against arbitrary child escapes.
                try:os.killpg(proc.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                proc.communicate()
    except Exception as exc:
        result["status"]="PROBE_INFRASTRUCTURE_"+type(exc).__name__
    finally:_probe_lock.release()
    from pathlib import Path
    result["probeSourceSha256"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return result


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
    gr.Markdown("## Isolation capability probe\nFixed host capability tests, including Landlock file and TCP restrictions. Candidate execution remains disabled.")
    isolation_button = gr.Button("Test execution isolation")
    isolation_result = gr.JSON(label="Isolation capability results")
    isolation_button.click(isolation_probe, outputs=isolation_result, api_name="swrlz_isolation_v03", concurrency_limit=1)
    gr.Markdown("## Combined Landlock browser test v0.4\nTrusted fixture only. This is a compatibility test, not approval for arbitrary project execution.")
    combined_button = gr.Button("Test Chromium under Landlock")
    combined_result = gr.JSON(label="Combined browser restriction results")
    combined_button.click(combined_probe, outputs=combined_result, api_name="swrlz_combined_v04", concurrency_limit=1)
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
