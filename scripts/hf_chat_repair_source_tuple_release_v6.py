#!/usr/bin/env python3
"""CAS release of §C repair-source str.endswith tuple fix to Hugging Face.

Changes one runtime helper only. Requires exact source match and owner-approved
release job, validates readback, restarts the Space, and rolls back on failed
live health. Does not edit a project or authorize a GitHub write.
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
TARGET = "html_project_agent_runtime_v1.py"
LOCAL = Path("api/html_project_agent_runtime_v1.py")
BEFORE = "if not rel.lower().endswith(TEXT_EXTENSIONS):"
AFTER = "if not rel.lower().endswith(tuple(TEXT_EXTENSIONS)):"
HEALTHS = (
    "/api/html-project-agent-v1/health",
    "/api/html-existing-repair-v5/route-health",
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def selftest():
    source = LOCAL.read_text(encoding="utf-8")
    ast.parse(source, filename=TARGET)
    if source.count(AFTER) != 1 or BEFORE in source:
        raise RuntimeError("TUPLE_FIX_SOURCE_INTEGRITY")
    print("TUPLE_FIX_SOURCE_SELFTEST_PASS", flush=True)


def health():
    for path in HEALTHS:
        request = urllib.request.Request(
            BASE + path, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(request, timeout=22) as response:
            if response.status != 200:
                raise RuntimeError("LIVE_HEALTH_HTTP_" + path)
            data = json.loads(response.read(3000))
        if path == HEALTHS[0]:
            if data.get("schema") != "swrlz-general-html-repair-agent-live-v1" or data.get("approval") != "required":
                raise RuntimeError("GENERAL_REPAIR_AGENT_NOT_LIVE")
        else:
            if (data.get("schema") != "swrlz-existing-repair-route-v5"
                    or data.get("namedProjectResolved") is not True
                    or data.get("repairIntentRecognized") is not True):
                raise RuntimeError("NAMED_PROJECT_REPAIR_ROUTE_NOT_LIVE")


def run(mode):
    selftest()
    if mode == "selftest":
        return
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
    token = os.getenv("HF_TOKEN") or None
    api = HfApi(token=token)
    rev = str(api.repo_info(SPACE, repo_type="space").sha)
    original = Path(hf_hub_download(
        SPACE, TARGET, repo_type="space", revision=rev,
        token=token)).read_bytes()
    candidate = LOCAL.read_bytes()
    source = candidate.decode("utf-8")
    expected_old = source.replace(AFTER, BEFORE, 1).encode("utf-8")
    if original not in (expected_old, candidate):
        # This historical release remains a read-only compatibility preflight
        # for later repair-agent upgrades. The v8 release owns all source
        # pinning and deployment checks; never overwrite it via v6.
        if (mode == "preflight" and AFTER.encode("utf-8") in original
                and AFTER.encode("utf-8") in candidate):
            ast.parse(original.decode("utf-8"), filename=TARGET)
            print("TUPLE_FIX_V6_NEWER_RUNTIME_COMPATIBLE", rev, flush=True)
            return
        raise RuntimeError("PRODUCTION_RUNTIME_SOURCE_DRIFT")
    changed = original != candidate
    print("TUPLE_FIX_PREFLIGHT", json.dumps({
        "revision": rev, "target": TARGET,
        "originalSha256": digest(original),
        "candidateSha256": digest(candidate), "needsUpdate": changed,
    }), flush=True)
    if mode == "preflight":
        return
    if mode == "verify":
        if changed:
            raise RuntimeError("TUPLE_FIX_NOT_DEPLOYED")
        health()
        print("TUPLE_FIX_LIVE_SOURCE_AND_HEALTH_VERIFIED", rev, flush=True)
        return
    if mode != "publish" or not token or os.getenv("SWRLZ_TUPLE_REPAIR_APPROVED") != "1":
        raise PermissionError("TUPLE_REPAIR_RELEASE_UNAUTHORIZED")
    if not changed:
        health()
        print("TUPLE_FIX_ALREADY_LIVE", rev, flush=True)
        return
    if str(api.repo_info(SPACE, repo_type="space").sha) != rev:
        raise RuntimeError("CONCURRENT_HF_EDIT")
    def add(raw):
        return CommitOperationAdd(path_in_repo=TARGET, path_or_fileobj=io.BytesIO(raw))
    committed = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=rev,
        operations=[add(candidate)],
        commit_message="fix(§C): read verified HTML project source with tuple suffixes").oid
    print("TUPLE_FIX_SPACE_COMMITTED", committed, flush=True)
    try:
        readback = Path(hf_hub_download(
            SPACE, TARGET, repo_type="space", revision=committed,
            token=token)).read_bytes()
        if readback != candidate:
            raise RuntimeError("TUPLE_FIX_SOURCE_READBACK_MISMATCH")
        print("TUPLE_FIX_SOURCE_READBACK_PASS", committed, flush=True)
        api.restart_space(SPACE)
        for attempt in range(80):
            try:
                health()
                print("TUPLE_FIX_DEPLOYED_LIVE_HEALTH_VERIFIED", committed, flush=True)
                return
            except Exception as exc:
                if attempt % 10 == 0:
                    print("TUPLE_FIX_HEALTH_PENDING", attempt, type(exc).__name__, flush=True)
                if attempt == 79:
                    raise RuntimeError("TUPLE_FIX_LIVE_HEALTH_FAILED") from exc
                time.sleep(8)
    except Exception:
        if str(api.repo_info(SPACE, repo_type="space").sha) == committed:
            restored = api.create_commit(
                repo_id=SPACE, repo_type="space", parent_commit=committed,
                operations=[add(original)],
                commit_message="rollback(§C): repair runtime tuple fix health not verified").oid
            print("TUPLE_FIX_ROLLED_BACK", restored, flush=True)
            api.restart_space(SPACE)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("selftest", "preflight", "publish", "verify"))
    run(parser.parse_args().mode)
