#!/usr/bin/env python3
"""Install local sandbox in existing Gradio Space; verify before accepting release."""
import argparse,ast,hashlib,io,json,os,sys,time,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from api.browser_worker_protocol_v1 import derive_key
from api.html_project_browser_client_v1 import validate
from scripts.hf_chat_server_browser_release_v13 import PINS, LOCAL as PREVIOUS_LOCAL, worker_test
SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
CHECK=BASE+"/api/html-project-agent-v14/runtime-check"
STATION="station.py"
MARK="# swrlz-local-browser-route-v14"
LOCAL=dict(PREVIOUS_LOCAL)
LOCAL.update({
 "html_project_local_browser_v1.py":Path("api/html_project_local_browser_v1.py"),
 "html_project_local_browser_entry_v1.py":Path("api/html_project_local_browser_entry_v1.py"),
 "html_project_local_browser_render_v1.py":Path("api/html_project_local_browser_render_v1.py")})
PROBE='''
# swrlz-local-browser-route-v14
import html_project_local_browser_v1 as _swrlz_local_browser_v14
import threading as _swrlz_v14_threading
_swrlz_local_browser_v14.install(app)
_swrlz_v14_lock=_swrlz_v14_threading.Lock()
_swrlz_v14_result=None
@app.get("/api/html-project-agent-v14/runtime-check",include_in_schema=False)
def _swrlz_v14_health():
    global _swrlz_v14_result
    if _swrlz_v14_result is not None:return _swrlz_v14_result
    if not _swrlz_v14_lock.acquire(blocking=False):return {"state":"running"}
    try:
        active=_swrlz_verified_repair_runtime_v7()
        import inspect
        if "browser_validator" not in inspect.signature(active.run).parameters:
            raise RuntimeError("V14_RUNTIME_NOT_ACTIVE")
        good=_swrlz_local_browser_v14.validate_local("local-route-smoke",
              {"index.html":"<html><body><p>Browser ready</p></body></html>"})["receipt"]
        if good.get("browserVerified") is not True or good.get("isolationVerified") is not True:
            raise RuntimeError("V14_ISOLATION_NOT_VERIFIED")
        _swrlz_v14_result={"schema":"swrlz-local-browser-v14","state":"passed","routeActive":True,
                         "isolationVerified":True,"sandbox":True,"approvalRequired":True}
    except Exception as exc:
        _swrlz_v14_result={"schema":"swrlz-local-browser-v14","state":"failed",
                         "error":str(exc)[:220]}
    finally:_swrlz_v14_lock.release()
    return _swrlz_v14_result
'''
def blob(raw):return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def patch_station(s):
    if MARK in s:
        if s.count(MARK)!=1 or "browser_validator=_swrlz_local_browser_v14.validate_local" not in s:raise RuntimeError("V14_PARTIAL_STATION")
        ast.parse(s);return s
    anchor="    yield from active.run(payload, coder_generate)"
    if s.count(anchor)!=1:raise RuntimeError("V14_STATION_ROUTE_DRIFT")
    s=s.replace(anchor,"    yield from active.run(payload, coder_generate, browser_validator=_swrlz_local_browser_v14.validate_local)",1)
    anchor2="def _swrlz_execute_model_repair_v7("
    if s.count(anchor2)!=1:raise RuntimeError("V14_STATION_PROBE_DRIFT")
    s=s.replace(anchor2,PROBE+"\n"+anchor2,1);ast.parse(s);return s
def append_lines(raw,lines):
    text=raw.decode()
    existing={line.strip() for line in text.splitlines()}
    for line in lines:
        if line not in existing:text=text.rstrip()+"\n"+line+"\n"
    return text.encode()
def selftest():
    fixture="def _swrlz_execute_model_repair_v7(payload, coder_generate):\n    active=None\n    yield from active.run(payload, coder_generate)\n"
    assert patch_station(patch_station(fixture))==patch_station(fixture)
    for p in LOCAL.values():
        if p.suffix==".py":ast.parse(p.read_bytes())
    assert append_lines(b"a\n",["a","b"])==b"a\nb\n"
    print("V14_SELFTEST_PASS",flush=True)
