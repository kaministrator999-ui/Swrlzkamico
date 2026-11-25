#!/usr/bin/env python3
"""Validate real preapproval GitHub worker, then enable §C adapter on existing Space."""
import argparse,ast,io,json,os,sys,time,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.hf_chat_server_browser_release_v13 import PINS,blob,LOCAL as OLD
from api.html_project_browser_backend_v1 import GitHubBrowserBackend,github_api
from api.html_project_agent_v1 import bind_model_edits,apply_proposal,inspect_static,VALID_EXT
SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
CHECK="/api/html-project-agent-v16/runtime-check"
MARK="# swrlz-browser-adapter-v16"
STATION="station.py"
LOCAL=dict(OLD)
LOCAL["html_project_browser_backend_v1.py"]=Path("api/html_project_browser_backend_v1.py")
PROBE='''
# swrlz-browser-adapter-v16
@app.get("/api/html-project-agent-v16/runtime-check",include_in_schema=False)
def _swrlz_v16_browser_health():
    from html_project_browser_backend_v1 import backend,WORKFLOW
    active=_swrlz_verified_repair_runtime_v7()
    import inspect
    return {"schema":"swrlz-browser-adapter-v16","backend":backend.name,
            "workflow":WORKFLOW,"routeActive":"browser_validator" in inspect.signature(active.run).parameters,
            "approvalRequired":True}
'''
def patch_station(s):
    if MARK in s:
        if s.count(MARK)!=1 or s.count(CHECK)!=1 or "browser_validator=_swrlz_v16_backend" not in s:
            raise RuntimeError("V16_PARTIAL_ROUTE")
        ast.parse(s);return s
    anchor="    yield from active.run(payload, coder_generate)"
    if s.count(anchor)!=1:raise RuntimeError("V16_ROUTE_DRIFT")
    s=s.replace(anchor,"    from html_project_browser_backend_v1 import backend as _swrlz_v16_backend\n    yield from active.run(payload, coder_generate, browser_validator=_swrlz_v16_backend)",1)
    anchor2="def _swrlz_execute_model_repair_v7("
    if s.count(anchor2)!=1:raise RuntimeError("V16_PROBE_DRIFT")
    s=s.replace(anchor2,PROBE+"\n"+anchor2,1);ast.parse(s);return s
def selftest():
    src="def _swrlz_execute_model_repair_v7(payload, coder_generate):\n    active=None\n    yield from active.run(payload, coder_generate)\n"
    assert patch_station(patch_station(src))==patch_station(src)
    for p in LOCAL.values():
        if p.suffix==".py":ast.parse(p.read_bytes())
    print("V16_SELFTEST_PASS",flush=True)
def worker_test():
    token=os.environ["GH_TOKEN"];sha=os.environ["GITHUB_SHA"]
    project="interactive-3d-model-viewer";root=Path("html-projects")/project
    files={f.relative_to(root).as_posix():f.read_text(encoding="utf-8") for f in root.rglob("*")
           if f.is_file() and f.suffix.lower() in VALID_EXT}
    anchor="<title>Interactive 3D Model Viewer</title>"
    # Both candidates are ephemeral. The second intentionally fails at runtime.
    probes=[(True,anchor.replace("Viewer","Viewer probe")),
            (False,anchor+"<script>throw new Error('SWRLZ_V16_RUNTIME_PROBE')</script>")]
    from concurrent.futures import ThreadPoolExecutor
    def test(item):
        expected,code=item
        plan=bind_model_edits(project,files,{"patches":[{"path":"index.html","op":"replace_once","anchor":anchor,"code":code}]})
        result=apply_proposal(project,files,plan,validation=inspect_static)
        adapter=GitHubBrowserBackend(github_api(token),token,sha,timeout=420)
        rec=adapter.validate_candidate(project,{**files,**result["proposedFiles"]},True,plan)["receipt"]
        if rec["browserVerified"] is not expected:raise RuntimeError("V16_REAL_WORKER_UNEXPECTED_RESULT")
        if not expected and not any("SWRLZ_V16_RUNTIME_PROBE" in i["detail"] for i in rec["issues"]):
            raise RuntimeError("V16_REAL_RUNTIME_ERROR_NOT_CAPTURED")
        print("V16_REAL_WORKER_PROOF",json.dumps({"runId":rec["runId"],"browserVerified":expected,
               "issues":rec["issues"],"entrySha256":rec["hashes"]["index.html"]}),flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(test,probes))
def run(mode):
    selftest()
    if mode=="selftest":return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    token=os.getenv("HF_TOKEN") or None;api=HfApi(token=token)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    names=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    def read(n,r):return Path(hf_hub_download(SPACE,n,repo_type="space",revision=r,token=token)).read_bytes()
    original={n:read(n,rev) for n in (*LOCAL,STATION) if n in names}
    candidate={n:p.read_bytes() for n,p in LOCAL.items()}
    for n,v in candidate.items():
        if n in PINS and (n not in original or (original[n]!=v and blob(original[n])!=PINS[n])):
            raise RuntimeError("V16_SOURCE_DRIFT:"+n)
        if n not in PINS and n in original and original[n]!=v:raise RuntimeError("V16_NEW_PATH_COLLISION:"+n)
    candidate[STATION]=patch_station(original[STATION].decode()).encode()
    changed={n:v for n,v in candidate.items() if original.get(n)!=v}
    print("V16_PREFLIGHT",rev,sorted(changed),flush=True)
    if mode=="preflight":return
    if mode!="publish" or not token or os.getenv("SWRLZ_V16_APPROVED")!="1":raise PermissionError("V16_NOT_APPROVED")
    # Live worker before production mutation. No HF token sent to browser job.
    worker_test()
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:raise RuntimeError("V16_CONCURRENT_SPACE_CHANGE")
    def add(n,v):return CommitOperationAdd(path_in_repo=n,path_or_fileobj=io.BytesIO(v))
    new=rev
    if changed:
        new=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
            operations=[add(n,v) for n,v in changed.items()],commit_message="§C v16: pluggable read-only browser worker").oid
    print("V16_SPACE_COMMIT",new,flush=True)
    try:
        for n,v in candidate.items():
            if read(n,new)!=v:raise RuntimeError("V16_READBACK_MISMATCH:"+n)
        api.restart_space(SPACE)
        for i in range(90):
            try:
                with urllib.request.urlopen(BASE+CHECK,timeout=15) as r:rec=json.load(r)
                if rec=={"schema":"swrlz-browser-adapter-v16","backend":"github-actions","workflow":"hf-html-project-browser-worker-v16.yml",
                         "routeActive":True,"approvalRequired":True}:
                    print("V16_DEPLOYED_VERIFIED",new,json.dumps(rec),flush=True);return
            except (OSError,ValueError):pass
            if i%5==0:print("V16_PENDING",i,str(api.get_space_runtime(SPACE).stage),flush=True)
            time.sleep(8)
        raise RuntimeError("V16_LIVE_ROUTE_UNVERIFIED")
    except Exception:
        if changed and str(api.repo_info(SPACE,repo_type="space").sha)==new:
            restored=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new,
              operations=[add(n,original[n]) if n in original else CommitOperationDelete(path_in_repo=n) for n in changed],
              commit_message="rollback §C v16: route not verified").oid
            api.restart_space(SPACE);print("V16_ROLLBACK",restored,flush=True)
        raise
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("selftest","preflight","publish"));run(p.parse_args().mode)
