#!/usr/bin/env python3
"""CAS-protected §C router and source-checkpoint auto-continuation release.

Only two same-Space files: Station routing and an isolated pure helper.
No model/token-limit, GitHub, authorization, thread schema, or §E edits.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import io
import os
import time
import urllib.request
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
STATION = "station.py"
HELPER = "execution_continuity_v1.py"
SOURCE = Path("api/execution_continuity_v1.py")
MARK = "swrlz-execution-continuity-router-v1"
IMPORT_ANCHOR = "ROOT=Path(__file__).resolve().parent"
ROUTE_ANCHOR = (
    "        elif forge_context is not None:\n"
    "            event_source=dispatch(model_id,payload,_generate,"
    "_stock_generate,_large_generate,_coder_generate,forge_context=forge_context)"
)
ROUTE_REPLACEMENT = (
    "        elif _swrlz_execution_continuity.read_only(payload):\n"
    "            # swrlz-execution-continuity-router-v1: owner-grounded\n"
    "            # inspection must never silently enter code generation.\n"
    "            payload['presentationIntent']='PROSE'\n"
    "            payload['programming']={'codingTask':False,"
    "'source':'verified-read-only-inspection'}\n"
    "            payload['responseDirective']=(str(payload.get('responseDirective') or '')"
    "+'\\nRead-only inspection: report only actual source and HTTP evidence. '"
    "'Do not generate source code, prepare mutations, or claim browser execution. '"
    "'Give one clear final report with concise headings for Verified checks, '"
    "'Findings, Unverified behavior, and Next action. Exclude intermediate '"
    "'waiting messages, abandoned plans and activity-log repetition.')\n"
    "            event_source=_generate(payload)\n"
    "        elif forge_context is not None:\n"
    "            event_source=dispatch(model_id,payload,_generate,"
    "_stock_generate,_large_generate,_coder_generate,forge_context=forge_context)"
)
WRAP = "        event_source=_swrlz_execution_continuity.stream(payload,_coder_generate,event_source)\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def patch_station(source):
    if MARK in source:
        raise RuntimeError("EXECUTION_ROUTER_ALREADY_PRESENT")
    if source.count(IMPORT_ANCHOR) != 1 or source.count(ROUTE_ANCHOR) != 1:
        candidates = [
            str(i + 1) + ":" + line.strip()[:150]
            for i,line in enumerate(source.splitlines())
            if ("forge_context" in line or "event_source=dispatch(" in line
                or "event_source=_coder_generate" in line)
        ][:20]
        raise RuntimeError("LIVE_STATION_ROUTING_SOURCE_DRIFT anchors=" +
                           str((source.count(IMPORT_ANCHOR), source.count(ROUTE_ANCHOR))) +
                           " context=" + repr(candidates))
    source = source.replace(IMPORT_ANCHOR,
         "import execution_continuity_v1 as _swrlz_execution_continuity\n" + IMPORT_ANCHOR, 1)
    source = source.replace(ROUTE_ANCHOR, ROUTE_REPLACEMENT, 1)
    tree = ast.parse(source, filename=STATION)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = ast.get_source_segment(source, node.test) or ""
            if test == "_swrlz_execution_continuity.read_only(payload)":
                found.append(node)
    if len(found) != 1:
        raise RuntimeError("EXECUTION_ROUTER_ROUTE_BRANCH_NOT_UNIQUE")
    lines = source.splitlines(keepends=True)
    lines.insert(found[0].end_lineno, WRAP)
    patched = "".join(lines)
    ast.parse(patched, filename=STATION)
    if patched.count(MARK) != 1 or patched.count(WRAP) != 1:
        raise RuntimeError("EXECUTION_ROUTER_PATCH_INTEGRITY_FAILED")
    return patched


def selftest():
    raw = SOURCE.read_text(encoding="utf-8")
    ast.parse(raw, filename=HELPER)
    test_source = '''from pathlib import Path
ROOT=Path(__file__).resolve().parent
def worker(payload,forge_context,model_id):
        if False:
            pass
        elif forge_context is not None:
            event_source=dispatch(model_id,payload,_generate,_stock_generate,_large_generate,_coder_generate,forge_context=forge_context)
        elif isinstance(payload.get("codeContinuation"),dict):
            event_source=_coder_generate(payload)
        elif payload.get("verifiedWorkAnswer"):
            event_source=_generate(payload)
        else:
            event_source=_generate(payload)
        for event in event_source:
            yield event
'''
    patched = patch_station(test_source)
    assert patched.count(MARK) == 1
    assert patched.index(WRAP.strip()) < patched.index("        for event in event_source:")
    try:
        patch_station(patched)
    except RuntimeError:
        pass
    else:
        raise AssertionError("DOUBLE_PATCH_NOT_BLOCKED")
    print("EXECUTION_CONTINUITY_SELFTEST_PASS", digest(SOURCE.read_bytes()), flush=True)


def health():
    request = urllib.request.Request(
        BASE + "/chat/%C2%A7wyrlz?__execution_continuity=1",
        headers={"Cache-Control":"no-cache"})
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            raise RuntimeError("LIVE_CHAT_HEALTH_UNVERIFIED")
        response.read(500)


def main(mode):
    selftest()
    if mode == "selftest":
        return
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
    token = os.getenv("HF_TOKEN") or None
    api = HfApi(token=token)
    revision = str(api.repo_info(SPACE,repo_type="space").sha)
    paths = set(api.list_repo_files(SPACE,repo_type="space",revision=revision))
    if HELPER in paths:
        raise RuntimeError("EXISTING_EXECUTION_HELPER_MUST_BE_RECONCILED")
    previous = Path(hf_hub_download(SPACE,STATION,repo_type="space",
                                   revision=revision,token=token)).read_bytes()
    patched = patch_station(previous.decode("utf-8")).encode("utf-8")
    helper = SOURCE.read_bytes()
    print("EXECUTION_CONTINUITY_PREFLIGHT", revision,
          {STATION:digest(patched),HELPER:digest(helper)}, flush=True)
    if mode == "preflight":
        return
    if (mode != "publish" or not token or
        os.environ.get("SWRLZ_EXECUTION_CONTINUITY_APPROVED") != "1"):
        raise PermissionError("EXPLICIT_SCOPED_RELEASE_APPROVAL_REQUIRED")
    if str(api.repo_info(SPACE,repo_type="space").sha) != revision:
        raise RuntimeError("CONCURRENT_HF_REVISION_CHANGED")
    changed = api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=revision,
        operations=[
            CommitOperationAdd(path_in_repo=STATION,path_or_fileobj=io.BytesIO(patched)),
            CommitOperationAdd(path_in_repo=HELPER,path_or_fileobj=io.BytesIO(helper))],
        commit_message="fix(§C): honor read-only inspection and auto-resume code checkpoints").oid
    print("EXECUTION_CONTINUITY_HF_COMMITTED",changed,flush=True)
    try:
        for path,expected in ((STATION,patched),(HELPER,helper)):
            fetched = Path(hf_hub_download(SPACE,path,repo_type="space",
                                          revision=changed,token=token)).read_bytes()
            if fetched != expected:
                raise RuntimeError("PUBLISHED_HELPER_BYTES_DIFFER:"+path)
        for attempt in range(24):
            try:
                health()
                print("EXECUTION_CONTINUITY_LIVE_HEALTH_VERIFIED",changed,flush=True)
                return
            except (RuntimeError,OSError,TimeoutError) as exc:
                if attempt == 23:
                    raise RuntimeError("LIVE_HEALTH_NOT_VERIFIED") from exc
                time.sleep(10)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha) == changed:
            rollback = api.create_commit(repo_id=SPACE,repo_type="space",
                parent_commit=changed,operations=[
                    CommitOperationAdd(path_in_repo=STATION,
                                       path_or_fileobj=io.BytesIO(previous)),
                    CommitOperationDelete(path_in_repo=HELPER)],
                commit_message="rollback(§C): execution continuity validation failed").oid
            print("EXECUTION_CONTINUITY_ROLLBACK",rollback,flush=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("selftest","preflight","publish"))
    main(parser.parse_args().mode)
