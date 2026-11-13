#!/usr/bin/env python3
"""Guarded, rollback-capable publication of the validated §C 9B overlay.

Only the existing kamiloki/Swyrlz files may change. Parent-commit protection
rejects concurrent releases. No Space creation, hardware setting, secret,
account record, older repo source package or Vercel operation is involved.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import time
import urllib.request

from huggingface_hub import HfApi, CommitOperationAdd, CommitOperationDelete, hf_hub_download
from hf_chat_qwen35_9b_integration import SPACE, EXPECTED_LIVE_REVISION, ROOT, OUT, BEFORE

DEPLOYMENT_RECORD = ROOT / "qwen35-deployment.json"
URL = "https://kamiloki-swyrlz.hf.space"


def _digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _api() -> HfApi:
    token = os.environ.get("HF_TOKEN", "").strip()
    if len(token) < 12:
        raise RuntimeError("Existing HF_TOKEN release secret is required")
    return HfApi(token=token)


def _manifest() -> dict:
    m = json.loads((OUT / "CANDIDATE.json").read_text("utf-8"))
    if m.get("space") != SPACE or m.get("previousRevision") != EXPECTED_LIVE_REVISION:
        raise RuntimeError("Model trial identity changed")
    if m.get("productionMutation") or m.get("hardwareChange") or m.get("published"):
        raise RuntimeError("Unexpected candidate provenance")
    if len(m.get("files", [])) != 8:
        raise RuntimeError("Unexpected model trial file count")
    for item in m["files"]:
        body = (OUT / item["path"]).read_bytes()
        if _digest(body) != item["afterSha"]:
            raise RuntimeError("Candidate bytes changed since source verification: " + item["path"])
        if item.get("beforeSha"):
            previous = (BEFORE / item["path"]).read_bytes()
            if _digest(previous) != item["beforeSha"]:
                raise RuntimeError("Rollback bytes mismatch: " + item["path"])
    return m


def publish() -> None:
    if os.environ.get("SWRLZ_QWEN35_APPROVED") != "1":
        raise RuntimeError("No explicit production deployment approval")
    m = _manifest()
    api = _api()
    live = api.repo_info(SPACE, repo_type="space").sha
    if live != EXPECTED_LIVE_REVISION:
        raise RuntimeError("Concurrent Hugging Face release detected: no mutation")
    operations = [
        CommitOperationAdd(path_in_repo=r["path"], path_or_fileobj=str(OUT / r["path"]))
        for r in m["files"]
    ]
    result = api.create_commit(
        repo_id=SPACE, repo_type="space",
        operations=operations, parent_commit=live,
        commit_message="§C Qwen3.5-9B single resident model trial; exact source overlay; rollback preserved",
    )
    after = getattr(result, "oid", None) or api.repo_info(SPACE, repo_type="space").sha
    receipt = {"space": SPACE, "before": live, "after": after, "model": m["model"],
               "stage": "SOURCE_PUBLISHED_RUNTIME_UNVERIFIED", "files": m["files"]}
    DEPLOYMENT_RECORD.write_text(json.dumps(receipt, indent=2), "utf-8")
    print(json.dumps({"status": receipt["stage"], "previous": live, "published": after}))


def verify() -> None:
    deployment = json.loads(DEPLOYMENT_RECORD.read_text("utf-8"))
    api = _api()
    sha = deployment["after"]
    if api.repo_info(SPACE, repo_type="space").sha != sha:
        raise RuntimeError("Space HEAD changed after candidate publication")
    # Space build, 6.7GB model preloading and a two-CPU llama.cpp build can take time.
    # The ready endpoint only returns true AFTER an actual native inference warmup.
    deadline = time.monotonic() + 1500
    attempts = 0
    last_phase = "STARTING"
    while time.monotonic() < deadline:
        attempts += 1
        if api.repo_info(SPACE, repo_type="space").sha != sha:
            raise RuntimeError("Newer Space update appeared during verification; refuse rollback")
        try:
            request = urllib.request.Request(URL + "/api/hf/qwen35-ready",
                    headers={"Cache-Control": "no-cache", "User-Agent": "Swrlz-Qwen35-Release-Check/1"})
            with urllib.request.urlopen(request, timeout=12) as response:
                ready = json.load(response)
            if ready.get("ready") is True and ready.get("model") == "qwen3.5-9b":
                with urllib.request.urlopen(URL + "/api/hf/models", timeout=12) as response:
                    models = json.load(response).get("models", [])
                names = {m.get("model_id") for m in models}
                if not {"stock", "700m", "coder"}.issubset(names):
                    raise RuntimeError("Expected compatibility route IDs missing")
                if not all("Qwen3.5-9B-GGUF" in m.get("checkpoint", "")
                           for m in models if m.get("model_id") in {"stock", "700m", "coder"}):
                    raise RuntimeError("Legacy model still active in route catalogue")
                print(json.dumps({"status": "LIVE_9B_READY", "revision": sha,
                                  "attempts": attempts, "routes": ["stock", "700m", "coder"]}))
                return
            last_phase = str(ready.get("ready", "NO_RESPONSE"))
        except Exception as error:
            last_phase = type(error).__name__
        if attempts % 8 == 0:
            print(json.dumps({"status": "WAITING_FOR_MODEL_WARMUP", "attempts": attempts,
                              "observation": last_phase}), flush=True)
        time.sleep(15)
    raise RuntimeError("Qwen3.5-9B did not become inference-ready on existing HF Space")


def rollback() -> None:
    if not DEPLOYMENT_RECORD.exists():
        print("NO_CANDIDATE_COMMIT_NO_ROLLBACK")
        return
    deployment = json.loads(DEPLOYMENT_RECORD.read_text("utf-8"))
    api = _api()
    live = api.repo_info(SPACE, repo_type="space").sha
    if live != deployment["after"]:
        print(json.dumps({"status": "ROLLBACK_BLOCKED_CONCURRENT_RELEASE", "head": live}))
        raise RuntimeError("Another owner release advanced HEAD: cannot safely roll back")
    m = _manifest()
    operations = []
    for r in m["files"]:
        if r.get("beforeSha"):
            operations.append(CommitOperationAdd(
                path_in_repo=r["path"], path_or_fileobj=str(BEFORE / r["path"])))
        else:
            operations.append(CommitOperationDelete(path_in_repo=r["path"]))
    result = api.create_commit(
        repo_id=SPACE, repo_type="space", operations=operations,
        parent_commit=live, commit_message="Rollback unsuccessful §C 9B trial to exact previous source")
    after = getattr(result, "oid", None) or api.repo_info(SPACE, repo_type="space").sha
    for r in m["files"]:
        if r.get("beforeSha"):
            restored = Path(hf_hub_download(SPACE, r["path"], repo_type="space",
                                            revision=after)).read_bytes()
            if _digest(restored) != r["beforeSha"]:
                raise RuntimeError("Rollback verification failed: " + r["path"])
    print(json.dumps({"status": "ROLLED_BACK_SOURCE", "from": live, "to": after,
                      "previousSource": deployment["before"]}))


if __name__ == "__main__":
    if sys.argv[1:] == ["publish"]:
        publish()
    elif sys.argv[1:] == ["verify"]:
        verify()
    elif sys.argv[1:] == ["rollback"]:
        rollback()
    else:
        raise SystemExit("Usage: hf_chat_qwen35_9b_release.py publish|verify|rollback")
