#!/usr/bin/env python3
"""CAS-scoped installation of §C's model-driven exact patch repair agent.

Only Station routing, the existing owner-approved repair helper and three
bounded Python modules are updated in the existing Hugging Face Space.
No project source is changed by this release. Roll back if live health fails.
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
HELPER = "html_project_repair_v1.py"
MARK = "swrlz-general-html-repair-agent-live-v1"
HEALTH = "/api/html-project-agent-v1/health"
IMPORT_ANCHOR = "import html_project_repair_v1 as _swrlz_project_repair"
ROUTE_ANCHOR = "event_source=_swrlz_project_repair.events(payload)"
OWNER_ANCHOR = 'payload["activeHtmlProject"]=html_project_ref'
MOUNT = 'app.mount("/chat/§wyrlz/assets",StaticFiles(directory=ROOT/"chat/§wyrlz/assets"),name="chat-assets")'
FILES = {
    HELPER: Path("api/html_project_repair_v1.py"),
    "html_project_agent_v1.py": Path("api/html_project_agent_v1.py"),
    "html_project_agent_runtime_v1.py": Path("api/html_project_agent_runtime_v1.py"),
    "project_code_targeted_repair_v1.py": Path("scripts/project_code_targeted_repair_v1.py"),
    "chat/§wyrlz/assets/html-project-publish-review-v1.js": Path("chat/html-project-publish-review-v1.js"),
}
ROUTE = '''
# swrlz-general-html-repair-agent-live-v1
@app.get("/api/html-project-agent-v1/health",include_in_schema=False)
def _swrlz_model_html_agent_health():
    from html_project_agent_v1 import VERSION
    return {"schema": "swrlz-general-html-repair-agent-live-v1",
            "engine": VERSION, "source": "owner-verified",
            "approval": "required", "deployedProjectChanges": False}
'''


def replace_one(source, old, new, label):
    if source.count(old) != 1:
        raise RuntimeError("SOURCE_DRIFT_" + label + "_" + str(source.count(old)))
    return source.replace(old, new, 1)


def patch_station(source):
    if MARK in source:
        # Existing deployments are valid during unrelated source-repair updates.
        # Refuse partial installations, but do not try to install twice.
        routes = (
            "event_source=_swrlz_model_repair.run(payload,_coder_generate)",
            "event_source=_swrlz_execute_model_repair_v7(payload,_coder_generate)",
        )
        required = (
            'payload["htmlRepairOwner"]=google_owner',
            'payload["htmlRepairThreadId"]=tid',
            '/api/html-project-agent-v1/health',
        )
        if (not any(route in source for route in routes)
                or any(anchor not in source for anchor in required)):
            raise RuntimeError("PARTIAL_AGENT_INSTALLATION")
        ast.parse(source, filename=STATION)
        return source
    source = replace_one(
        source, IMPORT_ANCHOR,
        IMPORT_ANCHOR + "\nimport html_project_agent_runtime_v1 as _swrlz_model_repair",
        "import")
    source = replace_one(
        source, ROUTE_ANCHOR,
        "event_source=_swrlz_model_repair.run(payload,_coder_generate)",
        "model_routing")
    source = replace_one(
        source, OWNER_ANCHOR,
        OWNER_ANCHOR
        + '\n            payload["htmlRepairOwner"]=google_owner'
        + '\n            payload["htmlRepairThreadId"]=tid',
        "server_owner_binding")
    source = replace_one(source, MOUNT, MOUNT + "\n" + ROUTE, "health")
    ast.parse(source, filename=STATION)
    return source


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selftest():
    sample = (
        "import html_project_repair_v1 as _swrlz_project_repair\n"
        + MOUNT + "\n"
        + "def run(payload):\n    if True:\n        " + ROUTE_ANCHOR + "\n"
        + "def source(payload,google_owner,tid,html_project_ref):\n"
        + "    if True:\n            " + OWNER_ANCHOR + "\n"
    )
    patched = patch_station(sample)
    assert MARK in patched and "htmlRepairOwner" in patched
    assert "_swrlz_model_repair.run(payload,_coder_generate)" in patched
    for target, path in FILES.items():
        data = path.read_bytes()
        if target.endswith(".py"):
            ast.parse(data.decode("utf-8"), filename=target)
    assert "def prepare_model(" in FILES[HELPER].read_text()
    assert "def run(payload, coder_generate):" in FILES["html_project_agent_runtime_v1.py"].read_text()
    print("GENERAL_HTML_REPAIR_AGENT_SELFTEST_PASS", flush=True)


def health():
    req = urllib.request.Request(BASE + HEALTH,
                                 headers={"Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=22) as resp:
        if resp.status != 200 or resp.headers.get("content-type","").split(";")[0].lower() != "application/json":
            raise RuntimeError("HEALTH_RESPONSE_INVALID")
        parsed = json.loads(resp.read(2000))
    if parsed != {
        "schema": MARK, "engine": "swrlz-html-repair-agent-v1",
        "source": "owner-verified", "approval": "required",
        "deployedProjectChanges": False,
    }:
        raise RuntimeError("LIVE_AGENT_NOT_INSTALLED")


def run(mode):
    selftest()
    if mode == "selftest":
        return
    from huggingface_hub import (
        HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete)
    token = os.getenv("HF_TOKEN") or None
    api = HfApi(token=token)
    rev = str(api.repo_info(SPACE, repo_type="space").sha)
    names = set(api.list_repo_files(SPACE, repo_type="space",revision=rev))
    originals = {}
    for filename in (STATION,*FILES):
        if filename in names:
            originals[filename] = Path(
                hf_hub_download(SPACE, filename, repo_type="space",
                                revision=rev, token=token)).read_bytes()
    if STATION not in originals or HELPER not in originals:
        raise RuntimeError("REQUIRED_PRODUCTION_SOURCE_MISSING")
    # The installed general agent legitimately adds MODEL_WORKFLOW. Only
    # reject a pre-existing helper when Station lacks the matching agent.
    if (MARK not in originals[STATION].decode("utf-8")
            and "MODEL_WORKFLOW =" in originals[HELPER].decode("utf-8")):
        raise RuntimeError("PRODUCTION_REPAIR_HELPER_ALREADY_CHANGED")
    patched = {
        STATION: patch_station(originals[STATION].decode("utf-8")).encode("utf-8")
    }
    for target, src in FILES.items():
        patched[target] = src.read_bytes()
    print("GENERAL_AGENT_PREFLIGHT",rev,
          {p:sha(data) for p,data in patched.items()},flush=True)
    if mode == "preflight":
        return
    if mode != "publish" or not token or os.getenv("SWRLZ_GENERAL_REPAIR_APPROVED")!="1":
        raise PermissionError("RELEASE_NOT_AUTHORIZED")
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:
        raise RuntimeError("CONCURRENT_PRODUCTION_EDIT")
    def add(path,raw):
        return CommitOperationAdd(path_in_repo=path,path_or_fileobj=io.BytesIO(raw))
    commit=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[add(p,raw) for p,raw in patched.items()],
        commit_message="feat(§C): deploy model-led source-preserving project repair agent").oid
    print("GENERAL_AGENT_SPACE_COMMITTED",commit,flush=True)
    try:
        for p,raw in patched.items():
            got=Path(hf_hub_download(SPACE,p,repo_type="space",
                 revision=commit,token=token)).read_bytes()
            if got!=raw:
                raise RuntimeError("SOURCE_READBACK_MISMATCH_"+p)
        print("GENERAL_AGENT_SOURCE_READBACK_PASS",commit,flush=True)
        api.restart_space(SPACE)
        print("GENERAL_AGENT_SPACE_RESTART_REQUESTED",commit,flush=True)
        for attempt in range(75):
            try:
                health()
                print("GENERAL_AGENT_LIVE_HEALTH_VERIFIED",commit,flush=True)
                return
            except Exception as exc:
                if attempt%10==0:
                    print("GENERAL_AGENT_HEALTH_PENDING",attempt,
                          type(exc).__name__,flush=True)
                if attempt==74:
                    raise RuntimeError("LIVE_AGENT_HEALTH_NOT_VERIFIED") from exc
                time.sleep(8)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==commit:
            restore = [add(p,raw) for p,raw in originals.items()]
            restore.extend(
                CommitOperationDelete(path_in_repo=p)
                for p in patched if p not in originals)
            rollback=api.create_commit(
                repo_id=SPACE,repo_type="space",parent_commit=commit,
                operations=restore,
                commit_message="rollback(§C): model repair agent live health failed").oid
            print("GENERAL_AGENT_ROLLED_BACK",rollback,flush=True)
            api.restart_space(SPACE)
        raise


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("mode",choices=("selftest","preflight","publish"))
    run(ap.parse_args().mode)
