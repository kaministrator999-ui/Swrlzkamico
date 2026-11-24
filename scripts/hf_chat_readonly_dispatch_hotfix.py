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
    old = "            event_source=_generate(payload)\n"
    new = "            event_source=dispatch(model_id,payload,_generate,_stock_generate,_large_generate,None,forge_context=None)\n"
    tree = ast.parse(source)
    nodes = [n for n in ast.walk(tree) if isinstance(n, ast.If) and ast.unparse(n.test) == "_swrlz_execution_continuity.read_only(payload)"]
    if len(nodes) != 1:
        raise RuntimeError("READ_ONLY_BRANCH_DRIFT")
    node = nodes[0]
    lines = source.splitlines(keepends=True)
    matches = [n.lineno-1 for n in node.body if isinstance(n, ast.Assign) and ast.unparse(n) == "event_source = _generate(payload)"]
    if len(matches) != 1 or lines[matches[0]] != old:
        raise RuntimeError("READ_ONLY_GENERATOR_DRIFT")
    lines[matches[0]] = new
    result = "".join(lines)
    ast.parse(result)
    return result

def selftest():
    source = """def worker(payload, model_id):
        if _swrlz_execution_continuity.read_only(payload):
            event_source=_generate(payload)
        return event_source
"""
    patched = patch_station(source)
    from types import SimpleNamespace
    calls = []
    def dispatch(model,payload,base,stock,large,coder,forge_context=None):
        assert base is None and coder is None and forge_context is None
        calls.append(model)
        return stock(payload)
    ns = {"_swrlz_execution_continuity":SimpleNamespace(read_only=lambda p:True),
          "_generate":None,"_stock_generate":lambda p:iter(["report"]),
          "_large_generate":None,"dispatch":dispatch}
    exec(compile(patched,"station-test","exec"),ns)
    assert list(ns["worker"]({},"stock")) == ["report"]
    assert calls == ["stock"]
    print("READ_ONLY_DISPATCH_SELFTEST_PASS",flush=True)


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
    if HELPER not in paths:
        raise RuntimeError("EXECUTION_HELPER_MISSING")
    previous = Path(hf_hub_download(SPACE,STATION,repo_type="space",
                                   revision=revision,token=token)).read_bytes()
    patched = patch_station(previous.decode("utf-8")).encode("utf-8")
    helper = Path(hf_hub_download(SPACE,HELPER,repo_type="space",revision=revision,token=token)).read_bytes()
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
            CommitOperationAdd(path_in_repo=STATION,path_or_fileobj=io.BytesIO(patched))],
        commit_message="fix(§C): route read-only reports through model dispatcher").oid
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
                                       path_or_fileobj=io.BytesIO(previous))],
                commit_message="rollback(§C): execution continuity validation failed").oid
            print("EXECUTION_CONTINUITY_ROLLBACK",rollback,flush=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("selftest","preflight","publish"))
    main(parser.parse_args().mode)
