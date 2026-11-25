"""Deploy authenticated fixed diagnostic, then add a gated §C roundtrip route.

No arbitrary candidate execution or browser-backend activation in this release.
"""
import ast,io,os,sys,time
from pathlib import Path
from huggingface_hub import HfApi, CommitOperationAdd, CommitOperationDelete, hf_hub_download
from x_diagnostic_client import derive_key, diagnose, station_diagnose, request_data, call_gradio, DiagnosticUnavailable
ROOT=Path(__file__).resolve().parent
X="kamiloki/swrlz-execution"
C="kamiloki/Swyrlz"
KEY="SWRLZ_X_DIAGNOSTIC_KEY"
MODULE="x_diagnostic_client.py"
STATION="station.py"
MARK="# swrlz-x-fixed-diagnostic-v1"
ANCHOR="def _swrlz_execute_model_repair_v7("
ROUTE=r'''
# swrlz-x-fixed-diagnostic-v1
from fastapi import Header as _swrlz_x_header, HTTPException as _swrlz_x_http_error
import threading as _swrlz_x_threading
_swrlz_x_lock = _swrlz_x_threading.Lock()
_swrlz_x_seen = {}

@app.post("/api/swrlz-x/v1/diagnostics", include_in_schema=False)
def _swrlz_x_diagnostic_route(
    raw: str = _swrlz_x_header(default="", alias="X-Swrlz-X-Request"),
    signature: str = _swrlz_x_header(default="", alias="X-Swrlz-X-Signature"),
):
    import os, json, hmac, re, time
    import x_diagnostic_client as x
    key = os.environ.get(x.KEY_NAME, "")
    if len(key) != 64 or len(raw) > 512 or len(signature) != 64 or not hmac.compare_digest(x.mac(key,"station-request",raw.encode()),signature):
        raise _swrlz_x_http_error(403,"DIAGNOSTIC_DENIED")
    try:
        obj=json.loads(raw); now=int(time.time())
        if set(obj)!={"schema","nonce","timestamp"} or obj["schema"]!=x.SCHEMA or not re.fullmatch(r"[0-9a-f]{32}",obj["nonce"]) or type(obj["timestamp"]) is not int or abs(now-obj["timestamp"])>120:
            raise ValueError()
    except (ValueError,TypeError,KeyError):
        raise _swrlz_x_http_error(400,"DIAGNOSTIC_INVALID")
    if not _swrlz_x_lock.acquire(blocking=False):
        raise _swrlz_x_http_error(429,"DIAGNOSTIC_BUSY")
    try:
        for n in list(_swrlz_x_seen):
            if now-_swrlz_x_seen[n]>241: del _swrlz_x_seen[n]
        if obj["nonce"] in _swrlz_x_seen or len(_swrlz_x_seen)>=256:
            raise _swrlz_x_http_error(409,"DIAGNOSTIC_REPLAY")
        _swrlz_x_seen[obj["nonce"]]=now
        try:
            receipt=x.diagnose(key)
        except Exception:
            raise _swrlz_x_http_error(503,"X_DIAGNOSTIC_UNAVAILABLE")
        response={"schema":x.SCHEMA,"nonce":obj["nonce"],"receipt":receipt,"backendActivated":False}
        return {**response,"signature":x.mac(key,"station-receipt",x.wire(response))}
    finally:
        _swrlz_x_lock.release()

'''
def patch_station(text):
    if MARK in text:
        if text.count(MARK)!=1 or text.count('def _swrlz_x_diagnostic_route(')!=1:
            raise RuntimeError("PARTIAL_EXISTING_ROUTE")
        if ROUTE.strip() not in text:
            raise RuntimeError("EXISTING_ROUTE_DRIFT")
        ast.parse(text);return text
    if text.count(ANCHOR)!=1:raise RuntimeError("STATION_ROUTE_ANCHOR_DRIFT")
    text=text.replace(ANCHOR,ROUTE+"\n"+ANCHOR,1)
    ast.parse(text)
    return text

def selftest():
    for name in ("app.py",MODULE,Path(__file__).name):
        ast.parse((ROOT/name).read_bytes())
    fixture="def _swrlz_execute_model_repair_v7():\n    pass\n"
    assert patch_station(patch_station(fixture))==patch_station(fixture)
    print("X_DIAGNOSTIC_SOURCE_VALIDATED",flush=True)