def main(mode):
    selftest()
    if mode=="selftest":return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    token=os.getenv("HF_TOKEN") or None;api=HfApi(token=token)
    info=api.repo_info(SPACE,repo_type="space");rev=str(info.sha)
    names=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    def read(n,r):return Path(hf_hub_download(SPACE,n,repo_type="space",revision=r,token=token)).read_bytes()
    original={n:read(n,rev) for n in (*LOCAL,STATION,"requirements.txt","packages.txt") if n in names}
    candidate={n:p.read_bytes() for n,p in LOCAL.items()}
    for n in LOCAL:
        if n in PINS:
            if n not in original or (original[n]!=candidate[n] and blob(original[n])!=PINS[n]):
                raise RuntimeError("V14_SOURCE_DRIFT:"+n)
        elif n in original and original[n]!=candidate[n]:
            raise RuntimeError("V14_NEW_PATH_COLLISION:"+n)
    candidate[STATION]=patch_station(original[STATION].decode()).encode()
    req=original.get("requirements.txt",b"")
    for line in req.decode().splitlines():
        if line.strip().lower().startswith("playwright") and line.strip()!="playwright==1.51.0":
            raise RuntimeError("V14_EXISTING_PLAYWRIGHT_PIN_CONFLICT")
    candidate["requirements.txt"]=append_lines(req,["playwright==1.51.0"])
    candidate["packages.txt"]=append_lines(original.get("packages.txt",b""),["bubblewrap","chromium","fonts-liberation"])
    changed={n:v for n,v in candidate.items() if original.get(n)!=v}
    print("V14_PREFLIGHT",rev,sorted(changed),flush=True)
    if mode=="preflight":return
    if mode!="publish" or not token or os.getenv("SWRLZ_V14_APPROVED")!="1":raise PermissionError("V14_NOT_APPROVED")
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:raise RuntimeError("V14_CONCURRENT_SOURCE_CHANGE")
    key=derive_key(token)
    api.add_space_secret(SPACE,"SWRLZ_BROWSER_WORKER_KEY",key)
    def add(n,v):return CommitOperationAdd(path_in_repo=n,path_or_fileobj=io.BytesIO(v))
    if changed:
        new=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
            operations=[add(n,v) for n,v in changed.items()],commit_message="§C v14: isolated browser on existing Space").oid
    else:new=rev
    print("V14_SPACE_COMMIT",new,flush=True)
    try:
        for n,v in candidate.items():
            if read(n,new)!=v:raise RuntimeError("V14_READBACK_MISMATCH:"+n)
        for i in range(90):
            try:
                with urllib.request.urlopen(CHECK,timeout=70) as r:rec=json.load(r)
                if rec.get("schema")=="swrlz-local-browser-v14" and rec.get("state")=="failed":
                    raise ValueError("V14_HOST_ISOLATION_FAILED:"+repr(rec))
                if rec!={"schema":"swrlz-local-browser-v14","state":"passed","routeActive":True,
                         "isolationVerified":True,"sandbox":True,"approvalRequired":True}:
                    raise RuntimeError("V14_NOT_READY")
                break
            except ValueError:raise
            except (OSError,RuntimeError) as exc:
                if i==89:raise
                if i%5==0:print("V14_PENDING",i,type(exc).__name__,flush=True)
                time.sleep(8)
        # Same authenticated protocol used by post-publication verification.
        worker_test(key)
        print("V14_DEPLOYED_VERIFIED",new,json.dumps(rec),flush=True)
    except Exception:
        if changed and str(api.repo_info(SPACE,repo_type="space").sha)==new:
            restored=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new,
                operations=[add(n,original[n]) if n in original else CommitOperationDelete(path_in_repo=n) for n in changed],
                commit_message="rollback §C v14: browser isolation not verified").oid
            print("V14_ROLLBACK",restored,flush=True)
        raise
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("selftest","preflight","publish"))
    main(p.parse_args().mode)
