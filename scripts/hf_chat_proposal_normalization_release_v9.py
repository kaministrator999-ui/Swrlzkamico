#!/usr/bin/env python3
"""CAS-scoped proposal normalization release with live in-memory patch execution."""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import time
import urllib.request
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
STATION = "station.py"
AGENT = "html_project_agent_v1.py"
RUNTIME = "html_project_agent_runtime_v1.py"
LOCAL = {AGENT: Path("api/html_project_agent_v1.py"),
         RUNTIME: Path("api/html_project_agent_runtime_v1.py")}
MARKER = "# swrlz-proposal-normalization-v9"
CHECK = "/api/html-project-agent-v9/runtime-check"
BASE_BLOB = "52015a1754f6a0cf883ba4e982090ef5bfec70e9"
ANCHOR = '                and callable(run)\n'
GUARD = '''                and "_check_model_metadata" in binder.__code__.co_names
                and callable(run)
'''
PROBE_ANCHOR = "def _swrlz_execute_model_repair_v7("
PROBE = '''
# swrlz-proposal-normalization-v9
@app.get("/api/html-project-agent-v9/runtime-check",include_in_schema=False)
def _swrlz_normalizer_v9_health():
    active = _swrlz_verified_repair_runtime_v7()
    source = "<html><body><p>old</p></body></html>"
    files = {"index.html": source}
    raw = {"summary": "synthetic probe", "diagnosis": {"kind":"test"},
           "deploymentNotes": "no deployment",
           "patches": [{"path":"index.html","op":"replace_once",
                        "anchor":"<p>old</p>","code":"<p>new</p>",
                        "explanation":"fixture metadata","lineNumber":1}]}
    bound = active.bind_model_edits("normalization-probe",files,raw)
    result = active.apply_proposal("normalization-probe",files,bound,
                                  validation=lambda _: {"passed":True})
    blocked = False
    try:
        active.bind_model_edits("normalization-probe",files,{**raw,"deploy":True})
    except ValueError:
        blocked = True
    return {
        "schema":"swrlz-proposal-normalization-v9",
        "metadataDiscarded":set(bound)=={"schema","project","patches","rationale"}
            and set(bound["patches"][0])=={"path","op","anchor","code","sourceSha256"},
        "patchApplied":result["proposedFiles"]["index.html"]==source.replace("old","new"),
        "authorityBlocked":blocked,
        "committed":result["committed"],
        "deployed":result["deployed"],
    }


'''

def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def selftest():
    from api.html_project_agent_v1 import bind_model_edits, apply_proposal
    source=LOCAL[AGENT].read_text()
    ast.parse(source,filename=AGENT)
    files={"index.html":"<html><body>old</body></html>"}
    p=bind_model_edits("test-project",files,{"summary":"ignored","patches":[
        {"path":"index.html","op":"replace_once","anchor":"old","code":"new","note":"ignored"}]})
    assert set(p)=={"schema","project","patches","rationale"}
    assert apply_proposal("test-project",files,p)["proposedFiles"]["index.html"]=="<html><body>new</body></html>"
    print("NORMALIZER_V9_SELFTEST_PASS",flush=True)


def patch_station(source):
    if MARKER in source:
        if source.count(MARKER)!=1 or source.count(CHECK)!=1 or GUARD not in source:
            raise RuntimeError("PARTIAL_NORMALIZER_V9_INSTALL")
        ast.parse(source,filename=STATION)
        return source
    if source.count(ANCHOR)!=1 or source.count(PROBE_ANCHOR)!=1 or "/api/html-project-agent-v8/runtime-check" not in source:
        raise RuntimeError("LIVE_V8_GUARD_ANCHOR_DRIFT")
    after=source.replace(ANCHOR,GUARD,1).replace(PROBE_ANCHOR,PROBE+PROBE_ANCHOR,1)
    ast.parse(after,filename=STATION)
    return after


def live_check():
    request=urllib.request.Request(BASE+CHECK,headers={"Cache-Control":"no-cache"})
    with urllib.request.urlopen(request,timeout=25) as response:
        receipt=json.load(response)
    expected={"schema":"swrlz-proposal-normalization-v9","metadataDiscarded":True,
              "patchApplied":True,"authorityBlocked":True,"committed":False,"deployed":False}
    if receipt!=expected:
        raise RuntimeError("V9_LIVE_NORMALIZATION_FAILED: "+repr(receipt))
    print("NORMALIZER_V9_LIVE_PATCH_EXECUTED",json.dumps(receipt),flush=True)


