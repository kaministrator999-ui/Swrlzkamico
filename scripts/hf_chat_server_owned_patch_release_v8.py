#!/usr/bin/env python3
"""CAS release of server-owned repair proposal identity and chained hashes.

Updates only the two §C model-patch helpers and the existing live Station
runtime guard. Requires source-pinned exact upgrade, model/patch regression
tests, source readback, and live in-memory Python function verification.
No GitHub project write or owner approval is performed.
"""
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
MARKER = "# swrlz-server-owned-model-patch-v8"
CHECK = "/api/html-project-agent-v8/runtime-check"
ANCHOR = "    return _swrlz_model_repair\n\n\ndef _swrlz_execute_model_repair_v7("
REPLACEMENT = """    return _swrlz_verified_repair_runtime_v8(_swrlz_model_repair)


# swrlz-server-owned-model-patch-v8
def _swrlz_verified_repair_runtime_v8(active):
    import dis
    import importlib
    try:
        agent = importlib.import_module("html_project_agent_v1")
    except ImportError:
        agent = importlib.import_module("api.html_project_agent_v1")

    def loaded():
        binder = getattr(agent, "bind_model_edits", None)
        run = getattr(active, "run", None)
        return (callable(binder)
                and getattr(active, "bind_model_edits", None) is binder
                and callable(run)
                and any(i.argval == "bind_model_edits"
                        for i in dis.get_instructions(run)))

    if not loaded():
        importlib.invalidate_caches()
        importlib.reload(agent)
        importlib.reload(active)
    if not loaded():
        raise RuntimeError("REPAIR_PROPOSAL_BINDER_STALE")
    return active


@app.get("/api/html-project-agent-v8/runtime-check", include_in_schema=False)
def _swrlz_server_owned_patch_v8_health():
    active = _swrlz_verified_repair_runtime_v7()
    agent = active.bind_model_edits
    return {
        "schema": "swrlz-server-owned-model-patch-v8",
        "loadedBinder": callable(agent),
        "runtime": active.__name__,
        "sourceIdentity": "server-pinned",
        "chainedSourceHashes": "server-computed",
        "approval": "required",
    }


def _swrlz_execute_model_repair_v7("""
BASE_AGENT = 'if not isinstance(proposal, dict) or proposal.get("schema") != VERSION or proposal.get("project") != project:'
BASE_RUNTIME = '                proposal = _model_patch(coder_generate, payload, messages)'
AFTER_AGENT = 'def bind_model_edits(project, original_files, model_proposal):'
AFTER_RUNTIME = '                proposal = bind_model_edits(project["project"], files, model_edits)'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def selftest():
    for module,path in LOCAL.items():
        source=path.read_text(encoding="utf-8")
        ast.parse(source,filename=module)
    agent=LOCAL[AGENT].read_text()
    runtime=LOCAL[RUNTIME].read_text()
    if (BASE_AGENT not in agent or AFTER_AGENT not in agent
            or BASE_RUNTIME in runtime or AFTER_RUNTIME not in runtime):
        raise RuntimeError("SERVER_OWNED_PATCH_SOURCE_INTEGRITY")
    print("SERVER_PATCH_V8_SELFTEST_PASS",flush=True)


def patch_station(source):
    if MARKER in source:
        if (source.count(MARKER)!=1 or source.count(CHECK)!=1
                or "_swrlz_verified_repair_runtime_v8(_swrlz_model_repair)" not in source):
            raise RuntimeError("PARTIAL_SERVER_PATCH_V8_INSTALL")
        ast.parse(source,filename=STATION)
        return source
    if source.count(ANCHOR)!=1:
        raise RuntimeError("LIVE_STATION_RUNTIME_GUARD_ANCHOR_DRIFT")
    if '/api/html-project-agent-v7/runtime-check' not in source:
        raise RuntimeError("RUNTIME_V7_NOT_INSTALLED")
    after=source.replace(ANCHOR,REPLACEMENT,1)
    ast.parse(after,filename=STATION)
    if after.count(MARKER)!=1:
        raise RuntimeError("RUNTIME_V8_INSERTION_INTEGRITY")
    return after


