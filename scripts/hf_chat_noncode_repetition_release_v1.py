#!/usr/bin/env python3
"""Scoped, CAS-protected live §C repetition guard release.

Wrap the current outermost model-event iterator, without touching weights,
native tokenizers, stream transport, user state, code-artifact validators or §E.
Never replace a live HF Space from a stale GitHub snapshot.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import io
import json
import os
import re
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
ENGINES = ("lfm2_700m_engine.py", "qwen_coder_engine.py")
HELPER = "api/noncode_repetition_guard_v1.py"
ROOT = Path("reports/swrlz-noncode-repetition-guard-v1")
MARK = "swrlz-noncode-repetition-stream-guard-v1"

WRAPPER = r'''

# swrlz-noncode-repetition-stream-guard-v1: outermost prose event boundary.
# Preserve all existing generation, candidate validation and route behavior.
_swrlz_pre_loop_guard_generate_events = generate_events


def generate_events(payload):
    from api.noncode_repetition_guard_v1 import RepetitionWatch, guard_eligible
    if not guard_eligible(payload):
        yield from _swrlz_pre_loop_guard_generate_events(payload)
        return
    watches = {"DELTA": RepetitionWatch(), "CANDIDATE_PREVIEW_DELTA": RepetitionWatch()}
    producer = _swrlz_pre_loop_guard_generate_events(payload)
    try:
        for item in producer:
            if not isinstance(item, dict):
                yield item
                continue
            kind = str(item.get("type") or "").upper()
            if kind == "CANDIDATE_PREVIEW_RESET":
                watches["CANDIDATE_PREVIEW_DELTA"].reset()
            watcher = watches.get(kind)
            evidence = watcher.observe(item.get("text") or "") if watcher else None
            if not evidence:
                yield item
                continue
            # Stop immediately instead of burning the remaining CPU/token
            # budget. Never accept an unverified lyric candidate as complete.
            if kind == "CANDIDATE_PREVIEW_DELTA":
                yield {"type": "CANDIDATE_PREVIEW_RESET", "attempt": item.get("attempt", 1)}
            yield {"type": "STATUS", "phase": "REPETITION_LOOP_STOPPED",
                   "reason": "Repeated non-code lines detected; generation ended early.",
                   "repetitionBlockSize": evidence["blockSize"],
                   "repetitionCycles": evidence["cycles"]}
            yield {"type": "CANDIDATE_VALIDATION", "validation": {
                "status": "INCOMPLETE", "accepted": False,
                "reasons": ["repetition-loop"], "verificationState": "UNVERIFIED_PARTIAL"}}
            yield {"type": "DELTA", "text":
                   "I stopped because the response began repeating itself. "
                   "That draft is not a verified finished answer; please ask me to retry."}
            yield {"type": "COMPLETED", "phase": "PARTIAL",
                   "repetitionGuardTriggered": True, "outputIncomplete": True}
            return
    finally:
        close = getattr(producer, "close", None)
        if callable(close):
            close()
'''


def checksum(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def patch_engine(source: str, path: str = "<engine>") -> str:
    if MARK in source:
        raise ValueError("LOOP_GUARD_ALREADY_PRESENT: " + path)
    tree = ast.parse(source, filename=path)
    top_level = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and n.name == "generate_events"]
    if not top_level or any(isinstance(n, ast.AsyncFunctionDef) for n in top_level):
        raise ValueError("LOOP_GUARD_SOURCE_DRIFT: expected sync generate_events: " + path)
    # Appended after the existing wrappers so preceding source evolution stays
    # authoritative. Does not replace a method body or monkeypatch imports.
    result = source.rstrip() + "\n" + WRAPPER + "\n"
    ast.parse(result, filename=path)
    return result


def candidate(live: dict[str, bytes]) -> dict[str, bytes]:
    helper = Path(HELPER).read_bytes()
    ast.parse(helper.decode("utf-8"), filename=HELPER)
    changed = {p: patch_engine(live[p].decode("utf-8"), p).encode("utf-8")
               for p in ENGINES}
    changed[HELPER] = helper
    return changed


def snapshot():
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise RuntimeError("EXACT_LIVE_HF_REVISION_MISSING")
    files = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if HELPER in files:
        raise RuntimeError("LIVE_REPETITION_HELPER_EXISTS: reconcile before replacing")
    before = {p: Path(hf_hub_download(SPACE, p, repo_type="space",
                                    revision=revision)).read_bytes()
              for p in ENGINES}
    after = candidate(before)
    (ROOT / "before").mkdir(parents=True, exist_ok=True)
    for path, value in before.items():
        (ROOT / "before" / path).write_bytes(value)
    manifest = {"contract": MARK, "space": SPACE, "revision": revision,
                "before": {p: checksum(v) for p, v in before.items()},
                "after": {p: checksum(v) for p, v in after.items()},
                "paths": list(after)}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("LOOP_GUARD_PREFLIGHT", json.dumps(manifest, sort_keys=True))


def publish():
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
    if os.environ.get("SWRLZ_NONCODE_LOOP_DEPLOY_APPROVED") != "1":
        raise PermissionError("Canonical §C scoped release approval missing")
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise PermissionError("HF release credential missing")
    m = json.loads((ROOT / "manifest.json").read_text())
    api = HfApi(token=token)
    old_rev = m["revision"]
    if api.repo_info(SPACE, repo_type="space").sha != old_rev:
        raise RuntimeError("SPACE_REVISION_MOVED: abort, do not overwrite newer work")
    if HELPER in set(api.list_repo_files(SPACE, repo_type="space", revision=old_rev)):
        raise RuntimeError("HELPER_CONFLICT: abort")
    before = {p: (ROOT / "before" / p).read_bytes() for p in ENGINES}
    for p, value in before.items():
        if checksum(value) != m["before"][p]:
            raise RuntimeError("SOURCE_SNAPSHOT_CHECKSUM_MISMATCH: " + p)
        if Path(hf_hub_download(SPACE, p, repo_type="space", revision=old_rev,
                                token=token)).read_bytes() != value:
            raise RuntimeError("LIVE_SOURCE_MISMATCH: " + p)
    after = candidate(before)
    if {p: checksum(v) for p, v in after.items()} != m["after"]:
        raise RuntimeError("PATCH_CANDIDATE_DRIFT")
    operations = [CommitOperationAdd(path_in_repo=p, path_or_fileobj=io.BytesIO(value))
                  for p, value in after.items()]
    change = api.create_commit(repo_id=SPACE, repo_type="space", operations=operations,
                               parent_commit=old_rev,
                               commit_message="fix(§C): stop runaway repetitive prose and lyrics")
    new_rev = getattr(change, "oid", None) or api.repo_info(SPACE, repo_type="space").sha
    try:
        for p, expected in after.items():
            readback = Path(hf_hub_download(SPACE, p, repo_type="space",
                                           revision=new_rev, token=token)).read_bytes()
            if readback != expected:
                raise RuntimeError("LIVE_READBACK_MISMATCH: " + p)
    except Exception:
        if api.repo_info(SPACE, repo_type="space").sha == new_rev:
            revert = [CommitOperationAdd(path_in_repo=p, path_or_fileobj=io.BytesIO(v))
                      for p, v in before.items()]
            revert.append(CommitOperationDelete(path_in_repo=HELPER))
            api.create_commit(repo_id=SPACE, repo_type="space", operations=revert,
                              parent_commit=new_rev,
                              commit_message="rollback(§C): restore exact pre-loop-guard source")
        raise
    print("LOOP_GUARD_PUBLISHED", json.dumps({"before": old_rev, "after": new_rev,
                                             "verified": True, "paths": list(after)}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("snapshot", "publish"))
    args = ap.parse_args()
    snapshot() if args.mode == "snapshot" else publish()
