#!/usr/bin/env python3
"""Probe existing Space after explicit restart, then activate only after sandbox proof."""
import argparse,ast,hashlib,io,json,os,re,sys,time,urllib.error,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import hf_chat_local_browser_release_v14 as v14
from api.browser_worker_protocol_v1 import derive_key
from scripts.hf_chat_server_browser_release_v13 import worker_test
SPACE=v14.SPACE
BASE=v14.BASE
PROBE_PATH="/api/html-project-agent-v15/startup-check"
MARK="# swrlz-startup-isolation-probe-v15"
STATION="station.py"
PROBE='''
# swrlz-startup-isolation-probe-v15
import threading as _swrlz_v15_threading
_swrlz_v15_lock=_swrlz_v15_threading.Lock()
_swrlz_v15_cached=None
@app.get("/api/html-project-agent-v15/startup-check",include_in_schema=False)
def _swrlz_v15_startup_check():
    global _swrlz_v15_cached
    if _swrlz_v15_cached is not None:return _swrlz_v15_cached
    if not _swrlz_v15_lock.acquire(blocking=False):return {"schema":"swrlz-startup-v15","state":"running"}
    import importlib.util,shutil
    facts={"chromium":bool(shutil.which("chromium")),"bubblewrap":bool(shutil.which("bwrap")),
           "playwright":importlib.util.find_spec("playwright") is not None}
    try:
        if not all(facts.values()):raise RuntimeError("REQUIRED_BROWSER_PACKAGES_UNAVAILABLE")
        import html_project_local_browser_v1 as local
        result=local.validate_local("startup-fixture",{"index.html":"<html><body><p>Local browser probe</p></body></html>"},key="a"*64)["receipt"]
        if result.get("browserVerified") is not True or result.get("isolationVerified") is not True or result.get("sandbox") is not True:
            raise RuntimeError("LOCAL_BROWSER_PROBE_FAILED")
        _swrlz_v15_cached={"schema":"swrlz-startup-v15","state":"passed","packages":facts,
                            "isolationVerified":True,"sandbox":True}
    except Exception as exc:
        _swrlz_v15_cached={"schema":"swrlz-startup-v15","state":"failed","packages":facts,
                           "error":str(exc)[:240]}
    finally:_swrlz_v15_lock.release()
    return _swrlz_v15_cached
'''
def patch_probe(s):
    if MARK in s:
        if s.count(MARK)!=1 or s.count(PROBE_PATH)!=1:raise RuntimeError("PARTIAL_PROBE")
        ast.parse(s);return s
    anchor="def _swrlz_execute_model_repair_v7("
    if s.count(anchor)!=1:raise RuntimeError("STARTUP_PROBE_SOURCE_DRIFT")
    s=s.replace(anchor,PROBE+"\n"+anchor,1);ast.parse(s);return s
def safe_logs(token):
    # Owner-authorized read, category counts only. No arbitrary log text or secrets.
    for kind in ("build","run"):
        try:
            req=urllib.request.Request("https://huggingface.co/api/spaces/"+SPACE+"/logs/"+kind,
                 headers={"Authorization":"Bearer "+token,"Accept":"text/event-stream"})
            with urllib.request.urlopen(req,timeout=5) as r:
                raw=r.read(65536).decode(errors="replace")
            cats=("ModuleNotFoundError","ImportError","NameError","SyntaxError","Permission denied",
                  "Operation not permitted","No usable sandbox","Failed to create","chromium","bubblewrap",
                  "playwright","Error loading ASGI app","Application startup complete","Uvicorn running","ERROR:","Traceback")
            print("V15_LOG_CATEGORIES",kind,json.dumps({p:raw.lower().count(p.lower()) for p in cats if p.lower() in raw.lower()}),flush=True)
        except Exception as e:
            print("V15_LOG_ACCESS",kind,type(e).__name__,getattr(e,"code",None),flush=True)
def runtime_stage(api):
    try:
        r=api.get_space_runtime(SPACE);return str(r.stage)
    except Exception as e:return "UNAVAILABLE:"+type(e).__name__
def await_route(api,path,schema):
    consecutive_404=0
    for i in range(90):
        stage=runtime_stage(api)
        if stage.upper() in ("BUILD_ERROR","RUNTIME_ERROR","CONFIG_ERROR"):
            raise RuntimeError("HOST_STARTUP_FAILED:"+stage)
        try:
            with urllib.request.urlopen(BASE+path,timeout=65) as r:receipt=json.load(r)
            if receipt.get("schema")==schema:
                if receipt.get("state")=="failed":
                    print("V15_PROBE_FAILURE",json.dumps(receipt),flush=True)
                    raise ValueError("LIVE_PROBE_FAILED")
                if receipt.get("state")=="passed":return receipt
            consecutive_404=0
        except ValueError:raise
        except (OSError,RuntimeError) as exc:
            code=getattr(exc,"code",None)
            consecutive_404=consecutive_404+1 if stage=="RUNNING" and code==404 else 0
            if i%5==0:print("V15_PENDING",path,i,stage,type(exc).__name__,code,flush=True)
            if consecutive_404>=12:raise RuntimeError("RUNNING_SPACE_MISSING_EXPECTED_ROUTE")
        if i==89:raise RuntimeError("STARTUP_PROBE_TIMEOUT")
        time.sleep(8)