def live_check():
    for i in range(4):
        request=urllib.request.Request(
            BASE+CHECK+"?probe="+str(i),
            headers={"Cache-Control":"no-cache"})
        with urllib.request.urlopen(request,timeout=25) as response:
            if response.status!=200:
                raise RuntimeError("V8_RUNTIME_HTTP")
            receipt=json.load(response)
        expected={
            "schema":"swrlz-server-owned-model-patch-v8",
            "loadedBinder":True,
            "runtime":"html_project_agent_runtime_v1",
            "sourceIdentity":"server-pinned",
            "chainedSourceHashes":"server-computed",
            "approval":"required",
        }
        if receipt!=expected:
            raise RuntimeError("V8_RUNTIME_LOADED_CODE_UNVERIFIED: "+repr(receipt))
    print("SERVER_PATCH_V8_LIVE_BYTECODE_VERIFIED",flush=True)


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
    current_agent=originals[AGENT].decode("utf-8")
    current_runtime=originals[RUNTIME].decode("utf-8")
    if (AFTER_AGENT in current_agent or AFTER_RUNTIME in current_runtime):
        if (originals[AGENT]!=candidate[AGENT]
                or originals[RUNTIME]!=candidate[RUNTIME]):
            raise RuntimeError("PARTIALLY_MODIFIED_LIVE_PROPOSAL_HELPERS")
    elif (BASE_AGENT not in current_agent or BASE_RUNTIME not in current_runtime):
        raise RuntimeError("LIVE_AGENT_PROPOSAL_ANCHOR_DRIFT")
    candidate[STATION]=patch_station(originals[STATION].decode("utf-8")).encode("utf-8")
    changed={name:raw for name,raw in candidate.items() if originals[name]!=raw}
    print("SERVER_PATCH_V8_PREFLIGHT",json.dumps({
        "revision":rev,"changes":sorted(changed),
        "sourceFingerprints":{name:{"before":digest(originals[name]),"after":digest(candidate[name])}
                              for name in (AGENT,RUNTIME,STATION)}
    }),flush=True)
    if mode=="preflight":
        return
    if mode=="verify":
        if changed:
            raise RuntimeError("SERVER_PATCH_V8_SOURCE_NOT_DEPLOYED")
        live_check()
        print("SERVER_PATCH_V8_SOURCE_AND_EXECUTION_VERIFIED",rev,flush=True)
        return
    if (mode!="publish" or not token
            or os.getenv("SWRLZ_SERVER_PATCH_V8_APPROVED")!="1"):
        raise PermissionError("SERVER_PATCH_V8_RELEASE_NOT_APPROVED")
    if not changed:
        live_check()
        print("SERVER_PATCH_V8_ALREADY_CURRENT",rev,flush=True)
        return
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:
        raise RuntimeError("CONCURRENT_SPACE_CHANGE")
    def addition(name,raw):
        return CommitOperationAdd(path_in_repo=name,path_or_fileobj=io.BytesIO(raw))
    new=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[addition(name,raw) for name,raw in changed.items()],
        commit_message="fix(§C): let server bind model repair identity and chained SHA hashes").oid
    print("SERVER_PATCH_V8_SPACE_COMMITTED",new,flush=True)
    try:
        for name,raw in candidate.items():
            readback=Path(hf_hub_download(
                SPACE,name,repo_type="space",revision=new,token=token)).read_bytes()
            if readback!=raw:
                raise RuntimeError("SERVER_PATCH_V8_READBACK_MISMATCH_"+name)
        print("SERVER_PATCH_V8_READBACK_PASS",new,flush=True)
        api.restart_space(SPACE)
        for attempt in range(85):
            try:
                live_check()
                print("SERVER_PATCH_V8_DEPLOYED_VERIFIED",new,flush=True)
                return
            except Exception as exc:
                if attempt%10==0:
                    print("SERVER_PATCH_V8_HEALTH_PENDING",attempt,type(exc).__name__,flush=True)
                if attempt==84:
                    raise RuntimeError("SERVER_PATCH_V8_RUNTIME_CHECK_FAILED") from exc
                time.sleep(8)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==new:
            restored=api.create_commit(
                repo_id=SPACE,repo_type="space",parent_commit=new,
                operations=[addition(name,originals[name]) for name in changed],
                commit_message="rollback(§C): server proposal binder runtime not verified").oid
            print("SERVER_PATCH_V8_ROLLBACK",restored,flush=True)
            api.restart_space(SPACE)
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("selftest","preflight","publish","verify"))
    release(parser.parse_args().mode)
