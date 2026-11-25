#!/usr/bin/env python3
"""Free, dedicated HF browser worker first; production integration only after sandbox proof."""
import argparse,ast,hashlib,io,json,os,sys,time,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from api.browser_worker_protocol_v1 import derive_key
from api.html_project_browser_client_v1 import validate
SPACE="kamiloki/Swyrlz"
WORKER="kamiloki/swrlz-browser-worker"
RUNTIME="html_project_agent_runtime_v1.py"
APPROVAL="html_project_repair_v1.py"
UI="chat/§wyrlz/assets/html-project-publish-review-v1.js"
CLIENT="html_project_browser_client_v1.py"
PROTOCOL="browser_worker_protocol_v1.py"
STATION="station.py"
PINS={RUNTIME:"cecc698cd7d193b68e20aef5a82fc9f32c42f35a",APPROVAL:"f5a0902dc73f3aa7ad51b27f9f929d07d41fac76",UI:"ce20a8b6573a6d2d32eadaa0fe100015c6ad8c06"}
LOCAL={RUNTIME:Path("api")/RUNTIME,APPROVAL:Path("api")/APPROVAL,
       UI:Path("chat/html-project-publish-review-v1.js"),CLIENT:Path("api")/CLIENT,PROTOCOL:Path("api")/PROTOCOL}
MARK="# swrlz-server-browser-route-v13"
CHECK="https://kamiloki-swyrlz.hf.space/api/html-project-agent-v13/runtime-check"
PROBE='''
# swrlz-server-browser-route-v13
import threading as _swrlz_v13_threading
_swrlz_v13_probe_lock=_swrlz_v13_threading.Lock()
_swrlz_v13_probe_receipt=None
@app.get("/api/html-project-agent-v13/runtime-check",include_in_schema=False)
def _swrlz_server_browser_v13_health():
    global _swrlz_v13_probe_receipt
    if _swrlz_v13_probe_receipt is not None:return _swrlz_v13_probe_receipt
    if not _swrlz_v13_probe_lock.acquire(blocking=False):return {"state":"running"}
    try:
        return _swrlz_v13_probe_once()
    finally:_swrlz_v13_probe_lock.release()

def _swrlz_v13_probe_once():
    global _swrlz_v13_probe_receipt
    import html_project_browser_client_v1 as browser
    active=_swrlz_verified_repair_runtime_v7()
    import inspect
    if "browser_validator" not in inspect.signature(active.run).parameters:
        raise RuntimeError("SERVER_BROWSER_ROUTE_NOT_ACTIVE")
    # Fixed, credential-free source fixture; no caller-controlled execution.
    receipt=browser.validate("route-smoke",{"index.html":"<html><body><p>Server browser ready</p></body></html>"})["receipt"]
    if receipt.get("browserVerified") is not True or receipt.get("sandbox") is not True:
        raise RuntimeError("SERVER_BROWSER_ROUNDTRIP_FAILED")
    _swrlz_v13_probe_receipt={"schema":"swrlz-server-browser-v13","routeActive":True,
            "browserConfigured":bool(__import__("os").environ.get("SWRLZ_BROWSER_WORKER_KEY")),
            "browserRoundtrip":True,"approvalRequired":True}
    return _swrlz_v13_probe_receipt
'''
def blob(raw):return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def patch_station(s):
    if MARK in s:
        if s.count(MARK)!=1 or "browser_validator=_swrlz_server_browser_validate" not in s:raise RuntimeError("V13_PARTIAL_STATION")
        ast.parse(s);return s
    anchor="    yield from active.run(payload, coder_generate)"
    if s.count(anchor)!=1:raise RuntimeError("V13_STATION_ROUTE_DRIFT")
    s=s.replace(anchor,'    from html_project_browser_client_v1 import validate as _swrlz_server_browser_validate\n    yield from active.run(payload, coder_generate, browser_validator=_swrlz_server_browser_validate)',1)
    anchor2="def _swrlz_execute_model_repair_v7("
    if s.count(anchor2)!=1:raise RuntimeError("V13_STATION_PROBE_DRIFT")
    s=s.replace(anchor2,PROBE+"\n"+anchor2,1);ast.parse(s);return s
