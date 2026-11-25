"""Single-Space browser worker: strict OS isolation before any project executes.

A fresh bubblewrap user/mount/pid/network namespace is mandatory. No project
code executes on the chat process or in an unsandboxed Chromium instance.
Only the interpreter, installed browser, trusted helper code, and selected
Playwright package paths are mapped. No project/credential mounts.
"""
from __future__ import annotations
import importlib.util,json,os,signal,subprocess,sys,tempfile,threading,time,shutil
from pathlib import Path
try:
    from browser_worker_protocol_v1 import validate_request,encode,file_hashes,verify_envelope,mac,VERSION,MAX_BODY
except ImportError:
    from api.browser_worker_protocol_v1 import validate_request,encode,file_hashes,verify_envelope,mac,VERSION,MAX_BODY
ROOT=Path(__file__).resolve().parent
BUSY=threading.Lock()
REPLAY_LOCK=threading.Lock()
SEEN={}
class LocalBrowserError(RuntimeError):pass

def namespace_ids():
    return {n:os.readlink("/proc/self/ns/"+n) for n in ("user","mnt","pid","net","ipc","uts")}

def command():
    bwrap=shutil.which("bwrap")
    chromium=shutil.which("chromium")
    interpreter=Path(sys.executable).resolve()
    if not bwrap or not chromium or not interpreter.is_relative_to("/usr"):
        raise LocalBrowserError("LOCAL_BROWSER_REQUIRED_SYSTEM_PACKAGES_UNAVAILABLE")
    if not Path(chromium).resolve().is_relative_to("/usr"):
        raise LocalBrowserError("LOCAL_BROWSER_UNTRUSTED_BINARY_PATH")
    args=[bwrap,"--unshare-all","--die-with-parent","--new-session","--cap-drop","ALL",
          "--clearenv","--ro-bind","/usr","/usr"]
    for path in ("/lib","/lib64","/bin"):
        if Path(path).exists():args.extend(["--ro-bind",path,path])
    args.extend(["--proc","/proc","--dev","/dev","--tmpfs","/tmp","--dir","/home",
                 "--dir","/home/browser","--dir","/etc","--dir","/worker","--dir","/deps"])
    for path in ("/etc/fonts","/etc/ld.so.cache","/etc/localtime","/etc/chromium.d"):
        if Path(path).exists():args.extend(["--ro-bind",path,path])
    for name in ("browser_worker_protocol_v1.py","html_project_local_browser_render_v1.py","html_project_local_browser_entry_v1.py"):
        path=ROOT/name
        if not path.is_file() or path.is_symlink():raise LocalBrowserError("LOCAL_BROWSER_TRUSTED_SOURCE_MISSING")
        args.extend(["--ro-bind",str(path),"/worker/"+name])
    for name in ("playwright","greenlet","pyee","typing_extensions"):
        spec=importlib.util.find_spec(name)
        if spec is None or not spec.origin:raise LocalBrowserError("LOCAL_BROWSER_PYTHON_DEPENDENCY_MISSING:"+name)
        path=Path(spec.origin).resolve()
        if spec.submodule_search_locations:
            path=path.parent;dest="/deps/"+name
        else:dest="/deps/"+path.name
        args.extend(["--ro-bind",str(path),dest])
    args.extend(["--setenv","PATH","/usr/local/bin:/usr/bin:/bin","--setenv","HOME","/home/browser",
                 "--setenv","TMPDIR","/tmp","--setenv","LANG","C.UTF-8",
                 "--setenv","SWRLZ_CHROMIUM_EXECUTABLE",chromium,
                 "--chdir","/home/browser","--",str(interpreter),"-I","/worker/html_project_local_browser_entry_v1.py"])
    return args