def release(mode):
    selftest()
    if mode=="selftest":
        return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
    token=os.getenv("HF_TOKEN") or None
    api=HfApi(token=token)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    originals={
        name:Path(hf_hub_download(
            SPACE,name,repo_type="space",revision=rev,token=token)).read_bytes()
        for name in (STATION,AGENT,RUNTIME)
    }
    candidate={name:path.read_bytes() for name,path in LOCAL.items()}
    raw=originals[AGENT]
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
    if (mode=="preflight" and b"swrlz-exact-patches-v10" in candidate[RUNTIME]
            and (originals[AGENT]!=candidate[AGENT] or originals[RUNTIME]!=candidate[RUNTIME])):
        # Only v10 owns the guarded upgrade; this historical release is read-only.
        if b"def _check_model_metadata(" not in originals[AGENT] or b"bind_model_edits" not in originals[RUNTIME]:
            raise RuntimeError("LIVE_V9_SOURCE_DRIFT")
        print("V9_NEWER_PATCH_PROTOCOL_PREFLIGHT",rev,flush=True)
        return
    if raw!=candidate[AGENT] and blob!=BASE_BLOB:
        raise RuntimeError("LIVE_AGENT_SOURCE_DRIFT")
    if originals[RUNTIME]!=candidate[RUNTIME]:
        raise RuntimeError("LIVE_RUNTIME_SOURCE_DRIFT")
    candidate[STATION]=patch_station(originals[STATION].decode("utf-8")).encode("utf-8")
    changed={name:raw for name,raw in candidate.items() if originals[name]!=raw}
    print("NORMALIZER_V9_PREFLIGHT",json.dumps({
        "revision":rev,"changes":sorted(changed),
        "sourceFingerprints":{name:{"before":digest(originals[name]),"after":digest(candidate[name])}
                              for name in (AGENT,RUNTIME,STATION)}
    }),flush=True)
    if mode=="preflight":
        return
    if mode=="verify":
        if changed:
            raise RuntimeError("NORMALIZER_V9_SOURCE_NOT_DEPLOYED")
        live_check()
        print("NORMALIZER_V9_SOURCE_AND_EXECUTION_VERIFIED",rev,flush=True)
        return
    if (mode!="publish" or not token
            or os.getenv("SWRLZ_NORMALIZER_V9_APPROVED")!="1"):
        raise PermissionError("NORMALIZER_V9_RELEASE_NOT_APPROVED")
    if not changed:
        live_check()
        print("NORMALIZER_V9_ALREADY_CURRENT",rev,flush=True)
        return
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:
        raise RuntimeError("CONCURRENT_SPACE_CHANGE")
    def addition(name,raw):
        return CommitOperationAdd(path_in_repo=name,path_or_fileobj=io.BytesIO(raw))
    new=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[addition(name,raw) for name,raw in changed.items()],
        commit_message="fix(§C): normalize inert model metadata before strict patch validation").oid
    print("NORMALIZER_V9_SPACE_COMMITTED",new,flush=True)
    try:
        for name,raw in candidate.items():
            readback=Path(hf_hub_download(
                SPACE,name,repo_type="space",revision=new,token=token)).read_bytes()
            if readback!=raw:
                raise RuntimeError("NORMALIZER_V9_READBACK_MISMATCH_"+name)
        print("NORMALIZER_V9_READBACK_PASS",new,flush=True)
        api.restart_space(SPACE)
        for attempt in range(85):
            try:
                live_check()
                print("NORMALIZER_V9_DEPLOYED_VERIFIED",new,flush=True)
                return
            except Exception as exc:
                if attempt%10==0:
                    print("NORMALIZER_V9_HEALTH_PENDING",attempt,type(exc).__name__,flush=True)
                if attempt==84:
                    raise RuntimeError("NORMALIZER_V9_RUNTIME_CHECK_FAILED") from exc
                time.sleep(8)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==new:
            restored=api.create_commit(
                repo_id=SPACE,repo_type="space",parent_commit=new,
                operations=[addition(name,originals[name]) for name in changed],
                commit_message="rollback(§C): proposal normalizer live execution failed").oid
            print("NORMALIZER_V9_ROLLBACK",restored,flush=True)
            api.restart_space(SPACE)
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("selftest","preflight","publish","verify"))
    release(parser.parse_args().mode)