def worker_files():
    root=Path("browser-worker")
    return {n:(root/n).read_bytes() for n in ("README.md","Dockerfile","render.py","render_entry.py","service.py")}|{PROTOCOL:LOCAL[PROTOCOL].read_bytes()}
def worker_test(key):
    fixture={"index.html": """<html><body><button id="go" onclick="document.querySelector('#out').textContent='ok'">Go</button><p id="out">old</p></body></html>"""}
    good=validate("worker-smoke",fixture,False,[{"op":"click","selector":"#go"},{"op":"text","selector":"#out","text":"ok"}],key=key)["receipt"]
    if good.get("browserVerified") is not True or len(good.get("checks",[]))!=2:raise RuntimeError("SERVER_BROWSER_INTERACTION_FAILED")
    bad=validate("worker-smoke",{"index.html":"<html><body><script>throw new Error('v13 fixture')</script></body></html>"},False,key=key)["receipt"]
    if bad.get("browserVerified") is not False or not any(i.get("code")=="BROWSER_PAGE_ERROR" for i in bad.get("issues",[])):raise RuntimeError("SERVER_BROWSER_ERROR_NOT_DETECTED")
    project=Path("html-projects/interactive-3d-model-viewer")
    files={f.relative_to(project).as_posix():f.read_text() for f in project.rglob("*") if f.is_file()}
    viewer=validate("interactive-3d-model-viewer",files,True,[{"op":"uncheck","selector":"#light-toggle"},{"op":"check","selector":"#wireframe-toggle"},{"op":"click","selector":"#reset-btn"},{"op":"unchecked","selector":"#wireframe-toggle"}],key=key)["receipt"]
    if viewer.get("browserVerified") is not True or viewer.get("canvasCount",0)<1:raise RuntimeError("SERVER_BROWSER_VIEWER_FAILED:"+repr(viewer.get("issues")))
    print("V13_WORKER_REAL_INTERACTIONS_PASS",json.dumps({"fixture":good["screenshotSha256"],"viewer":viewer["screenshotSha256"],"sandbox":True}),flush=True)
