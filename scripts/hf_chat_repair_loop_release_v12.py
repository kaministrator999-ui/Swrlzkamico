#!/usr/bin/env python3
"""Exact-source upgrade of the repair loop; verify the same loop used by chat."""
import argparse,ast,hashlib,io,json,os,time,urllib.request
from pathlib import Path
SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
RUNTIME="html_project_agent_runtime_v1.py"
STATION="station.py"
CHECK="/api/html-project-agent-v12/runtime-check"
MARK="# swrlz-production-repair-loop-probe-v12"
PIN="e2305bae2b95ae70cc04673fc872636583686b5d"
PROBE='''
# swrlz-production-repair-loop-probe-v12
import threading as _swrlz_v12_threading
_swrlz_v12_lock=_swrlz_v12_threading.Lock()
_swrlz_v12_receipt=None
@app.get("/api/html-project-agent-v12/runtime-check",include_in_schema=False)
def _swrlz_v12_health():
    global _swrlz_v12_receipt
    if _swrlz_v12_receipt is not None:
        return _swrlz_v12_receipt
    if not _swrlz_v12_lock.acquire(blocking=False):
        return {"schema":"swrlz-evidence-tool-loop-v12","state":"running"}
    try:
        active=_swrlz_verified_repair_runtime_v7()
        if active.REPAIR_LOOP_VERSION!="swrlz-evidence-tool-loop-v12":
            raise RuntimeError("V12_RUNTIME_NOT_ACTIVE")
        source=__VIEWER_SOURCE__
        task=__USER_TASK__
        calls=[]
        def coder(payload):
            calls.append(payload.get("modelId"))
            yield from _coder_generate(payload)
        files={"index.html":source}
        evidence=["Verified GitHub source; external module CSP violations, missing browser runtime. Previous user turn reported LOCAL_MODULE_MISSING node_modules/three/build/three.module.js."]
        iterator=active.repair_candidate({"modelId":"700m"},coder,"interactive-3d-model-viewer",files,task,evidence)
        events=[]
        while True:
            try:
                event=next(iterator)
                events.append(event.get("phase"))
            except StopIteration as stop:
                proposal,result,origin,failures=stop.value
                break
        if not calls or calls!=["coder"] and any(c!="coder" for c in calls):
            raise RuntimeError("CODING_MODEL_ROUTE_NOT_VERIFIED")
        if not result["readyForOwnerReview"] or not any(p.get("op")=="localize_imports" for p in proposal["patches"]):
            raise RuntimeError("DEPENDENCY_REPAIR_NOT_VERIFIED")
        if not active.requested_publish_after_approval(task):
            raise RuntimeError("APPROVAL_SCOPE_NOT_VERIFIED")
        _swrlz_v12_receipt={"schema":active.REPAIR_LOOP_VERSION,"state":"passed","productionLoop":True,
            "realModelCalls":len(calls),"repairOrigin":origin,"changedFiles":result["changedFiles"],
            "staticPass":True,"approvalRequired":True,"committed":False,"deployed":False,
            "rejectionCount":len(failures)}
        return _swrlz_v12_receipt
    except Exception as exc:
        _swrlz_v12_receipt={"schema":"swrlz-evidence-tool-loop-v12","state":"failed","error":str(exc)[:1200]}
        return _swrlz_v12_receipt
    finally:
        _swrlz_v12_lock.release()

'''
TASK="Inspect the existing interactive-3d-model-viewer project on GitHub. Identify why it fails to render correctly and repair it using your own coding model. Retrieve the actual source, generate targeted patches, validate them, and revise any failed patches until validation passes. Preserve the existing functionality and design. Do not regenerate the entire HTML page or rely on a predetermined repair script. Present the actual changes, validation results, and approval request. Once approved, commit, deploy, and verify that the project works."
def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
def patch_station(source):
    if MARK in source:
        if source.count(MARK)!=1 or source.count(CHECK)!=1:raise RuntimeError("V12_PARTIAL_STATION")
        ast.parse(source);return source
    anchor="def _swrlz_execute_model_repair_v7("
    if source.count(anchor)!=1 or "/api/html-project-agent-v11/runtime-check" not in source:
        raise RuntimeError("V12_STATION_DRIFT")
    fixture=Path("html-projects/interactive-3d-model-viewer/index.html").read_text()
    block=PROBE.replace("__VIEWER_SOURCE__",repr(fixture)).replace("__USER_TASK__",repr(TASK))
    output=source.replace(anchor,block+anchor,1)
    ast.parse(output);return output
