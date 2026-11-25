#!/usr/bin/env python3
"""Repair the actual §C production Station execution path, not only Space files.

A source-readback check cannot prove a Python worker imported new code.
The v7 endpoint checks the loaded _source_files bytecode, reloads the module
if stale, and suppresses *new project* GitHub handoff for existing repairs.
Only station.py is modified; the owner-authenticated source helper must already
match the repository. Commit is CAS-pinned and rolled back if live execution
verification does not pass.
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
RUNTIME = "html_project_agent_runtime_v1.py"
RUNTIME_LOCAL = Path("api/html_project_agent_runtime_v1.py")
MARKER = "# swrlz-repair-in-memory-runtime-v7"
HEALTH_PATH = "/api/html-project-agent-v7/runtime-check"
MOUNT = 'app.mount("/chat/§wyrlz/assets",StaticFiles(directory=ROOT/"chat/§wyrlz/assets"),name="chat-assets")'
OLD_ROUTE = "event_source=_swrlz_model_repair.run(payload,_coder_generate)"
NEW_ROUTE = "event_source=_swrlz_execute_model_repair_v7(payload,_coder_generate)"
OWNER_ANCHOR = '            payload["activeHtmlProject"]=html_project_ref'
OWNER_NEW = OWNER_ANCHOR + '\n            payload["htmlProjectIntent"]=None'
HANDOFF_COMMENT = "# swrlz-generated-html-github-handoff-v1: called only after the"
HANDOFF_OLD = '            if payload.get("htmlProjectIntent"):'
HANDOFF_NEW = ('            if payload.get("htmlProjectIntent") and not '
               '(payload.get("activeHtmlProject") or '
               'payload.get("existingProjectSourceError")):')

ROUTE_ADDITION = '''
# swrlz-repair-in-memory-runtime-v7
def _swrlz_repair_tuple_is_loaded_v7():
    import dis
    # Inspect the compiled function in the active interpreter, not its
    # Python source on disk. The old function lacks LOAD_GLOBAL tuple.
    return any(
        i.opname in ("LOAD_GLOBAL", "LOAD_NAME") and i.argval == "tuple"
        for i in dis.get_instructions(_swrlz_model_repair._source_files))


def _swrlz_verified_repair_runtime_v7():
    import importlib
    if not _swrlz_repair_tuple_is_loaded_v7():
        # A Space commit/restart may be acknowledged while an old interpreter
        # still handles requests. Reload only this stateless helper on demand.
        importlib.invalidate_caches()
        importlib.reload(_swrlz_model_repair)
    if not _swrlz_repair_tuple_is_loaded_v7():
        raise RuntimeError("REPAIR_RUNTIME_MODULE_STALE")
    return _swrlz_model_repair


def _swrlz_execute_model_repair_v7(payload, coder_generate):
    active = _swrlz_verified_repair_runtime_v7()
    yield {"type": "STATUS", "phase": "REPAIR_RUNTIME_V7_VERIFIED",
           "reason": "Loaded repair source loader uses tuple suffixes."}
    yield from active.run(payload, coder_generate)


@app.get("/api/html-project-agent-v7/runtime-check",include_in_schema=False)
def _swrlz_repair_runtime_v7_health():
    active = _swrlz_verified_repair_runtime_v7()
    return {
        "schema": "swrlz-repair-in-memory-runtime-v7",
        "loadedTupleSuffix": _swrlz_repair_tuple_is_loaded_v7(),
        "loadedModule": active.__name__,
        "handoff": "disabled-for-existing-projects",
        "approval": "required",
    }
'''


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def assert_install(source):
    ast.parse(source, filename=STATION)
    required = (
        MARKER, HEALTH_PATH, NEW_ROUTE, OWNER_NEW, HANDOFF_NEW,
        "def _swrlz_repair_tuple_is_loaded_v7():",
    )
    missing = [needle for needle in required if needle not in source]
    if missing or OLD_ROUTE in source or HANDOFF_OLD in source:
        raise RuntimeError("REPAIR_V7_ROUTE_INCOMPLETE: " + repr(missing))
    if source.count(MARKER) != 1 or source.count(HEALTH_PATH) != 1:
        raise RuntimeError("REPAIR_V7_DUPLICATE_OR_PARTIAL_INSTALL")


def patch_station(source):
    if MARKER in source:
        assert_install(source)
        return source
    if (source.count(MOUNT) != 1 or source.count(OLD_ROUTE) != 1
            or source.count(OWNER_ANCHOR) != 1
            or source.count(HANDOFF_COMMENT) != 1):
        raise RuntimeError("REPAIR_V7_PRODUCTION_ANCHOR_DRIFT")
    handoff = source.index(HANDOFF_COMMENT)
    if HANDOFF_OLD not in source[handoff:handoff+320]:
        raise RuntimeError("REPAIR_V7_HANDOFF_CONDITION_DRIFT")
    if source.count(HANDOFF_OLD) != 1:
        raise RuntimeError("REPAIR_V7_HANDOFF_NOT_UNIQUE")
    source = source.replace(OLD_ROUTE, NEW_ROUTE, 1)
    source = source.replace(OWNER_ANCHOR, OWNER_NEW, 1)
    source = source[:source.index(HANDOFF_COMMENT)] + source[
        source.index(HANDOFF_COMMENT):].replace(HANDOFF_OLD, HANDOFF_NEW, 1)
    source = source.replace(MOUNT, MOUNT + '\n' + ROUTE_ADDITION, 1)
    assert_install(source)
    return source


def selftest():
    runtime = RUNTIME_LOCAL.read_text(encoding="utf-8")
    ast.parse(runtime, filename=RUNTIME)
    if 'endswith(tuple(TEXT_EXTENSIONS))' not in runtime:
        raise RuntimeError("REPAIR_SOURCE_FIX_MISSING_IN_REPO")
    print("REPAIR_V7_REPOSITORY_SOURCE_PASS", flush=True)


def probe():
    results=[]
    for i in range(4):
        url=BASE + HEALTH_PATH + "?iteration=" + str(i)
        with urllib.request.urlopen(urllib.request.Request(
                url,headers={"Cache-Control":"no-store"}),timeout=25) as response:
            if response.status!=200:
                raise RuntimeError("REPAIR_V7_HEALTH_HTTP")
            data=json.load(response)
        if (data.get("schema")!="swrlz-repair-in-memory-runtime-v7"
            or data.get("loadedTupleSuffix") is not True
            or data.get("loadedModule")!="html_project_agent_runtime_v1"
            or data.get("handoff")!="disabled-for-existing-projects"
            or data.get("approval")!="required"):
            raise RuntimeError("REPAIR_V7_LOADED_RUNTIME_NOT_VERIFIED: " + repr(data))
        results.append({"loadedTupleSuffix":data["loadedTupleSuffix"],
                        "loadedModule":data["loadedModule"]})
    print("REPAIR_V7_LIVE_LOADED_BYTECODE_VERIFIED",json.dumps(results),flush=True)


def release(mode):
    selftest()
    if mode=="selftest":
        return
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
    token=os.getenv("HF_TOKEN") or None
    api=HfApi(token=token)
    revision=str(api.repo_info(SPACE,repo_type="space").sha)
    originals={}
    for name in (STATION,RUNTIME):
        originals[name]=Path(hf_hub_download(
            SPACE,name,repo_type="space",revision=revision,token=token)).read_bytes()
    if originals[RUNTIME]!=RUNTIME_LOCAL.read_bytes():
        raise RuntimeError("REPAIR_V7_HELPER_SOURCE_DRIFT")
    proposed=patch_station(originals[STATION].decode("utf-8")).encode("utf-8")
    print("REPAIR_V7_CAS_PREFLIGHT",json.dumps({
        "revision":revision,"before":sha(originals[STATION]),
        "after":sha(proposed),"runtime":sha(originals[RUNTIME]),
        "needsUpdate":originals[STATION]!=proposed
    }),flush=True)
    if mode=="preflight":
        return
    if mode=="verify":
        if originals[STATION]!=proposed:
            raise RuntimeError("REPAIR_V7_STATION_SOURCE_NOT_DEPLOYED")
        probe()
        print("REPAIR_V7_VERIFIED_REVISION",revision,flush=True)
        return
    if mode!="publish" or not token or os.getenv("SWRLZ_REPAIR_RUNTIME_V7_APPROVED")!="1":
        raise PermissionError("REPAIR_V7_RELEASE_NOT_APPROVED")
    if originals[STATION]==proposed:
        probe()
        print("REPAIR_V7_ALREADY_LIVE",revision,flush=True)
        return
    if str(api.repo_info(SPACE,repo_type="space").sha)!=revision:
        raise RuntimeError("REPAIR_V7_CONCURRENT_SOURCE_UPDATE")
    def addition(raw):
        return CommitOperationAdd(path_in_repo=STATION,path_or_fileobj=io.BytesIO(raw))
    committed=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=revision,
        operations=[addition(proposed)],
        commit_message="fix(§C): verify loaded repair bytecode and suppress fresh-HTML handoff").oid
    print("REPAIR_V7_SPACE_COMMITTED",committed,flush=True)
    try:
        readback=Path(hf_hub_download(
            SPACE,STATION,repo_type="space",revision=committed,token=token)).read_bytes()
        if readback!=proposed:
            raise RuntimeError("REPAIR_V7_SOURCE_READBACK_MISMATCH")
        print("REPAIR_V7_SOURCE_READBACK_PASS",committed,flush=True)
        api.restart_space(SPACE)
        for attempt in range(85):
            try:
                probe()
                print("REPAIR_V7_DEPLOYED_EXECUTION_VERIFIED",committed,flush=True)
                return
            except Exception as exc:
                if attempt%10==0:
                    print("REPAIR_V7_BOOT_PENDING",attempt,type(exc).__name__,flush=True)
                if attempt==84:
                    raise RuntimeError("REPAIR_V7_LOADED_CODE_NOT_VERIFIED") from exc
                time.sleep(8)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==committed:
            reverted=api.create_commit(
                repo_id=SPACE,repo_type="space",parent_commit=committed,
                operations=[addition(originals[STATION])],
                commit_message="rollback(§C): new repair interpreter did not pass loaded-code probe").oid
            print("REPAIR_V7_ROLLED_BACK",reverted,flush=True)
            api.restart_space(SPACE)
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("selftest","preflight","publish","verify"))
    release(parser.parse_args().mode)