def main(mode):
    if mode=="selftest":
        fixture="def _swrlz_execute_model_repair_v7(payload, coder_generate):\n    active=None\n    yield from active.run(payload, coder_generate)\n"
        assert patch_station(patch_station(fixture))==patch_station(fixture)
        for path in LOCAL.values():
            if path.suffix==".py":ast.parse(path.read_bytes())
        for n,v in worker_files().items():
            if n.endswith(".py"):ast.parse(v)
        print("V13_SELFTEST_PASS");return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    from huggingface_hub.errors import RepositoryNotFoundError
    token=os.getenv("HF_TOKEN") or None;api=HfApi(token=token)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    names=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    def read(space,name,revision):
        return Path(hf_hub_download(space,name,repo_type="space",revision=revision,token=token)).read_bytes()
    original={n:read(SPACE,n,rev) for n in (*LOCAL,STATION) if n in names}
    candidate={n:p.read_bytes() for n,p in LOCAL.items()}
    if mode=="preflight" and b"/api/html-project-browser-v14/render" in candidate[CLIENT]:
        if b"swrlz-evidence-tool-loop-v12" not in original[RUNTIME]:
            raise RuntimeError("V14_LINEAGE_MISMATCH")
        print("V13_HISTORICAL_PREFLIGHT_LOCAL_BROWSER_OWNS_RELEASE",rev,flush=True);return
    for n in LOCAL:
        if n not in original:
            if n not in (CLIENT,PROTOCOL):raise RuntimeError("V13_SOURCE_MISSING:"+n)
        elif original[n]!=candidate[n] and (n not in PINS or blob(original[n])!=PINS[n]):
            raise RuntimeError("V13_SOURCE_DRIFT:"+n)
    candidate[STATION]=patch_station(original[STATION].decode()).encode()
    changed={n:v for n,v in candidate.items() if original.get(n)!=v}
    print("V13_PREFLIGHT",rev,sorted(changed),flush=True)
    if mode=="preflight":return
    if mode!="publish" or not token or os.getenv("SWRLZ_V13_APPROVED")!="1":raise PermissionError("V13_RELEASE_NOT_APPROVED")
    key=derive_key(token)
    def add(n,v):return CommitOperationAdd(path_in_repo=n,path_or_fileobj=io.BytesIO(v))
    # Public worker implementation only; all render requests are authenticated.
    # Never put source projects, credentials, or render results into this repo.
    try:info=api.repo_info(WORKER,repo_type="space")
    except RepositoryNotFoundError:
        api.create_repo(WORKER,repo_type="space",space_sdk="docker",private=False,exist_ok=True)
        info=api.repo_info(WORKER,repo_type="space")
    status=api.get_space_runtime(WORKER)
    if str(status.hardware or "").lower() not in ("cpu-basic","spacehardware.cpu_basic","none","") or str(getattr(status,"requested_hardware",None) or "").lower() not in ("cpu-basic","spacehardware.cpu_basic","none",""):
        raise RuntimeError("WORKER_FREE_CPU_REQUIRED")
    wr=str(info.sha)
    files=worker_files()
    wn=set(api.list_repo_files(WORKER,repo_type="space",revision=wr))
    if wn-set(files)-{".gitattributes"}:raise RuntimeError("WORKER_EXISTING_SOURCE_NOT_OWNED")
    changes={n:v for n,v in files.items() if n not in wn or read(WORKER,n,wr)!=v}
    api.add_space_secret(WORKER,"SWRLZ_BROWSER_WORKER_KEY",key)
    if changes:
        info=api.repo_info(WORKER,repo_type="space")
        wcommit=api.create_commit(repo_id=WORKER,repo_type="space",parent_commit=str(info.sha),
            operations=[add(n,v) for n,v in changes.items()],commit_message="§C: isolated authenticated Chromium worker").oid
        print("V13_WORKER_COMMIT",wcommit,flush=True)
    for i in range(75):
        try:worker_test(key);break
        except RuntimeError as exc:
            if str(exc).startswith(("SERVER_BROWSER_INTERACTION_FAILED","SERVER_BROWSER_ERROR_NOT_DETECTED","SERVER_BROWSER_VIEWER_FAILED","CHROMIUM_SANDBOX")):raise
            if i==74:raise
            if i%5==0:print("V13_WORKER_PENDING",i,type(exc).__name__,str(exc)[:120],flush=True)
            time.sleep(8)
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:raise RuntimeError("MAIN_SPACE_CHANGED_REPREPARE")
    api.add_space_secret(SPACE,"SWRLZ_BROWSER_WORKER_KEY",key)
    if changed:
        new=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
            operations=[add(n,v) for n,v in changed.items()],commit_message="§C v13: server browser validation before approval").oid
        print("V13_MAIN_COMMIT",new,flush=True)
    else:new=rev
    try:
        for n,v in candidate.items():
            if read(SPACE,n,new)!=v:raise RuntimeError("V13_READBACK_MISMATCH:"+n)
        for i in range(75):
            try:
                with urllib.request.urlopen(CHECK,timeout=70) as r:rec=json.load(r)
                if rec!={"schema":"swrlz-server-browser-v13","routeActive":True,"browserConfigured":True,"browserRoundtrip":True,"approvalRequired":True}:raise RuntimeError("V13_NOT_READY")
                print("V13_DEPLOYED_VERIFIED",new,json.dumps(rec),flush=True);return
            except (OSError,ValueError,RuntimeError):
                if i==74:raise
                time.sleep(8)
    except Exception:
        if changed and str(api.repo_info(SPACE,repo_type="space").sha)==new:
            restored=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new,
              operations=[add(n,original[n]) if n in original else CommitOperationDelete(path_in_repo=n) for n in changed],
              commit_message="rollback §C server browser route").oid
            print("V13_ROLLBACK",restored,flush=True)
        raise
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("selftest","preflight","publish"));main(p.parse_args().mode)