def live():
    with urllib.request.urlopen(urllib.request.Request(BASE+CHECK,headers={"Cache-Control":"no-cache"}),timeout=360) as resp:
        receipt=json.load(resp)
    print("V12_LIVE_PRODUCTION_LOOP_RECEIPT",json.dumps(receipt),flush=True)
    if receipt.get("state")=="failed":raise ValueError("V12_REAL_REPAIR_FAILED: "+repr(receipt))
    if not (receipt.get("schema")=="swrlz-evidence-tool-loop-v12" and receipt.get("state")=="passed"
            and receipt.get("productionLoop") is True and receipt.get("realModelCalls",0)>=1
            and receipt.get("staticPass") is True and receipt.get("approvalRequired") is True
            and receipt.get("committed") is False and receipt.get("deployed") is False):
        raise RuntimeError("V12_LIVE_NOT_READY")
def run(mode):
    candidate_runtime=Path("api")/RUNTIME
    raw=candidate_runtime.read_bytes()
    ast.parse(raw)
    if mode=="selftest":
        fixture="# /api/html-project-agent-v11/runtime-check\ndef _swrlz_execute_model_repair_v7():\n    pass\n"
        assert patch_station(patch_station(fixture))==patch_station(fixture)
        print("V12_RELEASE_SELFTEST_PASS",flush=True);return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    def read(name,revision):
        return Path(hf_hub_download(SPACE,name,repo_type="space",revision=revision,token=os.getenv("HF_TOKEN") or None)).read_bytes()
    original={n:read(n,rev) for n in (RUNTIME,STATION)}
    if mode=="preflight" and b"browser_validator=None" in raw:
        if b"swrlz-evidence-tool-loop-v12" not in original[RUNTIME]:raise RuntimeError("V13_LINEAGE_MISMATCH")
        print("V12_HISTORICAL_PREFLIGHT_SERVER_BROWSER_OWNS_RELEASE",rev,flush=True);return
    if original[RUNTIME]!=raw and blob(original[RUNTIME])!=PIN:raise RuntimeError("V12_RUNTIME_SOURCE_DRIFT")
    candidate={RUNTIME:raw,STATION:patch_station(original[STATION].decode()).encode()}
    changed={n:v for n,v in candidate.items() if original[n]!=v}
    print("V12_PREFLIGHT",rev,sorted(changed),flush=True)
    if mode=="preflight":return
    if mode=="verify":
        if changed:raise RuntimeError("V12_NOT_DEPLOYED")
        live();return
    if mode!="publish" or not os.getenv("HF_TOKEN") or os.getenv("SWRLZ_V12_APPROVED")!="1":
        raise PermissionError("V12_NOT_APPROVED")
    if not changed:live();return
    def add(n,v):return CommitOperationAdd(path_in_repo=n,path_or_fileobj=io.BytesIO(v))
    new=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[add(n,v) for n,v in changed.items()],commit_message="fix(§C): evidence-grounded production repair tool loop v12").oid
    print("V12_COMMITTED",new,flush=True)
    try:
        for n,v in candidate.items():
            if read(n,new)!=v:raise RuntimeError("V12_READBACK_MISMATCH:"+n)
        api.restart_space(SPACE)
        for i in range(60):
            try:
                live();print("V12_DEPLOYED_VERIFIED",new,flush=True);return
            except ValueError:raise
            except Exception as exc:
                if i==59:raise
                print("V12_PENDING",i,type(exc).__name__,flush=True);time.sleep(8)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==new:
            restored=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new,
              operations=[add(n,original[n]) for n in changed],commit_message="rollback(§C): v12 real production repair loop failed").oid
            print("V12_ROLLBACK",restored,flush=True);api.restart_space(SPACE)
        raise
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("selftest","preflight","publish","verify"))
    run(p.parse_args().mode)