def wait_for(label,fn,attempts=36):
    for attempt in range(attempts):
        try:return fn()
        except Exception as exc:
            if attempt==attempts-1:raise RuntimeError(label+"_UNVERIFIED:"+type(exc).__name__) from None
            if attempt%4==0:print(label+"_PENDING",attempt,type(exc).__name__,flush=True)
            time.sleep(10)

def publish():
    token=os.environ.get("HF_TOKEN","")
    key=derive_key(token)
    api=HfApi(token=token)
    def rev(space):return str(api.repo_info(space,repo_type="space").sha)
    def names(space,r):return set(api.list_repo_files(space,repo_type="space",revision=r))
    def read(space,n,r):return Path(hf_hub_download(space,n,repo_type="space",revision=r,token=token)).read_bytes()
    def add(n,v):return CommitOperationAdd(path_in_repo=n,path_or_fileobj=io.BytesIO(v))
    def write(space,r,files,message):
        existing=names(space,r)
        changed={n:v for n,v in files.items() if n not in existing or read(space,n,r)!=v}
        new=r
        if changed:
            new=api.create_commit(repo_id=space,repo_type="space",revision="main",parent_commit=r,operations=[add(n,v) for n,v in changed.items()],commit_message=message).oid
        for n,v in files.items():
            if read(space,n,new)!=v:raise RuntimeError("READBACK_MISMATCH:"+n)
        return new,changed
    xfiles={n:(ROOT/n).read_bytes() for n in ("app.py","packages.txt","requirements.txt")}
    api.add_space_secret(X,KEY,key)
    xr,_=write(X,rev(X),xfiles,"§X: signed fixed Chromium diagnostic")
    print("X_SOURCE_READBACK_PASS",xr,flush=True)
    good=wait_for("X_REMOTE",lambda:diagnose(key))
    print("X_SIGNED_REMOTE_PASS",good["diagnostics"]["screenshot_sha256"],flush=True)
    # Negative: invalid signature must cause a completed remote rejection,
    # not merely an HTTP/network failure.
    _,raw,_=request_data(key)
    try:
        call_gradio(raw,"0"*64)
    except DiagnosticUnavailable as exc:
        if str(exc)!="X_REMOTE_REJECTED":raise
    else:raise RuntimeError("UNAUTHORIZED_REQUEST_ACCEPTED")
    print("X_INVALID_SIGNATURE_REJECTED",flush=True)
    # Only now touch the shared §C/§E Space. Preserve current source and use CAS.
    cr=rev(C); existing=names(C,cr)
    original={n:read(C,n,cr) for n in (STATION,MODULE) if n in existing}
    if STATION not in original:raise RuntimeError("STATION_SOURCE_MISSING")
    module=(ROOT/MODULE).read_bytes()
    if MODULE in original and original[MODULE]!=module:raise RuntimeError("DIAGNOSTIC_MODULE_COLLISION")
    candidate={MODULE:module,STATION:patch_station(original[STATION].decode()).encode()}
    if rev(C)!=cr:raise RuntimeError("STATION_CONCURRENT_CHANGE")
    api.add_space_secret(C,KEY,key)
    new,changed=write(C,cr,candidate,"§C: authenticated fixed §X diagnostic roundtrip only")
    print("C_SOURCE_READBACK_PASS",new,flush=True)
    try:
        result=wait_for("C_TO_X",lambda:station_diagnose(key))
        print("C_TO_X_SIGNED_ROUNDTRIP_PASS",result["receipt"]["diagnostics"]["screenshot_sha256"],flush=True)
    except Exception:
        if changed and rev(C)==new:
            restored=api.create_commit(repo_id=C,repo_type="space",revision="main",parent_commit=new,operations=[add(n,original[n]) if n in original else CommitOperationDelete(path_in_repo=n) for n in changed],commit_message="Rollback unverified §X diagnostic route").oid
            print("C_SOURCE_ROLLBACK",restored,flush=True)
        raise

if __name__=="__main__":
    selftest()
    if sys.argv[1:]==["publish"]:publish()
    elif sys.argv[1:]:raise SystemExit("unknown mode")
