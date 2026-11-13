#!/usr/bin/env python3
"""Guarded one-file fix for §C Qwen3.5-9B ordinary-response context budgeting.

Patch current live file only; never deploy a stale project snapshot, touch §E,
change HF hardware, change model weights, or truncate source/user prompts.
Authoritative prior source is preserved byte-for-byte for rollback.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from typing import Any
import urllib.request

from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download

SPACE = "kamiloki/Swyrlz"
PATH = "programming_repair_context.py"
MODEL_FILE = "qwen35_single_runtime.py"
WORK = Path(tempfile.mkdtemp(prefix="swrlz-qwen35-budget-"))
ORIGINAL = WORK / "before.py"
CANDIDATE = WORK / "after.py"
STATE = WORK / "release.json"
ORIGINAL_SHORT = 'return {"tier":"normal","tokens":4096,"stagedDelivery":False}'
ORIGINAL_DEFAULT = ORIGINAL_SHORT
PATCH_SHORT = 'return {"tier":"normal","tokens":(4096 if programming.get("codingTask") else 512),"stagedDelivery":False}'
PATCH_DEFAULT = 'return {"tier":"normal","tokens":(4096 if coding else 1024),"stagedDelivery":False}'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def api() -> HfApi:
    token = os.environ.get("HF_TOKEN", "").strip()
    if len(token) < 12:
        raise RuntimeError("Missing guarded HF_TOKEN; no mutation")
    return HfApi(token=token)


def candidate(source: str) -> str:
    # Two exact normal-tier results: one for explicit concise requests,
    # another after all large-delivery and code-budget decisions.
    old = ORIGINAL_DEFAULT
    if source.count(old) != 2:
        raise RuntimeError("LIVE_BUDGET_POLICY_SOURCE_DRIFT")
    if "def response_budget(" not in source or "def source_sized_budget(" not in source:
        raise RuntimeError("Expected owner-scoped budgeting not present")
    before_short, remainder = source.split(old, 1)
    middle, after_default = remainder.split(old, 1)
    if 'short or any(limit<=500 for limit in word_limits)' not in before_short:
        raise RuntimeError("Normal-short budget branch differs")
    if 'return {"tier":"large","tokens":16384,"stagedDelivery":True}' not in middle:
        raise RuntimeError("Substantial-project budget path missing")
    if 'return {"tier":"project","tokens":8192,"stagedDelivery":coding}' not in middle:
        raise RuntimeError("Project budget path missing")
    replacement = before_short + PATCH_SHORT + middle + PATCH_DEFAULT + after_default
    ast.parse(replacement, filename=PATH)
    return replacement


def test_budget(source: str) -> None:
    # Execute only the response_budget function, with an isolated stub of the
    # unrelated expensive context-expansion helper.
    parsed = ast.parse(source)
    fn = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == "response_budget")
    isolated = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(isolated)
    ns = {"re": re, "Any": Any, "expanded_project_delivery": lambda programming, prompt: False}
    exec(compile(isolated, "<response-budget-unit>", "exec"), ns)
    budget = ns["response_budget"]
    assert budget({}, "Hey how are you?")["tokens"] == 1024
    assert budget({}, "Please answer in one sentence")["tokens"] == 512
    assert budget({"codingTask": True}, "Write a Python function")["tokens"] == 4096
    assert budget({"codingTask": True}, "Write a huge comprehensive application")["tokens"] == 16384
    # Reproduce the screenshot's mandatory prompt size, with no truncation.
    input_tokens = 4938
    context, safety = 8192, 128
    normal = budget({}, "Hey how are you?")["tokens"]
    assert input_tokens <= context - safety - normal
    assert input_tokens > context - safety - 4096
    # Source-sensitive budget and source-preservation code are outside this
    # exact two-return-value patch; assert those anchors remain untouched.
    assert "def source_sized_budget(" in source
    assert "def preserve_existing_source(" in source
    print(json.dumps({"status": "PASS", "greetingOutputTokens": normal,
                      "greetingInputCapacity": context - safety - normal,
                      "mandatoryInputFromScreenshot": input_tokens,
                      "shortOutputTokens": 512,
                      "codingDefaultUnchanged": True}), flush=True)


def prepare() -> dict:
    hub = api()
    current = hub.repo_info(SPACE, repo_type="space")
    names = set(hub.list_repo_files(SPACE, repo_type="space", revision=current.sha))
    assert PATH in names and MODEL_FILE in names, "Live 9B source not present"
    current_model = Path(hf_hub_download(SPACE, MODEL_FILE, repo_type="space",
                                         revision=current.sha, token=hub.token)).read_text("utf-8")
    assert 'Qwen3.5-9B' in current_model, "Space is not current 9B deployment"
    data = Path(hf_hub_download(SPACE, PATH, repo_type="space", revision=current.sha,
                                token=hub.token)).read_bytes()
    after = candidate(data.decode("utf-8")).encode("utf-8")
    test_budget(after.decode("utf-8"))
    ORIGINAL.write_bytes(data)
    CANDIDATE.write_bytes(after)
    record = {"space": SPACE, "source": current.sha,
              "oldSha256": digest(data), "newSha256": digest(after),
              "operation": "exact-single-file-change", "hardware": "unchanged"}
    STATE.write_text(json.dumps(record), "utf-8")
    print(json.dumps({"status": "BUDGET_CANDIDATE_TESTED", **record}), flush=True)
    return record


def publish_and_verify() -> None:
    if os.environ.get("SWRLZ_BUDGET_APPROVED") != "1":
        raise RuntimeError("No explicit guarded hotfix approval")
    hub = api()
    state = prepare()
    oldrev = state["source"]
    if hub.repo_info(SPACE, repo_type="space").sha != oldrev:
        raise RuntimeError("Concurrent Space release detected, not changing source")
    res = hub.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=oldrev,
        operations=[CommitOperationAdd(path_in_repo=PATH, path_or_fileobj=str(CANDIDATE))],
        commit_message="§C Qwen3.5-9B: restore conversational token room in 8K context",
    )
    newrev = str(res.oid)
    print(json.dumps({"status": "BUDGET_SOURCE_PUBLISHED", "revision": newrev,
                      "previousRevision": oldrev}), flush=True)
    try:
        latest = hub.repo_info(SPACE, repo_type="space").sha
        if latest != newrev:
            raise RuntimeError("Live Space changed during budget verification")
        verified = Path(hf_hub_download(SPACE, PATH, repo_type="space",
                                        revision=newrev, token=hub.token)).read_bytes()
        if digest(verified) != state["newSha256"]:
            raise RuntimeError("Published hotfix bytes failed integrity check")
        test_budget(verified.decode("utf-8"))
        # The immutable resident-model module must remain exactly unchanged.
        for name in (MODEL_FILE, "app.py", "chat_vision.py", "model_router.py"):
            before = Path(hf_hub_download(SPACE, name, repo_type="space", revision=oldrev,
                                           token=hub.token)).read_bytes()
            after = Path(hf_hub_download(SPACE, name, repo_type="space", revision=newrev,
                                          token=hub.token)).read_bytes()
            if digest(before) != digest(after):
                raise RuntimeError("Out-of-scope module changed: " + name)
        print(json.dumps({"status": "QWEN35_BUDGET_LIVE_SOURCE_VERIFIED",
                          "revision": newrev, "greetingInputBudget": 7040,
                          "modelUnchanged": True}), flush=True)
    except Exception:
        if hub.repo_info(SPACE, repo_type="space").sha == newrev:
            rollback = hub.create_commit(
                repo_id=SPACE, repo_type="space", parent_commit=newrev,
                operations=[CommitOperationAdd(path_in_repo=PATH,
                                               path_or_fileobj=str(ORIGINAL))],
                commit_message="Rollback §C 9B output budget hotfix to exact prior bytes")
            print(json.dumps({"status": "BUDGET_ROLLBACK_APPLIED",
                              "rollbackRevision": str(rollback.oid)}), flush=True)
        raise


if __name__ == "__main__":
    if sys.argv[1:] != ["publish"]:
        raise SystemExit("Only guarded publish with preflight+rollback is supported")
    publish_and_verify()
