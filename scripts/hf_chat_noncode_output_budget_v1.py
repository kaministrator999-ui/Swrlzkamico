#!/usr/bin/env python3
"""Source-pinned, non-deploying §C output-budget recovery candidate.

Patch only the common last-decode termination seam in current live engines.
No broad HF Space replacement and no model/context or code artifact changes.
This module deliberately does not publish: promotion must use the governed
existing-space release path after source and test reconciliation.
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
ENGINE_FILES = ("lfm2_700m_engine.py", "qwen_coder_engine.py")
BACKUP_DIR = Path("swrlz-output-limit-backup")
OLD_TAIL = '''    if candidate_attempts and candidate_attempts[-1].get("finishReason")=="length":
        yield {"type":"FAILED","phase":"FAILED","reason":"OUTPUT_TOKEN_LIMIT","message":"The model reached its output limit before finishing; no complete artifact was accepted.","finishReason":"length"}
        return
'''
NEW_TAIL = '''    if candidate_attempts and candidate_attempts[-1].get("finishReason")=="length":
        # Non-code output caps are a paused delivery, not a failed request.
        # Do not bypass the accepted-code or source-edit validation gates.
        if not programming.get("codingTask") and not locals().get("source_change_mode"):
            if first_delta is None:
                # Buffered text is only revealed when its acceptance gate passed.
                # A rejected lyric/source candidate must never leak here.
                if candidate_check.get("status")=="PASS" and str(candidate_text or "").strip():
                    yield {"type":"DELTA","text":candidate_text}
                else:
                    yield {"type":"DELTA","text":"I reached the response limit before I could verify a complete answer. Please ask me to try the remaining part."}
            yield {"type":"CANDIDATE_VALIDATION","validation":{
                "status":"INCOMPLETE","reasons":["output-token-limit"],
                "verificationState":"UNVERIFIED_PARTIAL","accepted":False}}
            yield {"type":"STATUS","phase":"OUTPUT_LIMIT_PAUSED",
                   "reason":"The response reached a generation limit; existing visible text was retained. It may be incomplete."}
            yield {"type":"COMPLETED","phase":"PARTIAL","outputLimitReached":True}
            return
        yield {"type":"FAILED","phase":"FAILED","reason":"OUTPUT_TOKEN_LIMIT","message":"The model reached its output limit before finishing; no complete artifact was accepted.","finishReason":"length"}
        return
'''

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def patch_source(source: str, path: str = "<engine>") -> str:
    if source.count(OLD_TAIL) != 1:
        raise ValueError(f"UNSAFE_SOURCE_DRIFT {path}: termination anchor count={source.count(OLD_TAIL)}")
    if NEW_TAIL in source:
        raise ValueError(f"ALREADY_PATCHED {path}")
    edited = source.replace(OLD_TAIL, NEW_TAIL, 1)
    ast.parse(edited, filename=path)
    assert edited.count("UNVERIFIED_PARTIAL") == 1
    return edited

def inspect_live(*, snapshot: bool = False) -> None:
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    revision = api.repo_info(SPACE, repo_type="space").sha
    if not revision or len(revision) != 40:
        raise RuntimeError("Live Hugging Face revision unavailable")
    print("NONCODE_LIMIT_PREFLIGHT revision=" + revision, flush=True)
    manifest = {"space": SPACE, "revision": revision, "files": {}}
    for name in ENGINE_FILES:
        source = Path(hf_hub_download(SPACE, name, revision=revision, repo_type="space")).read_text(encoding="utf-8")
        edited = patch_source(source, name)
        manifest["files"][name] = {
            "before_sha256": sha256(source.encode("utf-8")),
            "after_sha256": sha256(edited.encode("utf-8"))}
        if snapshot:
            (BACKUP_DIR / "before").mkdir(parents=True, exist_ok=True)
            (BACKUP_DIR / "before" / name).write_bytes(source.encode("utf-8"))
        print("NONCODE_LIMIT_PREFLIGHT file=" + name
              + " before_sha256=" + sha256(source.encode("utf-8"))
              + " candidate_sha256=" + sha256(edited.encode("utf-8"))
              + " bytes=" + str(len(edited.encode("utf-8"))), flush=True)
    if snapshot:
        (BACKUP_DIR / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("NONCODE_LIMIT_PREFLIGHT_OK deploy_inert=true", flush=True)

def publish_live() -> None:
    """Guarded two-file CAS commit; no deletion or whole-Space packaging."""
    from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download
    if os.environ.get("SWRLZ_OUTPUT_BUDGET_APPROVED") != "1":
        raise RuntimeError("Missing approved canonical Hugging Face release guard")
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("Missing guarded Hugging Face credential")
    manifest = json.loads((BACKUP_DIR / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("space") != SPACE or len(str(manifest.get("revision") or "")) != 40:
        raise RuntimeError("Untrusted or missing immutable source snapshot")
    api = HfApi(token=token)
    old_revision = manifest["revision"]
    info = api.repo_info(SPACE, repo_type="space")
    if info.id != SPACE or info.sha != old_revision:
        raise RuntimeError("Live Space changed since preflight; refuse stale patch")
    if (getattr(info, "cardData", None) or {}).get("sdk") != "gradio":
        raise RuntimeError("Refuse unexpected Hugging Face Space SDK")
    originals, edits = {}, {}
    for name in ENGINE_FILES:
        original = (BACKUP_DIR / "before" / name).read_bytes()
        record = manifest["files"][name]
        if sha256(original) != record["before_sha256"]:
            raise RuntimeError("Snapshot hash mismatch: " + name)
        live = Path(hf_hub_download(
            SPACE, name, revision=old_revision, repo_type="space",
            token=token)).read_bytes()
        if live != original:
            raise RuntimeError("Live engine source differs from snapshot: " + name)
        candidate = patch_source(original.decode("utf-8"), name).encode("utf-8")
        if sha256(candidate) != record["after_sha256"]:
            raise RuntimeError("Candidate hash mismatch: " + name)
        originals[name] = original
        edits[name] = candidate
    operations = [
        CommitOperationAdd(path_in_repo=name, path_or_fileobj=io.BytesIO(edits[name]))
        for name in ENGINE_FILES]
    commit = api.create_commit(
        repo_id=SPACE, repo_type="space", operations=operations,
        commit_message="fix(§C): retain non-code output when token budget ends",
        parent_commit=old_revision)
    new_revision = getattr(commit, "oid", None) or api.repo_info(SPACE, repo_type="space").sha
    try:
        for name in ENGINE_FILES:
            actual = Path(hf_hub_download(
                SPACE, name, revision=new_revision, repo_type="space", token=token)).read_bytes()
            if actual != edits[name]:
                raise RuntimeError("Published source mismatch: " + name)
    except Exception:
        current_revision = api.repo_info(SPACE, repo_type="space").sha
        if current_revision == new_revision:
            api.create_commit(
                repo_id=SPACE, repo_type="space", parent_commit=new_revision,
                operations=[
                    CommitOperationAdd(path_in_repo=name, path_or_fileobj=io.BytesIO(originals[name]))
                    for name in ENGINE_FILES],
                commit_message="rollback(§C): restore exact engines after output guard readback failure")
        raise
    print("NONCODE_LIMIT_PUBLISHED previous=" + old_revision
          + " new=" + new_revision + " two_file_readback=verified", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("preflight", "snapshot", "publish"))
    args = parser.parse_args()
    if args.mode == "preflight":
        inspect_live()
    elif args.mode == "snapshot":
        inspect_live(snapshot=True)
    elif args.mode == "publish":
        publish_live()