def run_isolated(obj):
    validate_request(obj)
    if not BUSY.acquire(blocking=False):raise LocalBrowserError("LOCAL_BROWSER_BUSY")
    try:
        args=command()
        raw=encode({"request":obj,"parentNamespaces":namespace_ids()})
        # The parent never gives the child its inherited secrets or cwd.
        with tempfile.TemporaryDirectory(prefix="swrlz-browser-") as tmp:
            proc=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                cwd=tmp,env={"PATH":"/usr/local/bin:/usr/bin:/bin","LANG":"C.UTF-8"},start_new_session=True)
            try:out,err=proc.communicate(raw,timeout=48)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL);proc.communicate()
                raise LocalBrowserError("LOCAL_BROWSER_TIMEOUT")
        if proc.returncode:
            # Only report a bounded isolation diagnostic, not project content.
            reason=err.decode(errors="replace").splitlines()
            raise LocalBrowserError("LOCAL_BROWSER_NAMESPACE_UNAVAILABLE: "+(reason[0][:180] if reason else "child exit "+str(proc.returncode)))
        if len(out)>80_000:raise LocalBrowserError("LOCAL_BROWSER_RESPONSE_LIMIT")
        try:receipt=json.loads(out)
        except ValueError as exc:raise LocalBrowserError("LOCAL_BROWSER_INVALID_RESPONSE") from exc
        if (receipt.get("isolationVerified") is not True or receipt.get("sandbox") is not True
                or receipt.get("infrastructureError")):
            raise LocalBrowserError(str(receipt.get("infrastructureError") or "LOCAL_BROWSER_ISOLATION_UNVERIFIED"))
        return receipt
    finally:BUSY.release()

def validate_local(project,files,canvas=False,checks=None,*,key=None):
    import secrets
    key=key or os.getenv("SWRLZ_BROWSER_WORKER_KEY","")
    if len(key)!=64:raise LocalBrowserError("LOCAL_BROWSER_SIGNING_KEY_UNAVAILABLE")
    obj={"schema":VERSION,"nonce":secrets.token_hex(16),"timestamp":int(time.time()),
         "project":project,"files":files,"canvas":bool(canvas),"checks":checks or []}
    receipt=run_isolated(obj)
    envelope={"receipt":receipt,"signature":mac(key,"receipt",encode(receipt))}
    verify_envelope(key,envelope,project=project,hashes=file_hashes(files),nonce=obj["nonce"],max_age=180)
    return envelope

def install(app):
    """Authenticated delivery-only bridge; local model calls bypass HTTP."""
    from fastapi import Request
    from fastapi.responses import JSONResponse
    from starlette.concurrency import run_in_threadpool
    import hmac
    # FastAPI resolves postponed annotations in this module's globals.
    globals()["Request"]=Request
    @app.post("/api/html-project-browser-v14/render",include_in_schema=False)
    async def browser_delivery(request:Request):
        key=os.getenv("SWRLZ_BROWSER_WORKER_KEY","")
        if len(key)!=64 or not hmac.compare_digest(mac(key,"admission",b""),request.headers.get("x-swrlz-admission","")):
            return JSONResponse({"error":"AUTH_REQUIRED"},status_code=401)
        try:
            length=int(request.headers.get("content-length","0"))
            if not 0<length<=MAX_BODY:return JSONResponse({"error":"BODY_LIMIT"},status_code=413)
            raw=bytearray()
            async for chunk in request.stream():
                raw.extend(chunk)
                if len(raw)>MAX_BODY:return JSONResponse({"error":"BODY_LIMIT"},status_code=413)
            raw=bytes(raw)
            if len(raw)!=length or not hmac.compare_digest(mac(key,"request",raw),request.headers.get("x-swrlz-signature","")):
                return JSONResponse({"error":"BAD_SIGNATURE"},status_code=401)
            obj=validate_request(json.loads(raw))
            now=time.time()
            with REPLAY_LOCK:
                for nonce,stamp in list(SEEN.items()):
                    if stamp<now-180:del SEEN[nonce]
                if obj["nonce"] in SEEN:return JSONResponse({"error":"REPLAY"},status_code=409)
                if len(SEEN)>=128:return JSONResponse({"error":"REPLAY_LIMIT"},status_code=429)
                SEEN[obj["nonce"]]=now
            receipt=await run_in_threadpool(run_isolated,obj)
            return JSONResponse({"receipt":receipt,"signature":mac(key,"receipt",encode(receipt))},
                                headers={"Cache-Control":"no-store"})
        except (ValueError,TypeError,KeyError):
            return JSONResponse({"error":"INVALID_REQUEST"},status_code=400)
        except LocalBrowserError:
            return JSONResponse({"error":"LOCAL_BROWSER_UNAVAILABLE"},status_code=503)