def selftest():
    v14.selftest()
    src="def _swrlz_execute_model_repair_v7(payload,coder_generate):\n    active=None\n    yield from active.run(payload, coder_generate)\n"
    stage=patch_probe(src)
    assert patch_probe(stage)==stage and "browser_validator=" not in stage
    final=v14.patch_station(stage)
    assert "browser_validator=_swrlz_local_browser_v14.validate_local" in final
    print("V15_TWO_PHASE_SELFTEST_PASS",flush=True)
def run(mode):
    selftest()
    if mode=="selftest":return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    token=os.getenv("HF_TOKEN") or None;api=HfApi(token=token)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    names=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    def read(n,r):return Path(hf_hub_download(SPACE,n,repo_type="space",revision=r,token=token)).read_bytes()
    original={n:read(n,rev) for n in (*v14.LOCAL,STATION,"requirements.txt","packages.txt") if n in names}
    desired={n:p.read_bytes() for n,p in v14.LOCAL.items()}
    for n in v14.LOCAL:
        if n in v14.PINS:
            if n not in original or (original[n]!=desired[n] and v14.blob(original[n])!=v14.PINS[n]):
                raise RuntimeError("SOURCE_DRIFT:"+n)
        elif n in original and original[n]!=desired[n]:raise RuntimeError("NEW_PATH_COLLISION:"+n)
    req=original.get("requirements.txt",b"")
    for line in req.decode().splitlines():
        if line.strip().lower().startswith("playwright") and line.strip()!="playwright==1.51.0":raise RuntimeError("PLAYWRIGHT_PIN_CONFLICT")
    stage={n:v for n,v in desired.items() if n=="browser_worker_protocol_v1.py" or n.startswith("html_project_local_browser")}
    stage["requirements.txt"]=v14.append_lines(req,["playwright==1.51.0"])
    stage["packages.txt"]=v14.append_lines(original.get("packages.txt",b""),["bubblewrap","chromium","fonts-liberation"])
    stage[STATION]=patch_probe(original[STATION].decode()).encode()
    final={**stage,**desired,STATION:v14.patch_station(stage[STATION].decode()).encode()}
    print("V15_PREFLIGHT",rev,"stage",sorted(stage),"activation",sorted(set(final)-set(stage)),flush=True)
    if mode=="preflight":return
    if mode!="publish" or not token or os.getenv("SWRLZ_V15_APPROVED")!="1":raise PermissionError("V15_NOT_APPROVED")
    key=derive_key(token)
    current=rev
    changed_names=set()
    def add(n,v):return CommitOperationAdd(path_in_repo=n,path_or_fileobj=io.BytesIO(v))
    def commit(files,label):
        nonlocal current
        if str(api.repo_info(SPACE,repo_type="space").sha)!=current:raise RuntimeError("CONCURRENT_SPACE_CHANGE")
        listed=set(api.list_repo_files(SPACE,repo_type="space",revision=current))
        delta={n:v for n,v in files.items() if n not in listed or read(n,current)!=v}
        if delta:
            current=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=current,
                operations=[add(n,v) for n,v in delta.items()],commit_message=label).oid
            changed_names.update(delta)
        for n,v in files.items():
            if read(n,current)!=v:raise RuntimeError("READBACK_MISMATCH:"+n)
        print("V15_COMMIT",label,current,flush=True)
        # Explicit restart after source readback, unlike v14's implicit-only activation.
        api.restart_space(SPACE)
        print("V15_RESTART_REQUESTED",current,flush=True)
    try:
        commit(stage,"§C v15 phase A: packages and trusted sandbox startup probe only")
        receipt=await_route(api,PROBE_PATH,"swrlz-startup-v15")
        print("V15_STARTUP_PROOF",json.dumps(receipt),flush=True)
        if receipt.get("isolationVerified") is not True or receipt.get("sandbox") is not True:
            raise RuntimeError("ISOLATION_UNVERIFIED")
        api.add_space_secret(SPACE,"SWRLZ_BROWSER_WORKER_KEY",key)
        commit(final,"§C v15 phase B: enable validated local browser repair route")
        receipt=await_route(api,"/api/html-project-agent-v14/runtime-check","swrlz-local-browser-v14")
        if receipt.get("routeActive") is not True or receipt.get("isolationVerified") is not True:
            raise RuntimeError("BROWSER_ROUTE_NOT_VERIFIED")
        worker_test(key)
        print("V15_DEPLOYED_VERIFIED",current,json.dumps(receipt),flush=True)
    except Exception:
        safe_logs(token)
        if changed_names and str(api.repo_info(SPACE,repo_type="space").sha)==current:
            restored=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=current,
                operations=[add(n,original[n]) if n in original else CommitOperationDelete(path_in_repo=n) for n in sorted(changed_names)],
                commit_message="rollback §C v15: startup or sandbox verification failed").oid
            print("V15_ROLLBACK",restored,flush=True)
            api.restart_space(SPACE)
        raise
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("selftest","preflight","publish"));run(p.parse_args().mode)
