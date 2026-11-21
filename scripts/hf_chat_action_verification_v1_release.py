#!/usr/bin/env python3
"""Exact-source guarded rollout of §C generated-action advice verification.

Preflight takes immutable live Hugging Face Space bytes, patches a candidate,
compiles it, and records checksums. Publishing rejects concurrent Space edits,
uploads exactly two files, verifies readback, and rolls back on readback failure.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
ENGINE = "lfm2_700m_engine.py"
HELPER = "api/action_verification_v1.py"
ROOT = Path("reports/swrlz-action-verification-v1")
MARK = "swrlz-action-verification-runtime-v1"
APPEND = '''
# swrlz-action-verification-runtime-v1
# Existing tool routing stays authoritative; this is one bounded prose review.
import os as _swrlz_action_os
_swrlz_original_generate_events_action_v1 = generate_events

def generate_events(payload):
    if (not isinstance(payload, dict)
            or payload.get("_actionVerificationPass")
            or _swrlz_action_os.environ.get(
                "SWRLZ_ACTION_VERIFICATION_ENABLED", "1"
            ).strip().lower() in ("0", "false", "off")):
        yield from _swrlz_original_generate_events_action_v1(payload)
        return
    from api.action_verification_v1 import supervise, available_context
    from stop_transport import generation_cancelled
    # Preserve existing recursive tool-recovery/code routes without recursion.
    def _candidate(entry):
        return _swrlz_original_generate_events_action_v1(
            {**entry, "_actionVerificationPass": True})
    yield from supervise(payload, _candidate, available_context,
                         generation_cancelled)
'''


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def patch(original: bytes) -> bytes:
    text = original.decode("utf-8")
    if MARK in text:
        raise RuntimeError("ACTION_VERIFICATION_ALREADY_INSTALLED")
    tree = ast.parse(text, filename=ENGINE)
    names = [node for node in tree.body
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
             and node.name == "generate_events"]
    if len(names) != 1 or not isinstance(names[0], ast.FunctionDef):
        related = [(getattr(node, "name", ""), getattr(node, "lineno", 0),
                    type(node).__name__)
                   for node in tree.body
                   if "generat" in str(getattr(node, "name", "")).lower()]
        print("ACTION_CHECK_OWNER_DIAGNOSTIC " + json.dumps({
            "generate_events_defs": len(names),
            "related_entrypoints": related[:25],
            "source_bytes": len(original)}), flush=True)
        raise RuntimeError("GENERATION_OWNER_SOURCE_DRIFT")
    output = (text.rstrip() + "\n\n" + APPEND.lstrip()).encode("utf-8")
    compile(output.decode("utf-8"), ENGINE, "exec")
    return output


def stage():
    from huggingface_hub import HfApi, hf_hub_download
    token = os.environ.get("HF_TOKEN")
    api = HfApi(token=token)
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    if len(revision) != 40:
        raise RuntimeError("EXACT_SPACE_REVISION_UNAVAILABLE")
    paths = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if HELPER in paths:
        raise RuntimeError("HELPER_ALREADY_ON_SPACE_VERIFY_EXISTING_RUNTIME")
    original = Path(hf_hub_download(SPACE, ENGINE, repo_type="space",
                                    revision=revision, token=token)).read_bytes()
    helper = Path(HELPER).read_bytes()
    compile(helper.decode("utf-8"), HELPER, "exec")
    changed = patch(original)
    manifest = {
        "contract": MARK, "space": SPACE, "revision": revision,
        "before": {ENGINE: digest(original)},
        "after": {ENGINE: digest(changed), HELPER: digest(helper)},
        "paths": [ENGINE, HELPER],
        "modelWeightsChanged": False, "accountDataChanged": False,
        "engineSourceChanged": True
    }
    (ROOT / "before").mkdir(parents=True, exist_ok=True)
    (ROOT / "after" / "api").mkdir(parents=True, exist_ok=True)
    (ROOT / "before" / ENGINE).write_bytes(original)
    (ROOT / "after" / ENGINE).write_bytes(changed)
    (ROOT / "after" / HELPER).write_bytes(helper)
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("ACTION_CHECK_PREFLIGHT " + json.dumps(manifest, sort_keys=True),
          flush=True)
    return manifest


def deploy():
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
    if os.environ.get("SWRLZ_ACTION_VERIFICATION_DEPLOY_APPROVED") != "yes":
        raise PermissionError("DEPLOY_APPROVAL_REQUIRED")
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise PermissionError("HF_TOKEN_MISSING")
    manifest = json.loads((ROOT / "manifest.json").read_text())
    api = HfApi(token=token)
    current = str(api.repo_info(SPACE, repo_type="space").sha)
    if current != manifest["revision"]:
        raise RuntimeError("CONCURRENT_SPACE_SOURCE_CHANGED")
    source = Path(hf_hub_download(SPACE, ENGINE, repo_type="space",
                                  revision=current, token=token)).read_bytes()
    if digest(source) != manifest["before"][ENGINE]:
        raise RuntimeError("EXACT_ENGINE_SOURCE_CHANGED")
    changed = patch(source)
    helper = Path(HELPER).read_bytes()
    if digest(changed) != manifest["after"][ENGINE] or digest(helper) != manifest["after"][HELPER]:
        raise RuntimeError("CANDIDATE_CHANGED_AFTER_PREFLIGHT")
    published = None
    try:
        commit = api.create_commit(
            repo_id=SPACE, repo_type="space", parent_commit=current,
            operations=[
                CommitOperationAdd(path_in_repo=ENGINE,
                                   path_or_fileobj=io.BytesIO(changed)),
                CommitOperationAdd(path_in_repo=HELPER,
                                   path_or_fileobj=io.BytesIO(helper)),
            ],
            commit_message="feat(§C): check generated recommendations before delivery",
        )
        published = str(commit.oid)
        for name, expected in ((ENGINE, changed), (HELPER, helper)):
            actual = Path(hf_hub_download(
                SPACE, name, repo_type="space", revision=published,
                token=token)).read_bytes()
            if actual != expected:
                raise RuntimeError("ACTION_CHECK_SOURCE_READBACK_MISMATCH:" + name)
        print("ACTION_CHECK_SOURCE_PUBLISHED " + json.dumps({
            "previous": current, "revision": published,
            "sourceVerified": True, "liveBehaviorVerified": False,
            "files": [ENGINE, HELPER]}), flush=True)
    except Exception:
        if published and str(api.repo_info(SPACE, repo_type="space").sha) == published:
            reverted = api.create_commit(
                repo_id=SPACE, repo_type="space", parent_commit=published,
                operations=[
                    CommitOperationAdd(path_in_repo=ENGINE,
                                       path_or_fileobj=io.BytesIO(source)),
                    CommitOperationDelete(path_in_repo=HELPER),
                ],
                commit_message="rollback(§C): generated action verification")
            print("ACTION_CHECK_ROLLBACK " + str(reverted.oid), flush=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["preflight", "deploy"])
    mode = parser.parse_args().mode
    if mode == "preflight":
        stage()
    else:
        deploy()
